# Community Fact-Checking AI

A transparent research prototype for ranking evidence and combining anonymous community reviews without allowing a model to declare truth autonomously.

## Research question

How can machine assistance help community fact-checkers find relevant evidence while preserving provenance, disagreement, uncertainty and accountable human approval?

## What the prototype does

1. Accepts a claim, topic, evidence records and anonymous reviewer assessments.
2. Ranks evidence with an explainable TF-IDF relevance baseline and a small verified-source bonus.
3. Aggregates reviewer votes using declared confidence scores.
4. Returns `uncertain` when consensus or evidence is insufficient.
5. Pauses high-stakes cases and always retains human approval.
6. Writes a reproducible JSON report containing evidence metadata and safeguards.

## Optional LLM mode (version 0.2)

The original TF-IDF workflow remains the transparent baseline. An optional local Ollama model can now analyse only the supplied evidence and return a structured label, confidence, explanation and evidence IDs.

The software validates every cited ID, rejects conclusions without citations, pauses invalid model output and always requires human review. The LLM never controls the final decision.

```powershell
ollama pull gemma3:4b
factcheck-demo data/example_case.json --llm --ollama-model gemma3:4b --output outputs/llm_report.json
```

Ollama must be installed and running locally. Normal baseline use does not require Ollama or any API key.

## What it does not do

- It does not browse for evidence or verify that a URL is truthful.
- It does not infer evidence stance; stance is recorded by a reviewer or upstream process.
- The version 0.1 baseline does not use an LLM; version 0.2 makes LLM analysis optional.
- It must not be described as an automated truth detector or production system.

This baseline is deliberate. A later LLM-assisted component can be compared against it for retrieval quality, calibration, unsupported claims, demographic bias and reviewer usefulness.

## Run it

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
factcheck-demo data/example_case.json --output outputs/example_report.json
```

## Output interpretation

- `ranked_evidence`: relevance and provenance fields remain visible.
- `community_review.disagreement`: higher values mean weaker consensus.
- `publication_status`: `paused` or `ready_for_editorial_review`, never automatically published.
- `final_label`: a provisional workflow label, not an objective statement of truth.

## Planned evaluation

- Retrieval: precision@k and nDCG against reviewer relevance judgements.
- Classification support: macro F1 and abstention coverage, if a labelled dataset is introduced.
- Calibration: Brier score or expected calibration error for probabilistic outputs.
- Human factors: time saved, reviewer agreement and usefulness ratings.
- Safety: unsupported-citation rate, high-stakes pause recall and subgroup error analysis.

## Responsible AI design

The system stores no reviewer names in the example workflow. Real deployments would need consent, retention limits, access controls, abuse monitoring and a documented appeal process. Evidence verification and reviewer identity protection are governance responsibilities, not problems that an LLM can solve alone.

## Author

Akshith Moharampudi — Computer Science MComp graduate interested in responsible AI, information systems and reproducible research.
