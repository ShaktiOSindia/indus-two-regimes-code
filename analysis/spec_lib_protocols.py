"""Part 2b of the shared library: published-work protocols (spec 8), the specification-curve points (13.21), the seal
measures of 13.7, and the chronology test B' (PREREG_chronology Amendment 1). Builds on spec_lib and
spec_lib_measures. Standard library; Python 3.11. Readings of the text: SPEC_READINGS.md.
"""
import collections
import re
import math
import statistics

import spec_lib as S
import spec_lib_measures as M
from spec_lib_measures import (MEASURES, SEAL, TAB, LN2, apply_copy_rule, class_rows, coverage, final740, matched_n,
                               repeat_share, top_keys, whole_text_rows)


# ------------------------------------------------------------------------------------ published-work protocols (8)
def ebuds_like(rows):
    """Spec 8: complete; single-line; one copy per identical key across the whole corpus (all sites and types; copy
    kept = smallest row index); legible length 1 to 14. Filters in the order listed (SPEC_READINGS no. 9)."""
    cand = [r for r in rows if r.analyzable and r.complete and r.single_line]
    seen, out = set(), []
    for r in sorted(cand, key=lambda x: x.index):
        if r.key not in seen:
            seen.add(r.key)
            out.append(r)
    return [r for r in out if 1 <= r.n_legible <= 14]


def table2_samples(rows):
    """Spec 8: EBUDS-like; full = every analyzable text; sensitivity row = `dir.` exactly R/L or L/R. Under a copy
    rule (spec 12 D2(c)) the full and sensitivity samples take one copy per key AFTER their own filters; EBUDS-like
    keeps its own corpus-wide one-copy rule."""
    full = [r for r in rows if r.analyzable]
    return {"ebuds_like": ebuds_like(rows), "full": apply_copy_rule(full),
            "sensitivity_rl_lr": apply_copy_rule([r for r in full if r.dir in ("R/L", "L/R")])}


def yadav2013(rows):
    """Spec 8: texts of any completeness with >= 2 legible signs; the four most frequent keys over all such texts of
    all classes and sites (section 7 order); their share of all such TAB:I texts at Harappa."""
    pool = apply_copy_rule([r for r in rows if r.analyzable and r.n_legible >= 2])   # copy rule last (D2(c))
    four = [k for k, _ in top_keys([r.key for r in pool], k=4)]
    four_set = set(four)
    har = [r for r in pool if r.type == TAB and r.site == "Harappa"]
    num = sum(1 for r in har if r.key in four_set)
    return {"keys": [S.serialize(k) for k in four], "numerator": num, "denominator": len(har),
            "share": 100.0 * num / len(har)}


def key_without_000(key):
    """Spec 8 grid setting '000 removed' (999 is already absent from every key)."""
    right, lines, left = key
    return (right, tuple(tuple(t for t in line if t != "000") for line in lines), left)


GRID_SITES = (("all", None), ("Harappa", ("Harappa",)), ("Harappa+Mohenjo-daro", ("Harappa", "Mohenjo-daro")))


def grid(rows):
    """Spec 8: 000 (kept | removed) x minimum legible length (2 | 3) x sites (all | Harappa | Harappa and
    Mohenjo-daro) x population (all | complete) x tablet class (TAB:I | TAB:I and TAB:B) x top-N (5 | 10 | 20) =
    144 cells; a cell runs only with >= 30 texts in each class; statistic = raw top-N coverage, tablets minus SEAL:S."""
    cells = []
    for z in ("kept", "removed"):
        for min_len in (2, 3):
            for site_name, sites in GRID_SITES:
                for pop in ("all", "complete"):
                    for tabs in (("TAB:I",), ("TAB:I", "TAB:B")):
                        def sel(types):
                            sel_rows = [r for r in class_rows(rows, None, pop, min_legible=min_len, types=types)
                                        if sites is None or r.site in sites]
                            return [r.key if z == "kept" else key_without_000(r.key) for r in sel_rows]
                        t, s = sel(tabs), sel((SEAL,))
                        for n in (5, 10, 20):
                            if len(t) >= 30 and len(s) >= 30:
                                cells.append({"000": z, "min_len": min_len, "sites": site_name, "population": pop,
                                              "tablet_class": "+".join(tabs), "top_n": n, "n_tablet": len(t),
                                              "n_seal": len(s), "gap": coverage(t, n) - coverage(s, n)})
    gaps = [c["gap"] for c in cells]
    return {"cells": cells, "cells_run": len(cells), "positive": sum(1 for g in gaps if g > 0), "min": min(gaps),
            "median": statistics.median(gaps), "max": max(gaps), "negative_cells": [c for c in cells if c["gap"] < 0]}


def spec_curve_points(gaps):
    """Spec 13.21: 21 points of the sorted gaps at p = q / 20 by linear interpolation at pos = p (n - 1)."""
    g = sorted(gaps)
    pts = []
    for q in range(21):
        pos = (q / 20.0) * (len(g) - 1)
        lo = int(pos)
        hi = min(lo + 1, len(g) - 1)
        pts.append(g[lo] + (g[hi] - g[lo]) * (pos - lo))
    return pts


# ------------------------------------------------------------------------------------------ seal measures (13.7)
def g2_enrichment(seal_rows):
    """13.7 [09-G2]: among multi-sign texts with an eligible reading-final token: 740's share of all their legible
    tokens, of their final tokens and of their other legible tokens; enrichment = final share / other share."""
    el = [r for r in seal_rows if r.n_legible >= 2 and r.final_eligible]
    toks = [t for r in el for t in r.legible_reading]
    final = [r.final_sign for r in el]
    other = [t for r in el for t in r.legible_reading[:-1]]
    sh_all = 100.0 * toks.count("740") / len(toks)
    sh_fin = 100.0 * final.count("740") / len(final)
    sh_oth = 100.0 * other.count("740") / len(other)
    return {"texts": len(el), "share_all_tokens": sh_all, "share_final": sh_fin, "share_other": sh_oth,
            "enrichment": sh_fin / sh_oth}


def entropy_mm(items):
    """Positional entropy (13.7): plug-in H and Miller-Madow H + (K - 1) / (2 N ln 2)."""
    c = collections.Counter(items)
    n = sum(c.values())
    h = -sum((v / n) * math.log2(v / n) for v in c.values())
    return {"plugin": h, "mm": h + (len(c) - 1) / (2.0 * n * LN2), "N": n, "K": len(c)}


def g3_positional(seal_rows, complete_only=True):
    """13.7 [07-B, 09-G3]: complete both-end-eligible texts with >= 3 legible signs: first, middle (legible signs
    strictly between), last; plug-in and Miller-Madow; the MM first-minus-last gap at equal N. complete_only=False:
    the all-texts row beside (spec 12 D2(j))."""
    el = [r for r in seal_rows if (r.complete or not complete_only) and r.n_legible >= 3 and r.final_eligible
          and r.initial_eligible]
    first = [r.initial_sign for r in el]
    last = [r.final_sign for r in el]
    middle = [t for r in el for t in r.reading_lines[0][1:-1] if S.legible(t)]
    f, m, l = entropy_mm(first), entropy_mm(middle), entropy_mm(last)
    return {"n": len(el), "first": f, "middle": m, "last": l, "mm_gap_first_minus_last": f["mm"] - l["mm"]}


# --------------------------------------------------------------------------------------------- B' (Amendment 1)
def bprime(rows, variant):
    """Amendment 1: Harappa TAB:I vs SEAL:S, >= 2 legible signs, test population ALL texts; cells V-VII and IV; a cell
    is tested only with >= 30 texts of each class; matched-N top-10 coverage gap (200 draws, seed 42); criterion met
    if p5 > 0; beside it: repeat shares, the D2a-copy statistic, the 740-final rate; complete-text sizes printed."""
    out, fps = {}, {}
    for cell in ("V-VII", "IV"):
        def sel(cls, pop):
            # the cell is part of the population: the copy rule comes AFTER it (spec 12 D2(c))
            return apply_copy_rule([r for r in whole_text_rows(rows, cls, pop, copy=False)
                                    if r.site == "Harappa" and S.bprime_cell(S.bprime_level(r, variant)) == cell])
        t, s = sel(TAB, "all"), sel(SEAL, "all")
        res = {"n_tab_all": len(t), "n_seal_all": len(s), "n_tab_complete": len(sel(TAB, "complete")),
               "n_seal_complete": len(sel(SEAL, "complete")), "tested": len(t) >= 30 and len(s) >= 30}
        if res["tested"]:
            m = matched_n(t, s, MEASURES["cov10"], return_diffs=True)
            res["matched"] = {k: m[k] for k in ("mean", "p5", "p95")}
            res["matched"]["frac_gt0"] = frac_positive(m["diffs"])
            fps["%s.matched" % cell] = m["fingerprint"]
            res["criterion_met"] = m["p5"] > 0
            res["repeat_share_tab"] = repeat_share([r.key for r in t])
            res["repeat_share_seal"] = repeat_share([r.key for r in s])
            if M.COPY_RULE == "D0":                        # D2a is finer than D1: not computed under a copy rule
                d = matched_n(S.dedupe(t, "D2a"), S.dedupe(s, "D2a"), MEASURES["cov10"], return_diffs=True)
                res["d2a_matched"] = {k: d[k] for k in ("mean", "p5", "p95")}
                res["d2a_matched"]["frac_gt0"] = frac_positive(d["diffs"])
                fps["%s.d2a_matched" % cell] = d["fingerprint"]
            ft, fs = final740(t), final740(s)
            res["final740_tab"] = ft["rate"]
            res["final740_seal"] = fs["rate"]
            res["final740_tab_eligible"], res["final740_tab_hits"] = ft["eligible"], ft["hits"]
            res["final740_seal_eligible"], res["final740_seal_hits"] = fs["eligible"], fs["hits"]
        out[cell] = res
    out["outcome"] = bprime_outcome(out["V-VII"], out["IV"])
    out["fingerprints"] = fps                              # the runner moves these to the fingerprint file
    return out


def frac_positive(values):
    """[S8] frac>0 (kept by Amendment 1): percent of draws whose gap is strictly positive."""
    return 100.0 * sum(1 for v in values if v > 0) / len(values)


# ------------------------------------------------------------------------------- spec 12 D2(f), (i): file facts
def d2b_fill(rows):
    """D2(f): over ALL analyzable rows of TAB:I and of SEAL:S, the rows whose room-grid / depth is not MISSING."""
    out = {}
    for cls in (TAB, SEAL):
        sel = [r for r in rows if r.analyzable and r.type == cls]
        rg = sum(1 for r in sel if not S.is_missing(r.room_grid))
        dp = sum(1 for r in sel if not S.is_missing(r.depth))
        out[cls] = {"rows": len(sel), "room_grid_filled": rg, "room_grid_pct": 100.0 * rg / len(sel),
                    "depth_filled": dp, "depth_pct": 100.0 * dp / len(sel)}
    return out


def data_facts(rows):
    """D2(i): facts the paper prints, computed from the pinned file. Area values ending in '-' (spec 6, from the
    classified list); rows with an UNKNOWN find-spot per class; row order (13.10: the definitions of
    `profile/paper_t10/spec13_check/probe_row_order.py`, unchanged); Harappa Mound F rows (B': area starts 'F')."""
    known, unknown = S.classify_dash_areas(rows)
    pairs = set(known) | set(unknown)
    dash_rows = [r for r in rows if (r.site, r.area) in pairs]
    trench_rows = [r for r in rows if (r.site, r.area) in set(known)]

    def icit_key(v):
        a, _, b = v.strip().partition(".")
        return (int(a), int(b or 0)) if a.isdigit() and (b.isdigit() or not b) else None
    ik = [icit_key(r.id) for r in rows]
    ip = [(a, b) for a, b in zip(ik, ik[1:]) if a and b]
    real = re.compile(r"^([A-Za-z]+)-(\d+)$")
    ck = [real.match(r.cisi.strip()) for r in rows]
    same = [(a, b) for a, b in zip(ck, ck[1:]) if a and b and a.group(1) == b.group(1)]
    unk = {}
    for cls in (TAB, SEAL):
        sel = [r for r in rows if r.analyzable and r.type == cls]
        unk[cls] = {"rows": len(sel), "unknown_findspot": sum(1 for r in sel if r.findspot[0] == "row")}
    mound_f = [r for r in rows if r.site == "Harappa" and r.area.startswith("F")]
    return {"dash_area_values": len(pairs), "dash_area_rows": len(dash_rows), "dash_trench_values": len(known),
            "dash_trench_rows": len(trench_rows), "dash_unknown_values": len(unknown),
            "unknown_findspot_by_class": unk, "icit_order_ok": sum(1 for a, b in ip if a <= b),
            "icit_order_pairs": len(ip), "cisi_order_ok": sum(1 for a, b in same if int(a.group(2)) <= int(b.group(2))),
            "cisi_order_pairs": len(same), "mound_f_rows": len(mound_f),
            "mound_f_rows_analyzable": sum(1 for r in mound_f if r.analyzable)}


def bprime_outcome(big, small):
    """Amendment 1 s.4: H = criterion met in both cells; P = met in one; F = not met in V-VII (the larger cell);
    C = fallback, no cell tested. (Each cell dict: "tested" and, when tested, "criterion_met".)"""
    if not big["tested"] and not small["tested"]:
        return "C"
    if big["tested"] and not big["criterion_met"]:
        return "F"
    if big["tested"] and small["tested"] and big["criterion_met"] and small["criterion_met"]:
        return "H"
    return "P"
