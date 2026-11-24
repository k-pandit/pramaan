# Pramaan (প্ৰমাণ): rules with proof

A government-controlled knowledge, rules and document assistant for authorised officials, built for the **North-East Seva First Innovation Challenge 2026** (Stream 1) challenge *Trusted Government Knowledge, Rules & Document Assistant* (owners: Assam Administrative Staff College and the Assam State Space Application Centre).

**Ask a rule question. Pramaan answers from the text in force, shows what was amended or repealed and when, and quotes the notification. Every word, number and date points to the paragraph it came from, or it says it does not know.**

- **Live demo:** https://k-pandit.github.io/pramaan/
- **Evidence scorecard:** [reports/scorecard.md](reports/scorecard.md) · run history: [reports/CHANGELOG.md](reports/CHANGELOG.md)
- **Sources and hashes:** [SOURCES.md](SOURCES.md)

## Try the main example
*Who can sanction the State share of a centrally sponsored scheme?* The Delegation of Financial Power Rules, 1999 (Schedule I, Sl. 30) gave this to the Senior-most Secretary. Schedule I was recast in 2017 and Sl. 23(ii) rewritten on 23 July 2019. The Delegation of Financial Power Rules, Assam, 2022 (Notification FEB.136/2022/1) repealed the 1999 rules by Rule 30; the power now sits at Sl. 135(d). Pramaan answers from the 2022 text, shows the chain, and marks the earlier reviewed answer "under review".

## How it works
- **Register:** each document is split into rule- or paragraph-sized passages with document, page and access tier (`engine/register.py`, `engine/schema.sql`). Amendments, repeals, clarifications and conflicts are dated links between passages, confirmed by a curator (`register/links.json`).
- **Answers:** extractive by default, on CPU, with no language model (`engine/answer.py`). Every sentence shown is a verbatim part of the passage it cites. A **number guard** withholds any sentence whose figure is not in its cited passage. Weak matches are **refused** and sent to the curators' queue.
- **Access:** the role decides which search tables are queried at all (public and internal passages are indexed separately), so restricted text is never retrieved for a role without access.
- **Uploads:** documents containing instructions aimed at the assistant are quarantined for curator review, never searched.
- **Audit:** every answer is written to a hash-chained log; editing any entry breaks the chain.
- An optional writing layer (India-hosted model, public documents only, owners' approval) can sit behind the same checks; it is not used in this evidence build.

## Reproduce the evidence
```
pip install pymupdf
python run_evidence.py
```
Writes `reports/scorecard.md`, `scorecard.json` and `results.jsonl` in about two seconds on a laptop. The questions (`eval/questions.jsonl`) were committed before the first run; their SHA-256 is in `eval/FROZEN.txt` and checked on every run.

## Honest limits
Seven public documents; questions written by the project team and scored automatically, not by a domain expert; English text only (scanned pages and legacy-font Assamese are not searchable yet); synthetic fixtures for the leak and injection tests. Weak results (out-of-scope refusal, rule-in-force naming) are reported, not hidden; see the scorecard and change log.

## Team
Jorhat Institute of Science and Technology, Jorhat, Assam. Principal Investigator: Dr. Kamalesh Kumar Pandit, Assistant Professor, Department of Mathematics. Students: Saujyendra Dutta, Debika Das, Prashanta Kumar Singh, Abhishek Kumar Sharma.

## Licence
AGPL-3.0. The Government of Assam may use, modify and host it freely.
