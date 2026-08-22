from .models import Case
from .ranking import rank_evidence
from .reviews import aggregate_reviews
from .safeguards import safeguard_status


def assess_case(case: Case, minimum_reviews: int = 3) -> dict:
    ranked = rank_evidence(case.claim, case.evidence)
    review_summary = aggregate_reviews(case.reviews, minimum_reviews=minimum_reviews)
    verified_count = sum(item.verified for item in case.evidence)
    stance_counts = {"supports": 0, "refutes": 0, "unclear": 0}
    for item in case.evidence:
        stance_counts[item.stance] += 1

    safeguards = safeguard_status(case.topic, verified_count, review_summary["disagreement"])
    return {
        "claim": case.claim,
        "topic": case.topic,
        "method": "transparent_tfidf_baseline_plus_weighted_community_review",
        "evidence_summary": {
            "total": len(case.evidence),
            "verified": verified_count,
            "stance_counts": stance_counts,
        },
        "ranked_evidence": ranked,
        "community_review": review_summary,
        "safeguards": safeguards,
        "final_label": review_summary["decision"] if safeguards["publication_status"] != "paused" else "uncertain",
    }
