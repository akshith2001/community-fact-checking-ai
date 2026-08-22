import argparse
from pathlib import Path

from .io import load_case, write_report
from .pipeline import assess_case
from .llm import OllamaClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the community fact-checking research prototype")
    parser.add_argument("case", type=Path, help="JSON case containing a claim, evidence and anonymous reviews")
    parser.add_argument("--output", type=Path, default=Path("outputs/report.json"))
    parser.add_argument("--llm", action="store_true", help="Use a local Ollama model for evidence-grounded analysis")
    parser.add_argument("--ollama-model", default="gemma3:4b")
    parser.add_argument("--ollama-endpoint", default="http://localhost:11434/api/chat")
    args = parser.parse_args()
    llm_client = OllamaClient(args.ollama_model, args.ollama_endpoint) if args.llm else None
    report = assess_case(load_case(args.case), llm_client=llm_client)
    write_report(args.output, report)
    print(f"Report written to {args.output}")
    print(f"Decision: {report['final_label']}")
    print(f"Publication status: {report['safeguards']['publication_status']}")


if __name__ == "__main__":
    main()
