"""B3, the RENDERED-text check (DESIGN.md: "every number in the PDF text is the output of some macro or allow-listed";
not built until 12 Nov 2026). Two directions on the PDF's text layer, body only (up to the References heading):

  A  every macro the paper uses prints somewhere in the PDF (its value as numbers.tex writes it; a series macro,
     whose points are drawn as coordinates, is checked point by point only where the figure prints the value, so
     series macros are listed as NOTE, not checked);
  B  every numeric token in the PDF body is explained: a macro value, an allow-listed phrase's digits, a sign code
     (\\sgn{...}) or layout constant (\\lay{...}) of the source, a section / table / figure / citation number, a
     page number, or the template's licence line. Anything else is a FAIL.

Usage: python -I -B check_rendered.py PAPER.tex PAPER.pdf        (the packaged, compiled pair)
       python -I -B check_rendered.py --text PAPER.tex BODY.txt   (pre-extracted text, for the self-test)
Exit 0 = clean. Standard library + pdftotext (poppler, as shipped with Git for Windows).
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PDFTOTEXT = shutil.which("pdftotext") or r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"
NUM = re.compile(r"(?<![A-Za-z\d.])\d+(?:,\d{3})*(?:\.\d+)?(?![\d])")
DEF = re.compile(r"\\newcommand\{\\(n[A-Z][A-Za-z]*)\}\{(.*?)\}%")


def pdf_body(pdf):
    txt = subprocess.run([PDFTOTEXT, "-enc", "UTF-8", pdf, "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    return body_of(txt)


def body_of(txt):
    """The whole text without the bibliography: from the References heading to the first appendix heading
    ("A The ...") after it, or to the end when there is no appendix."""
    body = txt.replace("\f", "\n")
    ref = re.search(r"^\s*References\s*$", body, re.M)
    if ref:
        app = re.search(r"^[A-Z]\s+[A-Z][a-z]", body[ref.end():], re.M)
        end = ref.end() + app.start() if app else len(body)
        body = body[:ref.start()] + body[end:]
    body = body.replace("\u2212", "-").replace("\u2013", "-")
    body = re.sub(r"(\d)\s*\n\s*,(\d{3})", r"\1,\2", body)  # thousands group split over a line
    return body


def printed(value):
    """numbers.tex value -> the string the PDF text should contain."""
    v = value.replace("{,}", ",").replace("$-$", "-").replace("\\%", "%")
    return v


def source_sets(tex):
    import audit
    raw = open(tex, encoding="utf-8").read()
    src = audit.strip_comments(raw)  # not a naive split at '%': an escaped \% is text
    # the values come from numbers.tex (the generated file) when it is beside this script, not from the definitions
    # inlined into the checked paper: a wrong inlined value would otherwise be "confirmed" by itself (Codex review,
    # 12 Nov). audit.py's check (5) also compares the inlined definitions with numbers.tex.
    nt = os.path.join(HERE, "numbers.tex")
    macros = {n: printed(v) for n, v in DEF.findall(open(nt, encoding="utf-8").read() if os.path.exists(nt) else raw)}
    sgn = set(re.findall(r"\\sgn\{([^}]*)\}", src))
    lay = set(re.findall(r"\\lay\{([^}]*)\}", src))
    global SHAS
    SHAS = re.findall(r"\\sha\{([0-9a-fA-F]+)\}", src)  # file and commit hashes: identifiers, not numbers
    return macros, sgn, lay


SHAS = []


def check(tex, body, allow_entries):
    problems, notes = [], []
    macros, sgn, lay = source_sets(tex)
    flat = re.sub(r"\s+", " ", body)
    # ---- A: every macro value prints ----
    series = {n for n, v in macros.items() if "(" in v}
    for n in sorted(series):
        notes.append("series macro \\%s not checked in the rendered text (drawn as coordinates)" % n)
    for n, v in sorted(macros.items()):
        if n in series:
            continue
        if v not in flat:
            problems.append("A: macro \\%s = %r is not in the PDF text" % (n, v))
    # ---- B: every numeric token is explained ----
    explained = set()
    for v in macros.values():
        explained |= {m.group(0).replace(",", "") for m in NUM.finditer(v)}
    for e in allow_entries:
        explained |= {m.group(0).replace(",", "").replace("{,}", "") for m in NUM.finditer(e["text"].replace("{,}", ","))}
    explained |= {s.replace(",", "") for s in sgn} | {s.replace(",", "") for s in lay}
    structural = re.compile(
        r"^\s*(?:\d+(?:\.\d+)*)\s+[A-Z]"            # a numbered heading: "4.3 Regime 1"
        r"|^\s*(?:Table|Figure)\s+\d+:"             # a caption number
        r"|\[\d+(?:,\s*\d+)*(?:,\s*pp?\.\s*[\d\-,\s]+)?\]"  # a citation bracket with optional pages
        r"|(?:Table|Tables|Figure|Figures|Section|§|Appendix)\s*~?\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?"  # a cross-reference or range
        r"|^\s*\d{1,2}\s*$"                         # a page number on its own line
        r"|^\s*\d{1,2}\.\s+[A-Z]"                   # a numbered list item "9. Structure, not meaning."
        r"|Attribution 4\.0 International \(CC BY 4\.0\)|©\s*\d{4}|\(\d{4}\)"  # template licence line, cite years
        r"|Research Conference \d{4}|\d{4}, 1-1\. https://doi\.org/0+/0+"      # the template's first-page header
        r"|^\s*[A-Z]\.\d+\s"                        # an appendix table number "B.6"
        , re.M)
    masked = structural.sub(lambda m: " " * len(m.group(0)), body)
    for h in SHAS:  # a \sha{...} hash prints split over lines (seqsplit): mask it with any whitespace between chars
        masked = re.sub(r"\s*".join(map(re.escape, h)), lambda m: " " * len(m.group(0)), masked)
    for m in NUM.finditer(masked):
        tok = m.group(0).replace(",", "")
        if tok in explained:
            continue
        ctx = re.sub(r"\s+", " ", body[max(0, m.start() - 45):m.end() + 35])
        problems.append("B: number %r in the PDF text is not a macro value, allow-listed, a sign code or layout "
                        "constant: '...%s...'" % (m.group(0), ctx))
    return problems, notes


def main(argv):
    import allowlist
    if argv and argv[0] == "--text":
        tex, body = argv[1], open(argv[2], encoding="utf-8").read()
    else:
        tex, body = argv[0], pdf_body(argv[1])
    problems, notes = check(tex, body, allowlist.ENTRIES)
    for n in notes:
        print("  NOTE ", n)
    for p in problems:
        print("  FAIL ", p)
    print("rendered check: %d problem(s): %s" % (len(problems), "CLEAN" if not problems else "FAIL"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
