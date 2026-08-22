import unittest
from pathlib import Path

from community_factcheck.io import load_case
from community_factcheck.pipeline import assess_case


class ControlledEvaluationTests(unittest.TestCase):
    def test_cases_match_expected_baseline_labels(self):
        evaluation_dir = Path(__file__).parents[1] / "data" / "evaluation"
        expected = {
            "supported_case.json": "supported",
            "refuted_case.json": "refuted",
            "uncertain_case.json": "uncertain",
        }
        for filename, expected_label in expected.items():
            with self.subTest(filename=filename):
                report = assess_case(load_case(evaluation_dir / filename))
                self.assertEqual(report["final_label"], expected_label)


if __name__ == "__main__":
    unittest.main()
