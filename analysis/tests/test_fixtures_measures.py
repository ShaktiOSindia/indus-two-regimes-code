"""Spec section 10 synthetic fixtures for the measures (part 2). Every expected value is computed BY HAND in the comment
beside it (written 6 Nov 2026 before running the measures on the corpus).
"""
import math
import os
import sys
import unittest
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import spec_lib as S  # noqa: E402
import spec_lib_measures as M  # noqa: E402
import spec_lib_protocols as P  # noqa: E402


def k(tok):
    return ("", ((tok,),), "")


class TestWholeText(unittest.TestCase):
    def test_tie_at_the_tenth_key(self):
        # 14 texts, 11 keys: '100' x3, '050' x2, nine singletons '001'..'009'; '009' comes FIRST in file order.
        # Top-10 = 100, 050, then the singletons by serialization ascending: 001..008 (009 excluded, although first).
        keys = [k("009")] + [k("100")] * 3 + [k("050")] * 2 + [k("%03d" % i) for i in range(1, 9)]
        top = [S.serialize(x) for x, _ in M.top_keys(keys)]
        self.assertEqual(top, ["|100|", "|050|"] + ["|%03d|" % i for i in range(1, 9)])
        self.assertAlmostEqual(M.coverage(keys), 100.0 * 13 / 14, places=12)        # (3 + 2 + 8) / 14
        self.assertAlmostEqual(M.repeat_share(keys), 100.0 * 5 / 14, places=12)     # 3 + 2 texts repeat

    def test_fewer_than_ten_keys(self):
        keys = [k("001"), k("001"), k("002")]                                       # min(10, 2 keys)
        self.assertEqual(len(M.top_keys(keys)), 2)
        self.assertAlmostEqual(M.coverage(keys), 100.0, places=12)

    def test_percentile_index(self):
        g = list(range(200))                     # floor(0.05 * 199) = 9; floor(0.95 * 199) = floor(189.05) = 189
        self.assertEqual((S.pctl(g, 0.05), S.pctl(g, 0.95)), (9, 189))


class TestEntropy(unittest.TestCase):
    def test_h3_by_hand(self):
        runs = [list("abc"), list("abd"), list("abc"), list("xy"), list("pqrs")]
        # trigrams abc x2, abd x1, pqr x1, qrs x1: N = 5; contexts ab 3, pq 1, qr 1; K_tri = 4, K_ctx = 3
        # H3 = -(0.4 log2(2/3) + 0.2 log2(1/3) + 0.2 log2(1) + 0.2 log2(1)) = 0.5509775004326937
        h = M.h3(runs)
        self.assertEqual((h["n_tri"], h["k_tri"], h["k_ctx"]), (5, 4, 3))
        self.assertAlmostEqual(h["plugin"], -(0.4 * math.log2(2 / 3) + 0.2 * math.log2(1 / 3)), places=12)
        self.assertAlmostEqual(h["plugin"], 0.5509775004326937, places=12)
        # MM = H3 + (4 - 3) / (2 * 5 * ln 2) = 0.5509775004326937 + 0.14426950408889633
        self.assertAlmostEqual(h["mm"], 0.5509775004326937 + 0.14426950408889633, places=12)
        self.assertAlmostEqual(h["ktri_over_n"], 80.0, places=12)

    def test_h3_empty_is_na(self):
        self.assertIsNone(M.h3([list("ab")])["plugin"])

    def test_token_overshoot(self):
        rows = [NS(index=i, runs=[list("abcdefg")]) for i in range(3)]   # each text: 7 signs -> 5 trigram tokens
        self.assertEqual([len(M.take_until(rows, T)[0]) for T in (7, 10, 11)], [2, 2, 3])
        self.assertEqual(M.take_until(rows, 7)[1], 10)                     # the crossing text is kept: 10 >= 7

    def test_positional_entropy_by_hand(self):
        # a, a, b, c: H = 0.5 + 0.25 * 2 + 0.25 * 2 = 1.5; MM = 1.5 + (3 - 1) / (2 * 4 * ln 2) = 1.8606737602222408
        e = P.entropy_mm(["a", "a", "b", "c"])
        self.assertAlmostEqual(e["plugin"], 1.5, places=12)
        self.assertAlmostEqual(e["mm"], 1.5 + 2 / (8 * math.log(2)), places=12)
        self.assertEqual((e["N"], e["K"]), (4, 3))


class TestDraws(unittest.TestCase):
    def test_fold_split_unequal_groups(self):
        g3, g1a, g1b, g1c = ["a", "b", "c"], ["d"], ["e"], ["f"]          # 6 texts; half = 3
        self.assertEqual([len(x) for x in M.fold_split([g3, g1a, g1b, g1c], 6)], [3, 3])
        self.assertEqual([len(x) for x in M.fold_split([g1a, g3, g1b, g1c], 6)], [4, 2])
        self.assertEqual([len(x) for x in M.fold_split([g1a, g1b, g1c, g3], 6)], [3, 3])

    def test_cluster_drawn_twice_appears_twice(self):
        c0, c1 = ["r1", "r2"], ["r3"]
        self.assertEqual(M.concat([c0, c0]), ["r1", "r2", "r1", "r2"])
        self.assertEqual(M.concat([c1, c0]), ["r3", "r1", "r2"])

    def test_matched_n_equal_sizes_uses_no_draw(self):
        rows_t = [NS(index=i, key=k("001")) for i in range(5)]
        rows_s = [NS(index=10 + i, key=k("%03d" % i)) for i in range(5)]
        m = M.matched_n(rows_t, rows_s, M.MEASURES["cov10"], draws=3)
        self.assertEqual((m["mean"], m["p5"], m["p95"], m["n"]), (0.0, 0.0, 0.0, 5))   # 100 - 100 (5 keys <= 10)

    def test_matched_n_subsamples_only_the_larger_class(self):
        rows_t = [NS(index=i, key=k("001")) for i in range(8)]                         # coverage 100 at any size
        rows_s = [NS(index=10 + i, key=k("%03d" % i)) for i in range(4)]
        m = M.matched_n(rows_t, rows_s, M.MEASURES["cov10"], draws=4)
        self.assertEqual(m["n"], 4)
        self.assertEqual((m["mean"], m["p5"], m["p95"]), (0.0, 0.0, 0.0))


class TestCurve(unittest.TestCase):
    def test_spec_curve_points(self):
        self.assertEqual(P.spec_curve_points(list(range(21))), [float(x) for x in range(21)])
        pts = P.spec_curve_points([0.0, 10.0, 20.0])          # p = 0.25 -> pos 0.5 -> 5; p = 0.5 -> pos 1 -> 10
        self.assertEqual((pts[0], pts[5], pts[10], pts[20]), (0.0, 5.0, 10.0, 20.0))


class TestProtocols(unittest.TestCase):
    def test_bprime_outcomes(self):
        met, notmet, untested = {"tested": True, "criterion_met": True}, {"tested": True, "criterion_met": False}, \
            {"tested": False}
        self.assertEqual(P.bprime_outcome(met, met), "H")
        self.assertEqual(P.bprime_outcome(met, notmet), "P")
        self.assertEqual(P.bprime_outcome(met, untested), "P")
        self.assertEqual(P.bprime_outcome(notmet, met), "F")
        self.assertEqual(P.bprime_outcome(notmet, notmet), "F")
        self.assertEqual(P.bprime_outcome(untested, untested), "C")

    def test_ebuds_filter_order(self):
        # same key twice: the FIRST copy (row 0) is incomplete, the second (row 1) complete; filters in the listed
        # order (complete first, then one copy per key) keep row 1; deduplicating first would keep nothing.
        def fake(i, complete, key, n=2):
            return NS(index=i, analyzable=True, complete=complete, single_line=True, key=key, n_legible=n)
        rows = [fake(0, False, k("001")), fake(1, True, k("001")), fake(2, True, k("002"), n=15)]
        self.assertEqual([r.index for r in P.ebuds_like(rows)], [1])          # row 2 fails length 1-14

    def test_key_without_000(self):
        self.assertEqual(P.key_without_000(("+", (("000", "740"), ("033",)), "]")), ("+", (("740",), ("033",)), "]"))

    def test_g2_other_tokens_by_hand(self):
        # two eligible texts, reading order: [740, 033, 740] (final 740) and [520, 740] (final 740 too)
        # all legible tokens 5, of which 740: 3 -> 60%; finals 2 of 2 -> 100%; others [740, 033] + [520] -> 1 of 3
        def fake(seq):
            return NS(n_legible=len(seq), final_eligible=True, final_sign=seq[-1], legible_reading=seq)
        g = P.g2_enrichment([fake(["740", "033", "740"]), fake(["520", "740"])])
        self.assertEqual(g["texts"], 2)
        self.assertAlmostEqual(g["share_all_tokens"], 60.0, places=12)
        self.assertAlmostEqual(g["share_final"], 100.0, places=12)
        self.assertAlmostEqual(g["share_other"], 100.0 / 3, places=12)
        self.assertAlmostEqual(g["enrichment"], 3.0, places=12)


if __name__ == "__main__":
    unittest.main()
