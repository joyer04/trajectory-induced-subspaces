from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from tis.generate_ollama_outputs import DEFAULT_SYSTEM, load_existing_record_ids, record_identity
from tis.io_utils import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate raw reasoning outputs from an OpenAI-compatible local server such as vLLM."
    )
    parser.add_argument("--prompts", default="data/raw/clean_prompt_bank_v1_jobs.jsonl")
    parser.add_argument("--output", default="data/raw/model_outputs_clean_prompt_bank_v1.jsonl")
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=512)
    return parser.parse_args()


def completion_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/chat/completions"


def generate_response(
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        completion_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach OpenAI-compatible server at {base_url}: {exc}") from exc

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError(f"No choices returned by server at {base_url}: {body}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str):
        raise RuntimeError(f"No message content returned by server at {base_url}: {body}")
    return content.strip()


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
            if identity is None or identity in existing_ids:
                continue

            record_temperature = float(record.get("temperature", args.temperature))
            raw_output = generate_response(
                args.base_url,
                args.api_key,
                args.model,
                record["prompt"],
                record_temperature,
                args.max_tokens,
            )
            payload = {
                "prompt_id": record["prompt_id"],
                "task_family": record["task_family"],
                "difficulty": record["difficulty"],
                "model": args.model,
                "prompt": record["prompt"],
                "raw_output": raw_output,
                "temperature": record_temperature,
            }
            for extra_key in ["subfamily", "expected_answer", "trial_id", "repeat_index", "job_id", "temperature_tag"]:
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
