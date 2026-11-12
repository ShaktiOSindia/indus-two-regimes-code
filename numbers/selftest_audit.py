"""Self-test of audit.py on synthetic documents (scratch files only). Each plant must FAIL for its own reason;
the control must PASS. Run: python -I -B submission/numbers/selftest_audit.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit as A  # noqa: E402

REG = ["nCovTab", "nCovSeal"]
ALLOW = [{"text": "since 1940", "reason": "YEAR-IN-PROSE"}]

CONTROL = r"""\documentclass[final]{anthology-ch}
\usepackage{graphicx}
\newcommand{\nCovTab}{50.9}% generated
\begin{document}
\begin{abstract}Tablets reach \nCovTab\% against \nCovSeal\%.\end{abstract}
\section{Intro}\label{sec:1}
As shown in Table~\ref{tab:2} and by \textcite{vats1940}, sign \sgn{740} ends seals; excavated since 1940.
% a comment with 123 is ignored
\begin{table}[h]\caption{Coverage \nCovTab\%}\label{tab:2}
\begin{tabular}{p{0.3\textwidth}l} a & \nCovSeal \\ \end{tabular}\end{table}
\footnote{See \cite[p.~12]{fuls2023}.}
\begin{tikzpicture}[x=1.4cm, line width=0.8pt]\draw (\nCovTab,\lay{0}) -- (\lay{0},\nCovSeal);
\node at (\lay{1},\lay{2}) {x};\end{tikzpicture}
\newcommand{\sgnx}[1]{#1}\noindent\newline \definecolor{tabcol}{HTML}{1F5C99} \conferencename{Conference 2027}
\end{document}
"""

PLANTS = [
    ("body sentence", "ends seals;", "ends 35% of seals;", "hand-typed number '35'"),
    ("table cell", r"a & \nCovSeal", "a & 3.4", "hand-typed number '3'"),
    ("caption", r"\caption{Coverage \nCovTab\%}", r"\caption{Coverage 50.9\%}", "hand-typed number '50'"),
    ("abstract", r"against \nCovSeal\%", r"against 3.4\%", "hand-typed number '3'"),
    ("footnote", r"\footnote{See", r"\footnote{In 94 cases see", "hand-typed number '94'"),
    ("TikZ coordinate", r"(\nCovTab,\lay{0})", r"(50.9,\lay{0})", "hand-typed number '50'"),
    ("bare TikZ layout zero", r"(\lay{0},\nCovSeal)", r"(0,\nCovSeal)", "hand-typed number '0'"),
    ("thousands with LaTeX comma", "ends seals;", "ends 5{,}679 seals;", "hand-typed number '5'"),
    ("negative in math", "ends seals;", "ends $-3$ seals;", "hand-typed number '3'"),
    ("number before the word 'in'", "ends seals;", "ends 39 in the corpus;", "hand-typed number '39'"),
    ("decimal before 'pt' as a word", "ends seals;", "ends 4.5 pt of seals;", "hand-typed number '4'"),
    ("unregistered macro", r"Tablets reach \nCovTab", r"Tablets reach \nCovTabX \nCovTab", "not in the registry"),
    ("registered macro never used", None, None, "registered but never used"),
    ("stale allow-list entry", "since 1940", "since then", "never matched (stale)"),
    # (5), added 11 Nov 2026 after a number planted in the review copy's inlined definitions passed the audit
    ("inlined definition changed", r"\newcommand{\nCovTab}{50.9}", r"\newcommand{\nCovTab}{52.9}",
     "differs from numbers.tex"),
    ("inlined definition not in numbers.tex", r"\newcommand{\nCovTab}{50.9}",
     r"\newcommand{\nCovTab}{50.9}\newcommand{\nCovZed}{1}", "not in numbers.tex"),
    ("renewcommand override", r"\begin{document}", r"\renewcommand{\nCovSeal}{9.9}\begin{document}",
     "is redefined"),
    ("def override", r"\begin{document}", r"\def\nCovSeal{9.9}\begin{document}", "is redefined"),
]


DEFS = {"nCovTab": "50.9"}  # stands in for numbers.tex


def run(doc, reg=REG, allow=ALLOW):
    fd, p = tempfile.mkstemp(suffix=".tex", prefix="audit_selftest_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    try:
        return A.audit([p], reg, allow, numbers_check=False, defs=DEFS)
    finally:
        os.remove(p)


results = []
probs = run(CONTROL)
results.append(("control: clean synthetic document", not probs, "; ".join(probs)[:150] or "no problems"))
for label, old, new, reason in PLANTS:
    if old is None:
        probs = run(CONTROL, reg=REG + ["nUnusedMacro"])
    else:
        assert CONTROL.count(old) == 1, label
        probs = run(CONTROL.replace(old, new, 1))
    ok = any(reason in p for p in probs)
    results.append(("plant: " + label, ok, (probs[0] if probs else "did NOT fail")[:150]))

bad = [r for r in results if not r[1]]
for label, ok, msg in results:
    print("%-36s %s  %s" % (label, "OK  " if ok else "FAIL", msg))
print("selftest_audit: %d checks, %d failed: %s" % (len(results), len(bad), "PASS" if not bad else "FAIL"))
sys.exit(1 if bad else 0)
