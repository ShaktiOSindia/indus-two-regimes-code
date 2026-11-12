"""Hand-computed fixtures for section 13 entries 13.16, 13.17, 13.18, 13.19 (written 6 Nov 2026 before running them on
the corpus). Expected values are worked out in the comments.
"""
import collections
import os
import random
import sys
import unittest
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import spec_lib_s13d as D  # noqa: E402


def key(*tokens, right="+", left="+"):
    return (right, (tuple(tokens),), left)


class TestProvenance(unittest.TestCase):
    def test_real_cisi_and_object_repeats(self):
        def r(cisi, obj, k, typ="TAB:I", n=2):
            toks = list(k[1][0])
            return NS(cisi=cisi, object_id=obj, key=k, type=typ, n_legible=n, analyzable=True, malformed=False,
                      stored_lines=[toks])
        rows = [r("H-12", "o1", key("001", "002")), r("?-3", "o1", key("001", "002")), r("-", "o1", key("003", "004")),
                r("Ns-38", "o2", key("001", "002"))]
        p = D.provenance(rows)
        self.assertEqual((p["P2"]["real_cisi_all_rows"], p["P2"]["real_cisi_analyzable"]), (2, 2))  # H-12, Ns-38
        # o1 carries three multi-sign TAB:I texts, two identical: one object repeating, one repeat; o2 has one text
        self.assertEqual((p["P7"]["tab_objects_with_more_than_one_multisign_text"],
                          p["P7"]["tab_objects_repeating_a_key"], p["P7"]["within_object_repeats"]), (1, 1, 1))
        self.assertAlmostEqual(p["P7"]["pct_on_multi_text_objects"], 75.0, places=12)               # 3 of 4


class TestSignIdentity(unittest.TestCase):
    def test_split_order_and_untouched_tokens(self):
        k = key("740", "000", "033", right="+", left="]")
        out = D.apply_split([k], {"740", "033"}, random.Random(1))[0]
        g = random.Random(1)                          # the same draws, in token order: 740 first, then 033
        exp = ("740" + ("a" if g.random() < 0.5 else "b"), "000", "033" + ("a" if g.random() < 0.5 else "b"))
        self.assertEqual(out, ("+", (exp,), "]"))

    def test_merge_mapping(self):
        m = D.merge_mapping(["001", "002", "003", "004"], 3, random.Random(5))
        self.assertEqual(len(m), 3)
        self.assertTrue(all(v != k for k, v in m.items()))

    def test_template_codes_ordering(self):
        tab = [key("033", "700")] * 3 + [key("034", "700")] * 2
        order, load = D.template_codes(tab, ["001", "033", "034", "700"])
        self.assertEqual((order, load), (["033", "700", "034", "001"], ["033", "700", "034"]))

    def test_template_codes_rest_by_frequency(self):
        # ten keys seen twice (signs 100-109) fill the top 10; signs only in the rarer keys: 202 x2, 201 x1, 203 x1
        tab = [key("1%02d" % i) for i in range(10)] * 2 + [key("201", "202"), key("202", "203")]
        vocab = sorted({"001"} | {"1%02d" % i for i in range(10)} | {"201", "202", "203"})
        order, load = D.template_codes(tab, vocab)
        self.assertEqual(order[10:], ["202", "201", "203", "001"])     # count descending, then code; then the rest

    def test_parent_and_marker(self):
        self.assertEqual(D.parent(key("740a", "033b", "000")), key("740", "033", "000"))
        seqs = [["033", "740a"], ["740b", "220", "740a"]]
        m = D.marker_stats(seqs, {"740a", "740b"})        # terminal 2/2; non-terminal 033, 740b, 220 -> 1/3
        self.assertAlmostEqual(m["terminal_pct"], 100.0, places=12)
        self.assertAlmostEqual(m["nonterminal_pct"], 100.0 / 3, places=12)
        self.assertAlmostEqual(m["enrichment"], 3.0, places=12)

    def test_rarest_first(self):
        self.assertEqual(D.rarest_first(collections.Counter({"b": 1, "a": 1, "c": 5, "d": 2})), ["a", "b", "d", "c"])


class TestStorage(unittest.TestCase):
    def test_storage_by_hand(self):
        # R/L: A = 740 001 002, B = 003 004 190; L/R: C = A as stored, D = B reversed
        texts = [("R/L", ["740", "001", "002"]), ("R/L", ["003", "004", "190"]),
                 ("L/R", ["740", "001", "002"]), ("L/R", ["190", "004", "003"])]
        t = D.storage_tests(texts)
        self.assertEqual(t["T1.L/R"], {"N": 2, "left": 1, "right": 0})
        self.assertEqual(t["T3"], {"N": 2, "same": 1, "reversed": 1})
        # bigrams: two of the four L/R pairs equal R/L pairs as stored, two equal reversed R/L pairs: 2/4 each
        self.assertAlmostEqual(t["T4"]["same"], 0.5, places=12)
        self.assertAlmostEqual(t["T4"]["reversed"], 0.5, places=12)
        m = D.storage_tests([(d, q[::-1] if d == "L/R" else q) for d, q in texts])
        self.assertEqual(m["T1.L/R"], {"N": 2, "left": 0, "right": 1})      # the self-test mutant flips T1

    def test_t3_asymmetric(self):
        # one L/R text equal to an R/L text only when reversed: same 0, reversed 1
        t = D.storage_tests([("R/L", ["740", "001", "002"]), ("L/R", ["002", "001", "740"])])
        self.assertEqual(t["T3"], {"N": 1, "same": 0, "reversed": 1})

    def test_direction_class(self):
        self.assertEqual(D.dclass(NS(dir="R/l")), "R/L")


if __name__ == "__main__":
    unittest.main()
