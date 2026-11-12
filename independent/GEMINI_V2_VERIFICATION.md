# Assurance V2: Gemini's independent implementation of the headline section 13 numbers, verified (7 Nov 2026, 00:03-00:18 IST)

**Inputs:** `profile/paper_t10/independent_gemini_v2/` (impl_v2.py, output_v2.json, AMBIGUITIES.md, RUN_LOG.md;
committed UNCHANGED with this file) against our full run `submission/scripts_v2/out/full_output.json` (tag
`spec-frozen-2026-11-06-d1`, two byte-identical runs, SHA-256 794cabd1...). Entries: 13.4, 13.6, 13.9, 13.10, 13.11.

## Rules kept
Only its folder changed (`git status`); standard library only; it opens only the input and its output; freeze check
against the D1 tag exit 0; input SHA-256 equal; Python 3.11.9; two runs byte-identical (6560ee24...). CONFIRMED.

## Agreement (`compare_v2.py`, output saved)
347 values on both sides; **318 equal to 1e-9**, 29 differ; no key on one side only. Equal: every count, coverage,
once share and 740 rate; the slot test's observed counts and EXACT expectations; all of 13.6; 13.9's S4 groups, the
within-Harappa matched gap and find-spot interval, S6, S7 and S5 counts; all of 13.10 (M2 observed and null, M3,
sweep); all of 13.11 (cluster-aware and text-level).

## The 29 differences, each traced
| Group | Values | Cause | Whose reading | Effect |
|---|---|---|---|---|
| 13.4 slot null Monte Carlo (mc_mean, mc_se, p) | 11 | each draw shuffles a FRESH copy of every column (Gemini) vs the column's current order (ours) | both satisfy the registration ("in each draw, permute every column independently"); ours declared as SPEC_READINGS no. 16 at 19:02 on 6 Nov, before this comparison | p 0.0002 (ours) vs 0.0004 (all texts): both < 0.001; outcome A and the seal control (p > 0.01) unchanged; E[T] exact on both sides |
| 13.9 within-Harappa H3 line | 14 | Gemini shuffles the MULTI-SIGN Harappa texts (BUS rows without '/' kept); ours, section 7's entropy population (all lengths; BUS rows without '/' excluded) | both readable from 13.9 ("(multi-sign)" qualifies the S4 groups; the H3 line points to section 7); ours declared as SPEC_READINGS no. 6 on 6 Nov, before this comparison | e.g. complete texts, plug-in difference 0.298 (ours) vs 0.293 bits |
| 13.9 S5 K_tri/N at length 2 | 4 | 0 trigrams: ours "not defined" (None), Gemini 0.0 | ours follows section 7's "N = 0 -> NA" | reporting only |

**Decisive test** (`reproduce_v2_choices.py`, output saved): our library with Gemini's two choices switched in reproduces
all 28 of its draw-based values exactly. So the two programs differ only in those declared readings.

**Verdict: V2 PASSED.** No change to the frozen specification is needed: the differences are genuine ambiguities, read
one way by us BEFORE seeing Gemini's numbers, and none changes an outcome. The paper reports our values; the slot
test's p is reported as a bound ("p < 0.001") as the registration's presentation note already does.
