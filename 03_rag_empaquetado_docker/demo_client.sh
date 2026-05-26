#!/usr/bin/env bash
# Demo rápida para el vídeo del examen (RAG empaquetado en Docker)
set -e
BASE="${1:-http://localhost:8010}"
KEY="${RAG_API_KEY:-dam2-secret-2026}"

echo "== Health =="
curl -s "$BASE/health" | python3 -m json.tool

echo ""
echo "== Ingest =="
curl -s -X POST "$BASE/ingest" \
  -H "content-type: application/json" \
  -H "X-API-Key: $KEY" \
  -d '{"title":"Docker DAM2","text":"Docker Compose levanta varios contenedores. El volumen rag_data persiste el índice vectorial entre reinicios del contenedor."}' \
  | python3 -m json.tool

echo ""
echo "== Ask =="
curl -s -X POST "$BASE/ask" \
  -H "content-type: application/json" \
  -H "X-API-Key: $KEY" \
  -d '{"question":"¿Qué persiste entre reinicios?","top_k":3}' \
  | python3 -m json.tool
