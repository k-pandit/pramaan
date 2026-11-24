"""Build the knowledge register (SQLite) from the corpus, fixtures and curator files.

Units of truth are rule- or paragraph-sized passages ("units") with their document, page and access tier.
Amendments, repeals, clarifications and conflicts are stored as dated links between units, confirmed by a
curator in register/links.json. Nothing in this file uses a language model.
"""
import hashlib, json, os, re, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: os.path.join(ROOT, *p)

HEAD = re.compile(r'^(\d{1,3}\s?\.(\s|$)|\d{1,3}\s?\([a-z]\)|[A-Z]\.\s{1,3}[A-Z]|RULE\s+\d+|Rule\s+\d+\s*[.(]|Sl\.\s*No\.|\d+\)\s+[A-Z])')
INJECTION = re.compile(r'(?i)(ignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+(instructions|rules)|disregard\s+(the\s+)?(above|previous|instructions)|system\s+prompt|you\s+must\s+(answer|reply|say|state)|act\s+as\s+(an?\s+)?(ai|assistant))')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def split_page(text, max_len=1400):
    """Split one page into passages at rule, item or heading boundaries."""
    units, cur = [], []
    for line in (l.strip() for l in text.split('\n')):
        if not line:
            continue
        if HEAD.match(line) and len(' '.join(cur)) > 120:
            units.append(norm(' '.join(cur))); cur = []
        cur.append(line)
        if len(' '.join(cur)) > max_len:
            units.append(norm(' '.join(cur))); cur = []
    if cur:
        units.append(norm(' '.join(cur)))
    return [u for u in units if len(u) > 40]


def page_texts(path):
    import pymupdf                                    # text extraction only
    return [p.get_text() for p in pymupdf.open(path)]


def build(db_path=None, include_quarantined=False):
    db_path = db_path or J('build', 'pramaan.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(open(J('engine', 'schema.sql'), encoding='utf-8').read())
    sources = json.load(open(J('corpus', 'SOURCES.json'), encoding='utf-8'))
    overrides = json.load(open(J('register', 'overrides.json'), encoding='utf-8'))
    report = {'documents': 0, 'units': 0, 'quarantined': [], 'hash_mismatch': []}

    for d in sources:
        path = J('corpus', d['file'])
        if sha256(path) != d['sha256']:
            report['hash_mismatch'].append(d['file'])
        con.execute('INSERT INTO document VALUES (?,?,?,?,?,?,?,?,?,?)',
                    (d['id'], d['title'], d['issuer'], d['official_url'], d.get('archive_url'), d['sha256'],
                     d['tier'], d['status'], d.get('note', ''), d['file']))
        report['documents'] += 1
        pages = page_texts(path)
        skip = set(d.get('skip_pages', []))
        for pno, text in enumerate(pages, 1):
            if pno in skip:
                continue
            key = f"{d['id']}:{pno}"
            chunks = [norm(overrides[key]['text'])] if key in overrides else split_page(text)
            for i, u in enumerate(chunks, 1):
                uid = f"{d['id']}/p{pno}/{i}"
                origin = overrides[key]['origin'] if key in overrides else 'extracted'
                add_unit(con, uid, d['id'], pno, u, d['tier'], origin)
                report['units'] += 1

    for f in sorted(os.listdir(J('fixtures'))):
        meta, body = read_fixture(J('fixtures', f))
        flagged = bool(INJECTION.search(body))
        if flagged:
            report['quarantined'].append(f)
        con.execute('INSERT INTO document VALUES (?,?,?,?,?,?,?,?,?,?)',
                    (meta['id'], meta['title'], 'SYNTHETIC TEST FIXTURE', '', None, hashlib.sha256(body.encode()).hexdigest(),
                     meta['tier'], 'quarantined' if flagged else 'in_force', 'Synthetic test fixture, not a real document', f))
        if flagged and not include_quarantined:
            continue                                   # held for curator review, never searchable
        for i, u in enumerate([norm(p) for p in body.split('\n\n') if p.strip()], 1):
            add_unit(con, f"{meta['id']}/p1/{i}", meta['id'], 1, u, meta['tier'], 'fixture')

    resolve_links(con, json.load(open(J('register', 'links.json'), encoding='utf-8')), report)
    for v in json.load(open(J('register', 'reviewed.json'), encoding='utf-8')):
        con.execute('INSERT INTO reviewed VALUES (?,?,?,?,?,?,?)',
                    (v['id'], json.dumps([q.lower().strip(' ?') for q in v['questions']]), v['scope'],
                     json.dumps([find_unit(con, *a) for a in v['cites']]), v['reviewer'], v['reviewed_on'], v['review_by']))
    for r in json.load(open(J('register', 'datasets.json'), encoding='utf-8')):
        con.execute('INSERT INTO dataset VALUES (?,?,?,?,?,?,?,?)',
                    (r['id'], r['title'], r['theme'], r['area'], r['period'], r['custodian'], r['access'], r['source']))
    con.commit()
    return con, report


def read_fixture(path):
    raw = open(path, encoding='utf-8').read()
    head, body = raw.split('\n---\n', 1)
    meta = dict(l.split(': ', 1) for l in head.strip().splitlines())
    return meta, body.strip()


def add_unit(con, uid, doc, page, text, tier, origin):
    con.execute('INSERT INTO unit VALUES (?,?,?,?,?,?)', (uid, doc, page, text, tier, origin))
    con.execute(f"INSERT INTO fts_{'p' if tier == 'P' else 'i'}(uid, text) VALUES (?,?)", (uid, text))


def find_unit(con, doc, page, anchor):
    rows = con.execute('SELECT uid, text FROM unit WHERE doc=? AND page=?', (doc, page)).fetchall()
    for uid, text in rows:
        if anchor.lower() in text.lower():
            return uid
    raise ValueError(f'anchor not found: {doc} p{page} "{anchor}"')


def resolve_links(con, links, report):
    """Curator-confirmed links: amend / repeal / clarify / conflict, located by document, page and anchor text."""
    for l in links:
        a = find_unit(con, *l['from'])
        b = find_unit(con, *l['to'])
        con.execute('INSERT INTO link VALUES (?,?,?,?,?,?,?)',
                    (a, b, l['kind'], l['instrument'], l['date'], l['note'], l['confirmed_by']))
    report['links'] = len(links)
