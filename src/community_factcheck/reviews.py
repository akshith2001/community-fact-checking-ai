from .models import Review


def aggregate_reviews(reviews: tuple[Review, ...], minimum_reviews: int = 3) -> dict:
    if len(reviews) < minimum_reviews:
        return {
            "status": "insufficient_review",
            "review_count": len(reviews),
            "minimum_reviews": minimum_reviews,
            "decision": "uncertain",
            "disagreement": None,
            "scores": {"supported": 0.0, "refuted": 0.0, "uncertain": 0.0},
        }

    scores = {"supported": 0.0, "refuted": 0.0, "uncertain": 0.0}
    for review in reviews:
        if not 0 <= review.confidence <= 1:
            raise ValueError("review confidence must be between 0 and 1")
        scores[review.vote] += review.confidence

    total = sum(scores.values()) or 1.0
    normalized = {key: value / total for key, value in scores.items()}
    ordered = sorted(normalized.items(), key=lambda item: item[1], reverse=True)
    winner, winner_score = ordered[0]
    disagreement = 1.0 - winner_score
    decision = winner if winner_score >= 0.60 and disagreement <= 0.40 else "uncertain"
    return {
        "status": "reviewed",
        "review_count": len(reviews),
        "minimum_reviews": minimum_reviews,
        "decision": decision,
        "disagreement": round(disagreement, 4),
        "scores": {key: round(value, 4) for key, value in normalized.items()},
    }
