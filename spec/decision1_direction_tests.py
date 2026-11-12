"""Independent checks of ICIT's storage direction (3 Nov 2026). Shares no code with the paper (no chr_lib import).
Reads the pinned corpus JSON (symbols, direction, artefact_type). Read-only.

T1 terminal sign 740: at which END of the stored string, per direction class (incl. unknown/NR/T/B/BUS/SYM)
T2 initial-type signs (Fuls, Catalog Fig. 3.3: 190, 315, 853, 880): at which END, per direction class
T3 identical texts across directions: is an L/R text's stored string equal to an R/L text's stored string (same
   storage order) more often than to the REVERSE of one (physical order)?
T4 sign pairs: does the L/R texts' stored bigram distribution match the R/L texts' stored bigrams or their reverse?
T5 effect numbers recomputed from scratch: TAB:I top-10 coverage and the share of SEAL:S texts ending in 740, under
   the paper's rule and under ICIT's rule (paper prints 40.4% and 35.1% under its rule).
SELF-TEST: a mutant corpus in which every L/R string is reversed (as if L/R texts were stored physically) must flip
T1-T4 for L/R; otherwise the tests are blind.
"""
import collections, hashlib, json, math, sys
sys.stdout.reconfigure(encoding="utf-8")
P = "sanitized_corpus.json"  # deposit: a private file; this script is the RECORD of the 13.19 procedure, the shipped analysis re-implements it (spec_lib_s13d.py)
raw = open(P, "rb").read()
print("corpus sha256", hashlib.sha256(raw).hexdigest()[:12], "(pinned 0053bafcd025)")
C0 = json.loads(raw)
C0 = [r for r in C0 if any(s != "000" for s in r["symbols"])]          # analyzable, as the paper
print("analyzable rows:", len(C0))

def dclass(r):
    d = r["direction"].strip()
    return {"R/l": "R/L"}.get(d, d)

def legible(seq):
    return [s for s in seq if s not in ("000", "999")]

def run(C, label):
    out = {}
    print("\n==== %s ====" % label)
    # T1 / T2
    for name, signs in (("T1 terminal 740", {"740"}), ("T2 initial 190/315/853/880", {"190", "315", "853", "880"})):
        print(name, "(share of texts with 2+ legible signs whose LEFT / RIGHT end is that sign)")
        for d in ("R/L", "L/R", "-", "NR", "T/B", "BUS", "SYM"):
            rows = [legible(r["symbols"]) for r in C if dclass(r) == d]
            rows = [q for q in rows if len(q) >= 2]
            if not rows:
                continue
            left = sum(q[0] in signs for q in rows); right = sum(q[-1] in signs for q in rows)
            print("   %-4s N=%4d  left %5.1f%%  right %5.1f%%" % (d, len(rows), 100 * left / len(rows), 100 * right / len(rows)))
            out[(name, d)] = (left, right, len(rows))
    # T3
    RL = collections.Counter(tuple(legible(r["symbols"])) for r in C if dclass(r) == "R/L")
    LR = [tuple(legible(r["symbols"])) for r in C if dclass(r) == "L/R"]
    LR = [q for q in LR if len(q) >= 3 and q != q[::-1]]                   # palindromes cannot tell
    same = sum(1 for q in LR if q in RL); rev = sum(1 for q in LR if q[::-1] in RL)
    print("T3 L/R texts (3+ signs, not palindromes) N=%d: stored string also found among R/L texts AS STORED %d, "
          "only REVERSED %d" % (len(LR), same, rev))
    out["T3"] = (same, rev)
    # T4
    def bigrams(rows):
        c = collections.Counter()
        for q in rows:
            c.update(zip(q, q[1:]))
        return c
    rl = bigrams([legible(r["symbols"]) for r in C if dclass(r) == "R/L"])
    lr = bigrams([legible(r["symbols"]) for r in C if dclass(r) == "L/R"])
    def cos(a, b):
        keys = set(a) | set(b)
        num = sum(a[k] * b[k] for k in keys)
        return num / math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
    rl_rev = collections.Counter({(b, a): n for (a, b), n in rl.items()})
    c_same, c_rev = cos(lr, rl), cos(lr, rl_rev)
    print("T4 cosine similarity of L/R bigrams with R/L bigrams AS STORED %.3f, with R/L bigrams REVERSED %.3f"
          % (c_same, c_rev))
    out["T4"] = (c_same, c_rev)
    # T5
    def order(r, rule):
        s = r["symbols"]
        if rule == "paper":
            return list(s) if r["direction"].strip() == "L/R" else s[::-1]
        return s[::-1]                                                     # ICIT: every text read right to left
    for rule in ("paper", "icit"):
        tabs = [tuple(x for x in order(r, rule) if x != "000") for r in C if r["artefact_type"] == "TAB:I"]
        tabs = [q for q in tabs if len(q) >= 2]
        cnt = collections.Counter(tabs)
        top10 = 100 * sum(n for _, n in cnt.most_common(10)) / len(tabs)
        seals = [[x for x in order(r, rule) if x != "000"] for r in C if r["artefact_type"] == "SEAL:S"]
        seals = [q for q in seals if len(q) >= 2]
        e740 = 100 * sum(q[-1] == "740" for q in seals) / len(seals)
        print("T5 rule=%-5s TAB:I multi-sign N=%d top-10 coverage %.1f%% | SEAL:S multi-sign N=%d ending in 740 %.1f%%"
              % (rule, len(tabs), top10, len(seals), e740))
        out[("T5", rule)] = (round(top10, 1), round(e740, 1))
    return out

real = run(C0, "REAL CORPUS")
mut = [dict(r, symbols=r["symbols"][::-1]) if dclass(r) == "L/R" else r for r in C0]
mutant = run(mut, "SELF-TEST MUTANT: every L/R string reversed (as if stored in physical order)")

print("\n==== VERDICTS ====")
l1, r1, _ = real[("T1 terminal 740", "L/R")]; ml1, mr1, _ = mutant[("T1 terminal 740", "L/R")]
print("T1 L/R texts end-sign 740 on the LEFT like R/L texts:", l1 > r1, "| mutant flips it:", mr1 > ml1)
l2, r2, _ = real[("T2 initial 190/315/853/880", "L/R")]; ml2, mr2, _ = mutant[("T2 initial 190/315/853/880", "L/R")]
print("T2 L/R texts start-signs on the RIGHT like R/L texts:", r2 > l2, "| mutant flips it:", ml2 > mr2)
print("T3 identical texts stored the same way:", real["T3"][0] > real["T3"][1], "| mutant flips it:", mutant["T3"][1] > mutant["T3"][0])
print("T4 L/R pairs resemble R/L pairs as stored:", real["T4"][0] > real["T4"][1], "| mutant flips it:", mutant["T4"][1] > mutant["T4"][0])
print("T5 instrument check (paper rule reproduces printed 40.4 / 35.1):", real[("T5", "paper")] == (40.4, 35.1),
      "| ICIT rule:", real[("T5", "icit")])
