# Confirmation run, core part (roadmap C3): record (6 Nov 2026; written after the clock reading 13:18 IST)

- **What ran:** `submission/scripts_v2/run_core.py` at commit `344a31409b08e157ccb0e174ccf4aa36fdbe7dc3`, Python
  3.11.9, against the frozen specification (tag `spec-frozen-2026-11-06`; `submission/FREEZE_RECORD.md`). Scope:
  spec sections 0-8, 13.7's seal measures and B' (Amendment 1), under the independent implementation's output keys.
- **Gate tested both ways before the run:** an uncommitted library file -> refused (exit 1); one byte appended to the
  frozen specification -> refused (exit 1); restored -> passes. The input SHA-256 is checked by `load_rows`.
- **Two runs in fresh processes** (clock 13:17:01-13:17:21 and 13:17:21-13:17:42): byte-identical.

| File | SHA-256 (both runs) |
|---|---|
| `core_output.json` | `7c7e4d82c560fbd6f90be98dbc3e05f23ba806342e6bbedabea9c20c8a6882ec` |
| `core_fingerprints.json` | `fef6bacc0e93bac2eaabcf6aa9f271e3d88560dc0e6c82657d5ac048de84855f` |
| `exclusions.json` | `cbeb285224c551a119227db747d4c5bea79f129314d0cb2c2c63986f030c4544` |

- **Library checks at this commit:** 28 tests (hand-written section-10 fixtures, regression anchor: the submitted
  extraction for 5,679 of 5,679 rows and Table 3's H3 1.2960 / 0.2238 under the submitted rules); 35 of 35
  single-rule mutations caught.
- **Cross-checks against counts recorded earlier by other code (agreement = same reading of the data):** B' cell sizes
  equal the 5 Nov 18:46 record in all 8 cells (all texts 163/38, 53/39, sensitivity 168/40, 48/37; complete 144/25,
  47/28, 149/26, 42/27); the entropy gap at matched trigram tokens +0.328 (complete) / +0.344 (all) against the
  exploration's "about +0.33"; the grid runs 144 cells.
- **One difference, explained:** analyzable rows 5,530 here; `decision5_wording/DECISION5_CHECK.md` gave 5,531 "under
  the confirmed rules". It applied "999 is not a sign" (row 5503.1 has no legible sign; its code is not reproduced in this copy) but still
  counted the malformed rod 5406.1. The frozen spec (section 1) excludes both: 5,679 - 1 malformed - 148 rows without a
  legible sign = 5,530. That file says its final values come from the confirmation run; the CISI share there
  (4,894 of 5,531) is recomputed by section 13.16 on the same basis.
- **Not yet done:** comparison with the independent implementation (C4); section 13 analyses (C2 part 3). No number
  here is used in the paper before C4.
- **Line endings:** the hashes above are of the bytes the run writes (LF). A Windows checkout with git's autocrlf
  turns them into CRLF, so re-hash a fresh run's output, not a checked-out copy.
- **CORRECTION (6 Nov 20:19):** the line above, "35 of 35 single-rule mutations caught", was NOT valid evidence when written: the
  mutation harness's scratch copies could not find the input, so every mutant failed whatever the mutation (fixed in
  31eaad5 with a control: the unmutated copy must pass first). Re-run with the control: every mutation of this run's
  library (parts 1-2) is caught; 75 of 75 over the whole library. The run's outputs are unaffected (re-run after the
  fix: same three SHA-256 values).

## Full run (section 13), recorded 6 Nov 22:36 IST
- `run_full.py` at commit `0a12dd7e959cbe1900d489e3c40dd1326d243ab1`, Python 3.11.9, same freeze gate plus a whole-library commit check (tested: refused
  while `run_full.py` was uncommitted).
- Two runs in fresh processes (clock 22:13:13-22:17:56 and 22:17:56-22:21:28): byte-identical,
  `full_output.json` SHA-256 `e5fc77d7296dcf57969620c5cff298bb79251b98ff9fa7821b318ff176e4e0e0`.
- Sense checks: 4 empty values, all K_tri/N at legible length 2 (no trigrams exist there: expected); the registered
  storage test passes all 8 checks (T1-T4 and every self-test flip); Table 1 class counts equal the submitted
  paper's (1,754 / 1,080 / 898 / 388 / 529); CISI share 4,893 of 5,530 = 88.5% and ICIT objects 4,635 = the
  DECISION5 figures minus the malformed rod (predicted before the run).
- Not yet done: assurance V1-V6 (roadmap); no section 13 number is used in the paper before them.

## Full run after deviation D1, recorded 6 Nov 23:56 IST
- Tag `spec-frozen-2026-11-06-d1`; gate re-pointed (only the spec's blob changed); core re-run equals the recorded
  core hashes (7c7e4d82..., fef6bacc..., cbeb2852...).
- Two full runs (from 23:35:33 and 23:38:36): byte-identical, `full_output.json` SHA-256
  `794cabd1642d28d10e9622332f0d15f94b188a6b71b9c79808e87fe4a075a03c` (supersedes e5fc77d7...). The only intended
  change: 13.7 [07-A] over all seals (all texts: N 1,754, mean 4.23; complete: N 1,310, mean 4.62).

## Runs after deviation D2 (the 7 Nov fix batch), recorded 7 Nov 15:38 IST
- Tag `spec-frozen-2026-11-07-d2`; library at commit ff49ae8 (tests and harness changed after it, not the library).
- Core, two runs in fresh processes (15:10:47-15:12:45 and 15:12:45-15:14:44): byte-identical.
- Full, two runs (15:15:40-15:26:21 and 15:26:21-15:37:32): byte-identical.
- SHA-256 of every output (generated by `profile/paper_t10/fix_batch_d2/write_run_record_d2.py` from the files; `exclusions.json` is unchanged since 6 Nov):

| File | SHA-256 |
|---|---|
| `core_output.json` | `9e8df6e36064c29afedae45e1da10a37077d249901072d904ec6b7aba3694110` |
| `core_output_D1.json` | `129ada18b41378fc26055d77cf62800c84bbd65e51d9ab4e8a3d6e6f4ef382f7` |
| `core_output_D2a.json` | `89748dcf0e662ab53eaadf9570128e4ce24a68f727d5768f3523b34dbe93c7fa` |
| `core_fingerprints.json` | `45d549ed1c6595327598b4b2a1ec709d7bef77d8d54631a12c192c9b54860966` |
| `core_fingerprints_D1.json` | `576ca88d9c2bdf41f04100057a050b2a9da37c4b8899bfe0cab7467d2037b3ec` |
| `core_fingerprints_D2a.json` | `f8846c6c21cd3b351e3b1b3b034ae0ff9e86f2644606c29dbd61e5e01c9c3c76` |
| `exclusions.json` | `cbeb285224c551a119227db747d4c5bea79f129314d0cb2c2c63986f030c4544` |
| `full_output.json` | `e94703bba0f85309b3b38bc681d28364e7346c8e194a2e8fc9c9ea18f374c775` |
| `full_output_D1.json` | `e482b9328248391d76cc267b6062820c9075a613a51b111b823e028c22003e86` |
| `full_output_D2a.json` | `3599071de825c751738e3b6bf40c8912910972cf4e649d3b4ad34e805f9e6fc2` |
| `full_fingerprints.json` | `e1887c4a5b6d9c85edfbb1b437981ac812890ec7e466acfd806fc0abad8b1fb7` |
| `full_fingerprints_D1.json` | `d2504632547c17a6d29f12aa63e316d741ad17a77ab690c232ae52798601bb8f` |
| `full_fingerprints_D2a.json` | `a2d1605b39ded6c99007562b127b6992b38a31f2ac700d1fd7747bec199626fe` |

- Diff gate against the 6 Nov run (`profile/paper_t10/fix_batch_d2/check_d2_diff.py`): core 0 changed / 0 removed (87 leaves and 8 fingerprints added, all allowed by D2); full 7 changed = the 6 M-342 values (reading 12 revised) and 13.8 complete distinct seal sites 32 -> 39; 6 leaves added (13.10 sweep cells, 13.14 N); 0 removed.
- Register gate (`check_register.py`): 587 required key paths present; D2(c)'s exceptions absent from the D1 file.

## Runs after deviation D3 (11 Nov 2026; recorded after the clock reading 03:34 IST)
- Tag `spec-frozen-2026-11-11-d3-r1`; library at commit f84250e (input path and pin as parameters, today's defaults;
  explicit `--any-input` mode writing to `out_any_input/`; no computation changed).
- Tests: 101 of 101 (4 new D3 tests, written first: 3 failed on the old library for the missing feature).
- Core, two runs in fresh processes (03:11:23 and 03:13:23): byte-identical; full, two runs (03:15:37 and 03:25:25):
  byte-identical.
- **All 13 outputs equal the D2 SHA-256 values in the table above** (machine comparison, 13 of 13); only
  `core_meta.json` and `full_meta.json` changed (commit, tag, time).
- Mutation harness: 95 of 95 caught with its control (two D3 mutations added: hash check skipped; default pin None).
