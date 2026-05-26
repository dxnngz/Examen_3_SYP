# 04 · CSS3D — Stack Explorer

## Qué demuestra

- **CSS 3D transforms**: `perspective`, `transform-style: preserve-3d`, `translateZ`, `rotateX/Y`.
- **backface-visibility: hidden** en las caras del cubo.
- Controles: slider rotación Y, auto-rotación, **reduce motion**.
- Micro-interacción 3D en tarjetas laterales (tilt al pasar el ratón).

## Ejecutar

No requiere servidor. Abre el archivo o usa un servidor estático:

```bash
cd 04_css3d_stack_explorer
python3 -m http.server 8080
```

Abrir: http://localhost:8080

(O doble clic en `index.html`)

## Demo vídeo

1. Mostrar el cubo con caras **RAG, Docker, nginx, Ollama…**
2. Mover el **slider** de rotación.
3. Activar **Auto rotar** y luego **Reduce motion** (accesibilidad).
4. Pasar el ratón por las tarjetas de la derecha (efecto tilt).

## Personalización

- **Función**: temática stack DAM2/SysOps en las caras; auto-spin + tilt en cards.
- **Forma**: paleta violeta/teal (distinta al showcase azul de clase).
