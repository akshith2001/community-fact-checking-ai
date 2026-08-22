import json
import tempfile
import unittest
from pathlib import Path

from community_factcheck.io import load_case, write_report
from community_factcheck.llm import build_prompt, validate_analysis
from community_factcheck.models import Case, Evidence, Review
from community_factcheck.pipeline import assess_case
from community_factcheck.ranking import rank_evidence, tokens
from community_factcheck.reviews import aggregate_reviews
from community_factcheck.safeguards import safeguard_status


def evidence(evidence_id="E1", stance="supports", verified=True, text="energy evidence"):
    return Evidence(evidence_id, "Energy report", text, "https://example.org", "Example", "2026-01-01", stance, verified)


class RankingTests(unittest.TestCase):
    def test_tokenization_is_case_insensitive(self):
        self.assertEqual(tokens("Energy ENERGY 30%"), ["energy", "energy", "30"])

    def test_verified_source_receives_bonus(self):
        ranked = rank_evidence("restaurant energy", (evidence("A", verified=False), evidence("B", verified=True)))
        self.assertEqual(ranked[0]["evidence_id"], "B")

    def test_relevant_evidence_ranks_first(self):
        ranked = rank_evidence("restaurant electricity", (evidence("A", text="unrelated football"), evidence("B", text="restaurant electricity demand")))
        self.assertEqual(ranked[0]["evidence_id"], "B")


class ReviewTests(unittest.TestCase):
    def test_requires_minimum_number_of_reviews(self):
        result = aggregate_reviews((Review("a", "supported", 1.0, "ok"),))
        self.assertEqual(result["status"], "insufficient_review")

    def test_clear_weighted_majority_is_selected(self):
        reviews = (Review("a", "refuted", 1.0, ""), Review("b", "refuted", 0.9, ""), Review("c", "uncertain", 0.2, ""))
        self.assertEqual(aggregate_reviews(reviews)["decision"], "refuted")

    def test_disagreement_returns_uncertain(self):
        reviews = (Review("a", "supported", 1.0, ""), Review("b", "refuted", 1.0, ""), Review("c", "uncertain", 1.0, ""))
        self.assertEqual(aggregate_reviews(reviews)["decision"], "uncertain")

    def test_invalid_confidence_is_rejected(self):
        reviews = (Review("a", "supported", 1.2, ""), Review("b", "supported", 1.0, ""), Review("c", "supported", 1.0, ""))
        with self.assertRaises(ValueError):
            aggregate_reviews(reviews)


class SafeguardTests(unittest.TestCase):
    def test_high_stakes_topic_pauses_publication(self):
        self.assertEqual(safeguard_status("medical", 3, 0.1)["publication_status"], "paused")

    def test_too_few_verified_sources_pauses(self):
        self.assertIn("fewer_than_two_verified_sources", safeguard_status("energy", 1, 0.1)["reasons"])

    def test_sufficient_low_risk_case_reaches_editorial_review(self):
        self.assertEqual(safeguard_status("energy", 2, 0.2)["publication_status"], "ready_for_editorial_review")


class PipelineTests(unittest.TestCase):
    def test_pipeline_never_removes_human_approval(self):
        case = Case("claim", "energy", (evidence("A"), evidence("B", stance="refutes")), (
            Review("a", "supported", 1.0, ""), Review("b", "supported", 1.0, ""), Review("c", "supported", 1.0, "")))
        self.assertTrue(assess_case(case)["safeguards"]["requires_human_approval"])

    def test_paused_case_has_uncertain_final_label(self):
        case = Case("claim", "medical", (evidence("A"), evidence("B")), (
            Review("a", "supported", 1.0, ""), Review("b", "supported", 1.0, ""), Review("c", "supported", 1.0, "")))
        self.assertEqual(assess_case(case)["final_label"], "uncertain")

    def test_example_file_loads_and_report_writes(self):
        root = Path(__file__).parents[1]
        case = load_case(root / "data" / "example_case.json")
        report = assess_case(case)
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "report.json"
            write_report(output, report)
            self.assertEqual(json.loads(output.read_text())["claim"], case.claim)


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def analyse(self, claim, evidence):
        return self.response


class LLMTests(unittest.TestCase):
    def test_prompt_limits_model_to_supplied_evidence(self):
        prompt = build_prompt("claim", (evidence("E1"),))
        self.assertIn("using only the supplied evidence", prompt)
        self.assertIn('"evidence_id": "E1"', prompt)

    def test_valid_grounded_analysis_is_retained(self):
        raw = {"label": "supported", "confidence": 0.8, "explanation": "E1 supports it.", "evidence_ids": ["E1"], "unsupported_claims": []}
        result = validate_analysis(raw, {"E1"})
        self.assertTrue(result["valid"])
        self.assertTrue(result["requires_human_review"])

    def test_invented_citation_is_rejected(self):
        raw = {"label": "supported", "confidence": 0.8, "explanation": "E99 supports it.", "evidence_ids": ["E99"], "unsupported_claims": []}
        result = validate_analysis(raw, {"E1"})
        self.assertFalse(result["valid"])
        self.assertIn("invented_evidence_ids", result["validation_reasons"])

    def test_invalid_llm_output_pauses_pipeline(self):
        case = Case("claim", "energy", (evidence("E1"), evidence("E2")), (
            Review("a", "supported", 1.0, ""), Review("b", "supported", 1.0, ""), Review("c", "supported", 1.0, "")))
        client = FakeLLM({"label": "supported", "confidence": 0.9, "explanation": "No citation", "evidence_ids": [], "unsupported_claims": []})
        report = assess_case(case, llm_client=client)
        self.assertEqual(report["safeguards"]["publication_status"], "paused")
        self.assertIn("llm_output_invalid", report["safeguards"]["reasons"])


if __name__ == "__main__":
    unittest.main()
