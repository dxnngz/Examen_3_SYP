from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Optional

import requests
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from store import Chunk, JsonlVectorStore, embed, ollama_host

app = FastAPI(
    title="RAG Empaquetado — DAM2",
    description="Servicio RAG+IA en contenedor Docker con API key y volumen persistente.",
)

DATA = Path(__file__).resolve().parent / "data"
STORE = JsonlVectorStore(DATA / "index.jsonl")
API_KEY = os.environ.get("RAG_API_KEY", "dam2-secret-2026")


def chunk_text(text: str, size: int = 600, overlap: int = 100) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    out: list[str] = []
    i = 0
    while i < len(text):
        out.append(text[i : i + size])
        i += max(1, size - overlap)
    return out


def generate(prompt: str, model=None, system=None) -> str:
    model = model or os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
    payload: dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    r = requests.post(f"{ollama_host()}/api/generate", json=payload, timeout=180)
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=r.text)
    return (r.json().get("response") or "").strip()


def verify_key(x_api_key) -> None:
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida (header X-API-Key)")


class IngestBody(BaseModel):
    title: str
    text: str


class AskBody(BaseModel):
    question: str
    top_k: int = 5


@app.delete("/reset")
def reset_index(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    verify_key(x_api_key)
    STORE.path.write_text("", encoding="utf-8")
    return {"status": "ok", "message": "Índice vaciado"}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "chunks_indexed": len(STORE.all()),
        "ollama_host": ollama_host(),
        "model": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
    }


@app.post("/ingest")
def ingest_api(body: IngestBody, x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    verify_key(x_api_key)
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Título vacío")
    chunks = chunk_text(body.text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Texto vacío")
    for ix, t in enumerate(chunks):
        cid = hashlib.sha256(f"{body.title}:{ix}:{t}".encode()).hexdigest()[:16]
        STORE.add(
            Chunk(
                id=cid,
                text=t,
                embedding=embed(t),
                meta={"title": body.title, "chunk": ix},
            )
        )
    return {"status": "ok", "chunks": len(chunks)}


@app.post("/ask")
def ask_api(body: AskBody, x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    verify_key(x_api_key)
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Pregunta vacía")
    ctx = STORE.search(body.question, top_k=max(1, min(15, int(body.top_k))))
    if not ctx:
        return {"answer": "Sin contexto indexado. Llama primero a POST /ingest.", "citations": []}

    blocks: list[str] = []
    citations: list[dict] = []
    for i, c in enumerate(ctx, start=1):
        title = (c.get("meta") or {}).get("title") or "fuente"
        chunk = (c.get("meta") or {}).get("chunk")
        cite = f"[C{i}] {title}#{chunk}"
        citations.append(
            {
                "ref": f"C{i}",
                "title": title,
                "chunk": chunk,
                "score": c.get("score"),
            }
        )
        blocks.append(f"{cite}\n{c.get('text')}")

    system = "Responde solo con el CONTEXTO. Cita [C1], [C2]. Español, claro y breve."
    prompt = (
        "CONTEXTO:\n\n"
        + "\n\n---\n\n".join(blocks)
        + "\n\nPREGUNTA:\n"
        + body.question
        + "\n\nRESPUESTA:"
    )
    return {"answer": generate(prompt, system=system), "citations": citations}
