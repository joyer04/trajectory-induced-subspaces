from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from tis.io_utils import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build repeated prompt jobs for same-prompt recurrence experiments")
    parser.add_argument("--input", default="data/raw/prompts_seed.jsonl", help="Prompt bank JSONL")
    parser.add_argument("--output", default="data/raw/repeated_prompt_jobs.jsonl", help="Repeated prompt jobs JSONL")
    parser.add_argument("--prompts-per-family", type=int, default=2, help="How many prompt ids to sample per family")
    parser.add_argument("--repeats", type=int, default=5, help="How many repeated generations per prompt")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="Sampling temperature attached to each repeated job",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.input)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[record["task_family"]].append(record)

    jobs: list[dict] = []
    for task_family, family_records in grouped.items():
        selected = family_records[: args.prompts_per_family]
        for prompt_record in selected:
            for repeat_index in range(args.repeats):
                jobs.append(
                    {
                        **prompt_record,
                        "trial_id": f"{prompt_record['prompt_id']}__trial_{repeat_index + 1:02d}",
                        "repeat_index": repeat_index + 1,
                        "job_id": f"{prompt_record['prompt_id']}__job_{repeat_index + 1:02d}",
                        "temperature": args.temperature,
                    }
                )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
