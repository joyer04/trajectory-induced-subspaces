from __future__ import annotations

from typing import Iterable

import numpy as np


def flatten_steps(traces: Iterable[dict]) -> tuple[list[str], list[dict]]:
    step_texts: list[str] = []
    step_index: list[dict] = []

    for trace in traces:
        steps = trace.get("steps", [])
        for step_position, step_text in enumerate(steps):
            step_texts.append(step_text)
            step_index.append(
                {
                    "trace_id": trace["trace_id"],
                    "prompt_id": trace["prompt_id"],
                    "task_family": trace["task_family"],
                    "subfamily": trace.get("subfamily", ""),
                    "model": trace.get("model", "unknown"),
                    "difficulty": trace.get("difficulty", "unknown"),
                    "outcome": trace.get("outcome", "uncertain"),
                    "trial_id": trace.get("trial_id", ""),
                    "repeat_index": trace.get("repeat_index", ""),
                    "temperature": trace.get("temperature", ""),
                    "temperature_tag": trace.get("temperature_tag", ""),
                    "step_position": step_position,
                    "step_text": step_text,
                }
            )

    return step_texts, step_index


def build_delta_vectors(
    embeddings: np.ndarray,
    step_index: list[dict],
) -> tuple[np.ndarray, list[dict]]:
    deltas: list[np.ndarray] = []
    delta_index: list[dict] = []

    trace_to_rows: dict[str, list[int]] = {}
    for row_idx, row in enumerate(step_index):
        trace_to_rows.setdefault(row["trace_id"], []).append(row_idx)

    for trace_id, row_indices in trace_to_rows.items():
        ordered = sorted(row_indices, key=lambda idx: step_index[idx]["step_position"])
        for local_idx in range(1, len(ordered)):
            prev_idx = ordered[local_idx - 1]
            curr_idx = ordered[local_idx]
            delta = embeddings[curr_idx] - embeddings[prev_idx]
            deltas.append(delta)
            delta_index.append(
                {
                    "trace_id": trace_id,
                    "prompt_id": step_index[curr_idx]["prompt_id"],
                    "task_family": step_index[curr_idx]["task_family"],
                    "subfamily": step_index[curr_idx].get("subfamily", ""),
                    "model": step_index[curr_idx]["model"],
                    "difficulty": step_index[curr_idx]["difficulty"],
                    "outcome": step_index[curr_idx]["outcome"],
                    "trial_id": step_index[curr_idx].get("trial_id", ""),
                    "repeat_index": step_index[curr_idx].get("repeat_index", ""),
                    "temperature": step_index[curr_idx].get("temperature", ""),
                    "temperature_tag": step_index[curr_idx].get("temperature_tag", ""),
                    "from_step_position": step_index[prev_idx]["step_position"],
                    "to_step_position": step_index[curr_idx]["step_position"],
                    "from_step_text": step_index[prev_idx]["step_text"],
                    "to_step_text": step_index[curr_idx]["step_text"],
                }
            )

    if not deltas:
        return np.empty((0, embeddings.shape[1]), dtype=np.float32), delta_index

    return np.asarray(deltas, dtype=np.float32), delta_index
