from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from tis.io_utils import read_jsonl


def format_temperature_tag(temperature: float) -> str:
    return str(temperature).replace(".", "p")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build repeated prompt jobs across multiple temperatures")
    parser.add_argument("--input", default="data/raw/prompts_seed.jsonl", help="Prompt bank JSONL")
    parser.add_argument("--output", default="data/raw/repeated_prompt_jobs_temperatures.jsonl", help="Output JSONL")
    parser.add_argument("--prompts-per-family", type=int, default=4, help="Prompt ids per family")
    parser.add_argument("--repeats", type=int, default=5, help="Repeats per prompt and temperature")
    parser.add_argument(
        "--temperatures",
        nargs="+",
        type=float,
        default=[0.2, 0.5, 0.8],
        help="Temperature grid to attach to each prompt",
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
            for temperature in args.temperatures:
                temperature_tag = format_temperature_tag(temperature)
                for repeat_index in range(args.repeats):
                    jobs.append(
                        {
                            **prompt_record,
                            "temperature": temperature,
                            "temperature_tag": temperature_tag,
                            "trial_id": f"{prompt_record['prompt_id']}__temp_{temperature_tag}__trial_{repeat_index + 1:02d}",
                            "repeat_index": repeat_index + 1,
                            "job_id": f"{prompt_record['prompt_id']}__temp_{temperature_tag}__job_{repeat_index + 1:02d}",
                        }
                    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
