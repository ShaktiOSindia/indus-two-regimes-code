# Readings of the frozen specification made while coding (Claude's library; the counterpart of Gemini's AMBIGUITIES.md)

The specification is frozen (tag `spec-frozen-2026-11-06`). Where its text could be read two ways, the library takes
the literal reading, and each case is listed here with the evidence of whether it changes any number. Nothing here
changes the specification; a real change goes only through its section 12 (date, reason, AK's approval).
Evidence files: `fixtures/probe_spec_readings.py` and its `_output.txt` (counts only, no study outcome).

| # | Spec text | Two readings | Literal reading used | Does it change a number? |
|---|---|---|---|---|
| 1 | s.5: "the reading-final token is legible" | the end TOKEN (a 999 blank there makes it ineligible) or the end SIGN (skip a blank) | the end token | No: no single-line row has 999 at either stored end (probe Q1) |
| 2 | s.8 sensitivity row: "texts with `dir.` R/L or L/R only" | exact values, or also the variant spelling "R/l" | exact values | 2 rows ("R/l") in one sensitivity row; the submitted script also excluded them |
| 3 | s.5 sets eligibility; s.3 says whole-text measures use >= 2 legible signs | s.5's bare per-class 740 rate includes one-sign texts, or not | includes them (s.5 has no length rule; first/last is a separate category in s.3) | Yes for that bare rate (77 TAB:I and 79 SEAL:S one-sign texts are eligible; 18 and 14 are "740"), but the paper prints no bare rate: every reported 740 rate comes from an entry that says "multi-sign" (13.1, 13.7, 13.8, 13.9, B'). The run outputs both |
| 4 | B' s.2: "Trench VI" | any area value naming Trench VI, or the exact value | exact value `FTrench VI` | No: it is the only Mound F value containing "Trench VI" (96 rows); no "Trench VII" exists |
| 5 | B' s.2 sensitivity: "Trench VI's III, IV and V count as IV, V and VI" | only those three move, or every Trench VI stratum moves up one | only those three (as written) | No: Trench VI has no Stratum VI or VII rows (I 3, II 34, III 37, IV 16, V 6) |

| 6 | s.1, 3, 4: entropy (H3; matched-token comparison) uses "pair/triple/entropy" texts | with or without a >= 2-sign rule | the class's texts in the population, BUS rows without '/' excluded, no length rule (s.3 gives the >= 2 rule to whole-text measures only) | One-sign texts add no trigram, so H3 itself is unchanged; but they are in the list the matched-token comparison shuffles, so its draws (not its definition) depend on this reading |
| 7 | s.7: "K_tri / N reported beside" | a fraction or a percent | percent (s.0: shares in percent; Table 3 prints percent) | Format only |
| 8 | s.3 (b): "whole-object identity: object key = ..." | which statistic is computed on object keys | top-10 coverage and repeat share with objects as the units (the side-level statistics; coverage and repeat share do not depend on the tie rule, so object keys need no ordering rule) | Defines an appendix row; the spec names the key, not the statistic |
| 9 | s.8 EBUDS-like: "complete; single-line; one copy per identical key across the whole corpus; legible length 1 to 14" | one copy per key before or after the completeness filter | in the order listed: complete and single-line first, then one copy per key, then length | Yes, the sample size can differ; fixture `test_ebuds_filter_order` pins it |
| 10 | s.8 grid: "the median" | which median for an even number of cells | `statistics.median` (mean of the two middle values) | Equals 13.21's p = 0.5 point; for 144 cells the mean of the 72nd and 73rd |
| 11 | Amendment 1 s.4 outcomes | a tested, met V-VII with an untested IV is not named | P | Not reachable at the recorded sizes (both cells meet 30 in all texts) |

| 12 | 13.1 M-342: "its ratio to 740's share of all legible tokens of the same population" | the eligible texts only, or all multi-sign texts | all multi-sign texts of all classes in the population (the population the rate is drawn from; eligibility restricts only the rate's denominator) | Defines the concentration ratio; fixture `test_m342_by_hand` pins it |
| 13 | 13.2 Table 3: N, mean legible length, H1 | over the entropy population (BUS rows without '/' out) or over all analyzable texts of the class | N, mean length and H1 over all analyzable texts of the class (they are not pair/triple measures); H3, Miller-Madow and K_tri/N over the entropy population | N differs by the BUS rows without '/' (a few per class) |

| 14 | 13.3 [C]: slot "position when present (initial, medial, terminal; complete single-line texts)" | index over all tokens or over legible signs | over legible signs in reading order (13's general rule: positions are counted in legible signs) | Fixture `test_slot_description` pins it |
| 15 | 13.8 appendix: "mean legible length by tier" | over all multi-sign seals of the tier or over the eligible ones the rates use | the eligible ones (the same texts as the rates beside it) | Appendix row only |
| 16 | 13.4 registered null: "in each draw, permute every column independently" | permute from the original order each draw, or from the current order | from the current order (each draw is still a uniform random permutation of every column, as registered); length-1 texts never shuffled | Draw-level only; the exact E[T] check guards the distribution |

| 17 | 13.11: "Beside it, script 17's text-level version on this data layer" | its p as script 17 printed it (#/1,000) or in the +1 form | both: the count #{null >= observed} and the +1 p; its own generator (a separate reported quantity, spec 0) | Count printed, so either form can be read off |

Added as coding continues (section 13 analyses).

**Revision of reading 12 (7 Nov 2026; spec section 12 D2(e), approved by AK 14:52 IST).** The row above is kept as
history. From the D2 run on, 13.1 M-342 takes 740's token share over the ELIGIBLE texts (the population of the
rate: "of the same population"), as 13.7 [09-G2] does. Prompted by the blind review V3 (M4), not by the value; it
LOWERS the all-texts ratio. Both values (`full_output.json`, 6 Nov run -> D2 run): concentration complete 2.7599 ->
2.7631; all 2.7999 -> 2.6540; R/L-L/R row 2.8332 -> 2.7070 (token share complete 10.279 -> 10.267; all 10.611 ->
11.194). Fixture `test_fixtures_s13a.test_m342_by_hand` re-worked by hand for the new reading.

**Readings surfaced by the blind re-implementation (Codex, 12 Nov 2026; kept, AK 01:09 IST).** Codex re-implemented
13.1-13.19 (except 13.4, 13.6, 13.9-13.11) from the spec alone. Its values differ from ours in 7 places, and our
library, run under its reading, reproduces each exactly
(`profile/paper_t10/independent_review/reproduce_codex_readings.py`, 26 of 26 checks; record:
`REVIEW_VERIFICATION_2026-11-12.md`). The two that change printed digits are kept as run, and recorded here:
- **R1 (13.1, Table 2 and M-342, R/L-or-L/R row).** Spec 8: "texts with `dir.` R/L or L/R only". We take `dir.`
  exactly R/L or L/R. Two rows carry `dir.` 'R/l', which 13.19 (its named script) reads as R/L. Counted as R/L,
  the row gives N 4,454 (ours 4,452) and top-82 starters 81.0% (ours 81.1%); the other printed values are unchanged
  at their printed precision.
- **R2 (13.17 [MARKER], 740 split).** We draw a/b for every 740 token of every SEAL:S text in the population, in
  row order, and measure the eligible texts. Script 19 (l. 276) draws over the texts it measures, so Codex draws
  over the eligible texts only. Both are a split of each 740 occurrence with probability 1/2 from one
  `Random(42)`; the draws differ. Codex's reading gives terminal 19.2/19.9% and enrichment 15.7/15.9 (D0;
  ours 19.4/19.7, 15.5/16.1), and 15.2/16.0 under D1 (ours 16.2/15.1); the unsplit baselines (15.8; D1 15.6) agree.
  The claim (the enrichment does not move) holds under both.
The other five confirm our reading or change nothing printed: K_tri/N in percent (no. 7); 13.16 P2's percentage
is CISI rows / analyzable rows, as the paper's sentence says; 13.16 P4 counts the malformed row apart; 13.18 F6
ranks "rarest" over all analyzable rows (script 18: the whole corpus); 13.8 G4b's mean length is over the eligible
texts (no. 15); 13.7 07-C stems keep `000` ("tokens", section 1; all-texts values only).
