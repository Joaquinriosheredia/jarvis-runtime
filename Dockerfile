FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY jarvis/ jarvis/

RUN pip install --no-cache-dir -e .

VOLUME /app/data

CMD ["sleep", "infinity"]
