-- Pramaan knowledge register. Every answer is built from rows of `unit`, and every claim cites one.
CREATE TABLE document (
  id TEXT PRIMARY KEY, title TEXT, issuer TEXT, official_url TEXT, archive_url TEXT,
  sha256 TEXT, tier TEXT CHECK (tier IN ('P','I')),        -- P public, I internal; X is refused at upload
  status TEXT, note TEXT, file TEXT);
CREATE TABLE unit (                                        -- a rule, schedule item or paragraph
  uid TEXT PRIMARY KEY, doc TEXT REFERENCES document(id), page INTEGER, text TEXT,
  tier TEXT, origin TEXT);                                 -- extracted | curator-retyped | fixture
CREATE TABLE link (                                        -- curator-confirmed change between units
  from_uid TEXT REFERENCES unit(uid), to_uid TEXT REFERENCES unit(uid),
  kind TEXT CHECK (kind IN ('amend','repeal','clarify','conflict')),
  instrument TEXT, date TEXT, note TEXT, confirmed_by TEXT);
CREATE TABLE reviewed (                                    -- curator-reviewed answers (a flag, not a separate system)
  id TEXT PRIMARY KEY, questions TEXT, scope TEXT, cites TEXT, reviewer TEXT, reviewed_on TEXT, review_by TEXT);
CREATE TABLE dataset (                                     -- light ASSAC dataset finder (metadata only)
  id TEXT PRIMARY KEY, title TEXT, theme TEXT, area TEXT, period TEXT, custodian TEXT, access TEXT, source TEXT);
CREATE TABLE audit (                                       -- append-only, hash-chained
  seq INTEGER PRIMARY KEY, ts TEXT, role TEXT, question_masked TEXT, outcome TEXT, cited TEXT,
  answer_sha256 TEXT, prev_hash TEXT, hash TEXT);
-- Two search tables: the role filter decides which ones a query may touch (tier filter inside retrieval).
CREATE VIRTUAL TABLE fts_p USING fts5(uid UNINDEXED, text, tokenize='porter unicode61');
CREATE VIRTUAL TABLE fts_i USING fts5(uid UNINDEXED, text, tokenize='porter unicode61');
