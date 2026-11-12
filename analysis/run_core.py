"""Confirmation run, core part (roadmap C3): spec sections 0-8, 13.7's seal measures and B' (Amendment 1), written
under the same JSON keys as the independent implementation (`submission/GEMINI_INDEPENDENT_IMPL_PROMPT.md`).

Gate first (`submission/FREEZE_RECORD.md`): the frozen files equal the tag; their blob ids equal the record; the input
SHA-256 equals the pin (checked by load_rows); and the library itself has no uncommitted change, so every output
traces to one commit. Outputs (byte-identical across runs, nothing time-dependent inside):
  out/core_output.json   the numbers;   out/core_fingerprints.json   draw fingerprints (spec 0);
  out/exclusions.json    spec 11.       Run metadata (time, commit) goes to out/core_meta.json, not hashed.
Run: py -3.11 -I submission/scripts_v2/run_core.py
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deposit_gate  # noqa: E402  (deposit: the manifest is checked BEFORE any analysis module loads)
deposit_gate.check(os.path.dirname(HERE))
import spec_lib as S  # noqa: E402
import spec_lib_measures as M  # noqa: E402
import spec_lib_protocols as P  # noqa: E402

TAG = "spec-frozen-2026-11-11-d3-r1"   # deviation D3 (approved 11 Nov 03:07); before: -d2 (7 Nov 14:52), -d1, -06
FROZEN = {  # path -> blob id at the tag (from submission/FREEZE_RECORD.md)
    "submission/SPEC_decision2_DRAFT.md": "bce2fa3e5adfe4bd900d05d84fbe935aa845daf1",
    "submission/PREREG_chronology_Bprime_DRAFT.md": "a71368ff802cf500ddf5a920ccc1308f46fc6498",
    "submission/PREREG_chronology.md": "7318b8b92a1fd1f77fa910a5c190e7b81acec77b",
    "submission/PREREG_R2-2_slot_null.md": "7f338841289754ed86e6a9a7690c187b6548ba32",
    "submission/PREREG_corrections.md": "a09c19787ce608f0960027b69554fd44d074ccfc",
    "profile/paper_t10/gemini_review1/area_values_ending_dash.txt": "db83b0155b51cdd5785343d1ff6b00c4d4d7431f",
    "profile/fuls_2026-11-01/decision1_direction_tests.py": "c7ba86112200801b6f56c78e6df03057d7c4660b",
    "profile/paper_t10/scope_check/SCOPE_FINAL.md": "d3ac072e3464e408837cf4d22e8ac89e0f3b0168",
}
CLASSES, POPS, VARIANTS = (M.TAB, M.SEAL), ("complete", "all"), ("D0", "D1", "D2a", "D2b")


def git(*args):
    return subprocess.run(["git", *args], cwd=S.ROOT, capture_output=True, text=True)


def gate():
    """Deposit: the private repository's gate (git tag, blob ids, clean tree) is replaced by the manifest
    check: every shipped file must equal its SHA256SUMS.txt entry. No computation changes."""
    import deposit_gate
    deposit_gate.check(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    gate()
    in_path, in_pin, out_folder, note = S.input_mode(sys.argv[1:])   # spec 12 D3; default = the pinned file
    rows = S.load_rows(in_path, in_pin)                          # stops unless the input SHA-256 equals the pin
    out, fps = {}, {}

    # A. counts (spec 1, 3, 11)
    an = [r for r in rows if r.analyzable]
    out["rows_total"] = len(rows)
    out["malformed_ids"] = [r.id for r in rows if r.malformed]
    out["analyzable_rows"] = len(an)
    out["no_legible_sign_rows"] = sum(1 for r in rows if not r.malformed and r.n_legible == 0)
    by_type = {}
    for r in an:
        by_type[r.type] = by_type.get(r.type, 0) + 1
    out["analyzable_by_type"] = by_type
    out["bus_without_slash_rows"] = sum(1 for r in an if r.bus_without_slash)
    for c in CLASSES:
        for pop in POPS:
            out["multisign.%s.%s" % (c, pop)] = len(M.whole_text_rows(rows, c, pop))

    # B. whole-text measures (spec 2, 3, 6, 7)
    for c in CLASSES:
        for pop in POPS:
            base = M.whole_text_rows(rows, c, pop)
            for v in VARIANTS:
                sel = S.dedupe(base, v)
                keys = [r.key for r in sel]
                out["n.%s.%s.%s" % (c, pop, v)] = len(sel)
                out["cov10.%s.%s.%s" % (c, pop, v)] = M.coverage(keys)
                out["top10keys.%s.%s.%s" % (c, pop, v)] = [S.serialize(k) for k, _ in M.top_keys(keys)]
                out["repeat_share.%s.%s.%s" % (c, pop, v)] = M.repeat_share(keys)
            o = M.object_rows(base)
            out["object_top10_share.%s.%s" % (c, pop)] = o["a_share_objects_with_top10"]
            out["object_identity.%s.%s" % (c, pop)] = o["b"]

    # C. draw-based measures (spec 7), D0
    for pop in POPS:
        t, s = M.whole_text_rows(rows, M.TAB, pop), M.whole_text_rows(rows, M.SEAL, pop)
        for name in ("cov10", "repeat_share"):
            m = M.matched_n(t, s, M.MEASURES[name])
            fps["matched_n.%s.%s" % (name, pop)] = m.pop("fingerprint")
            out["matched_n.%s.%s" % (name, pop)] = m
            f = M.findspot_interval(t, s, M.MEASURES[name])
            fps["findspot_interval.%s.%s" % (name, pop)] = f.pop("fingerprint")
            out["findspot_interval.%s.%s" % (name, pop)] = f
        et, es = M.entropy_rows(rows, M.TAB, pop), M.entropy_rows(rows, M.SEAL, pop)
        out["h3.%s.%s" % (M.TAB, pop)] = M.h3(M.runs_of(et))
        out["h3.%s.%s" % (M.SEAL, pop)] = M.h3(M.runs_of(es))
        e = M.entropy_matched(et, es)
        fps["entropy_matched.%s" % pop] = e.pop("fingerprint")
        out["entropy_matched.%s" % pop] = e
        for g in ("G3", "G1", "G2"):
            h = M.holdout(t, s, g)
            fps["holdout.%s.%s" % (g, pop)] = h.pop("fingerprint")
            for c in CLASSES:
                out["holdout.%s.%s.%s" % (g, c, pop)] = h[c]
        out["synthetic_negative.%s" % pop] = M.synthetic_negative(rows, t, s)

    # D. first and last signs (spec 5): primary population, every copy, single-line (eligibility in the row)
    for c in CLASSES:
        for pop in POPS:
            out["final740.%s.%s" % (c, pop)] = M.final740(M.class_rows(rows, c, pop))

    # E. published-work protocols (spec 8) and the curve points (13.21)
    t2 = P.table2_samples(rows)
    out["table2_n"] = {k: len(v) for k, v in t2.items()}
    out["yadav2013"] = P.yadav2013(rows)
    gr = P.grid(rows)
    out["grid"] = gr
    out["spec_curve_points"] = P.spec_curve_points([c["gap"] for c in gr["cells"]])

    # F. seal measures (13.7); the complete-text row selects "complete" FIRST (spec 12 D2(c); same rows under D0)
    for pop in POPS:
        out["g2.%s" % pop] = P.g2_enrichment(M.class_rows(rows, M.SEAL, pop))
    out["g3"] = P.g3_positional(M.class_rows(rows, M.SEAL, "complete"))
    out["g3_all_texts"] = P.g3_positional(M.class_rows(rows, M.SEAL, "all"), complete_only=False)     # D2(j)

    # G. B' (Amendment 1)
    for var in ("primary", "sensitivity"):
        b = P.bprime(rows, var)
        out["bprime.%s.outcome" % var] = b.pop("outcome")
        for k, v in b.pop("fingerprints").items():                                       # D2(b)
            fps["bprime.%s.%s" % (var, k)] = v
        for cell, res in b.items():
            out["bprime.%s.%s" % (var, cell)] = res

    # H. file facts (spec 12 D2(f), (i))
    out["d2b_fill"] = P.d2b_fill(rows)
    out["data_facts"] = P.data_facts(rows)

    # I. Fuls's rule D1 for every measure, and D2a beside the headline whole-text figures (spec 12 D2(c), (d)):
    # separate files under the D0 keys, so the D0 files keep their bytes
    variants = {v: variant_pass(rows, v) for v in ("D1", "D2a")}

    # spec 11: exclusions
    excl = {"malformed": [r.id for r in rows if r.malformed],
            "no_legible_sign": [r.id for r in rows if not r.malformed and r.n_legible == 0],
            "fewer_than_2_legible_for_whole_text": [r.id for r in an if r.n_legible < 2],
            "bus_without_slash_for_pair_triple": [r.id for r in an if r.bus_without_slash],
            "multiline_or_bus_for_first_last": [r.id for r in an if not r.single_line]}

    od = os.path.join(HERE, out_folder)
    os.makedirs(od, exist_ok=True)
    files = [("core_output.json", out), ("core_fingerprints.json", fps), ("exclusions.json", excl)]
    for v, (ov, fv) in variants.items():
        files += [("core_output_%s.json" % v, ov), ("core_fingerprints_%s.json" % v, fv)]
    for name, obj in files:
        if note and isinstance(obj, dict):                       # any-input mode only: every output labelled
            obj = dict(obj, _any_input_note=note)
        with open(os.path.join(od, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(obj, sort_keys=True, indent=1) + "\n")
    meta = {"finished": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "commit": git("rev-parse", "HEAD").stdout.strip(), "python": sys.version.split()[0], "tag": TAG}
    with open(os.path.join(od, "core_meta.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(meta, sort_keys=True, indent=1) + "\n")
    print("written: out/core_output.json, core_fingerprints.json, exclusions.json, core_output_D1/D2a.json, "
          "core_fingerprints_D1/D2a.json (+ core_meta.json)")


def variant_pass(rows, v):
    """Spec 12 D2(c) (D1: every measure except the listed exceptions) and D2(d) (D2a: matched-N, find-spot interval,
    hold-out, synthetic negative, grid). The copy rule is applied inside the population selector, after its filters;
    the run stops first if any copy group mixes an attribute that a later filter uses (S.check_copy_groups)."""
    S.check_copy_groups(rows, v)
    out, fps = {}, {}
    with M.copy_rule(v):
        for pop in POPS:
            t, s = M.whole_text_rows(rows, M.TAB, pop), M.whole_text_rows(rows, M.SEAL, pop)
            for name in ("cov10", "repeat_share"):
                m = M.matched_n(t, s, M.MEASURES[name])
                fps["matched_n.%s.%s" % (name, pop)] = m.pop("fingerprint")
                out["matched_n.%s.%s" % (name, pop)] = m
                f = M.findspot_interval(t, s, M.MEASURES[name])
                fps["findspot_interval.%s.%s" % (name, pop)] = f.pop("fingerprint")
                out["findspot_interval.%s.%s" % (name, pop)] = f
            for g in ("G3", "G1", "G2"):
                h = M.holdout(t, s, g)
                fps["holdout.%s.%s" % (g, pop)] = h.pop("fingerprint")
                for c in CLASSES:
                    out["holdout.%s.%s.%s" % (g, c, pop)] = h[c]
            out["synthetic_negative.%s" % pop] = M.synthetic_negative(rows, t, s)   # pooled weights (D2(c))
        gr = P.grid(rows)
        out["grid"] = gr
        if v == "D1":
            for pop in POPS:
                et, es = M.entropy_rows(rows, M.TAB, pop), M.entropy_rows(rows, M.SEAL, pop)
                out["h3.%s.%s" % (M.TAB, pop)] = M.h3(M.runs_of(et))
                out["h3.%s.%s" % (M.SEAL, pop)] = M.h3(M.runs_of(es))
                e = M.entropy_matched(et, es)
                fps["entropy_matched.%s" % pop] = e.pop("fingerprint")
                out["entropy_matched.%s" % pop] = e
                for c in CLASSES:
                    out["final740.%s.%s" % (c, pop)] = M.final740(M.class_rows(rows, c, pop))
                    base = M.whole_text_rows(rows, c, pop)
                    o = M.object_rows(base)
                    out["object_top10_share.%s.%s" % (c, pop)] = o["a_share_objects_with_top10"]
                    out["object_identity.%s.%s" % (c, pop)] = o["b"]
                out["g2.%s" % pop] = P.g2_enrichment(M.class_rows(rows, M.SEAL, pop))
            t2 = P.table2_samples(rows)
            out["table2_n"] = {k: len(t2[k]) for k in ("full", "sensitivity_rl_lr")}   # EBUDS-like: own rule
            out["yadav2013"] = P.yadav2013(rows)
            out["g3"] = P.g3_positional(M.class_rows(rows, M.SEAL, "complete"))
            out["g3_all_texts"] = P.g3_positional(M.class_rows(rows, M.SEAL, "all"), complete_only=False)
            for var in ("primary", "sensitivity"):
                b = P.bprime(rows, var)
                out["bprime.%s.outcome" % var] = b.pop("outcome")
                for k, x in b.pop("fingerprints").items():
                    fps["bprime.%s.%s" % (var, k)] = x
                for cell, res in b.items():
                    out["bprime.%s.%s" % (var, cell)] = res
    out["copy_rule"] = v
    return out, fps


if __name__ == "__main__":
    main()
