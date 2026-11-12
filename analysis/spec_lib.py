"""The ONE shared library for the confirmation run (working rule 18). Implements the FROZEN measurement specification
`submission/SPEC_decision2_DRAFT.md` at tag `spec-frozen-2026-11-06` (record: `submission/FREEZE_RECORD.md`).
Standard library only; Python 3.11 (spec section 0). Every rule cites its spec section. Readings of the text where a
choice was needed are listed in `submission/scripts_v2/SPEC_READINGS.md`.

Part 1 (this file, first block): input (0), parsing and reading order (1), identity (2), runs (4), end eligibility
(5), find-spots and copy rules (6), objects (3), B' levels (PREREG_chronology Amendment 1).
"""
import contextlib
import csv
import hashlib
import io
import math
import os
import random
import re
from dataclasses import dataclass, field

# The repository root. INDUS_ROOT overrides it ONLY so the mutation harness can test scratch copies of this library
# against the real input (unset in every real run; the input's SHA-256 is checked either way).
ROOT = os.environ.get("INDUS_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # deposit: analysis/ sits one level below the root (two in the private tree)
PINNED = os.path.join(ROOT, "data", "input.csv")  # deposit: the reader places the file here; its SHA-256 must equal PINNED_SHA
PINNED_SHA = "c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98"      # spec 0
AREA_LIST = os.path.join(ROOT, "data", "area_values_ending_dash.txt")  # deposit: the private list is not shipped; the run derives the classification from the rows (classify_dash_areas)
SEED = 42                                                                               # spec 0
DRAWS = 200                                                                             # spec 0
MARKS = ("+", "[", "]")                                                                 # spec 1
TOKEN = re.compile(r"\d{3}")                                                            # spec 1
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}


# ------------------------------------------------------------------------- section 0 + 12 D2(b): draw fingerprints
def _ident(v):
    """How a drawn value enters a fingerprint: a row by its row index, anything else by repr."""
    i = getattr(v, "index", None)
    if isinstance(i, int):
        return "i%d" % i
    return repr(v)


class DrawRecorder(random.Random):
    """A random.Random with the SAME draws as random.Random(seed): getrandbits is defined here and only passes
    through, so Random.__init_subclass__ keeps the base class's _randbelow_with_getrandbits; the methods below call
    the base methods unchanged. Each public draw (sample, choices, choice, shuffle, random) is hashed in draw order
    (spec 12 D2(b)); draws made inside another draw (choices calls random) are not hashed twice."""

    def __init__(self, seed=None):
        self._fp = hashlib.sha256()
        self._depth = 0
        super().__init__(SEED if seed is None else seed)

    def getrandbits(self, k):
        return super().getrandbits(k)

    def _rec(self, tag, values):
        if self._depth == 0:
            self._fp.update((tag + "\x1e" + "\x1f".join(_ident(v) for v in values) + "\x1d").encode("utf-8"))

    def random(self):
        x = super().random()
        self._rec("r", [x])
        return x

    def sample(self, population, k, **kw):
        self._depth += 1
        try:
            out = super().sample(population, k, **kw)
        finally:
            self._depth -= 1
        self._rec("s", out)
        return out

    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        self._depth += 1
        try:
            out = super().choices(population, weights, cum_weights=cum_weights, k=k)
        finally:
            self._depth -= 1
        self._rec("c", out)
        return out

    def choice(self, seq):
        self._depth += 1
        try:
            out = super().choice(seq)
        finally:
            self._depth -= 1
        self._rec("o", [out])
        return out

    def shuffle(self, x):
        self._depth += 1
        try:
            super().shuffle(x)
        finally:
            self._depth -= 1
        self._rec("h", x)

    def hexdigest(self):
        return self._fp.hexdigest()


_FP, _FP_COUNT, _FP_SCOPE = {}, {}, ["root"]


@contextlib.contextmanager
def fp_scope(name):
    """Name the generators created inside: '<name>#1', '<name>#2', ... in creation order."""
    _FP_SCOPE.append(name)
    try:
        yield
    finally:
        _FP_SCOPE.pop()


def new_rng():
    """Spec 0: every reported quantity creates its OWN generator seeded with SEED; it is recorded (D2(b))."""
    name = _FP_SCOPE[-1]
    _FP_COUNT[name] = _FP_COUNT.get(name, 0) + 1
    g = DrawRecorder(SEED)
    _FP["%s#%d" % (name, _FP_COUNT[name])] = g
    return g


def fingerprints():
    return {k: g.hexdigest() for k, g in _FP.items()}


def reset_fingerprints():
    _FP.clear()
    _FP_COUNT.clear()


# ----------------------------------------------------------------------------------------------- section 0
def is_missing(value):
    """Spec 0: MISSING if, after removing leading/trailing whitespace and every '-', '?' and space, it is empty."""
    return value.strip().replace("-", "").replace("?", "").replace(" ", "") == ""


def pctl(sorted_values, q):
    """Spec 0: p5 = g[floor(0.05 (n - 1))], p95 = g[floor(0.95 (n - 1))], by exact index."""
    return sorted_values[math.floor(q * (len(sorted_values) - 1))]


def legible(tok):
    """Spec 1: 000 = eroded sign (not legible); 999 = blank (not a sign); any other token = a legible sign."""
    return tok not in ("000", "999")


# ----------------------------------------------------------------------------------------------- section 1
@dataclass
class Row:
    index: int
    id: str
    object_id: str
    cisi: str
    site: str
    type: str
    dir: str
    complete: bool
    area: str
    room_grid: str
    depth: str
    phase: str
    text: str
    left: str = ""
    right: str = ""
    stored_lines: list = field(default_factory=list)
    malformed: bool = False
    reading_lines: list = field(default_factory=list)
    key: tuple = None
    n_legible: int = 0
    single_line: bool = False
    bus_without_slash: bool = False
    analyzable: bool = False
    runs: list = None
    final_eligible: bool = False
    final_sign: str = None
    initial_eligible: bool = False
    initial_sign: str = None
    findspot: tuple = None
    findspot_d2b: tuple = None

    @property
    def legible_reading(self):
        """The legible signs in reading order, lines joined in reading order."""
        return [t for line in self.reading_lines for t in line if legible(t)]


def parse_text(text):
    """Spec 1: [left mark] core [right mark]; a mark is '+', '[' or ']' taken only as the first / last character.
    Returns (left, right, core, stored_lines, malformed). Stops the run on '+' inside the core (spec 1)."""
    t = text.strip()
    left = t[0] if t[:1] in MARKS else ""
    rest = t[len(left):]
    right = rest[-1] if rest[-1:] in MARKS else ""
    core = rest[:len(rest) - len(right)]
    if "+" in core:
        raise RuntimeError("spec 1: '+' inside a core (%r): the run stops" % text)
    lines = [line.split("-") for line in core.split("/")]
    malformed = any(not TOKEN.fullmatch(tok) for line in lines for tok in line)
    return left, right, core, lines, malformed


def serialize(key):
    """Spec 2, exactly: right + "|" + "/".join("-".join(line) for line in lines) + "|" + left."""
    right, lines, left = key
    return right + "|" + "/".join("-".join(line) for line in lines) + "|" + left


def build_row(index, rec):
    f = {k: (v or "").strip() for k, v in rec.items()}                  # spec 0: strip leading/trailing only
    r = Row(index=index, id=f["id"], object_id=f["id"].rpartition(".")[0], cisi=f["cisi"], site=f["site"],
            type=f["type"], dir=f["dir."], complete=(f["complete"] == "Y"), area=f["area-section"],
            room_grid=f["room-grid"], depth=f["depth"], phase=f["phase"], text=f["text"])
    r.left, r.right, core, r.stored_lines, r.malformed = parse_text(r.text)
    r.findspot, r.findspot_d2b = findspots(r)
    if r.malformed:
        return r
    # R1 (spec 1): a line in reading order is its stored tokens reversed; the lines are the stored lines reversed.
    r.reading_lines = [list(reversed(line)) for line in reversed(r.stored_lines)]
    # Identity key (spec 2): (stored right mark, reading-order lines with 999 removed and 000 kept, stored left mark).
    r.key = (r.right, tuple(tuple(t for t in line if t != "999") for line in r.reading_lines), r.left)
    r.n_legible = sum(1 for line in r.stored_lines for t in line if legible(t))
    r.analyzable = r.n_legible >= 1                                         # spec 1
    has_slash = "/" in core
    r.single_line = (not has_slash) and r.dir != "BUS"                      # spec 1
    r.bus_without_slash = r.dir == "BUS" and not has_slash                  # spec 1
    if not r.bus_without_slash:                                             # spec 1, 4
        r.runs = []
        for line in r.reading_lines:
            run = []
            for t in line:
                if legible(t):
                    run.append(t)
                else:
                    if run:
                        r.runs.append(run)
                    run = []
            if run:
                r.runs.append(run)
    if r.single_line:                                                       # spec 5
        line = r.reading_lines[0]
        if r.left == "+" and legible(line[-1]):       # reading END = stored LEFT end
            r.final_eligible, r.final_sign = True, line[-1]
        if r.right == "+" and legible(line[0]):       # reading START = stored RIGHT end
            r.initial_eligible, r.initial_sign = True, line[0]
    return r


ANY_INPUT_NOTE = ("any-input mode (spec 12 D3): computed on an input other than the pinned file; the numbers are "
                  "not expected to match the paper")


def input_mode(argv):
    """Spec 12 D3: (path, pin, output folder, note). Default: the pinned file, its SHA-256, 'out', no note. Only the
    explicit flag '--any-input PATH' selects another file, no hash check, a SEPARATE folder and a note."""
    if "--any-input" not in argv:
        return PINNED, PINNED_SHA, "out", None
    i = argv.index("--any-input")
    if i + 1 >= len(argv):
        raise SystemExit("--any-input needs a path to an ICIT-layout CSV")
    return argv[i + 1], None, "out_any_input", ANY_INPUT_NOTE


def load_rows(path=PINNED, pin=PINNED_SHA):
    """Spec 0: bytes; SHA-256 must EQUAL the pin, else stop; UTF-8 with the BOM removed; csv.DictReader; row index =
    0-based position in the file. Spec 12 D3: pin=None (any-input mode only) skips the hash check."""
    with open(path, "rb") as fh:
        raw = fh.read()
    got = hashlib.sha256(raw).hexdigest()
    if pin is not None and got != pin:
        raise RuntimeError("spec 0: input SHA-256 %s differs from the pin; the run stops" % got)
    text = raw.decode("utf-8")
    if text.startswith("﻿"):
        text = text[1:]
    return [build_row(i, rec) for i, rec in enumerate(csv.DictReader(io.StringIO(text, newline="")))]


def submitted_symbols(r):
    """REGRESSION ANCHOR ONLY (spec 10): the SUBMITTED extraction rules: lines joined in stored order, end marks
    dropped, 999 and 000 kept (empty tokens of a malformed code dropped). Never used by a measure."""
    return [t for line in r.stored_lines for t in line if t != ""]


def whole_text_key(r):
    """Spec 1-2: every analyzable row (BUS without '/' included) has its identity key for whole-text measures."""
    return r.key


# ----------------------------------------------------------------------------------------------- section 6
def findspot_unknown(area):
    """Spec 6: UNKNOWN if area-section is MISSING, or ends in '-' without naming a trench ("trench", any case)."""
    return is_missing(area) or (area.endswith("-") and "trench" not in area.lower())


def findspots(r):
    """Spec 6: (D2a find-spot, D2b find-spot). Unknown -> ("row", row index) for both."""
    if findspot_unknown(r.area):
        own = ("row", r.index)
        return own, own
    d2b = (r.site, r.area, "" if is_missing(r.room_grid) else r.room_grid, "" if is_missing(r.depth) else r.depth)
    return (r.site, r.area), d2b


def copy_key(r, variant):
    """Spec 6: D0 every copy; D1 (site, type, stored code string); D2a + find-spot; D2b + D2b find-spot."""
    if variant == "D0":
        return ("row", r.index)
    if variant == "D1":
        return (r.site, r.type, r.text)
    if variant == "D2a":
        return (r.site, r.type, r.text, r.findspot)
    if variant == "D2b":
        return (r.site, r.type, r.text, r.findspot_d2b)
    raise ValueError(variant)


def dedupe(rows, variant):
    """Spec 6: one copy per copy key; the copy kept is the row with the smallest row index; row-index order kept."""
    seen, out = set(), []
    for r in sorted(rows, key=lambda x: x.index):
        k = copy_key(r, variant)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


# Row attributes that filters apply AFTER the population selector (eligibility, BUS, length). If copies sharing a
# copy key differed in any of them, "one copy per key" before such a filter would depend on which copy is kept.
COPY_SAFE_ATTRS = ("bus_without_slash", "single_line", "runs", "final_eligible", "final_sign", "initial_eligible",
                   "initial_sign", "n_legible")


def check_copy_groups(rows, variant):
    """Spec 12 D2(c): stop unless every copy-key group of analyzable rows agrees on COPY_SAFE_ATTRS (then applying
    the copy rule at the end of the population selector equals applying it after every later filter)."""
    seen = {}
    for r in rows:
        if not r.analyzable:
            continue
        k = copy_key(r, variant)
        sig = tuple(repr(getattr(r, a, None)) for a in COPY_SAFE_ATTRS)
        if k in seen and seen[k][1] != sig:
            raise ValueError("copy group %r mixes post-selector attributes (rows %d and %d)" % (k, seen[k][0], r.index))
        seen.setdefault(k, (r.index, sig))


def classify_dash_areas(rows=None):
    """Spec 6 check: (site, area) pairs whose area ends in '-' and is not MISSING -> (known list, unknown list)."""
    rows = rows if rows is not None else load_rows()
    pairs = sorted({(r.site, r.area) for r in rows if r.area.endswith("-") and not is_missing(r.area)})
    known = [p for p in pairs if "trench" in p[1].lower()]
    unknown = [p for p in pairs if "trench" not in p[1].lower()]
    return known, unknown


def read_area_list_file(path=AREA_LIST):
    """The classified list that spec 6 makes part of the specification: lines 'KNOWN|UNKN | site | value | n rows'."""
    out = {"known": [], "unknown": []}
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 4 and parts[0] in ("KNOWN", "UNKN"):
            out["known" if parts[0] == "KNOWN" else "unknown"].append((parts[1], parts[2]))
    out["known"].sort()
    out["unknown"].sort()
    return out


# ----------------------------------------------------------------------------------------------- section 3
def object_key(side_keys):
    """Spec 3(b): object key = tuple(sorted(serialization(k) for k in side_keys)); duplicates kept."""
    return tuple(sorted(serialize(k) for k in side_keys))


# ------------------------------------------------------------------------------------ B' (Amendment 1, section 2)
def bprime_level(r, variant):
    """Amendment 1 s.2: Harappa Mound F (area-section starts with "F"); Vats stratum from `phase` ("Stratum I".."VII");
    only levels IV-VII enter a cell. Trench VI (area-section exactly "FTrench VI"): PRIMARY its Stratum III counts as
    IV; SENSITIVITY its III, IV, V count as IV, V, VI. Returns the level (4-7) or None."""
    if r.site != "Harappa" or not r.area.startswith("F"):
        return None
    m = re.fullmatch(r"Stratum (I|II|III|IV|V|VI|VII)", r.phase)
    if not m:
        return None
    n = ROMAN[m.group(1)]
    if r.area == "FTrench VI":
        if variant == "primary" and n == 3:
            n = 4
        elif variant == "sensitivity" and n in (3, 4, 5):
            n += 1
    return n if 4 <= n <= 7 else None


def bprime_cell(level):
    """Amendment 1 s.2: V-VII = levels 5-7; IV = level 4."""
    if level is None:
        return None
    return "V-VII" if level >= 5 else "IV"
