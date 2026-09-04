"""Central configuration. Everything is env-driven with localhost defaults.

Nothing else in the codebase reads os.environ directly — import `settings`
from here. That keeps "where does this run" a one-file concern.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ directory — all relative paths resolve against this.
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Runtime ----
    shipyard_env: str = "local"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ---- Data locations ----
    raw_saved_path: str = "../saved_posts.json"
    raw_liked_path: str = "../liked_posts (1).json"
    index_dir: str = "data/index"
    database_path: str = "data/state.sqlite"

    # ---- Embeddings ----
    # tfidf            -> sklearn TF-IDF + LSA; no native deps, fitted at build.
    # fastembed        -> ONNX, no torch, best for small Linux hosts (Render).
    # sentence-transformers -> torch; most portable where torch loads.
    # tfidf is the default: this project's target machine is a 2-core laptop
    # where transformer inference is ~1 hr for the full corpus. On faster
    # hardware or when deploying, set EMBED_BACKEND=fastembed and rebuild.
    embed_backend: str = "tfidf"
    embed_model: str = "BAAI/bge-small-en-v1.5"  # used by non-tfidf backends
    embed_batch: int = 256
    tfidf_components: int = 200
    tfidf_max_features: int = 20000

    # ---- Clustering ----
    cluster_method: str = "kmeans"  # hdbscan | kmeans
    hdbscan_min_cluster_size: int = 18
    kmeans_k: int = 0  # 0 = auto
    kmeans_k_min: int = 15
    kmeans_k_max: int = 45
    cluster_max_share: float = 0.08  # clusters bigger than this fraction -> ungrouped

    # ---- LLM ----
    llm_provider: str = "none"  # none | anthropic
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-5"
    llm_enrich_model: str = ""
    llm_max_enrich_items: int = 0  # 0 = all

    # ---- Derived path helpers ----
    def _resolve(self, value: str) -> Path:
        p = Path(value)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()

    @property
    def saved_file(self) -> Path:
        return self._resolve(self.raw_saved_path)

    @property
    def liked_file(self) -> Path:
        return self._resolve(self.raw_liked_path)

    @property
    def index_path(self) -> Path:
        return self._resolve(self.index_dir)

    @property
    def db_path(self) -> Path:
        return self._resolve(self.database_path)

    @property
    def corpus_file(self) -> Path:
        return self.index_path / "corpus.parquet"

    @property
    def embeddings_file(self) -> Path:
        return self.index_path / "embeddings.npy"

    @property
    def clusters_file(self) -> Path:
        return self.index_path / "clusters.json"

    @property
    def facets_file(self) -> Path:
        return self.index_path / "facets.json"

    @property
    def embed_model_file(self) -> Path:
        return self.index_path / "embed_model.pkl"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def enrich_model(self) -> str:
        return self.llm_enrich_model or self.llm_model

    @property
    def llm_enabled(self) -> bool:
        return self.llm_provider == "anthropic" and bool(self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
