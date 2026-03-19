from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tis.io_utils import read_jsonl


FINAL_ANSWER_PATTERN = re.compile(r"^\s*final answer\s*:\s*(.+)$", re.IGNORECASE)
NUMBERED_STEP_PATTERN = re.compile(r"^\s*(?:step\s*)?\d+[\).\:-]\s*(.+)$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert raw model outputs into trace JSONL")
    parser.add_argument(
        "--input",
        default="data/raw/model_outputs.jsonl",
        help="Raw model outputs JSONL path",
    )
    parser.add_argument(
        "--output",
        default="data/raw/traces.jsonl",
        help="Prepared trace JSONL path",
    )
    parser.add_argument(
        "--default-outcome",
        default="uncertain",
        choices=["correct", "incorrect", "uncertain"],
        help="Outcome label to assign when no grader is available",
    )
    return parser.parse_args()


def split_steps(raw_output: str) -> tuple[list[str], str]:
    steps: list[str] = []
    final_answer = ""

    for raw_line in raw_output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        final_match = FINAL_ANSWER_PATTERN.match(line)
        if final_match:
            final_answer = final_match.group(1).strip()
            continue

        numbered_match = NUMBERED_STEP_PATTERN.match(line)
        if numbered_match:
            steps.append(numbered_match.group(1).strip())
            continue

        steps.append(line)

    if not final_answer and steps:
        final_answer = steps[-1]

    return steps, final_answer


def convert_record(record: dict, default_outcome: str, trace_index: int) -> dict:
    steps, final_answer = split_steps(record["raw_output"])
    converted = {
        "trace_id": f"trace_{trace_index:05d}",
        "prompt_id": record["prompt_id"],
        "task_family": record["task_family"],
        "model": record["model"],
        "difficulty": record.get("difficulty", "unknown"),
        "prompt": record["prompt"],
        "steps": steps,
        "final_answer": final_answer,
        "outcome": record.get("outcome", default_outcome),
    }
    for extra_key in ["trial_id", "repeat_index", "job_id", "temperature", "temperature_tag"]:
        if extra_key in record:
            converted[extra_key] = record[extra_key]
    return converted


def main() -> None:
    args = parse_args()
    raw_records = read_jsonl(args.input)
    converted = [
        convert_record(record, args.default_outcome, idx)
        for idx, record in enumerate(raw_records, start=1)
    ]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in converted:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
