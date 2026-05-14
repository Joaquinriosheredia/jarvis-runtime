# Jarvis Runtime

**¿Harto de quedarte a mitad de una tarea por límites de tokens?**

Runtime híbrido que usa tu modelo local primero y solo llama a cloud cuando realmente hace falta.
Sin límites artificiales. Sin vendor lock-in. Sin sorpresas en la factura.

**Local-first hybrid AI runtime.** Runs fast and free on your machine. Falls back to OpenAI only when needed.

```
jarvis ask "explica qué es un transformer en 2 líneas"
```

```
⚡ LOCAL · llama3
╭─ Response ──────────────────────────────────────────────────────────╮
│                                                                      │
│  Un transformer es una arquitectura de red neuronal basada en        │
│  mecanismos de atención que procesa secuencias en paralelo...        │
│                                                                      │
╰──────────────────────────────────────────────────────────────────────╯
──────────────────────────────────
Latency:  1.34s
Tokens:   ~87
Cost:     $0.00000
Reason:   local suficiente
```

---

## Arquitectura

```
jarvis ask "..."
     │
     ▼
 router.py          ← scoring del prompt (longitud + keywords)
     │
     ├─ score == 0 ──► llm_local.py  (Ollama)   → respuesta válida → ✓
     │                      │
     │                 respuesta inválida
     │                      │
     └─ score > 0 ──► llm_cloud.py  (OpenAI)   → respuesta → ✓
     
     ▼
 memory.py    ← guarda prompt + respuesta en SQLite
 cost.py      ← registra tokens y coste acumulado
```

**Reglas de routing:**
- Prompt corto y genérico → **local** (gratis, ~1-3s)
- Prompt con código, arquitectura, comparativas → **cloud** (gpt-4o-mini)
- Local falla o responde mal → **fallback automático** a cloud

---

## Instalación

```bash
git clone https://github.com/tu-usuario/jarvis-runtime
cd jarvis-runtime

python -m venv venv
source venv/bin/activate

pip install -e ".[dev]"
```

---

## Configuración

Copia el archivo `.env` y añade tu API key:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-...       # requerido para cloud y fallback
OPENAI_MODEL=gpt-4o-mini    # opcional, default: gpt-4o-mini
OLLAMA_MODEL=llama3          # opcional, default: llama3
OLLAMA_BASE_URL=http://localhost:11434  # opcional
```

**Para usar modelos locales** necesitas [Ollama](https://ollama.com) instalado:

```bash
ollama pull llama3
ollama serve
```

---

## Uso

### Preguntar

```bash
jarvis ask "¿cuál es la diferencia entre TCP y UDP?"
jarvis ask "escribe una función python que invierta una lista"
jarvis ask "diseña la arquitectura de una API REST para un e-commerce"
```

### Ver historial

```bash
jarvis history           # últimas 10 interacciones
jarvis history --limit 25
```

### Ver uso y costes

```bash
jarvis usage
```

```
      Jarvis — Resumen de uso
 Fuente   Tokens   Coste (USD)
 local    1842     $0.00000
 cloud    347      $0.00694

Total requests: 12
Total tokens:   2189
Total cost:     $0.00694
```

---

## Estructura del proyecto

```
jarvis-runtime/
├── jarvis/
│   ├── __init__.py
│   ├── config.py      ← variables de entorno y paths
│   ├── router.py      ← lógica de routing local/cloud
│   ├── llm_local.py   ← cliente Ollama
│   ├── llm_cloud.py   ← cliente OpenAI
│   ├── memory.py      ← historial en SQLite
│   ├── cost.py        ← tracking de tokens y costes
│   └── cli.py         ← interfaz de línea de comandos
├── tests/
│   └── test_router.py
├── data/              ← generado automáticamente
│   └── jarvis.db
├── .env
├── pyproject.toml
└── README.md
```

---

## Tests

```bash
pytest
```

Los tests verifican:
- Scoring del prompt (local vs cloud)
- Routing local cuando la respuesta es válida
- Fallback a cloud cuando local falla o devuelve basura
- Estimación de costes

---

## Roadmap

- [ ] Streaming de respuestas en CLI
- [ ] Soporte para múltiples modelos locales (selector interactivo)
- [ ] Comando `jarvis search` con búsqueda en historial
- [ ] Exportar historial a Markdown
- [ ] Soporte para Claude (Anthropic) como alternativa cloud
- [ ] Dashboard web minimalista (FastAPI + HTMX)

---

## Filosofía

> "Instalar, ejecutar y entender el valor en menos de 2 minutos."

- **Local-first**: Ollama corre en tu máquina, sin latencia de red, sin coste.
- **Cloud solo cuando vale la pena**: prompts complejos que necesitan un modelo más potente.
- **Sin magia**: el código es simple y legible. Puedes leerlo en 20 minutos.
- **Sin lock-in**: cambiar de OpenAI a otro proveedor es un cambio de 10 líneas.

---

## Licencia

MIT
