from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import pandas as pd


SYSTEM_PROMPT = (
    "You are naming a reasoning-transition regime from example transitions. "
    "Return a short descriptive phrase only."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Label residual regimes from exemplars")
    parser.add_argument(
        "--family-distribution",
        default="outputs/static_dynamic_bridge_100_minilm/family_residual_distribution.csv",
        help="Family-aware residual distribution CSV",
    )
    parser.add_argument(
        "--family-exemplars",
        default="outputs/static_dynamic_bridge_100_minilm/family_residual_exemplars.csv",
        help="Family-aware residual exemplar CSV",
    )
    parser.add_argument(
        "--output",
        default="outputs/static_dynamic_bridge_100_minilm/residual_regime_labels.csv",
        help="Output CSV for regime labels",
    )
    parser.add_argument("--model", default="llama3.2:latest", help="Ollama model name")
    parser.add_argument("--host", default="http://127.0.0.1:11434", help="Ollama host URL")
    return parser.parse_args()


def ask_ollama(host: str, model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "system": SYSTEM_PROMPT,
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


def main() -> None:
    args = parse_args()
    distribution = pd.read_csv(args.family_distribution)
    exemplars = pd.read_csv(args.family_exemplars)

    rows: list[dict] = []
    for (task_family, outcome, cluster_id), subset in exemplars.groupby(
        ["task_family", "outcome", "residual_cluster"]
    ):
        top_terms = distribution[
            (distribution["task_family"] == task_family)
            & (distribution["outcome"] == outcome)
            & (distribution["residual_cluster"] == cluster_id)
        ]["top_terms"].iloc[0]
        example_lines = subset["transition_text"].head(4).tolist()
        prompt = (
            f"Task family: {task_family}\n"
            f"Outcome: {outcome}\n"
            f"Residual cluster: {cluster_id}\n"
            f"Top terms: {top_terms}\n\n"
            "Example transitions:\n"
            + "\n".join(f"- {text}" for text in example_lines)
            + "\n\nProvide a short name for the transition regime."
        )
        label = ask_ollama(args.host, args.model, prompt)
        rows.append(
            {
                "task_family": task_family,
                "outcome": outcome,
                "residual_cluster": int(cluster_id),
                "top_terms": top_terms,
                "label": label,
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
