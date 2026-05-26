from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import requests


def ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def embed(text: str, model: str = "nomic-embed-text") -> list[float]:
    r = requests.post(
        f"{ollama_host()}/api/embeddings",
        json={"model": model, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    v = r.json().get("embedding")
    if not isinstance(v, list):
        raise ValueError("embedding inválido")
    return [float(x) for x in v]


@dataclass
class Chunk:
    id: str
    text: str
    embedding: list[float]
    meta: dict[str, Any]


class JsonlVectorStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def add(self, chunk: Chunk) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(chunk.__dict__, ensure_ascii=False) + "\n")

    def all(self) -> list[Chunk]:
        items: list[Chunk] = []
        for ln in self.path.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            j = json.loads(ln)
            items.append(
                Chunk(
                    id=j["id"],
                    text=j["text"],
                    embedding=j["embedding"],
                    meta=j.get("meta") or {},
                )
            )
        return items

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        qv = np.array(embed(query), dtype=np.float32)
        chunks = self.all()
        if not chunks:
            return []
        M = np.array([c.embedding for c in chunks], dtype=np.float32)
        qn = np.linalg.norm(qv) + 1e-9
        Mn = np.linalg.norm(M, axis=1) + 1e-9
        sims = (M @ qv) / (Mn * qn)
        idx = np.argsort(-sims)[:top_k]
        out: list[dict] = []
        for i in idx:
            c = chunks[int(i)]
            out.append(
                {
                    "id": c.id,
                    "score": float(sims[int(i)]),
                    "text": c.text,
                    "meta": c.meta,
                }
            )
        return out
