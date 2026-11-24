# Pramaan evidence scorecard

Questions file SHA-256 `e1676f0650eebe14e1698444576d8df49f4e71699ce095336c4f12219a44baf5` (matches the frozen hash: **True**). Source files match their recorded SHA-256: **True**. Run time 1.6 s on a laptop CPU, no GPU, no language model.

Refusal threshold set on the 10 dev questions only: coverage ≥ 0.3 (dev refusal recall 4/4, dev false refusals 0/6).

| Measure | Result |
|---|---|
| Correct passage in the top 3 (answerable + amended) | 37 of 42 (88.1%; 95% CI 75.0–94.8%) |
| Answer correct: cites the right page and contains the expected fact | 23 of 30 (76.7%; 95% CI 59.1–88.2%) |
| Rule in force: answers from the current text and names the amending or repealing instrument | 6 of 12 (50.0%; 95% CI 25.4–74.6%) |
| Out-of-scope questions refused | 6 of 12 (50.0%; 95% CI 25.4–74.6%) |
| Answerable questions wrongly refused | 1 of 42 (2.4%; 95% CI 0.4–12.3%) |
| Citation validity: every sentence is a verbatim part of the passage it cites | 137 of 137 (100.0%; 95% CI 97.3–100%) |
| Altered figures caught by the number guard | 166 of 166 (100.0%; 95% CI 97.7–100.0%) |
| Number-guard false alarms on unaltered sentences | 0 of 103 (0.0%; 95% CI 0–3.6%); rule of three: true rate below 2.9% |
| Wrong figure typed in the question: flagged, never repeated as fact | 11 of 12 (91.7%; 95% CI 64.6–98.5%) |
| Restricted text shown to a role without access | 0 of 22 (0.0%; 95% CI 0.0–14.9%); rule of three: true rate below 13.6% (control: curator role found restricted text 3/3 restricted documents) |
| Planted figures shown from injected uploads | 0 of 9 (0.0%; 95% CI 0–29.9%); rule of three: true rate below 33.3%; uploads flagged and quarantined 3/3 |
| Same, if quarantine were switched off (shows why curation matters) | 9 of 9 (100.0%; 95% CI 70.1–100%) |
| Conflicting sources (notification dated 2013 vs 2017): both shown | fail |
| Reviewed answer withdrawn when a cited clause changes | pass |
| Audit log: hash chain verifies; one edited entry detected | True / True (61 entries) |
| Median time per answer | 0.001 s |

## Limits of this test

- Seven public documents only (Delegation of Financial Power Rules 1999 and 2022 with the 2019 amendment, the Handbook of Pension, the Leave Rules 1934, the e-Office SOP and the pension checklist). Several are archived copies of the official files; the original address, archive address and SHA-256 of each are in `corpus/SOURCES.json`.
- The questions were written by the project team, not by AASC faculty, and answers were scored automatically against expected facts, not graded by a domain expert. Intervals are wide because the test is small.
- English text only. Scanned pages and legacy-font Assamese are not searchable in this build; Assamese questions are not tested.
- Leak and injection tests use synthetic documents stamped SYNTHETIC TEST FIXTURE; they are never counted in accuracy.
- Amendment links were confirmed by a curator (demo role) against the PDF pages. The 2019 memorandum was retyped from the PDF because the scan reads poorly.
- This is the first run, published unchanged. Any later run will be shown beside it with a change log.
