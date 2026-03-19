from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

from tis.io_utils import read_jsonl


LABEL_PATTERN = re.compile(r"\b(correct|incorrect|uncertain)\b", re.IGNORECASE)

JUDGE_SYSTEM = (
    "You are labeling reasoning outcomes for a research dataset. "
    "Given a prompt and a final answer, reply with exactly one label: "
    "correct, incorrect, or uncertain."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge trace outcomes with a local Ollama model")
    parser.add_argument("--input", default="data/raw/traces_balanced.jsonl", help="Input traces JSONL")
    parser.add_argument("--output", default="data/raw/traces_balanced_scored.jsonl", help="Output traces JSONL")
    parser.add_argument("--model", default="llama3.2:latest", help="Ollama model name")
    parser.add_argument("--host", default="http://127.0.0.1:11434", help="Ollama host URL")
    return parser.parse_args()


def ask_ollama(host: str, model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "system": JUDGE_SYSTEM,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0},
    }
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["response"].strip()


def extract_label(text: str) -> str:
    match = LABEL_PATTERN.search(text)
    return match.group(1).lower() if match else "uncertain"


def build_prompt(record: dict) -> str:
    return (
        f"Prompt:\n{record['prompt']}\n\n"
        f"Steps:\n" + "\n".join(f"- {step}" for step in record["steps"]) + "\n\n"
        f"Final answer:\n{record['final_answer']}\n\n"
        "Label only whether the final answer is correct, incorrect, or uncertain."
    )


def main() -> None:
    args = parse_args()
    records = read_jsonl(args.input)
    scored: list[dict] = []

    for record in records:
        response = ask_ollama(args.host, args.model, build_prompt(record))
        scored_record = dict(record)
        scored_record["outcome"] = extract_label(response)
        scored.append(scored_record)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in scored:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
