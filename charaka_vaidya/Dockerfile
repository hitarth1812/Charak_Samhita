FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ── Install system deps (needed by some Python packages) ──────
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# ── Install Python deps (cached layer) ───────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ────────────────────────────────────
COPY . .

# ── Expose ports: FastAPI 8000, Streamlit 8501 ───────────────
EXPOSE 8000 8501

# ── Entrypoint ───────────────────────────────────────────────
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
