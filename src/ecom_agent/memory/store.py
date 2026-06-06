"""Agent memory persistence. `Store` is the port; JSON is the default."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path


class Store(ABC):
    @abstractmethod
    def save(self, session_id: str, record: dict) -> None: ...

    @abstractmethod
    def recall(self, query: str, limit: int = 5) -> list[dict]: ...


class JSONFileStore(Store):
    def __init__(self, root: str | Path = "./.data/memory") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, session_id: str, record: dict) -> None:
        path = self.root / f"{session_id}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        data.append({"ts": time.time(), **record})
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def recall(self, query: str, limit: int = 5) -> list[dict]:
        needle = query.lower()
        hits: list[dict] = []
        for f in sorted(self.root.glob("*.json")):
            for rec in json.loads(f.read_text(encoding="utf-8")):
                if needle in json.dumps(rec, ensure_ascii=False).lower():
                    hits.append(rec)
        return hits[:limit]