"""Every difference between Codex's blind re-implementation and our full run, recomputed with OUR library under
CODEX'S reading of the specification. If a reading reproduces Codex's values exactly, that difference is fully
explained by the reading (not by a bug on either side). Read-only (imports scripts_v2; writes nothing).
Also the converse for the unit difference (K_tri/N: ours x 1/100 = Codex) and the 13.16 key-meaning difference.

Run: py -3.11 -I -B independent/codex/reproduce_codex_readings.py [THEIRS_DIR]
"""
import collections
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]  # deposit root
SV2 = ROOT / "analysis"
sys.path.insert(0, str(SV2))
import spec_lib as S  # noqa: E402
import spec_lib_measures as M  # noqa: E402
import spec_lib_protocols as P  # noqa: E402
import spec_lib_s13a as A  # noqa: E402
import spec_lib_s13b as B  # noqa: E402
import spec_lib_s13d as D  # noqa: E402

THEIRS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "work"
OURS_F = {"D0": "full_output.json", "D1": "full_output_D1.json"}
THEIRS_F = {"D0": "output_D0.json", "D1": "output_D1.json"}
ours = {v: json.loads((SV2 / "out" / f).read_text(encoding="utf-8")) for v, f in OURS_F.items()}
theirs = {v: json.loads((THEIRS / f).read_text(encoding="utf-8")) for v, f in THEIRS_F.items()}
results = []


def same(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    return a == b


def check(label, variant, mine, key_path):
    t = theirs[variant]
    for k in key_path:
        t = t[k]
    o = ours[variant]
    for k in key_path:
        o = o[k]
    r_t, r_o = same(mine, t), same(mine, o)
    results.append((label, variant, r_t))
    print("%-58s %s  reproduces Codex: %-5s | equals our printed run: %s" % (label, variant, r_t, r_o))


rows = S.load_rows()
DIRMAP = {"R/l": "R/L"}


def codex_dir(r):
    d = r.dir.strip()
    return DIRMAP.get(d, d)


for variant in ("D0", "D1"):
    with M.copy_rule(variant):
        an = [r for r in rows if r.analyzable]
        # R1: direction row with 'R/l' -> 'R/L' (13.19's normalisation) instead of `dir.` exactly R/L or L/R
        rl = [r for r in an if codex_dir(r) in ("R/L", "L/R")]
        check("R1 13.1 Table 2 R/L-L/R row, 'R/l' counted as R/L", variant,
              A.table2_metrics(M.apply_copy_rule(rl)), ["13.1.table2", "sensitivity_rl_lr"])
        check("R1 13.1 M-342 R/L-L/R row, 'R/l' counted as R/L", variant,
              A.m342(M.apply_copy_rule(rl)), ["13.1.m342", "sensitivity_rl_lr"])
        for pop in ("all", "complete"):
            # R2: 740 split drawn over the ELIGIBLE (measured) texts only, in row order
            sea = M.whole_text_rows(rows, M.SEAL, pop)
            el = sorted([r for r in sea if r.final_eligible], key=lambda x: x.index)
            rng = S.new_rng()
            seqs = [[t + ("a" if rng.random() < 0.5 else "b") if t == "740" else t for t in r.legible_reading]
                    for r in el]
            mk = {"baseline": D.marker_stats([r.legible_reading for r in el], {"740"}),
                  "half_740a": D.marker_stats(seqs, {"740a"}), "half_740b": D.marker_stats(seqs, {"740b"}),
                  "both_halves": D.marker_stats(seqs, {"740a", "740b"})}
            check("R2 13.17 marker, split drawn over eligible texts (%s)" % pop, variant, mk,
                  ["13.17.%s" % pop, "marker"])
            # R3: F6 'rarest' ranked within the population (after the copy rule), not over all analyzable rows
            popr = M.apply_copy_rule([r for r in an if pop == "all" or r.complete])
            freq = collections.Counter(t for r in popr for line in r.stored_lines for t in line if S.legible(t))
            rarest = D.rarest_first(freq)
            tk = [r.key for r in M.whole_text_rows(rows, M.TAB, pop)]
            sk = [r.key for r in M.whole_text_rows(rows, M.SEAL, pop)]
            f6 = {}
            for k in (0, 100, 200, 400, 600):
                merge = set(rarest[:k])
                ct = M.coverage([D.map_key(x, lambda s: "MRG" if s in merge else s) for x in tk])
                cs = M.coverage([D.map_key(x, lambda s: "MRG" if s in merge else s) for x in sk])
                f6[str(k)] = {"TAB:I": ct, "SEAL:S": cs, "gap": ct - cs}
            check("R3 13.18 F6, rarest ranked within the population (%s)" % pop, variant, f6,
                  ["13.18.%s" % pop, "F6"])
            # R4: G4b mean length over ALL multi-sign SEAL:S of each tier (not only the eligible ones)
            ml = {}
            for tname in ("core", "regional"):
                x = [r for r in sea if B.tier(r.site) == tname]
                ml[tname] = sum(r.n_legible for r in x) / len(x)
            check("R4 13.8 G4b mean length over all multi-sign seals (%s)" % pop, variant, ml,
                  ["13.8.%s" % pop, "appendix_G4", "G4b_mean_length"])
            # R5: 07-C stems as LEGIBLE signs before the final one (000 dropped), not key tokens
            c = []
            for t, ct in B.ranked(collections.Counter(r.final_sign for r in el), 3):
                stems = collections.Counter(tuple(r.legible_reading[:-1]) for r in el if r.final_sign == t)
                c.append({"terminal": t, "texts": ct, "pct_of_eligible": 100.0 * ct / len(el),
                          "distinct_stems_pct": 100.0 * len(stems) / ct,
                          "stems_once_pct": 100.0 * sum(1 for v in stems.values() if v == 1) / ct,
                          "distinct_stems": len(stems)})
            check("R5 13.7 07-C stems without 000 (%s)" % pop, variant, {"eligible": len(el), "top3": c},
                  ["13.7.%s" % pop, "C_terminals"])

# U1: K_tri/N in percent (ours) vs as a fraction (Codex)
for variant in ("D0", "D1"):
    for pop in ("all", "complete"):
        o, t = ours[variant]["13.2.table3.%s" % pop], theirs[variant]["13.2.table3.%s" % pop]
        ok = all(same(o[c]["ktri_over_n"] / 100.0, t[c]["ktri_over_n"]) for c in o if "ktri_over_n" in o[c])
        results.append(("U1 K_tri/N unit (%s)" % pop, variant, ok))
        print("%-58s %s  ours/100 == Codex in every class: %s" % ("U1 K_tri/N unit (%s)" % pop, variant, ok))
# K1: 13.16 P2 pct_analyzable: ours = real CISI / analyzable; Codex = analyzable / all rows (same counts)
p_o, p_t = ours["D0"]["13.16"]["P2"], theirs["D0"]["13.16"]["P2"]
k1 = (same(p_o["pct_analyzable"], 100.0 * p_o["real_cisi_analyzable"] / p_o["analyzable"])
      and same(p_t["pct_analyzable"], 100.0 * p_t["analyzable"] / p_t["all_rows"])
      and all(p_o[k] == p_t[k] for k in p_o if k != "pct_analyzable"))
results.append(("K1 13.16 P2 key meaning", "D0", k1))
print("%-58s D0  counts equal; ours = CISI/analyzable, Codex = analyzable/all: %s" % ("K1 13.16 P2 key meaning", k1))
# K2: 13.16 P4 rows without a legible sign: Codex counts the 1 malformed row too
mal = sum(1 for r in rows if getattr(r, "malformed", False))
k2 = theirs["D0"]["13.16"]["P4"]["rows_without_legible_sign"] == ours["D0"]["13.16"]["P4"]["rows_without_legible_sign"] + mal
results.append(("K2 13.16 P4 malformed row counted by Codex", "D0", k2))
print("%-58s D0  Codex = ours + malformed (%d): %s" % ("K2 13.16 P4 malformed row counted by Codex", mal, k2))
print("\nALL READINGS REPRODUCE CODEX:", all(r[2] for r in results), "(%d checks)" % len(results))
