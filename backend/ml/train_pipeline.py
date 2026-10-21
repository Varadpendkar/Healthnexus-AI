from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np
try:
    from lightgbm import LGBMRegressor
except Exception:
    LGBMRegressor = None
from sklearn.model_selection import GroupShuffleSplit

from .evaluate import evaluate_ranking, fairness_slice_metrics
from .feature_engineering import build_training_frame
from .model_registry import create_version_tag, save_model_version


def train_and_register(data_dir: Path, models_dir: Path, outputs_dir: Path) -> Dict:
    bundle = build_training_frame(data_dir)
    df = bundle.dataframe.reset_index(drop=True)

    X = df[bundle.feature_columns]
    y = df[bundle.target_column].to_numpy(dtype=float)
    groups = df[bundle.group_column].astype(str).to_numpy()

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups=groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    model = LGBMRegressor(
        objective="regression",
        n_estimators=400,
        learning_rate=0.05,
        num_leaves=63,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    df_eval = df.iloc[test_idx].copy()

    metrics = evaluate_ranking(
        df_eval, y_test, y_pred, group_column=bundle.group_column)
    metrics["fairness_by_gender"] = fairness_slice_metrics(
        df_eval, y_test, y_pred, "gender_raw")
    metrics["fairness_by_region"] = fairness_slice_metrics(
        df_eval, y_test, y_pred, "region_raw")

    version = create_version_tag("ranker")

    artifact = {
        "model": model,
        "feature_cols": bundle.feature_columns,
        "target_col": bundle.target_column,
        "group_col": bundle.group_column,
        "training_rows": int(len(df)),
        "model_version": version,
    }

    metadata = save_model_version(models_dir, artifact, metrics)

    # Keep backward-compatible model file for existing runtime.
    legacy_file = models_dir / "plan_ranker.pkl"
    import pickle
    with open(legacy_file, "wb") as f:
        pickle.dump(artifact, f)

    outputs_dir.mkdir(parents=True, exist_ok=True)
    report_file = outputs_dir / f"training_report_{version}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({"metadata": metadata, "metrics": metrics}, f, indent=2)

    return {
        "model_version": version,
        "metrics": metrics,
        "report_file": str(report_file),
        "legacy_model": str(legacy_file),
    }
