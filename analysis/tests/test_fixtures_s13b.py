"""Hand-computed fixtures for section 13 entries 13.3, 13.4, 13.7 (script 07 parts) and 13.8 (written 6 Nov 2026
before running them on the corpus). Expected values are worked out in the comments.
"""
import math
import os
import sys
import unittest
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import spec_lib_s13b as B  # noqa: E402


def row(typ, reading, runs=None, complete=True, single=True, key=None, fin=None, ini=None, site="X"):
    leg = [t for t in reading if t not in ("000", "999")]
    return NS(type=typ, analyzable=True, n_legible=len(leg), legible_reading=leg, complete=complete,
              single_line=single, runs=runs, key=key or ("+", (tuple(reading),), "+"), final_eligible=fin is not None,
              final_sign=fin, initial_eligible=ini is not None, initial_sign=ini, site=site, reading_lines=[reading])


class TestSlot(unittest.TestCase):
    def test_exact_expectation_by_enumeration(self):
        # T1 = (032, x), T2 = (y, 033): 4 equally likely column arrangements, two of which put 032 and 033 together
        # -> E[T] = (0 + 1 + 1 + 0) / 4 * ... = 0.5 texts; a length-1 text adds nothing
        seqs = [["032", "x"], ["y", "033"], ["034"]]
        self.assertAlmostEqual(B.exact_ET(seqs), 0.5, places=12)
        self.assertEqual(B.slot_T(seqs), 0)
        r = B.slot_null(seqs, draws=4000)                     # must not raise: Monte Carlo agrees within 3 se
        self.assertAlmostEqual(r["E_exact"], 0.5, places=12)
        self.assertTrue(0.4 < r["mc_mean"] < 0.6)
        self.assertEqual(r["T_obs"], 0)

    def test_family_member_then_700(self):
        # 034-700 and 033-700 are the family; 700-032 (the reverse order) is not: 2 of 3 multi-sign texts
        rows = [row("TAB:I", ["034", "700"], runs=[["034", "700"]]), row("TAB:I", ["033", "700"], runs=[["033", "700"]]),
                row("TAB:I", ["700", "032"], runs=[["700", "032"]])]
        d = B.slot_description(rows, "all")
        self.assertEqual(d["family_member_then_700"], 2)
        self.assertAlmostEqual(d["family_pct_of_multisign"], 200.0 / 3, places=12)

    def test_perm_p_by_hand(self):
        self.assertEqual(B.perm_p(0, 10000), 1 / 10001)          # no draw at or below the observed value
        self.assertEqual(B.perm_p(4, 9), 0.5)                      # (1 + 4) / (1 + 9)

    def test_length_one_texts_carried_unchanged(self):
        # registered: length-1 texts are not shuffled, so adding two of them must leave every draw unchanged
        base = [["032", "x"], ["y", "033"], ["033", "z"]]
        a = B.slot_null(base, draws=300)
        b = B.slot_null(base + [["034"], ["032"]], draws=300)
        self.assertEqual((a["mc_mean"], a["p"]), (b["mc_mean"], b["p"]))

    def test_terminal_preceders(self):
        # 700 ends three tablets; preceded by 034 and 033; the 000 in the second text blocks its pair -> 2 of 3
        rows = [row("TAB:I", ["034", "700"], runs=[["034", "700"]], fin="700"),
                row("TAB:I", ["033", "000", "700"], runs=[["033"], ["700"]], fin="700"),
                row("TAB:I", ["033", "700"], runs=[["033", "700"]], fin="700")]
        t = B.tablet_templates(rows, "all")["B_terminals"]["top4"][0]
        self.assertEqual((t["terminal"], t["texts"]), ("700", 3))
        self.assertEqual(t["preceders_top5"], [["033", 1], ["034", 1]])
        self.assertAlmostEqual(t["top5_cover_pct"], 200.0 / 3, places=12)

    def test_independence_expectation(self):
        # n032 = 2, n033 = 2, n034 = 1, N = 4: 2*2/4 + 2*1/4 + 2*1/4 = 2.0
        seqs = [["032", "700"], ["033", "700"], ["032", "033"], ["034"]]
        self.assertAlmostEqual(B.independence_expectation(seqs), 2.0, places=12)
        self.assertEqual(B.slot_T(seqs), 1)

    def test_slot_description(self):
        rows = [row("TAB:I", ["034", "700"], runs=[["034", "700"]]),
                row("TAB:I", ["033", "000", "700"], runs=[["033"], ["700"]]),     # 000 breaks the pair
                row("TAB:I", ["700", "032"], runs=[["700", "032"]]),
                row("TAB:I", ["032", "033", "220"], runs=[["032", "033", "220"]])]
        d = B.slot_description(rows, "all")
        self.assertEqual(d["members_present"], {"1": 3, "2": 1})
        self.assertEqual(d["position_when_present"], {"initial": 3, "medial": 1, "terminal": 1})
        self.assertEqual(d["right_neighbours_top4"], [["033", 1], ["220", 1], ["700", 1]])   # ties by code
        self.assertAlmostEqual(d["pct_followed_by_700"], 100.0 / 3, places=12)
        self.assertEqual((d["family_member_then_700"], d["family_pct_of_multisign"]), (1, 25.0))


class TestSealAndGeography(unittest.TestCase):
    def test_stems(self):
        def s(reading, fin):
            return row("SEAL:S", reading, fin=fin)
        rows = [s(["001", "740"], "740"), s(["001", "740"], "740"), s(["002", "740"], "740"), s(["003", "520"], "520")]
        c = B.seal_frame(rows, "all")["C_terminals"]
        self.assertEqual(c["eligible"], 4)
        top = c["top3"][0]                                    # 740: 3 texts, stems (001) x2, (002) x1
        self.assertEqual((top["terminal"], top["texts"], top["distinct_stems"]), ("740", 3, 2))
        self.assertAlmostEqual(top["distinct_stems_pct"], 200.0 / 3, places=12)
        self.assertAlmostEqual(top["stems_once_pct"], 100.0 / 3, places=12)

    def test_seal_length_profile_counts_one_sign_seals(self):
        # deviation D1: [07-A] over ALL seals: lengths 1, 2, 3 -> mean 2.0 (multi-sign only would give 2.5)
        rows = [row("SEAL:S", ["740"], fin="740"), row("SEAL:S", ["001", "740"], fin="740"),
                row("SEAL:S", ["001", "002", "740"], fin="740")]
        f = B.seal_frame(rows, "all")
        self.assertEqual(f["A_length_profile"], {"1": 1, "2": 1, "3": 1})
        self.assertAlmostEqual(f["A_mean_legible_length"], 2.0, places=12)

    def test_site_bar_of_30(self):
        rows = ([row("SEAL:S", ["001", "740"], fin="740", site="A")] * 30 +
                [row("SEAL:S", ["001", "520"], fin="520", site="B")] * 29)
        g = B.geography(rows, "all")
        self.assertEqual(sorted(g["sites_rate_740"]), ["A"])          # B has 29 eligible seals: below the bar
        self.assertEqual(g["adequately_sampled_sites"], 1)

    def test_ztest_by_hand(self):
        # 50/100 vs 30/100: pooled 0.4; se = sqrt(0.4 * 0.6 * 0.02) = sqrt(0.0048); z = 0.2 / sqrt(0.0048)
        z, p = B.ztest(50, 100, 30, 100)
        self.assertAlmostEqual(z, 0.2 / math.sqrt(0.0048), places=12)
        self.assertAlmostEqual(p, 0.003892, places=5)


if __name__ == "__main__":
    unittest.main()
