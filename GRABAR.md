# Guía para grabar los 4 vídeos — SYP Examen 3

## Antes de grabar (checklist)

1. **Ollama activo:** `ollama serve` (en otra terminal o en segundo plano).
2. **Modelos instalados:**
   ```bash
   ollama pull nomic-embed-text
   ollama pull llama3.1:8b
   ```
3. **Puertos libres:** Si tienes **SSGG** (`Examen_3_SGE`) en 8001/8002, ciérralo o usa los puertos de abajo (8101, 8102…).
4. **Docker Desktop abierto** (solo para el proyecto 03).

## Arrancar todo para la grabación

```bash
# Terminal 1 — RAG
cd ~/Desktop/Examen_3_SYP/01_rag_sysops_vault
source .venv/bin/activate
uvicorn app:app --reload --port 8101

# Terminal 2 — RAG + IA
cd ~/Desktop/Examen_3_SYP/02_rag_ia_asistente
source .venv/bin/activate
uvicorn app:app --reload --port 8102

# Terminal 3 — Docker (proyecto 03)
cd ~/Desktop/Examen_3_SYP/03_rag_empaquetado_docker
docker compose up --build

# Proyecto 4 — solo abrir en navegador
open ~/Desktop/Examen_3_SYP/04_css3d_stack_explorer/index.html
```

| Proyecto | URL |
|----------|-----|
| 01 RAG | http://localhost:8101 |
| 02 RAG+IA | http://localhost:8102 |
| 03 Docker | http://localhost:8010/health |
| 04 CSS3D | archivo `index.html` o http://localhost:8080 |

---

## Vídeo 1 — RAG (≈2 min)

**URL:** http://localhost:8101

| Tiempo | Qué decir / hacer |
|--------|-------------------|
| 0:00 | "Este es SysOps Vault: RAG puro, sin IA generativa." |
| 0:15 | Clic **Vaciar índice** (si ya había datos) → **Cargar apuntes** → **Ingestar** |
| 0:45 | Mostrar JSON: chunks y categorías (docker, nginx, systemd…) |
| 1:00 | Buscar: `reverse proxy nginx` → mostrar score y palabras resaltadas |
| 1:30 | Filtro categoría **nginx** → buscar de nuevo |
| 2:00 | "Personalización: filtro por categoría, highlight y tema ámbar propio." |

---

## Vídeo 2 — RAG + IA (≈2–3 min)

**URL:** http://localhost:8102

| Tiempo | Qué decir / hacer |
|--------|-------------------|
| 0:00 | "Asistente DAM2: primero recupera chunks, luego Ollama redacta la respuesta." |
| 0:20 | **Indexar apuntes** (texto ya viene de ejemplo) |
| 0:50 | Pregunta: `¿Cómo expongo FastAPI con Nginx?` |
| 1:30 | Esperar respuesta (~10–20 s) → leer respuesta con [C1] |
| 2:00 | Señalar bloque **Fuentes** con score % |
| 2:30 | "RAG + IA local, sin enviar datos a la nube." |

---

## Vídeo 3 — RAG empaquetado (≈2–3 min)

**Terminal visible + navegador opcional**

| Tiempo | Qué decir / hacer |
|--------|-------------------|
| 0:00 | `docker compose up --build` — mostrar contenedor healthy |
| 0:30 | `./demo_client.sh` — ingest + ask con API key |
| 1:30 | `curl` sin `X-API-Key` → error **401** |
| 2:00 | `docker compose restart` → repetir pregunta (datos en volumen) |
| 2:30 | "Servicio empaquetado listo para desplegar." |

**API key:** `dam2-secret-2026` (header `X-API-Key`)

---

## Vídeo 4 — CSS3D (≈1–2 min)

**Abrir:** `04_css3d_stack_explorer/index.html`

| Tiempo | Qué decir / hacer |
|--------|-------------------|
| 0:00 | "Escena 3D solo con CSS: perspective y preserve-3d." |
| 0:20 | Mover slider **Rotación Y** |
| 0:40 | Activar **Auto rotar** |
| 1:00 | Activar **Reduce motion** (accesibilidad) |
| 1:20 | Pasar ratón por tarjetas (efecto tilt) |
| 1:40 | Caras del cubo: RAG, Docker, nginx… |

---

## Estado de la revisión técnica

| Proyecto | ¿Funciona? | Notas |
|----------|------------|-------|
| 01 RAG | ✅ Probado | Embeddings + búsqueda + highlight OK |
| 02 RAG+IA | ✅ Probado | Respuesta con citas en ~10 s |
| 03 Docker | ✅ API OK | Requiere Docker Desktop en marcha |
| 04 CSS3D | ✅ | Sin dependencias; abrir HTML |

## Si algo falla

| Error | Solución |
|-------|----------|
| `Connection refused` Ollama | `ollama serve` |
| `model not found` | `ollama pull llama3.1:8b` |
| Puerto en uso | Usa 8101/8102 o cierra SGE |
| Docker no arranca | Abre Docker Desktop |
| 401 en proyecto 03 | Header `X-API-Key: dam2-secret-2026` |
