"""Compare Codex's blind re-implementation (review folder, codex/work/output_D0.json, output_D1.json) with our full
run (submission/scripts_v2/out/full_output.json, full_output_D1.json), value by value, and then macro by macro: every
printed number (numbers/registry.py) whose sources lie in a compared key is AGREE, DIFFER or NOT-COVERED.
Numbers equal if |a - b| <= 1e-9 * max(1, |a|, |b|); other values must be identical. Read-only; prints a report.
Values are printed truncated to 80 characters (some keys are whole texts; this is our own data, never sent out).

Run: py -3.11 -I -B independent/codex/compare_codex.py [THEIRS_DIR]
THEIRS_DIR defaults to the review folder's codex/work.
"""
import collections
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[2]  # deposit root
OURS = ROOT / "analysis" / "out"
THEIRS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "work"
sys.path.insert(0, str(ROOT / "numbers"))
import registry  # noqa: E402

PAIRS = {"full_output.json": "output_D0.json", "full_output_D1.json": "output_D1.json"}


def flatten(o, p=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flatten(v, "%s/%s" % (p, k) if p else str(k)))
    elif isinstance(o, list):
        if not o:
            out[p + "[]"] = "<empty list>"
        for i, v in enumerate(o):
            out.update(flatten(v, "%s[%d]" % (p, i)))
    else:
        out[p] = o
    return out


def regpath(path):
    s = ""
    for x in path:
        s += "[%d]" % x if isinstance(x, int) else ("/%s" % x if s else str(x))
    return s


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return a == b
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def short(v):
    r = repr(v)
    return r if len(r) <= 80 else r[:77] + "..."


flat = {}
for ours_name, theirs_name in PAIRS.items():
    ours_all = json.loads((OURS / ours_name).read_text(encoding="utf-8"))
    theirs_all = json.loads((THEIRS / theirs_name).read_text(encoding="utf-8"))
    tops = sorted(theirs_all)
    missing = [k for k in tops if k not in ours_all]
    o = flatten({k: ours_all[k] for k in tops if k in ours_all})
    t = flatten(theirs_all)
    flat[ours_name] = (o, t, set(tops))
    common = sorted(set(o) & set(t))
    differ = [k for k in common if not same(o[k], t[k])]
    print("=" * 110)
    print("%s vs %s | top-level keys: theirs %d, missing in ours %s" % (ours_name, theirs_name, len(tops), missing))
    print("values compared: %d | equal: %d | differ: %d | only ours: %d | only theirs: %d"
          % (len(common), len(common) - len(differ), len(differ), len(set(o) - set(t)), len(set(t) - set(o))))
    per = collections.defaultdict(lambda: [0, 0, 0, 0])
    for k in common:
        per[k.split("/")[0].split("[")[0]][0 if same(o[k], t[k]) else 1] += 1
    for k in set(o) - set(t):
        per[k.split("/")[0].split("[")[0]][2] += 1
    for k in set(t) - set(o):
        per[k.split("/")[0].split("[")[0]][3] += 1
    print("  %-34s %7s %7s %9s %11s" % ("top-level key", "equal", "differ", "only ours", "only theirs"))
    for k in sorted(per, key=lambda s: [int(x) if x.isdigit() else x for x in s.replace(":", ".").split(".")]):
        e, d, oo, ot = per[k]
        print("  %-34s %7d %7d %9d %11d%s" % (k, e, d, oo, ot, "" if d == oo == ot == 0 else "   <--"))
    for k in differ:
        print("DIFF  %s\n      ours %s | theirs %s" % (k, short(o[k]), short(t[k])))
    for k in sorted(set(o) - set(t)):
        print("ONLY OURS    %s = %s" % (k, short(o[k])))
    for k in sorted(set(t) - set(o)):
        print("ONLY THEIRS  %s = %s" % (k, short(t[k])))

print("=" * 110)
print("PRINTED NUMBERS (registry entries) whose sources are in Codex's scope")
verdict = {}
detail = collections.defaultdict(list)
for e in registry.ENTRIES:
    srcs = [e["source"]] if "source" in e else list(e["sources"])
    states = []
    for f, p in srcs:
        if f not in flat:
            states.append("OUT")
            continue
        o, t, tops = flat[f]
        if p[0] not in tops:
            states.append("OUT")
            continue
        key = regpath(p)
        ok = [k for k in o if k == key or k.startswith(key + "/") or k.startswith(key + "[")]
        if not ok:
            states.append("NOKEY")
            detail[e["name"]].append("no such key in ours: " + key)
            continue
        bad = [k for k in ok if k not in t or not same(o[k], t[k])]
        states.append("DIFFER" if bad else "AGREE")
        for k in bad[:3]:
            detail[e["name"]].append("%s ours %s | theirs %s" % (k, short(o[k]), short(t.get(k, "<absent>"))))
    if all(s == "OUT" for s in states):
        v = "OUT-OF-SCOPE"
    elif "NOKEY" in states:
        v = "NOKEY"
    elif "DIFFER" in states:
        v = "DIFFER"
    elif "OUT" in states:
        v = "PARTLY-IN-SCOPE"
    else:
        v = "AGREE"
    verdict[e["name"]] = v
print(dict(collections.Counter(verdict.values())))
for n, v in sorted(verdict.items()):
    if v in ("DIFFER", "NOKEY", "PARTLY-IN-SCOPE"):
        print("  %-16s %s" % (v, n))
        for d in detail.get(n, []):
            print("      " + d)
