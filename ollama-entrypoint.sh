#!/bin/sh
set -e

ollama serve &

until ollama list >/dev/null 2>&1; do
  sleep 1
done

ollama pull qwen2.5:7b

wait
