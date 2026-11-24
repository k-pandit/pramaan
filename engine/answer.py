"""Answer a question from the register: cited sentences only, the rule in force, or an honest refusal.

Default mode is extractive and runs on CPU with no language model. Every sentence shown is a verbatim part of the
unit it cites; every figure in it must appear in that unit (number guard); the role decides which search tables
are touched at all (tier filter inside retrieval); every answer is written to a hash-chained audit log.
"""
import datetime, hashlib, json, re, sqlite3

ROLES = {'official': ['p'], 'curator': ['p', 'i']}        # official sees public documents; curator also internal
STOP = set('''a an and are as at be been by can could do does for from had has have how i if in into is it its
me my of on or shall should so than that the their them then there these they this to under up upon was what when
where which who whom whose why will with would you your am being did per any all also not no nor only very'''.split())
NUM = re.compile(r'\d[\d,]*(?:\.\d+)?')
RULE_REF = re.compile(r'(?i)\b(rule|sl\.?\s*no\.?|sl\.?|serial)\s*(\d{1,3})\s*(\([a-z]+\))?')
CFG = {'min_coverage': 0.5, 'top_k': 8, 'max_sentences': 3}
VERB = {'amend': 'Amended', 'repeal': 'Repealed', 'clarify': 'Clarified'}


def stem(w):
    for suf in ('ing', 'ed', 'es', 's'):
        if len(w) > 4 and w.endswith(suf):
            return w[:-len(suf)]
    return w


def terms(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1]


def nums(text):
    return {n.replace(',', '').rstrip('.') for n in NUM.findall(text)}


def segments(text):
    """Verbatim pieces of a unit used as answer sentences (split at sentence ends, semicolons and list items)."""
    parts = re.split(r'(?<=[.;:])\s+(?=[A-Z(\[0-9])|\s(?=(?:i{1,3}|iv|v|vi{0,3}|\d)\)\s)', text)
    return [p.strip() for p in parts if p and len(p.strip()) > 25 and readable(p)]


def readable(s):
    """Skip text extracted from legacy-font Assamese (shows as symbols); it is never shown as an answer sentence."""
    letters = sum(c.isascii() and c.isalnum() for c in s)
    return letters / max(1, len(s.replace(' ', ''))) > 0.8


class Pramaan:
    def __init__(self, db):
        self.db = sqlite3.connect(db) if isinstance(db, str) else db

    # ---------------------------------------------------------------- retrieval (tier filter inside the query)
    def search(self, question, role):
        q = terms(question)
        if not q:
            return [], q
        match = ' OR '.join(f'"{t}"' for t in dict.fromkeys(q))
        hits = []
        for t in ROLES[role]:
            hits += self.db.execute(f'SELECT uid, bm25(fts_{t}) FROM fts_{t} WHERE fts_{t} MATCH ? ORDER BY bm25(fts_{t}) LIMIT ?',
                                    (match, CFG['top_k'])).fetchall()
        hits.sort(key=lambda h: h[1])
        m = RULE_REF.search(question)                     # a named rule or serial number goes straight to that clause
        if m:
            num, sub = m.group(2), (m.group(3) or '')
            pat = f'%{num} {sub}%' if sub else f'%RULE {num}.%'
            direct = self.db.execute('SELECT uid FROM unit WHERE (text LIKE ? OR text LIKE ?) AND tier IN (%s)'
                                     % ','.join(repr(x.upper()) for x in ROLES[role]),
                                     (pat, f'%Rule {num} %')).fetchall()
            hits = [(u, -999.0) for (u,) in direct] + hits
        seen, out = set(), []
        for uid, s in hits:
            if uid not in seen:
                seen.add(uid); out.append(uid)
        return out[:CFG['top_k']], q

    def unit(self, uid):
        r = self.db.execute('SELECT u.uid,u.doc,u.page,u.text,u.tier,u.origin,d.title,d.status,d.official_url,d.archive_url,d.note '
                            'FROM unit u JOIN document d ON d.id=u.doc WHERE u.uid=?', (uid,)).fetchone()
        return dict(zip(['uid', 'doc', 'page', 'text', 'tier', 'origin', 'title', 'doc_status', 'url', 'archive', 'doc_note'], r))

    def coverage(self, q, uid):
        ut = set(terms(self.unit(uid)['text']))
        qs = set(q)
        return len(qs & ut) / max(1, len(qs))

    # ---------------------------------------------------------------- currency: follow curator-confirmed links
    def forward(self, uid, role):
        """Return the unit in force for `uid` and the chain of changes that led there."""
        chain, cur, seen = [], uid, set()
        while cur not in seen:
            seen.add(cur)
            nxt = self.db.execute("SELECT to_uid, kind, instrument, date, note FROM link WHERE from_uid=? AND kind IN ('amend','repeal','clarify')",
                                  (cur,)).fetchall()
            nxt = [n for n in nxt if self.unit(n[0])['tier'].lower() in ROLES[role]]
            if not nxt:
                break
            to, kind, ins, date, note = sorted(nxt, key=lambda n: n[3])[-1]
            chain.append({'from': cur, 'to': to, 'kind': kind, 'instrument': ins, 'date': date, 'note': note})
            cur = to
        return cur, chain

    def backward(self, uid):
        return [dict(zip(['from', 'kind', 'instrument', 'date', 'note'], r)) for r in self.db.execute(
            "SELECT from_uid, kind, instrument, date, note FROM link WHERE to_uid=? AND kind IN ('amend','repeal','clarify')", (uid,))]

    def conflicts(self, uid):
        return [dict(zip(['other', 'note'], r)) for r in self.db.execute(
            "SELECT CASE WHEN from_uid=? THEN to_uid ELSE from_uid END, note FROM link WHERE kind='conflict' AND (from_uid=? OR to_uid=?)",
            (uid, uid, uid))]

    def status(self, uid, role):
        u = self.unit(uid)
        if self.forward(uid, role)[1]:
            return 'amended or repealed'
        return 'repealed' if u['doc_status'] == 'repealed' else 'in force'

    # ---------------------------------------------------------------- answer checks
    @staticmethod
    def guard(sentences, units):
        """Number guard: drop any sentence whose figure does not appear in the unit it cites."""
        kept, dropped = [], []
        for s in sentences:
            ok = nums(s['text']) <= nums(units[s['cite']]['text'])
            (kept if ok else dropped).append(s)
        return kept, dropped

    def compose(self, q, uid, n):
        segs = segments(self.unit(uid)['text']) or [self.unit(uid)['text']]
        scored = sorted(range(len(segs)), key=lambda i: -len(set(terms(segs[i])) & set(q)))[:n]
        return [{'text': segs[i], 'cite': uid} for i in sorted(scored)]

    # ---------------------------------------------------------------- main entry
    def ask(self, question, role='official', log=True):
        cands, q = self.search(question, role)
        res = {'question': question, 'role': role, 'candidates': cands, 'sentences': [], 'sources': [], 'banner': None,
               'conflict': None, 'reviewed': None, 'refused': False, 'notes': []}
        rv = self.reviewed(question, role)
        if not cands or self.coverage(q, cands[0]) < CFG['min_coverage']:
            res['refused'] = True
            res['message'] = 'Not found in the approved documents available to your role. No guess is made; the question goes to the curators\' queue.'
            return self.finish(res, log)
        top = cands[0]
        primary, chain = self.forward(top, role)
        units = {}
        if chain:                                         # the top passage was changed: answer from the text in force
            res['banner'] = {'kind': chain[-1]['kind'], 'chain': chain,
                             'text': f"The passage found first ({self.unit(top)['title']}, p. {self.unit(top)['page']}) is no longer in force. "
                                     + ' Then '.join(f"{VERB[c['kind']]} by {c['instrument']} ({c['date']})." for c in chain)
                                     + ' The answer below is from the text in force.'}
        else:
            back = self.backward(primary)
            if back:
                res['banner'] = {'kind': 'current', 'chain': back,
                                 'text': 'This text is in force. Earlier text: ' + '; '.join(
                                     f"{b['instrument']} ({b['date']})" for b in back) + '.'}
            if self.unit(primary)['doc_status'] == 'repealed':
                res['banner'] = {'kind': 'repealed', 'chain': [], 'text': f"Not in force: {self.unit(primary)['title']}. {self.unit(primary)['doc_note']} "
                                 "No successor clause is linked for this passage yet; check the repealing rules."}
        sents = self.compose(q, primary, CFG['max_sentences'])
        units[primary] = self.unit(primary)
        for c in self.conflicts(primary):                 # sources disagree: show both, decide nothing
            units[c['other']] = self.unit(c['other'])
            res['conflict'] = {'with': c['other'], 'note': c['note']}
            sents += self.compose(q, c['other'], 1)
        kept, dropped = self.guard(sents, units)
        res['sentences'] = kept
        res['dropped'] = len(dropped)
        qnums = nums(question) - set().union(*(nums(u['text']) for u in units.values()))
        if qnums:
            res['notes'].append(f"The figure(s) {', '.join(sorted(qnums))} in your question do not appear in the cited source; the source text is shown instead.")
        if rv:
            res['reviewed'] = rv
        for uid in units:
            u = units[uid]
            res['sources'].append({k: u[k] for k in ('uid', 'title', 'page', 'url', 'archive', 'origin')} | {'status': self.status(uid, role), 'text': u['text']})
        for c in (res['banner'] or {}).get('chain', []):
            for k in ('from', 'to'):
                if c.get(k) and c[k] not in units:
                    u = self.unit(c[k])
                    res['sources'].append({x: u[x] for x in ('uid', 'title', 'page', 'url', 'archive', 'origin')} | {'status': self.status(c[k], role), 'text': u['text']})
        return self.finish(res, log)

    def reviewed(self, question, role):
        key = question.lower().strip(' ?')
        for rid, qs, scope, cites, who, on, by in self.db.execute('SELECT * FROM reviewed'):
            if key in json.loads(qs):
                cites = json.loads(cites)
                if any(self.unit(c)['tier'].lower() not in ROLES[role] for c in cites):
                    return None
                changed = [c for c in cites if self.forward(c, role)[1]]
                return {'id': rid, 'scope': scope, 'reviewer': who, 'reviewed_on': on, 'review_by': by,
                        'state': 'under review: a cited rule has changed' if changed else 'reviewed', 'cites': cites}
        return None

    def finish(self, res, log):
        if log:
            masked = NUM.sub('#', res['question'])
            body = json.dumps([s['text'] for s in res['sentences']], ensure_ascii=False)
            prev = (self.db.execute('SELECT hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone() or ['GENESIS'])[0]
            row = [datetime.datetime.now().isoformat(timespec='seconds'), res['role'], masked,
                   'refused' if res['refused'] else 'answered', json.dumps([s['cite'] for s in res['sentences']]),
                   hashlib.sha256(body.encode()).hexdigest(), prev]
            row.append(hashlib.sha256('|'.join(row).encode()).hexdigest())
            self.db.execute('INSERT INTO audit(ts,role,question_masked,outcome,cited,answer_sha256,prev_hash,hash) VALUES (?,?,?,?,?,?,?,?)', row)
        return res

    def verify_audit(self):
        prev = 'GENESIS'
        for r in self.db.execute('SELECT ts,role,question_masked,outcome,cited,answer_sha256,prev_hash,hash FROM audit ORDER BY seq'):
            if r[6] != prev or hashlib.sha256('|'.join(r[:7]).encode()).hexdigest() != r[7]:
                return False
            prev = r[7]
        return True
