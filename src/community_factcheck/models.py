from dataclasses import dataclass
from typing import Literal


Stance = Literal["supports", "refutes", "unclear"]
Vote = Literal["supported", "refuted", "uncertain"]


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    title: str
    text: str
    source_url: str
    publisher: str
    published_date: str
    stance: Stance
    verified: bool


@dataclass(frozen=True)
class Review:
    reviewer_id: str
    vote: Vote
    confidence: float
    rationale: str


@dataclass(frozen=True)
class Case:
    claim: str
    topic: str
    evidence: tuple[Evidence, ...]
    reviews: tuple[Review, ...]
