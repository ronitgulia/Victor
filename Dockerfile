# ─────────────────────────────────────────────────────────────────
# VICTOR BOT DETECTION — Dockerfile
# ─────────────────────────────────────────────────────────────────
# Runs two services inside one container via entrypoint.sh:
#   1. Flask  honeypot server  → http://localhost:5000
#   2. Streamlit dashboard     → http://localhost:8501
#
# Build & run:
#   docker compose up
# ─────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# ── System deps ───────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies first (layer cache) ──────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────────────────────────
COPY . .

# ── Create persistent dirs (data & models may be mounted) ─────────
RUN mkdir -p data/shap models

# ── Make entrypoint executable ────────────────────────────────────
RUN chmod +x entrypoint.sh

# ── Expose ports ──────────────────────────────────────────────────
EXPOSE 5000 8501

# ── Default command ───────────────────────────────────────────────
ENTRYPOINT ["./entrypoint.sh"]
