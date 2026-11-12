"""Part 2 of the shared library: populations (spec 3), measures (7), first/last (5), published-work protocols (8),
the seal measures of 13.7 and B' (Amendment 1). Builds only on spec_lib (part 1). Standard library; Python 3.11.
Every reported quantity creates its OWN generator `random.Random(SEED)` (spec 0); a draw over both classes handles
TAB:I first, then SEAL:S, in that generator. Readings of the text: SPEC_READINGS.md.
"""
import collections
import contextlib
import hashlib
import json
import math
import random
import statistics

import spec_lib as S

TAB, SEAL = "TAB:I", "SEAL:S"
LN2 = math.log(2)


# ------------------------------------------------------------------------------ copy rule (spec 6; 12 D2(c), (d))
COPY_RULE = "D0"


@contextlib.contextmanager
def copy_rule(variant):
    """Run the measures under one copy rule (D0 every copy; D1 Fuls; D2a, D2b); always restored to the outer rule."""
    global COPY_RULE
    if variant not in ("D0", "D1", "D2a", "D2b"):
        raise ValueError(variant)
    old, COPY_RULE = COPY_RULE, variant
    try:
        yield
    finally:
        COPY_RULE = old


def apply_copy_rule(rows):
    """One copy per key under the current rule (copy kept = smallest row index); D0 returns the list unchanged."""
    return rows if COPY_RULE == "D0" else S.dedupe(rows, COPY_RULE)


# --------------------------------------------------------------------------------------------- populations (3)
def class_rows(rows, cls, pop, min_legible=0, types=None, copy=True):
    """Analyzable rows of one class (or a set of types) in row-index order. pop 'complete' (complete = Y) or 'all'.
    The copy rule is applied LAST, after the population, class and length filters (spec 6-7 order); copy=False
    leaves it to a caller with further population filters of its own (B')."""
    types = types or (cls,)
    out = [r for r in rows if r.analyzable and r.type in types and r.n_legible >= min_legible]
    if pop == "complete":
        out = [r for r in out if r.complete]
    elif pop != "all":
        raise ValueError(pop)
    return apply_copy_rule(out) if copy else out


def whole_text_rows(rows, cls, pop, copy=True):
    """Spec 3: whole-text measures use texts with at least 2 legible signs."""
    return class_rows(rows, cls, pop, min_legible=2, copy=copy)


def entropy_rows(rows, cls, pop):
    """Spec 1, 3, 4: pair/triple/entropy population = the class's texts in the population, BUS rows without '/'
    excluded (no length rule: SPEC_READINGS no. 6)."""
    return [r for r in class_rows(rows, cls, pop) if r.runs is not None]


# ------------------------------------------------------------------------------------------ whole-text measures (7)
def top_keys(keys, k=10, ser=S.serialize):
    """Spec 7: count texts per key; order keys by (count descending, serialization ascending); first min(k, n keys)."""
    c = collections.Counter(keys)
    order = sorted(c.items(), key=lambda kv: (-kv[1], ser(kv[0])))
    return order[:min(k, len(order))]


def coverage(keys, k=10, ser=S.serialize):
    """Spec 7: 100 x (sum of the top-k keys' counts) / (number of texts)."""
    return 100.0 * sum(n for _, n in top_keys(keys, k, ser)) / len(keys)


def repeat_share(keys):
    """Spec 7: 100 x (texts whose key occurs at least twice in the class) / (number of texts)."""
    c = collections.Counter(keys)
    return 100.0 * sum(1 for x in keys if c[x] >= 2) / len(keys)


MEASURES = {"cov10": lambda rows: coverage([r.key for r in rows]),
            "repeat_share": lambda rows: repeat_share([r.key for r in rows])}


class Fingerprint:
    """Spec 0 draw fingerprint: SHA-256 of the drawn index lists, in draw order (our own format; JSON of lists)."""
    def __init__(self):
        self.draws = []

    def add(self, label, items):
        self.draws.append([label, [r.index if hasattr(r, "index") else r for r in items]])

    def hexdigest(self):
        return hashlib.sha256(json.dumps(self.draws, separators=(",", ":")).encode("ascii")).hexdigest()


def summary(values):
    g = sorted(values)
    return {"mean": sum(g) / len(g), "p5": S.pctl(g, 0.05), "p95": S.pctl(g, 0.95)}


def matched_n(tab_rows, seal_rows, measure, draws=S.DRAWS, return_diffs=False):
    """Spec 7 matched-N robustness summary: n = smaller class size; the smaller class used whole; in each draw the
    larger class is subsampled with rng.sample(rows, n); difference = TAB:I - SEAL:S. NOT a significance test.
    return_diffs: also return the per-draw differences (B' frac>0, spec 12 D2(g))."""
    rng, fp = S.new_rng(), Fingerprint()
    n = min(len(tab_rows), len(seal_rows))
    diffs = []
    for _ in range(draws):
        t = rng.sample(tab_rows, n) if len(tab_rows) > n else tab_rows
        s = rng.sample(seal_rows, n) if len(seal_rows) > n else seal_rows
        fp.add("t", t if len(tab_rows) > n else [])
        fp.add("s", s if len(seal_rows) > n else [])
        diffs.append(measure(t) - measure(s))
    out = summary(diffs)
    out.update({"n": n, "fingerprint": fp.hexdigest()})
    if return_diffs:
        out["diffs"] = diffs
    return out


def clusters(rows):
    """Spec 7: a class's clusters = its D2a find-spots ordered by first row index; rows in row-index order."""
    groups = collections.OrderedDict()
    for r in sorted(rows, key=lambda x: x.index):
        groups.setdefault(r.findspot, []).append(r)
    return list(groups.values())


def concat(chosen):
    """Spec 7: resampled rows = the chosen clusters' rows in the order drawn (a cluster drawn twice appears twice)."""
    return [r for c in chosen for r in c]


def findspot_interval(tab_rows, seal_rows, measure, draws=S.DRAWS):
    """Spec 7 find-spot resampling sensitivity interval (NOT a confidence interval)."""
    rng, fp = S.new_rng(), Fingerprint()
    ct, cs = clusters(tab_rows), clusters(seal_rows)
    diffs, discarded = [], 0
    while len(diffs) < draws:
        t = concat(rng.choices(ct, k=len(ct)))
        s = concat(rng.choices(cs, k=len(cs)))
        if len(t) < 2 or len(s) < 2:
            discarded += 1
            continue
        n = min(len(t), len(s))
        if len(t) > n:
            t = rng.sample(t, n)
        if len(s) > n:
            s = rng.sample(s, n)
        fp.add("t", t)
        fp.add("s", s)
        diffs.append(measure(t) - measure(s))
    g = sorted(diffs)
    return {"p5": S.pctl(g, 0.05), "p95": S.pctl(g, 0.95), "draws_discarded": discarded, "fingerprint": fp.hexdigest()}


# ---------------------------------------------------------------------------------------------------- entropy (7)
def trigram_counts(run_lists):
    """Trigram and context counts over runs (spec 4: pairs/triples only inside runs)."""
    tri, ctx = collections.Counter(), collections.Counter()
    for run in run_lists:
        for i in range(len(run) - 2):
            tri[tuple(run[i:i + 3])] += 1
            ctx[tuple(run[i:i + 2])] += 1
    return tri, ctx


def h3(run_lists):
    """Spec 7: N = trigram tokens; H3 = - sum_t (c(t)/N) log2(c(t)/c(x)); Miller-Madow exactly
    mm = h3 + (k_tri - k_ctx) / (2.0 * n * math.log(2)); N = 0 -> NA. K_tri/N in percent (SPEC_READINGS no. 7)."""
    tri, ctx = trigram_counts(run_lists)
    n = sum(tri.values())
    if n == 0:
        return {"plugin": None, "mm": None, "n_tri": 0, "k_tri": 0, "k_ctx": 0, "ktri_over_n": None}
    h = -sum((c / n) * math.log2(c / ctx[t[:2]]) for t, c in tri.items())
    k_tri, k_ctx = len(tri), len(ctx)
    return {"plugin": h, "mm": h + (k_tri - k_ctx) / (2.0 * n * math.log(2)), "n_tri": n, "k_tri": k_tri,
            "k_ctx": k_ctx, "ktri_over_n": 100.0 * k_tri / n}


def runs_of(rows):
    return [run for r in rows for run in r.runs]


def text_tokens(r):
    return sum(max(0, len(run) - 2) for run in r.runs)


def take_until(rows_in_order, target):
    """Spec 7: texts taken in order until their cumulative trigram tokens are at least T (the crossing text kept)."""
    taken, tot = [], 0
    for r in rows_in_order:
        if tot >= target:
            break
        taken.append(r)
        tot += text_tokens(r)
    return taken, tot


def entropy_matched(tab_rows, seal_rows, draws=S.DRAWS):
    """Spec 7 entropy comparison at matched trigram tokens; difference = SEAL:S - TAB:I (plug-in primary, MM beside)."""
    rng, fp = S.new_rng(), Fingerprint()
    ht, hs = h3(runs_of(tab_rows)), h3(runs_of(seal_rows))
    if ht["n_tri"] <= hs["n_tri"]:
        fixed, T, fixed_h, other = TAB, ht["n_tri"], ht, seal_rows
    else:
        fixed, T, fixed_h, other = SEAL, hs["n_tri"], hs, tab_rows
    pl, mm, achieved = [], [], []
    for _ in range(draws):
        order = sorted(other, key=lambda x: x.index)       # a row-index-ordered copy
        rng.shuffle(order)
        taken, tot = take_until(order, T)
        fp.add("o", taken)
        h = h3(runs_of(taken))
        if fixed == TAB:
            pl.append(h["plugin"] - fixed_h["plugin"])
            mm.append(h["mm"] - fixed_h["mm"])
        else:
            pl.append(fixed_h["plugin"] - h["plugin"])
            mm.append(fixed_h["mm"] - h["mm"])
        achieved.append(tot)
    a, b = summary(pl), summary(mm)
    return {"fixed_class": fixed, "T": T, "plugin_diff_mean": a["mean"], "plugin_diff_p5": a["p5"],
            "plugin_diff_p95": a["p95"], "mm_diff_mean": b["mean"], "mm_diff_p5": b["p5"], "mm_diff_p95": b["p95"],
            "mean_achieved_tokens": sum(achieved) / len(achieved), "fingerprint": fp.hexdigest()}


# ---------------------------------------------------------------------------------------------------- hold-out (7)
def group_key(r, grouping):
    if grouping == "G3":
        return r.findspot
    if grouping == "G1":
        return ("text", r.index)
    if grouping == "G2":
        return ("object", r.object_id)
    raise ValueError(grouping)


def groups_of(rows, grouping):
    """Spec 7: groups listed in order of first row index; rows inside in row-index order."""
    g = collections.OrderedDict()
    for r in sorted(rows, key=lambda x: x.index):
        g.setdefault(group_key(r, grouping), []).append(r)
    return list(g.values())


def fold_split(groups_in_order, n_texts):
    """Spec 7: groups taken in order into fold 1 while len(fold1) < len(texts) / 2; the rest into fold 2."""
    f1, f2 = [], []
    for grp in groups_in_order:
        if len(f1) < n_texts / 2:
            f1.extend(grp)
        else:
            f2.extend(grp)
    return f1, f2


def holdout(tab_rows, seal_rows, grouping, draws=S.DRAWS):
    rng, fp = S.new_rng(), Fingerprint()
    res = {TAB: {"in": [], "out": [], "ret": []}, SEAL: {"in": [], "out": [], "ret": []}}
    canon = {TAB: groups_of(tab_rows, grouping), SEAL: groups_of(seal_rows, grouping)}
    sizes = {TAB: len(tab_rows), SEAL: len(seal_rows)}
    for _ in range(draws):
        for cls in (TAB, SEAL):
            copy = list(canon[cls])                          # a FRESH copy each draw
            rng.shuffle(copy)
            f1, f2 = fold_split(copy, sizes[cls])
            fp.add(cls, f1)
            top = {k for k, _ in top_keys([r.key for r in f1])}
            cin = coverage([r.key for r in f1])
            cout = 100.0 * sum(1 for r in f2 if r.key in top) / len(f2)
            res[cls]["in"].append(cin)
            res[cls]["out"].append(cout)
            res[cls]["ret"].append(0.0 if cin == 0 else 100.0 * cout / cin)
    out = {}
    for cls in (TAB, SEAL):
        o, t, i = summary(res[cls]["out"]), summary(res[cls]["ret"]), summary(res[cls]["in"])
        out[cls] = {"in_mean": sum(res[cls]["in"]) / draws, "in_p5": i["p5"], "in_p95": i["p95"],
                    "out_mean": o["mean"], "out_p5": o["p5"],
                    "out_p95": o["p95"], "retained_mean": t["mean"], "retained_p5": t["p5"],
                    "retained_p95": t["p95"]}
    out["fingerprint"] = fp.hexdigest()
    return out


# ------------------------------------------------------------------------------------- synthetic negative control (7)
def sign_weights(rows):
    """Spec 7: sign frequencies = all legible signs of all analyzable rows of all classes; vocabulary ascending."""
    c = collections.Counter(t for r in rows if r.analyzable for line in r.stored_lines for t in line if S.legible(t))
    vocab = sorted(c)
    return vocab, [c[v] for v in vocab]


def synthetic_negative(all_rows, tab_rows, seal_rows, draws=S.DRAWS):
    rng = S.new_rng()
    vocab, weights = sign_weights(all_rows)
    len_t = [r.n_legible for r in tab_rows]
    len_s = [r.n_legible for r in seal_rows]
    observed = coverage([r.key for r in tab_rows]) - coverage([r.key for r in seal_rows])
    gaps = []
    for _ in range(draws):
        ct = coverage([("", (tuple(rng.choices(vocab, weights, k=n)),), "") for n in len_t])
        cs = coverage([("", (tuple(rng.choices(vocab, weights, k=n)),), "") for n in len_s])
        gaps.append(ct - cs)
    return {"observed_gap": observed, "mean_gap": sum(gaps) / len(gaps), "max_abs_gap": max(abs(g) for g in gaps)}


# ------------------------------------------------------------------------------------------------ object rows (3)
def object_rows(rows):
    """Spec 3: (a) share of OBJECTS carrying at least one of the class's top-10 keys (learned on the side-level
    population); (b) whole-object identity: object key over the sides in the population; coverage and repeat share
    with objects as the units (SPEC_READINGS no. 8)."""
    top = {k for k, _ in top_keys([r.key for r in rows])}
    objs = collections.OrderedDict()
    for r in sorted(rows, key=lambda x: x.index):
        objs.setdefault(r.object_id, []).append(r)
    share = 100.0 * sum(1 for sides in objs.values() if any(r.key in top for r in sides)) / len(objs)
    okeys = [S.object_key([r.key for r in sides]) for sides in objs.values()]
    return {"a_share_objects_with_top10": share, "b": {"n_objects": len(okeys),
            "cov10": coverage(okeys, ser=lambda t: "\n".join(t)), "repeat_share": repeat_share(okeys)}}


# -------------------------------------------------------------------------------------------------- first/last (5)
def final740(rows):
    """Spec 5: eligible = single-line, stored LEFT mark '+', legible reading-final token; rate = 740 / eligible."""
    el = [r for r in rows if r.final_eligible]
    hits = sum(1 for r in el if r.final_sign == "740")
    return {"eligible": len(el), "hits": hits, "rate": (100.0 * hits / len(el)) if el else None}
