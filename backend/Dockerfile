# syntax=docker/dockerfile:1.7

# --- Stage 1: Base ---
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# --- Stage 2: Dependencies ---
FROM base AS deps
COPY backend/requirements.txt .
RUN python -m venv "$VENV" \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# --- Stage 3: Development (hot reload) ---
FROM deps AS development
ENV PYTHONPATH=/app
COPY backend/ /app/
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Stage 4: Production ---
FROM base AS production
COPY --from=deps /opt/venv /opt/venv
RUN useradd -m -u 1001 appuser
WORKDIR /app
COPY --chown=appuser:appuser backend/ /app/
ENV PYTHONPATH=/app PORT=8000
EXPOSE 8000
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/todos || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
