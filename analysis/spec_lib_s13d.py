"""Part 3d of the shared library: spec section 13 entries 13.16 (provenance counts, script 15), 13.17 (sign-identity
sensitivity, script 19), 13.18 (Farmer-Sproat-Witzel F2 and F6, script 18) and 13.19 (the registered storage test,
`profile/fuls_2026-11-01/decision1_direction_tests.py` T1-T4 and its self-test). Builds on spec_lib and
spec_lib_measures. Standard library; Python 3.11.
"""
import collections
import math
import random
import re

import spec_lib as S
import spec_lib_measures as M

REAL_CISI = re.compile(r"[A-Za-z]+-\d+")
RATES = (0.01, 0.02, 0.05, 0.10, 0.20, 0.40)                           # script 19
FSW_CLASSES = ("TAB:I", "TAB:B", "SEAL:S", "SEAL:R", "POT:T:g")        # script 18
SLOT = frozenset(("032", "033", "034"))
DIRS = ("R/L", "L/R", "-", "NR", "T/B", "BUS", "SYM")                  # decision1_direction_tests.py
INITIAL_TYPE = frozenset(("190", "315", "853", "880"))


# ----------------------------------------------------------------------------------------------------- 13.16
def provenance(rows):
    an = [r for r in rows if r.analyzable]
    real = [r for r in rows if REAL_CISI.fullmatch(r.cisi)]
    real_an = [r for r in an if REAL_CISI.fullmatch(r.cisi)]
    h_range = [r for r in rows if re.fullmatch(r"H-(\d+)", r.cisi) and 104 <= int(r.cisi[2:]) <= 128]
    toks = [t for r in an for line in r.stored_lines for t in line]
    leg = [t for t in toks if S.legible(t)]
    objs = {r.object_id for r in an}
    by_obj = collections.defaultdict(list)
    for r in an:
        if r.type == M.TAB and r.n_legible >= 2:
            by_obj[r.object_id].append(r.key)
    multi = {o: v for o, v in by_obj.items() if len(v) > 1}
    n_multi_texts = sum(len(v) for v in multi.values())
    n_rep = sum(len(v) - len(set(v)) for v in multi.values())
    n_all = sum(len(v) for v in by_obj.values())
    return {"P2": {"real_cisi_all_rows": len(real), "all_rows": len(rows), "real_cisi_analyzable": len(real_an),
                   "analyzable": len(an), "pct_analyzable": 100.0 * len(real_an) / len(an)},
            "P4": {"rows_H104_H128": len(h_range), "rows_without_legible_sign": sum(1 for r in rows if not r.malformed
                                                                                   and r.n_legible == 0)},
            "P5": {"legible_tokens": len(leg), "distinct_legible_signs": len(set(leg)),
                   "tokens_000": toks.count("000"), "tokens_999": toks.count("999")},
            "P7": {"analyzable_texts": len(an), "icit_objects": len(objs),
                   "tab_objects_with_more_than_one_multisign_text": len(multi),
                   "tab_objects_repeating_a_key": sum(1 for v in multi.values() if len(set(v)) < len(v)),
                   "within_object_repeats": n_rep, "texts_on_multi_text_objects": n_multi_texts,
                   "multisign_tab_texts": n_all, "pct_on_multi_text_objects": 100.0 * n_multi_texts / n_all}}


# ----------------------------------------------------------------------------------------------------- 13.17
def map_key(key, f):
    """Apply f to every legible token of a key in order (000 placeholders and marks untouched)."""
    right, lines, left = key
    return (right, tuple(tuple(f(t) if S.legible(t) else t for t in line) for line in lines), left)


def merge_mapping(vocab, k, rng):
    """Script 19: k codes, each folded into a different code, corpus-wide."""
    mapping = {}
    for victim in rng.sample(vocab, k):
        target = rng.choice(vocab)
        while target == victim:
            target = rng.choice(vocab)
        mapping[victim] = target
    return mapping


def apply_merge(keys, mapping):
    return [map_key(k, lambda t: mapping.get(t, t)) for k in keys]


def apply_split(keys, victims, rng):
    """Script 19: each OCCURRENCE of a victim code independently becomes one of two codes (keys in the order given,
    tokens in reading order)."""
    return [map_key(k, lambda t: t + ("a" if rng.random() < 0.5 else "b") if t in victims else t) for k in keys]


def key_signs(key):
    return [t for line in key[1] for t in line if S.legible(t)]


def template_codes(tab_keys, vocab):
    """Script 19 hostile ordering: the signs of the top-10 tablet keys first, then the other tablet signs by frequency
    (count descending, code ascending), then the rest of the vocabulary ascending."""
    load = []
    for k, _ in M.top_keys(tab_keys):
        for s in key_signs(k):
            if s not in load:
                load.append(s)
    freq = collections.Counter(s for k in tab_keys for s in key_signs(k))
    rest = [s for s, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])) if s not in load]
    seen = set(load) | set(rest)
    ordering = load + rest + [s for s in vocab if s not in seen]
    assert len(ordering) == len(vocab), (len(ordering), len(vocab))
    return ordering, load


def parent(key):
    return map_key(key, lambda t: t[:-1] if t[-1] in "ab" and t[:-1].isdigit() else t)


def marker_stats(seqs_eligible, codes):
    term = [q[-1] for q in seqs_eligible]
    non = [s for q in seqs_eligible for s in q[:-1]]
    pt = 100.0 * sum(1 for s in term if s in codes) / len(term)
    pn = 100.0 * sum(1 for s in non if s in codes) / len(non)
    return {"terminal_pct": pt, "nonterminal_pct": pn, "enrichment": pt / pn if pn else None}


def sign_identity(rows, pop, draws=S.DRAWS):
    tab = M.whole_text_rows(rows, M.TAB, pop)
    sea = M.whole_text_rows(rows, M.SEAL, pop)
    tk, sk = [r.key for r in tab], [r.key for r in sea]
    vocab = sorted({t for r in rows if r.analyzable for line in r.stored_lines for t in line if S.legible(t)})
    K = len(vocab)
    base_t, base_s = M.coverage(tk), M.coverage(sk)
    ordered, load = template_codes(tk, vocab)
    rng0 = S.new_rng()
    probe = apply_merge(tk, merge_mapping(vocab, int(round(0.40 * K)), rng0))
    out = {"K": K, "base": {"TAB:I": base_t, "SEAL:S": base_s, "gap": base_t - base_s},
           "note_load_bearing_codes": len(load),
           "bite_merge40": {"tokens_rewritten": sum(1 for a, b in zip(tk, probe)
                                                    for x, y in zip(key_signs(a), key_signs(b)) if x != y),
                            "tablet_tokens": sum(len(key_signs(a)) for a in tk),
                            "sequences_altered": sum(1 for a, b in zip(tk, probe) if a != b),
                            "distinct_before": len(set(tk)), "distinct_after": len(set(probe))}}
    series = {}
    for mode in ("MERGE", "SPLIT", "SPLIT-WORST"):
        series[mode] = {"tab": [base_t], "sea": [base_s], "rows": []}
        for rate in RATES:
            k = max(1, int(round(rate * K)))
            rng = S.new_rng()
            gaps, ts, ss = [], [], []
            for _ in range(draws):
                if mode == "MERGE":
                    m = merge_mapping(vocab, k, rng)
                    t, s = apply_merge(tk, m), apply_merge(sk, m)
                else:
                    victims = set(rng.sample(vocab, k)) if mode == "SPLIT" else set(ordered[:k])
                    t = apply_split(tk, victims, rng)
                    s = apply_split(sk, victims, rng)
                ct, cs = M.coverage(t), M.coverage(s)
                ts.append(ct)
                ss.append(cs)
                gaps.append(ct - cs)
            g = M.summary(gaps)
            series[mode]["tab"].append(sum(ts) / draws)
            series[mode]["sea"].append(sum(ss) / draws)
            series[mode]["rows"].append({"rate": rate, "k": k, "tab_mean": sum(ts) / draws, "seal_mean": sum(ss) / draws,
                                         "gap_mean": g["mean"], "gap_p5": g["p5"], "gap_p95": g["p95"],
                                         "inverted_pct": 100.0 * sum(1 for x in gaps if x > 0) / draws})
    out["series"] = series
    orig_top = {k for k, _ in M.top_keys(tk)}
    prov = {}
    for rate in (0.02, 0.40):
        k = max(1, int(round(rate * K)))
        t = apply_split(tk, set(ordered[:k]), S.new_rng())
        top = M.top_keys(t)
        total = sum(n for _, n in top)
        frag = sum(n for key, n in top if parent(key) in orig_top)
        prov[str(rate)] = {"k": k, "top10_texts": total, "fragments_of_original": frag, "pct": 100.0 * frag / total}
    out["provenance"] = prov
    el = [r for r in sea if r.final_eligible]
    base = marker_stats([r.legible_reading for r in el], {"740"})
    rng = S.new_rng()
    split_all = {}
    for r in sorted(sea, key=lambda x: x.index):
        split_all[r.index] = [t + ("a" if rng.random() < 0.5 else "b") if t == "740" else t for t in r.legible_reading]
    seqs = [split_all[r.index] for r in el]
    out["marker"] = {"baseline": base, "half_740a": marker_stats(seqs, {"740a"}),
                     "half_740b": marker_stats(seqs, {"740b"}), "both_halves": marker_stats(seqs, {"740a", "740b"})}
    return out


# ----------------------------------------------------------------------------------------------------- 13.18
def rarest_first(freq):
    """13.18 F6 (and 13's general rule): "rarest first" = (count ascending, code ascending)."""
    return [s for s, _ in sorted(freq.items(), key=lambda kv: (kv[1], kv[0]))]


def fsw(rows, pop):
    f2 = {}
    for cls in FSW_CLASSES:
        q = [r.legible_reading for r in M.class_rows(rows, cls, pop)]
        one = sum(1 for x in q if len(SLOT & set(x)) >= 1)
        two = sum(1 for x in q if len(SLOT & set(x)) >= 2)
        f2[cls] = {"N": len(q), "ge1": one, "ge2": two, "rate_pct": 100.0 * two / max(one, 1)}
    # copy rule after the population filter (spec 12 D2(c)); identity under D0
    q = [r.legible_reading for r in M.apply_copy_rule([r for r in rows if r.analyzable and (pop == "all" or r.complete)])]
    f2["ALL"] = {"N": len(q), "ge1": sum(1 for x in q if len(SLOT & set(x)) >= 1),
                 "ge2": sum(1 for x in q if len(SLOT & set(x)) >= 2)}
    freq = collections.Counter(t for r in rows if r.analyzable for line in r.stored_lines for t in line if S.legible(t))
    rarest = rarest_first(freq)
    tk = [r.key for r in M.whole_text_rows(rows, M.TAB, pop)]
    sk = [r.key for r in M.whole_text_rows(rows, M.SEAL, pop)]
    f6 = {}
    for k in (0, 100, 200, 400, 600):
        merge = set(rarest[:k])
        t = [map_key(x, lambda s: "MRG" if s in merge else s) for x in tk]
        s = [map_key(x, lambda s_: "MRG" if s_ in merge else s_) for x in sk]
        ct, cs = M.coverage(t), M.coverage(s)
        f6[str(k)] = {"TAB:I": ct, "SEAL:S": cs, "gap": ct - cs}
    return {"F2": f2, "F6": f6, "F3": "not computed (13.18): one documented reading order after R1"}


# ----------------------------------------------------------------------------------------------------- 13.19
def dclass(r):
    return {"R/l": "R/L"}.get(r.dir, r.dir)


def stored_legible(r):
    """13.19: each text's legible tokens with lines joined in STORED order (the input the registered script read)."""
    return [t for line in r.stored_lines for t in line if S.legible(t)]


def cosine(a, b):
    keys = set(a) | set(b)
    num = sum(a[k] * b[k] for k in keys)
    return num / math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))


def storage_tests(texts):
    """T1-T4 of decision1_direction_tests.py on (direction class, stored legible sequence) pairs."""
    out = {}
    for name, signs in (("T1", {"740"}), ("T2", INITIAL_TYPE)):
        for d in DIRS:
            qs = [q for dc, q in texts if dc == d and len(q) >= 2]
            if qs:
                out["%s.%s" % (name, d)] = {"N": len(qs), "left": sum(q[0] in signs for q in qs),
                                            "right": sum(q[-1] in signs for q in qs)}
    rl = collections.Counter(tuple(q) for dc, q in texts if dc == "R/L")
    lr = [tuple(q) for dc, q in texts if dc == "L/R"]
    lr = [q for q in lr if len(q) >= 3 and q != q[::-1]]
    out["T3"] = {"N": len(lr), "same": sum(1 for q in lr if q in rl), "reversed": sum(1 for q in lr if q[::-1] in rl)}

    def bigrams(seqs):
        c = collections.Counter()
        for q in seqs:
            c.update(zip(q, q[1:]))
        return c
    b_rl = bigrams([q for dc, q in texts if dc == "R/L"])
    b_lr = bigrams([q for dc, q in texts if dc == "L/R"])
    b_rl_rev = collections.Counter({(y, x): n for (x, y), n in b_rl.items()})
    out["T4"] = {"same": cosine(b_lr, b_rl), "reversed": cosine(b_lr, b_rl_rev)}
    return out


def storage_test(rows):
    texts = [(dclass(r), stored_legible(r)) for r in rows if r.analyzable]
    real = storage_tests(texts)
    mutant = storage_tests([(d, q[::-1] if d == "L/R" else q) for d, q in texts])
    t1r, t1m = real["T1.L/R"], mutant["T1.L/R"]
    t2r, t2m = real["T2.L/R"], mutant["T2.L/R"]
    verdict = {"T1_LR_740_on_left_like_RL": t1r["left"] > t1r["right"], "T1_mutant_flips": t1m["right"] > t1m["left"],
               "T2_LR_initials_on_right": t2r["right"] > t2r["left"], "T2_mutant_flips": t2m["left"] > t2m["right"],
               "T3_identical_as_stored": real["T3"]["same"] > real["T3"]["reversed"],
               "T3_mutant_flips": mutant["T3"]["reversed"] > mutant["T3"]["same"],
               "T4_pairs_as_stored": real["T4"]["same"] > real["T4"]["reversed"],
               "T4_mutant_flips": mutant["T4"]["reversed"] > mutant["T4"]["same"]}
    return {"real": real, "mutant": mutant, "verdict": verdict}
