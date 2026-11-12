"""Part 3b of the shared library: spec section 13 entries 13.3 (tablet templates, script 06), 13.4 (the registered slot
null, `submission/PREREG_R2-2_slot_null.md`, and script 09-G5's independence expectation), 13.7's remaining parts
(script 07 A, C, D, E) and 13.8 (geography, script 08; script 09-G4 in the appendix). Builds on spec_lib and
spec_lib_measures. Standard library; Python 3.11. Readings: SPEC_READINGS.md.
"""
import collections
import math
import random

import spec_lib as S
import spec_lib_measures as M

SLOT = ("032", "033", "034")
SLOT_SET = frozenset(SLOT)
SLOT_DRAWS = 10000                                                # registered B
CORE = {"Mohenjo-daro", "Harappa"}                                # script 08 (= script 09)
FOREIGN = {"Ur", "Kish", "Susa", "Nippur", "Tello", "Girsu", "Tell Umma", "Failaka", "Karzakan", "Qala'at al-Bahrain",
           "Saar", "Janabiyah", "Hajar", "Ra's al-Junayz", "Salut", "Kalba", "Altyn Depe", "Gonur Depe",
           "Shortughai", "Tepe Yahya", "Luristan", "Pirak"}
N_MIN = 30                                                        # script 08; the one site bar (13.8)


def ranked(counter, k):
    """A ranked list of SIGNS (13 general rule): (count descending, code ascending), first k."""
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def tier(site):
    return "core" if site in CORE else ("foreign" if site in FOREIGN else "regional")


# ------------------------------------------------------------------------------------------------------ 13.3
def tablet_templates(rows, pop):
    tab = M.class_rows(rows, M.TAB, pop)
    multi = [r for r in tab if r.n_legible >= 2]
    lp = collections.Counter(r.n_legible for r in tab)
    out = {"A_length_profile": {str(n): {"texts": c, "pct": 100.0 * c / len(tab)} for n, c in sorted(lp.items())}}
    el = [r for r in multi if r.final_eligible]
    term = collections.Counter(r.final_sign for r in el)
    b = []
    for t, ct in ranked(term, 4):
        pre = collections.Counter()
        for r in el:
            line = r.reading_lines[0]
            if r.final_sign == t and len(line) >= 2 and S.legible(line[-2]):      # adjacent, same run
                pre[line[-2]] += 1
        top5 = ranked(pre, 5)
        b.append({"terminal": t, "texts": ct, "pct_of_eligible": 100.0 * ct / len(el),
                  "preceders_top5": [[s, n] for s, n in top5], "top5_cover_pct": 100.0 * sum(n for _, n in top5) / ct})
    out["B_terminals"] = {"eligible_multisign": len(el), "top4": b}
    out["C_slot"] = slot_description(rows, pop)
    keys = collections.Counter(r.key for r in multi)
    shared = {k: n for k, n in keys.items() if n >= 2}
    cum, curve = 0, []
    for k, n in M.top_keys([r.key for r in multi]):
        cum += n
        curve.append([S.serialize(k), n, 100.0 * cum / len(multi)])
    out["D_templates"] = {"multisign_texts": len(multi), "distinct_keys": len(keys), "keys_shared": len(shared),
                          "texts_on_shared_keys": sum(shared.values()),
                          "repeat_share": M.repeat_share([r.key for r in multi]), "top10_cumulative": curve}
    out["E_productivity"] = {}
    for cls in (M.TAB, M.SEAL):
        ks = [r.key for r in M.whole_text_rows(rows, cls, pop)]
        out["E_productivity"][cls] = {"N": len(ks), "cov10": M.coverage(ks) if ks else None,
                                      "once_pct": 100.0 - M.repeat_share(ks) if ks else None}
    return out


def slot_description(rows, pop):
    """13.3 [C]: members present per text (13.4 populations: all analyzable TAB:I texts of the population); position
    when present (complete single-line texts; legible signs in reading order); the 4 most frequent signs immediately
    after a member (pairs inside runs); texts that are exactly a member then 700 (multi-sign texts)."""
    tab = M.class_rows(rows, M.TAB, pop)
    present = collections.Counter(len(SLOT_SET & set(r.legible_reading)) for r in tab)
    pos = collections.Counter()
    # position: complete single-line texts; "complete" is selected FIRST so the copy rule comes after it (spec 12
    # D2(c)); under D0 these are the same rows in the same order as filtering `tab`
    for r in M.class_rows(rows, M.TAB, "complete"):
        if r.single_line:
            seq = r.legible_reading
            for i, x in enumerate(seq):
                if x in SLOT_SET:
                    pos["initial" if i == 0 else ("terminal" if i == len(seq) - 1 else "medial")] += 1
    rc = collections.Counter()
    for r in tab:
        for run in (r.runs or []):
            for i in range(len(run) - 1):
                if run[i] in SLOT_SET:
                    rc[run[i + 1]] += 1
    multi = [r for r in tab if r.n_legible >= 2]
    fam = sum(1 for r in multi if r.key[1] in tuple(((m, "700"),) for m in SLOT))
    return {"members_present": {str(k): v for k, v in sorted(present.items())},
            "position_when_present": dict(sorted(pos.items())),
            "right_neighbours_top4": [[s, n] for s, n in ranked(rc, 4)],
            "pct_followed_by_700": 100.0 * rc["700"] / sum(rc.values()) if rc else None,
            "family_member_then_700": fam, "family_pct_of_multisign": 100.0 * fam / len(multi)}


# ------------------------------------------------------------------------------------------------------ 13.4
def slot_sequences(rows, cls, pop):
    """13.4: positions = a text's legible signs in reading order, lines joined in reading order; all analyzable texts
    of the class in the population (the registration's population)."""
    return [r.legible_reading for r in M.class_rows(rows, cls, pop)]


def slot_T(seqs):
    """Registered statistic: texts containing at least two DISTINCT members of {032, 033, 034}."""
    return sum(1 for q in seqs if len(SLOT_SET & set(q)) >= 2)


def independence_expectation(seqs):
    """13.4 beside it: script 09-G5: E = n_032 n_033 / N + n_032 n_034 / N + n_033 n_034 / N."""
    n = {x: sum(1 for q in seqs if x in q) for x in SLOT}
    N = len(seqs)
    return n["032"] * n["033"] / N + n["032"] * n["034"] / N + n["033"] * n["034"] / N


def by_length(seqs):
    g = collections.defaultdict(list)
    for q in seqs:
        g[len(q)].append(q)
    return g


def exact_ET(seqs):
    """Registered cross-check: exact E[T] under N1 (each position uniform over its (length, position) column)."""
    e = 0.0
    for L, texts in by_length(seqs).items():
        if L < 2:
            continue
        n = len(texts)
        q = [collections.Counter(t[p] for t in texts) for p in range(L)]
        Q = [sum(q[p][s] for s in SLOT) / n for p in range(L)]
        none = math.prod(1 - Q[p] for p in range(L))
        at_most_one = none + sum(math.prod(1 - Q[p] + q[p][s] / n for p in range(L)) - none for s in SLOT)
        e += n * (1 - at_most_one)
    return e


def slot_null(seqs, draws=SLOT_DRAWS):
    """Registered null N1: for each length L >= 2 (sorted), each position column permuted independently across the
    texts of that length, columns in sorted (L, p) order; length-1 texts carried unchanged; B draws, Random(42);
    p = (1 + #{T_null <= T_obs}) / (1 + B); the Monte Carlo mean must agree with the exact E[T] within 3 standard
    errors, else the run stops (registration)."""
    rng = S.new_rng()
    t_obs = slot_T(seqs)
    groups = by_length(seqs)
    cols = {L: [[t[p] for t in groups[L]] for p in range(L)] for L in sorted(groups) if L >= 2}
    ts = []
    for _ in range(draws):
        t = 0
        for L in sorted(cols):
            for col in cols[L]:
                rng.shuffle(col)
            for i in range(len(groups[L])):
                if len(SLOT_SET & {col[i] for col in cols[L]}) >= 2:
                    t += 1
        ts.append(t)
    mean = sum(ts) / draws
    sd = math.sqrt(sum((x - mean) ** 2 for x in ts) / (draws - 1))
    se = sd / math.sqrt(draws)
    e = exact_ET(seqs)
    if abs(mean - e) > 3 * se:
        raise RuntimeError("registration: Monte Carlo mean %.4f differs from exact E[T] %.4f by more than 3 se (%.4f);"
                           " nothing is reported until the cause is found" % (mean, e, se))
    p = perm_p(sum(1 for x in ts if x <= t_obs), draws)
    return {"T_obs": t_obs, "E_exact": e, "mc_mean": mean, "mc_se": se, "p": p, "draws": draws}


def perm_p(n_at_or_below, draws):
    """Registered: p = (1 + #{T_null <= T_obs}) / (1 + B)."""
    return (1 + n_at_or_below) / (1 + draws)


def slot_test(rows, pop, draws=SLOT_DRAWS):
    tab, seal = slot_sequences(rows, M.TAB, pop), slot_sequences(rows, M.SEAL, pop)
    t, s = slot_null(tab, draws), slot_null(seal, draws)
    t["outcome"] = "A" if t["p"] <= 0.01 else "B"
    t["independence_expectation_G5"] = independence_expectation(tab)
    s["exclusivity_beyond_position"] = s["p"] <= 0.01
    return {"TAB:I": t, "SEAL:S_control": s}


# ------------------------------------------------------------------------------------------------- 13.7 (07)
def seal_frame(rows, pop):
    seal = M.whole_text_rows(rows, M.SEAL, pop)
    # [07-A] over ALL analyzable SEAL:S texts (spec section 12, deviation D1, approved 6 Nov 2026), as script 07 and
    # as 13.3 [A] for tablets; the other parts of 13.7 stay on multi-sign texts.
    all_seal = M.class_rows(rows, M.SEAL, pop)
    lp = collections.Counter(r.n_legible for r in all_seal)
    out = {"A_length_profile": {str(n): c for n, c in sorted(lp.items())},
           "A_mean_legible_length": sum(r.n_legible for r in all_seal) / len(all_seal)}
    el = [r for r in seal if r.final_eligible]
    c = []
    for t, ct in ranked(collections.Counter(r.final_sign for r in el), 3):
        stems = collections.Counter(r.key[1][0][:-1] for r in el if r.final_sign == t)
        c.append({"terminal": t, "texts": ct, "pct_of_eligible": 100.0 * ct / len(el),
                  "distinct_stems_pct": 100.0 * len(stems) / ct,
                  "stems_once_pct": 100.0 * sum(1 for v in stems.values() if v == 1) / ct, "distinct_stems": len(stems)})
    out["C_terminals"] = {"eligible": len(el), "top3": c}
    ini = [r for r in seal if r.initial_eligible]
    top5 = ranked(collections.Counter(r.initial_sign for r in ini), 5)
    out["D_openers"] = {"eligible": len(ini), "top5": [[s, n] for s, n in top5],
                        "top5_pct": 100.0 * sum(n for _, n in top5) / len(ini) if ini else None}
    out["E_reuse"] = {}
    for cls in (M.SEAL, M.TAB):
        multi = M.whole_text_rows(rows, cls, pop)
        both = [r for r in multi if r.initial_eligible and r.final_eligible]
        frames = [(r.initial_sign, r.final_sign) for r in both]
        out["E_reuse"][cls] = {"whole_text_cov10": M.coverage([r.key for r in multi]) if multi else None,
                               "frame_texts": len(both),
                               "frame_cov10": M.coverage(frames, ser=lambda f: f[0] + "|" + f[1]) if frames else None}
    return out


# ------------------------------------------------------------------------------------------------------ 13.8
def rate(texts):
    hits = sum(1 for r in texts if r.final_sign == "740")
    return {"N": len(texts), "hits": hits, "rate": 100.0 * hits / len(texts) if texts else None}


def geography(rows, pop):
    seal = M.whole_text_rows(rows, M.SEAL, pop)
    el = [r for r in seal if r.final_eligible]
    by_site = collections.defaultdict(list)
    for r in el:
        by_site[r.site].append(r)
    sites = {s: rate(v) for s, v in by_site.items() if len(v) >= N_MIN}
    tiers = {t: rate([r for r in el if tier(r.site) == t]) for t in ("core", "regional", "foreign")}
    foreign = {}
    for r in seal:
        if tier(r.site) == "foreign":
            f = foreign.setdefault(r.site, {"multisign": 0, "eligible": 0, "end_740": 0})
            f["multisign"] += 1
            if r.final_eligible:
                f["eligible"] += 1
                f["end_740"] += r.final_sign == "740"
    return {"sites_rate_740": dict(sorted(sites.items())), "adequately_sampled_sites": len(sites),
            "distinct_sites_with_SEAL:S": distinct_seal_sites(rows),
            "tiers": tiers, "foreign_itemised": dict(sorted(foreign.items())), "appendix_G4": gradient(el)}


def distinct_seal_sites(rows):
    """13.8 + spec 12 D2(a): a corpus description, so over ALL analyzable SEAL:S texts in both population blocks."""
    return len({r.site for r in rows if r.analyzable and r.type == M.SEAL})


def site_shares(rows):
    """13.8: TAB:I and SEAL:S, all analyzable texts: the 5 sites with most texts and the Harappa share."""
    out = {}
    for cls in (M.TAB, M.SEAL):
        texts = M.class_rows(rows, cls, "all")
        c = collections.Counter(r.site for r in texts)
        top = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        out[cls] = {"N": len(texts), "top5": [[s, n, 100.0 * n / len(texts)] for s, n in top],
                    "harappa_pct": 100.0 * c.get("Harappa", 0) / len(texts)}
    return out


def ztest(k1, n1, k2, n2):
    """Script 09: two-proportion z test with the pooled standard error; two-sided p via erf."""
    p1, p2, pp = k1 / n1, k2 / n2, (k1 + k2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    return z, 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def gradient(el):
    """13.8 appendix (09-G4a/b) on eligible multi-sign seals: core against regional with the z test; rates at legible
    lengths 2-6; mean legible length by tier (of the same eligible texts: SPEC_READINGS no. 15); core against regional
    at lengths 3, 4, 5."""
    core = [r for r in el if tier(r.site) == "core"]
    reg = [r for r in el if tier(r.site) == "regional"]
    kc, kr = rate(core)["hits"], rate(reg)["hits"]
    z, p = ztest(kc, len(core), kr, len(reg)) if core and reg else (None, None)

    def mean_len(x):
        return sum(r.n_legible for r in x) / len(x) if x else None
    return {"G4a": {"core": rate(core), "regional": rate(reg), "z": z, "p": p},
            "G4b_by_length": {str(n): rate([r for r in el if r.n_legible == n]) for n in (2, 3, 4, 5, 6)},
            "G4b_mean_length": {"core": mean_len(core), "regional": mean_len(reg)},
            "G4b_matched": {str(n): {"core": rate([r for r in core if r.n_legible == n]),
                                     "regional": rate([r for r in reg if r.n_legible == n])} for n in (3, 4, 5)}}
