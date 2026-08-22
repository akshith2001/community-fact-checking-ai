import json
from dataclasses import dataclass
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen

from .models import Evidence


ALLOWED_LABELS = {"supported", "refuted", "uncertain"}

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": sorted(ALLOWED_LABELS)},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "explanation": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
        "unsupported_claims": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["label", "confidence", "explanation", "evidence_ids", "unsupported_claims"],
}


class LLMClient(Protocol):
    def analyse(self, claim: str, evidence: tuple[Evidence, ...]) -> dict: ...


def build_prompt(claim: str, evidence: tuple[Evidence, ...]) -> str:
    records = [
        {
            "evidence_id": item.evidence_id,
            "title": item.title,
            "text": item.text,
            "publisher": item.publisher,
            "verified": item.verified,
        }
        for item in evidence
    ]
    return (
        "Assess the claim using only the supplied evidence. Do not use outside knowledge. "
        "Choose supported, refuted, or uncertain. Cite only supplied evidence_id values. "
        "Use uncertain when the evidence is insufficient or conflicting. Return JSON matching "
        f"this schema: {json.dumps(ANALYSIS_SCHEMA)}\n\n"
        f"CLAIM: {claim}\nEVIDENCE: {json.dumps(records, ensure_ascii=False)}"
    )


@dataclass(frozen=True)
class OllamaClient:
    model: str = "gemma3:4b"
    endpoint: str = "http://localhost:11434/api/chat"
    timeout_seconds: float = 120.0

    def analyse(self, claim: str, evidence: tuple[Evidence, ...]) -> dict:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": build_prompt(claim, evidence)}],
            "stream": False,
            "format": ANALYSIS_SCHEMA,
            "options": {"temperature": 0},
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        try:
            return json.loads(body["message"]["content"])
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Ollama returned an invalid response envelope") from exc


def validate_analysis(raw: dict, allowed_evidence_ids: set[str]) -> dict:
    reasons: list[str] = []
    label = raw.get("label")
    confidence = raw.get("confidence")
    explanation = raw.get("explanation")
    evidence_ids = raw.get("evidence_ids")
    unsupported_claims = raw.get("unsupported_claims")

    if label not in ALLOWED_LABELS:
        reasons.append("invalid_label")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        reasons.append("invalid_confidence")
    if not isinstance(explanation, str) or not explanation.strip():
        reasons.append("missing_explanation")
    if not isinstance(evidence_ids, list) or not all(isinstance(item, str) for item in evidence_ids):
        reasons.append("invalid_evidence_ids")
        evidence_ids = []
    unknown_ids = sorted(set(evidence_ids) - allowed_evidence_ids)
    if unknown_ids:
        reasons.append("invented_evidence_ids")
    if label in {"supported", "refuted"} and not evidence_ids:
        reasons.append("conclusion_without_citation")
    if not isinstance(unsupported_claims, list) or not all(isinstance(item, str) for item in unsupported_claims):
        reasons.append("invalid_unsupported_claims")

    return {
        "valid": not reasons,
        "validation_reasons": reasons,
        "label": label if label in ALLOWED_LABELS else "uncertain",
        "confidence": confidence if isinstance(confidence, (int, float)) and not isinstance(confidence, bool) else 0.0,
        "explanation": explanation if isinstance(explanation, str) else "",
        "evidence_ids": evidence_ids,
        "unsupported_claims": unsupported_claims if isinstance(unsupported_claims, list) else [],
        "requires_human_review": True,
    }
