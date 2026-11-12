# B3 design: every number in the camera-ready comes from the run (written 10 Nov 2026, after the clock reading 17:06 IST)

Pre-change map (rule 5) for roadmap v2 step B3. No code yet; this file is reviewed first.

## Goal
No number in the camera-ready text is typed by hand. Each result or data fact is a LaTeX macro generated from the
frozen run's outputs; a both-ways audit fails if (a) the text contains a number that is neither a macro's output nor
on a short, typed-for-a-reason allow-list, or (b) a registered macro is never used, or (c) a macro's value disagrees
with the run.

## Files (all new, in `submission/numbers/`)
| File | Role |
|---|---|
| `registry.py` | one entry per paper number: macro name; source (output file + JSON key path); format (decimals, unit: %, x, bits, count; thousands separator); a one-line meaning. Filled DURING the rewrite, section by section |
| `make_numbers.py` | checks the SHA-256 of every output it reads against the D2 table in `scripts_v2/out/RUN_RECORD.md` (refuses on a mismatch); writes `numbers.tex` (`\newcommand{\nX}{...}` lines, sorted, deterministic); fails on a missing key, a None, or a duplicate macro name |
| `allowlist.py` | the numbers that may be typed, each with its class: sign codes ("ICIT~740", `$003$`), years and pages in citations, section/table/figure numbers, the seed and draw counts fixed by the spec, numbers quoted from other papers (each with its first-hand source, a separate list), counts in the frozen spec's definitions |
| `audit.py` | the both-ways audit on the SOURCE (macros not yet expanded: every digit outside `\nX` macros, comments, `\ref`/`\cite`/labels and allow-listed contexts is a FAIL) and on the RENDERED text (every number in the PDF text is the output of some macro or allow-listed); every registered macro used; every used macro registered; values re-generated and diffed |
| `selftest.py` | planted failures, one per location class: body sentence, table cell, caption, abstract, footnote, appendix, TikZ coordinate, an unused macro, a wrong value in `numbers.tex`, a hand-typed number inside a macro's sentence; plus a control (the clean scratch copy passes) |

## Packaging seam (form Q29: ONE `paper.tex`)
`numbers.tex` is `\input` while writing; at packaging (step G3) the macros are inlined into the single `paper.tex`
(definitions block at the top), and the audit and every gate are re-run on that exact file.

## Rounding rule (to be fixed before the first macro)
Round once, from the full-precision run value, at the format the sentence needs; never round a rounded value; a
derived number (a difference, a ratio) is computed from full-precision values in `make_numbers.py`, never from two
printed macros.

## Open points for review
1. TikZ figures: their data coordinates become macros too (otherwise a figure can drift from the text).
2. Numbers in the before/after change list (step G2) use the same registry, so the letter and the paper cannot disagree.
3. The old `scripts/audit_numbers.py` (380 numbers, old code) is retired from the camera-ready build (B2).

## Built (11 Nov 2026, recorded after the clock reading 03:50 IST)
- `make_numbers.py` + `selftest_make_numbers.py`: 15 of 15; a rigged copy (hash check off) is caught.
- `audit.py` + `selftest_audit.py`: 13 of 13 (control, one plant per location class: body, table cell, caption,
  abstract, footnote, TikZ coordinate, bare TikZ layout zero, LaTeX thousands, negative in math; unregistered macro;
  unused macro; stale allow-list entry); a rigged copy (digit check off) fails 9 of 13.
- **Conventions for the rewrite:** every result or data fact = a `\nName` macro (registry.py); every ICIT sign code
  = `\sgn{740}`; every layout constant in a figure = `\lay{0}`; any other typed number = an exact phrase in
  allowlist.py with its class and source. The paper defines `\newcommand{\sgn}[1]{#1}` and `\newcommand{\lay}[1]{#1}`.
- Today's submitted text: 1,630 hand-typed digit groups (the rewrite's job); 6 seed macros unused (expected).
- RENDERED-text check BUILT 12 Nov 2026 (01:58-02:01 IST, AK's decision 01:49): `check_rendered.py`, run by
  `audit.py` whenever a PDF is given (so `build_final.sh`'s B3 step runs it). A: every non-series macro value is in
  the PDF text; B: every number in the PDF text (bibliography excluded) is a macro value, an allow-listed phrase's
  digits, a `\sgn`/`\lay` constant of the source, or structure (headings, captions, citation brackets, cross-reference
  ranges, list items, page numbers, the template's header and licence lines). Series macros (5, drawn as coordinates)
  are noted, not checked. `selftest_rendered.py`: control passes; a changed macro value, a stray number and a
  changed sign code are each caught (4 of 4 on the 12 Nov build).
