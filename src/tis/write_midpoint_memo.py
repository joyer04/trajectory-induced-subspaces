from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a midpoint memo from residual-regime and bridge outputs")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Directory containing bridge and residual analysis CSVs",
    )
    parser.add_argument(
        "--output",
        default="notes/midpoint_memo.md",
        help="Markdown memo output path",
    )
    return parser.parse_args()


def top_cluster_shifts(diff_frame: pd.DataFrame, top_k: int = 2) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for task_family, frame in diff_frame.groupby("task_family"):
        ranked = frame.sort_values("incorrect_minus_correct", ascending=False).head(top_k)
        result[task_family] = ranked.to_dict(orient="records")
    return result


def exemplar_map(exemplar_frame: pd.DataFrame, per_cluster: int = 3) -> dict[int, list[str]]:
    mapping: dict[int, list[str]] = {}
    for cluster_id, frame in exemplar_frame.groupby("residual_cluster"):
        mapping[int(cluster_id)] = frame["transition_text"].head(per_cluster).tolist()
    return mapping


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    alignment = pd.read_csv(bridge_dir / "alignment_group_summary.csv")
    failure = pd.read_csv(bridge_dir / "failure_regime_summary.csv")
    residual_var = pd.read_csv(bridge_dir / "residual_pca_variance.csv")
    residual_diff = pd.read_csv(bridge_dir / "residual_regime_differences.csv")
    residual_exemplars = pd.read_csv(bridge_dir / "residual_cluster_exemplars.csv")

    shifts = top_cluster_shifts(residual_diff, top_k=2)
    exemplars = exemplar_map(residual_exemplars, per_cluster=2)

    lines: list[str] = []
    lines.append("# Midpoint Memo")
    lines.append("")
    lines.append("## Core question")
    lines.append("")
    lines.append(
        "Can LLM reasoning be explained as movement along pre-existing static semantic axes, "
        "or does the trajectory itself induce additional local geometric structure?"
    )
    lines.append("")
    lines.append("## Current answer")
    lines.append("")
    lines.append(
        "Current evidence supports partial static explainability but not static sufficiency. "
        "Across the 100-trace MiniLM analysis, static-axis alignment remains modest while large residual structure remains."
    )
    lines.append("")
    lines.append("## Bridge summary")
    lines.append("")
    for _, row in alignment.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: "
            f"best_abs_alignment={row['best_abs_alignment']:.3f}, residual_energy={row['residual_energy']:.3f}"
        )
    lines.append("")
    lines.append("## Residual structure")
    lines.append("")
    top_components = residual_var.head(5)
    component_summary = ", ".join(
        f"{row['component']}={row['explained_variance_ratio']:.3f}"
        for _, row in top_components.iterrows()
    )
    lines.append(f"- Residual PCA top components: {component_summary}")
    lines.append("- Residual variance does not collapse after static-axis projection.")
    lines.append("")
    lines.append("## Failure-regime observations")
    lines.append("")
    for _, row in failure.iterrows():
        lines.append(
            f"- `{row['task_family']}`: "
            f"correct_residual={row['correct_residual_norm_mean']:.3f}, "
            f"incorrect_residual={row['incorrect_residual_norm_mean']:.3f}, "
            f"same_mode_cluster={bool(row['same_mode_cluster'])}"
        )
    lines.append("")
    lines.append("## Cluster-level differences")
    lines.append("")
    for task_family, rows in shifts.items():
        lines.append(f"- `{task_family}`:")
        for row in rows:
            cluster_id = int(row["residual_cluster"])
            diff = float(row["incorrect_minus_correct"])
            lines.append(
                f"  residual cluster {cluster_id} is shifted toward incorrect by {diff:.3f}"
            )
            if cluster_id in exemplars:
                for exemplar in exemplars[cluster_id]:
                    lines.append(f"  exemplar: {exemplar}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The strongest reading at this stage is that reasoning uses some static manifold structure, "
        "but dynamic transitions retain family-sensitive residual geometry. "
        "Failure appears less like global noise and more like entry into different residual regimes."
    )
    lines.append("")
    lines.append("## Remaining limits")
    lines.append("")
    lines.append("- Static axes are limited to a low-rank PCA basis.")
    lines.append("- Residual clusters are unsupervised and may still mix multiple transition types.")
    lines.append("- Outcome labels are model-judged, not gold-labeled.")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "Move from residual-cluster presence to residual-cluster semantics: "
        "label the residual regimes and test whether the same regime recurs across prompts within each family."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
