from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Optional

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def root_ui() -> str:
    return """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>RAG Dockerizado — Panel de Control</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet" />
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1528;
      --panel: rgba(20, 35, 65, 0.6);
      --t: #f1f5f9;
      --m: #94a3b8;
      --a: #0db7ed; /* Docker Cyan */
      --b: #3b82f6; /* Ocean Blue */
      --border: rgba(255, 255, 255, 0.08);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: radial-gradient(ellipse at top, #0f284e 0%, var(--bg) 65%);
      color: var(--t);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      padding: 18px 28px;
      border-bottom: 1px solid var(--border);
      background: rgba(11, 21, 40, 0.7);
      backdrop-filter: blur(8px);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-icon { font-size: 28px; }
    header h1 { font-size: 1.25rem; font-weight: 800; }
    header p { font-size: 12px; color: var(--m); margin-top: 1px; }
    .container {
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
      padding: 24px;
      flex: 1;
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 24px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      backdrop-filter: blur(12px);
      display: flex;
      flex-direction: column;
      gap: 16px;
      height: fit-content;
    }
    .panel-title { font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--a); display: flex; align-items: center; gap: 8px; }
    
    label { font-size: 11px; font-weight: 600; color: var(--m); text-transform: uppercase; }
    input, textarea, button {
      width: 100%;
      padding: 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: rgba(0, 0, 0, 0.3);
      color: var(--t);
      font: inherit;
      outline: none;
      transition: all 0.2s ease;
    }
    input:focus, textarea:focus {
      border-color: var(--a);
      box-shadow: 0 0 8px rgba(13, 183, 237, 0.2);
    }
    textarea { min-height: 160px; resize: vertical; }
    
    .btn {
      background: rgba(13, 183, 237, 0.15);
      border-color: var(--a);
      color: var(--a);
      cursor: pointer;
      font-weight: 700;
      font-size: 13.5px;
    }
    .btn:hover {
      background: var(--a);
      color: #000;
    }
    .btn-danger {
      background: rgba(239, 68, 68, 0.15);
      border-color: #ef4444;
      color: #ef4444;
    }
    .btn-danger:hover {
      background: #ef4444;
      color: #fff;
    }
    
    .chat-container {
      display: flex;
      flex-direction: column;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: var(--panel);
      backdrop-filter: blur(12px);
      min-height: 580px;
    }
    
    .chat-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(0,0,0,0.15);
      border-radius: 16px 16px 0 0;
    }
    
    .status-badge {
      font-size: 11px;
      font-weight: 700;
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      padding: 3px 8px;
      border-radius: 99px;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      height: 380px;
    }
    
    .msg {
      max-width: 80%;
      padding: 14px 16px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.5;
    }
    .msg.ai {
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border);
    }
    .msg.user {
      align-self: flex-end;
      background: var(--b);
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25);
    }
    
    .msg-cites {
      margin-top: 10px;
      font-size: 11px;
      color: var(--m);
      border-top: 1px solid rgba(255,255,255,0.06);
      padding-top: 8px;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .input-area {
      display: flex;
      gap: 12px;
      padding: 16px 20px;
      border-top: 1px solid var(--border);
      background: rgba(0,0,0,0.15);
      border-radius: 0 0 16px 16px;
    }
    .input-area input {
      flex: 1;
    }
    .input-area button {
      width: auto;
      padding: 0 24px;
    }
    
    .status-text {
      font-size: 12px;
      color: var(--m);
      font-family: 'JetBrains Mono', monospace;
      white-space: pre-wrap;
      word-break: break-all;
    }
    
    @media (max-width: 900px) {
      .container { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span class="brand-icon">🐳</span>
      <div>
        <h1>RAG Dockerizado</h1>
        <p>Servidor RAG+IA empaquetado en contenedor y securizado — DAM2</p>
      </div>
    </div>
    <div class="status-badge" id="service-health">Cargando estado...</div>
  </header>

  <main class="container">
    <!-- LEFT CONTROL SIDEBAR -->
    <aside style="display:flex; flex-direction:column; gap:20px;">
      <!-- AUTHENTICATION PANEL -->
      <section class="panel">
        <h2 class="panel-title">🔑 Acceso Autorizado</h2>
        <div>
          <label for="apiKey">X-API-Key Obligatoria</label>
          <input type="password" id="apiKey" value="dam2-secret-2026" placeholder="Introduce tu API Key" style="margin-top:4px;" />
        </div>
      </section>

      <!-- INGESTION / TRAINING PANEL -->
      <section class="panel">
        <h2 class="panel-title">📥 Entrenar RAG (Ingesta)</h2>
        <div style="display:flex; flex-direction:column; gap:8px;">
          <label for="docTitle">Título del Documento</label>
          <input id="docTitle" value="Docker Compose Apuntes" />
        </div>
        <div style="display:flex; flex-direction:column; gap:8px;">
          <label for="docText">Contenido Técnico</label>
          <textarea id="docText" placeholder="Pega aquí los apuntes que el RAG debe aprender..."></textarea>
        </div>
        <button class="btn" onclick="submitIngest()">Ingestar y Aprender</button>
        <div class="status-text" id="ingest-status"></div>
      </section>

      <!-- CLEANUP PANEL -->
      <section class="panel">
        <h2 class="panel-title">🗑️ Restablecer</h2>
        <button class="btn btn-danger" onclick="resetDatabase()">Borrar Base de Datos</button>
      </section>
    </aside>

    <!-- RIGHT CHAT WORKSPACE -->
    <section class="chat-container">
      <div class="chat-header">
        <h2 style="font-size:14px; font-weight:800; color:var(--t)">💬 Asistente IA (Inferencia RAG)</h2>
        <span class="status-badge" style="background:rgba(13, 183, 237, 0.12); color:var(--a);">Local LLM</span>
      </div>
      
      <div class="messages" id="chat-messages">
        <div class="msg ai">
          Hola. Soy tu RAG dockerizado. A la izquierda puedes introducir la <strong>API Key</strong> de acceso y pegar apuntes de texto para "entrenarme" (ingestarlos). Luego, hazme preguntas aquí.
        </div>
      </div>

      <div class="input-area">
        <input id="chat-input" placeholder="Pregúntame sobre los apuntes ingestados..." />
        <button class="btn" onclick="submitQuestion()">Preguntar</button>
      </div>
    </section>
  </main>

  <script>
    const API_URL = '';
    
    // Auto load health on start
    async function checkHealth() {
      try {
        const r = await fetch('/health');
        const j = await r.json();
        document.getElementById('service-health').textContent = `HEALTHY · ${j.chunks_indexed} CHUNKS`;
        document.getElementById('service-health').style.background = 'rgba(16, 185, 129, 0.15)';
        document.getElementById('service-health').style.color = '#10b981';
      } catch (e) {
        document.getElementById('service-health').textContent = 'UNHEALTHY / OFFLINE';
        document.getElementById('service-health').style.background = 'rgba(239, 68, 68, 0.15)';
        document.getElementById('service-health').style.color = '#ef4444';
      }
    }

    async function submitIngest() {
      const apiKey = document.getElementById('apiKey').value.trim();
      const title = document.getElementById('docTitle').value.trim();
      const text = document.getElementById('docText').value.trim();
      const statusDiv = document.getElementById('ingest-status');
      
      if(!apiKey) {
        statusDiv.textContent = 'Error: API Key es obligatoria.';
        statusDiv.style.color = '#ef4444';
        return;
      }
      if(!text) {
        statusDiv.textContent = 'Error: Contenido técnico vacío.';
        statusDiv.style.color = '#ef4444';
        return;
      }

      statusDiv.textContent = 'Vectorizando y subiendo...';
      statusDiv.style.color = 'var(--a)';
      
      try {
        const response = await fetch('/ingest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
          },
          body: JSON.stringify({ title, text })
        });
        
        const data = await response.json();
        if(response.ok) {
          statusDiv.textContent = `Éxito: Indexado en ${data.chunks} fragmentos.`;
          statusDiv.style.color = '#10b981';
          document.getElementById('docText').value = '';
          checkHealth();
        } else {
          statusDiv.textContent = `Error (${response.status}): ${data.detail || 'Fallo'}`;
          statusDiv.style.color = '#ef4444';
        }
      } catch (error) {
        statusDiv.textContent = `Error de red: ${error.message}`;
        statusDiv.style.color = '#ef4444';
      }
    }

    async function resetDatabase() {
      if(!confirm('¿Estás seguro de que quieres borrar el índice del RAG?')) return;
      const apiKey = document.getElementById('apiKey').value.trim();
      const statusDiv = document.getElementById('ingest-status');
      
      try {
        const response = await fetch('/reset', {
          method: 'DELETE',
          headers: {
            'X-API-Key': apiKey
          }
        });
        const data = await response.json();
        if(response.ok) {
          statusDiv.textContent = 'Base de datos vaciada con éxito.';
          statusDiv.style.color = '#10b981';
          checkHealth();
        } else {
          statusDiv.textContent = `Error: ${data.detail || 'Fallo'}`;
          statusDiv.style.color = '#ef4444';
        }
      } catch (e) {
        statusDiv.textContent = `Error: ${e.message}`;
        statusDiv.style.color = '#ef4444';
      }
    }

    async function submitQuestion() {
      const input = document.getElementById('chat-input');
      const question = input.value.trim();
      if(!question) return;

      const apiKey = document.getElementById('apiKey').value.trim();
      const messagesContainer = document.getElementById('chat-messages');

      // Add user message
      const userMsg = document.createElement('div');
      userMsg.className = 'msg user';
      userMsg.textContent = question;
      messagesContainer.appendChild(userMsg);
      input.value = '';
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      // Add thinking AI placeholder
      const aiMsg = document.createElement('div');
      aiMsg.className = 'msg ai';
      aiMsg.textContent = 'Pensando (haciendo consulta RAG y LLM)...';
      messagesContainer.appendChild(aiMsg);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      try {
        const response = await fetch('/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
          },
          body: JSON.stringify({ question, top_k: 4 })
        });
        
        const data = await response.json();
        if(response.ok) {
          aiMsg.innerHTML = data.answer.replace(/\\n/g, '<br>');
          
          if (data.citations && data.citations.length) {
            const citesDiv = document.createElement('div');
            citesDiv.className = 'msg-cites';
            citesDiv.innerHTML = '<strong>Fuentes consultadas:</strong><br>' + 
              data.citations.map(c => `[${c.ref}] ${c.title}#chunk_${c.chunk} (Similitud: ${(c.score * 100).toFixed(0)}%)`).join('<br>');
            aiMsg.appendChild(citesDiv);
          }
        } else {
          aiMsg.textContent = `Fallo en la consulta (${response.status}): ${data.detail || 'Error desconocido'}`;
          aiMsg.style.color = '#ef4444';
        }
      } catch (error) {
        aiMsg.textContent = `Error de conexión: ${error.message}`;
        aiMsg.style.color = '#ef4444';
      }
      
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    document.getElementById('chat-input').addEventListener('keydown', (e) => {
      if(e.key === 'Enter') submitQuestion();
    });

    setInterval(checkHealth, 5000);
    checkHealth();
  </script>
</body>
</html>
"""


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
