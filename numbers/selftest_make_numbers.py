"""Self-test of make_numbers.py: each planted fault must make it FAIL for its own reason; the control must PASS.
Works on scratch copies only (a temp folder); never touches the real outputs or numbers.tex.
Run: python -I -B submission/numbers/selftest_make_numbers.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_numbers as MN  # noqa: E402
import registry  # noqa: E402

results = []


def expect_fail(label, fn, must_contain):
    try:
        fn()
    except SystemExit as e:
        msg = str(e)
        ok = must_contain in msg
        results.append((label, ok, msg if ok else "failed for the WRONG reason: " + msg))
        return
    except Exception as e:  # a crash is not a detection
        results.append((label, False, "crashed (WRONG reason): %s: %s" % (type(e).__name__, e)))
        return
    results.append((label, False, "did NOT fail"))


def expect_pass(label, fn):
    try:
        fn()
        results.append((label, True, "passed"))
    except SystemExit as e:
        results.append((label, False, "unexpected failure: %s" % e))


hashes = MN.recorded_hashes()
names = MN.files_needed(registry.ENTRIES)

# control: the real registry on the real outputs
expect_pass("control: real registry, real outputs", lambda: MN.build(registry.ENTRIES, MN.load_outputs(names, hashes=hashes)))

# plant 1: one byte changed in a scratch copy of an output -> hash refusal
tmp = tempfile.mkdtemp(prefix="b3_selftest_")
try:
    for n in names:
        shutil.copy(os.path.join(MN.OUT_DIR, n), os.path.join(tmp, n))
    p = os.path.join(tmp, "core_output.json")
    raw = open(p, "rb").read()
    assert raw.count(b"50.87719298245614") >= 1  # a real value; changing one digit keeps the JSON valid
    open(p, "wb").write(raw.replace(b"50.87719298245614", b"50.97719298245614", 1))
    expect_fail("plant: one byte changed in an output", lambda: MN.load_outputs(names, out_dir=tmp, hashes=hashes), "differs from the record")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

data = MN.load_outputs(names, hashes=hashes)
base = registry.ENTRIES[0]
expect_fail("plant: an output not in the D2 table", lambda: MN.load_outputs({"not_a_run_file.json"}, hashes=hashes), "not in the D2 hash table")
expect_fail("plant: missing key", lambda: MN.build([dict(base, source=(base["source"][0], ["no.such.key"]))], data), "not found")
expect_fail("plant: duplicate macro", lambda: MN.build([base, dict(base)], data), "duplicate macro")
expect_fail("plant: macro name with a digit", lambda: MN.build([dict(base, name="nCov10")], data), "must be 'n' + an uppercase")
expect_fail("plant: macro name clashing with \\node", lambda: MN.build([dict(base, name="node")], data), "must be 'n' + an uppercase")
expect_fail("plant: unknown unit", lambda: MN.build([dict(base, format={"unit": "furlongs", "dec": 1})], data), "unknown unit")
expect_fail("plant: value is not a number", lambda: MN.fmt("50.9", {"unit": "pct", "dec": 1}), "is not a number")
expect_fail("plant: count with decimals", lambda: MN.fmt(5530, {"unit": "count", "dec": 1}), "a count takes dec=0")

# rounding: half-up from the full value (Python's round() would give 2.2 and 0.12)
for v, dec, want in ((2.25, 1, "2.3"), (0.125, 2, "0.13"), (-0.55, 1, "$-$0.6"), (5530, 0, None)):
    got = MN.fmt(v, {"unit": "count" if want is None else "pct", "dec": dec})
    want = want or "5{,}530"
    results.append(("rounding %r at %d -> %s" % (v, dec, want), got == want, "got %s" % got))

# zero is printed unsigned: -0.0 (seen in the run: 13.2 POT:T:g null_min) and a negative rounding to zero
for v, want in ((-0.0, "0.00"), (-0.004, "0.00"), (-0.005, "$-$0.01")):
    got = MN.fmt(v, {"unit": "plain", "dec": 2})
    results.append(("signed zero %r -> %s" % (v, want), got == want, "got %s" % got))
got = MN.fmt_coords([(0, -0.0)], {"unit": "coords", "dec": 1})
results.append(("coords signed zero", got == "(0,0.0)", "got %s" % got))

# coordinate series (figures): format, rounding once, plain minus, and refusals
got = MN.fmt_coords([(0, 2.25), (1, -0.55), (2, 10)], {"unit": "coords", "dec": 1})
results.append(("coords format and rounding", got == "(0,2.3) (1,-0.6) (2,10.0)", "got %s" % got))
expect_fail("plant: coords with a non-number", lambda: MN.fmt_coords([(0, "x")], {"unit": "coords", "dec": 1}), "is not a number")
expect_fail("plant: coords not a pair", lambda: MN.fmt_coords([(0, 1, 2)], {"unit": "coords", "dec": 1}), "not an (x, y) pair")
expect_fail("plant: empty series", lambda: MN.fmt_coords([], {"unit": "coords", "dec": 1}), "non-empty list")
expect_fail("plant: series without coords unit", lambda: MN.fmt_coords([(0, 1)], {"unit": "pct", "dec": 1}), "needs unit 'coords'")

# --check must catch an edited numbers.tex (scratch copy of the module's TEX path)
tmp2 = tempfile.mkdtemp(prefix="b3_check_")
try:
    real_tex = MN.TEX
    MN.TEX = os.path.join(tmp2, "numbers.tex")
    open(MN.TEX, "w", encoding="utf-8", newline="\n").write(MN.build(registry.ENTRIES, data).replace("50.9", "50.8"))
    rc = MN.main(["--check"])
    results.append(("plant: hand-edited numbers.tex caught by --check", rc == 1, "exit %d" % rc))
    open(MN.TEX, "w", encoding="utf-8", newline="\n").write(MN.build(registry.ENTRIES, data))
    rc = MN.main(["--check"])
    results.append(("control: fresh numbers.tex passes --check", rc == 0, "exit %d" % rc))
finally:
    MN.TEX = real_tex
    shutil.rmtree(tmp2, ignore_errors=True)

bad = [r for r in results if not r[1]]
for label, ok, msg in results:
    print("%-55s %s  (%s)" % (label, "OK  " if ok else "FAIL", msg[:90]))
print("selftest_make_numbers: %d checks, %d failed: %s" % (len(results), len(bad), "PASS" if not bad else "FAIL"))
sys.exit(1 if bad else 0)
