"""Part 3c of the shared library: spec section 13 entries 13.9 (site control, script 13), 13.10 (duplicate provenance,
script 16 M2/M3), 13.11 (cluster-aware label null), 13.12 (synthetic positive control, script 17-H3) and 13.13
(class prediction, script 17-H5). Builds on spec_lib, spec_lib_measures. Standard library; Python 3.11.
"""
import collections
import random
import statistics

import spec_lib as S
import spec_lib_measures as M

HARAPPA, MD = "Harappa", "Mohenjo-daro"
PERMS = 1000                                                         # script 17
BIAS_SIZES = (700, 500, 300, 150, 60)                                # script 13 [S7]


def at_site(rows, site):
    return [r for r in rows if r.site == site]


# ------------------------------------------------------------------------------------------------------ 13.9
def matched_n_detail(tab_rows, seal_rows, measure, draws=S.DRAWS):
    """Section 7's matched-N summary (the same draws as spec_lib_measures.matched_n) plus each class's own value
    per draw: mean, p5, p95 (13.9 [S6]; a class used whole has one value)."""
    rng = S.new_rng()
    n = min(len(tab_rows), len(seal_rows))
    d, vt, vs = [], [], []
    for _ in range(draws):
        t = rng.sample(tab_rows, n) if len(tab_rows) > n else tab_rows
        s = rng.sample(seal_rows, n) if len(seal_rows) > n else seal_rows
        a, b = measure(t), measure(s)
        vt.append(a)
        vs.append(b)
        d.append(a - b)
    return {"n": n, "diff": M.summary(d), "tab": M.summary(vt), "seal": M.summary(vs)}


def subsample_mean(rows, n, measure, draws=S.DRAWS):
    """13.9 [S7]: mean of the measure over 200 draws of rng.sample(rows, n), one generator per size."""
    rng = S.new_rng()
    return sum(measure(rng.sample(rows, n)) for _ in range(draws)) / draws


def site_control(rows, pop):
    cov = M.MEASURES["cov10"]
    tab = M.whole_text_rows(rows, M.TAB, pop)
    seal = M.whole_text_rows(rows, M.SEAL, pop)
    th, sh, sm = at_site(tab, HARAPPA), at_site(seal, HARAPPA), at_site(seal, MD)
    s4 = {}
    for label, g in (("TAB:I@Harappa", th), ("SEAL:S@Harappa", sh), ("SEAL:S@Mohenjo-daro", sm)):
        ks = [r.key for r in g]
        s4[label] = {"N": len(g), "cov10": M.coverage(ks), "once_pct": 100.0 - M.repeat_share(ks),
                     "final740": M.final740(g)}
    m = M.matched_n(th, sh, cov)
    f = M.findspot_interval(th, sh, cov)
    s4["within_Harappa_matched"] = {k: m[k] for k in ("n", "mean", "p5", "p95")}
    s4["within_Harappa_findspot_interval"] = {k: f[k] for k in ("p5", "p95", "draws_discarded")}
    s6 = {}
    for n in (2, 3, 4):
        t, s = [r for r in th if r.n_legible == n], [r for r in sh if r.n_legible == n]
        if len(t) >= 15 and len(s) >= 15:
            s6[str(n)] = dict(matched_n_detail(t, s, cov), n_tab=len(t), n_seal=len(s))
    s7 = {str(n): subsample_mean(th, n, cov) for n in BIAS_SIZES if n <= len(th)}
    s5 = {}
    for n in (2, 3, 4, 5):
        for cls in (M.TAB, M.SEAL):
            g = [r for r in at_site(M.entropy_rows(rows, cls, pop), HARAPPA) if r.n_legible == n]
            h = M.h3(M.runs_of(g))
            s5["%d.%s" % (n, cls)] = {"texts": len(g), "n_tri": h["n_tri"], "k_tri": h["k_tri"],
                                      "ktri_over_n": h["ktri_over_n"]}
    et = at_site(M.entropy_rows(rows, M.TAB, pop), HARAPPA)
    es = at_site(M.entropy_rows(rows, M.SEAL, pop), HARAPPA)
    e = M.entropy_matched(et, es)
    e.pop("fingerprint")
    return {"S4": s4, "S6": s6, "S7_bias": s7, "S5_estimability": s5, "H3_line_within_Harappa": e}


# ----------------------------------------------------------------------------------------------------- 13.10
def gaps(indexes):
    g = sorted(indexes)
    return [b - a for a, b in zip(g, g[1:])]


def duplicate_gaps(class_rows_multi, draws=S.DRAWS):
    """13.10 [M2] for one class (one generator): groups = keys carried by >= 2 texts, in order of first row index;
    observed = gaps between consecutive sorted row indexes; null = per draw, for every group, rng.sample of as many
    row indexes of the class's multi-sign texts, sorted, gaps; null gaps pooled over all draws and groups."""
    rng = S.new_rng()
    groups = collections.OrderedDict()
    for r in sorted(class_rows_multi, key=lambda x: x.index):
        groups.setdefault(r.key, []).append(r.index)
    dup = [v for v in groups.values() if len(v) >= 2]
    allidx = sorted(r.index for r in class_rows_multi)
    obs = [x for v in dup for x in gaps(v)]
    null = []
    for _ in range(draws):
        for v in dup:
            null.extend(gaps(rng.sample(allidx, len(v))))
    return {"repeated_keys": len(dup), "repeat_pairs": len(obs), "median_gap_observed": statistics.median(obs),
            "median_gap_null": statistics.median(null), "share_gap_le2_observed": 100.0 * sum(g <= 2 for g in obs) / len(obs),
            "share_gap_le2_null": 100.0 * sum(g <= 2 for g in null) / len(null)}


def collapse(rows):
    """13.10 [M3]: over all analyzable rows; within each (type, key) group in row-index order a run starts at a row and
    takes every later row within 2 of that FIRST row; each run keeps its first row."""
    groups = collections.OrderedDict()
    for r in sorted((x for x in rows if x.analyzable), key=lambda x: x.index):
        groups.setdefault((r.type, r.key), []).append(r)
    kept, dropped = [], 0
    for g in groups.values():
        first = g[0]
        kept.append(first)
        for r in g[1:]:
            if r.index - first.index <= 2:
                dropped += 1
            else:
                first = r
                kept.append(r)
    return sorted(kept, key=lambda x: x.index), dropped


def duplicate_provenance(rows, pop):
    out = {"M2": {}}
    for cls in (M.TAB, M.SEAL):
        out["M2"][cls] = duplicate_gaps(M.whole_text_rows(rows, cls, pop))
    kept, dropped = collapse(rows)
    out["M3_rows_collapsed"] = dropped
    for label, rs in (("original", rows), ("collapsed", kept)):
        t, s = M.whole_text_rows(rs, M.TAB, pop), M.whole_text_rows(rs, M.SEAL, pop)
        ct, cs = M.coverage([r.key for r in t]), M.coverage([r.key for r in s])
        out["M3_" + label] = {"TAB:I_cov10": ct, "TAB:I_N": len(t), "SEAL:S_cov10": cs, "SEAL:S_N": len(s),
                              "gap": ct - cs}
    sweep, cells = [], []
    for n in (5, 10, 20):
        for site in (None, HARAPPA):
            t = [r.key for r in M.whole_text_rows(kept, M.TAB, pop) if site is None or r.site == site]
            s = [r.key for r in M.whole_text_rows(kept, M.SEAL, pop) if site is None or r.site == site]
            if len(t) >= 30 and len(s) >= 30:
                sweep.append(M.coverage(t, n) - M.coverage(s, n))
                cells.append({"top_n": n, "sites": "all" if site is None else site, "n_tablet": len(t),
                              "n_seal": len(s), "gap": sweep[-1]})
    out["M3_sweep"] = {"cells": len(sweep), "positive": sum(1 for g in sweep if g > 0), "min": min(sweep),
                       "cells_detail": cells}                    # every cell with its gap (spec 12 D2(j))
    return out


# ----------------------------------------------------------------------------------------------------- 13.11
def units_of(tab_rows, seal_rows):
    """13.11: units = each class's own find-spots; both classes' units in one list ordered by first row index."""
    u = [rows for rows in M.clusters(tab_rows)] + [rows for rows in M.clusters(seal_rows)]
    return sorted(u, key=lambda g: g[0].index)


def assign_units(units_in_order, n_tab):
    """13.11: units taken in order into pseudo-TAB:I while it holds fewer texts than n_tab; the rest pseudo-SEAL:S."""
    pt, ps = [], []
    for u in units_in_order:
        if len(pt) < n_tab:
            pt.extend(u)
        else:
            ps.extend(u)
    return pt, ps


def perm_p_ge(n_at_or_above, perms):
    return (1 + n_at_or_above) / (1 + perms)


def label_null(rows, pop, perms=PERMS):
    cov = M.MEASURES["cov10"]
    tab, seal = M.whole_text_rows(rows, M.TAB, pop), M.whole_text_rows(rows, M.SEAL, pop)
    obs = cov(tab) - cov(seal)
    rng = S.new_rng()
    units = units_of(tab, seal)
    null = []
    for _ in range(perms):
        copy = list(units)
        rng.shuffle(copy)
        pt, ps = assign_units(copy, len(tab))
        null.append(cov(pt) - cov(ps))
    ge = sum(1 for g in null if g >= obs)
    out = {"observed": obs, "units": len(units), "cluster": {"null_mean": sum(null) / perms, "null_max": max(null),
           "n_ge_observed": ge, "p": perm_p_ge(ge, perms)}}
    rng2 = S.new_rng()                                     # text-level version (script 17), own generator
    pool = sorted(tab, key=lambda x: x.index) + sorted(seal, key=lambda x: x.index)
    null2 = []
    for _ in range(perms):
        rng2.shuffle(pool)
        null2.append(cov(pool[:len(tab)]) - cov(pool[len(tab):]))
    ge2 = sum(1 for g in null2 if g >= obs)
    out["text_level"] = {"null_mean": sum(null2) / perms, "null_max": max(null2), "n_ge_observed": ge2,
                         "p": perm_p_ge(ge2, perms)}
    return out


# ----------------------------------------------------------------------------------------------------- 13.12
def positive_control(rows, pop):
    """13.12 (script 17-H3), one generator: ten templates; class A = 40% templates; class B none; keys as section 7."""
    rng = S.new_rng()
    vocab, weights = M.sign_weights(rows)
    len_tab = [r.n_legible for r in M.whole_text_rows(rows, M.TAB, pop)]
    len_seal = [r.n_legible for r in M.whole_text_rows(rows, M.SEAL, pop)]
    templates = [tuple(rng.choices(vocab, weights=weights, k=rng.choice(len_tab))) for _ in range(10)]
    a = []
    for _ in range(len(len_tab)):
        if rng.random() < 0.40:
            a.append(rng.choice(templates))
        else:
            a.append(tuple(rng.choices(vocab, weights=weights, k=rng.choices(len_tab, k=1)[0])))
    b = [tuple(rng.choices(vocab, weights=weights, k=rng.choices(len_seal, k=1)[0])) for _ in range(len(len_seal))]
    ka, kb = [("", (x,), "") for x in a], [("", (x,), "") for x in b]
    return {"A_cov10": M.coverage(ka), "B_cov10": M.coverage(kb), "gap": M.coverage(ka) - M.coverage(kb)}


# ----------------------------------------------------------------------------------------------------- 13.13
def learn_rules(train_tab, train_seal):
    tset, sset = {r.key for r in train_tab}, {r.key for r in train_seal}
    fin = collections.Counter(r.final_sign for r in train_seal if r.final_eligible)
    marker = sorted(fin.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    med = sorted(r.n_legible for r in train_tab)[len(train_tab) // 2]
    return tset, sset, marker, med


def predict_tablet(r, rules):
    """13.13: (1) tablet if its key is among training tablets and not seals; (2) seal if the reverse; (3) else seal if
    its eligible reading-final sign is the marker; (4) else tablet if its legible length <= the median, else seal."""
    tset, sset, marker, med = rules
    in_t, in_s = r.key in tset, r.key in sset
    if in_t and not in_s:
        return True
    if in_s and not in_t:
        return False
    if r.final_eligible and r.final_sign == marker:
        return False
    return r.n_legible <= med


def class_prediction(rows, pop, draws=S.DRAWS):
    tab, seal = M.whole_text_rows(rows, M.TAB, pop), M.whole_text_rows(rows, M.SEAL, pop)
    canon = {M.TAB: M.groups_of(tab, "G3"), M.SEAL: M.groups_of(seal, "G3")}
    rng = S.new_rng()
    acc, bal, trec, srec = [], [], [], []
    for _ in range(draws):
        folds = {}
        for cls, rs in ((M.TAB, tab), (M.SEAL, seal)):
            copy = list(canon[cls])
            rng.shuffle(copy)
            folds[cls] = M.fold_split(copy, len(rs))
        rules = learn_rules(folds[M.TAB][0], folds[M.SEAL][0])
        tt, st = folds[M.TAB][1], folds[M.SEAL][1]
        tp = sum(1 for r in tt if predict_tablet(r, rules))
        tn = sum(1 for r in st if not predict_tablet(r, rules))
        trec.append(tp / len(tt))
        srec.append(tn / len(st))
        acc.append((tp + tn) / (len(tt) + len(st)))
        bal.append(0.5 * (tp / len(tt) + tn / len(st)))

    def avg(v):
        return 100.0 * sum(v) / len(v)
    return {"accuracy": avg(acc), "majority_baseline": 100.0 * max(len(tab), len(seal)) / (len(tab) + len(seal)),
            "balanced_accuracy": avg(bal), "tablet_recall": avg(trec), "seal_recall": avg(srec)}
