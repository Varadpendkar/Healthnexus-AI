#!/usr/bin/env python3
"""Print latest model metrics from registry."""
from ml.model_registry import load_latest_metrics
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def main():
    models_dir = PROJECT_ROOT / "shared" / "models"
    metrics = load_latest_metrics(models_dir)

    if not metrics:
        print("No registered model metrics found.")
        return

    print("\n=== Latest Recommendation Model Metrics ===\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
