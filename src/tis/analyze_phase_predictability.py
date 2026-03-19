from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate outcome predictability from phase-wise regime features")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory with trace_phase_paths.csv",
    )
    parser.add_argument("--max-folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def evaluate_classifier(frame: pd.DataFrame, feature_columns: list[str], max_folds: int, seed: int) -> tuple[float, float]:
    model_frame = frame[frame["outcome"].isin(["correct", "incorrect"])].copy()
    if model_frame["outcome"].nunique() < 2:
        return float("nan"), float("nan")

    y = (model_frame["outcome"] == "correct").astype(int).to_numpy()
    class_counts = model_frame["outcome"].value_counts()
    n_splits = min(max_folds, int(class_counts.min()))
    if n_splits < 2:
        return float("nan"), float("nan")

    X = pd.get_dummies(model_frame[feature_columns].astype(str), drop_first=False)
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    accuracies: list[float] = []
    balanced: list[float] = []

    for train_idx, test_idx in splitter.split(X, y):
        model = LogisticRegression(max_iter=2000)
        model.fit(X.iloc[train_idx], y[train_idx])
        preds = model.predict(X.iloc[test_idx])
        accuracies.append(accuracy_score(y[test_idx], preds))
        balanced.append(balanced_accuracy_score(y[test_idx], preds))

    return float(np.mean(accuracies)), float(np.mean(balanced))


def late_cluster_rule_accuracy(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    valid = frame[frame["late_cluster"].astype(str) != "NA"].copy()
    for task_family, family_frame in valid.groupby("task_family"):
        for feature_set, columns in {
            "early_only": ["early_cluster"],
            "early_middle": ["early_cluster", "middle_cluster"],
        }.items():
            grouped = family_frame.groupby(columns)
            correct = 0
            total = 0
            for _, group in grouped:
                mode_cluster = group["late_cluster"].mode().iloc[0]
                correct += int((group["late_cluster"] == mode_cluster).sum())
                total += int(len(group))
            rows.append(
                {
                    "task_family": task_family,
                    "feature_set": feature_set,
                    "late_cluster_rule_accuracy": correct / total if total else float("nan"),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    paths = pd.read_csv(bridge_dir / "trace_phase_paths.csv")

    rows: list[dict] = []
    for task_family, family_frame in paths.groupby("task_family"):
        for feature_set, columns in {
            "early_only": ["early_cluster"],
            "early_middle": ["early_cluster", "middle_cluster"],
            "full_path": ["early_cluster", "middle_cluster", "late_cluster"],
        }.items():
            accuracy, balanced = evaluate_classifier(family_frame, columns, args.max_folds, args.seed)
            rows.append(
                {
                    "task_family": task_family,
                    "feature_set": feature_set,
                    "cv_accuracy": accuracy,
                    "cv_balanced_accuracy": balanced,
                }
            )

    predictability = pd.DataFrame(rows)
    predictability.to_csv(bridge_dir / "phase_predictability_summary.csv", index=False)

    late_accuracy = late_cluster_rule_accuracy(paths)
    late_accuracy.to_csv(bridge_dir / "late_cluster_predictability.csv", index=False)


if __name__ == "__main__":
    main()
