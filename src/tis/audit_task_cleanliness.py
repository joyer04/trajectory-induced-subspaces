from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from tis.arithmetic_utils import expected_arithmetic_answer, infer_arithmetic_subfamily
from tis.causal_utils import causal_oracle_correct, get_causal_rule
from tis.io_utils import read_jsonl
from tis.temporal_utils import expected_temporal_answer, parse_temporal_constraints


TRACE_FILES = [
    "data/raw/traces_arithmetic_expansion_large_oracle.jsonl",
    "data/raw/traces_causal_subfamily_expanded_oracle.jsonl",
    "data/raw/traces_temporal_subfamily_expanded_v2_oracle_fixed.jsonl",
    "data/raw/traces_query_extraction_combined_fixed.jsonl",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit prompt cleanliness for regime geometry experiments")
    parser.add_argument("--base-dir", default="/Users/tedhong/Research/trajectory-induced-subspaces")
    parser.add_argument("--output-dir", default="outputs/task_audit")
    parser.add_argument(
        "--trace-files",
        nargs="*",
        default=TRACE_FILES,
        help="Trace JSONL files relative to base-dir. Defaults to the current exploratory trace set.",
    )
    return parser.parse_args()


def infer_family(record: dict) -> tuple[str, str]:
    task_family = str(record.get("original_task_family") or record.get("task_family") or "")
    subfamily = str(record.get("subfamily") or task_family)
    if task_family == "arithmetic" or subfamily in {"combine_subtract", "inverse_linear", "average_speed"}:
        return "arithmetic", subfamily or infer_arithmetic_subfamily(record["prompt"])
    if task_family == "temporal_ordering" or subfamily in {"query_extraction", "full_ordering"}:
        return "temporal", subfamily
    if task_family in {"causal_micro_world", "causal_reasoning"} or subfamily in {"gated_condition", "chain_propagation"}:
        return "causal", subfamily
    return task_family, subfamily


def audit_prompt(prompt: str, broad_family: str, subfamily: str) -> dict[str, object]:
    if broad_family == "arithmetic":
        expected, inferred = expected_arithmetic_answer(prompt)
        return {
            "expected_answer": "" if expected is None else str(expected),
            "inferred_subfamily": inferred,
            "parser_success": expected is not None,
            "fragility_reason": "" if expected is not None else "arithmetic parser could not infer expected answer",
        }

    if broad_family == "causal":
        ok, expected, inferred = causal_oracle_correct(prompt, "")
        rule = get_causal_rule(prompt)
        return {
            "expected_answer": "" if expected is None else str(expected),
            "inferred_subfamily": inferred,
            "parser_success": rule is not None,
            "fragility_reason": "" if rule is not None else "causal rule missing",
        }

    if broad_family == "temporal":
        ordering, entities, question = parse_temporal_constraints(prompt)
        expected, inferred = expected_temporal_answer(prompt)
        reason = ""
        if expected is None:
            reason = "temporal parser could not infer expected answer"
        elif len(entities) < 2 and subfamily == "query_extraction":
            reason = "query prompt has too few parsed entities"
        return {
            "expected_answer": "" if expected is None else str(expected),
            "inferred_subfamily": inferred,
            "parser_success": expected is not None and not reason,
            "fragility_reason": reason,
            "parsed_entity_count": len(entities),
            "parsed_ordering_len": len(ordering),
            "question": question,
        }

    return {
        "expected_answer": "",
        "inferred_subfamily": subfamily,
        "parser_success": False,
        "fragility_reason": "unknown broad family",
    }


def status_for_row(row: pd.Series) -> str:
    if not bool(row["parser_success"]):
        return "parser_fragile"
    if int(row["trace_count"]) < 3:
        return "low_support"
    if int(row["correct_count"]) == 0 or int(row["incorrect_count"]) == 0:
        return "single_outcome"
    return "clean_mixed"


def main() -> None:
    args = parse_args()
    base = Path(args.base_dir)
    output_dir = base / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    for relative in args.trace_files:
        path = base / relative
        if not path.exists():
            continue
        for record in read_jsonl(path):
            broad_family, subfamily = infer_family(record)
            records.append(
                {
                    "source_file": relative,
                    "prompt_id": record["prompt_id"],
                    "prompt": record["prompt"],
                    "broad_family": broad_family,
                    "subfamily": subfamily,
                    "outcome": record.get("outcome", "uncertain"),
                    "trace_id": record.get("trace_id", ""),
                }
            )

    trace_frame = pd.DataFrame(records)
    if trace_frame.empty:
        raise FileNotFoundError(f"No trace records found for: {args.trace_files}")
    audit_rows: list[dict] = []
    for (prompt_id, prompt), group in trace_frame.groupby(["prompt_id", "prompt"]):
        first = group.iloc[0]
        audit = audit_prompt(str(first["prompt"]), str(first["broad_family"]), str(first["subfamily"]))
        counts = group["outcome"].value_counts().to_dict()
        audit_rows.append(
            {
                "source_files": ";".join(sorted(str(value) for value in group["source_file"].unique())),
                "prompt_id": prompt_id,
                "broad_family": first["broad_family"],
                "subfamily": first["subfamily"],
                "trace_count": int(len(group)),
                "correct_count": int(counts.get("correct", 0)),
                "incorrect_count": int(counts.get("incorrect", 0)),
                "uncertain_count": int(counts.get("uncertain", 0)),
                "prompt": first["prompt"],
                **audit,
            }
        )

    audit_frame = pd.DataFrame(audit_rows)
    audit_frame["clean_status"] = audit_frame.apply(status_for_row, axis=1)
    audit_frame.to_csv(output_dir / "task_audit_table.csv", index=False)

    support = (
        audit_frame.groupby(["broad_family", "subfamily", "clean_status"])
        .agg(
            prompt_count=("prompt_id", "count"),
            trace_count=("trace_count", "sum"),
            correct_count=("correct_count", "sum"),
            incorrect_count=("incorrect_count", "sum"),
        )
        .reset_index()
        .sort_values(["broad_family", "subfamily", "clean_status"])
    )
    support.to_csv(output_dir / "subfamily_clean_support.csv", index=False)

    clean_mixed = audit_frame[audit_frame["clean_status"] == "clean_mixed"]
    summary = [
        "# Task Cleanliness Audit",
        "",
        "Artifacts:",
        "",
        f"- `{output_dir / 'task_audit_table.csv'}`",
        f"- `{output_dir / 'subfamily_clean_support.csv'}`",
        "",
        "## Summary",
        "",
        f"- prompts audited: `{len(audit_frame)}`",
        f"- clean mixed prompts: `{len(clean_mixed)}`",
        f"- parser-fragile prompts: `{int((audit_frame['clean_status'] == 'parser_fragile').sum())}`",
        f"- single-outcome prompts: `{int((audit_frame['clean_status'] == 'single_outcome').sum())}`",
        "",
        "## Read",
        "",
        "Use `clean_mixed` prompts for mechanism validation whenever possible.",
        "Use `single_outcome` prompts for generation-quality diagnostics, not for same-location/history tests.",
        "Treat `parser_fragile` prompts as excluded until the oracle is improved.",
    ]
    (base / "notes/task_audit_memo.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
