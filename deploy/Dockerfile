# Single-service image: builds the frontend, serves it from the FastAPI backend.
# Build context = repo root:  docker build -f deploy/Dockerfile -t shipyard .

# ---- frontend build ----
FROM node:20-slim AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- backend ----
FROM python:3.11-slim AS app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/ ./
COPY --from=web /web/dist ./frontend/dist

# Data: mount raw exports + a persistent volume for the SQLite state file.
# Build the index at container start if it's missing, then launch.
ENV SHIPYARD_ENV=production \
    INDEX_DIR=/data/index \
    DATABASE_PATH=/data/state.sqlite \
    RAW_SAVED_PATH=/data/raw/saved_posts.json \
    RAW_LIKED_PATH=/data/raw/liked_posts.json \
    EMBED_BACKEND=fastembed \
    API_HOST=0.0.0.0 \
    API_PORT=8000

EXPOSE 8000
CMD ["sh", "-c", "test -f $INDEX_DIR/corpus.parquet || python -m scripts.build_index; python -m shipyard.main"]
