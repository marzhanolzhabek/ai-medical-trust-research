import tempfile
import unittest
from pathlib import Path
from benchmark import run


class BenchmarkSmokeTests(unittest.TestCase):
    def test_sample(self):
        result = run("configs/config.json")
        self.assertEqual(result["valid_rows"], 10)
        self.assertEqual(result["invalid_rows"], 0)
        self.assertTrue(all(result["guardrails"].values()))
        self.assertTrue(result["synthetic_sample"])
        self.assertEqual(result["inference_status"], "not_performed_smoke_test")


if __name__ == "__main__":
    unittest.main()
