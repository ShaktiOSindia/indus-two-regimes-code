"""Hand-computed fixtures for section 13 entries 13.9, 13.10, 13.11, 13.13 (written 6 Nov 2026 before running them on
the corpus). Expected values are worked out in the comments.
"""
import os
import random
import sys
import unittest
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import spec_lib_measures as M  # noqa: E402
import spec_lib_s13c as C  # noqa: E402


def k(tok):
    return ("", ((tok,),), "")


class TestSiteControl(unittest.TestCase):
    def test_detail_uses_the_same_draws_as_matched_n(self):
        rng = random.Random(7)
        t = [NS(index=i, key=k("%03d" % rng.randrange(25))) for i in range(40)]     # varied: coverage changes
        s = [NS(index=100 + i, key=k("%03d" % rng.randrange(30))) for i in range(25)]
        a = M.matched_n(t, s, M.MEASURES["cov10"], draws=50)
        b = C.matched_n_detail(t, s, M.MEASURES["cov10"], draws=50)
        self.assertEqual((a["mean"], a["p5"], a["p95"], a["n"]), (b["diff"]["mean"], b["diff"]["p5"],
                                                                  b["diff"]["p95"], b["n"]))
        self.assertEqual(b["seal"]["p5"], b["seal"]["p95"])     # the smaller class is used whole: one value


class TestDuplicates(unittest.TestCase):
    def test_collapse_by_hand(self):
        # same (type, key) at rows 1, 3, 4, 8: run from 1 takes 3 (3 - 1 <= 2); 4 - 1 = 3 starts a run; 8 starts one
        rows = [NS(index=i, type="TAB:I", key=k("001"), analyzable=True) for i in (1, 3, 4, 8)]
        rows.append(NS(index=2, type="TAB:I", key=k("002"), analyzable=True))
        kept, dropped = C.collapse(rows)
        self.assertEqual(([r.index for r in kept], dropped), ([1, 2, 4, 8], 1))

    def test_gaps_sort_first(self):
        self.assertEqual(C.gaps([20, 10, 12]), [2, 8])        # sorted 10, 12, 20

    def test_gaps_by_hand(self):
        # key L at rows 5, 30 (first: 5) then key K at 10, 12, 20: observed gaps [25] + [2, 8]
        rows = [NS(index=i, key=k("K")) for i in (10, 12, 20)] + [NS(index=i, key=k("L")) for i in (5, 30)] + \
            [NS(index=7, key=k("M"))]
        d = C.duplicate_gaps(rows, draws=10)
        self.assertEqual((d["repeated_keys"], d["repeat_pairs"], d["median_gap_observed"]), (2, 3, 8))
        self.assertAlmostEqual(d["share_gap_le2_observed"], 100.0 / 3, places=12)


class TestLabelNull(unittest.TestCase):
    def test_assign_whole_units(self):
        u3, u1, u2 = ["a", "b", "c"], ["d"], ["e", "f"]
        self.assertEqual([len(x) for x in C.assign_units([u3, u1, u2], 3)], [3, 3])
        self.assertEqual([len(x) for x in C.assign_units([u1, u2, u3], 3)], [3, 3])
        self.assertEqual([len(x) for x in C.assign_units([u1, u3, u2], 3)], [4, 2])   # the crossing unit is kept

    def test_p_by_hand(self):
        self.assertEqual(C.perm_p_ge(0, 1000), 1 / 1001)


class TestPrediction(unittest.TestCase):
    def test_rules_by_hand(self):
        rules = ({k("A"), k("B")}, {k("B"), k("C")}, "740", 2)

        def r(key, n=2, fin=None):
            return NS(key=k(key), n_legible=n, final_eligible=fin is not None, final_sign=fin)
        self.assertTrue(C.predict_tablet(r("A"), rules))                  # rule 1
        self.assertFalse(C.predict_tablet(r("C"), rules))                 # rule 2
        self.assertFalse(C.predict_tablet(r("B", fin="740"), rules))      # rule 3 (in both; ends in the marker)
        self.assertTrue(C.predict_tablet(r("D", 2, "520"), rules))        # rule 4: length 2 <= median 2
        self.assertFalse(C.predict_tablet(r("D", 3, "520"), rules))       # rule 4: length 3 > median 2
        not_eligible = NS(key=k("B"), n_legible=2, final_eligible=False, final_sign="740")
        self.assertTrue(C.predict_tablet(not_eligible, rules))            # rule 3 needs an ELIGIBLE end -> rule 4

    def test_learn_rules_ties_and_median(self):
        tab = [NS(key=k("T%d" % i), n_legible=n) for i, n in enumerate((2, 3, 4, 5))]
        seal = [NS(key=k("S%d" % i), final_eligible=True, final_sign=f) for i, f in enumerate(("740", "520", "740",
                                                                                                   "520"))]
        tset, sset, marker, med = C.learn_rules(tab, seal)
        self.assertEqual((marker, med), ("520", 4))          # tie 2-2 -> code ascending; sorted [2,3,4,5][4 // 2]


if __name__ == "__main__":
    unittest.main()
