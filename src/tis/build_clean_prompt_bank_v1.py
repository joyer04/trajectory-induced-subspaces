from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tis.arithmetic_utils import expected_arithmetic_answer
from tis.causal_utils import get_causal_rule
from tis.temporal_utils import expected_temporal_answer


DEFAULT_OUTPUT = Path("data/raw/clean_prompt_bank_v1.jsonl")
DEFAULT_MEMO = Path("notes/clean_prompt_bank_v1_memo.md")


def arithmetic_prompts() -> list[dict[str, Any]]:
    specs = [
        ("combine_subtract", "easy", "A class collected 14 cans on Monday and 19 on Tuesday. If 6 were discarded, how many usable cans remained?"),
        ("combine_subtract", "easy", "A store sold 23 pencils in the morning and 18 in the afternoon. If 7 were returned, how many pencils stayed sold?"),
        ("combine_subtract", "medium", "A club raised 125 dollars on Friday and 87 dollars on Saturday. If 36 dollars were spent, how much money remained?"),
        ("combine_subtract", "medium", "A library checked out 42 books to adults and 31 to children. If 9 books were returned, how many books stayed checked out?"),
        ("combine_subtract", "hard", "A warehouse shipped 240 boxes in one batch and 175 in another. If 58 boxes came back, how many boxes remained delivered?"),
        ("combine_subtract", "hard", "A fundraiser got 318 dollars online and 247 dollars in person. If 89 dollars paid fees, how much money was left?"),
        ("combine_subtract", "easy", "A gardener planted 16 tulips and 21 roses. If 5 plants wilted, how many plants stayed healthy?"),
        ("combine_subtract", "medium", "A museum sold 76 adult tickets and 54 student tickets. If 18 tickets were refunded, how many tickets remained sold?"),
        ("combine_subtract", "hard", "A depot received 430 packages in the morning and 285 at night. If 96 packages were damaged, how many packages remained usable?"),
        ("combine_subtract", "medium", "A team scored 38 points in the first half and 44 in the second half. If 12 points were removed by penalties, what score remained?"),
        ("inverse_linear", "easy", "A number is multiplied by 3 and then 5 is added to get 26. What is the original number?"),
        ("inverse_linear", "easy", "A number is doubled and then 9 is subtracted to get 17. What is the original number?"),
        ("inverse_linear", "medium", "A number is multiplied by 5 and then 12 is added to get 67. What is the original number?"),
        ("inverse_linear", "medium", "A number is divided by 4 and then 6 is added to get 14. What is the original number?"),
        ("inverse_linear", "hard", "A number is multiplied by 7, then 11 is subtracted, and the result is 45. What is the original number?"),
        ("inverse_linear", "hard", "A number is multiplied by 8 and then 16 is added to get 80. What is the original number?"),
        ("inverse_linear", "medium", "A number is divided by 6 and then 4 is added to get 13. What is the original number?"),
        ("inverse_linear", "hard", "A number is multiplied by 9, then 18 is subtracted, and the result is 63. What is the original number?"),
        ("inverse_linear", "easy", "A number is doubled and then 4 is subtracted to get 20. What is the original number?"),
        ("inverse_linear", "medium", "A number is multiplied by 4 and then 10 is added to get 46. What is the original number?"),
        ("average_speed", "easy", "A car travels 60 km in 1 hour and then 90 km in 2 hours. What is the average speed over the whole trip?"),
        ("average_speed", "easy", "A runner completes 4 km in 20 minutes and then 2 km in 10 minutes. What is the average speed in km per minute?"),
        ("average_speed", "medium", "A train travels 150 km in 3 hours and then 220 km in 4 hours. What is the average speed across the full trip?"),
        ("average_speed", "medium", "A cyclist rides 18 miles in 1.5 hours and then 12 miles in 1 hour. What is the average speed for the entire ride?"),
        ("average_speed", "hard", "A delivery van travels 84 km in 1.5 hours and then 126 km in 2.5 hours. What is the average speed while moving?"),
        ("average_speed", "easy", "A bus travels 40 km in 1 hour and then 80 km in 2 hours. What is the average speed over the whole route?"),
        ("average_speed", "medium", "A boat moves 24 miles in 2 hours and then 18 miles in 1 hour. What is the average speed for the full trip?"),
        ("average_speed", "medium", "A hiker walks 6 km in 1.5 hours and then 10 km in 2.5 hours. What is the average speed across the hike?"),
        ("average_speed", "hard", "A scooter travels 27 miles in 0.75 hours and then 45 miles in 1.25 hours. What is the average speed across both legs?"),
        ("average_speed", "hard", "A truck covers 132 km in 2 hours and then 198 km in 3 hours. What is the average speed for the total distance?"),
    ]
    rows = []
    for index, (subfamily, difficulty, body) in enumerate(specs, start=1):
        rows.append(
            {
                "prompt_id": f"clean_arithmetic_{index:03d}",
                "task_family": "arithmetic",
                "subfamily": subfamily,
                "difficulty": difficulty,
                "prompt": f"Solve step by step: {body}",
            }
        )
    return rows


def temporal_prompts() -> list[dict[str, Any]]:
    specs = [
        ("query_extraction", "easy", "A happened before B. B happened before C. Which event happened last?"),
        ("query_extraction", "easy", "A happened before B. B happened before C. Who arrived first?"),
        ("query_extraction", "medium", "A happened after B but before C. D happened before B. Which event happened last?"),
        ("query_extraction", "medium", "A happened after B but before C. D happened before B. Which event was second?"),
        ("query_extraction", "hard", "A happened before B. B happened before C. C happened before D. Which stage was third?"),
        ("query_extraction", "hard", "A happened before B. B happened before C. C happened before D. What happened in the middle?"),
        ("query_extraction", "medium", "Noor arrived before Mina. Mina arrived before Joon. Who arrived in the middle?"),
        ("query_extraction", "medium", "Kira left before Leo. Leo left before Mara. Who left earliest?"),
        ("query_extraction", "hard", "A happened after B but before D. C happened before B. Which event happened last?"),
        ("query_extraction", "hard", "A happened after B but before D. C happened before B. Which event was second?"),
        ("full_ordering", "easy", "A happened before B. B happened before C. Order A, B, C from earliest to latest."),
        ("full_ordering", "easy", "Mina arrived before Joon. Joon arrived before Sora. Order Mina, Joon, Sora from earliest to latest."),
        ("full_ordering", "medium", "A happened after B but before C. D happened before B. Order A, B, C, D from earliest to latest."),
        ("full_ordering", "medium", "Task W finished after Task X but before Task Y. Task Z finished before Task X. Order W, X, Y, Z from earliest to latest."),
        ("full_ordering", "hard", "A happened after B but before D. C happened before B. E happened after D. Order A, B, C, D, E from earliest to latest."),
        ("full_ordering", "hard", "Stage P happened before Stage Q. Stage R happened after Stage Q but before Stage S. Order P, Q, R, S from earliest to latest."),
        ("full_ordering", "medium", "Checkpoint A happened before Checkpoint B. Checkpoint C happened after Checkpoint B. Order A, B, C from earliest to latest."),
        ("full_ordering", "medium", "Chapter A was read before Chapter B. Chapter B was read before Chapter C. Order A, B, C from earliest to latest."),
        ("full_ordering", "hard", "A happened before C. B happened after A but before C. D happened after C. Order A, B, C, D from earliest to latest."),
        ("full_ordering", "hard", "Trial A ended after Trial B but before Trial D. Trial C ended before Trial B. Order A, B, C, D from earliest to latest."),
    ]
    rows = []
    for index, (subfamily, difficulty, body) in enumerate(specs, start=1):
        rows.append(
            {
                "prompt_id": f"clean_temporal_{index:03d}",
                "task_family": "temporal_ordering",
                "subfamily": subfamily,
                "difficulty": difficulty,
                "prompt": f"Reason step by step: {body}",
            }
        )
    return rows


def causal_prompts() -> list[dict[str, Any]]:
    specs = [
        ("chain_propagation", "easy", "Reason step by step: If rainfall drops, plant growth slows, and rabbits depend on those plants. What later change is expected for the rabbit population?"),
        ("chain_propagation", "medium", "Reason step by step: If road ice increases, cars slow down, and slower cars create queues. What later change is expected for traffic delay?"),
        ("chain_propagation", "medium", "Reason step by step: If water temperature rises, oxygen falls, and low oxygen stresses fish. What later change is expected for fish stress?"),
        ("chain_propagation", "hard", "Reason step by step: If a factory shutdown reduces supply, prices rise, and high prices reduce purchases. What later change is expected for demand?"),
        ("chain_propagation", "hard", "Reason step by step: If cooling fails, servers throttle, and throttled servers process requests slowly. What later change is expected for request backlog?"),
        ("chain_propagation", "medium", "Reason step by step: If a drought continues, tree growth slows, and weak tree growth reduces canopy. What later change is expected for shade coverage?"),
        ("chain_propagation", "hard", "Reason step by step: If a major upstream spill contaminates the feed stream, filtration becomes overloaded, and overloaded filtration removes less contaminant. What later change is expected for output purity?"),
        ("chain_propagation", "easy", "Reason step by step: If a freezer loses power, ice warms, and warm ice melts. What later change is expected for water collects at the bottom?"),
        ("gated_condition", "easy", "Reason step by step: An alarm triggers only if both the sensor fails and the backup is off. The sensor fails, but the backup is on. Does the alarm trigger?"),
        ("gated_condition", "easy", "Reason step by step: A lamp turns on only if power is available and the bulb is working. Power is available, but the bulb is broken. Does the lamp turn on?"),
        ("gated_condition", "medium", "Reason step by step: Reactant A is absent. Product C forms only if enzyme X is present and substrate Y is available. The indicator changes only if Product C forms. What later state is expected for the indicator?"),
        ("gated_condition", "medium", "Reason step by step: A toy door opens only if the code is correct and the lock has power. The code is correct, but the lock has no power. Does the toy door open?"),
        ("gated_condition", "medium", "Reason step by step: A greenhouse fan starts only if the switch is on and electricity is available. The switch is on, but electricity is unavailable. Does the greenhouse fan start?"),
        ("gated_condition", "hard", "Reason step by step: A rover transmits data only if the antenna is connected and the battery is charged. The antenna is connected, but the battery is empty. Does the rover transmit data?"),
        ("gated_condition", "hard", "Reason step by step: A safety valve releases pressure only if the sensor detects overload and the release channel is clear. The sensor detects overload, but the release channel is blocked. Does the safety valve release pressure?"),
        ("gated_condition", "hard", "Reason step by step: Product C forms only if enzyme X is present and substrate Y is available. Enzyme X is present, but substrate Y is unavailable. Does Product C form?"),
    ]
    rows = []
    for index, (subfamily, difficulty, prompt) in enumerate(specs, start=1):
        rows.append(
            {
                "prompt_id": f"clean_causal_{index:03d}",
                "task_family": "causal_reasoning",
                "subfamily": subfamily,
                "difficulty": difficulty,
                "prompt": prompt,
            }
        )
    return rows


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    prompt = record["prompt"]
    expected: Any = None
    inferred_subfamily: str | None = None
    validation_error: str | None = None

    if record["task_family"] == "arithmetic":
        expected, inferred_subfamily = expected_arithmetic_answer(prompt)
    elif record["task_family"] == "temporal_ordering":
        expected, inferred_subfamily = expected_temporal_answer(prompt)
    elif record["task_family"] == "causal_reasoning":
        rule = get_causal_rule(prompt)
        if rule is None:
            validation_error = "no_causal_rule"
        else:
            expected = rule.expected_label
            inferred_subfamily = rule.subfamily
    else:
        validation_error = "unknown_task_family"

    if expected is None and validation_error is None:
        validation_error = "missing_expected_answer"
    if inferred_subfamily is not None and inferred_subfamily != record["subfamily"]:
        validation_error = f"subfamily_mismatch:{inferred_subfamily}"

    validated = dict(record)
    validated["expected_answer"] = expected
    validated["oracle_subfamily"] = inferred_subfamily
    validated["validation_status"] = "ok" if validation_error is None else "failed"
    validated["validation_error"] = validation_error
    return validated


def build_bank() -> list[dict[str, Any]]:
    rows = arithmetic_prompts() + temporal_prompts() + causal_prompts()
    validated = [validate_record(row) for row in rows]
    failures = [row for row in validated if row["validation_status"] != "ok"]
    if failures:
        messages = [f"{row['prompt_id']}: {row['validation_error']}" for row in failures]
        raise ValueError("Clean prompt bank validation failed:\n" + "\n".join(messages))
    return validated


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def write_memo(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_family = Counter(row["task_family"] for row in records)
    by_subfamily = Counter((row["task_family"], row["subfamily"]) for row in records)
    by_difficulty = Counter(row["difficulty"] for row in records)

    lines = [
        "# Clean Prompt Bank v1",
        "",
        "This bank is designed for prompt-recurrent regime experiments where parser/oracle ambiguity should not dominate the geometry.",
        "",
        "Design constraints:",
        "- Every prompt has a dry-run expected answer.",
        "- Every prompt has an oracle-recognized subfamily.",
        "- Temporal prompts use parser-stable proper names or symbolic entities.",
        "- Causal prompts preserve rule-token coverage from the current causal oracle.",
        "- Arithmetic prompts target the three existing arithmetic mechanisms: combine-subtract, inverse-linear, and average-speed.",
        "",
        f"Total prompts: {len(records)}",
        "",
        "Family counts:",
    ]
    for family, count in sorted(by_family.items()):
        lines.append(f"- {family}: {count}")

    lines.extend(["", "Subfamily counts:"])
    for (family, subfamily), count in sorted(by_subfamily.items()):
        lines.append(f"- {family}/{subfamily}: {count}")

    lines.extend(["", "Difficulty counts:"])
    for difficulty, count in sorted(by_difficulty.items()):
        lines.append(f"- {difficulty}: {count}")

    lines.extend(
        [
            "",
            "Next use:",
            "```bash",
            "PYTHONPATH=src python3 -m tis.build_subfamily_jobs --input data/raw/clean_prompt_bank_v1.jsonl --output data/raw/clean_prompt_bank_v1_jobs.jsonl --repeats 5 --temperature 0.3",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a validated clean prompt bank for regime experiments.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--memo", type=Path, default=DEFAULT_MEMO)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = build_bank()
    write_jsonl(args.output, records)
    write_memo(args.memo, records)
    print(f"wrote {len(records)} prompts to {args.output}")
    print(f"wrote memo to {args.memo}")


if __name__ == "__main__":
    main()
