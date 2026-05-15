#!/bin/bash
set -e

COMPOSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$COMPOSE_DIR"

command -v docker >/dev/null 2>&1 || { echo "Error: Docker not installed. Get it at https://docs.docker.com/get-docker/"; exit 1; }

[ ! -f .env ] && cp .env.example .env

echo "Building and starting Jarvis Runtime..."
docker compose up -d --build

echo ""
echo "Downloading qwen2.5:7b model (first run only, ~4.7GB)..."
echo "This may take a few minutes depending on your connection."
echo ""

until docker compose exec -T jarvis-runtime echo ok >/dev/null 2>&1; do
  printf "."
  sleep 5
done
echo ""

# Install jarvis wrapper
cat > /tmp/jarvis-wrapper << 'WRAPPER'
#!/bin/bash
COMPOSE_DIR="__COMPOSE_DIR__"
docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec jarvis-runtime jarvis "$@"
WRAPPER
sed -i "s|__COMPOSE_DIR__|$COMPOSE_DIR|g" /tmp/jarvis-wrapper

if command -v sudo >/dev/null 2>&1; then
  sudo mv /tmp/jarvis-wrapper /usr/local/bin/jarvis
  sudo chmod +x /usr/local/bin/jarvis
else
  mv /tmp/jarvis-wrapper /usr/local/bin/jarvis
  chmod +x /usr/local/bin/jarvis
fi

echo ""
echo "Jarvis Runtime is ready."
echo ""
echo "  jarvis ask \"hola\""
echo ""
