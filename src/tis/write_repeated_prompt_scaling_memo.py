from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare repeated-prompt recurrence across experiment scales")
    parser.add_argument("--small-bridge-dir", default="outputs/static_dynamic_bridge_repeated_minilm")
    parser.add_argument("--large-bridge-dir", default="outputs/static_dynamic_bridge_repeated_4x5_minilm")
    parser.add_argument("--output", default="notes/repeated_prompt_scaling_memo.md")
    return parser.parse_args()


def load_same_prompt_gap(bridge_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    global_summary = pd.read_csv(bridge_dir / "prompt_level_distance_summary.csv")
    family_summary = pd.read_csv(bridge_dir / "prompt_level_same_prompt_summary.csv")
    nn_summary = pd.read_csv(bridge_dir / "prompt_level_nearest_neighbor_summary.csv")

    global_same = global_summary[
        (global_summary["same_prompt"]) & (global_summary["same_family"]) & (global_summary["same_outcome"])
    ].iloc[0]
    global_diff = global_summary[
        (~global_summary["same_prompt"]) & (global_summary["same_family"]) & (global_summary["same_outcome"])
    ].iloc[0]
    global_gap = pd.DataFrame(
        [
            {
                "js_same_prompt": float(global_same["js_divergence"]),
                "js_diff_prompt": float(global_diff["js_divergence"]),
                "js_gap": float(global_diff["js_divergence"] - global_same["js_divergence"]),
                "tv_same_prompt": float(global_same["tv_distance"]),
                "tv_diff_prompt": float(global_diff["tv_distance"]),
                "tv_gap": float(global_diff["tv_distance"] - global_same["tv_distance"]),
            }
        ]
    )

    family_same = family_summary[family_summary["same_outcome"]].copy()
    same_prompt = (
        family_same[family_same["same_prompt"]][["task_family", "js_divergence", "tv_distance"]]
        .rename(columns={"js_divergence": "js_same_prompt", "tv_distance": "tv_same_prompt"})
    )
    diff_prompt = (
        family_same[~family_same["same_prompt"]][["task_family", "js_divergence", "tv_distance"]]
        .rename(columns={"js_divergence": "js_diff_prompt", "tv_distance": "tv_diff_prompt"})
    )
    family_gap = same_prompt.merge(diff_prompt, on="task_family", how="inner")
    family_gap["js_gap"] = family_gap["js_diff_prompt"] - family_gap["js_same_prompt"]
    family_gap["tv_gap"] = family_gap["tv_diff_prompt"] - family_gap["tv_same_prompt"]

    return global_gap, family_gap, nn_summary


def main() -> None:
    args = parse_args()
    small_dir = Path(args.small_bridge_dir)
    large_dir = Path(args.large_bridge_dir)

    small_global, small_family, small_nn = load_same_prompt_gap(small_dir)
    large_global, large_family, large_nn = load_same_prompt_gap(large_dir)

    family_compare = small_family.merge(
        large_family,
        on="task_family",
        suffixes=("_small", "_large"),
    )
    family_compare["js_gap_change"] = family_compare["js_gap_large"] - family_compare["js_gap_small"]
    family_compare["tv_gap_change"] = family_compare["tv_gap_large"] - family_compare["tv_gap_small"]
    family_compare = family_compare.sort_values("js_gap_large", ascending=False)

    nn_compare = small_nn.merge(large_nn, on="task_family", suffixes=("_small", "_large"))
    nn_compare["same_family_nn_change"] = nn_compare["same_family_nn_large"] - nn_compare["same_family_nn_small"]
    nn_compare["same_outcome_nn_change"] = nn_compare["same_outcome_nn_large"] - nn_compare["same_outcome_nn_small"]

    lines: list[str] = []
    lines.append("# Repeated Prompt Scaling Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Compare the smaller repeated-prompt experiment (2 prompts/family x 5 repeats) "
        "against the larger repeated-prompt experiment (4 prompts/family x 5 repeats)."
    )
    lines.append("")
    lines.append("## Global same-prompt advantage")
    lines.append("")
    lines.append(
        "- 2x5: "
        f"same_prompt_js={small_global.loc[0, 'js_same_prompt']:.3f}, "
        f"diff_prompt_js={small_global.loc[0, 'js_diff_prompt']:.3f}, "
        f"gap={small_global.loc[0, 'js_gap']:.3f}"
    )
    lines.append(
        "- 4x5: "
        f"same_prompt_js={large_global.loc[0, 'js_same_prompt']:.3f}, "
        f"diff_prompt_js={large_global.loc[0, 'js_diff_prompt']:.3f}, "
        f"gap={large_global.loc[0, 'js_gap']:.3f}"
    )
    lines.append("")
    lines.append("## Family-level same-prompt advantage")
    lines.append("")
    for _, row in family_compare.iterrows():
        lines.append(
            f"- `{row['task_family']}`: "
            f"2x5_gap={row['js_gap_small']:.3f}, "
            f"4x5_gap={row['js_gap_large']:.3f}, "
            f"delta={row['js_gap_change']:.3f}"
        )
    lines.append("")
    lines.append("## Nearest-neighbor shifts")
    lines.append("")
    for _, row in nn_compare.sort_values("same_family_nn_large", ascending=False).iterrows():
        lines.append(
            f"- `{row['task_family']}`: "
            f"same_family_nn {row['same_family_nn_small']:.3f} -> {row['same_family_nn_large']:.3f}, "
            f"same_outcome_nn {row['same_outcome_nn_small']:.3f} -> {row['same_outcome_nn_large']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "If the 4x5 run keeps or increases the same-prompt advantage over different prompts within the same family "
        "then the residual regime signal is less likely to be a fluke of tiny prompt support."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
