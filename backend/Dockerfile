# API-only image (used when the web app is hosted elsewhere, e.g. Vercel).
# For the all-in-one image (web + API), use the Dockerfile at the repo root.
FROM python:3.12.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 DATA_DIR=/app/data
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

VOLUME /app/data
EXPOSE 8000
# $PORT is injected by Railway; defaults to 8000 locally.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
