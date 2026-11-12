"""Spec 12 D3 (11 Nov 2026): input path and pin as parameters; an explicit any-input mode. Written BEFORE the code.
Synthetic only: no ICIT row is used (the synthetic CSV below is invented)."""
import inspect
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import spec_lib as S  # noqa: E402

COLUMNS = ["id", "cisi", "site", "type", "dir.", "complete", "area-section", "room-grid", "depth", "phase", "text"]
SYNTH = [  # invented rows (not ICIT data)
    ["1.1", "X-1", "Sitea", "TAB:I", "R/L", "Y", "--", "--", "- -", "-", "+101-102+"],
    ["2.1", "X-2", "Sitea", "SEAL:S", "R/L", "Y", "--", "--", "- -", "-", "+103-104-105+"],
]


def synthetic_csv():
    fd, path = tempfile.mkstemp(suffix=".csv", prefix="d3_synth_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(COLUMNS) + "\n")
        for r in SYNTH:
            fh.write(",".join(r) + "\n")
    return path


class TestD3InputModes(unittest.TestCase):
    def test_defaults_unchanged(self):
        sig = inspect.signature(S.load_rows)
        self.assertEqual(list(sig.parameters), ["path", "pin"])
        self.assertEqual(sig.parameters["path"].default, S.PINNED)
        self.assertEqual(sig.parameters["pin"].default, S.PINNED_SHA)
        self.assertEqual(S.PINNED_SHA, "c02e3d7bb74cf5abb11cc94f88d8d469e6acc5d6fad4b7153c02c43428f58d98")
        self.assertTrue(S.PINNED.endswith("input.csv"))

    def test_default_pin_refuses_another_file(self):
        p = synthetic_csv()
        try:
            with self.assertRaises(RuntimeError):
                S.load_rows(p)
        finally:
            os.remove(p)

    def test_any_input_mode_parses_another_file(self):
        p = synthetic_csv()
        try:
            rows = S.load_rows(p, pin=None)
        finally:
            os.remove(p)
        self.assertEqual([r.id for r in rows], ["1.1", "2.1"])
        self.assertEqual(rows[1].n_legible, 3)

    def test_input_mode_flag(self):
        self.assertEqual(S.input_mode([]), (S.PINNED, S.PINNED_SHA, "out", None))
        path, pin, outdir, note = S.input_mode(["--any-input", "other.csv"])
        self.assertEqual((path, pin, outdir), ("other.csv", None, "out_any_input"))
        self.assertIn("not expected to match", note)
        with self.assertRaises(SystemExit):
            S.input_mode(["--any-input"])          # a path is required


if __name__ == "__main__":
    unittest.main()
