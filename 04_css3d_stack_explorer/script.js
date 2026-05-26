/* ==========================================================================
   CSS 3D STACK EXPLORER - STUNNING INTERACTION & TELEMETRY ENGINE
   ========================================================================== */

// --- STATE MANAGEMENT ---
let state = {
  activeScene: 'cube-scene', // 'cube-scene', 'carousel-scene', 'layers-scene'
  rotX: -16,
  rotY: 32,
  perspective: 800,
  autoRotate: true,
  autoRotateSpeed: 15, // seconds for 360 deg
  dragRotationEnabled: true,
  reduceMotion: false,
  activeTheme: 'neon',
  
  // Drag states
  isDragging: false,
  startX: 0,
  startY: 0,
  startRotX: 0,
  startRotY: 0,
  velocityX: 0,
  velocityY: 0,
  
  // Carousel state
  carouselIndex: 0,
  carouselItemCount: 5,
  carouselRotationAngle: 72 // 360 / 5
};

// --- DOM ELEMENTS ---
const elements = {
  body: document.body,
  viewport: document.getElementById('viewport'),
  sceneWrapper: document.getElementById('scene-wrapper'),
  cubeScene: document.getElementById('cube-scene'),
  carouselScene: document.getElementById('carousel-scene'),
  layersScene: document.getElementById('layers-scene'),
  
  cube: document.getElementById('cube'),
  carouselRing: document.getElementById('carousel-ring'),
  layersStack: document.getElementById('layers-stack'),
  groundShadow: document.getElementById('ground-shadow'),
  
  // Sliders
  sliderRotY: document.getElementById('rot-y'),
  sliderRotX: document.getElementById('rot-x'),
  sliderPersp: document.getElementById('perspective'),
  sliderSpeed: document.getElementById('spin-speed'),
  speedContainer: document.getElementById('spin-speed-container'),
  
  // Slider values text
  valRotY: document.getElementById('val-rot-y'),
  valRotX: document.getElementById('val-rot-x'),
  valPersp: document.getElementById('val-persp'),
  valSpeed: document.getElementById('val-speed'),
  
  // Quick stats
  valStatPersp: document.getElementById('val-perspective'),
  valStatAuto: document.getElementById('val-auto'),
  valStatActive: document.getElementById('val-active-node'),
  
  // Toggles
  toggleAuto: document.getElementById('auto'),
  toggleDrag: document.getElementById('drag-rotation'),
  toggleReduce: document.getElementById('reduce'),
  
  // Carousel controls
  carouselPrev: document.getElementById('carousel-prev'),
  carouselNext: document.getElementById('carousel-next'),
  carouselIndicator: document.getElementById('carousel-indicator'),
  
  // Terminal
  terminalBody: document.getElementById('terminal-body'),
  inspectorOutput: document.getElementById('inspector-output'),
  clearTermBtn: document.getElementById('clear-term'),
  pendingPrompt: document.getElementById('pending-prompt')
};

// --- DETAILED TECH METADATA FOR TERMINAL ---
const techMetadata = {
  rag: {
    title: "SISTEMA RAG (Retrieval-Augmented Generation)",
    cmd: "python3 rag_agent.py --query='¿cómo securizar nginx?' --context='./docs/sysops/'",
    output: `[INFO] Inicializando Pipeline RAG en local...
[DB] Conectando a base de datos vectorial ChromaDB en localhost:8000
[DB] Colección 'sysops_dam2' cargada con 147 chunks de conocimiento.
[RAG] Búsqueda semántica completada para: '¿cómo securizar nginx?'
[RAG] 3 fragmentos de contexto recuperados (Similitud del coseno: 0.892, 0.864, 0.811)
[LLM] Enviando consulta enriquecida a Ollama (modelo: deepseek-r1:8b)...
[LLM] Respuesta generada con éxito en 1.84 segundos [Tokens/seg: 42.5]

=== CONTEXTO APLICADO ===
"Para configurar nginx de forma segura:
1. Desactiva cabecera de versión: server_tokens off;
2. Limita accesos de red con UFW local.
3. Habilita HTTPS estricto usando TLSv1.3..."`
  },
  docker: {
    title: "PLATAFORMA DE CONTENEDORES DOCKER",
    cmd: "docker compose ps --services --filter 'status=running'",
    output: `NAME                     IMAGE                         COMMAND                  SERVICE             STATUS
sysops-nginx-1           nginx:alpine                  "/docker-entrypoint.…"   nginx               running (healthy)
sysops-fastapi-app-1     python:3.11-slim              "uvicorn app.main:ap…"   fastapi-app         running (healthy)
sysops-chromadb-1        chromadb/chroma:latest        "/entrypoint.sh"         chromadb            running (healthy)
sysops-ollama-local-1    ollama/ollama:latest          "/bin/ollama serve"      ollama-local        running (healthy)

[SYSTEM] CPU usage: 4.8% | Memory limit: 2048MB | Active connections: 12`
  },
  nginx: {
    title: "PROXY INVERSO NGINX & CONFIG SSL",
    cmd: "nginx -T | grep -E 'server_name|ssl_protocols|proxy_pass'",
    output: `nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
    server_name sysops.dam2.local;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    proxy_pass http://fastapi-app:8000;
    proxy_pass http://ollama-local:11434;
    proxy_pass http://chromadb:8000;

[NETWORK] Port 80 (HTTP) -> Redirecting to 443 (HTTPS SSL)
[SSL] Certificado Let's Encrypt cargado correctamente. Caduca en 89 días.`
  },
  ollama: {
    title: "MODELO DE LENGUAJE LOCAL OLLAMA",
    cmd: "ollama show deepseek-r1:8b",
    output: `  Model
    arch             llama
    parameters       8.3B
    quantization     Q4_K_M
    context length   16384
    embedding dim    4096

  Parameters
    stop    "<｜end of sentence｜>"
    stop    "<｜Sentence Queued｜>"
    temperature 0.6
    top_p 0.95

  System Prompt:
    "Eres un asistente virtual experto en Administración de Sistemas Linux y Redes para DAM2..."`
  },
  deploy: {
    title: "AUTOMATIZACIÓN CI/CD & DEPLOY",
    cmd: "git log -n 1 --stat && docker-compose build --no-cache",
    output: `commit d1a3e6f9b8c0a7f1a8e2b839f992 (HEAD -> main, origin/main)
Author: Daniel Giménez Zaragoza <daniel@dam2.es>
Date:   Tue May 26 11:53:18 2026 +0200

    feat(sysops): Integrar base vectorial y optimizar seguridad perimetral.

 README.md           | 12 +++++++++++-
 app/main.py         | 24 ++++++++++++++++++++++--
 docker-compose.yml  |  6 +++++-
 nginx/sysops.conf   |  8 ++++++--
 4 files changed, 45 insertions(+), 6 deletions(-)

[BUILD] Building service: fastapi-app... Done.
[DEPLOY] Docker containers restarted in production environment.`
  },
  ufw: {
    title: "SEGURIDAD PERIMETRAL - FIREWALL UFW",
    cmd: "sudo ufw status verbose",
    output: `Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp (SSH)               LIMIT       192.168.1.0/24             # Acceso SSH local restringido
80/tcp (HTTP)              ALLOW       Anywhere                   # Redirección web
443/tcp (HTTPS)            ALLOW       Anywhere                   # Acceso HTTPS seguro
11434/tcp (Ollama API)     DENY        Anywhere                   # Bloqueado externamente (solo Docker)
8000/tcp (Chroma API)      DENY        Anywhere                   # Bloqueado externamente (solo Docker)
80/tcp (v6)                ALLOW       Anywhere (v6)
443/tcp (v6)               ALLOW       Anywhere (v6)`
  }
};

// --- LOGGING ENGINE (TERMINAL WRITER) ---
function logToTerminal(techKey) {
  const meta = techMetadata[techKey];
  if (!meta) return;

  // Update quick stat active node
  elements.valStatActive.innerText = techKey.toUpperCase();
  
  // Format log output
  const logHTML = `
    <div class="terminal-line"><span class="term-prompt">sysops@dam2:~$</span> <span class="term-cmd">${meta.cmd}</span></div>
    <div class="terminal-output">
      <span class="text-accent" style="font-weight: bold;">[AUDITORÍA] ${meta.title}</span>
---------------------------------------------------------
${meta.output}
    </div>
  `;
  
  // Append or replace
  elements.inspectorOutput.innerHTML = logHTML;
  elements.pendingPrompt.innerText = `systemctl status ${techKey}.service`;
  
  // Auto-scroll
  elements.terminalBody.scrollTop = elements.terminalBody.scrollHeight;
}

// Clear Terminal
elements.clearTermBtn.addEventListener('click', () => {
  elements.inspectorOutput.innerHTML = `
    <div class="terminal-output text-muted">
      Terminal limpia. Haz clic en cualquier elemento 3D de la escena para auditarlo.
    </div>
  `;
  elements.pendingPrompt.innerText = 'systemctl status --sysops';
});

// --- DYNAMIC ROTATION LOOP (rAF) ---
let lastTime = 0;
function updateAnimation(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const deltaTime = (timestamp - lastTime) / 1000;
  lastTime = timestamp;

  // Apply automatic rotation if enabled and not currently dragging
  if (state.autoRotate && !state.isDragging && !state.reduceMotion) {
    // Degrees per second: 360 / autoRotateSpeed
    const degPerSec = 360 / state.autoRotateSpeed;
    state.rotY += degPerSec * deltaTime;
    
    // Normalize Y rotation
    if (state.rotY >= 360) state.rotY -= 360;
    
    // Sync slider Y
    elements.sliderRotY.value = Math.round(state.rotY > 180 ? state.rotY - 360 : state.rotY);
    elements.valRotY.innerText = Math.round(elements.sliderRotY.value) + '°';
  }

  // Apply momentum if velocity exists from drag release
  if (!state.isDragging && (Math.abs(state.velocityX) > 0.05 || Math.abs(state.velocityY) > 0.05)) {
    state.rotY += state.velocityX;
    state.rotX += state.velocityY;
    
    // Decay velocity
    state.velocityX *= 0.92;
    state.velocityY *= 0.92;
    
    // Constraints on X
    state.rotX = Math.max(-85, Math.min(85, state.rotX));
    
    // Sync sliders
    elements.sliderRotY.value = Math.round(state.rotY > 180 ? state.rotY - 360 : (state.rotY < -180 ? state.rotY + 360 : state.rotY));
    elements.sliderRotX.value = Math.round(state.rotX);
    elements.valRotY.innerText = Math.round(elements.sliderRotY.value) + '°';
    elements.valRotX.innerText = Math.round(elements.sliderRotX.value) + '°';
  }

  // Apply transforms
  applyTransformations();
  
  requestAnimationFrame(updateAnimation);
}

// Apply transform styles depending on active scene
function applyTransformations() {
  if (state.reduceMotion) {
    // Set static transform values
    elements.cube.style.transform = `rotateX(-16deg) rotateY(32deg)`;
    elements.carouselRing.style.transform = `rotateY(${-state.carouselIndex * state.carouselRotationAngle}deg)`;
    elements.layersStack.style.transform = `rotateX(60deg) rotateZ(-30deg)`;
    elements.groundShadow.style.transform = `translateX(-50%) rotateX(90deg) translateZ(-160px) scale(1)`;
    return;
  }

  // Apply to Active Scene
  if (state.activeScene === 'cube-scene') {
    elements.cube.style.transform = `rotateX(${state.rotX}deg) rotateY(${state.rotY}deg)`;
    
    // Ground shadow reacts dynamically to rotation tilt
    const scaleFactor = 1 - (Math.abs(state.rotX) / 180);
    elements.groundShadow.style.transform = `translateX(-50%) rotateX(90deg) translateZ(-165px) scale(${scaleFactor})`;
  } 
  else if (state.activeScene === 'carousel-scene') {
    // Carousel rotates horizontally based on Y rotation, plus active index offset
    const activeCarouselOffset = -state.carouselIndex * state.carouselRotationAngle;
    elements.carouselRing.style.transform = `rotateX(${state.rotX * 0.3}deg) rotateY(${state.rotY + activeCarouselOffset}deg)`;
  } 
  else if (state.activeScene === 'layers-scene') {
    // Parallax layers stack moves isometrically
    elements.layersStack.style.transform = `rotateX(${60 + state.rotX * 0.4}deg) rotateZ(${-30 + state.rotY * 0.5}deg)`;
  }
}

// --- INTERACTIVE DRAG TO ROTATE (MOUSE & TOUCH) ---
function initDragControls() {
  const startDrag = (clientX, clientY) => {
    if (!state.dragRotationEnabled || state.reduceMotion) return;
    
    state.isDragging = true;
    state.startX = clientX;
    state.startY = clientY;
    state.startRotX = state.rotX;
    state.startRotY = state.rotY;
    state.velocityX = 0;
    state.velocityY = 0;
    
    elements.viewport.style.cursor = 'grabbing';
  };

  const moveDrag = (clientX, clientY) => {
    if (!state.isDragging) return;
    
    const deltaX = clientX - state.startX;
    const deltaY = clientY - state.startY;
    
    // Sensitivity factor
    const sensitivity = 0.35;
    
    const nextRotY = state.startRotY + deltaX * sensitivity;
    const nextRotX = state.startRotX - deltaY * sensitivity;
    
    // Calculate velocities for inertia
    state.velocityX = nextRotY - state.rotY;
    state.velocityY = nextRotX - state.rotX;
    
    state.rotY = nextRotY;
    // Limit vertical angle so user doesn't flip the scene upside down
    state.rotX = Math.max(-85, Math.min(85, nextRotX));
    
    // Update sliders
    elements.sliderRotY.value = Math.round(state.rotY > 180 ? state.rotY - 360 : (state.rotY < -180 ? state.rotY + 360 : state.rotY));
    elements.sliderRotX.value = Math.round(state.rotX);
    elements.valRotY.innerText = Math.round(elements.sliderRotY.value) + '°';
    elements.valRotX.innerText = Math.round(elements.sliderRotX.value) + '°';
  };

  const endDrag = () => {
    if (!state.isDragging) return;
    state.isDragging = false;
    elements.viewport.style.cursor = 'grab';
  };

  // Mouse events
  elements.viewport.addEventListener('mousedown', (e) => {
    // Only drag with left click
    if (e.button !== 0) return;
    startDrag(e.clientX, e.clientY);
  });
  
  window.addEventListener('mousemove', (e) => {
    moveDrag(e.clientX, e.clientY);
  });
  
  window.addEventListener('mouseup', endDrag);

  // Touch events for mobile support
  elements.viewport.addEventListener('touchstart', (e) => {
    if (e.touches.length > 0) {
      startDrag(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });
  
  window.addEventListener('touchmove', (e) => {
    if (e.touches.length > 0) {
      moveDrag(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });
  
  window.addEventListener('touchend', endDrag);
}

// --- SLIDERS EVENT HANDLERS ---
function initSliderHandlers() {
  elements.sliderRotY.addEventListener('input', (e) => {
    state.rotY = parseFloat(e.target.value);
    elements.valRotY.innerText = Math.round(state.rotY) + '°';
    // Pause auto-rotate if manual control is touched
    if (state.autoRotate) {
      state.autoRotate = false;
      elements.toggleAuto.checked = false;
      elements.valStatAuto.innerText = 'OFF';
      elements.valStatAuto.classList.remove('text-accent');
    }
  });

  elements.sliderRotX.addEventListener('input', (e) => {
    state.rotX = parseFloat(e.target.value);
    elements.valRotX.innerText = Math.round(state.rotX) + '°';
  });

  elements.sliderPersp.addEventListener('input', (e) => {
    state.perspective = parseInt(e.target.value, 10);
    elements.valPersp.innerText = state.perspective + 'px';
    elements.valStatPersp.innerText = state.perspective + 'px';
    elements.viewport.style.perspective = state.perspective + 'px';
  });

  elements.sliderSpeed.addEventListener('input', (e) => {
    state.autoRotateSpeed = parseInt(e.target.value, 10);
    elements.valSpeed.innerText = state.autoRotateSpeed + 's';
  });
}

// --- SYSTEM PREFERENCES & TOGGLES ---
function initPreferenceHandlers() {
  // Auto-Rotate
  elements.toggleAuto.addEventListener('change', (e) => {
    state.autoRotate = e.target.checked;
    elements.valStatAuto.innerText = state.autoRotate ? 'ON' : 'OFF';
    if (state.autoRotate) {
      elements.valStatAuto.classList.add('text-accent');
      elements.speedContainer.style.display = 'block';
    } else {
      elements.valStatAuto.classList.remove('text-accent');
      elements.speedContainer.style.display = 'none';
    }
  });

  // Drag Rotation
  elements.toggleDrag.addEventListener('change', (e) => {
    state.dragRotationEnabled = e.target.checked;
  });

  // Reduce Motion (Accessibility)
  elements.toggleReduce.addEventListener('change', (e) => {
    setReduceMotion(e.target.checked);
  });

  // Listen to OS prefers-reduced-motion
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (mediaQuery.matches) {
    elements.toggleReduce.checked = true;
    setReduceMotion(true);
  }
}

function setReduceMotion(enabled) {
  state.reduceMotion = enabled;
  if (enabled) {
    elements.body.classList.add('reduced-motion-active');
    // Disable auto-rotate
    state.autoRotate = false;
    elements.toggleAuto.checked = false;
    elements.valStatAuto.innerText = 'OFF';
    elements.valStatAuto.classList.remove('text-accent');
    // Hide speed slider
    elements.speedContainer.style.display = 'none';
  } else {
    elements.body.classList.remove('reduced-motion-active');
    // Restore state
    state.autoRotate = elements.toggleAuto.checked;
    elements.valStatAuto.innerText = state.autoRotate ? 'ON' : 'OFF';
    if (state.autoRotate) {
      elements.valStatAuto.classList.add('text-accent');
      elements.speedContainer.style.display = 'block';
    }
  }
}

// --- SCENE TABS SYSTEM ---
function initSceneTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Deactivate tabs
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      const targetScene = tab.dataset.scene;
      switchScene(targetScene);
    });
  });
}

function switchScene(sceneId) {
  state.activeScene = sceneId;
  
  // Hide all scenes
  elements.cubeScene.classList.remove('active');
  elements.carouselScene.classList.remove('active');
  elements.layersScene.classList.remove('active');
  
  // Show target scene
  const target = document.getElementById(sceneId);
  target.classList.add('active');
  
  // Update state values & text
  let humanFriendlyName = "Cubo 3D";
  if (sceneId === 'carousel-scene') {
    humanFriendlyName = "Carrusel 3D";
    // Setup carousel indicator
    updateCarouselIndicator();
  } else if (sceneId === 'layers-scene') {
    humanFriendlyName = "Pila de Capas";
  }
  elements.valStatActive.innerText = humanFriendlyName;
  
  // Reset rotations or set context appropriate defaults
  if (sceneId === 'layers-scene') {
    state.rotX = 0; // Layers work better with neutral initial tilts
    state.rotY = 0;
  } else {
    state.rotX = -16;
    state.rotY = 32;
  }
  
  // Update sliders to match reset values
  elements.sliderRotY.value = Math.round(state.rotY);
  elements.sliderRotX.value = Math.round(state.rotX);
  elements.valRotY.innerText = Math.round(state.rotY) + '°';
  elements.valRotX.innerText = Math.round(state.rotX) + '°';
  
  // Write a clean switch log in the terminal
  const logHTML = `
    <div class="terminal-line"><span class="term-prompt">sysops@dam2:~$</span> <span class="term-cmd">switch-stage --target=${sceneId}</span></div>
    <div class="terminal-output text-success">
      [SCENE] Renderizando escena 3D: '${humanFriendlyName.toUpperCase()}'
      [RENDER] Aceleración por hardware WebGL/CSS3D: HABILITADA
      [STAGE] Transformación: perspective(${state.perspective}px), preserve-3d
    </div>
  `;
  elements.inspectorOutput.innerHTML = logHTML;
  elements.pendingPrompt.innerText = `systemctl status ${sceneId}.service`;
  elements.terminalBody.scrollTop = elements.terminalBody.scrollHeight;
}

// --- CAROUSEL NAVIGATION ENGINE ---
function initCarouselControls() {
  const rotateCarousel = (direction) => {
    if (direction === 'next') {
      state.carouselIndex++;
    } else {
      state.carouselIndex--;
    }
    
    // Clamp or wrap carousel index
    if (state.carouselIndex >= state.carouselItemCount) {
      state.carouselIndex = 0;
    } else if (state.carouselIndex < 0) {
      state.carouselIndex = state.carouselItemCount - 1;
    }
    
    // Pause auto rotate on interaction
    if (state.autoRotate) {
      state.autoRotate = false;
      elements.toggleAuto.checked = false;
      elements.valStatAuto.innerText = 'OFF';
      elements.valStatAuto.classList.remove('text-accent');
    }
    
    updateCarouselIndicator();
    
    // Find active element's technology dataset key
    const activeItem = document.querySelector(`.carousel-item[data-index="${state.carouselIndex}"]`);
    if (activeItem) {
      const techKey = activeItem.dataset.tech;
      logToTerminal(techKey);
    }
  };

  elements.carouselNext.addEventListener('click', () => rotateCarousel('next'));
  elements.carouselPrev.addEventListener('click', () => rotateCarousel('prev'));
}

function updateCarouselIndicator() {
  elements.carouselIndicator.innerText = `Elemento ${state.carouselIndex + 1} / ${elements.carouselItemCount}`;
}

// --- DYNAMIC CARD & ELEMENT CLICK SELECTION ---
function initClickListeners() {
  // 1. Cube faces
  const faces = document.querySelectorAll('.face');
  faces.forEach(face => {
    face.addEventListener('click', () => {
      const tech = face.dataset.tech;
      logToTerminal(tech);
    });
    // Keyboard accessibility support
    face.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        logToTerminal(face.dataset.tech);
      }
    });
  });

  // 2. Carousel items
  const items = document.querySelectorAll('.carousel-item');
  items.forEach(item => {
    item.addEventListener('click', () => {
      const index = parseInt(item.dataset.index, 10);
      state.carouselIndex = index;
      updateCarouselIndicator();
      logToTerminal(item.dataset.tech);
    });
    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const index = parseInt(item.dataset.index, 10);
        state.carouselIndex = index;
        updateCarouselIndicator();
        logToTerminal(item.dataset.tech);
      }
    });
  });

  // 3. Layer items
  const layers = document.querySelectorAll('.layer-item');
  layers.forEach(layer => {
    layer.addEventListener('click', () => {
      logToTerminal(layer.dataset.tech);
    });
  });
}

// --- THEME ENGINE ---
function initThemeSelector() {
  const themeBtns = document.querySelectorAll('.theme-btn');
  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Deactivate theme buttons
      themeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const theme = btn.dataset.theme;
      applyTheme(theme);
    });
  });
}

function applyTheme(themeName) {
  // Remove existing themes from body
  elements.body.classList.remove('theme-neon', 'theme-emerald', 'theme-amber', 'theme-ice');
  
  // Apply new theme class if not default neon
  if (themeName !== 'neon') {
    elements.body.classList.add(`theme-${themeName}`);
  }
  
  state.activeTheme = themeName;
  
  // Log theme change to terminal
  const colors = {
    neon: 'VIOLET/TEAL NEON',
    emerald: 'MATRIX EMERALD',
    amber: 'VINTAGE AMBER',
    ice: 'GLACIAL ICE'
  };
  
  const logHTML = `
    <div class="terminal-line"><span class="term-prompt">sysops@dam2:~$</span> <span class="term-cmd">set-theme --style=${themeName}</span></div>
    <div class="terminal-output text-info">
      [THEME] Cambiando esquema lumínico del sistema...
      [COLOR] Perfil activo: ${colors[themeName]}
      [LIGHT] Renderizado de reflejos de ambiente actualizado.
    </div>
  `;
  elements.inspectorOutput.innerHTML = logHTML;
  elements.terminalBody.scrollTop = elements.terminalBody.scrollHeight;
}

// --- GLOBAL KEYBOARD ACCESSIBILITY ---
function initKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    // Clear terminal: Escape key
    if (e.key === 'Escape') {
      elements.clearTermBtn.click();
    }
    
    // Toggle auto rotation: Space bar
    // Avoid triggering when user is in form inputs/buttons
    if (e.key === ' ' && document.activeElement.tagName !== 'BUTTON' && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      elements.toggleAuto.click();
    }
  });
}

// --- INITIALIZATION ---
function init() {
  // 1. Setup events
  initDragControls();
  initSliderHandlers();
  initPreferenceHandlers();
  initSceneTabs();
  initCarouselControls();
  initClickListeners();
  initThemeSelector();
  initKeyboardShortcuts();
  
  // 2. Initial state configuration
  setReduceMotion(elements.toggleReduce.checked);
  
  // 3. Start render loop
  requestAnimationFrame(updateAnimation);
}

// Initialize on load
window.addEventListener('DOMContentLoaded', init);
