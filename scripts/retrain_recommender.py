#!/usr/bin/env python3
"""Manual retraining hook script (scheduler-friendly)."""
import subprocess
from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    train_script = root / "scripts" / "train_recommender.py"
    subprocess.run(["python", str(train_script)], check=True)
