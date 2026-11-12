# Independent re-implementation of the remaining analyses (brief for Codex CLI)

**How AK runs this.** Open Codex CLI in `<private path>` and say: "Read BRIEF.md and do exactly what it says." It may
take a long while; let it finish. Everything below is addressed to Codex.

---

**Purpose.** A research paper reports numbers computed by one program from a written, frozen specification. You
write a SECOND program, from the specification alone, for the analyses listed below, so that the two can be
compared number by number. You have not seen the first program or its results and must not look for them. Agreement
is evidence that both follow the text; a difference means one of the two is wrong or the text is ambiguous. Both
findings are equally valuable: do not aim to agree, aim to follow the text.

## Rules

1. **Read ONLY** the files in this folder, `inputs/` and `schema/`, plus the one data file named in rule 5:
   - `inputs/SPEC_decision2_DRAFT.md`: sections 0-12 in full (section 12 amends earlier sections; where it does, the
     amendment wins); in section 13 the general rule at its start, the entries in the scope below, and 13.20-13.22.
   - `inputs/old_scripts/`: the scripts the specification names. Its general rule for section 13 says each analysis
     keeps the PROCEDURE of its named script (thresholds, draw counts, order of operations) and replaces its DATA
     LAYER by sections 0-7. Read them for procedure only. **Never run them**: they read another file through an old
     data layer that the specification replaces. `decision1_direction_tests.py` is the script 13.19 names.
   - `inputs/PREREG_corrections.md` (named by 13.19) and `inputs/area_values_ending_dash.txt` (named by section 6).
   - `schema/schema_D0.json`, `schema/schema_D1.json`: the output layout (rule 9).
2. **Do NOT open anything else.** In particular nothing under `<private path>` except the data file: not its
   scripts, outputs, notes, paper or git history. The specification mentions other files (reviews, checks, scope
   notes); they are not part of the definition. Where you think the text does not define something, record it
   (rule 7) instead of looking elsewhere.
3. **Write ONLY** in `work/`: `impl.py` (one file, Python standard library only), `output_D0.json`,
   `output_D1.json`, `AMBIGUITIES.md`, `RUN_LOG.md`, and, if you write them, tests in `work/tests/`. Change no other
   file. No git operations, no network, no package installs.
4. **Python:** `py -3.11 -I work\impl.py`. Use `random.Random(42)` exactly as the specification places it (one
   generator per reported quantity unless an entry says otherwise).
5. **The data file and its rule.** The input is
   `<private path>`
   (SHA-256 `c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98`). It is third-party data; its maintainer has permitted the publication of statistical
   results from it. Therefore:
   - your program reads it locally; **you never open, print, display, quote or paste any row, any field value of a
     row, or any text (sign sequence) of a row**, in the terminal, in a file, or in a message. No `type`, `cat`,
     `head`, `more`, `Get-Content`, no printing of parsed records, no "show me a sample" while debugging;
   - while debugging print only aggregates (counts, sums, shares) and refer to a row by its row index;
   - `AMBIGUITIES.md` and `RUN_LOG.md` cite rows by row index only, never by content;
   - some output keys are themselves texts (for example a top-10 list of whole-text keys). Write them to the output
     file, which is compared by machine; do not print or display them;
   - the column NAMES and the parsing rules are in the specification (sections 0-1); you do not need to look at rows.
6. **Freeze check first** (record in `RUN_LOG.md`, with the clock time): the SHA-256 of
   `inputs/SPEC_decision2_DRAFT.md` is `8c3481b73e9c0a3331b5a69da1accb09c759e9526856417f1dee05adcc35a343`, and the data file's SHA-256 equals the value above and in
   section 0. If either differs, stop and record it.
7. **Never ask, never stop at an ambiguity.** Take the most literal reading of the text, compute it, and record it in
   `AMBIGUITIES.md`: the spec line, the readings you considered, your choice and the output keys it affects. Most
   consequential first.
8. **Run twice** in fresh processes; both outputs must be byte-identical (record both SHA-256 and clock times).
9. **Output layout.** `output_D0.json` is every copy (copy rule D0, sections 6-7) and has exactly the keys of
   `schema/schema_D0.json` (47 top-level keys); `output_D1.json` is the same analyses under copy rule D1 (the
   maintainers' rule, applied as section 12 says) with exactly the keys of `schema/schema_D1.json` (43). In the
   schema each value is replaced by its type (`int`, `float`, `str`, `bool`); `{"__list__": n, "item": ...}` is a list
   of up to n items of that shape (shorter when the data have fewer), and `{"__tuple__": [...]}` a list whose positions have the types given (for example
   `[str, int]` = a sign code and its count). A key in angle brackets with a `__keys__` note (for example
   `"<site>"`) stands for one key per value that occurs in the data: write the actual values as keys (a site name, a
   length as a string), each with the shape given, and do not write `__keys__`. A key or key part `complete` / `all` is the population of section 3. Write
   `json.dumps(obj, sort_keys=True, indent=1)`; floats at full precision (no rounding); shares in percent (0-100);
   entropies in bits; p-values as fractions. A `str` value that the specification fixes as a sentence (for example
   an analysis it says is not computed) may be the specification's own short wording; it is not compared.
   If you believe a key cannot be computed from the text, write `null` and say why in `AMBIGUITIES.md`.

## Scope: the entries of section 13 to implement

13.1 (Tables 1-2 and the marker line), 13.2 (Table 3, shuffle null, singleton-context share), 13.3 (tablet
templates), 13.5 (two-sign share of the top 10), 13.7 (seal regime, all parts), 13.8 (geography, with its appendix
parts), 13.12 (synthetic positive control), 13.13 (class prediction), 13.14 (incised versus moulded), 13.15 (shared
texts), 13.16 (provenance counts), 13.17 (sign-identity sensitivity), 13.18 (checklist F2 and F6), 13.19 (storage
test with its self-test). Sections 0-8 define the data layer, populations, keys, ties, the top-k rule, find-spots,
copy rules and the protocols these entries use; implement what they need.

## `AMBIGUITIES.md` and `RUN_LOG.md`

Short. Every choice numbered, most consequential first. The log: clock times, the freeze check, the Python version,
both runs' SHA-256 per output file, the run time, and any key you wrote as `null`.
