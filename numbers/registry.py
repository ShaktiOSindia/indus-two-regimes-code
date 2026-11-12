"""B3 registry: one entry per number the camera-ready prints. Filled DURING the rewrite (E1), section by section.
Entry: name (macro, 'n' + Uppercase + letters), source (output file, [key path]) or sources + derive, format {unit,
dec}, meaning (one line). For the change list (decision 5) an entry also records `was` (the value printed in the
SUBMITTED paper, tag chr2027-submitted, with its line) and `cause` (from the fixed list in DESIGN.md), or
`was: None` when the number is new.
"""
C = "core_output.json"
C1 = "core_output_D1.json"
F = "full_output.json"
X = "exclusions.json"
P2, P4, P5, P7 = ["13.16", "P2"], ["13.16", "P4"], ["13.16", "P5"], ["13.16", "P7"]
DF = ["data_facts", "unknown_findspot_by_class"]

ENTRIES = [
    # ---- Data section (E1 step 1, 11 Nov) ----
    {"name": "nRowsAll", "source": (F, P2 + ["all_rows"]), "format": {"unit": "count", "dec": 0},
     "meaning": "rows of the input file", "was": "5,679 (l.126)", "cause": "unchanged"},
    {"name": "nRowsMalformed", "sources": [(X, ["malformed"])], "derive": len, "format": {"unit": "count", "dec": 0},
     "meaning": "malformed rows (spec 1)", "was": None, "cause": "R2 cleaning (Decision 2): new rule"},
    {"name": "nRowsNoLegible", "source": (F, P4 + ["rows_without_legible_sign"]), "format": {"unit": "count", "dec": 0},
     "meaning": "rows with no legible sign", "was": "147 (l.130)", "cause": "R2 cleaning: 999 is not a sign"},
    {"name": "nAnalyzableRows", "source": (C, ["analyzable_rows"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable texts", "was": "5,532 (l.132)", "cause": "R2 cleaning: 999 not a sign; malformed row"},
    {"name": "nObjects", "source": (F, P7 + ["icit_objects"]), "format": {"unit": "count", "dec": 0},
     "meaning": "objects carrying the analyzable texts (ICIT object id)", "was": "4,039 catalogued objects (l.133)",
     "cause": "measure redefined: ICIT object ids, not CISI catalogue objects"},
    {"name": "nLegibleTokens", "source": (F, P5 + ["legible_tokens"]), "format": {"unit": "count", "dec": 0},
     "meaning": "legible sign tokens", "was": "18,061 (l.135)", "cause": "R2 cleaning: 999 not a sign"},
    {"name": "nDistinctSigns", "source": (F, P5 + ["distinct_legible_signs"]), "format": {"unit": "count", "dec": 0},
     "meaning": "distinct legible signs", "was": "713 (l.135)", "cause": "R2 cleaning: 999 not a sign"},
    {"name": "nTokensEroded", "source": (F, P5 + ["tokens_000"]), "format": {"unit": "count", "dec": 0},
     "meaning": "eroded-sign tokens (000)", "was": None, "cause": "new figure"},
    {"name": "nTokensBlank", "source": (F, P5 + ["tokens_999"]), "format": {"unit": "count", "dec": 0},
     "meaning": "blank-space tokens (999)", "was": None, "cause": "new figure"},
    {"name": "nCisiAnalyzable", "source": (F, P2 + ["real_cisi_analyzable"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable texts with a CISI number", "was": "4,900 (l.146)", "cause": "R2 cleaning: population"},
    {"name": "nCisiPct", "source": (F, P2 + ["pct_analyzable"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "share of analyzable texts with a CISI number", "was": "88.6 (l.146)", "cause": "R2 cleaning"},
    {"name": "nUnknownFindspotTab", "source": (C, DF + ["TAB:I", "unknown_findspot"]), "format": {"unit": "count", "dec": 0},
     "meaning": "incised-tablet texts with no recorded find-spot", "was": None, "cause": "new figure (D6 C5)"},
    {"name": "nUnknownFindspotSeal", "source": (C, DF + ["SEAL:S", "unknown_findspot"]), "format": {"unit": "count", "dec": 0},
     "meaning": "square-seal texts with no recorded find-spot", "was": None, "cause": "new figure (D6 C5)"},
    {"name": "nClassSealS", "source": (C, ["analyzable_by_type", "SEAL:S"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable SEAL:S texts", "was": "1,754 (Table 1)", "cause": "unchanged"},
    {"name": "nClassTabB", "source": (C, ["analyzable_by_type", "TAB:B"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable TAB:B texts", "was": "1,080 (Table 1)", "cause": "unchanged"},
    {"name": "nClassTabI", "source": (C, ["analyzable_by_type", "TAB:I"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable TAB:I texts", "was": "898 (Table 1)", "cause": "unchanged"},
    {"name": "nClassSealR", "source": (C, ["analyzable_by_type", "SEAL:R"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable SEAL:R texts", "was": "388 (Table 1)", "cause": "unchanged"},
    {"name": "nClassPotG", "source": (C, ["analyzable_by_type", "POT:T:g"]), "format": {"unit": "count", "dec": 0},
     "meaning": "analyzable POT:T:g texts", "was": "529 (Table 1)", "cause": "unchanged"},
]

# ---- Section 4.1, Table 2 (Yadav replication; spec 13.1 and 8), generated per column x metric ----
_T2 = ["13.1.table2"]
_COLS = {"Ebuds": "ebuds_like", "Full": "full", "Dir": "sensitivity_rl_lr"}
_WAS = {  # the submitted Table 2 (tag chr2027-submitted); the Dir column is new (spec 8, R1 point (a))
    "Ebuds": {"N": "3,309", "TopSign": "10.28", "TopSixtyNine": "78.14", "TopEightyTwo": "81.49", "Starters": "80.55",
              "Enders": "80.49", "MeanLen": "4.03"},
    "Full": {"N": "5,532", "TopSign": "9.80", "TopSixtyNine": "79.15", "TopEightyTwo": "82.36", "Starters": "80.17",
             "Enders": "75.56", "MeanLen": "3.56"},
}
_MET = [("N", "N", "count", 0), ("TopSign", "top_sign_share", "pct", 1), ("TopSixtyNine", "top69_coverage", "pct", 1),
        ("TopEightyTwo", "top82_coverage", "pct", 1), ("Starters", "starters_top82", "pct", 1),
        ("Enders", "enders_top23", "pct", 1), ("MeanLen", "mean_legible_length", "plain", 2)]
for _c, _ck in _COLS.items():
    for _m, _mk, _u, _d in _MET:
        _w = _WAS.get(_c, {}).get(_m)
        ENTRIES.append({"name": "nTabTwo%s%s" % (_c, _m), "source": (F, _T2 + [_ck, _mk]),
                        "format": {"unit": _u, "dec": _d}, "meaning": "Table 2, %s, %s" % (_ck, _mk),
                        "was": (_w + " (Table 2)") if _w else None,
                        "cause": "R1 reading order + R2 cleaning; EBUDS-like rules (spec 8)" if _w else "new column (spec 8)"})

# ---- Section 4.1, the 740 (M-342) terminal concentration (spec 13.1, reading 12 revised: AK 7 Nov) ----
_M = ["13.1.m342"]
for _p, _pk in (("Complete", "complete"), ("All", "all")):
    for _m, _mk, _u, _d in (("Rate", "rate_740_final", "pct", 1), ("Share", "token_share_740", "pct", 1),
                            ("Conc", "concentration", "plain", 2), ("Eligible", "eligible", "count", 0)):
        ENTRIES.append({"name": "nMarker%s%s" % (_p, _m), "source": (F, _M + [_pk, _mk]),
                        "format": {"unit": _u, "dec": _d}, "meaning": "740 final, %s, %s" % (_pk, _mk),
                        "was": {"Rate": "27.9", "Share": "9.80", "Conc": "2.8x"}.get(_m) if _p == "All" else None,
                        "cause": "R1 + R2; population = texts with an eligible final token (reading 12)"})

# ---- Section 4.2, Table 3 and the within-run shuffle null (spec 13.2); complete = primary, all beside ----
_T3 = {"SealS": "SEAL:S", "SealR": "SEAL:R", "TabB": "TAB:B", "TabI": "TAB:I", "PotG": "POT:T:g"}
_T3WAS = {"SealS": ("1,754", "4.50", "6.82", "1.30", "0.99", "74.7"), "SealR": ("388", "4.54", "6.71", "0.70", "0.30", "87.8"),
          "TabB": ("1,080", "3.33", "6.14", "0.41", "0.78", "46.8"), "TabI": ("898", "2.49", "5.54", "0.22", "0.53", "53.1"),
          "PotG": ("529", "2.12", "6.20", "0.09", "0.07", "98.7")}
for _c, _ck in _T3.items():
    _w = _T3WAS[_c]
    for _i, (_m, _path, _u, _d) in enumerate((("N", ["N"], "count", 0), ("MeanLen", ["mean_legible_length"], "plain", 2),
                                              ("HOne", ["H1"], "plain", 2), ("HThree", ["H3"], "plain", 2))):
        ENTRIES.append({"name": "nTabThree%s%s" % (_c, _m), "source": (F, ["13.2.table3.complete", _ck] + _path),
                        "format": {"unit": _u, "dec": _d}, "meaning": "Table 3, complete, %s %s" % (_ck, _path[0]),
                        "was": _w[_i] + " (Table 3, all texts, raw mean length)",
                        "cause": "population: complete texts primary; R1 + R2; mean length now legible signs"})
    ENTRIES.append({"name": "nTabThree%sKtri" % _c, "source": (F, ["13.2.table3.complete", _ck, "ktri_over_n"]),
                    "format": {"unit": "pct", "dec": 1}, "meaning": "Table 3, complete, %s K_tri/N" % _ck,
                    "was": _w[5] + " (Table 3)", "cause": "population: complete texts primary; R1 + R2"})
    ENTRIES.append({"name": "nTabThree%sNull" % _c, "source": (F, ["13.2.null.%s.complete" % _ck, "null_mean"]),
                    "format": {"unit": "plain", "dec": 2}, "meaning": "within-run shuffle null mean H3, complete, %s" % _ck,
                    "was": _w[4] + " (Table 3 'shuffled')", "cause": "population; null defined on runs (spec 13.2)"})
    ENTRIES.append({"name": "nTabThree%sHThreeAll" % _c, "source": (F, ["13.2.table3.all", _ck, "H3"]),
                    "format": {"unit": "plain", "dec": 2}, "meaning": "Table 3, ALL texts, %s H3" % _ck,
                    "was": _w[3] + " (Table 3)", "cause": "R1 + R2 (same population as submitted)"})
for _c, _ck, _was in (("Seals", "SEALS pooled", ("2,142", "4.50", "1.36")), ("Tablets", "TABLETS pooled", ("1,978", "2.95", "0.46"))):
    for _i, (_m, _mk, _u, _d) in enumerate((("N", "N", "count", 0), ("MeanLen", "mean_legible_length", "plain", 2), ("HThree", "H3", "plain", 2))):
        ENTRIES.append({"name": "nTabThreePooled%s%s" % (_c, _m), "source": (F, ["13.2.table3.complete", _ck, _mk]),
                        "format": {"unit": _u, "dec": _d}, "meaning": "Table 3, complete, %s %s" % (_ck, _mk),
                        "was": _was[_i] + " (Table 3)", "cause": "population: complete texts primary; R1 + R2"})
ENTRIES += [
    {"name": "nGapRawComplete", "sources": [(F, ["13.2.table3.complete", "SEAL:S", "H3"]), (F, ["13.2.table3.complete", "TAB:I", "H3"])],
     "derive": lambda s, t: s - t, "format": {"unit": "plain", "dec": 2},
     "meaning": "raw H3 gap SEAL:S - TAB:I, complete, from full precision", "was": "1.07 (l.~296)", "cause": "R1 + R2 + population"},
    {"name": "nEntMatchedMean", "source": (C, ["entropy_matched.complete", "plugin_diff_mean"]), "format": {"unit": "plain", "dec": 2},
     "meaning": "H3 gap at matched trigram tokens, complete, mean (plug-in)", "was": None, "cause": "new (promised to Fuls 7 Nov)"},
    {"name": "nEntMatchedLow", "source": (C, ["entropy_matched.complete", "plugin_diff_p5"]), "format": {"unit": "plain", "dec": 2},
     "meaning": "same, p5", "was": None, "cause": "new"},
    {"name": "nEntMatchedHigh", "source": (C, ["entropy_matched.complete", "plugin_diff_p95"]), "format": {"unit": "plain", "dec": 2},
     "meaning": "same, p95", "was": None, "cause": "new"},
]

# ---- Section 4.3, Regime 1 (incised tablets; spec 13.3-13.6, 13.18 F2, 13.11; core coverage, hold-out) ----
C2 = "core_output_D2a.json"
_T3C, _T3A = ["13.3.complete"], ["13.3.all"]
_TERM = ["B_terminals", "top4"]
def _e(name, src, fmt, meaning, was=None, cause="R1 + R2 + population (complete texts primary)"):
    ENTRIES.append({"name": name, "source": src, "format": fmt, "meaning": meaning, "was": was, "cause": cause})
_P, _N, _D = {"unit": "pct", "dec": 1}, {"unit": "count", "dec": 0}, {"unit": "plain", "dec": 1}
_e("nTabTwoSignPct", (F, _T3C + ["A_length_profile", "2", "pct"]), _P, "share of complete TAB:I with 2 legible signs", "48 (l.~374, all texts)")
for _i, _nm in enumerate(("SevenHundred", "FourHundred", "SevenForty", "EightSixtyOne")):
    _e("nTerm%sTexts" % _nm, (F, _T3C + _TERM + [_i, "texts"]), _N, "texts ending in terminal #%d" % _i)
    _e("nTerm%sPct" % _nm, (F, _T3C + _TERM + [_i, "pct_of_eligible"]), _P, "share of eligible texts, terminal #%d" % _i)
    _e("nTerm%sCover" % _nm, (F, _T3C + _TERM + [_i, "top5_cover_pct"]), _P, "top-5 preceders' cover, terminal #%d" % _i)
_e("nTermFourHundredBySevenForty", (F, _T3C + _TERM + [1, "preceders_top5", 0, 1]), _N, "texts where 740 precedes final 400")
_e("nSlotOneComplete", (F, _T3C + ["C_slot", "members_present", "1"]), _N, "complete TAB:I with exactly one slot member", "299 (all)")
_e("nSlotOneAll", (F, _T3A + ["C_slot", "members_present", "1"]), _N, "all TAB:I with exactly one slot member (registered population)", "299", "unchanged")
_e("nSlotIndepComplete", (F, ["13.4.complete", "TAB:I", "independence_expectation_G5"]), _D, "independence expectation, complete", "~33 (all)")
_e("nSlotIndepAll", (F, ["13.4.all", "TAB:I", "independence_expectation_G5"]), _D, "independence expectation, all texts", "~33")
_e("nSlotExpAll", (F, ["13.4.all", "TAB:I", "E_exact"]), _D, "E[T] under the registered null, all texts (primary)", "8.7 (l.~392)")
_e("nSlotExpComplete", (F, ["13.4.complete", "TAB:I", "E_exact"]), _D, "E[T] under the registered null, complete")
_e("nSealSlotObsAll", (F, ["13.4.all", "SEAL:S_control", "T_obs"]), _N, "SEAL:S control, observed, all texts", "11 (l.~401)")
_e("nSealSlotExpAll", (F, ["13.4.all", "SEAL:S_control", "E_exact"]), _D, "SEAL:S control, E[T], all texts")
_e("nSealSlotPAll", (F, ["13.4.all", "SEAL:S_control", "p"]), {"unit": "plain", "dec": 2}, "SEAL:S control, p, all texts")
_e("nSlotInitialPct", None, _P, "slot members in initial position, complete single-line", "76 (l.~393)")
ENTRIES[-1].pop("source"); ENTRIES[-1]["sources"] = [(F, _T3C + ["C_slot", "position_when_present", k]) for k in ("initial", "medial", "terminal")]
ENTRIES[-1]["derive"] = lambda i, m, t: 100.0 * i / (i + m + t)
_e("nSlotFollowSevenHundred", (F, _T3C + ["C_slot", "pct_followed_by_700"]), _P, "slot member followed by 700, %", "71 (l.~394)")
_e("nFamilyTexts", (F, _T3C + ["C_slot", "family_member_then_700"]), _N, "texts exactly member + 700, complete", "171 (all)")
_e("nFamilyPct", (F, _T3C + ["C_slot", "family_pct_of_multisign"]), _P, "family share of complete multi-sign TAB:I", "24 (all)")
for _c, _ck in (("SealS", "SEAL:S"), ("SealR", "SEAL:R"), ("PotG", "POT:T:g"), ("TabB", "TAB:B")):
    _e("nFTwo%sTwo" % _c, (F, ["13.18.complete", "F2", _ck, "ge2"]), _N, "%s texts with >= 2 slot members, complete" % _ck)
    _e("nFTwo%sOne" % _c, (F, ["13.18.complete", "F2", _ck, "ge1"]), _N, "%s texts with >= 1 slot member, complete" % _ck)
_e("nFTwoSealSRate", (F, ["13.18.complete", "F2", "SEAL:S", "rate_pct"]), _P, "SEAL:S co-occurrence rate, complete", "4.2 (all)")
_e("nKeysSharedTab", (F, _T3C + ["D_templates", "keys_shared"]), _N, "TAB:I texts (keys) carried by >= 2 tablets, complete", "90 (all)")
_e("nTextsSharedTab", (F, _T3C + ["D_templates", "texts_on_shared_keys"]), _N, "tablets carrying a shared text, complete", "527 (all)")
_e("nMultiTabComplete", (F, _T3C + ["D_templates", "multisign_texts"]), _N, "complete multi-sign TAB:I", "725 (all)")
_e("nRepeatTabComplete", (F, _T3C + ["D_templates", "repeat_share"]), _P, "TAB:I repeat share, complete", "73 (all)")
_e("nSealOncePct", (F, _T3C + ["E_productivity", "SEAL:S", "once_pct"]), _P, "SEAL:S texts occurring once, complete", "~88 (l.~427)")
_e("nTopTenTwoSignKeys", (F, ["13.5.complete", "top10_two_sign_keys"]), _N, "two-sign keys among the top 10", "seven (all)")
_e("nTopTenTwoSignTexts", (F, ["13.5.complete", "texts_two_sign"]), _N, "texts of the two-sign top-10 keys", "248 (all)")
_e("nTopTenTexts", (F, ["13.5.complete", "texts_top10"]), _N, "texts covered by the top 10", "293 (all)")
for _l, _ln in (("2", "Two"), ("3", "Three"), ("4", "Four"), ("5", "Five")):
    _e("nFixLen%sTab" % _ln, (F, ["13.6.complete", _l, "TAB:I", "cov10"]), _P, "TAB:I top-10 coverage at length %s" % _l, None, "new figures in the text (G1)")
    _e("nFixLen%sSeal" % _ln, (F, ["13.6.complete", _l, "SEAL:S", "cov10"]), _P, "SEAL:S top-10 coverage at length %s" % _l, None, "new figures in the text (G1)")
_e("nFixLenFiveTabN", (F, ["13.6.complete", "5", "TAB:I", "N"]), _N, "TAB:I texts of length 5, complete")
_e("nCovTabCompleteDone", (C, ["cov10.TAB:I.complete.D1"]), _P, "top-10 coverage, tablets, Fuls's rule (D1)", None, "new (D1 printed)")
_e("nCovSealCompleteDone", (C, ["cov10.SEAL:S.complete.D1"]), _P, "top-10 coverage, seals, D1", None, "new (D1 printed)")
_e("nMatchedGapCompleteDzero", (C, ["matched_n.cov10.complete", "mean"]), _D, "matched-N gap, complete, D0", None, "new")
_e("nMatchedGapCompleteDtwoa", (C2, ["matched_n.cov10.complete", "mean"]), _D, "matched-N gap, complete, D2a", None, "new")
_e("nRepeatSealCompleteDone", (C, ["repeat_share.SEAL:S.complete.D1"]), _P, "SEAL:S repeat share under D1, complete", None, "new (D6 C4)")
_e("nTabIHarappaPct", (F, ["13.8.site_shares", "TAB:I", "harappa_pct"]), _P, "share of analyzable TAB:I from Harappa", "96.8 (abstract)", "unchanged")
_e("nHoldOutTabOut", (C, ["holdout.G3.TAB:I.complete", "out_mean"]), _P, "G3 hold-out, tablets, out-of-sample coverage", "38.7 (random split)", "find-spot grouping (G3) primary")
_e("nHoldOutSealOut", (C, ["holdout.G3.SEAL:S.complete", "out_mean"]), _P, "G3 hold-out, seals, out-of-sample coverage", "1.3 (random split)", "find-spot grouping (G3) primary")
_e("nHoldOutTabOutDtwoa", (C2, ["holdout.G3.TAB:I.complete", "out_mean"]), _P, "G3 hold-out, tablets, D2a")
_e("nHoldOutSealOutDtwoa", (C2, ["holdout.G3.SEAL:S.complete", "out_mean"]), _P, "G3 hold-out, seals, D2a")
_e("nClusterNullMax", (F, ["13.11.complete", "cluster", "null_max"]), _D, "cluster-aware null, largest shuffled gap", None, "new (13.11 replaces 17-H2)")
_e("nClusterObserved", (F, ["13.11.complete", "observed"]), _D, "cluster-aware null, observed gap")
_e("nClusterPDone", ("full_output_D1.json", ["13.11.complete", "cluster", "p"]), {"unit": "plain", "dec": 2}, "cluster-aware null p under D1")

# ---- Section 4.4, Regime 2 (square seals; spec 13.7: 07-A, 07-C, 07-D, 07-E, 09-G2, 09-G3); complete primary ----
_S7 = ["13.7.complete"]
_e("nSealN", (F, ["13.2.table3.complete", "SEAL:S", "N"]), _N, "complete SEAL:S texts", "1,754 (all)")
_e("nSealMulti", (C, ["multisign.SEAL:S.complete"]), _N, "complete multi-sign SEAL:S", "1,617 (all)")
_e("nSealMeanLen", (F, _S7 + ["A_mean_legible_length"]), {"unit": "plain", "dec": 2}, "mean legible length, complete SEAL:S", "4.23 (all)")
for _p in ("first", "middle", "last"):
    _nm = {"first": "First", "middle": "Middle", "last": "Last"}[_p]
    _e("nPosEnt%sMM" % _nm, (C, ["g3", _p, "mm"]), {"unit": "plain", "dec": 2}, "positional entropy MM, %s" % _p,
       {"first": "6.77", "middle": "6.58", "last": "4.65"}[_p] + " (Table 4)")
    _e("nPosEnt%sPlug" % _nm, (C, ["g3", _p, "plugin"]), {"unit": "plain", "dec": 2}, "positional entropy plug-in, %s" % _p,
       {"first": "6.62", "middle": "6.52", "last": "4.55"}[_p] + " (Table 4)")
_e("nPosEntN", (C, ["g3", "first", "N"]), _N, "texts in the positional-entropy population (first = last N)", "1,297 (all)")
_e("nPosEntMiddleN", (C, ["g3", "middle", "N"]), _N, "middle-sign tokens")
_e("nPosEntGap", (C, ["g3", "mm_gap_first_minus_last"]), {"unit": "plain", "dec": 2}, "first minus last, MM, equal N", "2.13")
_e("nPosEntGapDone", ("core_output_D1.json", ["g3", "mm_gap_first_minus_last"]), {"unit": "plain", "dec": 2}, "same under D1")
_e("nEnrich", (C, ["g2.complete", "enrichment"]), _D, "740 terminal enrichment, complete", "10.9")
_e("nEnrichDone", ("core_output_D1.json", ["g2.complete", "enrichment"]), _D, "740 terminal enrichment under D1")
_e("nShareFinal", (C, ["g2.complete", "share_final"]), _P, "740 share of final tokens", "35")
_e("nShareOther", (C, ["g2.complete", "share_other"]), {"unit": "pct", "dec": 2}, "740 share of other legible tokens", "3.2")
_e("nShareAll", (C, ["g2.complete", "share_all_tokens"]), _P, "740 share of all legible tokens", "10.3")
_e("nMarkerTexts", (F, _S7 + ["C_terminals", "top3", 0, "texts"]), _N, "seals ending in 740 (eligible)", "567 (all)")
_e("nMarkerStems", (F, _S7 + ["C_terminals", "top3", 0, "distinct_stems"]), _N, "distinct stems before 740", "520 (all)")
_e("nMarkerStemsPct", (F, _S7 + ["C_terminals", "top3", 0, "distinct_stems_pct"]), _P, "distinct stems, %", "92")
_e("nMarkerStemsOncePct", (F, _S7 + ["C_terminals", "top3", 0, "stems_once_pct"]), _P, "stems occurring once, %", "87")
_e("nSecondMarkerPct", (F, _S7 + ["C_terminals", "top3", 1, "pct_of_eligible"]), _P, "520 as final, % of eligible", "9")
_e("nThirdMarkerPct", (F, _S7 + ["C_terminals", "top3", 2, "pct_of_eligible"]), _P, "390 as final, % of eligible", "5")
_e("nOpenersTopFive", (F, _S7 + ["D_openers", "top5_pct"]), _P, "top-5 openers' cover", "25")
_e("nFrameSeal", (F, _S7 + ["E_reuse", "SEAL:S", "frame_cov10"]), _P, "top-10 frame coverage, seals", None, "new (07-E)")
_e("nFrameTab", (F, _S7 + ["E_reuse", "TAB:I", "frame_cov10"]), _P, "top-10 frame coverage, tablets", None, "new (07-E)")

# ---- Sections 4.5 (inversion) and 4.6 (geography; spec 13.8, complete primary) ----
_e("nTabOncePct", (F, _T3C + ["E_productivity", "TAB:I", "once_pct"]), _P, "TAB:I texts occurring once, complete", "27 (Table 5)")
_G = ["13.8.complete"]
for _s, _sk in (("Harappa", "Harappa"), ("Mohenjo", "Mohenjo-daro"), ("Dholavira", "Dholavira"),
                ("Chanhu", "Chanhu-daro"), ("Lothal", "Lothal"), ("Kalibangan", "Kalibangan")):
    _e("nSite%sRate" % _s, (F, _G + ["sites_rate_740", _sk, "rate"]), _P, "740 final rate, %s, complete" % _sk)
    _e("nSite%sN" % _s, (F, _G + ["sites_rate_740", _sk, "N"]), _N, "eligible multi-sign seals, %s, complete" % _sk)
_e("nSitesAdequate", (F, _G + ["adequately_sampled_sites"]), _N, "sites with >= 30 eligible seals", "six", "bar restated (spec 13.8)")
_e("nSitesWithSeals", (F, _G + ["distinct_sites_with_SEAL:S"]), _N, "distinct sites with a SEAL:S text", "39", "unchanged")
_e("nForeignN", (F, _G + ["tiers", "foreign", "N"]), _N, "foreign eligible seals, complete", "8 (all)")
_e("nForeignHits", (F, _G + ["tiers", "foreign", "hits"]), _N, "foreign seals ending in 740, complete", "3 (all)")
_e("nForeignNAll", (F, ["13.8.all", "tiers", "foreign", "N"]), _N, "foreign eligible seals, all texts")
_e("nForeignHitsAll", (F, ["13.8.all", "tiers", "foreign", "hits"]), _N, "foreign seals ending in 740, all texts")
_e("nSealHarappaPct", (F, ["13.8.site_shares", "SEAL:S", "harappa_pct"]), _P, "SEAL:S share from Harappa", "18.0", "unchanged")
_e("nSealMohenjoPct", (F, ["13.8.site_shares", "SEAL:S", "top5", 0, 2]), _P, "SEAL:S share from Mohenjo-daro", "62", "unchanged")

# ---- Appendix A, geographic gradient (spec 13.8 appendix G4a/G4b; SCOPE_FINAL: appendix) ----
_G4 = ["13.8.complete", "appendix_G4"]
_e("nGradCoreRate", (F, _G4 + ["G4a", "core", "rate"]), _P, "core 740 rate", "37 (all)")
_e("nGradCoreN", (F, _G4 + ["G4a", "core", "N"]), _N, "core eligible seals")
_e("nGradRegRate", (F, _G4 + ["G4a", "regional", "rate"]), _P, "regional 740 rate", "27 (all)")
_e("nGradRegN", (F, _G4 + ["G4a", "regional", "N"]), _N, "regional eligible seals")
_e("nGradZ", (F, _G4 + ["G4a", "z"]), {"unit": "plain", "dec": 2}, "two-proportion z", "3.14")
_e("nGradP", (F, _G4 + ["G4a", "p"]), {"unit": "plain", "dec": 3}, "two-proportion p", "0.0017")
_e("nGradLenTwo", (F, _G4 + ["G4b_by_length", "2", "rate"]), _P, "740 rate at length 2", "21")
_e("nGradLenSix", (F, _G4 + ["G4b_by_length", "6", "rate"]), _P, "740 rate at length 6", "47")
_e("nGradMeanCore", (F, _G4 + ["G4b_mean_length", "core"]), {"unit": "plain", "dec": 2}, "mean legible length, core", "4.56")
_e("nGradMeanReg", (F, _G4 + ["G4b_mean_length", "regional"]), {"unit": "plain", "dec": 2}, "mean legible length, regional", "4.25")
for _l, _ln in (("3", "Three"), ("4", "Four"), ("5", "Five")):
    for _t, _tk in (("Core", "core"), ("Reg", "regional")):
        _e("nGradLen%s%sRate" % (_ln, _t), (F, _G4 + ["G4b_matched", _l, _tk, "rate"]), _P, "%s rate at length %s" % (_tk, _l))
        _e("nGradLen%s%sN" % (_ln, _t), (F, _G4 + ["G4b_matched", _l, _tk, "N"]), _N, "%s N at length %s" % (_tk, _l))

ENTRIES += [
    # ---- seeds from Decision 6, used when the regime sections are written ----
    {"name": "nCovTabCompleteDzero", "source": (C, ["cov10.TAB:I.complete.D0"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, complete multi-sign incised tablets, every copy",
     "was": "40 (abstract; 40.4 in the submitted Robustness section, tag chr2027-submitted)",
     "cause": "R1 + R2 + population (complete texts primary)"},
    {"name": "nCovSealCompleteDzero", "source": (C, ["cov10.SEAL:S.complete.D0"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, complete multi-sign square seals, every copy",
     "was": "3 (abstract; 3.0 in the submitted Robustness section, tag chr2027-submitted)",
     "cause": "R1 + R2 + population (complete texts primary)"},
    {"name": "nCovTabCompleteDtwoa", "source": (C, ["cov10.TAB:I.complete.D2a"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, tablets, one copy per find-spot", "cause": "new (spec 12 D2(d): D2a beside every headline figure)"},
    {"name": "nCovSealCompleteDtwoa", "source": (C, ["cov10.SEAL:S.complete.D2a"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, seals, one copy per find-spot", "cause": "new (spec 12 D2(d): D2a beside every headline figure)"},
    # D11 (AK 12 Nov 16:31): Table 5's all-texts twin, so that "every headline figure is printed for both populations"
    # (paper, Method) holds
    {"name": "nCovTabAllDzero", "source": (C, ["cov10.TAB:I.all.D0"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, all multi-sign incised tablets, every copy (Table 5)",
     "cause": "new (D11: all-texts column of Table 5)"},
    {"name": "nCovSealAllDzero", "source": (C, ["cov10.SEAL:S.all.D0"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, all multi-sign square seals, every copy (Table 5)",
     "cause": "new (D11: all-texts column of Table 5)"},
    {"name": "nFrameTabAll", "source": (F, ["13.7.all", "E_reuse", "TAB:I", "frame_cov10"]),
     "format": {"unit": "pct", "dec": 1}, "meaning": "top-10 frame coverage, tablets, all texts (Table 5)",
     "cause": "new (D11: all-texts column of Table 5)"},
    {"name": "nFrameSealAll", "source": (F, ["13.7.all", "E_reuse", "SEAL:S", "frame_cov10"]),
     "format": {"unit": "pct", "dec": 1}, "meaning": "top-10 frame coverage, seals, all texts (Table 5)",
     "cause": "new (D11: all-texts column of Table 5)"},
    {"name": "nTabOncePctAll", "source": (F, ["13.3.all", "E_productivity", "TAB:I", "once_pct"]),
     "format": {"unit": "pct", "dec": 1}, "meaning": "TAB:I texts occurring once, all texts (Table 5)",
     "cause": "new (D11: all-texts column of Table 5)"},
    {"name": "nSealOncePctAll", "source": (F, ["13.3.all", "E_productivity", "SEAL:S", "once_pct"]),
     "format": {"unit": "pct", "dec": 1}, "meaning": "SEAL:S texts occurring once, all texts (Table 5)",
     "cause": "new (D11: all-texts column of Table 5)"},
    # D11 continued (AK 12 Nov 19:02 "if figures needed ... we should have it"): the all-texts twins of the remaining
    # abstract figures, so that "every headline figure is printed for both populations" holds for each of them
    {"name": "nCovTabAllDtwoa", "source": (C, ["cov10.TAB:I.all.D2a"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, tablets, one copy per find-spot, all texts", "cause": "new (D11: all-texts twin)"},
    {"name": "nCovSealAllDtwoa", "source": (C, ["cov10.SEAL:S.all.D2a"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, seals, one copy per find-spot, all texts", "cause": "new (D11: all-texts twin)"},
    {"name": "nCovTabAllDone", "source": (C, ["cov10.TAB:I.all.D1"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, tablets, Fuls's rule (D1), all texts", "cause": "new (D11: all-texts twin)"},
    {"name": "nCovSealAllDone", "source": (C, ["cov10.SEAL:S.all.D1"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "top-10 coverage, seals, D1, all texts", "cause": "new (D11: all-texts twin)"},
    {"name": "nShareFinalAll", "source": (C, ["g2.all", "share_final"]), "format": {"unit": "pct", "dec": 1},
     "meaning": "740 share of final tokens, all texts", "cause": "new (D11: all-texts twin)"},
    {"name": "nEnrichAll", "source": (C, ["g2.all", "enrichment"]), "format": {"unit": "plain", "dec": 1},
     "meaning": "740 terminal enrichment, all texts", "cause": "new (D11: all-texts twin)"},
    {"name": "nMatchedGapCompleteDone", "source": (C1, ["matched_n.cov10.complete", "mean"]),
     "format": {"unit": "pct", "dec": 1}, "meaning": "matched-N tablet-seal gap under Fuls's rule (D1), complete",
     "cause": "new (spec 12 D2(c): D1 for every measure)"},
]

# ---- Robustness (E1 step 8, 11 Nov; SCOPE_FINAL main text + Appendix B; spec 7, 8, 13.2, 13.9-13.19, 13.21) ----
_W = "submitted Robustness section, tag chr2027-submitted"
F1 = "full_output_D1.json"
_S9 = ["13.9.complete"]
_S4 = _S9 + ["S4"]
_e("nSiteCtlTabN", (F, _S4 + ["TAB:I@Harappa", "N"]), _N, "complete multi-sign TAB:I at Harappa")
_e("nSiteCtlSealN", (F, _S4 + ["SEAL:S@Harappa", "N"]), _N, "complete multi-sign SEAL:S at Harappa")
_e("nSiteCtlMohenjoN", (F, _S4 + ["SEAL:S@Mohenjo-daro", "N"]), _N, "complete multi-sign SEAL:S at Mohenjo-daro")
_e("nSiteCtlTabCov", (F, _S4 + ["TAB:I@Harappa", "cov10"]), _P, "top-10 coverage, TAB:I at Harappa")
_e("nSiteCtlSealCov", (F, _S4 + ["SEAL:S@Harappa", "cov10"]), _P, "top-10 coverage, SEAL:S at Harappa")
_e("nSiteCtlMohenjoCov", (F, _S4 + ["SEAL:S@Mohenjo-daro", "cov10"]), _P, "top-10 coverage, SEAL:S at Mohenjo-daro")
_e("nSiteCtlTabOnce", (F, _S4 + ["TAB:I@Harappa", "once_pct"]), _P, "texts occurring once, TAB:I at Harappa")
_e("nSiteCtlSealOnce", (F, _S4 + ["SEAL:S@Harappa", "once_pct"]), _P, "texts occurring once, SEAL:S at Harappa")
_e("nSiteCtlMohenjoOnce", (F, _S4 + ["SEAL:S@Mohenjo-daro", "once_pct"]), _P, "texts occurring once, SEAL:S at Mohenjo-daro")
_e("nSiteCtlTabFinal", (F, _S4 + ["TAB:I@Harappa", "final740", "rate"]), _P, "740 final rate, TAB:I at Harappa")
_e("nSiteCtlMatched", (F, _S4 + ["within_Harappa_matched", "mean"]), _P, "within-Harappa matched-N gap, mean",
   "+35.7 (" + _W + ")")
_e("nSiteCtlMatchedLow", (F, _S4 + ["within_Harappa_matched", "p5"]), _P, "same, p5")
_e("nSiteCtlMatchedHigh", (F, _S4 + ["within_Harappa_matched", "p95"]), _P, "same, p95")
_e("nSiteCtlSpotLow", (F, _S4 + ["within_Harappa_findspot_interval", "p5"]), _P, "within-Harappa find-spot interval, p5",
   None, "new (spec 7, 13.9)")
_e("nSiteCtlSpotHigh", (F, _S4 + ["within_Harappa_findspot_interval", "p95"]), _P, "same, p95", None, "new (spec 7, 13.9)")
_H3L = _S9 + ["H3_line_within_Harappa"]
_e("nSiteCtlHThree", (F, _H3L + ["plugin_diff_mean"]), {"unit": "plain", "dec": 2},
   "within-Harappa H3 SEAL:S - TAB:I at matched trigram tokens, plug-in mean",
   "0.448 TAB:I-SEAL:S gap at matched N (" + _W + ")", "measure redefined: matched trigram tokens (spec 7, 13.9)")
_e("nSiteCtlHThreeLow", (F, _H3L + ["plugin_diff_p5"]), {"unit": "plain", "dec": 2}, "same, p5")
_e("nSiteCtlHThreeHigh", (F, _H3L + ["plugin_diff_p95"]), {"unit": "plain", "dec": 2}, "same, p95")
_e("nSiteCtlHThreeMM", (F, _H3L + ["mm_diff_mean"]), {"unit": "plain", "dec": 2}, "same, Miller-Madow mean")
_e("nSiteCtlHThreeTokens", (F, _H3L + ["T"]), _N, "trigram tokens matched (TAB:I fixed)")
for _l, _ln in (("2", "Two"), ("3", "Three"), ("4", "Four")):
    _c = _S9 + ["S6", _l]
    _e("nSLTabMean" + _ln, (F, _c + ["tab", "mean"]), _P, "Harappa, length %s, TAB:I coverage at seal N, mean" % _l)
    _e("nSLTabLow" + _ln, (F, _c + ["tab", "p5"]), _P, "same, p5")
    _e("nSLTabHigh" + _ln, (F, _c + ["tab", "p95"]), _P, "same, p95")
    _e("nSLSeal" + _ln, (F, _c + ["seal", "mean"]), _P, "Harappa, length %s, SEAL:S coverage (used whole)" % _l)
    _e("nSLTabN" + _ln, (F, _c + ["n_tab"]), _N, "Harappa, length %s, TAB:I texts" % _l)
    _e("nSLSealN" + _ln, (F, _c + ["n_seal"]), _N, "Harappa, length %s, SEAL:S texts" % _l)
    ENTRIES.append({"name": "nSLFloor" + _ln, "sources": [(F, _c + ["n_seal"])], "derive": lambda n: 100.0 * min(10, n) / n,
                    "format": _P, "meaning": "floor of top-10 coverage at the seal cell size, 100 x min(10, N) / N",
                    "was": None, "cause": "new (the 10/N floor, PREREG_chronology_Bprime_DRAFT 5(f))"})
for _sz, _sn in (("500", "FiveHundred"), ("300", "ThreeHundred"), ("150", "OneFifty"), ("60", "Sixty")):
    _e("nBias" + _sn, (F, _S9 + ["S7_bias", _sz]), _P, "TAB:I at Harappa subsampled to %s, mean coverage" % _sz)
_EST = _S9 + ["S5_estimability"]
for _nm, _cls, _key, _fn, _fmt in (("nEstSealKtriMin", "SEAL:S", "ktri_over_n", min, _P),
                                   ("nEstSealKtriMax", "SEAL:S", "ktri_over_n", max, _P),
                                   ("nEstTabKtriMin", "TAB:I", "ktri_over_n", min, _P),
                                   ("nEstTabKtriMax", "TAB:I", "ktri_over_n", max, _P),
                                   ("nEstSealTriMin", "SEAL:S", "n_tri", min, _N),
                                   ("nEstSealTriMax", "SEAL:S", "n_tri", max, _N)):
    ENTRIES.append({"name": _nm, "sources": [(F, _EST + [l + "." + _cls, _key]) for l in ("3", "4", "5")],
                    "derive": (lambda f: (lambda *v: f(v)))(_fn), "format": _fmt,
                    "meaning": "Harappa %s, lengths 3-5: %s of %s" % (_cls, _fn.__name__, _key), "was": None, "cause": "new"})
# 13.10 duplicate provenance
_M2 = ["13.10.complete", "M2"]
for _c, _ck in (("Tab", "TAB:I"), ("Seal", "SEAL:S")):
    _e("nDup%sNear" % _c, (F, _M2 + [_ck, "share_gap_le2_observed"]), _P, "%s repeat gaps <= 2, observed" % _ck,
       "15.6 (" + _W + ")" if _c == "Tab" else None)
    _e("nDup%sNearNull" % _c, (F, _M2 + [_ck, "share_gap_le2_null"]), _P, "%s repeat gaps <= 2, null" % _ck,
       "5.3 (" + _W + ")" if _c == "Tab" else None)
    _e("nDup%sMedian" % _c, (F, _M2 + [_ck, "median_gap_observed"]), _N, "%s median gap, observed" % _ck)
    _e("nDup%sMedianNull" % _c, (F, _M2 + [_ck, "median_gap_null"]), _N, "%s median gap, null" % _ck)
    _e("nDup%sKeys" % _c, (F, _M2 + [_ck, "repeated_keys"]), _N, "%s repeated keys" % _ck)
    _e("nDup%sPairs" % _c, (F, _M2 + [_ck, "repeat_pairs"]), _N, "%s repeat pairs" % _ck)
_M3 = ["13.10.complete"]
_e("nDupRows", (F, _M3 + ["M3_rows_collapsed"]), _N, "rows removed by the near-adjacent collapse",
   "344 (" + _W + "; 342 in the 24-29 Oct text; corrected 12 Nov, B4 gate G3)")
_e("nDupTabCov", (F, _M3 + ["M3_collapsed", "TAB:I_cov10"]), _P, "TAB:I coverage after collapse", "37.8 (" + _W + ")")
_e("nDupSealCov", (F, _M3 + ["M3_collapsed", "SEAL:S_cov10"]), _P, "SEAL:S coverage after collapse", "2.9 (" + _W + ")")
_e("nDupGap", (F, _M3 + ["M3_collapsed", "gap"]), _P, "gap after collapse", "+34.9 (" + _W + ")")
_e("nDupGapOrig", (F, _M3 + ["M3_original", "gap"]), _P, "gap before collapse", "+37.4 (" + _W + ")")
_e("nDupSweepPos", (F, _M3 + ["M3_sweep", "positive"]), _N, "post-collapse sweep cells positive")
_e("nDupSweepCells", (F, _M3 + ["M3_sweep", "cells"]), _N, "post-collapse sweep cells run")
_e("nDupSweepMin", (F, _M3 + ["M3_sweep", "min"]), _P, "post-collapse sweep minimum", "+26.3 (" + _W + ")")
# spec 8 grid and the 13.21 curve
_e("nGridPositive", (C, ["grid", "positive"]), _N, "grid cells with a positive gap", "432 (" + _W + ")",
   "R1 point (b): direction fork dropped, 144 genuine cells")
_e("nGridCells", (C, ["grid", "cells_run"]), _N, "grid cells run", "432 (" + _W + ")", "R1 point (b)")
_e("nGridMedian", (C, ["grid", "median"]), _P, "grid median gap", "+27.4 (" + _W + ")")
_e("nGridMin", (C, ["grid", "min"]), _P, "grid minimum gap", "+7.2 (" + _W + ")")
_e("nGridMax", (C, ["grid", "max"]), _P, "grid maximum gap", "+54.2 (" + _W + ")")


def _weak_run(cells):
    s = sorted(cells, key=lambda x: x["gap"])
    n = 0
    while n < len(s) and s[n]["tablet_class"] != "TAB:I" and s[n]["top_n"] == 5:
        n += 1
    return n


ENTRIES += [
    {"name": "nGridWeakRun", "sources": [(C, ["grid", "cells"])], "derive": _weak_run, "format": _N,
     "meaning": "weakest grid cells (ranked) that all pool TAB:B with TAB:I at top-5", "was": None, "cause": "new"},
    {"name": "nSpecCurve", "sources": [(C, ["spec_curve_points"])], "derive": lambda p: [(5 * i, v) for i, v in enumerate(p)],
     "format": {"unit": "coords", "decx": 0, "dec": 1}, "meaning": "spec curve: 21 points (x = 5q, q = 0..20; spec 13.21)",
     "was": "21 typed points (" + _W + ")", "cause": "spec 8 grid (144 cells)"},
]
# spec 7 negative control, 13.12 positive control
_e("nSynthNegMax", (C, ["synthetic_negative.complete", "max_abs_gap"]), _P, "synthetic negative control, largest |gap|",
   "+5.1 max (" + _W + "; +5.0 in the 24-29 Oct text; corrected 12 Nov, B4 gate G3)")
_e("nSynthNegMean", (C, ["synthetic_negative.complete", "mean_gap"]), _P, "synthetic negative control, mean gap",
   "+2.5 (" + _W + ")")
_e("nSynthNegObs", (C, ["synthetic_negative.complete", "observed_gap"]), _P, "observed raw gap beside the control",
   "+37.4 (" + _W + ")")
_e("nSynthPosA", (F, ["13.12.complete", "A_cov10"]), _P, "positive control, planted class coverage",
   "40.6 (" + _W + "; 40.4 in the 24-29 Oct text; corrected 12 Nov, B4 gate G3)")
_e("nSynthPosB", (F, ["13.12.complete", "B_cov10"]), _P, "positive control, plain class coverage", "1.7 (" + _W + ")")
# 13.17 sign identity (Decision 6 s.10 line-813 rewrite); D1 marker beside
_SI = ["13.17.complete"]
_e("nSignK", (F, _SI + ["K"]), _N, "sign vocabulary K (13.17)", "713 (" + _W + ")")
_e("nSignBaseTab", (F, _SI + ["base", "TAB:I"]), _P, "TAB:I coverage, unperturbed", "40.4 (" + _W + ")")
_e("nSignBaseGap", (F, _SI + ["base", "gap"]), _P, "gap, unperturbed", "+37.4 (" + _W + ")")
_SW = _SI + ["series", "SPLIT-WORST", "rows"]
_e("nSignWorstKOne", (F, _SW + [0, "k"]), _N, "SPLIT-WORST at 1%: codes split", "seven (" + _W + ")")
_e("nSignWorstTabOne", (F, _SW + [0, "tab_mean"]), _P, "SPLIT-WORST at 1%: TAB:I coverage", "25.4 (" + _W + ")")
_e("nSignWorstKTwo", (F, _SW + [1, "k"]), _N, "SPLIT-WORST at 2%: codes split", "fourteen (" + _W + ")")
_e("nSignWorstTabTwo", (F, _SW + [1, "tab_mean"]), _P, "SPLIT-WORST at 2%: TAB:I coverage", "21.6 (" + _W + ")")
_e("nSignWorstSealTwo", (F, _SW + [1, "seal_mean"]), _P, "SPLIT-WORST at 2%: SEAL:S coverage", "2.4 (" + _W + ")")
_e("nSignWorstGapTwo", (F, _SW + [1, "gap_mean"]), _P, "SPLIT-WORST at 2%: gap")
_e("nSignMergeGap", (F, _SI + ["series", "MERGE", "rows", 5, "gap_mean"]), _P, "MERGE at 40%: gap",
   None, "new: the submitted paper printed no MERGE-40% gap (its +36.3 'at 600 codes' is script 18's F6, "
   "nFsixGapSixHundred; B4 fresh-eye pass, 12 Nov)")
ENTRIES += [
    {"name": "nSignPosMin", "sources": [(F, _SI + ["series"])],
     "derive": lambda s: min(r["inverted_pct"] for m in ("MERGE", "SPLIT", "SPLIT-WORST") for r in s[m]["rows"]),
     "format": {"unit": "pct", "dec": 0}, "meaning": "smallest share of draws with a positive gap, any mode and rate",
     "was": "200 of 200 (" + _W + ")", "cause": "R1 + R2 + population"},
    {"name": "nSignSealOtherMin", "sources": [(F, _SI + ["series"])],
     "derive": lambda s: min(min(s["MERGE"]["sea"]), min(s["SPLIT"]["sea"])), "format": _P,
     "meaning": "seal coverage under MERGE and SPLIT, smallest mean", "was": None, "cause": "new"},
    {"name": "nSignSealOtherMax", "sources": [(F, _SI + ["series"])],
     "derive": lambda s: max(max(s["MERGE"]["sea"]), max(s["SPLIT"]["sea"])), "format": _P,
     "meaning": "same, largest mean", "was": None, "cause": "new"},
]
for _m, _mn in (("MERGE", "Merge"), ("SPLIT", "Split"), ("SPLIT-WORST", "Worst")):
    for _cl, _cn in ((("tab", "Tab"), ("sea", "Seal")) if _m == "SPLIT-WORST" else (("tab", "Tab"),)):
        ENTRIES.append({"name": "nSignCurve%s%s" % (_mn, _cn), "sources": [(F, _SI + ["series", _m, _cl])],
                        "derive": lambda v: [(i, y) for i, y in enumerate(v)], "format": {"unit": "coords", "decx": 0, "dec": 1},
                        "meaning": "fig:signid %s %s means at rates 0,1,2,5,10,20,40 pct (x = index)" % (_m, _cl),
                        "was": None, "cause": "spec 13.21"})
_MK = _SI + ["marker"]
_e("nSignMarkerTerm", (F, _MK + ["baseline", "terminal_pct"]), _P, "740 terminal rate, unsplit", "35.1 (" + _W + ")")
_e("nSignMarkerTermA", (F, _MK + ["half_740a", "terminal_pct"]), _P, "740a terminal rate", "18.0 (" + _W + ")")
_e("nSignMarkerTermB", (F, _MK + ["half_740b", "terminal_pct"]), _P, "740b terminal rate", "17.1 (" + _W + ")")
_e("nSignMarkerEnrich", (F, _MK + ["baseline", "enrichment"]), _D, "740 enrichment, unsplit", "10.9 (" + _W + ")")
_e("nSignMarkerEnrichA", (F, _MK + ["half_740a", "enrichment"]), _D, "740a enrichment", "12.6 (" + _W + ")")
_e("nSignMarkerEnrichB", (F, _MK + ["half_740b", "enrichment"]), _D, "740b enrichment", "9.5 (" + _W + ")")
_e("nSignMarkerEnrichDone", (F1, _MK + ["baseline", "enrichment"]), _D, "740 enrichment, unsplit, D1", None, "new (D6 s.10)")
_e("nSignMarkerEnrichDoneA", (F1, _MK + ["half_740a", "enrichment"]), _D, "740a enrichment, D1", None, "new (D6 s.10)")
_e("nSignMarkerEnrichDoneB", (F1, _MK + ["half_740b", "enrichment"]), _D, "740b enrichment, D1", None, "new (D6 s.10)")
_e("nSignBiteRewritten", (F, _SI + ["bite_merge40", "tokens_rewritten"]), _N, "MERGE 40%: tablet tokens rewritten")
_e("nSignBiteTokens", (F, _SI + ["bite_merge40", "tablet_tokens"]), _N, "MERGE 40%: tablet tokens")
_e("nSignBiteAltered", (F, _SI + ["bite_merge40", "sequences_altered"]), _N, "MERGE 40%: tablet sequences altered")
_e("nSignBiteDistinctBefore", (F, _SI + ["bite_merge40", "distinct_before"]), _N, "MERGE 40%: distinct sequences before",
   "288 (" + _W + ")")
_e("nSignBiteDistinctAfter", (F, _SI + ["bite_merge40", "distinct_after"]), _N, "MERGE 40%: distinct sequences after",
   "287 (" + _W + ")")
_e("nSignNoteCodes", (F, _SI + ["note_load_bearing_codes"]), _N, "codes the top-10 tablet texts are built from",
   "fifteen (" + _W + ")")
_e("nSignProvTwoK", (F, _SI + ["provenance", "0.02", "k"]), _N, "worst-case split at 2%: codes")
_e("nSignProvTwoPct", (F, _SI + ["provenance", "0.02", "pct"]), {"unit": "pct", "dec": 0},
   "share of surviving top-10 texts that are fragments, 2%")
_e("nSignProvFortyK", (F, _SI + ["provenance", "0.4", "k"]), _N, "worst-case split at 40%: codes")
_e("nSignProvFortyPct", (F, _SI + ["provenance", "0.4", "pct"]), {"unit": "pct", "dec": 0}, "same, 40%")
# 13.19 storage test (real corpus; the self-test mutant is in the verdicts)
_RL = ["13.19", "real"]
for _nm, _path, _mean in (("nStoreLRN", ["T1.L/R", "N"], "L/R texts (T1)"),
                          ("nStoreLRLeft", ["T1.L/R", "left"], "L/R: 740 at the stored left end"),
                          ("nStoreLRRight", ["T1.L/R", "right"], "L/R: 740 at the stored right end"),
                          ("nStoreRLN", ["T1.R/L", "N"], "R/L texts (T1)"),
                          ("nStoreRLLeft", ["T1.R/L", "left"], "R/L: 740 at the stored left end"),
                          ("nStoreRLRight", ["T1.R/L", "right"], "R/L: 740 at the stored right end"),
                          ("nStoreInitLRLeft", ["T2.L/R", "left"], "L/R: initial-type signs at the stored left end"),
                          ("nStoreInitLRRight", ["T2.L/R", "right"], "L/R: initial-type signs at the stored right end"),
                          ("nStoreInitRLLeft", ["T2.R/L", "left"], "R/L: initial-type signs at the stored left end"),
                          ("nStoreInitRLRight", ["T2.R/L", "right"], "R/L: initial-type signs at the stored right end"),
                          ("nStoreTThreeN", ["T3", "N"], "T3 L/R texts tested"),
                          ("nStoreTThreeSame", ["T3", "same"], "T3 equal to an R/L text as stored"),
                          ("nStoreTThreeRev", ["T3", "reversed"], "T3 equal to an R/L text only reversed")):
    _e(_nm, (F, _RL + _path), _N, _mean, None, "new (13.19, replaces the 09-G6 row)")
_e("nStoreTFourSame", (F, _RL + ["T4", "same"]), {"unit": "plain", "dec": 2}, "T4 cosine, as stored", None, "new (13.19)")
_e("nStoreTFourRev", (F, _RL + ["T4", "reversed"]), {"unit": "plain", "dec": 2}, "T4 cosine, reversed", None, "new (13.19)")
ENTRIES += [
    {"name": "nStoreVerdictsTrue", "sources": [(F, ["13.19", "verdict"])],
     "derive": lambda v: sum(1 for x in v.values() if x is True), "format": _N,
     "meaning": "storage-test verdicts that hold (checks and their mutant flips)", "was": None, "cause": "new (13.19)"},
    {"name": "nStoreVerdicts", "sources": [(F, ["13.19", "verdict"])], "derive": len, "format": _N,
     "meaning": "storage-test verdicts", "was": None, "cause": "new (13.19)"},
]
# spec 7 hold-out, all three groupings (Appendix B table)
for _g, _gn in (("G3", "Spot"), ("G1", "Text"), ("G2", "Object")):
    for _c, _ck in (("Tab", "TAB:I"), ("Seal", "SEAL:S")):
        _h = ["holdout.%s.%s.complete" % (_g, _ck)]
        for _st, _sk in (("In", "in_mean"), ("Out", "out_mean"), ("OutLow", "out_p5"), ("OutHigh", "out_p95"),
                         ("Ret", "retained_mean"), ("RetLow", "retained_p5"), ("RetHigh", "retained_p95")):
            _e("nHold%s%s%s" % (_gn, _c, _st), (C, _h + [_sk]),
               {"unit": "pct", "dec": 0} if _st.startswith("Ret") else _P, "hold-out %s %s %s" % (_g, _ck, _sk))
# 13.11 text-level beside; 13.13 class prediction; 13.14 mould; 13.15 shared texts; 13.18 F6; 13.2 singleton shares
_e("nClusterTextMax", (F, ["13.11.complete", "text_level", "null_max"]), _P, "text-level label null, largest gap",
   "+4.8 (" + _W + ")")
_PR = ["13.13.complete"]
_e("nPredAcc", (F, _PR + ["accuracy"]), _P, "class prediction accuracy", "82.3 (" + _W + ")",
   "find-spot groups (13.13 stated change)")
_e("nPredBase", (F, _PR + ["majority_baseline"]), _P, "majority-class baseline", "69.0 (" + _W + ")")
_e("nPredBal", (F, _PR + ["balanced_accuracy"]), _P, "balanced accuracy", "79.9 (" + _W + ")")
_e("nPredTabRecall", (F, _PR + ["tablet_recall"]), _P, "tablet recall")
_e("nPredSealRecall", (F, _PR + ["seal_recall"]), _P, "seal recall")
_e("nMouldTabB", (F, ["13.14.complete", "TAB:B"]), _P, "top-10 coverage, complete multi-sign TAB:B", "28 (" + _W + ")")
_e("nMouldTabBN", (F, ["13.14.complete", "N", "TAB:B"]), _N, "complete multi-sign TAB:B")
_e("nSharedTypesMulti", (F, ["13.15", "multisign", "keys_with_more_than_one_type"]), _N,
   "multi-sign texts on > 1 object type", "234 (" + _W + ")")
_e("nSharedBothMulti", (F, ["13.15", "multisign", "keys_in_both_TAB:I_and_SEAL:S"]), _N,
   "multi-sign texts on both TAB:I and SEAL:S", "52 (" + _W + ")")
_e("nSharedTypesAny", (F, ["13.15", "any_length", "keys_with_more_than_one_type"]), _N, "texts of any length on > 1 type")
_e("nSharedBothAny", (F, ["13.15", "any_length", "keys_in_both_TAB:I_and_SEAL:S"]), _N, "texts of any length on both")
_e("nFsixGapSixHundred", (F, ["13.18.complete", "F6", "600", "gap"]), _P, "F6: gap with the 600 rarest signs merged",
   "+36.3 (" + _W + ")")
for _c, _ck in (("SealS", "SEAL:S"), ("SealR", "SEAL:R"), ("TabB", "TAB:B"), ("TabI", "TAB:I"), ("PotG", "POT:T:g")):
    _e("nSingle%sObs" % _c, (F, ["13.2.singleton.%s.complete" % _ck, "observed"]), _P,
       "singleton-context share, %s, observed" % _ck)
    _e("nSingle%sShuf" % _c, (F, ["13.2.singleton.%s.complete" % _ck, "shuffled_mean"]), _P, "same, mean of 200 shuffles")

# ---- Re-verification gaps G-a, G-b (11 Nov; REVERIFY_ROBUSTNESS.md item 1): spec 13.2 values not yet printed ----
for _c, _ck in _T3.items():
    _e("nTabThree%sHThreeMM" % _c, (F, ["13.2.table3.complete", _ck, "H3_mm"]), {"unit": "plain", "dec": 2},
       "Table 3, complete, %s H3 Miller-Madow" % _ck, None, "spec 13.2 column (SCOPE_FINAL: MM stays in Table 3)")
    _n = ["13.2.null.%s.complete" % _ck]
    _e("nNull%sMin" % _c, (F, _n + ["null_min"]), {"unit": "plain", "dec": 2}, "shuffle null minimum H3, %s" % _ck,
       {"TabI": "0.37", "TabB": "0.66"}.get(_c) and {"TabI": "0.37", "TabB": "0.66"}[_c] + " (submitted Robustness)")
    _e("nNull%sP" % _c, (F, _n + ["p"]), {"unit": "plain", "dec": 4}, "shuffle null p = (1 + #{null <= obs}) / (1 + iter), %s" % _ck,
       {"TabI": "< 1e-4", "TabB": "< 1e-4", "SealS": "1.0", "PotG": "0.83"}.get(_c))
    _e("nNull%sRed" % _c, (F, _n + ["reduction_pct"]), {"unit": "pct", "dec": 0}, "shuffle null reduction %%, %s" % _ck,
       {"TabI": "58", "TabB": "48"}.get(_c))
    _e("nNull%sIter" % _c, (F, _n + ["iterations"]), _N, "shuffle null iterations, %s" % _ck)
ENTRIES.append({"name": "nNullTemplatedCount", "sources": [(F, ["13.2.null.%s.complete" % k, "templated"]) for k in _T3.values()],
                "derive": lambda *v: sum(1 for x in v if x is True), "format": _N,
                "meaning": "classes meeting script 10's rule (p < 0.05 and reduction > 0), complete", "was": None,
                "cause": "spec 13.2"})

# ---- Discussion (E1 step 9, 11 Nov): the Yadav 2013 protocol (spec 8, script 14) ----
_e("nYadavShare", (C, ["yadav2013", "share"]), _P,
   "four most frequent texts (all classes, >= 2 legible signs, any completeness): share of TAB:I at Harappa",
   "28.4 (submitted Discussion)", "R1 + R2 (spec 8 protocol)")
_e("nYadavNum", (C, ["yadav2013", "numerator"]), _N, "Harappa TAB:I texts that are one of the four", None, "new (spec 8)")
_e("nYadavDen", (C, ["yadav2013", "denominator"]), _N, "Harappa TAB:I texts with >= 2 legible signs", None, "new (spec 8)")

# ---- Limitations (E1 step 10, 11 Nov): B' (PREREG_chronology_Bprime_DRAFT; spec 12(g)), 13.16 P7, site counts ----
_WB = "submitted Limitations (old period-label test, withdrawn by the B' registration)"
for _v, _vn in (("primary", ""), ("sensitivity", "S")):
    for _c, _cn in (("V-VII", "V"), ("IV", "IV")):
        _b = ["bprime.%s.%s" % (_v, _c)]
        _p = "nBp%s%s" % (_vn, _cn)
        _e(_p + "Tab", (C, _b + ["n_tab_all"]), _N, "B' %s %s: TAB:I texts (all)" % (_v, _c), None, "new (B')")
        _e(_p + "Seal", (C, _b + ["n_seal_all"]), _N, "B' %s %s: SEAL:S texts (all)" % (_v, _c), None, "new (B')")
        _e(_p + "TabC", (C, _b + ["n_tab_complete"]), _N, "same, complete", None, "new (B')")
        _e(_p + "SealC", (C, _b + ["n_seal_complete"]), _N, "same, complete", None, "new (B')")
        _e(_p + "Gap", (C, _b + ["matched", "mean"]), _P, "B' %s %s: matched-N gap, mean" % (_v, _c),
           {"V": "+33.1 (period label withheld)", "IV": "+15.2 (period label withheld)"}.get(_cn) if _vn == "" else None, "B' replaces the period-label test")
        _e(_p + "Low", (C, _b + ["matched", "p5"]), _P, "same, p5")
        _e(_p + "High", (C, _b + ["matched", "p95"]), _P, "same, p95")
        _e(_p + "Pos", (C, _b + ["matched", "frac_gt0"]), {"unit": "pct", "dec": 1}, "same, share of draws > 0 (spec 12(g))")
        _e(_p + "Dtwoa", (C, _b + ["d2a_matched", "mean"]), _P, "B' %s %s: one copy per find-spot, mean" % (_v, _c))
        _e(_p + "DtwoaLow", (C, _b + ["d2a_matched", "p5"]), _P, "same, p5")
        _e(_p + "DtwoaPos", (C, _b + ["d2a_matched", "frac_gt0"]), {"unit": "pct", "dec": 1}, "same, share of draws > 0")
        _e(_p + "RepTab", (C, _b + ["repeat_share_tab"]), _P, "B' %s %s: TAB:I repeat share" % (_v, _c))
        _e(_p + "RepSeal", (C, _b + ["repeat_share_seal"]), _P, "B' %s %s: SEAL:S repeat share" % (_v, _c))
ENTRIES += [
    {"name": "nBpFloorLow", "sources": [(C, ["bprime.primary.V-VII", "n_seal_all"]), (C, ["bprime.primary.IV", "n_seal_all"])],
     "derive": lambda a, b: 100.0 * 10 / max(a, b), "format": _P, "meaning": "B' primary: top-10 floor at the larger seal cell",
     "was": None, "cause": "new (B' registration s.2 (i): the floor stated beside the result)"},
    {"name": "nBpFloorHigh", "sources": [(C, ["bprime.primary.V-VII", "n_seal_all"]), (C, ["bprime.primary.IV", "n_seal_all"])],
     "derive": lambda a, b: 100.0 * 10 / min(a, b), "format": _P, "meaning": "B' primary: top-10 floor at the smaller seal cell",
     "was": None, "cause": "new (B' registration s.2 (i))"},
    {"name": "nBpDoneMaxAbs", "sources": [(C1, ["bprime.%s.%s" % (v, c), "matched", "mean"])
                                           for v in ("primary", "sensitivity") for c in ("V-VII", "IV")],
     "derive": lambda *g: max(abs(x) for x in g), "format": _P,
     "meaning": "B' under the maintainers' rule (D1): largest |matched gap| over both variants and cells",
     "was": None, "cause": "new (D6 C6: F under D1)"},
    {"name": "nTabIMohenjoN", "sources": [(F, ["13.8.site_shares", "TAB:I", "top5"])],
     "derive": lambda top: next(n for s, n, _p in top if s == "Mohenjo-daro"), "format": _N,
     "meaning": "analyzable TAB:I texts from Mohenjo-daro (found by name in the top-5 list)", "was": "8 (l.~675)",
     "cause": "unchanged"},
]
_P7 = ["13.16", "P7"]
_e("nPsevenTabTexts", (F, _P7 + ["multisign_tab_texts"]), _N, "multi-sign TAB:I texts (all)", None, "new (13.16 P7)")
_e("nPsevenOnMulti", (F, _P7 + ["texts_on_multi_text_objects"]), _N, "of them on objects with > 1 multi-sign text",
   "538 (l.~837)", "13.16 P7: ICIT object ids, every row has one")
_e("nPsevenMultiPct", (F, _P7 + ["pct_on_multi_text_objects"]), _P, "same, %", "78 (l.~835)", "13.16 P7")
_e("nPsevenMultiObj", (F, _P7 + ["tab_objects_with_more_than_one_multisign_text"]), _N, "objects with > 1 multi-sign TAB:I text",
   "254 (l.~837)", "13.16 P7")
_e("nPsevenRepeatObj", (F, _P7 + ["tab_objects_repeating_a_key"]), _N, "objects repeating a text across sides", "one (l.~837)", "13.16 P7")
