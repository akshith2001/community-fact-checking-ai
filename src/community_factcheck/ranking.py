import math
import re
from collections import Counter

from .models import Evidence


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _tfidf_vectors(texts: list[str]) -> list[dict[str, float]]:
    tokenized = [tokens(text) for text in texts]
    document_count = len(tokenized)
    document_frequency = Counter(token for doc in tokenized for token in set(doc))
    vectors: list[dict[str, float]] = []
    for doc in tokenized:
        counts = Counter(doc)
        total = max(len(doc), 1)
        vectors.append({
            token: (count / total) * (math.log((1 + document_count) / (1 + document_frequency[token])) + 1)
            for token, count in counts.items()
        })
    return vectors


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    common = left.keys() & right.keys()
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def rank_evidence(claim: str, evidence: tuple[Evidence, ...]) -> list[dict]:
    texts = [claim] + [f"{item.title} {item.text}" for item in evidence]
    vectors = _tfidf_vectors(texts)
    ranked = []
    for item, vector in zip(evidence, vectors[1:]):
        relevance = _cosine(vectors[0], vector)
        provenance_bonus = 0.10 if item.verified else 0.0
        ranked.append({
            "evidence_id": item.evidence_id,
            "title": item.title,
            "source_url": item.source_url,
            "publisher": item.publisher,
            "published_date": item.published_date,
            "stance": item.stance,
            "verified": item.verified,
            "relevance": round(relevance, 4),
            "ranking_score": round(min(relevance + provenance_bonus, 1.0), 4),
        })
    return sorted(ranked, key=lambda row: (-row["ranking_score"], row["evidence_id"]))
