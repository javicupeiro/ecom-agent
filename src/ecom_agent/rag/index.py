"""Chroma-backed knowledge base over the SaborMix markdown files, using OpenAI
embeddings and cosine distance. Retrieval filters by language so the UI toggle
brings the right documents.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

AREAS = ("products", "recipes", "support")
LANGS = ("es", "en")


@dataclass
class Hit:
    title: str
    area: str
    lang: str
    path: str
    text: str


def _chunks(text: str) -> list[str]:
    """Split a markdown doc into paragraph-sized chunks for better retrieval."""
    parts, buf = [], []
    for line in text.splitlines():
        if line.strip() == "" and buf:
            parts.append("\n".join(buf).strip())
            buf = []
        else:
            buf.append(line)
    if buf:
        parts.append("\n".join(buf).strip())
    return [p for p in parts if len(p) > 30]


class KnowledgeBase:
    def __init__(
        self,
        persist_dir: str,
        collection: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small",
        top_k: int = 3,
    ) -> None:
        self.top_k = top_k
        embed = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key, model_name=embedding_model
        )
        client = chromadb.PersistentClient(path=persist_dir)
        # The embedding function is bound to the collection on create AND reopen.
        self._collection = client.get_or_create_collection(
            name=collection, embedding_function=embed, metadata={"hnsw:space": "cosine"}
        )

    def ingest(self, root: str) -> int:
        """(Re)build the index from the markdown KB. Idempotent: ids are content hashes."""
        root_path = Path(root)
        ids, docs, metas = [], [], []
        for area in AREAS:
            for lang in LANGS:
                for path in (root_path / area / lang).glob("*.md"):
                    raw = path.read_text(encoding="utf-8")
                    title = raw.splitlines()[0].lstrip("# ").strip() if raw else path.stem
                    for chunk in _chunks(raw):
                        ids.append(hashlib.sha1(f"{path}:{chunk}".encode()).hexdigest())
                        docs.append(chunk)
                        metas.append({"area": area, "lang": lang, "title": title, "path": str(path)})
        if ids:
            self._collection.upsert(ids=ids, documents=docs, metadatas=metas)
        return len(ids)

    def search(self, query: str, lang: str = "es", k: int | None = None) -> list[Hit]:
        res = self._collection.query(
            query_texts=[query], n_results=k or self.top_k, where={"lang": lang}
        )
        hits: list[Hit] = []
        for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
            hits.append(Hit(meta["title"], meta["area"], meta["lang"], meta["path"], doc))
        return hits