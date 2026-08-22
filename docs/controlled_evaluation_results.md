# Controlled evaluation: first recorded run

## Scope

This small diagnostic run checks workflow behaviour; it is not evidence of real-world accuracy. It uses three synthetic energy cases designed to have unambiguous expected labels: one supported, one refuted and one uncertain. No private venue or reviewer data is included.

Run date: 22 August 2026  
Local provider: Ollama  
Model: `gemma3:4b`  
Temperature: `0`

## Results

| Expected label | Baseline label | Raw LLM label | Confidence | Citations | LLM output accepted? | Workflow result |
|---|---|---|---:|---|---|---|
| supported | supported | supported | 0.95 | E1, E2 | No | paused / uncertain |
| refuted | refuted | refuted | 0.95 | E1, E2 | No | paused / uncertain |
| uncertain | uncertain | uncertain | 0.60 | E1, E2, E3 | No | paused / uncertain |

The transparent community-review baseline matched all three expected labels. The LLM also selected all three expected labels and cited only supplied evidence IDs. However, every LLM response populated `unsupported_explanation_claims`. Under the project's fail-closed validation policy, this makes the response invalid, pauses the workflow and prevents its label from becoming the final result.

## Interpretation

The run demonstrates useful evidence-grounded classification behaviour, but it also exposes an interface-reliability problem: this model did not follow the intended meaning of the unsupported-claims field. A three-case synthetic test is far too small to support an accuracy claim. The correct result to report is therefore:

- baseline: 3/3 expected labels on controlled synthetic cases;
- raw LLM labels: 3/3 expected labels, with valid supplied citations;
- accepted LLM outputs: 0/3;
- safety-pause recall for these invalid outputs: 3/3;
- automatic publication: 0 cases.

## Next experiment

Before changing the validator, expand the labelled set and compare two structured-output designs. Preserve every invalid response, evaluate accepted-output coverage separately from raw-label accuracy, and require human review for every case. Real-world performance must be tested on appropriately licensed, independently labelled evidence rather than inferred from these synthetic examples.
