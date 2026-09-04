import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import type { CreatorRank, Query } from "../types";
import { cx } from "../util";

const PAGE = 40;
const SOURCE: [NonNullable<Query["source"]>, string][] = [
  ["both", "Both"],
  ["saved", "Saved"],
  ["liked", "Liked"],
];

export function CreatorsView({ onCreator }: { onCreator: (creator: string) => void }) {
  const [source, setSource] = useState<NonNullable<Query["source"]>>("both");
  const [creators, setCreators] = useState<CreatorRank[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  const load = useCallback((nextOffset: number, append: boolean) => {
    setLoading(true);
    api
      .creators({ source, offset: nextOffset, limit: PAGE })
      .then((r) => {
        setTotal(r.total);
        setOffset(nextOffset);
        setCreators((prev) => (append ? [...prev, ...r.creators] : r.creators));
      })
      .finally(() => setLoading(false));
  }, [source]);

  useEffect(() => load(0, false), [load]);

  return (
    <>
      <div className="console__row" style={{ marginBottom: 16 }}>
        <span className="eyebrow">Source</span>
        <div className="seg">
          {SOURCE.map(([v, label]) => (
            <button key={v} className={cx(source === v && "is-active")} onClick={() => setSource(v)}>
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="result-count">
        <strong>{loading && !creators.length ? "…" : total.toLocaleString()}</strong>
        <span> creators</span>
      </div>

      {!loading && !creators.length ? (
        <div className="empty">
          <div className="empty__title">No creators</div>
          <p className="empty__body">Nothing matches this source filter.</p>
        </div>
      ) : (
        <div className="grid">
          {creators.map((c) => (
            <button key={c.creator} className="card" onClick={() => onCreator(c.creator)}>
              <div className="card__top">
                <span className="card__creator">@{c.creator}</span>
              </div>
              <div className="card__summary">{c.creator_name || "—"}</div>
              <div className="card__foot">
                {c.saved_count > 0 && <span className="badge badge--saved">{c.saved_count} saved</span>}
                {c.liked_count > 0 && <span className="badge badge--liked">{c.liked_count} liked</span>}
                <span className="card__score">{c.count}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {creators.length < total && (
        <div className="loadmore">
          <button className="btn" disabled={loading} onClick={() => load(offset + PAGE, true)}>
            {loading ? "Loading…" : `Load more — ${creators.length} of ${total.toLocaleString()}`}
          </button>
        </div>
      )}
    </>
  );
}
