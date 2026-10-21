#!/usr/bin/env python3
"""Train and register HealthNexus recommendation model."""
from ml.train_pipeline import train_and_register
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def main():
    data_dir = PROJECT_ROOT / "shared" / "data"
    models_dir = PROJECT_ROOT / "shared" / "models"
    outputs_dir = PROJECT_ROOT / "outputs" / "ml"

    print("\n=== HealthNexus ML Training ===\n")
    result = train_and_register(data_dir, models_dir, outputs_dir)

    print("✅ Training complete")
    print(f"Model version: {result['model_version']}")
    print(f"NDCG@10: {result['metrics'].get('ndcg_at_10', 0):.4f}")
    print(f"Precision@5: {result['metrics'].get('precision_at_5', 0):.4f}")
    print(f"Coverage@5: {result['metrics'].get('coverage_at_5', 0):.4f}")
    print(f"Report: {result['report_file']}")


if __name__ == "__main__":
    main()
