from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from tis.prompt_bank import build_prompt_bank


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a seed prompt bank for TIS experiments")
    parser.add_argument(
        "--output",
        default="data/raw/prompts_seed.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument(
        "--per-family",
        type=int,
        default=15,
        help="Maximum number of prompts to keep per task family",
    )
    parser.add_argument(
        "--order",
        choices=["grouped", "interleave"],
        default="interleave",
        help="Whether to keep prompts grouped by family or interleave families",
    )
    return parser.parse_args()


def interleave_records(records: list) -> list:
    grouped: dict[str, list] = defaultdict(list)
    family_order: list[str] = []

    for record in records:
        if record.task_family not in grouped:
            family_order.append(record.task_family)
        grouped[record.task_family].append(record)

    interleaved: list = []
    row = 0
    while True:
        added = False
        for family in family_order:
            family_records = grouped[family]
            if row < len(family_records):
                interleaved.append(family_records[row])
                added = True
        if not added:
            break
        row += 1
    return interleaved


def main() -> None:
    args = parse_args()
    records = build_prompt_bank()
    family_counts: dict[str, int] = {}
    selected_records: list = []

    for record in records:
        count = family_counts.get(record.task_family, 0)
        if count >= args.per_family:
            continue
        selected_records.append(record)
        family_counts[record.task_family] = count + 1

    if args.order == "interleave":
        selected_records = interleave_records(selected_records)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in selected_records:
            handle.write(json.dumps(record.as_dict(), ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
