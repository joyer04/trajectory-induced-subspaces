from __future__ import annotations

import argparse
import json
from pathlib import Path

from tis.io_utils import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract unique reasoning step texts into a JSON list")
    parser.add_argument("--input", default="data/raw/traces_balanced_scored.jsonl")
    parser.add_argument("--output", default="data/tis_step_texts_balanced.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.input)
    seen: set[str] = set()
    texts: list[str] = []

    for record in records:
        for step in record.get("steps", []):
            step = step.strip()
            if step and step not in seen:
                texts.append(step)
                seen.add(step)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(texts, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
