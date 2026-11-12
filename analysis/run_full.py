"""Confirmation run, section 13 part (roadmap C3, full): every other analysis the corrected paper keeps (spec 13.1-13.19;
13.7's G2/G3 and the 13.21 curve points are in the core output). Complete texts primary, all texts beside, wherever the
entry is a whole-text, pair/triple/entropy or first/last measure; corpus descriptions once.

Spec 12 D2 (7 Nov 2026): every generator is recorded under the output key that uses it (out/full_fingerprints.json);
Fuls's rule D1 for every entry except the listed exceptions (out/full_output_D1.json); D2a beside 13.9 [S4]'s
within-Harappa figures (out/full_output_D2a.json); each with its fingerprint file. The D0 file keeps its keys.

Gate first: the frozen files equal the tag (run_core's FREEZE_RECORD list); the input SHA-256 (load_rows); and NO
uncommitted change in any library file or in this script, so the outputs trace to one commit. Outputs are
byte-identical across runs (nothing time-dependent inside); run metadata in out/full_meta.json (not hashed).
Run: py -3.11 -I submission/scripts_v2/run_full.py
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deposit_gate  # noqa: E402  (deposit: the manifest is checked BEFORE any analysis module loads)
deposit_gate.check(os.path.dirname(HERE))
import spec_lib as S  # noqa: E402
import spec_lib_measures as M  # noqa: E402
import spec_lib_protocols as P  # noqa: E402
import spec_lib_s13a as A  # noqa: E402
import spec_lib_s13b as B  # noqa: E402
import spec_lib_s13c as C  # noqa: E402
import spec_lib_s13d as D  # noqa: E402
import run_core  # noqa: E402

POPS = ("complete", "all")
LIB = ["submission/scripts_v2/%s" % f for f in ("spec_lib.py", "spec_lib_measures.py", "spec_lib_protocols.py",
                                               "spec_lib_s13a.py", "spec_lib_s13b.py", "spec_lib_s13c.py",
                                               "spec_lib_s13d.py", "run_core.py", "run_full.py")]
# Spec 12 D2(c): not computed under D1 (corpus counts and descriptions; registered protocols; 13.10 tests duplicates)
D1_EXCEPTIONS = ("13.1.table1", "13.4.", "13.8.site_shares", "13.10.", "13.16", "13.19")


def gate():
    """Deposit: the private repository's gate (git tag, blob ids, clean tree) is replaced by the manifest
    check: every shipped file must equal its SHA256SUMS.txt entry. No computation changes."""
    import deposit_gate
    deposit_gate.check(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def stamp(msg):
    print("%s  %s" % (datetime.datetime.now().strftime("%H:%M:%S"), msg), flush=True)


def put(out, key, fn, *args):
    """Compute one output key with its generators recorded under that key (spec 12 D2(b))."""
    with S.fp_scope(key):
        out[key] = fn(*args)


def section13(rows, variant):
    """All of section 13 under the current copy rule. variant 'D0' = everything; 'D1' = everything except
    D1_EXCEPTIONS (the copy rule itself is set by the caller)."""
    out = {}
    an = [r for r in rows if r.analyzable]
    skip = (lambda key: variant == "D1" and key.startswith(D1_EXCEPTIONS))
    stamp("13.1 (%s)" % variant)
    if not skip("13.1.table1"):
        out["13.1.table1"] = {c: sum(1 for r in an if r.type == c) for c in A.FIVE}
    t2 = {k: A.table2_metrics(v) for k, v in P.table2_samples(rows).items()}
    if variant == "D1":
        t2.pop("ebuds_like")                                       # EBUDS-like keeps its own one-copy rule
    out["13.1.table2"] = t2
    out["13.1.m342"] = {"all": A.m342(M.apply_copy_rule(an)),   # copy rule after each population filter
                        "complete": A.m342(M.apply_copy_rule([r for r in an if r.complete])),
                        "sensitivity_rl_lr": A.m342(M.apply_copy_rule([r for r in an if r.dir in ("R/L", "L/R")]))}
    for pop in POPS:
        stamp("13.2 %s (%s)" % (pop, variant))
        put(out, "13.2.table3.%s" % pop, A.table3, rows, pop)
        for cls in A.FIVE:
            ent = M.entropy_rows(rows, cls, pop)
            put(out, "13.2.null.%s.%s" % (cls, pop), A.shuffle_null, ent, A.NULL_ITERS[cls])
            put(out, "13.2.singleton.%s.%s" % (cls, pop), A.singleton_report, ent)
        stamp("13.3-13.6 %s (%s)" % (pop, variant))
        put(out, "13.3.%s" % pop, B.tablet_templates, rows, pop)
        if not skip("13.4."):
            put(out, "13.4.%s" % pop, B.slot_test, rows, pop)
        put(out, "13.5.%s" % pop, A.two_sign_share, M.whole_text_rows(rows, M.TAB, pop))
        put(out, "13.6.%s" % pop, A.reuse_fixed_length, rows, pop)
        stamp("13.7-13.9 %s (%s)" % (pop, variant))
        put(out, "13.7.%s" % pop, B.seal_frame, rows, pop)
        put(out, "13.8.%s" % pop, B.geography, rows, pop)
        if variant == "D1":
            out["13.8.%s" % pop].pop("distinct_sites_with_SEAL:S")   # a corpus description (D2(a), (c))
        put(out, "13.9.%s" % pop, C.site_control, rows, pop)
        stamp("13.10-13.14 %s (%s)" % (pop, variant))
        if not skip("13.10."):
            put(out, "13.10.%s" % pop, C.duplicate_provenance, rows, pop)
        put(out, "13.11.%s" % pop, C.label_null, rows, pop)
        put(out, "13.12.%s" % pop, C.positive_control, rows, pop)
        put(out, "13.13.%s" % pop, C.class_prediction, rows, pop)
        put(out, "13.14.%s" % pop, A.mould, rows, pop)
        stamp("13.17-13.18 %s (%s)" % (pop, variant))
        put(out, "13.17.%s" % pop, D.sign_identity, rows, pop)
        put(out, "13.18.%s" % pop, D.fsw, rows, pop)
    stamp("13.8 shares, 13.15, 13.16, 13.19 (%s)" % variant)
    if not skip("13.8.site_shares"):
        out["13.8.site_shares"] = B.site_shares(rows)
    put(out, "13.15", A.shared_keys, rows)
    if not skip("13.16"):
        out["13.16"] = D.provenance(rows)
    if not skip("13.19"):
        put(out, "13.19", D.storage_test, rows)
    return out


NOTE = None  # spec 12 D3: set only in any-input mode; then every output is labelled


def write(od, name, obj):
    if NOTE and isinstance(obj, dict):
        obj = dict(obj, _any_input_note=NOTE)
    with open(os.path.join(od, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, sort_keys=True, indent=1) + "\n")


def main():
    gate()
    global NOTE
    in_path, in_pin, out_folder, NOTE = S.input_mode(sys.argv[1:])   # spec 12 D3; default = the pinned file
    rows = S.load_rows(in_path, in_pin)
    od = os.path.join(HERE, out_folder)
    os.makedirs(od, exist_ok=True)

    S.reset_fingerprints()
    out = section13(rows, "D0")
    write(od, "full_output.json", out)
    write(od, "full_fingerprints.json", S.fingerprints())

    S.check_copy_groups(rows, "D1")                                     # stops if a copy group mixes (D2(c))
    S.reset_fingerprints()
    with M.copy_rule("D1"):
        out1 = section13(rows, "D1")
    out1["copy_rule"] = "D1"
    write(od, "full_output_D1.json", out1)
    write(od, "full_fingerprints_D1.json", S.fingerprints())

    S.check_copy_groups(rows, "D2a")
    S.reset_fingerprints()
    stamp("13.9 [S4] (D2a)")
    out2 = {}
    with M.copy_rule("D2a"):
        for pop in POPS:
            with S.fp_scope("13.9.%s" % pop):
                s4 = C.site_control(rows, pop)["S4"]
            out2["13.9.%s" % pop] = {"S4": {k: s4[k] for k in ("within_Harappa_matched",
                                                                 "within_Harappa_findspot_interval")}}
    out2["copy_rule"] = "D2a"
    write(od, "full_output_D2a.json", out2)
    write(od, "full_fingerprints_D2a.json", S.fingerprints())

    meta = {"finished": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "commit": run_core.git("rev-parse", "HEAD").stdout.strip(), "python": sys.version.split()[0],
            "tag": run_core.TAG}
    write(od, "full_meta.json", meta)
    stamp("written: out/full_output.json, full_output_D1.json, full_output_D2a.json, and their fingerprint files "
          "(+ full_meta.json)")


if __name__ == "__main__":
    main()
