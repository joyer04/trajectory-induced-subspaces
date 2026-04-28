from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tis.arithmetic_utils import expected_arithmetic_answer, predicted_arithmetic_answer
from tis.causal_utils import causal_oracle_correct
from tis.io_utils import read_jsonl
from tis.temporal_utils import temporal_oracle_correct


ARITHMETIC_SUBFAMILIES = {"combine_subtract", "inverse_linear", "average_speed"}
TEMPORAL_SUBFAMILIES = {"query_extraction", "full_ordering"}
CAUSAL_SUBFAMILIES = {"chain_propagation", "gated_condition"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Relabel mixed clean prompt bank traces with deterministic oracles.")
    parser.add_argument("--input", default="data/raw/traces_clean_prompt_bank_v1.jsonl")
    parser.add_argument("--output", default="data/raw/traces_clean_prompt_bank_v1_oracle.jsonl")
    parser.add_argument(
        "--promote-subfamily-as-task-family",
        action="store_true",
        help="Replace task_family with subfamily for subfamily-level geometry scans.",
    )
    return parser.parse_args()


def broad_family(record: dict[str, Any]) -> str:
    task_family = str(record.get("original_task_family") or record.get("task_family") or "")
    subfamily = str(record.get("subfamily") or "")
    if task_family == "arithmetic" or subfamily in ARITHMETIC_SUBFAMILIES:
        return "arithmetic"
    if task_family == "temporal_ordering" or subfamily in TEMPORAL_SUBFAMILIES:
        return "temporal"
    if task_family in {"causal_reasoning", "causal_micro_world"} or subfamily in CAUSAL_SUBFAMILIES:
        return "causal"
    return "unknown"


def relabel_record(record: dict[str, Any]) -> dict[str, Any]:
    family = broad_family(record)
    prompt = record.get("prompt", "")
    final_answer = record.get("final_answer", "")
    updated = dict(record)
    updated["original_task_family"] = record.get("original_task_family") or record.get("task_family", "")

    if family == "arithmetic":
        expected, subfamily = expected_arithmetic_answer(prompt)
        predicted = predicted_arithmetic_answer(record.get("steps", []))
        ok = expected is not None and predicted is not None and abs(expected - predicted) <= 1e-6
        updated["subfamily"] = subfamily
        updated["oracle_expected_answer"] = expected
        updated["oracle_predicted_answer"] = predicted
        updated["oracle_correct"] = ok
    elif family == "temporal":
        ok, expected, subfamily = temporal_oracle_correct(prompt, final_answer)
        updated["subfamily"] = subfamily
        updated["oracle_expected_answer"] = expected
        updated["oracle_correct"] = ok
    elif family == "causal":
        ok, expected, subfamily = causal_oracle_correct(prompt, final_answer)
        updated["subfamily"] = subfamily
        updated["oracle_expected_answer"] = expected
        updated["oracle_correct"] = ok
    else:
        updated["subfamily"] = record.get("subfamily", "unknown")
        updated["oracle_expected_answer"] = None
        updated["oracle_correct"] = False
        updated["oracle_error"] = "unknown_task_family"

    updated["outcome"] = "correct" if bool(updated["oracle_correct"]) else "incorrect"
    return updated


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            updated = relabel_record(record)
            if args.promote_subfamily_as_task_family:
                updated["task_family"] = updated["subfamily"]
            handle.write(json.dumps(updated, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
