# Examen 3 — Servicios y Procesos (SYP)

Cuatro mini-proyectos para la evaluación 3, basados en lo visto en clase (RAG, RAG+IA, RAG empaquetado, CSS3D) con **personalización en función y forma**.

> SSGG está en otra carpeta (`Examen_3_SGE`). Aquí solo **Servicios y Procesos**.

## Estructura

| Carpeta | Tema examen | Puerto recomendado |
|---------|-------------|-------------------|
| `01_rag_sysops_vault/` | RAG (retrieval) | **8101** |
| `02_rag_ia_asistente/` | RAG + IA | **8102** |
| `03_rag_empaquetado_docker/` | RAG empaquetado | **8010** |
| `04_css3d_stack_explorer/` | CSS3D | abrir `index.html` |

> **Importante:** Si tienes SSGG (`Examen_3_SGE`) usando 8001/8002, ciérralo o usa los puertos 8101/8102. Ver **[GRABAR.md](GRABAR.md)** para el guion de los vídeos.

## Requisitos globales

- Python 3.10+
- [Ollama](https://ollama.com) en marcha: `ollama serve`
- Modelos: `ollama pull nomic-embed-text` y `ollama pull llama3.1:8b` (o el que uses)
- Docker (solo proyecto 03)

## Arranque rápido

```bash
# Terminal 1 — RAG puro
cd 01_rag_sysops_vault && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn app:app --reload --port 8101

# Terminal 2 — RAG + IA
cd 02_rag_ia_asistente && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn app:app --reload --port 8102

# Terminal 3 — Docker
cd 03_rag_empaquetado_docker && docker compose up --build

# Proyecto 4 — abrir index.html o:
cd 04_css3d_stack_explorer && python3 -m http.server 8080
```

## Formato de entrega (por cada pregunta)

1. Documento Google Drive compartido (explicación + capturas).
2. Rúbrica de 4 puntos (plantilla en cada `README.md`).
3. Vídeo 1–3 min demostrando el proyecto.

### Guion sugerido para cada vídeo

| Tiempo | Contenido |
|--------|-----------|
| 0:00–0:15 | Qué problema resuelve |
| 0:15–1:30 | Demo en vivo |
| 1:30–2:30 | Detalle técnico (RAG, Docker, CSS3D…) |
| 2:30–3:00 | Personalización función + forma |

## Personalización global (tema DAM2 SysOps)

- Apuntes de despliegue: Docker, nginx, systemd, RAG, firewall.
- Estética propia: ámbar (01), azul chat (02), contenedor Docker (03), violeta/teal 3D (04).

## Autor

Daniel Giménez — DAM2 · Evaluación 3 SYP
