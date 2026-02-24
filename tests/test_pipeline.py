from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from qdep.cli import run_pipeline


class TestPipeline(unittest.TestCase):
    def test_pipeline_outputs_and_counts(self) -> None:
        fixture = Path("fixtures/sample_page.html").resolve()
        self.assertTrue(fixture.exists(), "fixture HTML should exist")

        with TemporaryDirectory() as td:
            outdir = Path(td)
            extracted, valid, invalid = run_pipeline(input_path=fixture, outdir=outdir, realtime=False)

            # output files exist
            self.assertTrue((outdir / "output.json").exists())
            self.assertTrue((outdir / "output.csv").exists())
            self.assertTrue((outdir / "summary.txt").exists())
            self.assertTrue((outdir / "run.log").exists())

            # valid count >= 10
            self.assertGreaterEqual(valid, 10)

            # CSV row count matches valid count
            with (outdir / "output.csv").open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), valid)

            # JSON sanity
            data = json.loads((outdir / "output.json").read_text(encoding="utf-8"))
            self.assertEqual(len(data["items"]), valid)
            self.assertEqual(len(data["errors"]), invalid)


if __name__ == "__main__":
    unittest.main()