# Measurement specification, Decision 2 part: FROZEN 6 Nov 2026 (v3 sections 0-12 + section 13)

**FROZEN (AK 6 Nov 2026 11:53 IST: "ok", after reading Gemini review 3's verification).** Reviewed before freezing:
Codex review 1 (sections 0-12; 16 of 16 comments confirmed and fixed), Gemini reviews 1 and 2 (sections 0-12:
"FREEZE-READY"), Gemini review 3 (section 13) with Claude's verification (`profile/paper_t10/gemini_review3/
GEMINI3_VERIFICATION.md`: its coverage claim refuted, the gaps fixed). The frozen text is this file at git tag
`spec-frozen-2026-11-06`; its commit and the git blob ids of every file it relies on are in
`submission/FREEZE_RECORD.md`, and the confirmation run refuses to start if any of them differs. From now on every
change goes into section 12 with its date, reason and AK's approval; the earlier status notes below are history.

**v3 (5 Nov 2026, written from the clock reading 22:49 IST):** Gemini review 1's 19 comments, each verified by Claude
(`profile/paper_t10/gemini_review1/GEMINI1_VERIFICATION.md`), written in: one generator per measure with TAB:I then
SEAL:S per draw; exact percentile index; exact serialization and object key; hold-out with a fresh copy each draw and
retained in percent; cluster-interval pseudocode; plug-in entropy difference primary, Miller-Madow beside; single-line
defined; find-spot rule covering all 51 area values that end in '-'; the Yadav protocol (>= 2 signs, as script 14);
Table 2's approved sensitivity row; the specification grid; more fixtures.
**Status (5 Nov 2026, 21:34 IST): v2 DRAFT.** v1 (17:05, AK's choices 18:42) is in git history. v2 writes in the fixes
for Codex review 1's 16 comments, each verified by Claude (`profile/paper_t10/codex_review1/CODEX1_VERIFICATION.md`),
AK's answers A-G (21:27: "ok go ahead with your recommendations for all"), and one rule Claude found while choosing test
rows (mound-only find-spots, section 6). Next: an independent review of this text (Gemini, a different model), then
AK approves and it is FROZEN (commit hash recorded here). After freezing, every change goes into section 12.
Reasons and evidence: `profile/paper_t10/decision2_cleaning/DECISION2.md`. No exploration result is written here.

**AK's choices:** side is the unit; complete texts primary for whole-text, pair/triple/entropy and first/last measures,
all texts beside; every copy (D0) primary, one copy per find-spot (D2a) beside every headline whole-text figure, Fuls's
rule (D1) printed for every measure, D2b in an appendix; entropy compared at matched trigram tokens and DESCRIPTIVE only;
hold-out primary grouping = find-spots (G3), texts (G1) and objects (G2) as sensitivity rows; malformed codes excluded
and listed.

## 0. Conventions
- Python 3.11; the input is read as bytes, its SHA-256 must EQUAL
  `c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98`, else the run stops; decoded as UTF-8 (BOM
  removed); rows via `csv.DictReader`; the ROW INDEX is the 0-based position in the file. Every list of rows is kept in
  row-index order unless a step says otherwise.
- Field values are used after removing leading and trailing whitespace only. A value is MISSING if, after also removing
  every '-', '?' and space, it is empty.
- Randomness: every reported quantity (one measure on one population variant) creates ONE generator
  `random.Random(42)` at its start; when it covers TAB:I and SEAL:S, each draw handles TAB:I first and then SEAL:S in
  that same generator; draws follow exactly the order stated for that measure. 200 draws. For a sorted list g of n
  draws, p5 = g[math.floor(0.05 * (n - 1))] and p95 = g[math.floor(0.95 * (n - 1))], by exact index (no interpolating
  routine such as numpy.percentile). The SHA-256 of each measure's drawn index lists is saved (draw fingerprint).
- Units: coverage and shares in percent; differences in percentage points; entropy in bits.

## 1. Reading the code (`text`)
- Grammar: [left mark] core [right mark]; a mark is one of '+', '[', ']' and is taken only as the first / last
  character; core = lines separated by '/'; line = tokens separated by '-'; token = exactly three digits.
- If the core contains '+' (a text part) or '++' (an eroded part), the run STOPS (none in this file; checked).
- A row whose core has an empty or non-three-digit token is MALFORMED: excluded from every measure and listed in the
  exclusions table with its id (this file: row 5406.1, a rod; its code is not reproduced in this copy).
- Tokens: `000` = one eroded sign (a sign position, not legible); `999` = a blank space, NOT a sign; any other token =
  a legible sign.
- Reading order (R1): every stored code is read right to left: a line in reading order is its stored tokens reversed;
  the lines in reading order are the stored lines reversed. Reading START = stored RIGHT end; reading END = stored LEFT.
- Multi-line: a row with '/' OR `dir.` = BUS. A BUS row without '/' cannot be split: it is EXCLUDED from pair/triple
  measures (all classes, all populations) and KEPT for whole-text measures. First/last measures use SINGLE-LINE texts
  only: no '/' in the code AND `dir.` not BUS (so every row with '/' and every BUS row is excluded from them).
- Analyzable: not malformed and at least one legible sign. Object id = the part of `id` before its last '.'.

## 2. Identity of a text
- Key = (stored right mark, tuple of lines in reading order, each a tuple of its tokens with `999` removed and `000`
  kept, stored left mark); a missing mark is "". Serialization (for ordering), exactly:
  `right + "|" + "/".join("-".join(line) for line in lines) + "|" + left`. Two texts are the same text only if their
  keys are equal.

## 3. Units and populations
- Unit: the SIDE (one ICIT text). Object rows beside it: (a) share of OBJECTS carrying at least one of the class's top-10
  keys (top-10 learned on the side-level population; an object = its sides that are in the population; each object
  counted once); (b) whole-object identity: object key = `tuple(sorted(serialization(k) for k in side_keys))` over
  its sides in the population (sides order-free; duplicate side keys kept).
- Whole-text measures use texts with at least 2 legible signs.
- Primary population: COMPLETE texts (`complete` = Y) for whole-text, pair/triple/entropy and first/last measures; ALL
  analyzable texts printed beside each. (B' uses all texts as its own registered exception: see the B' amendment.)
- Classes: every ICIT `type` is measured; the contrast is TAB:I against SEAL:S.

## 4. Runs (pairs, triples, entropy)
A run is a maximal sequence of legible signs within one line, in reading order; `000`, `999` and a line break end it.
Pairs and triples are counted only inside runs.

## 5. First and last sign (740-final rate)
Population: the primary population, every copy, single-line texts (no '/' and not BUS; section 1). Eligible = the stored LEFT mark
is '+' and the reading-final token is legible. Rate = texts whose reading-final sign is 740 / eligible texts; NA if no
eligible text. The reading-initial sign likewise (stored RIGHT mark '+'). All-texts row beside.

## 6. Repeated identical texts
- D0: every copy. D1 (Fuls, *Catalog* p. 71): one copy per (site, type, stored code string). D2a: one copy per (site,
  type, stored code string, find-spot). D2b: a KNOWN D2a find-spot becomes (site, area-section, room-grid, depth), each
  of the last two "" when MISSING (section 0); an UNKNOWN find-spot stays ("row", row index).
- Find-spot = (site, area-section). It is UNKNOWN, and the row is its own find-spot ("row", row index), if area-section
  is MISSING, or ends in '-' WITHOUT naming a trench (the value does not contain "trench", any case): an area recorded
  without a trench or section ("F-", "DK-", "KLB-1-", "Castle-", "Middle Town-", ...). Of the 51 values that end in '-'
  (1,312 rows), 41 are UNKNOWN and 10 name a trench ("Trench B-", ...; 16 rows) and stay KNOWN find-spots, like
  "FTrench I". The full classified list is part of this specification:
  `profile/paper_t10/gemini_review1/area_values_ending_dash.txt`. Unknown find-spots make the D2a and G3 rows less
  strict for those rows (copies whose spot is not recorded are never grouped); the paper says so.
- The copy kept is the row with the smallest row index.
- Reporting: D0 primary; D2a beside every headline whole-text figure; D1 for every measure (for whole-text coverage with
  the note that it reduces tablets to the 10/N floor); D2b in the appendix, stating the unequal fill rates (room-grid
  TAB:I 33% / SEAL:S 60%; depth 44% / 75%).

## 7. Measures (all on lists in row-index order)
- **Top-10 keys:** count texts per key; order keys by (count descending, serialization ascending); take the first
  min(10, number of keys). **Coverage** = 100 x (sum of their counts) / (number of texts). (Coverage cannot depend on
  the tie rule; the key SET can.)
- **Repeat share** (no 10/N floor) = 100 x (texts whose key occurs at least twice in the class) / (number of texts).
- **Matched-N robustness summary** (whole-text measures): n = the smaller class's number of texts; the smaller class is
  used whole; in each draw the larger class is subsampled with `rng.sample(rows, n)`; the measure is recomputed on the
  draw (top-10 re-learned); difference = TAB:I value - SEAL:S value; report the mean, p5, p95. It describes sensitivity
  to subsampling; it is NOT a significance test.
- **Find-spot resampling sensitivity interval** (whole-text measures): for each class, clusters = its D2a find-spots
  ordered by first row index, each cluster's rows in row-index order (an unknown find-spot is a one-row cluster). Loop
  until 200 valid draws: `chosen_tab = rng.choices(clusters_tab, k=len(clusters_tab))`, then `chosen_seal =
  rng.choices(clusters_seal, k=len(clusters_seal))`; each class's resampled rows = the chosen clusters' rows in the
  order drawn (a cluster drawn twice appears twice); if either class has fewer than 2 texts the draw is discarded and
  the loop continues in the same generator; n = the smaller resampled size; a class larger than n is subsampled with
  `rng.sample(rows, n)` (TAB:I first; a class of exactly n is not subsampled and uses no draw); top-10 re-learned;
  difference = TAB:I - SEAL:S. Report p5 and p95; it is NOT a confidence interval.
- **Conditional trigram entropy H3** (over runs): N = trigram tokens; c(t) = count of trigram t; c(x) = count of its
  first two signs as the start of a trigram; H3 = - sum over t of (c(t)/N) log2(c(t)/c(x)); Miller-Madow, exactly:
  `mm_h3 = h3 + (k_tri - k_ctx) / (2.0 * n * math.log(2))`, k_tri = distinct trigrams, k_ctx = distinct
  trigram-starting pairs; N = 0 -> NA.
  K_tri / N reported beside. DESCRIPTIVE only: no inferential claim.
- **Entropy comparison at matched trigram tokens:** T = the trigram tokens of the class with FEWER tokens (its H3 fixed);
  in each draw the other class's texts are shuffled (`rng.shuffle` of a row-index-ordered copy) and taken in that order
  until their cumulative trigram tokens are at least T (the text that crosses T is kept); H3 of the taken texts;
  difference = SEAL:S - TAB:I of the PLUG-IN H3 (reported primary; same as Table 3's estimator), with the Miller-Madow
  difference reported beside it from the same draws; report the mean, p5, p95 and the mean achieved tokens.
- **Predictive hold-out** (descriptive): groups: PRIMARY G3 = D2a find-spot (unknown find-spot = own group);
  sensitivity G1 = each text its own group, G2 = object id. Groups are listed in order of first row index. One generator
  per grouping; in each draw, for TAB:I then SEAL:S: a FRESH copy of that class's canonical group list is shuffled with
  `rng.shuffle(copy)`, then groups are taken in that order into fold 1 while fold 1 holds fewer than half of the class's
  texts (`len(fold1) < len(texts) / 2`), the rest into fold 2. The top-10 keys are learned on fold 1; in-sample = fold-1
  coverage of those keys; out-of-sample = share (percent) of fold-2 texts whose key is among them; retained = 100 x out
  / in (0 if in = 0). Report means, p5, p95, for TAB:I and SEAL:S. Retained values are descriptive (a split-sample
  summary), not a calibrated test.
- **Synthetic negative control:** sign frequencies = all legible signs of all analyzable rows of all classes (pooled);
  vocabulary in ascending code order; each class's length vector = the legible lengths of its texts in the population,
  in row-index order; in each draw, for TAB:I then SEAL:S, one synthetic text per length, `rng.choices(vocab, weights,
  k=length)`, keyed as ("", (tuple(signs),), "") (one line, no end marks); coverage of each class; gap = TAB:I -
  SEAL:S; report max over draws of abs(gap) (unsigned) and the mean gap, beside the observed raw gap. The paper says only that class size and length under an i.i.d.-sign null do not produce
  the gap; it rules out nothing else (production, find-spot, collection).

## 8. Comparisons with published work (protocols)
- **EBUDS-like (Table 2):** complete texts; single-line (no '/', not BUS); one copy per identical key across the whole
  corpus (all sites and types; the copy kept = smallest row index); legible length 1 to 14. Not reproducible from ICIT
  and stated in the paper: EBUDS's "doubtfully read" signs (ICIT has no such mark), the 1977 sign list (417 signs vs
  ICIT's 713) and corpus. Always called "EBUDS-like".
- **Table 2, full column** (R1 point (a), approved 3 Nov): every analyzable text, whatever its direction; plus ONE
  sensitivity row on the earlier sample (texts with `dir.` R/L or L/R only).
- **Yadav 2013 (script 14):** texts of ANY completeness with at least 2 legible signs (as script 14; Yadav's four
  frequent texts are all of 2-3 signs); the four most frequent keys over all such texts of all classes and sites (ties
  as in section 7); their share of all such TAB:I texts at Harappa; beside it Yadav's 36% of Harappa miniature-tablet
  lines, with the stated differences (her M77 lines and "miniature tablets" category; our ICIT sides and TAB:I).
- **Specification grid (script 16; R1 point (b), direction fork dropped):** every combination of: `000` in the identity
  key (kept as placeholder, as section 2 | removed); minimum legible length (2 | 3); sites (all | Harappa | Harappa and
  Mohenjo-daro); population (all texts | complete only); tablet class (TAB:I | TAB:I and TAB:B); top-N (5 | 10 | 20):
  2 x 2 x 3 x 2 x 2 x 3 = 144 cells; a cell is run only with >= 30 texts in each class; statistic = raw top-N coverage
  of the tablet class minus SEAL:S (as registered); report how many cells are positive, the minimum, the median, the
  maximum, and every negative cell.

## 9. Not settled here
How strongly the paper interprets tablet repetition and the headline wording (Decision 6; the hold-out's PRIMARY
grouping is now fixed as G3); object-level nulls are NOT part of this run. (Sign-identity sensitivity is now section
13.17.)

## 10. Required tests before the run (fixtures written independently of the production parser)
- Hand-written expected parses for: 605 (a `999` inside), 2832 (three lines), 1562 and 1528 (doubtful ends, *Corpus*
  p. 27), 5406.1 (malformed -> excluded), 110.1 (BUS without '/'), 21.1 (several `000`), 207.1 (`000` at an end), and
  find-spot fixtures 160.1 (area missing), 162.1 and 235.1 (mound-only "F-"), 228.1 (room-grid, no depth), 207.1
  (room-grid and depth), and 221.1 (Trench VI Stratum III, for B'). Added in v3: 262.2 and 2731.1 (a mark at one end
  only); the first "Castle-" row (Dholavira; unknown find-spot) and the first "Trench B-" row (Lakhanjo-daro; known);
  objects 262 and 1168 (side order differs between tuple and serialization sorting); the first Mound F Stratum III row
  outside Trench VI (excluded from B's cells).
- Synthetic fixtures: a tie at the 10th key; a token-overshoot case; H3 and Miller-Madow on tiny sequences computed by
  hand; a hold-out fold split with unequal groups; a cluster resample with a repeated cluster.
- Mutation tests: changing each rule above must make at least one fixture fail.
- Regression anchor only: under the SUBMITTED rules, the parser reproduces `sanitized_corpus.json` for 5,679 of 5,679
  rows and the paper's Table 3 (SEAL:S H3 1.2960, TAB:I 0.2238).
- Two runs of the whole command give byte-identical outputs and identical draw fingerprints.

## 11. Exclusions table (filled by the run)
Every excluded row with its reason (malformed; no legible sign; fewer than 2 legible signs where required; BUS without
'/' for pair/triple measures; any '/' or BUS for first/last measures).

## 12. Deviation log (after freezing)
- **D1 (6 Nov 2026, 23:12 IST; approved by AK 23:11 "ok approve the fix").** 13.7 [07-A]: the legible-length profile
  and mean are taken over ALL analyzable SEAL:S texts of the population, as script 07 does and as 13.3 [A] does for
  tablets; the rest of 13.7 stays on multi-sign texts. Reason: assurance V1 (`profile/paper_t10/assurance_v1/
  V1_REPORT.md`) found that the frozen text departed from script 07 without stating it (script 07: mean over all
  1,754 seals; the frozen text: multi-sign only), which would put the tablet and seal length profiles on different
  bases. The text of 13.7 above is left unchanged; this entry amends it. New tag: `spec-frozen-2026-11-06-d1`.
- **D2 (7 Nov 2026, written after the clock reading 14:56 IST, BEFORE any code; approved by AK 14:52: "im ok with all
  the recommendation only if done fully and truly with needed capabilities and aspects check").** Sources: assurance
  V3 (`profile/paper_t10/assurance_v3/V3_VERIFICATION.md`), the gap analysis (`profile/paper_t10/gap_analysis/
  GAP_SPEC_TO_OUTPUT.md`, checked in `GAP_VERIFICATION.md`), the proposal (`FIX_BATCH_PROPOSAL_2026-11-07.md`). The
  text above is left unchanged; this entry amends it. Each item: what the run does from now on.
  (a) **13.8 site count:** "distinct sites with a SEAL:S text" is a corpus description: counted over ALL analyzable
  texts in both population blocks (the general rule of 13 for corpus descriptions).
  (b) **Fingerprints (sections 0, 10):** every draw-based quantity of both runs saves its fingerprint (SHA-256 of the
  JSON of the drawn index lists, in draw order; where a draw is not over indexes, of the drawn values): core in
  `out/core_fingerprints.json` (adding B': matched-N and D2a per variant and cell), section 13 in a new
  `out/full_fingerprints.json`, one key per quantity. No value changes.
  (c) **D1 (Fuls's rule) for every measure** (section 6), applied AFTER the population, class and legible-length
  filters (section 6-7 order), by one copy per D1 key at the end of the population selector; measures that select
  rows themselves apply the same rule after their own filters (Table 2 "full" and its R/L-L/R row, 13.1 M-342, Yadav
  2013). Written to `out/core_output_D1.json` and `out/full_output_D1.json` under the D0 keys, so the D0 files keep
  their bytes. **Not computed under D1 (reason):** corpus counts and descriptions (counts of rows, types, sites,
  exclusions; 13.1 Table 1; 13.8 site shares and site counts; 13.16) because they describe the file, not a measure;
  section 6's own D0/D1/D2a/D2b quantities (already printed); EBUDS-like (its own corpus-wide one-copy rule, stricter
  than D1); 13.4 and 13.19 (registered protocols); 13.10 (it tests duplicates itself); the D2a statistic of B' (D2a
  is finer than D1). The synthetic negative control keeps its pooled sign weights (section 7 defines them over all
  analyzable rows, a corpus description); only the class texts follow D1. Where D1 reduces a class to the 10/N
  floor, the paper says so (section 6).
  (d) **D2a beside every headline whole-text figure** (section 6), same mechanism: matched-N and the find-spot
  interval (both measures), hold-out G3/G1/G2 (copies reduced BEFORE the grouping), the synthetic negative control's
  observed gap, the grid, 13.9 [S4] within-Harappa matched-N and interval. Written to `out/core_output_D2a.json` and
  `out/full_output_D2a.json` under the D0 keys.
  (e) **Reading 12 revised (13.1 M-342):** 740's token share is taken over the ELIGIBLE texts (the population of the
  rate, "of the same population"), as 13.7 [09-G2] does; both values are recorded in `SPEC_READINGS.md`.
  (f) **D2b fill rates (section 6):** computed by the run over ALL analyzable rows of TAB:I and of SEAL:S: the share
  whose room-grid is not MISSING and the share whose depth is not MISSING; the paper prints the run's values.
  (g) **B':** frac>0 (share of draws with a positive gap) beside mean, p5, p95, for the matched and the D2a
  statistic ([S8] "unchanged"); each 740-final rate with its eligible count and hits.
  (h) **Hold-out:** in-sample p5 and p95 beside the in-sample mean (section 7).
  (i) **Data facts** printed by the paper and computable from the pinned file: the '-'-ending area values and their
  rows (section 6: 51 / 1,312; 10 naming a trench / 16 rows), the rows with an UNKNOWN find-spot per class, the row
  order checks of 13.10 (ICIT id order, CISI same-prefix order), the Mound F row count of B'. Not computable here and
  cited from their records: ICIT's 713 signs (spec 8), "22 of 22" and "137 of 364" (B').
  (j) **Small outputs:** 13.10 [M3] sweep: every cell with its gap; 13.14: the N of each class; 13.7 [07-B, 09-G3]:
  the all-texts row beside the complete-text one (general rule).
  (k) **Checks before the run:** fixtures and planted errors for the copy keys and "copy kept = smallest row index",
  and for each rule the gap analysis found untested where a fixture can be written; the D0 files must be
  byte-identical to the 6 Nov run except the keys added by (b) and (f)-(j) and the values changed by (a) and (e) (a
  diff gate lists every changed key); the existing D1/D2a coverage keys must equal the new mechanism's values.
  New tag: `spec-frozen-2026-11-07-d2`.
- **D3 (11 Nov 2026, written after the clock reading 03:08 IST [corrected: first written as 03:09, a time not read from the clock; tag spec-frozen-2026-11-11-d3 holds that text and is superseded by -d3-r1], BEFORE any code; decision A3 approved by AK 11 Nov
  03:07: "3approved"; record `profile/paper_t10/decision_A3_reproduction/DECISION_A3.md`).** Reason: the code-only
  public deposit (decision A2) must run for readers who cannot obtain the pinned file. **No computation changes.**
  (a) `load_rows(path, pin)`: the input path and the expected SHA-256 become parameters; the DEFAULTS are today's
  path and pin, so every existing call is unchanged. (b) An explicit any-input mode (`pin=None`, reached only by an
  explicit flag of the run scripts) skips the hash check and labels every output as "any-input: numbers not expected
  to match the paper". (c) The private freeze gate (tag, blobs, clean-library check) is unchanged; it stays in the
  private repository. (d) Checks: tests written first (the default still refuses a changed file; the any-input mode
  runs on a synthetic CSV and labels its output; the default path and pin are unchanged); then core and full runs
  twice: **all 13 outputs byte-identical to the D2 SHA-256 values in `submission/scripts_v2/out/RUN_RECORD.md`**;
  the mutation harness re-run (93 of 93 caught, with its control). New tag: `spec-frozen-2026-11-11-d3`.

## 13. Every other analysis the corrected paper keeps (scope approved by AK 6 Nov 02:07; v2, clock 02:42)
Scope: `profile/paper_t10/scope_check/SCOPE_FINAL.md`. v1 (commit b192fba) was checked entry by entry against the
scripts and the pinned file before any review; what changed and why: `profile/paper_t10/spec13_check/SPEC13_CHECK.md`.

**General rule for 13.1-13.19.** Each analysis keeps the PROCEDURE of the named script at git tag `pre-corrections`
(commit 8130099, 4 Nov: the baseline the current paper was audited against, 380 of 380; the reviewed version is tag
`chr2027-submitted`, commit 3b5feb8, and eleven analysis scripts changed between the two), including its thresholds and
draw counts, and replaces its DATA LAYER by sections 0-7:
- parsing, exclusions and the R1 reading order (section 1); only legible signs are signs (000 and 999 never are); the
  identity key (section 2) wherever whole texts are compared; runs (section 4) for every pair or triple of signs,
  including "the sign before / after" a given sign (counted only when both are legible and adjacent in one line);
- first and last signs by section 5 (single-line; stored end mark '+'; legible end token). A measure that needs BOTH
  ends (a frame, or first against last at equal N) uses "both-end-eligible" texts: both stored marks '+' and both end
  tokens legible. Positions in the middle of a text: complete single-line texts only, counted in legible signs in
  reading order;
- the tie rule of section 7 wherever a top-k SET of keys is learned; a ranked list of SIGNS is ordered by (count
  descending, code ascending), and "rarest first" by (count ascending, code ascending);
- one generator `random.Random(42)` per reported quantity (section 0): where a script shares one generator across
  classes or parts, each class or part gets its own, unless the entry says TAB:I then SEAL:S per draw;
- populations (section 3): complete texts primary and all texts beside for whole-text, pair/triple/entropy and
  first/last measures; corpus descriptions (counts, site shares, provenance) use all analyzable texts; "multi-sign"
  means at least 2 legible signs.
Every departure from a script's procedure beyond this data layer is stated in its entry ("stated change").

- **13.1 Tables 1-2 and the marker replication (script 01).** Table 1: analyzable texts per class (SEAL:S, TAB:B,
  TAB:I, SEAL:R, POT:T:g). Table 2 (columns as section 8: EBUDS-like, full, and the R/L-or-L/R sensitivity row): N;
  top sign share (the most frequent sign's share of legible tokens); top-69 and top-82 sign coverage (share of legible
  tokens that are among the k most frequent signs); top-82 starters and top-23 enders (share of section-5-eligible
  texts whose reading-initial / reading-final sign is among the k most frequent such signs); mean legible length.
  M-342 line: among multi-sign texts of all classes with an eligible reading-final token, the share ending in 740, and
  its ratio to 740's share of all legible tokens of the same population (script 01 took that share over every row while
  restricting the rate to R/L and L/R texts: stated change); the R/L-or-L/R row beside (section 8).
- **13.2 Table 3 and the within-class shuffle null (scripts 01, 10).** Rows SEAL:S, SEAL:R, TAB:B, TAB:I, POT:T:g, plus
  pooled seals (SEAL:S + SEAL:R) and pooled tablets (TAB:B + TAB:I) with N, mean legible length and H3. Columns: N,
  mean legible length, H1 (entropy of legible signs), H3 plug-in and Miller-Madow, K_tri/N (section 7). Null, per
  class: in each iteration every run of the class (runs in row-index order; within a text in reading order) is copied
  and the copy shuffled with `rng.shuffle`, then H3 is recomputed; 10,000 iterations for TAB:I and TAB:B, 2,000 for
  the others (script 10). Report the observed H3, the null mean and minimum, p = (1 + #{null <= observed}) / (1 +
  iterations), the reduction 100 x (null mean - observed) / null mean, and script 10's verdict rule (templated if p <
  0.05 and reduction > 0). Singleton-context share (share of trigram tokens whose two-sign context occurs exactly
  once): observed, and the mean over 200 shuffles of the same kind. Shuffling within runs replaces shuffling whole
  texts so that each run keeps its length and its signs, as each text did in script 10.
- **13.3 Tablet templates (script 06), on TAB:I.** [A] legible-length profile (all analyzable TAB:I). [B] the 4 most
  frequent eligible reading-final signs of multi-sign texts (section 5) and, for each, the 5 most frequent signs
  immediately before it. [C] the slot {032, 033, 034}: per text the number of distinct members present (populations
  as 13.4); position when present (initial, medial, terminal; complete single-line texts); the 4 most frequent signs
  immediately after a member; the number of texts whose reading-order tokens are exactly a member then 700. [D]
  distinct keys of multi-sign texts, keys carried by at least 2 texts and the texts those keys carry (section 7's
  repeat share), and the top 10 with cumulative coverage. [E]
  top-10 coverage and the share of texts occurring once, TAB:I and SEAL:S.
- **13.4 Slot null (script 09-G5b; `submission/PREREG_R2-2_slot_null.md`).** Statistic, null N1, B = 10,000,
  `random.Random(42)`, p, the decision rule and the SEAL:S control exactly as registered. Population as registered:
  all analyzable TAB:I texts (a registered exception to section 3, like B'), complete texts beside; a text's positions
  are its legible signs in reading order with lines joined in reading order, as the registered gated reading order.
  Beside it, script 09-G5's independence expectation (the paper's "~33"), on the same populations: E = n_032 n_033 / N
  + n_032 n_034 / N + n_033 n_034 / N, where n_x = texts containing member x and N = texts, with the observed number of
  texts containing at least two distinct members.
- **13.5 Two-sign share of the top 10 (script 11, its composition part).** Multi-sign TAB:I: of the top-10 keys
  (section 7), how many have exactly 2 legible signs, and how many of the texts the top 10 cover they account for.
- **13.6 Reuse at fixed length (script 09-G1).** Top-10 coverage of TAB:I and of SEAL:S among texts of legible length
  2, 3, 4 and 5 (no size threshold, as script 09).
- **13.7 Seal regime (scripts 07, 09-G2, 09-G3), on multi-sign SEAL:S.** [07-A] legible-length profile and mean.
  [07-C] the 3 most frequent eligible reading-final signs (section 5) and, for each, its stems (the reading-order
  tokens without the final one): distinct stems and stems occurring once, each as a share of the texts ending in that
  sign. [07-D] the 5 most frequent eligible reading-initial signs and their combined share. [07-E] top-10 whole-text
  coverage, and top-10 frame coverage over both-end-eligible texts (frame = (initial, final) sign pair), SEAL:S and
  TAB:I. [09-G2] among texts with an eligible reading-final token: 740's share of all their legible tokens, of their
  final tokens and of their other legible tokens; enrichment = final share / other share. [07-B, 07-B2, 09-G3]
  complete both-end-eligible texts with at least 3 legible signs: entropy of first signs, of middle signs (legible
  signs strictly between) and of last signs, plug-in and Miller-Madow (H + (K - 1) / (2 N ln 2)); the Miller-Madow
  first-minus-last gap at equal N.
- **13.8 Geography (script 08; script 09-G4 in the appendix).** Multi-sign SEAL:S: the 740 reading-final rate
  (section 5) per site for sites with at least 30 eligible texts (script 08's N_MIN); pooled by script 08's tiers
  (core, regional, foreign); foreign seals itemised as counts. The "adequately sampled" sites are these same sites, and
  the paper gives the number of distinct sites with a SEAL:S text beside them (script 08 also counted sites with at
  least 44 SEAL:S rows of any length, a second bar that matched the first only in the old data: stated change). TAB:I
  and SEAL:S (all analyzable texts): the 5 sites with most texts and the Harappa share. Appendix (09-G4a/b): core
  against regional rate with script 09's two-proportion z test; rates at legible lengths 2-6; mean legible length by
  tier; core against regional at lengths 3, 4 and 5.
- **13.9 Site control (script 13).** [S4] TAB:I at Harappa, SEAL:S at Harappa, SEAL:S at Mohenjo-daro (multi-sign):
  top-10 coverage, share of texts occurring once (100 - repeat share), 740 reading-final rate (section 5); the
  within-Harappa TAB:I - SEAL:S coverage difference by the matched-N summary and the find-spot interval (section 7).
  [S6] Harappa, legible lengths 2, 3 and 4, cells with at least 15 texts per class: the matched-N summary of top-10
  coverage (section 7; script 13 always subsampled TAB:I to the SEAL:S size, the same whenever TAB:I is larger), and
  from the same draws each class's own coverage: mean, p5 and p95 (a class used whole has one value). [S7]
  TAB:I at Harappa subsampled to 700, 500, 300, 150 and 60 texts (sizes above the class size skipped): mean top-10
  coverage over 200 draws, one generator per size. [S5] estimability counts at Harappa, lengths 2-5, per class:
  texts, trigram tokens, distinct trigrams, K_tri/N. H3: ONE descriptive line, the within-Harappa SEAL:S - TAB:I
  difference of plug-in H3 at matched trigram tokens with Miller-Madow beside (section 7); it replaces the H3 values
  of S1, S2, S3 and S5 (13.20). [S8] is B'.
- **13.10 Duplicate-provenance test (script 16, M2 and M3).** Distance = difference of ROW INDEX. The rows are in
  ICIT's own id order (5,678 of 5,678 consecutive pairs non-decreasing) and the old scripts' own ids are the
  row index + 1, so this is script 16's distance unchanged; the paper names it "ICIT's own numbering", not "catalogue
  identifiers" (CISI order agrees only in part: 4,272 of 4,795 consecutive same-prefix pairs). [M2] per class (TAB:I,
  SEAL:S; multi-sign), one generator per class: groups = keys carried by at least 2 texts, in order of first row index;
  observed = gaps between consecutive sorted row indexes within each group; null = 200 draws, each drawing for every
  group `rng.sample` of as many row indexes from the class's multi-sign texts, sorted, and their gaps; report
  repeated keys, repeat-pairs, and the median gap and share of gaps <= 2, observed and null (the null's gaps pooled
  over all 200 draws and all groups into one list, as script 16). [M3] collapse,
  over all analyzable rows: within each (type, key) group in row-index order, a run starts at a row and takes every
  later row within 2 of that FIRST row; each run keeps its first row (as script 16). Then TAB:I and SEAL:S top-10
  coverage before and after, and the post-collapse sweep: top-N 5, 10, 20 x sites all and Harappa, cells with at least
  30 texts per class.
- **13.11 Label-permutation null, CLUSTER-AWARE (replaces script 17-H2's text-level shuffle).** Units = each class's
  own find-spots (section 6; an unknown find-spot is a one-row unit) over the multi-sign TAB:I and SEAL:S texts of the
  population, as section 7's interval: a find-spot's tablets and its seals are separate sets of copies and each moves
  whole. Both classes' units in one list ordered by first row index. 1,000 permutations, one generator: in each, a
  fresh copy of the list is shuffled (`rng.shuffle`) and units are taken in that order into pseudo-TAB:I while it
  holds fewer texts than the real TAB:I set (`while len(pseudo_tab) < n_tab: pseudo_tab.extend(next unit)`: the unit
  that crosses n_tab is included), the rest into pseudo-SEAL:S; statistic = top-10 coverage of pseudo-TAB:I
  minus pseudo-SEAL:S. Report the observed difference, the null mean and maximum, and p = (1 + #{null >= observed}) /
  (1 + 1,000) (script 17 printed #/1,000; the +1 form, as in script 10 and the slot registration, is never 0: stated
  change). Beside it, script 17's text-level version on this data layer (pool = TAB:I then SEAL:S texts in row-index
  order, shuffled in place 1,000 times; the first n_TAB texts are pseudo-TAB:I).
- **13.12 Synthetic positive control (script 17-H3).** One generator; vocabulary, weights and the TAB:I and SEAL:S
  length vectors as section 7's negative control (len_tab, len_seal). Ten templates, each `tuple(rng.choices(vocab,
  weights=weights, k=rng.choice(len_tab)))`. Class A, n_tab texts in turn: if `rng.random() < 0.40`, a template by
  `rng.choice(templates)`, else `rng.choices(vocab, weights=weights, k=rng.choices(len_tab, k=1)[0])`. Class B, n_seal
  texts: `rng.choices(vocab, weights=weights, k=rng.choices(len_seal, k=1)[0])` (no `rng.random()` call, as script
  17). Keys as section 7. Report top-10 coverage of A and B and the gap (one realisation, as script 17).
- **13.13 Class prediction (script 17-H5; appendix).** Multi-sign TAB:I and SEAL:S. 200 draws, one generator; in each,
  for TAB:I then SEAL:S, the class's G3 groups are split by section 7's fold rule (fold 1 = training). Learned on the
  training folds: the training TAB:I keys and SEAL:S keys; the marker = the most frequent eligible reading-final sign
  of training SEAL:S texts (section 5); the median = the training TAB:I legible lengths, sorted, at index len // 2. A
  test text is predicted: (1) tablet if its key is among training tablets and not seals; (2) seal if the reverse; (3)
  else seal if its eligible reading-final sign is the marker; (4) else tablet if its legible length <= the median,
  else seal. Report accuracy, the majority-class baseline (larger class's share), balanced accuracy, tablet and seal
  recall. (Script 17 split random halves of texts; find-spot groups stop copies from one spot falling on both sides,
  the leak the hold-out's G3 removes: stated change.)
- **13.14 Incised versus moulded reuse (script 09-MOLD).** Top-10 coverage of multi-sign TAB:I against TAB:B; the
  verdict wording follows Decision 6.
- **13.15 Shared texts across classes (script 09-G7; battery row "class label is a proxy for the text").** Over all
  analyzable multi-sign texts: distinct keys carried by more than one `type`, and keys found in both TAB:I and SEAL:S;
  the same two counts over texts of any length beside (script 09-G7 counted any length; the analysed texts are the
  primary row: stated change).
- **13.16 Provenance counts (script 15, parts P2, P4, P5, P7).** [P2] rows with a real CISI number (letters, '-',
  digits; '-' and the five '?-n' placeholders do not count; script 15 counted the placeholders: stated change), of all
  rows and of analyzable rows. [P4] rows with CISI H-104 to H-128, and rows without a legible sign. [P5] legible tokens
  and distinct legible signs of analyzable rows, with 000 and 999 tokens counted separately. [P7] analyzable texts and
  the distinct ICIT objects carrying them (section 1's object id, which every row has; script 15 counted distinct CISI
  values, which 661 rows lack: stated change); for multi-sign TAB:I texts: objects carrying more than one, objects
  repeating a key across sides, within-object repeats, and the share of such texts on multi-text objects. P0 and P1
  (lineage of the input file) follow Decision 3; P3 and P6 are removed (13.20).
- **13.17 Sign-identity sensitivity (script 19).** Multi-sign TAB:I and SEAL:S keys; perturbations change legible signs
  only (000 placeholders and end marks untouched); vocabulary = distinct legible signs of all analyzable rows,
  ascending (K = its size). [BASE]; [NOTE] (the signs of the top-10 TAB:I keys); [BITE] (MERGE at 40%); MERGE, SPLIT and
  SPLIT-WORST at rates 1, 2, 5, 10, 20 and 40% (k = max(1, int(round(rate x K)))), 200 draws, one generator per (mode,
  rate), one mapping per draw shared by both classes; [PROVENANCE] (worst-case split at 2% and 40%); [MARKER] (740
  split; terminal = an eligible reading-final token, section 5; non-terminal = the other legible tokens of the same
  texts). Short in the main text; the figure and the rest in the appendix.
- **13.18 Farmer-Sproat-Witzel checklist (script 18; appendix).** F2 (co-occurrences of {032, 033, 034} in every class)
  and F6 (the k rarest legible signs merged into one symbol; k = 0, 100, 200, 400, 600) on this data layer. F3 (the
  inversion under three reading conventions) is not computed: after R1 there is one documented convention, and
  whole-text identity is unchanged when every text is reversed (R1 point (b)); the appendix says so in one sentence.
- **13.19 Storage test (replaces the 09-G6 row; R1 point (c)).** Checks T1-T4 and the self-test of
  `profile/fuls_2026-11-01/decision1_direction_tests.py` (3 Nov; registered in `PREREG_corrections.md`, R1), exactly as
  that script, on the pinned file parsed by section 1 (malformed row excluded; each text's legible tokens with lines
  joined in STORED order, which is the input that script read): T1 sign 740 and T2 the initial-type signs 190, 315,
  853, 880 at the stored left against the stored right end, per `dir.` class; T3 L/R texts (at least 3 legible signs,
  not palindromes) equal to an R/L text as stored against only reversed; T4 cosine similarity of L/R stored sign pairs
  with R/L stored pairs as stored against reversed; the self-test (every L/R text reversed) must flip T1-T4 for L/R.
  One sentence in the main text; the results in the appendix.
- **13.20 Removed or not run.** Approved removals (AK 02:07; reasons in SCOPE_FINAL): script 02; scripts 03, 05, 12 and
  script 04's bootstrap interval (Table 7; Miller-Madow stays as a Table 3 column); the 09-G6 row; the older-database
  battery row (script 15 P3 and P6); the 17-H6 catalogue-order blocks. Within the approved "H3 parts one descriptive
  line" (13.9): script 13's S1 matched-N H3 gap, S2 (Mohenjo-daro tablet pool, N = 149), S3 (site effect on seals) and
  S5's H3 values; the paper prints S1-S3 at lines 616-627. Not run because the paper prints no number from them:
  script 11's trigram table; 09-G7's CISI-prefix count. Replaced: script 08's second site bar (13.8); 18-F3 (13.18);
  17-H7's two object rows (404 identified tablet objects; unidentified texts as singletons) by section 7's G2 row on
  ICIT object ids, which every row has.
  Every number that leaves the paper is listed in the chairs letter; scripts of removed analyses leave the corrected
  deposit.
- **13.21 Figures.** Every plotted coordinate is a number defined above or in sections 7-8. The specification curve
  (section 8 grid) plots 21 points: the cell gaps sorted ascending, read at p = q / 20 (q = 0, ..., 20) by linear
  interpolation at position pos = p x (n - 1): lo = int(pos), hi = min(lo + 1, n - 1), value = g[lo] + (g[hi] - g[lo])
  x (pos - lo), as script 16 (a figure rule only; section 0's p5/p95 rule is unchanged; at p = 0.5 it equals the
  median). The shuffle-null figure plots 13.2's observed H3 and null mean per class; the site-by-length figure,
  13.9's [S6] TAB:I coverage (mean with p5-p95 bar) against the SEAL:S coverage; the sign-identity figure, 13.17's MERGE, SPLIT and SPLIT-WORST means at split
  rates 0, 1, 2, 5, 10, 20 and 40% (0 = unperturbed); the hold-out figure, section 7's means with p5 and p95.
- **13.22 How section 13 is checked.** The independent implementation (a second program written from this
  specification by another model, sharing no code) covers sections 0-8 and also 13.7's [09-G2] enrichment and
  [07-B, 09-G3] positional entropies: the earlier audit already checked those two by a second implementation
  (`reference_impl.py`), and the corrected paper must not check less. Every other entry is checked by the shared
  library's fixtures and mutation tests and by the both-ways audit (every printed number has a source in the run, and
  every number the run reports for the paper is printed).
