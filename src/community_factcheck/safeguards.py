HIGH_STAKES_TOPICS = {"medical", "legal", "election", "public_safety", "financial"}


def safeguard_status(topic: str, verified_evidence: int, disagreement: float | None) -> dict:
    reasons: list[str] = []
    if topic.lower() in HIGH_STAKES_TOPICS:
        reasons.append("high_stakes_topic")
    if verified_evidence < 2:
        reasons.append("fewer_than_two_verified_sources")
    if disagreement is None or disagreement > 0.40:
        reasons.append("review_consensus_not_established")
    return {
        "requires_human_approval": True,
        "publication_status": "paused" if reasons else "ready_for_editorial_review",
        "reasons": reasons,
        "notice": "This prototype supports reviewers; it does not determine truth autonomously.",
    }
