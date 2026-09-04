# Shipyard — running the app

A demo of one loop over your real Instagram export:
**capture → understand → intent → schedule → resurface → resolve**, plus
semantic search, automatic topic clustering, and archive Q&A.

```
backend/     FastAPI + retrieval index (Python)
frontend/    Vite + React + TypeScript
```

Nothing here reads a database at request time: the corpus + embeddings +
clusters are a static index built once; the only mutable state is a small
SQLite file of your notes / schedules / resolves.

---

## 1. One-time setup

### Data
Put the two Instagram export files at the repo root (default paths, override in
`.env`):

```
saved_posts.json
liked_posts (1).json
```

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate            # Windows;  source .venv/bin/activate  elsewhere
pip install -r requirements.txt   # or requirements-local.txt (see Embeddings below)
python -m scripts.build_index     # builds data/index/  (~1–4 min, CPU)
```

### Frontend

Requires **Node ≥ 18**.

```bash
cd frontend
npm install
```

---

## 2. Run (two terminals)

```bash
# terminal 1
cd backend && .venv/Scripts/activate && python -m shipyard.main
#   -> http://127.0.0.1:8000  (API + docs at /docs)

# terminal 2
cd frontend && npm run dev
#   -> http://localhost:5173
```

The vite dev server proxies `/api` to the backend, so no CORS config is needed
locally.

---

## 3. Config — everything is env-driven

Copy `.env.example` to `.env` at the repo root. Key switches:

| Var | Default | Notes |
|---|---|---|
| `EMBED_BACKEND` | `fastembed` | `fastembed` (ONNX, small) · `sentence-transformers` (torch) · `tfidf` (sklearn, no native deps) |
| `CLUSTER_METHOD` | `hdbscan` | `hdbscan` (auto count, leaves one-offs as "ungrouped") · `kmeans` (fixed partition, auto-K) |
| `LLM_PROVIDER` | `none` | `none` = heuristic summaries/tags/cluster-names, Q&A disabled. `anthropic` = Claude enrichment + Q&A |
| `ANTHROPIC_API_KEY` | — | required when `LLM_PROVIDER=anthropic` |
| `LLM_MODEL` | `claude-sonnet-5` | used for enrichment + Q&A |
| `LLM_MAX_ENRICH_ITEMS` | `0` (all) | cap the Claude enrichment pass to bound cost; the rest fall back to heuristics |

After changing embedding or clustering settings, re-run `python -m scripts.build_index`.

### Embeddings note (Windows)
`fastembed`/`onnxruntime` and `torch` need a current MS VC++ runtime. If the
ONNX DLL fails to load on an older Windows 10 build, either install the latest
[VC++ redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe), or set
`EMBED_BACKEND=tfidf` (pure scikit-learn, no native deps) and rebuild.

---

## 4. Deploying later

The architecture is deployment-ready without changes:

- **Frontend/backend split point** is a single `VITE_API_BASE_URL` (frontend) /
  `CORS_ORIGINS` (backend).
- **One-service deploy:** `npm run build` in `frontend/`, then the backend
  serves `frontend/dist/` automatically — one process, one port.
- **Render / Fly / Railway:** see `deploy/`. A `Dockerfile` and `render.yaml`
  are included. Mount a persistent disk for `DATABASE_PATH`; commit or
  build-step the `data/index/` artifact.
- **Not Vercel** — the app is a long-lived process with an in-memory index and a
  writable SQLite file; serverless doesn't fit.
