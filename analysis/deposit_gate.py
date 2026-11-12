"""Deposit gate: the shipped files must be exactly those listed in SHA256SUMS.txt, each equal to its entry: none
missing, none changed, none added (the inputs and outputs a reader creates are ignored: data/, out/, out_any_input/,
work/, __pycache__/, and the two Gemini output files). This replaces the private repository's git gate (tag, blob ids,
clean tree). What it can and cannot establish: it detects any accidental or local change to the shipped code before a
run; it cannot authenticate the manifest itself (anyone who edits files can edit the manifest). The authentic version
is the tagged commit whose ID the paper prints: a git commit ID fixes every byte of every file, the manifest included.
Standard library only; run_core.py and run_full.py call it before importing any analysis module."""
import hashlib
import os
import sys

IGNORED_DIRS = {".git", "__pycache__", "data", "out", "out_any_input", "work"}
IGNORED_FILES = {"SHA256SUMS.txt", "output.json", "output_v2.json"}


def check(root):
    manifest = os.path.join(root, "SHA256SUMS.txt")
    if not os.path.exists(manifest):
        sys.exit("GATE: SHA256SUMS.txt is missing at the deposit root; the run stops")
    bad, listed = [], set()
    with open(manifest, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            digest, rel = line.rstrip("\n").split("  ", 1)
            listed.add(rel)
            p = os.path.join(root, rel)
            if not os.path.exists(p):
                bad.append("missing: " + rel)
            elif hashlib.sha256(open(p, "rb").read()).hexdigest() != digest:
                bad.append("changed: " + rel)
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in IGNORED_DIRS]
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), root).replace(os.sep, "/")
            if fn not in IGNORED_FILES and rel not in listed:
                bad.append("not in the manifest: " + rel)
    if bad:
        sys.exit("GATE: the deposit differs from its manifest; the run stops:\n  " + "\n  ".join(bad))
