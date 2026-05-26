# 02 · RAG + IA — Asistente DAM2

## Qué demuestra

- **Retrieval**: embeddings + top‑k sobre apuntes indexados.
- **Augmented Generation**: Ollama (`llama3.1:8b` u otro) responde solo con el contexto recuperado.
- **Citas** `[C1]`, `[C2]` visibles en la UI y en el JSON de la API.

## Requisitos

```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

## Ejecutar

```bash
cd 02_rag_ia_asistente
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8002
```

Abrir: http://localhost:8002

## API (opcional para el vídeo)

```bash
curl -s -X POST http://localhost:8002/ingest -H 'content-type: application/json' \
  -d '{"title":"apuntes","text":"Nginx hace de reverse proxy..."}'

curl -s -X POST http://localhost:8002/ask -H 'content-type: application/json' \
  -d '{"question":"¿Qué hace Nginx?","top_k":3}'
```

## Demo vídeo

1. Indexar apuntes (panel izquierdo).
2. Preguntar: *¿Cómo expongo FastAPI con Nginx?*
3. Mostrar respuesta + bloque **Fuentes** con scores.

## Personalización

- **Función**: chat con citas numeradas y scores de similitud.
- **Forma**: layout chat + panel de ingesta (tema azul índigo).
