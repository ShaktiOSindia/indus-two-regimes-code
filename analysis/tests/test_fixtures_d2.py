"""Spec section 12, deviation D2 (7 Nov 2026): fixtures written BEFORE the code (tests first). Expected values are
worked by hand in the comment beside each, or (class TestDataD2) are the values assurance V3 measured with its own
script (`profile/paper_t10/assurance_v3/v3_measure_findings_output.txt`) and the spec's own statements.
"""
import json
import os
import random
import sys
import unittest
from types import SimpleNamespace as NS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import spec_lib as S  # noqa: E402
import spec_lib_measures as M  # noqa: E402
import spec_lib_protocols as P  # noqa: E402
import spec_lib_s13a as A  # noqa: E402
import spec_lib_s13b as B  # noqa: E402


def row(i, site="H", typ="TAB:I", text="t1", fs=("H", "A"), fs2=("H", "A", "", ""), complete=True, n=2, **kw):
    base = dict(index=i, site=site, type=typ, text=text, findspot=fs, findspot_d2b=fs2, analyzable=True,
                complete=complete, n_legible=n, key=("", ((text,),), ""), single_line=True, bus_without_slash=False,
                final_eligible=True, initial_eligible=True, final_sign="740", initial_sign="001", runs=[[text]],
                room_grid="", depth="", area="A")
    base.update(kw)
    return NS(**base)


class TestCopyKeys(unittest.TestCase):
    def test_copy_key_each_variant(self):
        r = row(7)
        self.assertEqual(S.copy_key(r, "D0"), ("row", 7))
        self.assertEqual(S.copy_key(r, "D1"), ("H", "TAB:I", "t1"))
        self.assertEqual(S.copy_key(r, "D2a"), ("H", "TAB:I", "t1", ("H", "A")))
        self.assertEqual(S.copy_key(r, "D2b"), ("H", "TAB:I", "t1", ("H", "A", "", "")))

    def test_d1_key_separates_sites_and_types(self):
        # same text at another site, and as another type: three different D1 keys -> nothing removed
        rows = [row(0), row(1, site="M"), row(2, typ="SEAL:S")]
        self.assertEqual([r.index for r in S.dedupe(rows, "D1")], [0, 1, 2])

    def test_dedupe_keeps_smallest_index_whatever_the_input_order(self):
        # rows given as 5, 2, 9; 5 and 2 share a D1 key -> keep 2 (smallest index); output in row-index order
        rows = [row(5), row(2), row(9, text="t2")]
        self.assertEqual([r.index for r in S.dedupe(rows, "D1")], [2, 9])

    def test_d2a_keeps_one_copy_per_findspot(self):
        rows = [row(0), row(1), row(2, fs=("H", "B"))]
        self.assertEqual([r.index for r in S.dedupe(rows, "D2a")], [0, 2])   # 0 and 1 share find-spot A
        self.assertEqual([r.index for r in S.dedupe(rows, "D1")], [0])       # D1 ignores the find-spot
        self.assertEqual([r.index for r in S.dedupe(rows, "D0")], [0, 1, 2])


class TestCopyRuleInSelector(unittest.TestCase):
    def test_population_first_then_one_copy(self):
        # row 0 incomplete, row 1 complete, same D1 key. Population 'complete' first -> row 1 survives;
        # one copy first would keep row 0 and then lose it to the population filter.
        rows = [row(0, complete=False), row(1)]
        with M.copy_rule("D1"):
            self.assertEqual([r.index for r in M.class_rows(rows, "TAB:I", "complete")], [1])
            self.assertEqual([r.index for r in M.class_rows(rows, "TAB:I", "all")], [0])

    def test_d0_is_the_default_and_identity(self):
        rows = [row(0), row(1)]
        self.assertEqual(M.COPY_RULE, "D0")
        self.assertEqual([r.index for r in M.class_rows(rows, "TAB:I", "all")], [0, 1])

    def test_rule_restored_after_exit_and_on_error(self):
        with M.copy_rule("D1"):
            self.assertEqual(M.COPY_RULE, "D1")
        self.assertEqual(M.COPY_RULE, "D0")
        with self.assertRaises(RuntimeError):
            with M.copy_rule("D2a"):
                raise RuntimeError("x")
        self.assertEqual(M.COPY_RULE, "D0")

    def test_copy_false_leaves_copies_for_the_caller(self):
        rows = [row(0), row(1)]
        with M.copy_rule("D1"):
            self.assertEqual([r.index for r in M.class_rows(rows, "TAB:I", "all", copy=False)], [0, 1])
            self.assertEqual([r.index for r in M.apply_copy_rule(rows)], [0])
        self.assertEqual([r.index for r in M.apply_copy_rule(rows)], [0, 1])          # D0 outside

    def test_unknown_rule_rejected(self):
        with self.assertRaises(ValueError):
            with M.copy_rule("D9"):
                pass


class TestCopyGroupSafety(unittest.TestCase):
    def test_group_mixing_a_post_selector_attribute_stops_the_run(self):
        # same D1 key, but one copy is a BUS row without '/': a filter after the selector would see a different
        # copy depending on the order -> the run must stop
        rows = [row(0, bus_without_slash=True, runs=None), row(1)]
        with self.assertRaises(ValueError):
            S.check_copy_groups(rows, "D1")

    def test_unmixed_groups_pass(self):
        S.check_copy_groups([row(0), row(1), row(2, text="t2", final_eligible=False)], "D1")


class TestDrawRecorder(unittest.TestCase):
    def calls(self, g):
        a = g.sample(list(range(100)), 5)
        b = g.choices(["a", "b", "c"], [1, 2, 3], k=4)
        c = g.choice(list(range(9)))
        d = list(range(12))
        g.shuffle(d)
        e = g.random()
        return a, b, c, d, e

    def test_same_draws_as_random_Random(self):
        self.assertEqual(self.calls(S.DrawRecorder(42)), self.calls(random.Random(42)))

    def test_fingerprint_repeatable_and_sensitive(self):
        g1, g2, g3 = S.DrawRecorder(42), S.DrawRecorder(42), S.DrawRecorder(42)
        self.calls(g1)
        self.calls(g2)
        g3.sample(list(range(100)), 6)                       # a different draw
        self.assertEqual(g1.hexdigest(), g2.hexdigest())
        self.assertNotEqual(g1.hexdigest(), g3.hexdigest())

    def test_each_method_is_hashed_on_its_own(self):
        # two generators that differ ONLY in one draw of one method must fingerprint differently (pins each method)
        draws = {"sample": (lambda g: g.sample(list(range(100)), 5), lambda g: g.sample(list(range(100)), 6)),
                 "choices": (lambda g: g.choices("abc", k=3), lambda g: g.choices("abc", k=4)),
                 "choice": (lambda g: g.choice(list(range(9))), lambda g: g.choice(list(range(10, 19)))),
                 "shuffle": (lambda g: g.shuffle(list(range(12))), lambda g: g.shuffle(list(range(13)))),
                 "random": (lambda g: g.random(), lambda g: [g.random(), g.random()])}
        for name, (a, b) in draws.items():
            g1, g2 = S.DrawRecorder(42), S.DrawRecorder(42)
            a(g1)
            b(g2)
            self.assertNotEqual(g1.hexdigest(), g2.hexdigest(), name)
            self.assertNotEqual(g1.hexdigest(), S.DrawRecorder(42).hexdigest(), name + " recorded nothing")

    def test_rows_recorded_by_index(self):
        # two different lists of rows with the same indexes draw the same and fingerprint the same
        g1, g2 = S.DrawRecorder(42), S.DrawRecorder(42)
        g1.sample([NS(index=i, x=1) for i in range(20)], 3)
        g2.sample([NS(index=i, x=2) for i in range(20)], 3)
        self.assertEqual(g1.hexdigest(), g2.hexdigest())

    def test_scopes_name_generators_in_creation_order(self):
        S.reset_fingerprints()
        with S.fp_scope("x"):
            S.new_rng().random()
            S.new_rng().random()
        with S.fp_scope("y"):
            S.new_rng().random()
        self.assertEqual(sorted(S.fingerprints()), ["x#1", "x#2", "y#1"])
        S.reset_fingerprints()

    def test_new_rng_uses_the_spec_seed(self):
        self.assertEqual(S.new_rng().random(), random.Random(S.SEED).random())
        S.reset_fingerprints()


class TestSmallItems(unittest.TestCase):
    def test_frac_positive(self):
        self.assertEqual(P.frac_positive([1.0, -1.0, 0.0, 2.0]), 50.0)      # 2 of 4 strictly positive

    def test_m342_share_over_eligible_texts(self):
        # A: eligible, final 740, tokens [001, 740]; B: NOT eligible, tokens [740, 740]
        # rate = 1/1 = 100%; share over ELIGIBLE texts = 1/2 = 50% -> concentration 2.0
        # (the old reading, share over all multi-sign texts = 3/4 = 75%, would give 1.333)
        a = row(0, stored_lines=[["001", "740"]], final_eligible=True, final_sign="740")
        b = row(1, text="t2", stored_lines=[["740", "740"]], final_eligible=False, final_sign=None)
        m = A.m342([a, b])
        self.assertAlmostEqual(m["rate_740_final"], 100.0, places=12)
        self.assertAlmostEqual(m["token_share_740"], 50.0, places=12)
        self.assertAlmostEqual(m["concentration"], 2.0, places=12)

    def test_holdout_reports_in_sample_p5_p95(self):
        # G1, 12 seals with 12 DIFFERENT texts: each fold has 6 texts and 6 keys, so the top-10 covers the whole fold:
        # in-sample coverage 100% in every draw (in_p5 = in_p95 = 100), out-of-sample 0% (no key shared)
        tab = [row(i, text="t%d" % (i % 3)) for i in range(12)]
        seal = [row(100 + i, typ="SEAL:S", text="s%d" % i) for i in range(12)]
        h = M.holdout(tab, seal, "G1", draws=20)
        self.assertEqual((h["SEAL:S"]["in_p5"], h["SEAL:S"]["in_p95"]), (100.0, 100.0))
        self.assertEqual((h["SEAL:S"]["out_p5"], h["SEAL:S"]["out_p95"]), (0.0, 0.0))
        self.assertLessEqual(h["TAB:I"]["in_p5"], h["TAB:I"]["in_p95"])

    def test_bprime_copy_rule_comes_after_the_cell(self):
        # two copies of one tablet text at Harappa Mound F: row 0 in Stratum IV (cell IV), row 1 in Stratum V (cell
        # V-VII). The cell is part of B''s population, so under D1 each cell keeps its own copy (1 and 1); one copy
        # BEFORE the cell would keep only row 0 and leave V-VII empty.
        rows = [row(0, site="Harappa", area="FTrench I", phase="Stratum IV"),
                row(1, site="Harappa", area="FTrench I", phase="Stratum V")]
        with M.copy_rule("D1"):
            b = P.bprime(rows, "primary")
        self.assertEqual((b["V-VII"]["n_tab_all"], b["IV"]["n_tab_all"]), (1, 1))

    def test_table2_sensitivity_copy_rule_comes_after_the_direction_filter(self):
        # same D1 key: row 0 has no direction ('-'), row 1 is R/L. The R/L-L/R row filters first, then one copy:
        # it keeps row 1. One copy first would keep row 0 and then lose it to the direction filter.
        rows = [row(0, dir="-"), row(1, dir="R/L")]
        with M.copy_rule("D1"):
            t2 = P.table2_samples(rows)
        self.assertEqual([r.index for r in t2["sensitivity_rl_lr"]], [1])
        self.assertEqual([r.index for r in t2["full"]], [0])

    def test_g3_all_texts_variant_includes_incomplete(self):
        def seal(i, complete):
            return NS(complete=complete, n_legible=3, final_eligible=True, initial_eligible=True, initial_sign="001",
                      final_sign="740", reading_lines=[["001", "002", "740"]])
        rows = [seal(0, True), seal(1, False)]
        self.assertEqual(P.g3_positional(rows)["n"], 1)                       # complete only (the entry)
        self.assertEqual(P.g3_positional(rows, complete_only=False)["n"], 2)   # all texts beside

    def test_d2b_fill_rates(self):
        rows = [row(0, room_grid="-X0/00", depth="-99.9 ft"), row(1, room_grid="", depth="-"),
                row(2, typ="SEAL:S", room_grid="?", depth="3 ft")]
        f = P.d2b_fill(rows)
        self.assertEqual(f["TAB:I"], {"rows": 2, "room_grid_filled": 1, "room_grid_pct": 50.0, "depth_filled": 1,
                                      "depth_pct": 50.0})
        self.assertEqual(f["SEAL:S"]["room_grid_filled"], 0)                  # '?' is MISSING (spec 0)
        self.assertEqual(f["SEAL:S"]["depth_filled"], 1)

    def test_distinct_seal_sites_over_all_analyzable_texts(self):
        rows = [row(0, typ="SEAL:S", site="X"), row(1, typ="SEAL:S", site="Y", complete=False),
                row(2, typ="SEAL:S", site="Z", n=1), row(3, typ="TAB:I", site="W")]
        self.assertEqual(B.distinct_seal_sites(rows), 3)                       # X, Y (incomplete), Z (one sign)


if __name__ == "__main__":
    unittest.main()
