import json
from pathlib import Path

from .models import Case, Evidence, Review


def load_case(path: Path) -> Case:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Case(
        claim=raw["claim"],
        topic=raw["topic"],
        evidence=tuple(Evidence(**item) for item in raw["evidence"]),
        reviews=tuple(Review(**item) for item in raw["reviews"]),
    )


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
