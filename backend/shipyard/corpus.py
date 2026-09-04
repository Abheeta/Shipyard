"""In-memory static index: corpus rows + embedding matrix + cluster names.

Loaded once at process start. Never mutated at runtime — all user state lives
in state.py (SQLite).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .config import settings


class Corpus:
    def __init__(self) -> None:
        self.df: pd.DataFrame = pd.DataFrame()
        self.embeddings: np.ndarray = np.zeros((0, 384), dtype=np.float32)
        # confidence weight for semantic ranking: near-empty captions embed to
        # noisy directions and otherwise rank spuriously high.
        self.text_weight: np.ndarray = np.zeros(0, dtype=np.float32)
        self.cluster_names: dict[int, str] = {}
        self.facets: dict = {}
        self._id_to_pos: dict[str, int] = {}
        self.loaded = False

    def load(self) -> None:
        if not settings.corpus_file.exists():
            raise FileNotFoundError(
                f"{settings.corpus_file} missing. Run: python -m scripts.build_index"
            )
        self.df = pd.read_parquet(settings.corpus_file)
        self.embeddings = np.load(settings.embeddings_file)
        if settings.clusters_file.exists():
            raw = json.loads(settings.clusters_file.read_text(encoding="utf-8"))
            self.cluster_names = {int(k): v["name"] for k, v in raw.items()}
        if settings.facets_file.exists():
            self.facets = json.loads(settings.facets_file.read_text(encoding="utf-8"))
        clen = self.df["caption"].fillna("").str.len().to_numpy()
        self.text_weight = np.clip(clen / 45.0, 0.3, 1.0).astype(np.float32)
        self._id_to_pos = {rid: i for i, rid in enumerate(self.df["id"].tolist())}
        self.loaded = True

    # ---- lookups ----
    def __len__(self) -> int:
        return len(self.df)

    def pos(self, item_id: str) -> int | None:
        return self._id_to_pos.get(item_id)

    def row(self, item_id: str) -> dict | None:
        p = self.pos(item_id)
        return None if p is None else self._row_at(p)

    def _row_at(self, p: int) -> dict:
        r = self.df.iloc[p].to_dict()
        r["cluster_name"] = self.cluster_names.get(int(r.get("cluster_id", -1)), "")
        # normalize numpy/pandas scalars for JSON
        for k in ("hashtags", "tags"):
            v = r.get(k)
            r[k] = list(v) if v is not None else []
        r["is_ad"] = bool(r.get("is_ad", False))
        r["is_actionable"] = bool(r.get("is_actionable", True))
        r["cluster_id"] = int(r.get("cluster_id", -1))
        r["timestamp"] = int(r.get("timestamp", 0))
        if r.get("year") is not None and not pd.isna(r.get("year")):
            r["year"] = int(r["year"])
        else:
            r["year"] = None
        sd = r.get("saved_date")
        r["saved_date"] = str(sd) if sd is not None and not pd.isna(sd) else None
        return r

    def rows_at(self, positions: list[int]) -> list[dict]:
        return [self._row_at(p) for p in positions]


corpus = Corpus()
