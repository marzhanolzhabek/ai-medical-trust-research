
import unittest
from benchmark import run


class BenchmarkSmokeTests(unittest.TestCase):

    def setUp(self):
        self.result = run("configs/config.json")

    def test_sample(self):
        self.assertEqual(self.result["valid_rows"], 10)
        self.assertEqual(self.result["invalid_rows"], 0)
        self.assertTrue(all(self.result["guardrails"].values()))
        self.assertTrue(self.result["synthetic_sample"])
        self.assertEqual(
            self.result["inference_status"],
            "not_performed_smoke_test"
        )

    def test_participant_groups(self):
        self.assertEqual(self.result["groups"]["student"]["n"], 5)
        self.assertEqual(self.result["groups"]["patient"]["n"], 5)

    def test_mean_trust_difference(self):
        self.assertAlmostEqual(
            self.result["student_minus_patient_mean_trust"], 0.8
        )

    def test_completion_rate(self):
        self.assertEqual(self.result["completion_rate"], 1.0)
        self.assertEqual(self.result["invalid_response_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
