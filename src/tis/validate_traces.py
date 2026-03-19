from __future__ import annotations

import argparse
from collections import Counter

from tis.io_utils import read_jsonl


REQUIRED_FIELDS = {
    "trace_id",
    "prompt_id",
    "task_family",
    "model",
    "difficulty",
    "prompt",
    "steps",
    "final_answer",
    "outcome",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate trace JSONL structure")
    parser.add_argument(
        "--traces",
        default="data/raw/traces.jsonl",
        help="Path to traces JSONL",
    )
    return parser.parse_args()


def main() -> None:
    traces = read_jsonl(parse_args().traces)
    failures: list[str] = []
    outcomes = Counter()
    families = Counter()

    for idx, trace in enumerate(traces, start=1):
        missing = REQUIRED_FIELDS - set(trace)
        if missing:
            failures.append(f"record {idx}: missing fields {sorted(missing)}")
            continue
        if not isinstance(trace["steps"], list) or not trace["steps"]:
            failures.append(f"record {idx}: steps must be a non-empty list")
            continue
        if any(not isinstance(step, str) or not step.strip() for step in trace["steps"]):
            failures.append(f"record {idx}: every step must be a non-empty string")
            continue
        outcomes[trace["outcome"]] += 1
        families[trace["task_family"]] += 1

    if failures:
        print("TRACE VALIDATION FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("TRACE VALIDATION OK")
    print(f"records={len(traces)}")
    print(f"task_families={dict(families)}")
    print(f"outcomes={dict(outcomes)}")


if __name__ == "__main__":
    main()
