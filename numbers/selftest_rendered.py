"""Self-test of check_rendered.py on a compiled pair (PAPER.tex PAPER.pdf): the real text must pass; a copy with one
macro value altered must FAIL in direction A; a copy with one stray number inserted must FAIL in direction B; a
copy where a sign code is written with a digit changed must FAIL in direction B. Exit 0 only if all four hold.
Usage: python -I -B selftest_rendered.py PAPER.tex PAPER.pdf
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import allowlist  # noqa: E402
import check_rendered as C  # noqa: E402


def run(label, tex, body, expect_prefix):
    probs, _ = C.check(tex, body, allowlist.ENTRIES)
    hit = [p for p in probs if p.startswith(expect_prefix)] if expect_prefix else probs
    ok = (not probs) if expect_prefix is None else bool(hit)
    print("%-52s %s  (%d problem(s)%s)" % (label, "OK" if ok else "NOT CAUGHT", len(probs),
                                         ("; e.g. " + hit[0][:70]) if hit else ""))
    return ok


def main(argv):
    tex, pdf = argv
    body = C.pdf_body(pdf)
    macros, sgn, _ = C.source_sets(tex)
    # a value that prints exactly once, with a decimal point, so the mutation is unambiguous
    target = next(v for n, v in sorted(macros.items()) if "." in v and body.count(v) == 1 and "(" not in v)
    mutated = body.replace(target, target[:-1] + ("7" if target[-1] != "7" else "8"), 1)
    stray = body.replace("Introduction", "Introduction 31337", 1)
    # a real sign code (not the 000 placeholder, which the template's dummy DOI also contains), written once as a
    # whole token in the body; its digit changed must surface as an unexplained number
    code = next(c for c in sorted(sgn) if c not in ("000", "999")
                and len(re.findall(r"(?<![\d.])" + c + r"(?![\d])", body)) == 1)
    new = ("9" if code[0] != "9" else "8") + code[1:]
    wrong_sign = re.sub(r"(?<![\d.])" + code + r"(?![\d])", new, body, count=1)
    ok = run("control: the real text passes", tex, body, None)
    ok &= run("A: one macro value altered in the text (%s)" % target, tex, mutated, "A:")
    ok &= run("B: one stray number inserted", tex, stray, "B:")
    ok &= run("B: one sign code altered (%s -> %s)" % (code, new), tex, wrong_sign, "B: number %r" % new)
    print("selftest_rendered:", "4 of 4" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
