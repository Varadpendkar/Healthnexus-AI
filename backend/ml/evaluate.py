from __future__ import annotations

from collections import defaultdict
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics import precision_score


def ndcg_at_k_for_user(relevances: np.ndarray, scores: np.ndarray, k: int = 10) -> float:
    if len(relevances) == 0:
        return 0.0

    order = np.argsort(scores)[::-1][:k]
    rel_sorted = relevances[order]
    gains = (2 ** rel_sorted - 1) / np.log2(np.arange(2, len(rel_sorted) + 2))
    dcg = float(np.sum(gains))

    ideal_order = np.argsort(relevances)[::-1][:k]
    rel_ideal = relevances[ideal_order]
    ideal_gains = (2 ** rel_ideal - 1) / \
        np.log2(np.arange(2, len(rel_ideal) + 2))
    idcg = float(np.sum(ideal_gains))

    return dcg / idcg if idcg > 0 else 0.0


def precision_at_k_for_user(relevances: np.ndarray, scores: np.ndarray, k: int = 5, threshold: float = 0.5) -> float:
    if len(relevances) == 0:
        return 0.0
    order = np.argsort(scores)[::-1][:k]
    rel = relevances[order]
    return float(np.mean((rel >= threshold).astype(float)))


def evaluate_ranking(df_eval: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray, group_column: str = "user_id") -> Dict:
    grouped = defaultdict(list)

    for idx, uid in enumerate(df_eval[group_column].astype(str).tolist()):
        grouped[uid].append(idx)

    ndcg5, ndcg10, p5 = [], [], []
    coverage_pool = []

    for _, idxs in grouped.items():
        rel = y_true[idxs]
        sc = y_pred[idxs]
        ndcg5.append(ndcg_at_k_for_user(rel, sc, k=5))
        ndcg10.append(ndcg_at_k_for_user(rel, sc, k=10))
        p5.append(precision_at_k_for_user(rel, sc, k=5))

        order = np.argsort(sc)[::-1][:5]
        if len(order) > 0:
            coverage_pool.extend(np.array(idxs)[order].tolist())

    overall_bin_true = (y_true >= 0.5).astype(int)
    overall_bin_pred = (y_pred >= 0.5).astype(int)
    overall_precision = float(precision_score(
        overall_bin_true, overall_bin_pred, zero_division=0))

    coverage = len(set(coverage_pool)) / max(len(y_true), 1)

    return {
        "num_eval_rows": int(len(df_eval)),
        "num_users": int(len(grouped)),
        "ndcg_at_5": float(np.mean(ndcg5)) if ndcg5 else 0.0,
        "ndcg_at_10": float(np.mean(ndcg10)) if ndcg10 else 0.0,
        "precision_at_5": float(np.mean(p5)) if p5 else 0.0,
        "precision_binary": overall_precision,
        "coverage_at_5": float(coverage),
    }


def fairness_slice_metrics(df_eval: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray, slice_col: str) -> Dict:
    if slice_col not in df_eval.columns:
        return {}

    df_local = df_eval.reset_index(drop=True)
    out = {}
    for value, sdf in df_local.groupby(slice_col):
        idx = sdf.index.to_numpy(dtype=int)
        metrics = evaluate_ranking(
            sdf, y_true[idx], y_pred[idx], group_column="user_id")
        out[str(value)] = {
            "ndcg_at_10": metrics["ndcg_at_10"],
            "precision_at_5": metrics["precision_at_5"],
            "coverage_at_5": metrics["coverage_at_5"],
        }
    return out
