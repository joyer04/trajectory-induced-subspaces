from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tis.io_utils import read_jsonl
from tis.prepare_traces import convert_record
from tis.relabel_clean_prompt_bank_oracle import relabel_record


DEFAULT_MODEL_OUTPUTS = Path("data/raw/model_outputs_clean_prompt_bank_v1.jsonl")
DEFAULT_TRACES = Path("data/raw/traces_clean_prompt_bank_v1.jsonl")
DEFAULT_ORACLE = Path("data/raw/traces_clean_prompt_bank_v1_oracle.jsonl")
DEFAULT_SUMMARY_DIR = Path("outputs/clean_prompt_bank_v1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare, relabel, and summarize clean prompt bank traces.")
    parser.add_argument("--model-outputs", type=Path, default=DEFAULT_MODEL_OUTPUTS)
    parser.add_argument("--traces", type=Path, default=DEFAULT_TRACES)
    parser.add_argument("--oracle-traces", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--summary-dir", type=Path, default=DEFAULT_SUMMARY_DIR)
    parser.add_argument("--promote-subfamily-as-task-family", action="store_true")
    return parser.parse_args()


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(records: list[dict[str, Any]], summary_dir: Path) -> None:
    by_subfamily: Counter[tuple[str, str, str]] = Counter()
    prompt_outcomes: dict[str, Counter[str]] = defaultdict(Counter)
    prompt_meta: dict[str, dict[str, str]] = {}

    for record in records:
        family = str(record.get("original_task_family") or record.get("task_family") or "")
        subfamily = str(record.get("subfamily") or "")
        outcome = str(record.get("outcome") or "uncertain")
        prompt_id = str(record.get("prompt_id") or "")
        by_subfamily[(family, subfamily, outcome)] += 1
        prompt_outcomes[prompt_id][outcome] += 1
        prompt_meta[prompt_id] = {
            "prompt_id": prompt_id,
            "family": family,
            "subfamily": subfamily,
            "prompt": str(record.get("prompt", "")),
        }

    subfamily_rows: list[dict[str, Any]] = []
    family_subfamilies = sorted({(family, subfamily) for family, subfamily, _ in by_subfamily})
    for family, subfamily in family_subfamilies:
        correct = by_subfamily[(family, subfamily, "correct")]
        incorrect = by_subfamily[(family, subfamily, "incorrect")]
        uncertain = by_subfamily[(family, subfamily, "uncertain")]
        total = correct + incorrect + uncertain
        subfamily_rows.append(
            {
                "family": family,
                "subfamily": subfamily,
                "trace_count": total,
                "correct_count": correct,
                "incorrect_count": incorrect,
                "uncertain_count": uncertain,
                "correct_rate": round(correct / total, 4) if total else 0.0,
            }
        )

    prompt_rows: list[dict[str, Any]] = []
    for prompt_id, counts in sorted(prompt_outcomes.items()):
        total = sum(counts.values())
        status = "clean_mixed" if counts["correct"] > 0 and counts["incorrect"] > 0 else "single_outcome"
        meta = prompt_meta[prompt_id]
        prompt_rows.append(
            {
                **meta,
                "trace_count": total,
                "correct_count": counts["correct"],
                "incorrect_count": counts["incorrect"],
                "uncertain_count": counts["uncertain"],
                "clean_status": status,
            }
        )

    write_csv(
        summary_dir / "subfamily_outcome_summary.csv",
        subfamily_rows,
        ["family", "subfamily", "trace_count", "correct_count", "incorrect_count", "uncertain_count", "correct_rate"],
    )
    write_csv(
        summary_dir / "prompt_outcome_support.csv",
        prompt_rows,
        ["prompt_id", "family", "subfamily", "trace_count", "correct_count", "incorrect_count", "uncertain_count", "clean_status", "prompt"],
    )

    mixed_count = sum(1 for row in prompt_rows if row["clean_status"] == "clean_mixed")
    memo = [
        "# Clean Prompt Bank v1 Run Summary",
        "",
        "Artifacts:",
        f"- `{summary_dir / 'subfamily_outcome_summary.csv'}`",
        f"- `{summary_dir / 'prompt_outcome_support.csv'}`",
        "",
        f"Traces: `{len(records)}`",
        f"Prompts: `{len(prompt_rows)}`",
        f"Clean mixed prompts: `{mixed_count}`",
        "",
        "Interpretation:",
        "- `clean_mixed` prompts are the strongest support set for same-prompt recurrence and outcome-contrast geometry.",
        "- `single_outcome` prompts are still useful for family/subfamily geometry, but not for correct-vs-incorrect local comparisons.",
    ]
    (summary_dir / "run_summary.md").write_text("\n".join(memo) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if not args.model_outputs.exists():
        raise FileNotFoundError(f"Missing model outputs: {args.model_outputs}")

    raw_records = read_jsonl(args.model_outputs)
    traces = [convert_record(record, "uncertain", index) for index, record in enumerate(raw_records, start=1)]
    write_jsonl(args.traces, traces)

    oracle_records = [relabel_record(record) for record in traces]
    if args.promote_subfamily_as_task_family:
        for record in oracle_records:
            record["task_family"] = record["subfamily"]
    write_jsonl(args.oracle_traces, oracle_records)
    summarize(oracle_records, args.summary_dir)

    print(f"prepared traces: {args.traces}")
    print(f"oracle traces: {args.oracle_traces}")
    print(f"summary dir: {args.summary_dir}")


if __name__ == "__main__":
    main()
