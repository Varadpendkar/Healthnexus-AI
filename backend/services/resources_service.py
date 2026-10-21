from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json


class ResourceSearchService:
    def __init__(self, shared_dir: Path):
        self.shared_dir = shared_dir
        self.kb_file = self.shared_dir / "knowledge_base.json"

    def _load(self) -> List[Dict]:
        if not self.kb_file.exists():
            return []
        with open(self.kb_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def search(self, query: str, category: str | None = None, limit: int = 10):
        docs = self._load()
        q = (query or "").strip().lower()
        category = (category or "").strip().lower()

        scored = []
        for doc in docs:
            text = (doc.get("text") or "").lower()
            title = (doc.get("title") or "").lower()
            topics = " ".join(
                doc.get("metadata", {}).get("topics", [])).lower()
            doc_cat = (doc.get("metadata", {}).get("category") or "").lower()

            if category and doc_cat != category:
                continue

            score = 0
            if q:
                score += title.count(q) * 5
                score += topics.count(q) * 3
                score += text.count(q)
            else:
                score = 1

            if score <= 0:
                continue

            scored.append(
                {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "url": doc.get("url"),
                    "category": doc_cat or "general",
                    "snippet": (doc.get("text", "")[:220] + "...") if len(doc.get("text", "")) > 220 else doc.get("text", ""),
                    "score": score,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[: max(1, limit)]
