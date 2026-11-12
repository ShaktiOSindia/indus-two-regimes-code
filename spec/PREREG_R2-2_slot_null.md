# Pre-registration: R2.2, the {032,033,034} slot under a length- and position-matched null

Written and committed BEFORE the analysis below was run on real data. The decision
rule was approved by AK on 2026-10-24 ("p(T=0) <= 0.01"). Any deviation after running is
logged at the end, never edited into the sections above.

## Why
Reviewer 2, question 2: *"The expectation of about 33 co-occurrences for {032, 033, 034}
appears to be computed from marginal frequencies alone. Since about half of the tablets have
only two signs and these signs are mostly in initial position followed by ICIT 700,
positional and length constraints alone may reduce the expected number considerably. An
expectation conditioned on text length and position would make this comparison more
convincing."*

The paper (Section 4, and Table 8 row "Slot exclusivity is chance") compares the observed
0 with ~33 expected "under independence" (script 09, G5: sum over sign pairs of
count(a) x count(b) / N, ignoring length and position).

An earlier plan (RESUME_HERE, 2026-10-24) proposed a *within-inscription* permutation null.
That null is degenerate for this statistic: co-occurrence is set membership, which a
reordering inside a text cannot change. It is not used.

## Population (identical to G5)
TAB:I, analyzable corpus (the pinned 5,679-row file, SHA-256 0053bafc...; rows that are
entirely ICIT-000 excluded), each text gated (ICIT-000 removed) and in reading order:
`[gate(reading_order(r)) for r in corpus if r.artefact_type == "TAB:I"]`, all gated
lengths. N = 898.

## Statistic
T = number of texts containing at least two DISTINCT members of {032, 033, 034}.
Observed on TAB:I: T_obs = 0 (G5; script 18).

## Null model N1: length- and position-matched column shuffle
For each gated text length L, take the L position-columns of all texts of that length; in
each draw, permute every column independently across those texts. Each text keeps its
length; every (length, position) cell keeps its exact multiset of signs; association
between positions within a text is destroyed. Length-1 texts cannot reach T and are
carried unchanged.

- B = 10,000 draws, `random.Random(42)`, columns permuted in sorted (L, p) order.
- Monte Carlo p-value: p = (1 + #{draws with T_null <= T_obs}) / (1 + B).
- Cross-check: the exact expectation E[T] under N1. Positions are independent across
  columns and each position is uniform over its column, so for a text of length L with
  column sign shares q_p(s): P(<=1 distinct slot sign) = P(no slot sign) + sum over s in
  slot of [prod_p (1 - Q_p + q_p(s)) - prod_p (1 - Q_p)], with Q_p = sum over slot of q_p(t);
  E[T] = sum over texts of (1 - that). The Monte Carlo mean must agree with E[T] to within
  3 Monte Carlo standard errors, or the implementation is wrong and nothing is reported
  until it is found.

## Decision rule (primary, approved)
- **A: p <= 0.01.** The signs never co-occur, although a null that keeps length and
  position expects E[T]. The exclusivity is not explained by position alone. Keep the claim,
  with the conditioned expectation replacing ~33.
- **B: p > 0.01.** Position explains the exclusivity: the three signs share one initial slot,
  so they cannot co-occur in the texts where they sit. Drop the "0 vs ~33" comparison. The
  slot is evidenced by its shared position and shared right neighbour (ICIT 700), not by
  exclusivity beyond position. Report E[T] and p.

## Control (secondary): the same test on square seals
Same population definition with SEAL:S, same null, same B and seed. T_obs(SEAL:S) = 11
(script 18). p_seal = (1 + #{T_null <= T_obs}) / (1 + B).
- If p_seal > 0.01: the null does not manufacture "exclusivity" where co-occurrence
  occurs, and seals show none beyond position. Consistent with "specific to the tablet
  classes".
- If p_seal <= 0.01: seals ALSO co-occur less than position predicts. The paper's
  "specific to the tablet classes" must soften to: rarer than position predicts in both
  classes, absent only on tablets. This holds under either A or B.

## Paper wording, fixed in advance
- Outcome A, Section 4: "...and none contains two or more, against $E$ co-occurrences
  expected when every tablet keeps its length and every position keeps its sign
  distribution ($p = X$; script~09, G5b)". Table 8 row: "0 co-occurrences vs. ${\sim}E$
  under a length- and position-matched null ($p=X$) | Slot".
- Outcome B, Section 4: "...and none contains two or more. That alone is not evidence:
  the three signs share one initial position, and a shuffle that keeps every tablet's
  length and every position's signs expects only $E$ co-occurrences ($p = X$; script~09,
  G5b). The slot is defined by that shared position and by a common right neighbour
  (ICIT~700 follows a member 71\% of the time)." Table 8 row: "Slot exclusivity beyond
  position | 0 vs. ${\sim}E$ expected ($p=X$) | Positional". Abstract: "a mutually
  exclusive initial slot" becomes "a single shared initial slot".
- The ~33 (unconditioned) figure is retained once, attributed to independence of
  marginals, so the change is visible.

## Deviation log (filled after running; sections above are never edited)
- **Implementation (not a design change).** Each draw places the slot-sign entries of a
  column on a uniformly random set of that length's texts, instead of permuting whole
  columns. The null distribution is the same, because the other entries cannot change T
  and columns are permuted independently. Before the real run this was verified against
  brute-force enumeration of every column arrangement on three toy datasets (up to 124,416
  arrangements each): the exact E[T] matched to 1e-9, and the Monte Carlo matched E[T] and
  P(T=0).
- **Presentation.** p is printed as "none of 10,000 shuffles reached zero ($p<0.001$)",
  not "p = 0.0001". With no draw at or below T_obs, (1+0)/(1+B) is the smallest value B =
  10,000 can show, so it is a bound, not an estimate.
- **Wording, to stay within the 6,000-word limit (measured 6,002 before the trim):** the
  Outcome A sentence was shortened without changing its content ("predict", not "would
  predict"; "shuffles", not "such shuffles"), and two words were cut elsewhere in the
  paragraph ("a slot member" -> "a member"; "charge precisely that" -> "charge that").

## Result (run once, 2026-10-25, corpus SHA-256 0053bafc...)
- **TAB:I:** observed 0; E[T] = 8.72 exactly (Monte Carlo 8.70, se 0.025; agrees);
  p = 0.0001 (no draw reached 0). **Outcome A**: the exclusivity is not explained by
  length and position.
- **SEAL:S control:** observed 11; E[T] = 16.00 (Monte Carlo 16.04); p = 0.0869 > 0.01. No
  exclusivity beyond position. This is consistent with "specific to the tablet classes".
- **Reviewer 2 was right that position matters:** conditioning cuts the expectation from
  ~33 to 8.7. Zero co-occurrences against 8.7 is still decisive (a Poisson approximation
  gives e^-8.72 = 0.00016).
