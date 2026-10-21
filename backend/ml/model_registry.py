from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import joblib


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_version_tag(prefix: str = "ranker") -> str:
    return f"{prefix}_v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


def registry_dir(models_root: Path) -> Path:
    path = models_root / "registry"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_model_version(models_root: Path, artifact: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    reg = registry_dir(models_root)
    version = artifact.get("model_version") or create_version_tag()
    version_dir = reg / version
    version_dir.mkdir(parents=True, exist_ok=True)

    model_file = version_dir / "artifact.joblib"
    metrics_file = version_dir / "metrics.json"
    meta_file = version_dir / "meta.json"

    artifact["model_version"] = version
    artifact.setdefault("created_at", _utc_now())

    joblib.dump(artifact, model_file)

    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    metadata = {
        "model_version": version,
        "created_at": _utc_now(),
        "artifact_path": str(model_file),
        "metrics_path": str(metrics_file),
        "primary_metric": metrics.get("ndcg_at_10"),
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    latest_file = reg / "latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def load_latest_artifact(models_root: Path):
    reg = registry_dir(models_root)
    latest_file = reg / "latest.json"
    if not latest_file.exists():
        return None

    with open(latest_file, "r", encoding="utf-8") as f:
        latest = json.load(f)

    artifact_path = Path(latest["artifact_path"])
    if not artifact_path.exists():
        return None

    return joblib.load(artifact_path)


def load_latest_metrics(models_root: Path) -> Dict[str, Any]:
    reg = registry_dir(models_root)
    latest_file = reg / "latest.json"
    if not latest_file.exists():
        return {}

    with open(latest_file, "r", encoding="utf-8") as f:
        latest = json.load(f)

    metrics_path = Path(latest.get("metrics_path", ""))
    if not metrics_path.exists():
        return {"model_version": latest.get("model_version")}

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    metrics["model_version"] = latest.get("model_version")
    return metrics
