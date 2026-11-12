# Specification Ambiguities and Implementation Choices

This document records all ambiguities encountered in `submission/SPEC_decision2_DRAFT.md` and `submission/PREREG_chronology.md` during the independent reimplementation (Roadmap C1), ordered from most consequential to least consequential. Per Rule 6 of `GEMINI_INDEPENDENT_IMPL_PROMPT.md`, when the text allowed multiple readings, the most literal reading was implemented and documented here.

---

### Entry 1: Population Filter for Terminal Sign 740 Analysis (Section 5)
- **Specification Reference:** `submission/SPEC_decision2_DRAFT.md`, Section 5 (lines 201-209).
- **Ambiguity:** Section 5 states: *"Single-line texts whose reading ends at an intact edge (`+`) with a legible sign."* Unlike Section 3 (Whole-text measures), which explicitly specifies filtering to texts with $\ge 2$ legible signs, Section 5 does not restate the multi-sign restriction. 
  - *Reading A (Literal):* Any analyzable row satisfying `single_line == True`, `left_mark == '+'`, and whose reading-final token is not `'000'` or `'999'`, regardless of text length (including 1-sign inscriptions).
  - *Reading B (Multi-sign restricted):* Only texts with $\ge 2$ legible signs (inheriting the multi-sign convention of Sections 3 and 4).
- **Choice Made:** Reading A (literal reading of Section 5 text). All single-line texts with intact left mark and legible terminal sign are included in the eligible denominator.
- **Output Keys Affected:**
  - `final740.TAB:I.complete`
  - `final740.TAB:I.all`
  - `final740.SEAL:S.complete`
  - `final740.SEAL:S.all`
  - `bprime.primary.*.final740_tab`
  - `bprime.primary.*.final740_seal`
  - `bprime.sensitivity.*.final740_tab`
  - `bprime.sensitivity.*.final740_seal`

---

### Entry 2: Whole-Object Identity Definition and Metrics (Section 3)
- **Specification Reference:** `submission/SPEC_decision2_DRAFT.md`, Section 3 (lines 145-149).
- **Ambiguity:** Section 3 defines two separate object-level analyses under D0:
  *(a)* The share of objects carrying at least one of the class's top-10 inscriptions (derived from side-level frequencies).
  *(b)* Whole-object identity, treating each multi-face object as a composite unit (e.g., set or sequence of side inscriptions).
  The spec mentions both concepts but prompt section B asks for `object_top10_share.{c}.{pop}` for (a) and `object_identity.{c}.{pop}` for (b) with the fields computed.
  - *Reading A (Composite tuple representation):* Represent an object's whole inscription as a sorted tuple of the canonical serializations of all its analyzable sides (`"+".join(sorted(sides))`), then compute `n_objects`, top-10 coverage (`cov10`), `repeat_share` ($\ge 2$ occurrences), and the list of `top10keys`.
  - *Reading B (Set representation or side concatenation):* Concatenate side texts directly without ordering or sorting.
- **Choice Made:** Reading A. For each object ID, collect the canonical reading-order serializations of its sides, sort lexicographically, and evaluate the resulting object-level types. Output dictionary containing `n_objects`, `cov10`, `repeat_share`, and `top10keys`.
- **Output Keys Affected:**
  - `object_top10_share.TAB:I.complete`
  - `object_top10_share.TAB:I.all`
  - `object_top10_share.SEAL:S.complete`
  - `object_top10_share.SEAL:S.all`
  - `object_identity.TAB:I.complete`
  - `object_identity.TAB:I.all`
  - `object_identity.SEAL:S.complete`
  - `object_identity.SEAL:S.all`

---

### Entry 3: Specification Grid Median Calculation (Section 8)
- **Specification Reference:** `submission/SPEC_decision2_DRAFT.md`, Section 8 (lines 343-346).
- **Ambiguity:** The specification grid evaluates 144 design combinations. With an even number of evaluated cells (144), the median can be computed as the arithmetic mean of the 72nd and 73rd sorted gaps, or as the lower/upper median.
  - *Reading A:* Python standard library `statistics.median(gaps)` (arithmetic mean of middle two elements).
  - *Reading B:* Low median or high median from `statistics.median_low` / `statistics.median_high`.
- **Choice Made:** Reading A (`statistics.median`).
- **Output Keys Affected:**
  - `grid.median`

---

### Entry 4: Stratum Cell Deduplication Scope for D2a (Chronology Amendment 1)
- **Specification Reference:** `submission/PREREG_chronology.md`, Amendment 1 (lines 207-214).
- **Ambiguity:** When computing the `d2a_matched` sensitivity metric within each Harappa F cell (e.g., Stratum IV or Stratum V-VII):
  - *Reading A (Local cell deduplication):* Deduplicate within the cell's eligible texts using the D2a key `(site, type, raw_text, findspot_d2a)`.
  - *Reading B (Global deduplication):* Deduplicate the entire Harappa or entire corpus under D2a first, then partition into stratum cells.
- **Choice Made:** Reading A. Deduplication is performed on the stratum cell's multi-sign texts directly, following the principle that each cell is analyzed as a self-contained sub-corpus.
- **Output Keys Affected:**
  - `bprime.primary.V-VII.d2a_matched`
  - `bprime.primary.IV.d2a_matched`
  - `bprime.sensitivity.V-VII.d2a_matched`
  - `bprime.sensitivity.IV.d2a_matched`

---

### Entry 5: Resampling Subsampling Order in Find-Spot Cluster Interval (Section 7)
- **Specification Reference:** `submission/SPEC_decision2_DRAFT.md`, Section 7 (lines 268-281).
- **Ambiguity:** In each cluster-bootstrap draw of find-spots, after clusters are drawn with replacement and texts pooled, if the tablet pool and seal pool have unequal text counts ($N_{tab} \ne N_{seal}$), the larger class is subsampled without replacement down to $N_{res} = \min(N_{tab}, N_{seal})$.
  - *Reading A:* Use `rng.sample(larger_pool, n_res)` directly. If both pools are subsampled conditionally, TAB:I is checked first then SEAL:S.
  - *Reading B:* Resample at cluster level rather than text level down to matched sample size.
- **Choice Made:** Reading A (exact wording of Section 7: "the larger class is subsampled without replacement to $N_{res}$").
- **Output Keys Affected:**
  - `findspot_interval.cov10.complete`
  - `findspot_interval.cov10.all`
  - `findspot_interval.repeat_share.complete`
  - `findspot_interval.repeat_share.all`
