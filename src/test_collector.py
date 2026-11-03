import json
import tempfile
import unittest
from pathlib import Path

from collector import calculate_trust, collect, percentile


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {
            "trust_score_min": 1, "trust_score_max": 5,
            "minimum_completion_rate": 0.9,
            "maximum_invalid_response_rate": 0.1,
        }
        self.rows = [
            {"response_id": "s1", "participant_group": "student", "trust_score": "4"},
            {"response_id": "p1", "participant_group": "patient", "trust_score": "2"},
        ]

    def test_means(self):
        result = calculate_trust(self.rows, self.cfg)
        self.assertEqual(result["student_minus_patient_mean_trust"], 2)
        self.assertEqual(result["valid_rows"], 2)

    def test_edge_cases_are_counted(self):
        rows = self.rows + [
            {"response_id": "s1", "participant_group": "student", "trust_score": "4"},
            {"response_id": "s2", "participant_group": "student", "trust_score": ""},
            {"response_id": "s3", "participant_group": "student", "trust_score": "999"},
            {"response_id": "", "participant_group": "patient", "trust_score": "2"},
            {"response_id": "s4", "participant_group": "student", "trust_score": "⭐"},
        ]
        result = calculate_trust(rows, self.cfg)
        self.assertEqual(result["invalid_rows"], 5)
        self.assertFalse(result["guardrails"]["invalid_response_rate_pass"])

    def test_empty_dataset(self):
        self.assertEqual(calculate_trust([], self.cfg)["total_rows"], 0)

    def test_percentiles(self):
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 95), 4.8)
        self.assertIsNone(percentile([], 99))

    def test_jsonl_120_measurements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "configs").mkdir()
            (root / "data" / "sample").mkdir(parents=True)
            import csv
            from benchmark import REQUIRED
            source = root / "data/sample/sample_synthetic.csv"
            with source.open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=sorted(REQUIRED))
                w.writeheader()
                for row in self.rows:
                    w.writerow(row)
            cfg = dict(self.cfg, scenario="synthetic_test", input_path="data/sample/sample_synthetic.csv",
                       output_jsonl_path="data/raw/test_run.jsonl", summary_output_path="results/summary.json",
                       workload={"warmup_runs": 2, "measurement_runs": 120, "calculations_per_measurement": 1})
            (root / "configs/config.yaml").write_text(json.dumps(cfg))
            result = collect(str(root / "configs/config.yaml"))
            entries = (root / "data/raw/test_run.jsonl").read_text().splitlines()
            self.assertEqual(len(entries), 120)
            self.assertEqual(result["warmup_runs_excluded"], 2)
            self.assertEqual(result["errors"], 0)
            self.assertTrue(all(json.loads(s)["status"] == "ok" for s in entries))


if __name__ == "__main__":
    unittest.main()
