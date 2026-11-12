"""Independent implementation of the frozen Decision 2 measurement specification.

This file intentionally uses only the Python standard library and no project code.
It reads the pinned CSV without emitting record contents.
"""
import csv
import hashlib
import io
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent  # deposit: schema/ and work/ sit beside this file
DATA = Path(__file__).resolve().parents[2] / "data" / "input.csv"  # deposit: the pinned file
PIN = "c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98"
CLASSES = ("SEAL:S", "SEAL:R", "TAB:B", "TAB:I", "POT:T:g")
CORE = {"Mohenjo-daro", "Harappa"}
FOREIGN = {"Ur", "Kish", "Susa", "Nippur", "Tello", "Girsu", "Tell Umma",
           "Failaka", "Karzakan", "Qala'at al-Bahrain", "Saar", "Janabiyah",
           "Hajar", "Ra's al-Junayz", "Salut", "Kalba", "Altyn Depe",
           "Gonur Depe", "Shortughai", "Tepe Yahya", "Luristan", "Pirak"}


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def q(v):
    s = sorted(v)
    return (s[math.floor(.05 * (len(s) - 1))], s[math.floor(.95 * (len(s) - 1))]) if s else (0.0, 0.0)


def rank_items(c, key=lambda x: x):
    return sorted(c.items(), key=lambda z: (-z[1], key(z[0])))


def missing(v):
    return not str(v or "").strip().replace("-", "").replace("?", "").replace(" ", "")


def field(row, *names):
    for n in names:
        if n in row:
            return row[n].strip()
    return ""


def text_parts(s):
    """Return stored marks/tokens, or None for a malformed code."""
    s = s.strip()
    left = s[0] if s and s[0] in "+[]" else ""
    if left:
        s = s[1:]
    right = s[-1] if s and s[-1] in "+[]" else ""
    if right:
        s = s[:-1]
    if "+" in s:
        raise RuntimeError("text-part marker found in core")
    lines = s.split("/")
    stored = [line.split("-") for line in lines]
    if any(not tok or not re.fullmatch(r"\d{3}", tok)
           for line in stored for tok in line):
        return None
    return left, stored, right


def make_row(i, raw):
    raw = {k: (v or "").strip() for k, v in raw.items()}
    code = field(raw, "text")
    parsed = text_parts(code)
    r = {
        "i": i, "id": field(raw, "id"), "cisi": field(raw, "cisi"),
        "site": field(raw, "site"), "type": field(raw, "type", "artefact_type"),
        "dir": field(raw, "dir.", "direction"), "complete": field(raw, "complete") == "Y",
        "code": code, "area": field(raw, "area-section", "area_section", "area section"),
        "room": field(raw, "room-grid", "room_grid", "room grid"),
        "depth": field(raw, "depth"), "malformed": parsed is None,
    }
    if parsed is None:
        r.update(left="", right="", stored=[], read=[], key=None, ser="", leg=[])
        return r
    left, stored, right = parsed
    read = [list(reversed(x)) for x in reversed(stored)]
    keylines = [tuple(x for x in line if x != "999") for line in read]
    r.update(left=left, right=right, stored=stored, read=read,
             key=(right, tuple(keylines), left),
             ser=right + "|" + "/".join("-".join(x) for x in keylines) + "|" + left,
             leg=[x for line in read for x in line if x not in ("000", "999")])
    return r


def load_rows():
    blob = DATA.read_bytes()
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("data SHA-256 mismatch")
    rows = [make_row(i, x) for i, x in enumerate(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline="")))]
    return rows


def analyzable(r):
    return not r["malformed"] and bool(r["leg"])


def objid(r):
    return r["id"].rsplit(".", 1)[0]


def single(r):
    return "/" not in r["code"] and r["dir"].strip().upper() != "BUS"


def end_ok(r):
    return single(r) and r["left"] == "+" and bool(r["read"]) and r["read"][-1] and r["read"][-1][-1] not in ("000", "999")


def start_ok(r):
    return single(r) and r["right"] == "+" and bool(r["read"]) and r["read"][0] and r["read"][0][0] not in ("000", "999")


def final(r):
    return r["read"][-1][-1]


def initial(r):
    return r["read"][0][0]


def tier(site):
    return "core" if site in CORE else ("foreign" if site in FOREIGN else "regional")


def copy_d1(rows):
    kept = {}
    for r in rows:
        k = (r["site"], r["type"], r["code"])
        if k not in kept:
            kept[k] = r
    return list(kept.values())


def selected(rows, variant, cls=None, d1=False, multi=False):
    a = [r for r in rows if analyzable(r) and (variant == "all" or r["complete"])
         and (cls is None or r["type"] == cls) and (not multi or len(r["leg"]) >= 2)]
    return copy_d1(a) if d1 else a


def keys(rows):
    return Counter(r["key"] for r in rows)


def topkeys(rows, n=10):
    c = keys(rows)
    return [k for k, _ in sorted(c.items(), key=lambda z: (-z[1], ser_key(z[0])))[:n]]


def ser_key(k):
    return k[0] + "|" + "/".join("-".join(x) for x in k[1]) + "|" + k[2]


def key_legible_length(k):
    """Number of legible signs in a section-2 identity key."""
    return sum(x not in ("000", "999") for line in k[1] for x in line)


def cov(rows, n=10, func=lambda r: r["key"], order=lambda z: z):
    if not rows:
        return 0.0
    c = Counter(func(r) for r in rows)
    return pct(sum(x for _, x in sorted(c.items(), key=lambda z: (-z[1], order(z[0])))[:n]), len(rows))


def repeat_share(rows):
    c = keys(rows)
    return pct(sum(v for v in c.values() if v >= 2), len(rows))


def runs(rows):
    out = []
    for r in rows:
        if r["dir"].strip().upper() == "BUS" and "/" not in r["code"]:
            continue
        for line in r["read"]:
            cur = []
            for x in line:
                if x in ("000", "999"):
                    if cur:
                        out.append(cur)
                    cur = []
                else:
                    cur.append(x)
            if cur:
                out.append(cur)
    return out


def h1(rows):
    c = Counter(x for r in rows for x in r["leg"])
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values()) if n else 0.0


def trigrams(rows_or_runs, already_runs=False):
    rs = rows_or_runs if already_runs else runs(rows_or_runs)
    tri, ctx = Counter(), Counter()
    for line in rs:
        for i in range(len(line) - 2):
            t = tuple(line[i:i + 3]); tri[t] += 1; ctx[t[:2]] += 1
    return tri, ctx


def h3(rows_or_runs, already_runs=False):
    tri, ctx = trigrams(rows_or_runs, already_runs)
    n = sum(tri.values())
    if not n:
        return 0.0, 0.0, 0, 0
    h = -sum(v / n * math.log2(v / ctx[t[:2]]) for t, v in tri.items())
    return h, h + (len(tri) - len(ctx)) / (2.0 * n * math.log(2)), len(tri), n


def singleton(rows_or_runs, already_runs=False):
    tri, ctx = trigrams(rows_or_runs, already_runs)
    n = sum(tri.values())
    return pct(sum(v for v in ctx.values() if v == 1), n)


def shuf_h3(rows, iterations):
    observed = h3(rows)[0]
    rr = runs(rows); rng = random.Random(42); vals = []
    for _ in range(iterations):
        rs = []
        for x in rr:
            y = x[:]; rng.shuffle(y); rs.append(y)
        vals.append(h3(rs, True)[0])
    mean = sum(vals) / len(vals)
    return {"iterations": iterations, "observed": observed, "null_mean": mean,
            "null_min": min(vals), "p": (1 + sum(x <= observed for x in vals)) / (1 + iterations),
            "reduction_pct": pct(mean - observed, mean),
            "templated": ((1 + sum(x <= observed for x in vals)) / (1 + iterations) < .05 and mean > observed)}


def shuf_single(rows):
    rr = runs(rows); rng = random.Random(42); vals = []
    for _ in range(200):
        z = []
        for x in rr:
            y = x[:]; rng.shuffle(y); z.append(y)
        vals.append(singleton(z, True))
    return {"observed": singleton(rr, True), "shuffled_mean": sum(vals) / len(vals)}


def sign_stats(rows):
    toks = [x for r in rows for x in r["leg"]]
    c = Counter(toks); n = len(toks)
    top = [x for x, _ in rank_items(c)]
    e = [r for r in rows if end_ok(r)]
    s = [r for r in rows if start_ok(r)]
    return {"N": len(rows), "top_sign_share": pct(max(c.values()) if c else 0, n),
            "top69_coverage": pct(sum(c[x] for x in top[:69]), n),
            "top82_coverage": pct(sum(c[x] for x in top[:82]), n),
            "eligible_starters": len(s), "eligible_enders": len(e),
            "starters_top82": pct(sum(1 for r in s if initial(r) in set([x for x, _ in rank_items(Counter(initial(z) for z in s))][:82])), len(s)),
            "enders_top23": pct(sum(1 for r in e if final(r) in set([x for x, _ in rank_items(Counter(final(z) for z in e))][:23])), len(e)),
            "mean_legible_length": sum(len(r["leg"]) for r in rows) / len(rows) if rows else 0.0}


def m342(rows):
    m = [r for r in rows if len(r["leg"]) >= 2]
    e = [r for r in m if end_ok(r)]
    hits = sum(final(r) == "740" for r in e)
    toks = [x for r in e for x in r["leg"]]
    share = pct(toks.count("740"), len(toks))
    rate = pct(hits, len(e))
    return {"multisign_texts": len(m), "eligible": len(e), "rate_740_final": rate,
            "token_share_740": share, "concentration": rate / share if share else 0.0}


def table3(rows):
    out = {}
    for cls in CLASSES:
        x = [r for r in rows if r["type"] == cls]
        hp, hm, kt, nt = h3(x)
        out[cls] = {"N": len(x), "mean_legible_length": sum(len(r["leg"]) for r in x) / len(x) if x else 0.0,
                    "H1": h1(x), "H3": hp, "H3_mm": hm, "ktri_over_n": kt / nt if nt else 0.0}
    for label, cs in (("SEALS pooled", ("SEAL:S", "SEAL:R")), ("TABLETS pooled", ("TAB:B", "TAB:I"))):
        x = [r for r in rows if r["type"] in cs]
        out[label] = {"N": len(x), "mean_legible_length": sum(len(r["leg"]) for r in x) / len(x) if x else 0.0,
                      "H3": h3(x)[0]}
    return out


def tablet_templates(rows):
    tab = [r for r in rows if r["type"] == "TAB:I"]
    multi = [r for r in tab if len(r["leg"]) >= 2]
    lp = Counter(len(r["leg"]) for r in tab)
    e = [r for r in multi if end_ok(r)]
    tc = Counter(final(r) for r in e)
    terminals = []
    for t, n in rank_items(tc)[:4]:
        pre = Counter()
        for r in e:
            if final(r) == t:
                line = r["read"][-1]
                if len(line) >= 2 and line[-2] not in ("000", "999"):
                    pre[line[-2]] += 1
        top = rank_items(pre)[:5]
        terminals.append({"terminal": t, "texts": n, "pct_of_eligible": pct(n, len(e)),
                          "preceders_top5": [[x, v] for x, v in top],
                          "top5_cover_pct": pct(sum(v for _, v in top), n)})
    slot = {"032", "033", "034"}
    present = Counter(str(len(slot & set(r["leg"]))) for r in tab)
    pos = Counter(); neigh = Counter(); following = 0; neighbours = 0
    for r in tab:
        if r["complete"] and single(r):
            z = r["leg"]
            for j, x in enumerate(z):
                if x in slot:
                    pos["initial" if j == 0 else "terminal" if j == len(z) - 1 else "medial"] += 1
        for line in r["read"]:
            for j in range(len(line) - 1):
                if line[j] in slot and line[j + 1] not in ("000", "999"):
                    neigh[line[j + 1]] += 1; neighbours += 1
                    following += line[j + 1] == "700"
    fam = sum(r["leg"] in (["032", "700"], ["033", "700"], ["034", "700"]) for r in multi)
    c = keys(multi); cum = 0; tops = []
    for k, n in sorted(c.items(), key=lambda z: (-z[1], ser_key(z[0])))[:10]:
        cum += n; tops.append([ser_key(k), n, pct(cum, len(multi))])
    prod = {}
    for cls in ("TAB:I", "SEAL:S"):
        x = [r for r in rows if r["type"] == cls and len(r["leg"]) >= 2]
        cc = keys(x)
        prod[cls] = {"N": len(x), "cov10": cov(x), "once_pct": pct(sum(v for v in cc.values() if v == 1), len(x))}
    return {"A_length_profile": {str(k): {"texts": v, "pct": pct(v, len(tab))} for k, v in sorted(lp.items())},
            "B_terminals": {"eligible_multisign": len(e), "top4": terminals},
            "C_slot": {"members_present": dict(present), "position_when_present": {x: pos[x] for x in ("initial", "medial", "terminal")},
                       "right_neighbours_top4": [[x, v] for x, v in rank_items(neigh)[:4]],
                       "pct_followed_by_700": pct(following, neighbours), "family_member_then_700": fam,
                       "family_pct_of_multisign": pct(fam, len(multi))},
            "D_templates": {"multisign_texts": len(multi), "distinct_keys": len(c),
                            "keys_shared": sum(v >= 2 for v in c.values()), "texts_on_shared_keys": sum(v for v in c.values() if v >= 2),
                            "repeat_share": repeat_share(multi), "top10_cumulative": tops}, "E_productivity": prod}


def seal_regime(rows):
    seal_all = [r for r in rows if r["type"] == "SEAL:S"]
    seal = [r for r in seal_all if len(r["leg"]) >= 2]
    lp = Counter(len(r["leg"]) for r in seal_all)
    e = [r for r in seal if end_ok(r)]
    tc = Counter(final(r) for r in e); tops = []
    for t, n in rank_items(tc)[:3]:
        stems = Counter(tuple(r["leg"][:-1]) for r in e if final(r) == t)
        tops.append({"terminal": t, "texts": n, "pct_of_eligible": pct(n, len(e)),
                     "distinct_stems": len(stems), "distinct_stems_pct": pct(len(stems), n),
                     "stems_once_pct": pct(sum(v == 1 for v in stems.values()), n)})
    st = [r for r in seal if start_ok(r)]
    opens = rank_items(Counter(initial(r) for r in st))[:5]
    reuse = {}
    for cls in ("SEAL:S", "TAB:I"):
        x = [r for r in rows if r["type"] == cls and len(r["leg"]) >= 2]
        f = [r for r in x if start_ok(r) and end_ok(r)]
        reuse[cls] = {"whole_text_cov10": cov(x), "frame_texts": len(f),
                      "frame_cov10": cov(f, func=lambda r: (initial(r), final(r)), order=lambda z: z)}
    return {"A_length_profile": {str(k): v for k, v in sorted(lp.items())},
            "A_mean_legible_length": sum(len(r["leg"]) for r in seal_all) / len(seal_all) if seal_all else 0.0,
            "C_terminals": {"eligible": len(e), "top3": tops},
            "D_openers": {"eligible": len(st), "top5": [[x, v] for x, v in opens],
                          "top5_pct": pct(sum(v for _, v in opens), len(st))}, "E_reuse": reuse}


def rate_block(rows):
    n = len(rows); hits = sum(final(r) == "740" for r in rows)
    return {"N": n, "hits": hits, "rate": pct(hits, n)}


def ztest(a, na, b, nb):
    if not na or not nb:
        return 0.0, 1.0
    p = (a + b) / (na + nb)
    se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb))
    z = (a / na - b / nb) / se if se else 0.0
    return z, math.erfc(abs(z) / math.sqrt(2))


def geography(rows, d1, corpus_rows=None):
    """Section 13.8 for one population/copy-rule variant.

    The rate denominators are section-5 eligible texts.  Length description is
    not an end-marker measure, so it retains all multi-sign seals, as script 09
    does.  The D2 site-count amendment is a corpus description and therefore
    receives the unfiltered analyzable corpus separately.
    """
    seal = [r for r in rows if r["type"] == "SEAL:S" and len(r["leg"]) >= 2]
    elig = [r for r in seal if end_ok(r)]
    bysite = defaultdict(list)
    for r in elig:
        bysite[r["site"]].append(r)
    sites = {s: rate_block(x) for s, x in bysite.items() if len(x) >= 30}
    tiers = {}
    for t in ("core", "regional", "foreign"):
        tiers[t] = rate_block([r for r in elig if tier(r["site"]) == t])
    foreign = {}
    for s in sorted({r["site"] for r in seal if tier(r["site"]) == "foreign"}):
        a = [r for r in seal if r["site"] == s]; b = [r for r in a if end_ok(r)]
        foreign[s] = {"multisign": len(a), "eligible": len(b), "end_740": sum(final(r) == "740" for r in b)}
    core = [r for r in elig if tier(r["site"]) == "core"]
    reg = [r for r in elig if tier(r["site"]) == "regional"]
    core_multi = [r for r in seal if tier(r["site"]) == "core"]
    reg_multi = [r for r in seal if tier(r["site"]) == "regional"]
    z, p = ztest(sum(final(r) == "740" for r in core), len(core), sum(final(r) == "740" for r in reg), len(reg))
    bylen = {str(L): rate_block([r for r in elig if len(r["leg"]) == L]) for L in range(2, 7)}
    match = {}
    for L in range(3, 6):
        match[str(L)] = {"core": rate_block([r for r in core if len(r["leg"]) == L]),
                         "regional": rate_block([r for r in reg if len(r["leg"]) == L])}
    g = {"adequately_sampled_sites": len(sites), "sites_rate_740": sites, "tiers": tiers,
         "foreign_itemised": foreign,
         "appendix_G4": {"G4a": {"core": rate_block(core), "regional": rate_block(reg), "z": z, "p": p},
                          "G4b_by_length": bylen, "G4b_mean_length": {
                              "core": sum(len(r["leg"]) for r in core_multi) / len(core_multi) if core_multi else 0.0,
                              "regional": sum(len(r["leg"]) for r in reg_multi) / len(reg_multi) if reg_multi else 0.0},
                          "G4b_matched": match}}
    if not d1 and corpus_rows is not None:
        allseal = [r for r in corpus_rows if analyzable(r) and r["type"] == "SEAL:S"]
        g["distinct_sites_with_SEAL:S"] = len({r["site"] for r in allseal})
    return g


def site_shares(rows):
    out = {}
    for cls in ("TAB:I", "SEAL:S"):
        x = [r for r in rows if r["type"] == cls]
        c = Counter(r["site"] for r in x)
        top = c.most_common(5)
        out[cls] = {"N": len(x), "harappa_pct": pct(c["Harappa"], len(x)),
                    "top5": [[s, n, pct(n, len(x))] for s, n in top]}
    return out


def positive(rows):
    tab = [r for r in rows if r["type"] == "TAB:I" and len(r["leg"]) >= 2]
    sea = [r for r in rows if r["type"] == "SEAL:S" and len(r["leg"]) >= 2]
    vocab = GLOBAL_VOCAB; weights = [GLOBAL_FREQ[x] for x in vocab]
    rng = random.Random(42)
    lt, ls = [len(r["leg"]) for r in tab], [len(r["leg"]) for r in sea]
    templates = [tuple(rng.choices(vocab, weights=weights, k=rng.choice(lt))) for _ in range(10)]
    a, b = [], []
    for _ in range(len(tab)):
        if rng.random() < .40:
            a.append(rng.choice(templates))
        else:
            a.append(tuple(rng.choices(vocab, weights=weights, k=rng.choices(lt, k=1)[0])))
    for _ in range(len(sea)):
        b.append(tuple(rng.choices(vocab, weights=weights, k=rng.choices(ls, k=1)[0])))
    def cc(x):
        c = Counter(x); return pct(sum(v for _, v in rank_items(c, key=lambda z: z)[:10]), len(x))
    aa, bb = cc(a), cc(b)
    return {"A_cov10": aa, "B_cov10": bb, "gap": aa - bb}


def groups(rows, mode):
    d = {}; anon = 0
    for r in rows:
        if mode == "G1":
            k = ("text", r["i"])
        elif mode == "G2":
            k = ("obj", objid(r))
        else:
            if missing(r["area"]) or (r["area"].endswith("-") and "trench" not in r["area"].lower()):
                k = ("row", r["i"])
            else:
                k = ("spot", r["site"], r["area"])
        d.setdefault(k, []).append(r)
    return list(d.values())


def split_groups(groups0, n, rng):
    order = groups0[:]; rng.shuffle(order); fold1 = []
    for g in order:
        if len(fold1) < n / 2:
            fold1.extend(g)
        else:
            break
    used = {r["i"] for r in fold1}
    return fold1, [r for g in groups0 for r in g if r["i"] not in used]


def prediction(rows):
    tab = [r for r in rows if r["type"] == "TAB:I" and len(r["leg"]) >= 2]
    sea = [r for r in rows if r["type"] == "SEAL:S" and len(r["leg"]) >= 2]
    tg, sg = groups(tab, "G3"), groups(sea, "G3")
    rng = random.Random(42); acc = []; bal = []; tr = []; sr = []
    for _ in range(200):
        tt, te = split_groups(tg, len(tab), rng); st, se = split_groups(sg, len(sea), rng)
        ts, ss = {r["key"] for r in tt}, {r["key"] for r in st}
        markers = Counter(final(r) for r in st if end_ok(r))
        marker = rank_items(markers)[0][0] if markers else ""
        lengths = sorted(len(r["leg"]) for r in tt); med = lengths[len(lengths) // 2] if lengths else 0
        def pred(r):
            if r["key"] in ts and r["key"] not in ss: return 1
            if r["key"] in ss and r["key"] not in ts: return 0
            if end_ok(r) and final(r) == marker: return 0
            return int(len(r["leg"]) <= med)
        hit_t = sum(pred(r) for r in te); hit_s = sum(not pred(r) for r in se)
        tr.append(pct(hit_t, len(te))); sr.append(pct(hit_s, len(se)))
        acc.append(pct(hit_t + hit_s, len(te) + len(se))); bal.append((tr[-1] + sr[-1]) / 2)
    return {"accuracy": sum(acc) / len(acc), "majority_baseline": pct(max(len(tab), len(sea)), len(tab) + len(sea)),
            "balanced_accuracy": sum(bal) / len(bal), "tablet_recall": sum(tr) / len(tr), "seal_recall": sum(sr) / len(sr)}


def shared(rows):
    out = {}
    for name, multi in (("multisign", True), ("any_length", False)):
        x = [r for r in rows if not multi or len(r["leg"]) >= 2]
        d = defaultdict(set)
        for r in x: d[r["key"]].add(r["type"])
        out[name] = {"distinct_keys": len(d), "keys_with_more_than_one_type": sum(len(v) > 1 for v in d.values()),
                     "keys_in_both_TAB:I_and_SEAL:S": sum({"TAB:I", "SEAL:S"} <= v for v in d.values())}
    return out


def provenance(allrows):
    an = [r for r in allrows if analyzable(r)]
    real = lambda r: bool(re.fullmatch(r"[A-Za-z]+-\d+", r["cisi"]))
    h = [r for r in allrows if re.fullmatch(r"H-(?:10[4-9]|11[0-9]|12[0-8])", r["cisi"])]
    total000 = sum(x == "000" for r in an for line in r["stored"] for x in line)
    total999 = sum(x == "999" for r in an for line in r["stored"] for x in line)
    toks = [x for r in an for x in r["leg"]]
    tab = [r for r in an if r["type"] == "TAB:I" and len(r["leg"]) >= 2]
    by = defaultdict(list)
    for r in tab: by[objid(r)].append(r)
    multi = {k: v for k, v in by.items() if len(v) > 1}
    onmulti = sum(len(v) for v in multi.values())
    reps = sum(len(v) - len({r["key"] for r in v}) for v in multi.values())
    return {"P2": {"all_rows": len(allrows), "analyzable": len(an), "pct_analyzable": pct(len(an), len(allrows)),
                    "real_cisi_all_rows": sum(real(r) for r in allrows), "real_cisi_analyzable": sum(real(r) for r in an)},
            "P4": {"rows_H104_H128": len(h), "rows_without_legible_sign": sum(not r["leg"] for r in allrows)},
            "P5": {"legible_tokens": len(toks), "distinct_legible_signs": len(set(toks)), "tokens_000": total000, "tokens_999": total999},
            "P7": {"analyzable_texts": len(an), "icit_objects": len({objid(r) for r in an}), "multisign_tab_texts": len(tab),
                   "tab_objects_with_more_than_one_multisign_text": len(multi),
                   "tab_objects_repeating_a_key": sum(len({r["key"] for r in v}) < len(v) for v in multi.values()),
                   "within_object_repeats": reps, "texts_on_multi_text_objects": onmulti,
                   "pct_on_multi_text_objects": pct(onmulti, len(tab))}}


def merge_mapping(vocab, k, rng):
    d = {}
    for victim in rng.sample(vocab, k):
        target = rng.choice(vocab)
        while target == victim:
            target = rng.choice(vocab)
        d[victim] = target
    return d


def merge_key(k, mapping):
    """Apply a corpus-wide sign conflation without changing marks, breaks, or 000."""
    return (k[0], tuple(tuple(mapping.get(x, x) if x != "000" else x for x in line)
                        for line in k[1]), k[2])


def split_key(k, victims, rng):
    """Independently split each occurrence of a selected *legible* sign."""
    return (k[0], tuple(tuple(x + ("a" if rng.random() < .5 else "b")
                               if x in victims else x for x in line)
                        for line in k[1]), k[2])


def split_sequence(seq, victims, rng):
    """The marker check operates on a single eligible line, not on text keys."""
    return tuple(x + ("a" if rng.random() < .5 else "b") if x in victims else x for x in seq)


def covkeys(texts):
    c = Counter(texts)
    return pct(sum(v for _, v in sorted(c.items(), key=lambda z: (-z[1], ser_key(z[0])))[:10]), len(texts))


def parent_key(k):
    def parent_sign(x):
        return x[:-1] if len(x) == 4 and x[:3].isdigit() and x[-1] in "ab" else x
    return (k[0], tuple(tuple(parent_sign(x) for x in line) for line in k[1]), k[2])


def sensitivity(rows, global_vocab):
    # Section 13.17 is explicitly a key-based analysis.  A perturbation changes
    # only legible tokens inside the section-2 key: end marks, line boundaries
    # and 000 placeholders remain part of identity.
    tab = [r["key"] for r in rows if r["type"] == "TAB:I" and len(r["leg"]) >= 2]
    sea = [r["key"] for r in rows if r["type"] == "SEAL:S" and len(r["leg"]) >= 2]
    vocab = global_vocab
    K = len(vocab)
    bt, bs = covkeys(tab), covkeys(sea)
    c = Counter(tab)
    load = []
    for key, _ in sorted(c.items(), key=lambda z: (-z[1], ser_key(z[0])))[:10]:
        for line in key[1]:
            for sign in line:
                if sign != "000" and sign not in load:
                    load.append(sign)
    tc = Counter(sign for key in tab for line in key[1] for sign in line if sign != "000")
    rest = [sign for sign, _ in rank_items(tc) if sign not in load]
    seen = set(load) | set(rest)
    ordered = load + rest + [sign for sign in vocab if sign not in seen]
    probe_mapping = merge_mapping(vocab, max(1, int(round(.4 * K))), random.Random(42))
    probe = [merge_key(key, probe_mapping) for key in tab]
    bite = {
        "tablet_tokens": sum(key_legible_length(key) for key in tab),
        "tokens_rewritten": sum(
            x != y for old, new in zip(tab, probe)
            for old_line, new_line in zip(old[1], new[1])
            for x, y in zip(old_line, new_line)
        ),
        "sequences_altered": sum(old != new for old, new in zip(tab, probe)),
        "distinct_before": len(set(tab)),
        "distinct_after": len(set(probe)),
    }
    series = {}
    for mode in ("MERGE", "SPLIT", "SPLIT-WORST"):
        tt, ss, records = [bt], [bs], []
        for rate in (.01, .02, .05, .10, .20, .40):
            k = max(1, int(round(rate * K)))
            rng = random.Random(42)
            ts, zs, gs = [], [], []
            for _ in range(200):
                if mode == "MERGE":
                    mapping = merge_mapping(vocab, k, rng)
                    a = [merge_key(key, mapping) for key in tab]
                    b = [merge_key(key, mapping) for key in sea]
                else:
                    victims = set(rng.sample(vocab, k)) if mode == "SPLIT" else set(ordered[:k])
                    a = [split_key(key, victims, rng) for key in tab]
                    b = [split_key(key, victims, rng) for key in sea]
                aa, bb = covkeys(a), covkeys(b)
                ts.append(aa)
                zs.append(bb)
                gs.append(aa - bb)
            lo, hi = q(gs)
            mt, ms = sum(ts) / len(ts), sum(zs) / len(zs)
            tt.append(mt)
            ss.append(ms)
            records.append({"rate": rate, "k": k, "tab_mean": mt, "seal_mean": ms,
                            "gap_mean": sum(gs) / len(gs), "gap_p5": lo, "gap_p95": hi,
                            "inverted_pct": pct(sum(value > 0 for value in gs), len(gs))})
        series[mode] = {"rows": records, "tab": tt, "sea": ss}
    prov = {}
    originals = {key for key, _ in sorted(c.items(), key=lambda z: (-z[1], ser_key(z[0])))[:10]}
    for rate in (.02, .4):
        k = max(1, int(round(rate * K)))
        rng = random.Random(42)
        altered = [split_key(key, set(ordered[:k]), rng) for key in tab]
        top = sorted(Counter(altered).items(), key=lambda z: (-z[1], ser_key(z[0])))[:10]
        n = sum(count for _, count in top)
        fragments = sum(count for key, count in top if parent_key(key) in originals)
        prov[str(rate)] = {"k": k, "top10_texts": n, "fragments_of_original": fragments,
                           "pct": pct(fragments, n)}

    def marker(seqs, codes):
        terminal = [seq[-1] for seq in seqs]
        nonterminal = [sign for seq in seqs for sign in seq[:-1]]
        terminal_pct = pct(sum(sign in codes for sign in terminal), len(terminal))
        nonterminal_pct = pct(sum(sign in codes for sign in nonterminal), len(nonterminal))
        return {"terminal_pct": terminal_pct, "nonterminal_pct": nonterminal_pct,
                "enrichment": terminal_pct / nonterminal_pct if nonterminal_pct else 0.0}

    marker_rows = [tuple(r["leg"]) for r in rows if r["type"] == "SEAL:S"
                   and len(r["leg"]) >= 2 and end_ok(r)]
    marker_rng = random.Random(42)
    split_marker = [split_sequence(seq, {"740"}, marker_rng) for seq in marker_rows]
    return {"K": K, "base": {"TAB:I": bt, "SEAL:S": bs, "gap": bt - bs},
            "note_load_bearing_codes": len(load), "bite_merge40": bite, "series": series,
            "provenance": prov,
            "marker": {"baseline": marker(marker_rows, {"740"}),
                       "half_740a": marker(split_marker, {"740a"}),
                       "half_740b": marker(split_marker, {"740b"}),
                       "both_halves": marker(split_marker, {"740a", "740b"})}}


def f2f6(rows, vocab):
    slot = {"032", "033", "034"}; out = {"F2": {}, "F3": "Not computed: R1 defines one documented reading convention.", "F6": {}}
    allx = rows
    for cls in CLASSES:
        x = [r for r in rows if r["type"] == cls]; one = sum(bool(slot & set(r["leg"])) for r in x); two = sum(len(slot & set(r["leg"])) >= 2 for r in x)
        out["F2"][cls] = {"N": len(x), "ge1": one, "ge2": two, "rate_pct": pct(two, one)}
    one = sum(bool(slot & set(r["leg"])) for r in allx); two = sum(len(slot & set(r["leg"])) >= 2 for r in allx)
    out["F2"]["ALL"] = {"N": len(allx), "ge1": one, "ge2": two}
    freq = Counter(x for r in rows for x in r["leg"])
    rare = [x for x, _ in sorted(freq.items(), key=lambda z: (z[1], z[0]))]
    for k in (0, 100, 200, 400, 600):
        m = set(rare[:k])
        def qx(cls):
            return [merge_key(r["key"], {x: "MRG" for x in m}) for r in rows
                    if r["type"] == cls and len(r["leg"]) >= 2]
        a, b = covkeys(qx("TAB:I")), covkeys(qx("SEAL:S"))
        out["F6"][str(k)] = {"TAB:I": a, "SEAL:S": b, "gap": a - b}
    return out


def direction_class(r):
    return {"R/l": "R/L"}.get(r["dir"].strip(), r["dir"].strip())


def stored_leg(r, mutant=False):
    q0 = [x for line in r["stored"] for x in line if x not in ("000", "999")]
    return list(reversed(q0)) if mutant and direction_class(r) == "L/R" else q0


def storage(rows, mutant=False):
    dirs = ("R/L", "L/R", "-", "NR", "T/B", "BUS", "SYM")
    out = {}
    for tag, signs in (("T1", {"740"}), ("T2", {"190", "315", "853", "880"})):
        for d in dirs:
            x = [stored_leg(r, mutant) for r in rows if direction_class(r) == d]; x = [q0 for q0 in x if len(q0) >= 2]
            out[tag + "." + d] = {"N": len(x), "left": sum(q0[0] in signs for q0 in x), "right": sum(q0[-1] in signs for q0 in x)}
    rl = Counter(tuple(stored_leg(r, mutant)) for r in rows if direction_class(r) == "R/L")
    lr = [tuple(stored_leg(r, mutant)) for r in rows if direction_class(r) == "L/R"]
    lr = [q0 for q0 in lr if len(q0) >= 3 and q0 != q0[::-1]]
    out["T3"] = {"N": len(lr), "same": sum(q0 in rl for q0 in lr), "reversed": sum(q0[::-1] in rl for q0 in lr)}
    def pairs(qs):
        c = Counter()
        for q0 in qs: c.update(zip(q0, q0[1:]))
        return c
    a = pairs([stored_leg(r, mutant) for r in rows if direction_class(r) == "R/L"]); b = pairs([stored_leg(r, mutant) for r in rows if direction_class(r) == "L/R"])
    def cosine(x, y):
        ks = set(x) | set(y); den = math.sqrt(sum(v * v for v in x.values()) * sum(v * v for v in y.values()))
        return sum(x[k] * y[k] for k in ks) / den if den else 0.0
    rev = Counter({(y, x): n for (x, y), n in a.items()})
    out["T4"] = {"same": cosine(b, a), "reversed": cosine(b, rev)}
    return out


def ebuds(rows):
    x = [r for r in rows if analyzable(r) and r["complete"] and single(r) and 1 <= len(r["leg"]) <= 14]
    first = {}
    for r in x:
        first.setdefault(r["key"], r)
    return list(first.values())


def sensitivity_rl(rows, d1=False):
    x = [r for r in rows if analyzable(r) and direction_class(r) in ("R/L", "L/R")]
    return copy_d1(x) if d1 else x


def table1(rows):
    return {c: sum(analyzable(r) and r["type"] == c for r in rows) for c in CLASSES}


def two_sign(rows):
    x = [r for r in rows if r["type"] == "TAB:I" and len(r["leg"]) >= 2]
    tk = topkeys(x); covered = [r for r in x if r["key"] in set(tk)]
    n2 = sum(len(r["leg"]) == 2 for r in covered)
    return {"top10_two_sign_keys": sum(key_legible_length(k) == 2 for k in tk), "texts_top10": len(covered),
            "texts_two_sign": n2, "share_pct": pct(n2, len(covered))}


def extra_seal_parts(rows):
    """Compute 13.7's unkeyed G2/G3 quantities (schema omits their fields)."""
    x = [r for r in rows if r["type"] == "SEAL:S" and len(r["leg"]) >= 2]
    e = [r for r in x if end_ok(r)]
    toks = [z for r in e for z in r["leg"]]
    terminal = [final(r) for r in e]
    other = [z for r in e for z in r["leg"][:-1]]
    _ = (pct(toks.count("740"), len(toks)), pct(terminal.count("740"), len(terminal)), pct(other.count("740"), len(other)))
    y = [r for r in x if r["complete"] and start_ok(r) and end_ok(r) and len(r["leg"]) >= 3]
    for z in ([initial(r) for r in y], [u for r in y for u in r["leg"][1:-1]], [final(r) for r in y]):
        c = Counter(z); n = len(z)
        _ = (-sum(v / n * math.log2(v / n) for v in c.values()) + (len(c) - 1) / (2 * n * math.log(2))) if n else 0.0


def build(rows, d1=False):
    out = {}
    # 13.1
    if not d1:
        out["13.1.table1"] = table1(rows)
    a_all = selected(rows, "all", d1=d1); a_complete = selected(rows, "complete", d1=d1)
    out["13.1.m342"] = {"all": m342(a_all), "complete": m342(a_complete),
                          "sensitivity_rl_lr": m342(sensitivity_rl(rows, d1))}
    t2 = {"full": sign_stats(a_all), "sensitivity_rl_lr": sign_stats(sensitivity_rl(rows, d1))}
    if not d1:
        t2["ebuds_like"] = sign_stats(ebuds(rows))
    out["13.1.table2"] = t2
    # 13.2
    for variant in ("all", "complete"):
        every = selected(rows, variant, d1=d1)
        out["13.2.table3." + variant] = table3(every)
        for cls in CLASSES:
            x = [r for r in every if r["type"] == cls]
            out["13.2.null." + cls + "." + variant] = shuf_h3(x, 10000 if cls in ("TAB:I", "TAB:B") else 2000)
            out["13.2.singleton." + cls + "." + variant] = shuf_single(x)
    # 13.3, 13.5, 13.7
    for variant in ("all", "complete"):
        every = selected(rows, variant, d1=d1)
        out["13.3." + variant] = tablet_templates(every)
        out["13.5." + variant] = two_sign(every)
        out["13.7." + variant] = seal_regime(every)
        extra_seal_parts(every)
    # 13.8
    for variant in ("all", "complete"):
        out["13.8." + variant] = geography(selected(rows, variant, d1=d1), d1, rows)
    if not d1:
        out["13.8.site_shares"] = site_shares(selected(rows, "all"))
    # 13.12--15
    for variant in ("all", "complete"):
        every = selected(rows, variant, d1=d1)
        out["13.12." + variant] = positive(every)
        out["13.13." + variant] = prediction(every)
        ti = [r for r in every if r["type"] == "TAB:I" and len(r["leg"]) >= 2]
        tb = [r for r in every if r["type"] == "TAB:B" and len(r["leg"]) >= 2]
        out["13.14." + variant] = {"N": {"TAB:I": len(ti), "TAB:B": len(tb)}, "TAB:I": cov(ti), "TAB:B": cov(tb)}
        out["13.17." + variant] = sensitivity(every, GLOBAL_VOCAB)
        out["13.18." + variant] = f2f6(every, GLOBAL_VOCAB)
    out["13.15"] = shared(selected(rows, "all", d1=d1))
    if not d1:
        out["13.16"] = provenance(rows)
        real = storage([r for r in rows if analyzable(r)], False)
        mutant = storage([r for r in rows if analyzable(r)], True)
        out["13.19"] = {"real": real, "mutant": mutant,
                          "verdict": {
                              "T1_LR_740_on_left_like_RL": real["T1.L/R"]["left"] > real["T1.L/R"]["right"],
                              "T1_mutant_flips": mutant["T1.L/R"]["right"] > mutant["T1.L/R"]["left"],
                              "T2_LR_initials_on_right": real["T2.L/R"]["right"] > real["T2.L/R"]["left"],
                              "T2_mutant_flips": mutant["T2.L/R"]["left"] > mutant["T2.L/R"]["right"],
                              "T3_identical_as_stored": real["T3"]["same"] > real["T3"]["reversed"],
                              "T3_mutant_flips": mutant["T3"]["reversed"] > mutant["T3"]["same"],
                              "T4_pairs_as_stored": real["T4"]["same"] > real["T4"]["reversed"],
                              "T4_mutant_flips": mutant["T4"]["reversed"] > mutant["T4"]["same"]}}
    return out


def validate_schema_value(value, schema):
    """Fail closed if an output cannot have the exact declared JSON layout."""
    if isinstance(schema, str):
        if schema == "int":
            ok = type(value) is int
        elif schema == "float":
            ok = type(value) is float and math.isfinite(value)
        elif schema == "str":
            ok = type(value) is str
        elif schema == "bool":
            ok = type(value) is bool
        else:
            ok = False
        if not ok:
            raise RuntimeError("output value does not match its declared schema type")
        return
    if "__list__" in schema:
        if not isinstance(value, list) or len(value) > schema["__list__"]:
            raise RuntimeError("output list does not match its declared schema")
        for item in value:
            validate_schema_value(item, schema["item"])
        return
    if "__tuple__" in schema:
        wanted = schema["__tuple__"]
        if not isinstance(value, (list, tuple)) or len(value) != len(wanted):
            raise RuntimeError("output tuple does not match its declared schema")
        for item, item_schema in zip(value, wanted):
            validate_schema_value(item, item_schema)
        return
    if not isinstance(value, dict):
        raise RuntimeError("output object does not match its declared schema")
    dynamic = [key for key in schema if key.startswith("<") and key.endswith(">")]
    static = {key for key in schema if key not in dynamic and key != "__keys__"}
    if dynamic:
        if len(dynamic) != 1 or not static <= set(value):
            raise RuntimeError("output dynamic-key object does not match its schema")
        for key in static:
            validate_schema_value(value[key], schema[key])
        for key, item in value.items():
            if key not in static:
                validate_schema_value(item, schema[dynamic[0]])
    else:
        if set(value) != static:
            raise RuntimeError("output object keys do not match its declared schema")
        for key in static:
            validate_schema_value(value[key], schema[key])


def write_output(name, obj):
    schema = json.loads((ROOT / "schema" / ("schema_" + name + ".json")).read_text(encoding="utf-8"))
    if set(obj) != set(schema):
        raise RuntimeError(name + " top-level keys differ from schema")
    validate_schema_value(obj, schema)
    (ROOT / "work").mkdir(exist_ok=True)
    (ROOT / "work" / ("output_" + name + ".json")).write_text(json.dumps(obj, sort_keys=True, indent=1) + "\n", encoding="utf-8")


def main():
    global GLOBAL_VOCAB, GLOBAL_FREQ
    rows = load_rows()
    GLOBAL_VOCAB = sorted({x for r in rows if analyzable(r) for x in r["leg"]})
    GLOBAL_FREQ = Counter(x for r in rows if analyzable(r) for x in r["leg"])
    write_output("D0", build(rows, False))
    write_output("D1", build(rows, True))


if __name__ == "__main__":
    main()



