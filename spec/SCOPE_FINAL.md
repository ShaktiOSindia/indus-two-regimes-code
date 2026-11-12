# Scope of the corrected paper: Claude's considered recommendation (6 Nov 2026, 01:10 IST)

**AK 00:48:** "its not about what i agreed to its about what is right best in each aspect of each work ... i am also not
a field expert but what i want from you is every aspect thought of for recommending each". **Supersedes**
`SCOPE_ASSESSMENT.md` (00:37) and the criteria table of 00:43, which were made from script DESCRIPTIONS and text
searches and contained errors found tonight by reading the paper itself: script 11 is used for the two-sign caveat (not
a trigram measure); 09-G3 is POSITIONAL entropy (supports the seal regime), not the conditional entropy; 17-H5 IS in the
paper (battery row "majority-class baseline 79.9% balanced"); geography is the conclusion's contribution (3).

**How this was made:** the whole battery table (paper lines 947-992), the scalar section and Table 7 (501-606), the
conclusion's contributions (1000-1020), the abstract (46-77), script 09's and 17's own test lists, and the audit's
inventory of which script supplies each printed number (`audit_numbers.py`: check_in calls 01:6, 02:1, 04:3, 05:1,
06:2, 07:8, 08:8, 09:16, 10:9, 11:2, 12:5, 13:16, 14:2, 15:8, 16:7, 17:17, 18:3, 19:2; plus 62 recomputed values).
Questions asked of EACH analysis: does it answer a question a reader (reviewer, epigraphist, statistician, the
database's owners) would really ask; is its method sound under the corrected rules; does keeping it help or hurt the
paper's credibility; where would a reader look for it.

## MAIN TEXT (sound, and the paper's claims need them)
| Analysis | Why it stays | What changes |
|---|---|---|
| 01 Tables 1-3 | corpus description (praised); Yadav replication (abstract; praised "three times larger"); entropy as a SHORT screening table (R2.1) | Table 2 metrics via end marks + sign-list note; Table 3 with plug-in and Miller-Madow H3, token-matched gap stated |
| 10 within-class permutation null + its figure | the strongest entropy result: tablets fall far below their OWN shuffled baseline, so the structure is real order, not a small vocabulary; within one class, so no cross-class matching problem | shuffle within runs |
| 06 templates + 09-G5 slot null (own pre-registration R2.2) + 11 two-sign caveat + 09-G1 reuse at fixed length | the abstract's tablet regime; the slot claim; the honest "short texts" caveat and its answer | recomputed under the new rules |
| 07 seal regime + 09-G2 (10.9x enrichment) + 09-G3 positional gap | the abstract's seal regime; G3 shows only ONE edge is constrained (the conclusion's refuted "frame") | end-mark rule; the "which edge depends on the reading convention" sentence corrected (R1) |
| 08 geography: marker spans every sampled site; tablets 96.8% Harappa | conclusion contribution (3) "two regimes, two geographies"; abstract's 96.8% | the softened gradient (G4a/b, Table 6) goes to the appendix |
| 13 site control + site x length | abstract ("holds within Harappa"; "too sparse ... under site and length jointly") | coverage as spec s.7; H3 parts one descriptive line |
| 16-M1 grid (144); 16-M2 duplicate-provenance (short) | abstract (grid); M2 answers the sharpest published objection (Nair) | spec s.8; M2 defined |
| 17-H1 hold-out (G3 find-spots primary; G1 texts, G2 objects = old H7 beside) + H4 negative control + H3 positive control | PRAISED by both reviewers; the controls show the measure neither invents nor misses structure | spec s.7 |
| 17-H2 label-permutation null, made CLUSTER-AWARE | the headline's own null; as printed it shuffles copies one by one although copies come in sets, so its p-value is too precise; shuffling find-spot groups fixes it | new definition (find-spot groups) |
| 09-MOLD incised vs moulded reuse | answers "is reuse mould duplication?"; Meadow & Kenoyer now confirm incised tablets were hand-made copies | verdict wording from Decision 6 ("copies made in sets", not "Scribal") |
| Battery row "class label is a proxy for the text" | cheap descriptive check | recomputed |
| 14 Yadav 2013; 15 provenance counts; B' (limits) | honest prior-work credit; praised transparency; reviewer R1 asked for the chronology limits | spec s.8; B' |
| 19 sign identity (SHORT paragraph) | the epigraphers' sharpest objection to exact-identity measures; ICIT's documented sign decisions now cited | figure and details to the appendix |

## APPENDIX (worth keeping, not needed in the body)
08/09-G4 geographic gradient and Table 6 (a softened, length-confounded result); 18 Farmer-Sproat-Witzel checklist
(the paper takes no linguistic position); 17-H5 class prediction (redone with find-spot grouping, else it leaks like the
old hold-out); 19 details; the storage test details (one sentence in the main text replaces the G6 row).

## REMOVE (a scientific reason for each; needs AK's yes, the "never remove without asking" rule)
| Analysis | Reason |
|---|---|
| 02 damage confound | redundant: complete texts are now primary and every result is printed for both populations |
| 03 length, 05 CISI-only, 12 pooled length, 04's bootstrap CI (Table 7 and its "Refuted / Excl. 0" verdicts) | they argue that the CROSS-class entropy GAP is robust, inferentially; the corrected paper treats that gap as descriptive, and under fair (token) matching it is about a third of the printed size; the token-matched comparison with both populations replaces them. Keeping robustness claims for a demoted, smaller gap would mislead. (Miller-Madow stays as a Table 3 column.) |
| 09-G6 row (marker on R/L seals only) | it CANNOT detect the reading-direction error (R/L texts read the same under both rules: R1 point (c)); replaced by the storage test |
| Battery row "rows absent from the older database" | it rests on an older copy of the file; its data-vintage question is minor |
| 17-H6 catalogue-order blocks | a proxy for clustering, superseded by the real thing: find-spot grouping (G3) |
The discussion's contribution (4) "four scalar confound tests ..." is rewritten to the robustness programme that remains.

**Firmness:** this rests on the paper's text and the audit's inventory, not on descriptions. It changes only if new
evidence appears, and then the evidence is shown to AK first.

**[6 Nov 2026 02:07 IST] APPROVED by AK ("ok"):** the main text / appendix / remove split above, including the five
removals. Next: spec section 13 (every kept analysis), one short Gemini check, the freeze.
