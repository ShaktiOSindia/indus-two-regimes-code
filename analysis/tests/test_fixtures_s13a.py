"""Hand-computed fixtures for section 13 entries 13.1, 13.2, 13.5, 13.15 (written 6 Nov 2026 before running them on
the corpus). Expected values are worked out in the comments.
"""
import os
import random
import sys
import unittest
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import spec_lib_s13a as A  # noqa: E402


def text(tokens, ini=None, fin=None):
    leg = [t for t in tokens if t not in ("000", "999")]
    return NS(stored_lines=[list(tokens)], n_legible=len(leg), initial_eligible=ini is not None, initial_sign=ini,
              final_eligible=fin is not None, final_sign=fin)


class TestTable2(unittest.TestCase):
    def test_top_shares_by_hand(self):
        # tokens 740, 001 | 740, 002, (000) | 003: legible 5, 740 twice -> top sign share 2/5 = 40%
        rows = [text(["740", "001"], ini="001", fin="740"), text(["740", "002", "000"], fin="740"),
                text(["003"], ini="003", fin="003")]
        m = A.table2_metrics(rows)
        self.assertAlmostEqual(m["top_sign_share"], 40.0, places=12)
        self.assertAlmostEqual(m["top69_coverage"], 100.0, places=12)
        self.assertEqual((m["eligible_starters"], m["eligible_enders"]), (2, 3))
        self.assertAlmostEqual(m["mean_legible_length"], 5 / 3, places=12)      # (2 + 2 + 1) / 3

    def test_enders_top23_of_25(self):
        rows = [text(["%03d" % i], fin="%03d" % i) for i in range(1, 26)]       # 25 distinct final signs
        m = A.table2_metrics(rows)
        self.assertAlmostEqual(m["enders_top23"], 92.0, places=12)             # 23 / 25
        self.assertIsNone(m["starters_top82"])                                  # no eligible start
        self.assertAlmostEqual(m["top_sign_share"], 4.0, places=12)            # 1 / 25

    def test_m342_by_hand(self):
        # multi-sign: A (740 033, final 740), B (740 001, final 001), C (740 740 002, not eligible); D one-sign excluded
        # rate 1 of 2 eligible = 50%. Reading 12 REVISED (spec 12 D2(e), 7 Nov): the token share is over the ELIGIBLE
        # texts A and B: 740 tokens 1 + 1 = 2 of 4 = 50%; ratio 1.0. (The 6 Nov reading, over A, B, C: 4 of 7 =
        # 57.142857%, ratio 0.875, is the value this fixture held before the revision.)
        rows = [text(["033", "740"], fin="740"), text(["001", "740"], fin="001"), text(["002", "740", "740"]),
                text(["740"], fin="740")]
        m = A.m342(rows)
        self.assertEqual((m["multisign_texts"], m["eligible"]), (3, 2))
        self.assertAlmostEqual(m["rate_740_final"], 50.0, places=12)
        self.assertAlmostEqual(m["token_share_740"], 50.0, places=12)
        self.assertAlmostEqual(m["concentration"], 1.0, places=12)


class TestTable3Null(unittest.TestCase):
    def test_h1_by_hand(self):
        self.assertAlmostEqual(A.h1([text(["a", "a", "b", "c"])]), 1.5, places=12)

    def test_singleton_share_by_hand(self):
        # trigrams abc, abd, abe, xyz, uvw; contexts ab x3, xy x1, uv x1: two tokens have singleton contexts -> 2/5
        runs = [list("abc"), list("abd"), list("abe"), list("xyz"), list("uvw")]
        self.assertAlmostEqual(A.singleton_share(runs), 40.0, places=12)

    def test_null_p_by_hand(self):
        self.assertEqual(A.null_p(0, 50), 1 / 51)          # no shuffle at or below the observed H3
        self.assertEqual(A.null_p(9, 9), 1.0)

    def test_shuffle_keeps_each_run(self):
        rows = [NS(index=2, runs=[list("pqrs")]), NS(index=1, runs=[list("abc"), list("de")])]
        out = A.shuffled_runs(rows, random.Random(42))
        self.assertEqual([sorted(r) for r in out], [list("abc"), list("de"), list("pqrs")])   # row-index order

    def test_null_of_identical_signs(self):
        rows = [NS(index=i, runs=[["a", "a", "a"]]) for i in range(3)]          # H3 = 0 in every shuffle
        n = A.shuffle_null(rows, iters=50)
        self.assertEqual((n["observed"], n["null_mean"], n["null_min"]), (0.0, 0.0, 0.0))
        self.assertEqual(n["p"], 1.0)                                          # (1 + 50) / (1 + 50)
        self.assertEqual((n["reduction_pct"], n["templated"]), (0.0, False))


class TestSmall(unittest.TestCase):
    def test_two_sign_share(self):
        ka, kb, kc = ("", (("001", "002"),), ""), ("", (("001", "002", "003"),), ""), ("", (("004", "005"),), "")
        rows = ([NS(key=ka, n_legible=2)] * 3 + [NS(key=kb, n_legible=3)] * 2 + [NS(key=kc, n_legible=2)])
        s = A.two_sign_share(rows)                                             # A and C two-sign: 4 of 6 texts
        self.assertEqual((s["top10_two_sign_keys"], s["texts_two_sign"], s["texts_top10"]), (2, 4, 6))

    def test_shared_keys(self):
        def r(key, typ, n=2):
            return NS(key=key, type=typ, n_legible=n, analyzable=True)
        rows = [r("K1", "TAB:I"), r("K1", "SEAL:S"), r("K2", "TAB:I"), r("K2", "TAB:B"), r("K3", "TAB:I"),
                r("K4", "SEAL:S", 1), r("K4", "TAB:I", 1)]
        s = A.shared_keys(rows)
        self.assertEqual(s["multisign"], {"distinct_keys": 3, "keys_with_more_than_one_type": 2,
                                          "keys_in_both_TAB:I_and_SEAL:S": 1})
        self.assertEqual(s["any_length"], {"distinct_keys": 4, "keys_with_more_than_one_type": 3,
                                           "keys_in_both_TAB:I_and_SEAL:S": 2})


if __name__ == "__main__":
    unittest.main()
