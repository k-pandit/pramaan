# Evaluation run history

The questions were committed (`eval/questions.jsonl`, SHA-256 `e1676f06…`) before any run. Results are never edited; each run is kept.

| Run | Date | What changed | Effect |
|---|---|---|---|
| 1 | 24 Nov 2026 | First run of the frozen questions. Published unchanged in `reports/run1/`. | — |
| 2 | 24 Nov 2026 | **Measurement fix only, engine unchanged.** The leak check searched the whole response, including the user's own question; six leak questions were the restricted passages typed in verbatim, so the canary was found in the echoed question, not in anything the system returned. The check now excludes the question. The positive control now counts restricted documents found by the curator role. | Restricted text shown to a role without access: Run 1 reported 6/22 (measurement error), Run 2 reports 0/22 with all 3 restricted documents found by the authorised role. All other numbers identical. |

## Known weaknesses found by Run 1 (not fixed here, so the numbers stay honest)
- **Out-of-scope refusal 6/12.** The refusal threshold was tuned on four easy dev questions and is too permissive; loosely related leave and DFP pages are returned for GPF interest, child care leave, RTI fee and similar questions. Pilot work: a second refusal signal (answer-type match) tuned on a larger dev set written by AASC faculty.
- **Rule in force 6/12.** In several cases the current text is cited but the quoted sentences do not name the instrument (for example, the "RULE 30" heading falls outside the quoted sentence), and one rephrased DFP question was refused. Pilot work: always print the in-force clause's heading and instrument line with the answer.
- **Conflict case failed.** Conflicts are checked only on the top passage; here the handbook index page ranked first. Pilot work: check conflicts on every passage shown.

## Run 3 (24 Nov 2026): feature fix, scored results unchanged
A current reviewed answer is now shown from the passage the curator reviewed (before, the badge could sit on an answer drawn from another paragraph). None of the frozen test questions matches a reviewed-answer pattern; a rerun produced identical scored results.
