from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from services.bill_analyzer import analyze_bill_file


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class BillJobManager:
    def __init__(self, uploads_dir: Path, jobs_dir: Path):
        self.uploads_dir = uploads_dir
        self.jobs_dir = jobs_dir
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def _job_file(self, job_id: str) -> Path:
        return self.jobs_dir / f"{job_id}.json"

    def _save_status(self, job_id: str, payload: Dict):
        with open(self._job_file(job_id), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def _run_job(self, job_id: str, file_path: Path, extension: str):
        try:
            with open(file_path, "rb") as fp:
                result = analyze_bill_file(fp, extension)

            payload = {
                "job_id": job_id,
                "status": "completed" if result.get("status") != "error" else "failed",
                "updated_at": _now_iso(),
                "result": result,
                "progress": 100,
            }
            self._save_status(job_id, payload)
        except Exception as e:
            payload = {
                "job_id": job_id,
                "status": "failed",
                "updated_at": _now_iso(),
                "error": str(e),
                "progress": 100,
            }
            self._save_status(job_id, payload)
        finally:
            try:
                file_path.unlink(missing_ok=True)
            except Exception:
                pass

    def submit(self, filename: str, data: bytes) -> Dict:
        extension = Path(filename).suffix.lower()
        job_id = str(uuid.uuid4())
        file_path = self.uploads_dir / f"{job_id}{extension}"

        with open(file_path, "wb") as f:
            f.write(data)

        queued = {
            "job_id": job_id,
            "status": "processing",
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "progress": 10,
        }
        self._save_status(job_id, queued)

        thread = threading.Thread(target=self._run_job, args=(
            job_id, file_path, extension), daemon=True)
        thread.start()

        return queued

    def status(self, job_id: str) -> Dict:
        job_file = self._job_file(job_id)
        if not job_file.exists():
            return {"job_id": job_id, "status": "not_found", "progress": 0}
        with open(job_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload

    def result(self, job_id: str) -> Dict:
        payload = self.status(job_id)
        if payload.get("status") == "not_found":
            return payload
        if payload.get("status") != "completed":
            return payload
        result = payload.get("result", {})
        return {"job_id": job_id, "status": payload.get("status"), **result}
