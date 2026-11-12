# Ambiguities and Implementation Choices (Roadmap V2)

Choices made in `impl_v2.py`, ordered from most consequential to least consequential:

### 1. M3 Collapse Universe and Row Count Reporting (`13.10.{pop}`)
- **Spec Line:** Spec 13.10 lines 290–292: "[M3] collapse, over all analyzable rows: within each (type, key) group in row-index order, a run starts at a row and takes every later row within 2 of that FIRST row; each run keeps its first row (as script 16). Then TAB:I and SEAL:S top-10 coverage before and after..."
- **Readings:**
  - *Reading A:* Collapse is executed globally over all 5,530 analyzable rows in the corpus, yielding 305 collapsed rows (`M3_rows_collapsed = 305` for both populations). Surviving rows in the population are those remaining after global collapse.
  - *Reading B:* Collapse is executed within the specific population (`complete` vs `all`), yielding 280 collapsed rows for `complete`.
- **Choice Made:** Reading A: Collapsed globally across all 5,530 analyzable rows (`M3_rows_collapsed = 305`). Empirical testing verified that for multi-sign texts, the surviving texts and top-10 coverage before and after collapse are identical under both readings (TAB:I N: 570 -> 518, cov10: 50.8772% -> 48.4556%; SEAL:S N: 1263 -> 1258, cov10: 3.4046% -> 3.3386%).
- **Output Keys Affected:** `13.10.complete.M3_rows_collapsed`, `13.10.all.M3_rows_collapsed`.

### 2. M3 Post-Collapse Sweep Return Structure (`13.10.{pop}.M3_sweep`)
- **Spec Line:** Prompt line 48: `"M3_sweep": {"cells":, "positive":, "min":}`.
- **Readings:**
  - *Reading A:* `"cells"` is an integer reporting the count of cells that ran with $\ge 30$ texts per class (consistent with `"units": len(units)` in 13.11 and plural count keys in 13.10).
  - *Reading B:* `"cells"` is a list of objects describing each individual cell.
- **Choice Made:** Reading A: Reported `"cells": 6` (integer), `"positive": 6`, `"min": min(gaps)` as scalar metrics.
- **Output Keys Affected:** `13.10.complete.M3_sweep.cells`, `13.10.all.M3_sweep.cells`.

### 3. N1 Column Permutation and Generator Scope (`13.4.{pop}`)
- **Spec Line:** PREREG lines 33–40, 59–61 & Spec 13.4: "Length-1 texts cannot reach T and are carried unchanged. B = 10,000 draws, random.Random(42), columns permuted in sorted (L, p) order... Control: Same population definition with SEAL:S, same null, same B and seed."
- **Readings:**
  - *Reading A:* Permutations are executed for lengths $L \ge 2$ in sorted $L$ order and sorted position $p \in \{0, \dots, L-1\}$. TAB:I and SEAL:S control each initialize their own fresh `random.Random(42)`.
  - *Reading B:* Permutations loop over all lengths including $L = 1$, or share a single RNG stream across TAB:I and SEAL:S.
- **Choice Made:** Reading A: Shuffled columns for $L \ge 2$ in sorted $(L, p)$ order, with independent `random.Random(42)` per class/control.
- **Output Keys Affected:** `13.4.complete`, `13.4.all`.

### 4. 13.11 Label-Permutation Null Generator Allocation (`13.11.{pop}`)
- **Spec Line:** Spec 13 general rule & Spec 13.11: "one generator random.Random(42) per reported quantity... 1,000 permutations, one generator... Beside it, script 17's text-level version on this data layer".
- **Readings:**
  - *Reading A:* Cluster-aware null and text-level null are separate reported null quantities, each starting with its own `random.Random(42)`.
  - *Reading B:* The single generator continues from cluster-aware into text-level null without re-seeding.
- **Choice Made:** Reading A: Fresh `random.Random(42)` for cluster-aware null and fresh `random.Random(42)` for text-level null.
- **Output Keys Affected:** `13.11.complete.text_level`, `13.11.all.text_level`.

### 5. S7 Bias Target Sizes Filtering (`13.9.{pop}.S7_bias`)
- **Spec Line:** Spec 13.9: "[S7] TAB:I at Harappa subsampled to 700, 500, 300, 150 and 60 texts (sizes above the class size skipped): mean top-10 coverage over 200 draws, one generator per size."
- **Readings:**
  - In `complete`, $N_{\text{TAB:I@Harappa}} = 556 < 700$, so size 700 is omitted, yielding 4 keys.
  - In `all`, $N_{\text{TAB:I@Harappa}} = 701 \ge 700$, so size 700 is included, yielding 5 keys.
- **Choice Made:** Followed the explicit instruction to skip sizes exceeding class size.
- **Output Keys Affected:** `13.9.complete.S7_bias`, `13.9.all.S7_bias`.

### 6. S4 `final740` Eligibility Scope (`13.9.{pop}.S4.*.final740`)
- **Spec Line:** Spec 13.9 lines 271–272: "[S4] TAB:I at Harappa, SEAL:S at Harappa, SEAL:S at Mohenjo-daro (multi-sign): top-10 coverage, share of texts occurring once (100 - repeat share), 740 reading-final rate (section 5)".
- **Readings:**
  - *Reading A:* The group definition is explicitly scoped by `(multi-sign)` (`legible_len >= 2`), so `final740` is computed on eligible single-line texts of those multi-sign groups.
  - *Reading B:* Section 5 general rule defines reading-final rate on single-line texts without a length restriction, which would include length-1 single-line texts.
- **Choice Made:** Reading A: Evaluated `final740` on eligible single-line texts within the multi-sign groups.
- **Output Keys Affected:** `13.9.complete.S4.*.final740`, `13.9.all.S4.*.final740`.
