# Jarvis Runtime

**¿Harto de quedarte a mitad de una tarea por límites de tokens?**

Runtime híbrido que usa tu modelo local primero y solo llama a cloud cuando realmente hace falta.
Sin límites artificiales. Sin vendor lock-in. Sin sorpresas en la factura.

```
jarvis ask "explica qué es un decorator en Python"
```

```
⚡ LOCAL · qwen2.5:7b
╭─ Response ─────────────────────────────────────────────╮
│                                                         │
│  Un decorator es una función que envuelve a otra        │
│  función para extender su comportamiento sin            │
│  modificar su código fuente...                          │
│                                                         │
╰─────────────────────────────────────────────────────────╯
Latency:  2.1s   Tokens: ~94   Cost: $0.00000
```

---

## Instalación

**Requisito:** [Docker](https://docs.docker.com/get-docker/)

```bash
git clone https://github.com/Joaquinriosheredia/jarvis-runtime
cd jarvis-runtime
./setup.sh
```

El primer arranque descarga el modelo qwen2.5:7b (~4.7GB). Tarda 2–5 minutos según tu conexión.
Cuando termine, el comando `jarvis` quedará disponible en tu terminal.

---

## Uso

```bash
jarvis ask "hola"
jarvis history        # últimas 10 interacciones
jarvis usage          # tokens y coste acumulado
```

---

## Casos de uso reales

**1. Explicar código sin salir del flujo de trabajo**
```bash
jarvis ask "¿qué hace esta línea en Python: [x for x in lista if x > 0]?"
# Responde en local en ~2s, sin abrir un navegador
```

**2. Decisiones rápidas de arquitectura**
```bash
jarvis ask "¿cuándo usar Redis en lugar de una base de datos relacional?"
# Prompt complejo → enruta automáticamente a cloud si tienes API key
```

**3. Revisar tu historial de consultas**
```bash
jarvis history --limit 25
# Todas tus preguntas y respuestas guardadas localmente en SQLite
```

---

## OpenAI (opcional)

El sistema funciona sin API key. Si quieres fallback a cloud para prompts complejos, añade tu key a `.env`:

```env
OPENAI_API_KEY=sk-...
```

---

## Licencia

MIT
