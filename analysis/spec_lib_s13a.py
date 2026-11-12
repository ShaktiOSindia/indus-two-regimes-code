"""Part 3a of the shared library: spec section 13 entries 13.1, 13.2, 13.5, 13.6, 13.14, 13.15 (each = the procedure
of the named script at tag `pre-corrections` on this specification's data layer; departures as the entry states).
Builds on spec_lib, spec_lib_measures. Standard library; Python 3.11. Readings: SPEC_READINGS.md.
"""
import collections
import math
import random

import spec_lib as S
import spec_lib_measures as M

FIVE = ("SEAL:S", "SEAL:R", "TAB:B", "TAB:I", "POT:T:g")          # Table 3 rows, script 01 / 10 order
POOLED = (("SEALS pooled", ("SEAL:S", "SEAL:R")), ("TABLETS pooled", ("TAB:B", "TAB:I")))
NULL_ITERS = {"TAB:I": 10000, "TAB:B": 10000, "SEAL:S": 2000, "SEAL:R": 2000, "POT:T:g": 2000}   # script 10
SINGLETON_DRAWS = 200                                                                              # script 10


def legible_tokens(rows):
    return [t for r in rows for line in r.stored_lines for t in line if S.legible(t)]


# ------------------------------------------------------------------------------------------------------ 13.1
def table2_metrics(rows):
    """13.1: N; top sign share; top-69 and top-82 sign coverage (legible tokens); top-82 starters and top-23 enders
    (share of section-5-eligible texts whose reading-initial / -final sign is among the k most frequent such signs);
    mean legible length."""
    c = collections.Counter(legible_tokens(rows))
    tot = sum(c.values())
    counts = sorted(c.values(), reverse=True)
    starts = collections.Counter(r.initial_sign for r in rows if r.initial_eligible)
    ends = collections.Counter(r.final_sign for r in rows if r.final_eligible)

    def topk(counter, k):
        v = sorted(counter.values(), reverse=True)
        return 100.0 * sum(v[:k]) / sum(v) if v else None
    return {"N": len(rows), "top_sign_share": 100.0 * counts[0] / tot, "top69_coverage": 100.0 * sum(counts[:69]) / tot,
            "top82_coverage": 100.0 * sum(counts[:82]) / tot, "starters_top82": topk(starts, 82),
            "enders_top23": topk(ends, 23), "eligible_starters": sum(starts.values()),
            "eligible_enders": sum(ends.values()), "mean_legible_length": sum(r.n_legible for r in rows) / len(rows)}


def m342(rows):
    """13.1 M-342 line: among multi-sign texts (all classes) with an eligible reading-final token, the share ending in
    740; its ratio to 740's share of all legible tokens of the same ELIGIBLE texts (reading 12 as revised by spec
    12 D2(e): the population of the rate)."""
    multi = [r for r in rows if r.n_legible >= 2]
    el = [r for r in multi if r.final_eligible]
    rate = 100.0 * sum(1 for r in el if r.final_sign == "740") / len(el)
    toks = legible_tokens(el)
    share = 100.0 * toks.count("740") / len(toks)
    return {"multisign_texts": len(multi), "eligible": len(el), "rate_740_final": rate, "token_share_740": share,
            "concentration": rate / share}


# ------------------------------------------------------------------------------------------------------ 13.2
def h1(rows):
    c = collections.Counter(legible_tokens(rows))
    n = sum(c.values())
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def table3(rows, pop):
    """13.2: per class (five classes, then the two pooled rows): N and mean legible length over the class's analyzable
    texts; H1 over their legible signs; H3 plug-in and Miller-Madow and K_tri/N over the entropy population (BUS rows
    without '/' excluded; SPEC_READINGS no. 13)."""
    out = {}
    for cls in FIVE:
        texts = M.class_rows(rows, cls, pop)
        h = M.h3(M.runs_of(M.entropy_rows(rows, cls, pop)))
        out[cls] = {"N": len(texts), "mean_legible_length": sum(r.n_legible for r in texts) / len(texts),
                    "H1": h1(texts), "H3": h["plugin"], "H3_mm": h["mm"], "ktri_over_n": h["ktri_over_n"]}
    for label, types in POOLED:
        texts = M.class_rows(rows, None, pop, types=types)
        ent = [r for r in texts if r.runs is not None]
        h = M.h3(M.runs_of(ent))
        out[label] = {"N": len(texts), "mean_legible_length": sum(r.n_legible for r in texts) / len(texts),
                      "H3": h["plugin"]}
    return out


def shuffled_runs(rows, rng):
    """13.2: every run of the class (runs in row-index order; within a text in reading order) is copied and the copy
    shuffled with rng.shuffle."""
    out = []
    for r in sorted(rows, key=lambda x: x.index):
        for run in r.runs:
            c = list(run)
            rng.shuffle(c)
            out.append(c)
    return out


def null_p(n_at_or_below, iters):
    """Script 10 / 13.2: p = (1 + #{null <= observed}) / (1 + iterations)."""
    return (n_at_or_below + 1) / (iters + 1)


def shuffle_null(ent_rows, iters):
    """13.2 within-class null (script 10's procedure, runs instead of whole texts): observed H3, null mean and minimum,
    p = (1 + #{null <= observed}) / (1 + iterations), reduction, and script 10's verdict rule."""
    rng = S.new_rng()
    obs = M.h3(M.runs_of(ent_rows))["plugin"]
    null = [M.h3(shuffled_runs(ent_rows, rng))["plugin"] for _ in range(iters)]
    le = sum(1 for x in null if x <= obs)
    mean = sum(null) / len(null)
    p = null_p(le, iters)
    red = 100.0 * (mean - obs) / mean if mean > 0 else 0.0           # script 10's guard for a zero mean
    return {"observed": obs, "null_mean": mean, "null_min": min(null), "p": p, "reduction_pct": red,
            "iterations": iters, "templated": p < 0.05 and red > 0}


def singleton_share(run_lists):
    """Script 10: share of trigram TOKENS whose two-sign context occurs exactly once (token-weighted)."""
    tri, ctx = M.trigram_counts(run_lists)
    n = sum(tri.values())
    return 100.0 * sum(1 for v in ctx.values() if v == 1) / n if n else None


def singleton_report(ent_rows, draws=SINGLETON_DRAWS):
    """13.2: observed singleton share and its mean over 200 shuffles of the same kind; one generator per class."""
    rng = S.new_rng()
    obs = singleton_share(M.runs_of(ent_rows))
    vals = [singleton_share(shuffled_runs(ent_rows, rng)) for _ in range(draws)]
    return {"observed": obs, "shuffled_mean": sum(vals) / len(vals)}


# ------------------------------------------------------------------------------------------------------ 13.5
def two_sign_share(tab_rows):
    """13.5: multi-sign TAB:I: of the top-10 keys, how many have exactly 2 legible signs, and how many of the texts the
    top 10 cover they account for."""
    top = M.top_keys([r.key for r in tab_rows])
    nleg = {r.key: r.n_legible for r in tab_rows}
    two = [(k, n) for k, n in top if nleg[k] == 2]
    covered = sum(n for _, n in top)
    return {"top10_two_sign_keys": len(two), "texts_two_sign": sum(n for _, n in two), "texts_top10": covered,
            "share_pct": 100.0 * sum(n for _, n in two) / covered}


# ------------------------------------------------------------------------------------------------------ 13.6
def reuse_fixed_length(rows, pop):
    """13.6 (09-G1): top-10 coverage of TAB:I and of SEAL:S among texts of legible length 2, 3, 4, 5."""
    out = {}
    for n in (2, 3, 4, 5):
        cell = {}
        for cls in (M.TAB, M.SEAL):
            sel = [r for r in M.whole_text_rows(rows, cls, pop) if r.n_legible == n]
            cell[cls] = {"N": len(sel), "cov10": M.coverage([r.key for r in sel]) if sel else None}
        out[str(n)] = cell
    return out


# ----------------------------------------------------------------------------------------------------- 13.14
def mould(rows, pop):
    """13.14 (09-MOLD): top-10 coverage of multi-sign TAB:I against TAB:B; the N of each (spec 12 D2(j))."""
    sel = {cls: M.whole_text_rows(rows, cls, pop) for cls in ("TAB:I", "TAB:B")}
    out = {cls: M.coverage([r.key for r in sel[cls]]) for cls in ("TAB:I", "TAB:B")}
    out["N"] = {cls: len(sel[cls]) for cls in ("TAB:I", "TAB:B")}
    return out


# ----------------------------------------------------------------------------------------------------- 13.15
def shared_keys(rows):
    """13.15 (09-G7): over all analyzable multi-sign texts: distinct keys carried by more than one `type`, and keys
    found in both TAB:I and SEAL:S; the same over texts of any length beside."""
    def count(sel):
        types = collections.defaultdict(set)
        for r in sel:
            types[r.key].add(r.type)
        return {"distinct_keys": len(types), "keys_with_more_than_one_type": sum(1 for v in types.values() if len(v) > 1),
                "keys_in_both_TAB:I_and_SEAL:S": sum(1 for v in types.values() if {"TAB:I", "SEAL:S"} <= v)}
    an = [r for r in rows if r.analyzable]
    # copy rule after each population filter (spec 12 D2(c)); identity under D0
    return {"multisign": count(M.apply_copy_rule([r for r in an if r.n_legible >= 2])),
            "any_length": count(M.apply_copy_rule(an))}
