from __future__ import annotations  # noqa: F401 — compat Python 3.9

import hashlib
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from store import Chunk, JsonlVectorStore, embed

app = FastAPI(title="SysOps Vault — RAG Retriever")

DATA = Path(__file__).resolve().parent / "data"
STORE = JsonlVectorStore(DATA / "index.jsonl")

SAMPLE_NOTES = """
Docker: contenedor ligero que empaqueta app + dependencias. docker compose up levanta varios servicios.
Nginx: servidor web y reverse proxy. Escucha en 80/443 y reenvía tráfico a backends.
systemd: gestor de servicios en Linux. systemctl start nginx activa un servicio.
RAG: Retrieval Augmented Generation. Primero recuperas fragmentos relevantes y luego generas la respuesta.
UFW: firewall simplificado en Ubuntu. ufw allow 22/tcp abre SSH.
""".strip()


def chunk_text(text: str, size: int = 500, overlap: int = 80) -> list[str]:
    raw_paras = [p.strip() for p in text.replace("\r", "").split("\n") if p.strip()]
    if len(raw_paras) > 1 and all(len(p) <= size for p in raw_paras):
        return raw_paras
    text = " ".join(text.split())
    if not text:
        return []
    out: list[str] = []
    i = 0
    while i < len(text):
        out.append(text[i : i + size])
        i += max(1, size - overlap)
    return out


def detect_category(title: str, text: str) -> str:
    blob = f"{title} {text}".lower()
    if any(k in blob for k in ("docker", "compose", "contenedor")):
        return "docker"
    if any(k in blob for k in ("nginx", "proxy", "http")):
        return "nginx"
    if any(k in blob for k in ("systemd", "systemctl", "servicio")):
        return "systemd"
    if any(k in blob for k in ("rag", "embedding", "ollama")):
        return "ia"
    return "general"


class IngestBody(BaseModel):
    title: str
    text: str
    category: Optional[str] = None


class SearchBody(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>SysOps Vault — RAG</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0c0a09;
      --card: #1c1917;
      --t: #fafaf9;
      --m: #a8a29e;
      --a: #f59e0b;
      --ok: #34d399;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, sans-serif;
      background:
        radial-gradient(800px 400px at 10% 0%, rgba(245,158,11,.15), transparent 50%),
        var(--bg);
      color: var(--t);
    }
    header {
      padding: 22px 20px;
      border-bottom: 1px solid rgba(255,255,255,.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }
    .logo { font-weight: 800; font-size: 1.25rem; }
    .logo span { color: var(--a); }
    .hint { color: var(--m); font-size: 13px; max-width: 520px; }
    main {
      max-width: 1100px;
      margin: 0 auto;
      padding: 18px 20px 40px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 16px;
      padding: 16px;
    }
    h2 { margin: 0 0 12px; font-size: 1rem; }
    input, textarea, select, button {
      width: 100%;
      background: rgba(0,0,0,.35);
      border: 1px solid rgba(255,255,255,.12);
      color: var(--t);
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 8px;
      font: inherit;
    }
    textarea { min-height: 180px; resize: vertical; }
    button {
      width: auto;
      cursor: pointer;
      background: rgba(245,158,11,.2);
      border-color: rgba(245,158,11,.5);
      font-weight: 600;
    }
    button:hover { background: rgba(245,158,11,.35); }
    .row { display: flex; gap: 8px; flex-wrap: wrap; }
    .result {
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 12px;
      padding: 12px;
      margin-top: 10px;
      background: rgba(0,0,0,.25);
    }
    .score { color: var(--ok); font-size: 12px; font-weight: 600; }
    mark { background: rgba(245,158,11,.45); color: #fff; padding: 0 2px; border-radius: 3px; }
    .meta { color: var(--m); font-size: 12px; margin-top: 6px; }
    @media (max-width: 900px) { main { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <div>
      <div class="logo">SysOps <span>Vault</span></div>
      <div class="hint">RAG puro: ingesta, embeddings (Ollama) y recuperación top‑k con filtro por categoría.</div>
    </div>
    <button type="button" onclick="loadSample()">Cargar apuntes de ejemplo</button>
    <button type="button" onclick="resetIndex()" style="background:rgba(239,68,68,.2);border-color:#ef4444">Vaciar índice</button>
  </header>
  <main>
    <section class="card">
      <h2>1) Ingesta de apuntes</h2>
      <input id="title" placeholder="Título (ej. Docker básico)" />
      <select id="category">
        <option value="">Categoría (auto)</option>
        <option value="docker">docker</option>
        <option value="nginx">nginx</option>
        <option value="systemd">systemd</option>
        <option value="ia">ia</option>
        <option value="general">general</option>
      </select>
      <textarea id="text" placeholder="Pega tus apuntes de Servicios y Procesos..."></textarea>
      <div class="row">
        <button onclick="ingest()">Ingestar</button>
      </div>
      <pre id="ingOut" style="color:var(--m);font-size:12px;white-space:pre-wrap"></pre>
    </section>
    <section class="card">
      <h2>2) Búsqueda semántica</h2>
      <input id="q" placeholder="Ej: ¿cómo abro el puerto 22 en el firewall?" />
      <div class="row">
        <input id="k" value="5" style="max-width:80px" title="top_k" />
        <select id="filterCat" style="max-width:160px">
          <option value="">Todas las categorías</option>
          <option value="docker">docker</option>
          <option value="nginx">nginx</option>
          <option value="systemd">systemd</option>
          <option value="ia">ia</option>
          <option value="general">general</option>
        </select>
        <button onclick="search()">Buscar</button>
      </div>
      <div id="results"></div>
    </section>
  </main>
  <script>
    const SAMPLE = `""" + SAMPLE_NOTES.replace("`", "\\`") + """`;
    function loadSample() {
      document.getElementById('title').value = 'Apuntes DAM2 — SysOps';
      document.getElementById('text').value = SAMPLE;
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
    async function resetIndex() {
      if (!confirm('¿Vaciar todo el índice?')) return;
      const r = await fetch('/api/reset', { method: 'DELETE' });
      const j = await r.json();
      document.getElementById('ingOut').textContent = JSON.stringify(j);
      document.getElementById('results').innerHTML = '';
    }
    async function ingest() {
      document.getElementById('ingOut').textContent = 'Generando embeddings...';
      try {
        const j = await post('/api/ingest', {
          title: document.getElementById('title').value,
          text: document.getElementById('text').value,
          category: document.getElementById('category').value || null
        });
        document.getElementById('ingOut').textContent = JSON.stringify(j, null, 2);
      } catch (e) {
        document.getElementById('ingOut').textContent = e.message;
      }
    }
    async function search() {
      const box = document.getElementById('results');
      box.innerHTML = '<p style="color:var(--m)">Buscando...</p>';
      try {
        const j = await post('/api/search', {
          query: document.getElementById('q').value,
          top_k: parseInt(document.getElementById('k').value || '5', 10),
          category: document.getElementById('filterCat').value || null
        });
        if (!j.results.length) {
          box.innerHTML = '<p>No hay resultados. Ingesta apuntes primero.</p>';
          return;
        }
        box.innerHTML = j.results.map((r, i) => `
          <div class="result">
            <div class="score">#${i+1} · score ${(r.score*100).toFixed(1)}%</div>
            <div>${r.text_highlighted || r.text}</div>
            <div class="meta">${r.meta?.title || ''} · ${r.meta?.category || ''} · chunk ${r.meta?.chunk ?? ''}</div>
          </div>
        `).join('');
      } catch (e) {
        box.innerHTML = '<p>' + e.message + '</p>';
      }
    }
  </script>
</body>
</html>"""


@app.post("/api/ingest")
def ingest_api(body: IngestBody) -> dict:
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Título vacío")
    chunks = chunk_text(body.text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Texto vacío")
    ids: list[str] = []
    categories_used: set[str] = set()
    try:
        for ix, t in enumerate(chunks):
            category = body.category or detect_category(body.title, t)
            categories_used.add(category)
            cid = hashlib.sha256(f"{body.title}:{ix}:{t}".encode()).hexdigest()[:16]
            vec = embed(t)
            STORE.add(
                Chunk(
                    id=cid,
                    text=t,
                    embedding=vec,
                    meta={"title": body.title, "chunk": ix, "category": category},
                )
            )
            ids.append(cid)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return {
        "status": "ok",
        "chunks": len(ids),
        "categories": sorted(categories_used),
        "ids": ids[:5],
    }


@app.post("/api/search")
def search_api(body: SearchBody) -> dict:
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Consulta vacía")
    results = STORE.search(
        body.query,
        top_k=max(1, min(20, int(body.top_k))),
        category=body.category or None,
    )
    return {"results": results, "count": len(results)}


@app.delete("/api/reset")
def reset_index() -> dict:
    """Borra el índice (útil antes de grabar el vídeo)."""
    path = STORE.path
    path.write_text("", encoding="utf-8")
    return {"status": "ok", "message": "Índice vaciado"}


@app.get("/api/stats")
def stats() -> dict:
    chunks = STORE.all()
    cats: dict[str, int] = {}
    for c in chunks:
        cat = c.meta.get("category", "general")
        cats[cat] = cats.get(cat, 0) + 1
    return {"chunks": len(chunks), "by_category": cats}
