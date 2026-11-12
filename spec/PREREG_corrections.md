# Pre-registration: the corrections after review (R1, reading order, first)

Written from 2026-11-03 22:15 IST and committed BEFORE any corrected re-run of the paper's analyses; the commit time
is the record. Each rule is approved by AK one decision at a time (`profile/paper_t10/CHANGES_SINCE_SUBMISSION.md`).
Any deviation after running is logged at the end, never edited into the sections above. Values already measured on
1-3 Nov (while checking Andreas Fuls's points) are listed as KNOWN, not as predictions. This file may be adapted
before any public deposit (publication rule: public material is built fresh and read by AK first).

## Status
| Rule | Decision | State |
|---|---|---|
| R1 reading order | Decision 1, AK 3 Nov 21:14 | rule fixed; points (a)-(e) APPROVED by AK 3 Nov 22:35 ("ok then recommend for each": the recommended option for each); amended before any re-run, see the note below the table |
| R2 data cleaning (completeness marks, `999`, line breaks, `000`) | Decision 2, AK 5 Nov 18:42 | DECIDED; the full rule text is `submission/SPEC_decision2_DRAFT.md` (reading the code, identity, populations, runs, end marks, repeats, every measure and its matching); it becomes binding at the freeze, after Codex review 1. Evidence: `profile/paper_t10/decision2_cleaning/DECISION2.md` |
| R5 wording corrections | Decision 5 | not yet decided; section to be added |

Amendment 3 Nov 22:37, before any corrected re-run (git keeps the 22:16 version): (a) and (b) gained the facts
found while re-checking them for AK (the expected fall of the 27.9% figure; the duplicate cells of the earlier
grid); the predictions in P3 were updated to match. No rule changed.

## R1. Reading order

### Rule
Every text is read in the reverse of its stored ICIT sequence: the first-read sign is the right-most stored sign and
the last-read sign the left-most. There is no exception for any value of the direction field (R/L, L/R, -, NR, T/B,
BUS, SYM, or the variants `R/l` and `R/L ` with a trailing space). The direction field is kept only as the record of
how a text was originally written.

The paper's earlier rule ("reverse unless the direction field is L/R") differs from R1 only for the texts marked
L/R: 215 analyzable texts, read backwards until now. Every other text is reversed under both rules.

### Source: the data producer's documentation, not our earlier rule
- ICIT online manual (`help_onlinedatabase.pdf`, the 21-page version served at
  https://www.user.tu-berlin.de/fuls/Homepage/indus/help_onlinedatabase.pdf, SHA-256 `0f48b10b31f4bb13...`, re-fetched
  identical on 3 Nov), p. 6, "Text Details": "All sign sequences are coded in such a way, that they must be read from
  right to left (thus, the text on seals is coded as it would be on the seal impression). The original direction of
  reading is indicated as follows: R/L (from right to left), L/R (from left to right), T/B (from top to bottom), BUS
  (bustrophedon)." Its example marks the initial sign as `231+` and the terminal sign as `+407`.
- Fuls, *Corpus of Indus Inscriptions*, pp. 16-17, 20 (Table 2.5) and 26, as recorded in
  `profile/fuls_2026-11-01/FINDINGS.md` s.2 and s.4h.
- The data producer pointed out the error himself (Fuls to the author, 29 Oct 2026).
- Checks on the pinned corpus with fresh code that imports nothing from the analysis library, each flipped by a
  planted fault (`profile/fuls_2026-11-01/decision1_direction_tests.py`, `decision1_unknown_direction.py`,
  `decision1_spec_by_direction.py`, with saved outputs): sign 740 at the left end of L/R texts 24.4% vs right 3.4%
  (R/L: 29.1% vs 1.2%); 31 L/R texts identical to an R/L text as stored vs 1 only when reversed; sign-pair
  similarity of L/R with R/L texts 0.654 as stored vs 0.059 reversed. Unknown-direction texts agree on weaker
  evidence (4 vs 0; 0.244 vs 0.149).

### Implementation
1. `chr_lib.reading_order(r)` returns the reversed stored sequence for every row.
2. `reference_impl.py` takes its reading-order rule from the manual sentence quoted above, quoted in its docstring.
   Its rule and core statistics are re-written by an author who does not read `chr_lib.py` (planned: Codex, run by
   AK, 7 Nov), so that the two implementations no longer share an assumption.
3. A gate (exercise 6: the untracked draft `check_reading_order.py`, to be reviewed with AK first) fails unless
   (i) both implementations give the reversed stored order on every row, and (ii) on the corpus, L/R texts behave
   like R/L texts as stored (identical-text and sign-pair tests above). The earlier rule must make it fail (mutation
   test, both directions).

### Points to settle before the re-run (Claude's recommendation; AK to confirm)
- **(a) Table 2 sample (script 01, `poscov`).** It leaves out every text whose direction is not R/L or L/R because
  "reading-order position is undefined without a known direction", which is false under R1. Recommended: include
  every analyzable text (one rule everywhere) and add one sensitivity row on the earlier sample (R/L and L/R only),
  so the replication's earlier basis stays visible. Alternative: keep the exclusion with a true reason (original
  direction recorded). The "27.9% of length->=2 inscriptions (well-defined direction)" sentence follows this choice.
  **APPROVED: include every text + the sensitivity row.** Expected cost, estimated from the counts already measured
  (decision1_direction_tests T1: 740 at the stored left end of only 2.3% of 258 unknown-direction texts, mostly
  pottery): the 27.9% falls to about 26-27% and the 2.8x concentration to about 2.7x; the sensitivity row keeps the
  earlier sample's figure visible.
- **(b) Specification grid (script 16).** Its direction fork has three values: the paper's rule, as stored, and
  reversed. The grid measures whole-text coverage, which a consistently applied direction cannot change (as stored
  and reversed gave identical values in all 144 cell pairs, measured 3 Nov between 22:15 and 22:16 while writing this point, before
  this file was committed); after R1 the paper's rule equals "reversed". Recommended: drop
  the fork (432 -> 144 cells) and state in the corrections note that under the earlier rule all 144 cells were also
  positive (weakest +7.2). The abstract's "all 432 cells" changes with it. Alternative: keep three labelled values
  (ICIT order, stored order, earlier rule) to stay at 432.
  **APPROVED: drop the fork (144 cells).** Fact found while re-checking: as-stored and reversed are identical BY
  CONSTRUCTION for whole-text coverage (all 144 pairs equal), so the submitted "432 analytic forks" counted 144
  exact duplicates and 144 cells under the wrong rule: only 144 were genuine specifications. A wording correction
  for the corrections note (Decision 5). If Decision 2 adds a genuine fork (e.g. completeness by ICIT's end marks),
  the grid may grow again, never with duplicate cells.
- **(c) Battery G6 (script 09: 740-final on exact-R/L texts vs all).** It cannot detect a wrong rule for L/R texts,
  because R/L texts read the same under both rules. Recommended: replace it with the storage test above, which the
  earlier rule fails.
- **(d)** As Implementation 2-3.
- **(e) Multi-line texts** (`/`, 118 texts): R1 reverses the whole stored string, so line order reverses with it.
  Whether lines are split for pairs and triples is Decision 2 (R2). R1 runs first on the strings as now.

### Predictions (fixed now)
**P1. Must not change at all (any change is a bug):** every number that does not depend on the order of signs
within a text: corpus and class counts, tokens and distinct signs, mean lengths, unigram entropies (H1), shares by
site, type or catalogue (e.g. 96.8% Harappan, 88.6% with a CISI number), sign frequencies, and the slot statistic T
(texts holding two distinct members of {032, 033, 034}: set membership; observed 0).

**P2. KNOWN (measured 1-3 Nov under R1; not predictions):**
| Quantity | As printed | Under R1 |
|---|---|---|
| Hold-out retention, incised tablets / square seals | 94% (41.1 -> 38.7) / 35% (3.7 -> 1.3) | 95% (43.3 -> 41.2) / 36% (3.8 -> 1.4) |
| Top-10 coverage, TAB:I / SEAL:S | 40.4% / 3.0% | 42.8% / 3.1% |
| Miller-Madow entropy gap | 1.229 | 1.269 |
| ICIT 740 ends multi-sign square seals | 35.1% | 35.6% |
| Top-23 reading-order enders | 75.56% | 77.63% |
| Texts appearing once, TAB:I / SEAL:S | 27% / 88% (27.3 / 88.2) | 25.2% / 87.6% |
| Grid cells already using R1 ("reversed") | (inside the 432) | 144 of 144 positive; weakest +8.6, median +28.4 |

**P3. Order-dependent, not yet measured: predicted direction.**
- Size limit: only the 215 L/R texts change order: 61 of 725 multi-sign incised tablets (8.4%) and 30 of 1,617
  multi-sign square seals (1.9%). A seal-side share can therefore move by at most 1.9 points, a tablet-side share
  by at most 8.4 points.
- Tablet trigram entropy (H3, TAB:I) falls or stays: the earlier rule turned L/R tablets' trigrams around (e.g.
  (400, 740, 176) against (176, 740, 400)), adding spurious distinct trigrams. Square-seal H3 changes little.
- 740 terminal enrichment (10.9x) rises or stays (end share up, non-end share down). The "27.9%" final share: on the
  earlier sample (sensitivity row) rises or stays; on the approved full sample (a) falls to about 26-27%.
- Seal stems "92% unique; 87% appearing once" move by at most 1.9 points.
- The within-Harappa reuse gap (+35.7 points) rises or stays: Harappa holds 140 of the 215 L/R texts and tablet
  coverage rises.
- The slot test (R2.2): T stays 0 (P1); the matched-null expectation (8.7) may move a little (61 tablets change
  positions); its verdict (p(T=0) <= 0.01) is predicted to stand.
- The initial-slot claim ({032, 033, 034} at the start of tablets): their initial share on TAB:I rises or stays.

**P4. Mechanical check:** all audited values are computed under the earlier rule and under R1. Every value that
changes must be order-dependent (P2 or P3); every P1 value must be identical. Any exception stops the work for
discussion with AK.
[Amendment 4 Nov 01:20, before any run: "audited values" alone would miss the 264 stdout-matched numbers, whose
audit record holds the paper's constant, not the code's value. P4 therefore compares the full printed output of
all 19 scripts plus the audit's report and state, against the baseline in
`profile/paper_t10/baseline_pre_corrections/` (tag `pre-corrections`; two runs identical; see its BASELINE.md).]

### What counts as "the claim holds" (fixed now)
The headline claims, as printed: (1) incised tablets reuse whole texts far more than square seals (top-10 coverage
gap positive; tablets' hold-out retention far above seals'); (2) square seals carry a shared marker at one edge
(ICIT 740 ends about a third of multi-sign square seals, about ten times enriched there); (3) the inversion holds
within Harappa and in every grid cell. Each holds under R1 if it keeps its sign and its printed wording stays true
with the numbers updated. If any reverses or its wording becomes false: stop and report to AK before any other
correction.

### Order of work
R1 alone first, on the strings as now (no other correction): snapshot every audited value before and after (P4).
Then each further rule one at a time (R2 ...), with a snapshot after each, so every change in the paper has one
cause.

## Deviation log (filled after running)
(empty)
