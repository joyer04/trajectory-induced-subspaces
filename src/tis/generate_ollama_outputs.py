from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from tis.io_utils import read_jsonl


DEFAULT_SYSTEM = (
    "You are generating reasoning traces for a research dataset. "
    "Answer with concise numbered steps, then a final line in the form "
    "'Final answer: ...'. Do not add extra commentary."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate raw reasoning outputs from a local Ollama model")
    parser.add_argument(
        "--prompts",
        default="data/raw/prompts_seed.jsonl",
        help="Prompt bank JSONL path",
    )
    parser.add_argument(
        "--output",
        default="data/raw/model_outputs.jsonl",
        help="Raw model output JSONL path",
    )
    parser.add_argument(
        "--model",
        default="qwen3:4b",
        help="Ollama model name",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of prompts to run",
    )
    parser.add_argument(
        "--host",
        default="http://127.0.0.1:11434",
        help="Ollama host URL",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rewrite the output file instead of appending only missing prompts",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Pause between requests",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for Ollama generation",
    )
    return parser.parse_args()


def ollama_generate(host: str, model: str, prompt: str, temperature: float) -> str:
    payload = {
        "model": model,
        "system": DEFAULT_SYSTEM,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach Ollama at {host}: {exc}") from exc
    return body["response"].strip()


def record_identity(record: dict) -> str | None:
    if "job_id" in record:
        return str(record["job_id"])
    if "prompt_id" in record:
        return str(record["prompt_id"])
    return None


def load_existing_record_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()
    identities: set[str] = set()
    for record in read_jsonl(output_path):
        identity = record_identity(record)
        if identity is not None:
            identities.add(identity)
    return identities


def main() -> None:
    args = parse_args()
    prompt_records = read_jsonl(args.prompts)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    existing_ids = set() if args.overwrite else load_existing_record_ids(output_path)
    write_mode = "w" if args.overwrite else "a"
    written = 0

    with output_path.open(write_mode, encoding="utf-8") as handle:
        for record in prompt_records:
            if written >= args.limit:
                break
            identity = record_identity(record)
            if identity is None:
                continue
            if identity in existing_ids:
                continue

            record_temperature = float(record.get("temperature", args.temperature))
            raw_output = ollama_generate(args.host, args.model, record["prompt"], record_temperature)
            payload = {
                "prompt_id": record["prompt_id"],
                "task_family": record["task_family"],
                "difficulty": record["difficulty"],
                "model": args.model,
                "prompt": record["prompt"],
                "raw_output": raw_output,
                "temperature": record_temperature,
            }
            for extra_key in ["trial_id", "repeat_index", "job_id", "temperature_tag"]:
                if extra_key in record:
                    payload[extra_key] = record[extra_key]
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
            handle.flush()
            written += 1
            existing_ids.add(identity)

            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)


if __name__ == "__main__":
    main()
