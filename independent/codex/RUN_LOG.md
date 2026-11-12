# Run log

1. Freeze check — 2026-11-12 00:20:47 +05:30
   - `inputs/SPEC_decision2_DRAFT.md` SHA-256: `8c3481b73e9c0a3331b5a69da1accb09c759e9526856417f1dee05adcc35a343` (matches).
   - Pinned data-file SHA-256: `c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98` (matches).
2. Environment — Python 3.11.9; command: `py -3.11 -I work\impl.py`.
3. Synthetic parser, identity-preservation, and copy-rule fixtures — 4/4 passed before the full runs.
4. Full fresh run A — completed 2026-11-12 00:34:25 +05:30; wall time about 34 seconds.
   - `output_D0.json`: `6c28c25df0c9c3176d88ca8626736fc711d660160329edfe0c630fcfb2a98c2e`
   - `output_D1.json`: `f315b47efcdfb01b587566cdb618a95013dfe06165d98d0c7d6d835e3c0d5008`
5. Full fresh run B — completed 2026-11-12 00:35:12 +05:30; wall time about 31 seconds.
   - `output_D0.json`: `6c28c25df0c9c3176d88ca8626736fc711d660160329edfe0c630fcfb2a98c2e`
   - `output_D1.json`: `f315b47efcdfb01b587566cdb618a95013dfe06165d98d0c7d6d835e3c0d5008`
   - Both outputs are byte-identical across the fresh runs; each was recursively validated against its schema before being written.
6. Parser exclusion summary (aggregate only): 5,679 rows; 5,530 analyzable; 1 malformed; 148 non-malformed rows without a legible sign. There are 5 analyzable BUS-without-`/` rows excluded from pair/triple measures, and 123 analyzable rows excluded from first/last measures for not being single-line. These categories are measure-specific and are not summed.
7. No output key was written as `null`.
