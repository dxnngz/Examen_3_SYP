# 03 · RAG Empaquetado (Docker)

## Qué demuestra

- Mismo flujo **RAG + IA** que el proyecto 02, pero **empaquetado** en imagen Docker.
- **Volumen** `rag_data` para persistir el índice entre reinicios.
- **Seguridad**: header `X-API-Key` obligatorio en `/ingest` y `/ask`.
- **Healthcheck** en `docker-compose.yml`.
- Ollama en el host accesible vía `host.docker.internal`.

## Requisitos

- Docker + Docker Compose
- Ollama en el Mac: `ollama serve` y modelos `nomic-embed-text`, `llama3.1:8b`

## Levantar el servicio

```bash
cd 03_rag_empaquetado_docker
docker compose up --build -d
docker compose ps
```

API: http://localhost:8010/health

## Probar (script o curl)

```bash
chmod +x demo_client.sh
./demo_client.sh
```

O manualmente:

```bash
export KEY=dam2-secret-2026
curl -s -X POST http://localhost:8010/ingest \
  -H "content-type: application/json" -H "X-API-Key: $KEY" \
  -d '{"title":"apuntes","text":"systemd gestiona servicios en Linux..."}'

curl -s -X POST http://localhost:8010/ask \
  -H "content-type: application/json" -H "X-API-Key: $KEY" \
  -d '{"question":"¿Qué es systemd?"}'
```

## Demo vídeo

1. `docker compose up --build` y `docker compose ps` (healthy).
2. `./demo_client.sh` — ingest + ask con API key.
3. `docker compose restart` y repetir ask (índice persiste en volumen).
4. Probar sin API key → error 401.

## Parar

```bash
docker compose down
# docker compose down -v   # borra también el volumen
```

## Personalización

- **Función**: API key configurable, healthcheck, script de demo.
- **Forma**: nombre contenedor `rag-dam2-packaged`, variables en compose.
