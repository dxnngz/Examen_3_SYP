# 01 · RAG — SysOps Vault

Mini-proyecto **Servicios y Procesos** · Evaluación 3.

## Qué demuestra

- **RAG** sin generación: ingesta, chunking, embeddings (Ollama `nomic-embed-text`) y recuperación top‑k.
- Personalización **función**: filtro por categoría (`docker`, `nginx`, `systemd`, `ia`), detección automática de categoría, resaltado de términos en resultados.
- Personalización **forma**: tema ámbar/terminal “SysOps Vault”, botón de apuntes de ejemplo, tarjetas de resultados.

## Requisitos

```bash
ollama pull nomic-embed-text
ollama serve   # si no está activo
```

## Ejecutar

```bash
cd 01_rag_sysops_vault
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```

Abrir: http://localhost:8001

## Demo para el vídeo (1–3 min)

1. Pulsa **Cargar apuntes de ejemplo** → **Ingestar** (muestra chunks y categoría).
2. Busca: `¿qué es un reverse proxy?` o `firewall puerto 22`.
3. Muestra el **score**, el **resaltado** y el filtro por categoría **nginx** / **docker**.

## Rúbrica (4 puntos) — copia a Drive

| Criterio | 0 | 1 | 2 |
|----------|---|---|---|
| RAG correcto (ingesta + búsqueda) | No funciona | Parcial | Completo |
| Uso de embeddings Ollama | No | Con errores | Estable |
| Personalización función | Ninguna | 1 mejora | Filtros + highlight |
| Personalización forma | Plantilla | Tema propio | UI pulida + UX |
