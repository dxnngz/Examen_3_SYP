from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from store import Chunk, JsonlVectorStore, embed, ollama_host

app = FastAPI(title="Asistente DAM2 — RAG + IA")

DATA = Path(__file__).resolve().parent / "data"
STORE = JsonlVectorStore(DATA / "index.jsonl")

DEFAULT_SYSTEM = (
    "Eres un tutor de DAM2 para la asignatura Servicios y Procesos. "
    "Responde SOLO con el CONTEXTO recuperado. Si falta información, dilo. "
    "Incluye referencias [C1], [C2] en la respuesta."
)


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


class IngestBody(BaseModel):
    title: str
    text: str


class AskBody(BaseModel):
    question: str
    top_k: int = 4


@app.get("/", response_class=HTMLResponse)
def chat_ui() -> str:
    return """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Asistente DAM2 — RAG + IA</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0f172a;
      --panel: #1e293b;
      --t: #f1f5f9;
      --m: #94a3b8;
      --a: #38bdf8;
      --user: #6366f1;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: system-ui, sans-serif;
      background: radial-gradient(ellipse at top, #1e3a5f 0%, var(--bg) 55%);
      color: var(--t);
      display: flex;
      flex-direction: column;
    }
    header {
      padding: 16px 20px;
      border-bottom: 1px solid rgba(255,255,255,.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }
    header h1 { margin: 0; font-size: 1.2rem; }
    header p { margin: 4px 0 0; color: var(--m); font-size: 13px; }
    .layout {
      flex: 1;
      display: grid;
      grid-template-columns: 320px 1fr;
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
      gap: 0;
      min-height: 0;
    }
    aside {
      border-right: 1px solid rgba(255,255,255,.08);
      padding: 16px;
      background: rgba(0,0,0,.2);
    }
    aside label { font-size: 12px; color: var(--m); display: block; margin-bottom: 4px; }
    aside input, aside textarea, aside button {
      width: 100%;
      margin-bottom: 10px;
      padding: 10px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,.12);
      background: var(--panel);
      color: var(--t);
      font: inherit;
    }
    aside textarea { min-height: 120px; resize: vertical; }
    aside button {
      background: rgba(56,189,248,.2);
      border-color: var(--a);
      cursor: pointer;
      font-weight: 600;
    }
    .chat {
      display: flex;
      flex-direction: column;
      min-height: 70vh;
    }
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .msg {
      max-width: 85%;
      padding: 12px 14px;
      border-radius: 14px;
      line-height: 1.5;
      font-size: 14px;
    }
    .msg.user {
      align-self: flex-end;
      background: var(--user);
    }
    .msg.ai {
      align-self: flex-start;
      background: var(--panel);
      border: 1px solid rgba(255,255,255,.1);
    }
    .cites {
      margin-top: 10px;
      font-size: 11px;
      color: var(--m);
      border-top: 1px solid rgba(255,255,255,.08);
      padding-top: 8px;
    }
    .input-row {
      display: flex;
      gap: 10px;
      padding: 16px 20px;
      border-top: 1px solid rgba(255,255,255,.08);
    }
    .input-row input {
      flex: 1;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,.15);
      background: var(--panel);
      color: var(--t);
      font: inherit;
    }
    .input-row button {
      padding: 12px 20px;
      border-radius: 12px;
      border: none;
      background: var(--a);
      color: #0f172a;
      font-weight: 700;
      cursor: pointer;
    }
    @media (max-width: 800px) {
      .layout { grid-template-columns: 1fr; }
      aside { border-right: none; border-bottom: 1px solid rgba(255,255,255,.08); }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Asistente DAM2</h1>
      <p>RAG + IA (Ollama): recupera apuntes y genera respuesta con citas [C1]…</p>
    </div>
  </header>
  <div class="layout">
    <aside>
      <label>Título del documento</label>
      <input id="docTitle" value="Despliegue web — apuntes" />
      <label>Texto a indexar</label>
      <textarea id="docText">Para desplegar una API FastAPI en producción usamos Gunicorn o Uvicorn detrás de Nginx como reverse proxy. Docker Compose define servicios, redes y volúmenes. systemd permite arrancar el stack al boot con systemctl enable. RAG combina búsqueda vectorial con un LLM local (Ollama) para respuestas fundamentadas.</textarea>
      <button type="button" onclick="doIngest()">Indexar apuntes</button>
      <p id="ingStatus" style="font-size:12px;color:var(--m)"></p>
    </aside>
    <section class="chat">
      <div class="messages" id="messages">
        <div class="msg ai">Hola. Indexa tus apuntes a la izquierda y pregúntame sobre despliegue, Docker o RAG.</div>
      </div>
      <div class="input-row">
        <input id="question" placeholder="Ej: ¿Cómo expongo FastAPI con Nginx?" />
        <button type="button" onclick="doAsk()">Preguntar</button>
      </div>
    </section>
  </div>
  <script>
    const messages = document.getElementById('messages');
    function addMsg(text, role, citations) {
      const d = document.createElement('div');
      d.className = 'msg ' + role;
      d.textContent = text;
      if (citations && citations.length) {
        const c = document.createElement('div');
        c.className = 'cites';
        c.textContent = 'Fuentes: ' + citations.map(x =>
          `[${x.ref}] ${x.title}#${x.chunk} (${(x.score*100).toFixed(0)}%)`
        ).join(' · ');
        d.appendChild(c);
      }
      messages.appendChild(d);
      messages.scrollTop = messages.scrollHeight;
      return d;
    }
    async function post(path, body) {
      const r = await fetch(path, {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: JSON.stringify(body)
      });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(j.detail || 'Error');
      return j;
    }
    async function doIngest() {
      document.getElementById('ingStatus').textContent = 'Indexando...';
      try {
        const j = await post('/ingest', {
          title: document.getElementById('docTitle').value,
          text: document.getElementById('docText').value
        });
        document.getElementById('ingStatus').textContent =
          'OK — ' + j.chunks + ' chunks indexados.';
      } catch (e) {
        document.getElementById('ingStatus').textContent = e.message;
      }
    }
    async function doAsk() {
      const q = document.getElementById('question').value.trim();
      if (!q) return;
      addMsg(q, 'user');
      document.getElementById('question').value = '';
      const loading = addMsg('Pensando...', 'ai');
      try {
        const j = await post('/ask', { question: q, top_k: 4 });
        loading.textContent = j.answer;
        if (j.citations && j.citations.length) {
          const c = document.createElement('div');
          c.className = 'cites';
          c.textContent = 'Fuentes: ' + j.citations.map(x =>
            `[${x.ref}] ${x.title}#${x.chunk} (${(x.score*100).toFixed(0)}%)`
          ).join(' · ');
          loading.appendChild(c);
        }
      } catch (e) {
        loading.textContent = e.message;
      }
    }
    document.getElementById('question').addEventListener('keydown', e => {
      if (e.key === 'Enter') doAsk();
    });
  </script>
</body>
</html>"""


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
        "chunks_indexed": len(STORE.all()),
    }


@app.delete("/reset")
def reset_index() -> dict:
    STORE.path.write_text("", encoding="utf-8")
    return {"status": "ok", "message": "Índice vaciado"}


@app.post("/ingest")
def ingest(body: IngestBody) -> dict:
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
def ask(body: AskBody) -> dict:
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Pregunta vacía")
    ctx = STORE.search(body.question, top_k=max(1, min(10, int(body.top_k))))
    if not ctx:
        return {
            "answer": "No hay apuntes indexados. Usa el panel izquierdo para ingestar texto.",
            "citations": [],
        }

    blocks: list[str] = []
    citations: list[dict] = []
    for i, c in enumerate(ctx, start=1):
        title = (c.get("meta") or {}).get("title") or "fuente"
        chunk = (c.get("meta") or {}).get("chunk")
        cite = f"[C{i}] {title}#{chunk} id={c.get('id')}"
        citations.append(
            {
                "ref": f"C{i}",
                "title": title,
                "chunk": chunk,
                "id": c.get("id"),
                "score": c.get("score"),
            }
        )
        blocks.append(f"{cite}\n{c.get('text')}")

    prompt = (
        "CONTEXTO:\n\n"
        + "\n\n---\n\n".join(blocks)
        + "\n\nPREGUNTA:\n"
        + body.question
        + "\n\nRESPUESTA (con referencias [C1], [C2]...):"
    )
    answer = generate(prompt, system=DEFAULT_SYSTEM)
    return {"answer": answer, "citations": citations}
