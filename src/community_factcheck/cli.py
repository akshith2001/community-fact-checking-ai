import argparse
from pathlib import Path

from .io import load_case, write_report
from .pipeline import assess_case


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the community fact-checking research prototype")
    parser.add_argument("case", type=Path, help="JSON case containing a claim, evidence and anonymous reviews")
    parser.add_argument("--output", type=Path, default=Path("outputs/report.json"))
    args = parser.parse_args()
    report = assess_case(load_case(args.case))
    write_report(args.output, report)
    print(f"Report written to {args.output}")
    print(f"Decision: {report['final_label']}")
    print(f"Publication status: {report['safeguards']['publication_status']}")


if __name__ == "__main__":
    main()
