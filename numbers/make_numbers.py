"""B3: write every paper number as a LaTeX macro, from the frozen run's outputs (design: DESIGN.md).

- Refuses unless EVERY output file it reads has the SHA-256 recorded in the D2 table of
  `submission/scripts_v2/out/RUN_RECORD.md` (so a macro can only come from the verified run).
- Each registry entry (registry.py) names a macro, a source (output file + key path), a format and a meaning.
- Rounding: ONCE, from the full-precision run value, half-up, via Decimal(repr(value)); never from a rounded value.
- Output `numbers.tex`: one `\\newcommand{\\nName}{value}` per entry, sorted by name; deterministic bytes (LF).
- Fails on: a missing key, a None or non-number value, a duplicate or ill-formed macro name, an unknown format.
Run: python -I -B submission/numbers/make_numbers.py [--check]   (--check: regenerate in memory, compare, exit 1 on
any difference; used by the audit)
"""
import decimal
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "analysis", "out"))  # deposit: the runs write here
RUN_RECORD = os.path.normpath(os.path.join(HERE, "..", "run_record", "RUN_RECORD.md"))  # deposit location
TEX = os.path.join(HERE, "numbers.tex")
NAME = re.compile(r"^n[A-Z][A-Za-z]*$")  # n + UPPERCASE, so no clash with \newcommand, \node, \noindent
UNITS = {"pct", "plain", "x", "bits", "count", "p"}


def recorded_hashes(path=RUN_RECORD):
    text = open(path, encoding="utf-8").read()
    part = text.split("## Runs after deviation D2")[1]
    rows = re.findall(r"^\| `([^`]+\.json)` \| `([0-9a-f]{64})` \|", part, flags=re.M)
    table = dict(rows)
    if len(table) != 13:
        raise SystemExit("make_numbers: expected 13 rows in the D2 hash table of RUN_RECORD.md, found %d" % len(table))
    return table


def load_outputs(names, out_dir=OUT_DIR, hashes=None):
    hashes = hashes if hashes is not None else recorded_hashes()
    data = {}
    for n in sorted(names):
        if n not in hashes:
            raise SystemExit("make_numbers: %s is not in the D2 hash table; only verified outputs may be used" % n)
        raw = open(os.path.join(out_dir, n), "rb").read()
        got = hashlib.sha256(raw).hexdigest()
        if got != hashes[n]:
            raise SystemExit("make_numbers: %s SHA-256 %s differs from the record %s; refusing" % (n, got, hashes[n]))
        data[n] = json.loads(raw.decode("utf-8"))
    return data


def lookup(data, source):
    fname, path = source
    o = data[fname]
    for k in path:
        if isinstance(o, list) and isinstance(k, int) and -len(o) <= k < len(o):
            o = o[k]
        elif isinstance(o, dict) and k in o:
            o = o[k]
        else:
            raise SystemExit("make_numbers: key %r not found on the path %r in %s" % (k, path, fname))
    return o


def fmt(value, f):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SystemExit("make_numbers: value %r is not a number" % (value,))
    unit = f.get("unit")
    if unit not in UNITS:
        raise SystemExit("make_numbers: unknown unit %r" % (unit,))
    dec = f.get("dec", 0)
    q = decimal.Decimal(1).scaleb(-dec)
    d = decimal.Decimal(repr(value)).quantize(q, rounding=decimal.ROUND_HALF_UP)
    if d == 0:  # -0.0, or a tiny negative that rounds to zero: zero is printed unsigned, never "$-$0.00"
        d = abs(d)
    if unit == "count":
        if dec != 0:
            raise SystemExit("make_numbers: a count takes dec=0")
        s = "{:,}".format(int(d)).replace(",", "{,}")
    else:
        s = format(d, "f")
    if s.startswith("-"):
        s = "$-$" + s[1:]
    return s


def fmt_coords(points, f):
    """A TikZ coordinate list "(x,y) (x,y) ..." from [(x, y), ...]; each number rounded ONCE, half-up, from full
    precision; a minus sign is a plain '-' (TikZ syntax), never '$-$'."""
    if f.get("unit") != "coords":
        raise SystemExit("make_numbers: a series needs unit 'coords'")
    if not isinstance(points, (list, tuple)) or not points:
        raise SystemExit("make_numbers: a coordinate series must be a non-empty list")
    dx, dy = f.get("decx", 0), f.get("dec", 1)
    out = []
    for p in points:
        if not (isinstance(p, (list, tuple)) and len(p) == 2):
            raise SystemExit("make_numbers: coordinate %r is not an (x, y) pair" % (p,))
        xs = []
        for v, d in zip(p, (dx, dy)):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise SystemExit("make_numbers: coordinate value %r is not a number" % (v,))
            q = decimal.Decimal(1).scaleb(-d)
            r = decimal.Decimal(repr(v)).quantize(q, rounding=decimal.ROUND_HALF_UP)
            xs.append(format(abs(r) if r == 0 else r, "f"))
        out.append("(%s,%s)" % tuple(xs))
    return " ".join(out)


def build(registry, data):
    seen, lines = set(), []
    for e in registry:
        name = e["name"]
        if not NAME.match(name):
            raise SystemExit("make_numbers: macro name %r must be 'n' + an uppercase letter + letters only" % name)
        if name in seen:
            raise SystemExit("make_numbers: duplicate macro %r" % name)
        seen.add(name)
        if "derive" in e:  # a derived number from FULL-precision sources, never from printed macros
            vals = [lookup(data, s) for s in e["sources"]]
            value = e["derive"](*vals)
        else:
            value = lookup(data, e["source"])
        text = fmt_coords(value, e["format"]) if e["format"].get("unit") == "coords" else fmt(value, e["format"])
        lines.append((name, text, e.get("meaning", "")))
    lines.sort()
    body = "".join("\\newcommand{\\%s}{%s}%% %s\n" % (n, v, m.replace("%", "pct")) for n, v, m in lines)
    return "% GENERATED by submission/numbers/make_numbers.py from the D2 run outputs; do not edit.\n" + body


def files_needed(registry):
    out = set()
    for e in registry:
        for s in (e["sources"] if "sources" in e else [e["source"]]):
            out.add(s[0])
    return out


def main(argv):
    import registry
    data = load_outputs(files_needed(registry.ENTRIES))
    text = build(registry.ENTRIES, data)
    if "--check" in argv:
        old = open(TEX, encoding="utf-8").read() if os.path.exists(TEX) else None
        if old != text:
            print("make_numbers --check: numbers.tex differs from a fresh generation")
            return 1
        print("make_numbers --check: numbers.tex equals a fresh generation (%d macros)" % len(registry.ENTRIES))
        return 0
    with open(TEX, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("make_numbers: wrote %s (%d macros)" % (TEX, len(registry.ENTRIES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
