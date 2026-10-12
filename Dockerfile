# MoodQueue — complete app in ONE image: web interface + API + SQLite.
#
#   docker build -t moodqueue .
#   docker run -p 8000:8000 -v moodqueue-data:/app/data moodqueue
#   -> http://localhost:8000
#
# Base images are pinned to exact versions so the build stays reproducible.

# ---- 1. Build the web app ---------------------------------------------------
FROM node:22.11.0-bookworm-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

# ---- 2. Python backend serving API + built web app -------------------------
FROM python:3.12.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATA_DIR=/app/data
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY --from=web /web/dist ./static

# SQLite database + auto-generated secret key live here: keep it in a volume
VOLUME /app/data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT','8000'))"

# $PORT is set by hosts like Railway/Render; 8000 otherwise
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
