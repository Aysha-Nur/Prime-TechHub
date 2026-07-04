# ── Base image: slim Python 3.14 (matches your exact terminal runtime) ──
FROM python:3.14-slim

# ── System dependencies ─────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Set working directory inside the container ──────────────────
WORKDIR /app

# ── Install Python dependencies FIRST (leverages Docker cache) ──
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy all application source code ────────────────────────────
COPY . .

# ── Create data directory for SQLite persistence ────────────────
RUN mkdir -p data

# ── Expose Streamlit's internal port ────────────────────────────
EXPOSE 8501

# ── Health check so Docker knows if the app is alive ────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# ── Launch command with proxy safety flags ──────────────────────
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
