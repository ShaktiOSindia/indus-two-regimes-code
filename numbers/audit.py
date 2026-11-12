"""B3 part 2: the both-ways number audit on the LaTeX SOURCE of the camera-ready (design: DESIGN.md).

FAILS when:
  (1) a digit in the text is not (a) inside a generated number macro \\nName, (b) inside \\sgn{...} (an ICIT sign
      code), (c) inside \\ref/\\eqref/\\label/\\cite*/\\input/\\include/\\includegraphics/\\url/\\href/\\documentclass/
      \\usepackage/\\begin/\\end arguments or a length (12pt, 0.5\\textwidth, ...), or (d) part of an allow-list entry;
  (2) a \\nName macro is used but not in the registry, or registered but never used;
  (3) an allow-list entry is never matched (a stale entry);
  (4) numbers.tex differs from a fresh generation (make_numbers --check);
  (5) a number macro is DEFINED in an audited file (the packaged upload inlines numbers.tex) with a value that is
      not exactly numbers.tex's, or with a name numbers.tex does not define; or is redefined anywhere
      (\\renewcommand, \\def). Added 11 Nov 2026: a number planted in the inlined definitions of the review copy
      passed checks (1)-(4), which never read those definitions.
Comments (%...) are stripped first; the generated definitions block is then checked by (5) and skipped by (1).
Run: python -I -B submission/numbers/audit.py paper.tex [more.tex ...]   (exit 0 = clean)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ARG_CMDS = ("ref", "eqref", "autoref", "cref", "Cref", "label", "cite", "citep", "citet", "parencite", "textcite",
            "autocite", "citeauthor", "citeyear", "input", "include", "includegraphics", "url", "href",
            "documentclass", "usepackage", "begin", "end", "addbibresource", "bibliography", "pubyear", "pubvolume",
            "pagestart", "pageend", "paperorder", "doi", "author", "affiliation", "sgn", "lay", "sha", "newcommand", "renewcommand",
            "setcounter", "addtocounter", "hypersetup", "definecolor", "conferencename")
LENGTH = re.compile(r"-?\d*\.?\d+(pt|em|ex|cm|mm|in|bp|sp|pc|mu)\b|-?\d*\.?\d+\\(textwidth|linewidth|columnwidth|"
                    r"textheight|baselineskip|paperwidth)")  # unit ATTACHED: "39 in the corpus" is not a length
                                                              # (blind spot found 11 Nov by the old-tokeniser check)
MACRO_USE = re.compile(r"\\(n[A-Z][A-Za-z]*)(?![A-Za-z])")  # n + UPPERCASE: \newcommand, \node, \noindent are
                                                             # not number macros (bug found 11 Nov on the real paper)


def strip_comments(tex):
    out = []
    for line in tex.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[:m.start()] if m else line)
    return "\n".join(out)


def blank_args(tex):
    """Blank (with spaces, keeping offsets) the brace and bracket arguments of ARG_CMDS and every \\nName use."""
    chars = list(tex)
    for m in re.finditer(r"\\(%s)\*?" % "|".join(ARG_CMDS), tex):
        i = m.end()
        while i < len(tex) and tex[i] in "[{ ":
            if tex[i] == " ":
                i += 1
                continue
            close = "]" if tex[i] == "[" else "}"
            depth, j = 0, i
            while j < len(tex):
                if tex[j] == tex[i]:
                    depth += 1
                elif tex[j] == close:
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            for k in range(i, min(j + 1, len(tex))):
                if chars[k] != "\n":
                    chars[k] = " "
            i = j + 1
    for m in MACRO_USE.finditer(tex):
        for k in range(m.start(), m.end()):
            chars[k] = " "
    for m in LENGTH.finditer(tex):
        for k in range(m.start(), m.end()):
            chars[k] = " "
    return "".join(chars)


DEF_START = re.compile(r"\\newcommand\{\\(n[A-Z][A-Za-z]*)\}\{")
REDEF = re.compile(r"\\(renewcommand\*?\{\\|providecommand\*?\{\\|def\\|let\\|edef\\|gdef\\|xdef\\)(n[A-Z][A-Za-z]*)"
                   r"(?![A-Za-z])")


def parse_defs(tex):
    """[(name, value, line)] for every \\newcommand{\\nName}{value}; value read with balanced braces."""
    out = []
    for m in DEF_START.finditer(tex):
        depth, j = 1, m.end()
        while j < len(tex) and depth:
            if tex[j] == "{" and tex[j - 1] != "\\":
                depth += 1
            elif tex[j] == "}" and tex[j - 1] != "\\":
                depth -= 1
            j += 1
        out.append((m.group(1), tex[m.end():j - 1], tex.count("\n", 0, m.start()) + 1))
    return out


def numbers_tex_defs():
    with open(os.path.join(HERE, "numbers.tex"), encoding="utf-8") as fh:
        return {n: v for n, v, _ in parse_defs(strip_comments(fh.read()))}


def audit(tex_paths, registry_names, allow, numbers_check=True, defs=None):
    problems = []
    used_macros, used_allow = set(), set()
    if defs is None:
        defs = numbers_tex_defs()
    for path in tex_paths:
        raw = open(path, encoding="utf-8").read()
        tex = strip_comments(raw)
        base = os.path.basename(path)
        for name, value, line in parse_defs(tex):  # (5) inlined definitions must equal numbers.tex exactly
            if name not in defs:
                problems.append("%s:%d: \\%s is defined here but not in numbers.tex" % (base, line, name))
            elif value != defs[name]:
                problems.append("%s:%d: inlined \\%s = %r differs from numbers.tex %r" % (base, line, name, value,
                                                                                        defs[name]))
        for m in REDEF.finditer(tex):
            problems.append("%s:%d: number macro \\%s is redefined (%s)" % (base, tex.count("\n", 0, m.start()) + 1,
                                                                           m.group(2), m.group(1).rstrip("{\\")))
        tex = "\n".join(l for l in tex.split("\n") if not l.lstrip().startswith("\\newcommand{\\n"))
        used_macros |= set(MACRO_USE.findall(tex))
        work = blank_args(tex)
        for idx, entry in enumerate(allow):
            text = entry["text"]
            start = 0
            while True:
                k = tex.find(text, start)
                if k == -1:
                    break
                used_allow.add(idx)
                work = work[:k] + " " * len(text) + work[k + len(text):]
                start = k + len(text)
        for m in re.finditer(r"\d+", work):
            line = tex.count("\n", 0, m.start()) + 1
            ctx = tex[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            problems.append("%s:%d: hand-typed number %r in '...%s...'" % (os.path.basename(path), line, m.group(0), ctx))
    reg = set(registry_names)
    for n in sorted(used_macros - reg):
        problems.append("macro \\%s is used but not in the registry" % n)
    for n in sorted(reg - used_macros):
        problems.append("macro \\%s is registered but never used" % n)
    for idx, entry in enumerate(allow):
        if idx not in used_allow:
            problems.append("allow-list entry never matched (stale): %r" % entry["text"])
    if numbers_check:
        import make_numbers
        if make_numbers.main(["--check"]) != 0:
            problems.append("numbers.tex differs from a fresh generation")
    return problems


def main(argv):
    import allowlist
    import registry
    pdfs = [a for a in argv if a.lower().endswith(".pdf")]
    paths = [a for a in argv if not a.startswith("-") and not a.lower().endswith(".pdf")]
    if not paths:
        print(__doc__)
        return 2
    probs = audit(paths, [e["name"] for e in registry.ENTRIES], allowlist.ENTRIES)
    for pdf in pdfs:  # the RENDERED-text check (check_rendered.py, built 12 Nov 2026): on the compiled PDF
        import check_rendered
        rp, notes = check_rendered.check(paths[0], check_rendered.pdf_body(pdf), allowlist.ENTRIES)
        print("  rendered-text check of %s: %d series macro(s) drawn as coordinates (not checked), %d problem(s)"
              % (os.path.basename(pdf), len(notes), len(rp)))
        probs += ["rendered: " + p for p in rp]
    for p in probs:
        print("  FAIL ", p)
    print("audit: %d problem(s): %s" % (len(probs), "CLEAN" if not probs else "FAIL"))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
