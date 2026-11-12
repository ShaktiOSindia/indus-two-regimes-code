# Third implementation (Codex CLI): comparison with the paper's code

Written 12 Nov 2026 for the public code deposit. The full private record is `REVIEW_VERIFICATION_2026-11-12.md`.

**What was done.** Codex CLI was given the frozen specification (sections 0-13), the old scripts it names (for
procedure only), the two output schemas (key layout with value types) and the pinned input file, and asked to write a
second program from the text alone, without seeing our code or outputs (`BRIEF.md`). It covered the entries of
section 13 whose printed numbers no second program had computed yet: 13.1-13.3, 13.5, 13.7, 13.8, 13.12-13.19
(`impl.py`, standard library only; `AMBIGUITIES.md`; `RUN_LOG.md`). Its delivered outputs were re-run by us twice
from its final code in fresh processes: identical bytes (the hashes in its own run log are of an earlier, unfinished
run).

**Result** (`compare_codex.py` -> `compare_codex_output.txt`): under copy rule D0, 1,436 values compared, 1,381
equal, 55 differ; under D1, 1,269 compared, 1,213 equal, 56 differ; no key missing on either side. Of the 286
printed numbers in scope, **263 agree exactly** (262 in Codex's two output files, and the count of malformed rows,
which matches its run log) and 23 differ; before Table 5 gained its all-texts columns on 12 November, 259 of 282. Every difference is explained by one of seven
readings of the specification: our own library, run under Codex's reading, reproduces Codex's value exactly in 26
of 26 checks (`reproduce_codex_readings.py` -> `reproduce_codex_readings_output.txt`). No arithmetic error was found
on either side.

| id | difference | our reading / Codex's reading | printed numbers affected |
|---|---|---|---|
| U1 | K_tri/N | percent / fraction | 5, none at the printed precision |
| K1 | 13.16 P2 `pct_analyzable` | CISI rows / analyzable rows (the paper's sentence) / analyzable / all rows | none (same counts) |
| K2 | 13.16 P4 rows without a legible sign | the malformed row counted apart / included | none |
| R3 | 13.18 F6 "k rarest" | ranked over all analyzable rows (the named script) / within each population | 1 |
| R4 | 13.8 G4b mean length by tier | the eligible texts, the same set as the rate (the named script) / all multi-sign seals | 2 |
| R5 | 13.7 07-C stems | key tokens including `000` ("tokens", section 1) / legible signs only | none (all-texts values only) |
| R1 | 13.1 R/L-or-L/R row | `dir.` exactly R/L or L/R (section 8) / 'R/l' read as R/L, as 13.19 does (2 rows) | 2 (N 4,452 vs 4,454; 81.1 vs 81.0) |
| R2 | 13.17 [MARKER] 740 split | draws over every text of the population, measured on the eligible / draws over the eligible texts only (script 19's order) | 6 (halves 15.5/16.1 vs 15.7/15.9; D1 16.2/15.1 vs 15.2/16.0; terminal 19.4/19.7 vs 19.2/19.9) |

The paper keeps its runs as recorded and states both readings of R1 and R2 in `analysis/SPEC_READINGS.md`. The
claim R2's numbers support (the enrichment does not move under a split of the marker) holds under both readings; the
unsplit baselines (15.8; D1 15.6) agree exactly between the two programs.
