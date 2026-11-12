# Independent implementation (roadmap C1) checked against the confirmation run (C4): verified by Claude, 6 Nov 2026

**Inputs:** Gemini's folder `profile/paper_t10/independent_gemini/` (impl.py, output.json, AMBIGUITIES.md, RUN_LOG.md;
written 15:58-16:11 IST per its log; committed UNCHANGED with this file) and our core output
`submission/scripts_v2/out/core_output.json` (commit 4172e9e; two byte-identical runs).

## Did it keep the rules?
- Wrote only in its folder (`git status` at 16:32: nothing else changed); `impl.py` imports only the standard
  library and opens only the pinned input and its own output. Python 3.11.9; freeze check exit 0; input SHA-256
  equal; two fresh runs byte-identical (`16422b2a...`). CONFIRMED.
- Whether it read a forbidden file cannot be proven; nothing in its code or log points to one.

## Agreement (`compare_outputs.py`, output saved)
1,548 values on both sides: **1,411 equal to 1e-9; 137 differ.** Every top-level key exists on both sides (ours has
one extra: the 13.21 curve points, not asked of it). Equal: all counts; coverage, top-10 key sets and repeat shares
for every class, population and copy rule; object rows; matched-N summaries; find-spot intervals; H3 and
Miller-Madow; the synthetic negative control; the 740 rates; Table 2 samples; Yadav 2013; all 144 grid cells
(same order, same gaps; min 9.66, median 29.21, max 54.18, none negative); 13.7's enrichment and positional
entropies; every B' cell, statistic and outcome (H / H).

## The 137 differences, each traced
| Group | Count | Cause | Who follows the frozen text |
|---|---|---|---|
| grid cell `sites` label | 48 | "2-city" vs "Harappa+Mohenjo-daro" for the same cells | label only, no number |
| hold-out (G3, G1, G2; both populations) | 75 | Gemini draws all 200 TAB:I splits, then all 200 SEAL:S splits; spec 0 and 7 say "in each draw, TAB:I then SEAL:S" in one generator | ours (literal); Gemini did not list this as an ambiguity |
| matched-token entropy (both populations) | 14 | Gemini's shuffled list keeps the 3 SEAL:S BUS rows without '/'; spec 1 excludes them "from pair/triple measures (all classes, all populations)" | ours (literal); H3 itself agrees because those rows add no trigram |

**Decisive test** (`reproduce_their_choices.py`, output saved): our library run with Gemini's two choices switched in
reproduces all 100 of its draw-based values exactly (0 differ). So the two programs differ ONLY in those two
procedural choices; the measured quantities agree. Size of the effect (ours | Gemini): TAB:I out-of-sample under
G3, complete texts 40.3 | 40.0; matched-token entropy gap, complete 0.328 | 0.328.

## Its ambiguity list (5 entries) against ours (`submission/scripts_v2/SPEC_READINGS.md`)
No. 1 (section 5's bare 740 rate includes one-sign texts) = our reading 3; no. 3 (grid median) = our reading 10;
no. 4 (B' D2a within each cell) and no. 5 (find-spot subsampling) = what both programs do; no. 2 (object key joined
with "+" instead of a tuple) gives identical numbers.

**Verdict: C4 PASSED for the independent-implementation scope (spec 0-8, 13.7, B').** No spec change is needed:
both differences are departures from explicit text, not ambiguities. The paper's numbers come from our run.
