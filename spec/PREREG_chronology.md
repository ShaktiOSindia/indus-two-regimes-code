# Pre-registration: a within-period control for the tablet/seal inversion (Reviewer 1)

Written and committed BEFORE any coverage, gap or marker rate below was computed by period.
Seen beforehand: only the feasibility counts that chose the periods (2026-10-24: Harappa
multi-sign texts per period label). AK approved running a within-period test on 2026-10-24
(recommendation 3). Deviations after running go in the log at the end; nothing above it is
edited.

## Sections withheld in this copy

The registration, pre-run notes, results and deviation log of the original within-period test (from "Why" to
"Gates added", 169 lines in the private repository) are not reproduced here. That test used the database's own
`time` field, the period-and-phase labels the database assigns, and its text quotes those labels, how they map onto
the recorded period and phase at each site, and row counts per label: content of the database, which this
repository does not publish. The test was withdrawn on 6 November 2026 and replaced by Amendment 1 below
(option B'), which uses the published excavation strata; the paper reports only B'.

---

## Amendment 1 (6 Nov 2026, FROZEN with the measurement specification at tag spec-frozen-2026-11-06)
The text below is `submission/PREREG_chronology_Bprime_DRAFT.md` as frozen, appended unchanged (as its status paragraph
requires: appended before any code or run). Approved by AK 6 Nov 2026 11:53 IST.

# Amendment 1 to `PREREG_chronology.md`: option B' (FROZEN 6 Nov 2026; in force)

**FROZEN (AK 6 Nov 2026 11:53 IST: "ok") together with the measurement specification, at git tag
`spec-frozen-2026-11-06` (`submission/FREEZE_RECORD.md`); appended unchanged to `PREREG_chronology.md` as Amendment 1
in the same commit, before any code or run. "The specification" below means `submission/SPEC_decision2_DRAFT.md` as
frozen. The status notes that follow are history.**

**Status (5 Nov 2026, 18:58 IST): DRAFT for AK, UPDATED to the Decision 2 specification (AK 18:54 "yes ok"):
sections 2, 3, 4 and 6 now point to `submission/SPEC_decision2_DRAFT.md`; test population DECIDED (b), all texts
(AK 18:58); Codex review 1 fixes no. 12-14 written in 21:34 (AK 21:27 "ok go ahead with your recommendations for
all"); nothing is run; approved text frozen after the independent re-read.** First written 4 Nov 21:48. Decision 7 = B' (AK, 21:22). When AK approves this text it is
appended UNCHANGED to `PREREG_chronology.md` as "Amendment 1" and committed BEFORE any code or run. Nothing in the
paper, the scripts or the existing registration has changed. Evidence: `profile/paper_t10/item2_phase_coverage/`
(`SOURCES_READ.md`, `RESULT.md`, `VERIFY_STRATA_BEFORE_CHANGE.md`, `sourced_cells_output.txt`).

**[5 Nov 18:46] SEAM FOUND before any run: Decision 2 (AK 18:42) makes COMPLETE texts the primary population, and
under it both B' cells fall below the registered threshold of 30 seals.** Cell SIZES only (no outcome computed;
`profile/paper_t10/item2_phase_coverage/sourced_cells_spec.py` + output): complete texts: V-VII TAB:I 144 / SEAL:S 25,
IV 47 / 28 (full Trench VI variant 149 / 26, 42 / 27); all texts: V-VII 163 / 38, IV 53 / 39 (168 / 40, 48 / 37).
Under section 4's rule the complete-text test would fall back to option C. **AK to decide before the freeze:**
(a) fallback C (no chronology test; cited sentences and a plain limit); (b) run B' on ALL texts (the spec's
conservative second population, end marks in the identity key), where both cells meet the threshold, and report the
complete-text cell sizes as below threshold; (c) one merged Mound F cell (Strata IV-VII). Claude: (b), declared now,
before any outcome; (c) changes the design after seeing sizes; (a) is the safest claim.
**[5 Nov 18:58] DECIDED by AK: (b)** ("ok continue with recommendation"): the B' test runs on ALL texts; the
complete-text cell sizes are reported as below the threshold. No outcome has been computed. The full text is
approved at the freeze, after Codex review 1.

## 1. What changes, and why
- **Withdrawn:** the [S8] test on the source file's `time` labels (two of its labels; withheld in this copy). Reason: the labels
  are an assignment made in the database (its manual: the "Time Line" menu "assign[s] a specific period and phase of a
  location ... to a time period"); it is the database's own classification, without a documented concordance to the
  excavation reports [wording made neutral 5 Nov, Gemini review 1 no. 18]; no published source
  was found for most of its labels (Fuls's *Corpus* s.1.3; both manuals; Vats 1940; Meadow & Kenoyer 2000, 2001,
  2005). The 25 Oct run and its result (outcome H) stay on record unchanged; this amendment does not hide it.
- **Replaced by:** the same statistic in Vats's published Mound F strata, dated through Meadow & Kenoyer's Trench I
  correlation, which WE extend to the rest of Mound F through Vats's mound-wide scheme (an analyst assumption, stated in
  the result sentence; section 2). [5 Nov 21:34, Codex review 1 no. 13: "ONLY from published sources" withdrawn.]

## 2. The rule
- **Population:** Harappa; incised tablets (TAB:I) vs square seals (SEAL:S); texts read, keyed and counted exactly
  as `submission/SPEC_decision2_DRAFT.md` (as frozen) sections 1-3 say (Decision 1 reading order; 999 not a sign; malformed
  codes excluded; end marks kept; 000 a placeholder in a text's identity; the side as the unit); at least 2 legible
  signs. **Test population: ALL texts (decided (b), AK 5 Nov 18:58).** This is the chronology check's registered
  EXCEPTION to the specification's primary population (complete texts): with complete texts both cells miss the
  registered threshold of 30 seals. The complete-text cell sizes are printed beside the result.
- **Level of each text:** Mound F only (the source file's `area-section` starts with "F"); the stratum is Vats's, as
  the source file records it in `phase` ("Stratum I".."Stratum VII"). Texts with no Vats stratum are excluded (this
  removes the unstratified texts and the later trenches' rows that one of the old period-label bins contained; labels and counts withheld in this copy).
  Only Strata IV-VII enter a cell. Stratum III and above are EXCLUDED from both cells, EXCEPT Trench VI's Stratum III,
  which counts as IV under Vats's correction (primary); under the sensitivity variant Trench VI's III, IV and V count
  as IV, V and VI. [5 Nov, Gemini review 1 no. 16: 44 Mound F rows (all classes) carry Stratum III outside Trench VI.]
- **Vats's Trench VI correction** (Vats 1940 p. 127: Trench VI's Stratum III "probably corresponds with the IVth in
  other trenches"): PRIMARY = Vats's stated correction only (Trench VI III counts as IV); SENSITIVITY = the full
  one-level offset (Trench VI III, IV, V count as IV, V, VI; Claude's inference, not stated by Vats).
- **Two cells, as the excavators group Vats's levels** (Meadow & Kenoyer 2000 p. 325, offprint p. 5, and its Table
  2; volume pages 321-340 throughout): **V-VII** = "the
  second half of Period 3B and ... the earliest part of Period 3C"; **IV** = Period 3C (above about 12 ft). Vats 1940
  pp. 9-10 and p. 25 make Mound F's strata one mound-wide scheme (the Granary = Stratum V datum); Meadow & Kenoyer's
  own correlation is for Trench I; its use for the rest of Mound F rests on Vats's scheme (stated in the paper).
  [5 Nov 21:34, Codex review 1 no. 13, verified on the page] Meadow & Kenoyer correlate "accepting his below-surface
  measurements and correlating them with our excavations" and conclude "on the evidence of Trench I alone" (printed
  pp. 5-6). Extending that dating to the rest of Mound F is OUR assumption. Trench I alone cannot carry the test
  (all texts: V-VII 112 tablets / 11 seals, IV 6 / 6; complete: 101 / 7, 6 / 5; counted 20:52, sizes only).
- **Threshold (unchanged, registered 25 Oct):** a cell is tested only with >= 30 texts of EACH class. Cell sizes
  (TAB:I / SEAL:S), counted 5 Nov 18:46 under the spec's rules (`sourced_cells_spec_output.txt`; sizes only):
  all texts: V-VII 163 / 38, IV 53 / 39 (full Trench VI variant 168 / 40, 48 / 37): all meet it; complete texts:
  V-VII 144 / 25, IV 47 / 28 (149 / 26, 42 / 27): all below it (seals).
- **Statistic and criterion (unchanged from [S8]):** the matched-N top-10 whole-text coverage gap, TAB:I minus SEAL:S,
  larger class subsampled to the smaller N, 200 draws, seed 42, identity and draws exactly as in the frozen spec (sections
  2, 0, 7); the matched-N ROBUSTNESS CRITERION is MET in a cell if p5 of the matched difference is above zero. It
  describes sensitivity to subsampling, not a significance test (Codex review 1 no. 14; the 25 Oct registration's
  "holds" is reported in these words).
- **Reported beside it, NOT decision-bearing** (added 5 Nov, before any run): (i) the repeat share (share of a cell's
  texts whose identity occurs at least twice in the cell), because at about 38 texts the top-10 coverage cannot fall
  below 10/38 = 26% even if every text is unique, so it is compressed by that floor; (ii) the same statistic with one
  copy per find-spot (spec D2a, section 6; mound-only rows such as "F-" are their own find-spot), as the spec requires
  beside every headline figure; (iii) the 740-final rate under the spec's end-mark rule (section 5). The floor is
  stated in the paper beside the result.

## 3. What this is and is not (stated in the paper)
- **A sensitivity check, not a blind test.** Cells overlapping these (the old period-label bins) were run on 25 Oct
  under the old reading rule; the V-VII and IV cells were defined after that, from the excavators' own grouping, not
  from any result. The re-run under the corrected reading rule is new. Option (b) was chosen (AK 5 Nov 18:58): the test
  population was chosen after seeing cell SIZES (not outcomes), to keep the registered threshold; this is said in the
  paper.
- **Limits:** Vats calls his dating "rough and provisional" and his Trench IV/V levels "tentative and approximate";
  the Trench I correlation is extended to the rest of Mound F through Vats's scheme; the source file's record of Vats's
  strata matched Vats's printed lists for 22 of 22 objects checked, but 137 of the 364 Mound F rows could not be
  located in his lists and are unchecked; Meadow & Kenoyer's *SAA 1999* report (the Mound F seasons) is unread.
- **The cited context sentence:** square seals in use from late Period 2 to 3C, incised tablets from Period 3B into 3C
  (Meadow & Kenoyer 2001; 2005 p. 207), and a seal and 22 tablets sharing a sign sequence from deposits "formed at
  about the same time" (Meadow & Kenoyer 2000, p. 336 of the volume).

## 4. Outcomes and wording, fixed in advance
- **H (criterion met in both cells, primary variant):** "Within Vats's Mound F Strata V-VII (N tablets, M seals),
  which Meadow & Kenoyer's Trench I correlation places in late Period 3B to the earliest 3C, and Stratum IV (Period
  3C; ...), the matched-N difference is +X [p5 a] and +Y [p5 b] points; extending the Trench I dating to the rest of
  Mound F is our assumption, and the strata are those recorded in the database (22 of 22 checked against Vats's
  lists)." + the remaining limits in 3 + the cited context sentence.
  [Wording revised 5 Nov 21:34, Codex review 1 no. 13-14: was "Within Mound F levels that the excavators date to ...".]
- **P (criterion met in one cell):** as H, naming the cell where it is not met.
- **F (not met in V-VII, the larger cell):** "Within the best-sampled excavated levels the matched-N robustness
  criterion is not met, so the class contrast may be partly chronological." STOP: report to AK before any change to
  the abstract, claims or discussion.
- **Sensitivity variant:** reported in one clause; if it changes the outcome (H vs P vs F), that is said plainly.
- **Fallback C:** if either cell falls below 30 of either class after the cleaning rules, no test is reported in that
  cell; if both fall below, the item reverts to the cited sentences and the plain limit (option C).

## 5. Pre-change map (everything this touches; changed only after AK approves, then Codex reads the rules)
`submission/make_period_labels.py` and `scripts/period_labels.json` (replaced by a strata-label generator and file,
with a lineage gate); script 13 [S8] (its hard check for two of the database's period labels); `check_corpus_lineage.py`;
the SHA pins in script 13, `check_deposit_manifest.py` and the deposit CI; `audit_numbers.py` (4 group sizes, 4 gap
values, the outcome line); `mutate_paper_gate.py` (4 cases); the paper gate's anchor "chronology control" and rule
"period label"; the Limitations item; the bibliography (Vats 1940; Meadow & Kenoyer 2001, 2005; `meadow2000` pages
321--340).

## 6. What would change this decision (rule 1) and pre-mortem (rule 15)
- **Would change it:** Fuls publishing or explaining his Time Line with sources; the excavators' *SAA 1999* report
  dating Vats's other trenches differently; a check of the 137 unlocated rows showing ICIT's strata differ from Vats's.
- **Pre-mortem (how B' could turn out wrong):** (a) the strata recorded in the source file differ from Vats for rows we
  could not check; (b) Vats's mound-wide numbering is too coarse, so a "level" mixes times; (c) a reader sees a
  non-blind check as tailored; (d) the cleaning rules shrink a cell below 30 [HAPPENED for complete texts, 5 Nov
  18:46: the seam note and options a/b/c]; (f) at about 38 seals the coverage measure is compressed by its 10/N floor
  [handled by reporting the floor-free repeat share beside it]; (e) Fuls objects to any use of his
  database's fields (covered by Decision 3). Each is either stated in the paper (a, b, c), handled by the fallback (d),
  or decided elsewhere (e).
