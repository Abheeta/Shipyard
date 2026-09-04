import { useEffect, useState } from "react";
import { api } from "../api";
import type { CreatorRank, Facets, Intent, Query } from "../types";
import { cx } from "../util";

const TIME: [string, string][] = [
  ["", "All time"],
  ["this_year", "This year"],
  ["last_year", "Last year"],
  ["older", "Older"],
];
const INTENT: [Intent | "", string][] = [
  ["", "All"],
  ["try", "Try it"],
  ["do_later", "Do later"],
  ["learn", "Learn"],
  ["remember", "Remember"],
];
const STATUS: NonNullable<Query["status"]>[] = ["saved", "scheduled", "resolved"];
const SOURCE: [NonNullable<Query["source"]>, string][] = [
  ["both", "Both"],
  ["saved", "Saved"],
  ["liked", "Liked"],
];

function Seg<T extends string>({
  options,
  value,
  onPick,
}: {
  options: [T, string][];
  value: T;
  onPick: (v: T) => void;
}) {
  return (
    <div className="seg">
      {options.map(([v, label]) => (
        <button key={v} className={cx(value === v && "is-active")} onClick={() => onPick(v)}>
          {label}
        </button>
      ))}
    </div>
  );
}

export function FilterConsole({
  facets,
  query,
  onChange,
}: {
  facets: Facets | null;
  query: Query;
  onChange: (q: Query) => void;
}) {
  const [text, setText] = useState(query.q ?? "");
  const [topicsOpen, setTopicsOpen] = useState(false);
  const [creatorsOpen, setCreatorsOpen] = useState(false);
  const [tagsOpen, setTagsOpen] = useState(false);
  const [rankedCreators, setRankedCreators] = useState<CreatorRank[] | null>(null);

  useEffect(() => setText(query.q ?? ""), [query.q]);
  const set = (patch: Partial<Query>) => onChange({ ...query, ...patch });

  const discovering = query.cluster_id != null || (query.tags?.length ?? 0) > 0;

  // Re-rank the creator chip list to "who posts about this" whenever the
  // topic/tag/source selection changes — a topic or tag alone is enough
  // signal to discover by, so this only depends on the filters that shape
  // *which* creators are relevant, not free-text search or pagination.
  useEffect(() => {
    let cancelled = false;
    const t = setTimeout(() => {
      api
        .creators({
          source: query.source,
          cluster_id: query.cluster_id,
          tags: query.tags,
          time_preset: query.time_preset,
          actionable: query.actionable,
          status: query.status,
          intent: query.intent,
        })
        .then((r) => !cancelled && setRankedCreators(r.creators))
        .catch(() => !cancelled && setRankedCreators(null));
    }, 200);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [
    query.source,
    query.cluster_id,
    JSON.stringify(query.tags),
    query.time_preset,
    query.actionable,
    query.status,
    query.intent,
  ]);

  const activeTags = query.tags ?? [];
  const toggleTag = (tag: string) => {
    const next = activeTags.includes(tag) ? activeTags.filter((t) => t !== tag) : [...activeTags, tag];
    set({ tags: next.length ? next : undefined });
  };

  const submitSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const raw = text.trim();
    const hashtagTokens = Array.from(raw.matchAll(/#([a-z0-9_]+)/gi)).map((m) => m[1].toLowerCase());
    const rest = raw.replace(/#[a-z0-9_]+/gi, "").replace(/\s+/g, " ").trim();
    if (hashtagTokens.length) {
      const merged = Array.from(new Set([...activeTags, ...hashtagTokens]));
      set({ q: rest || undefined, tags: merged });
    } else {
      set({ q: rest || undefined });
    }
  };

  const staticCreators =
    query.source === "saved"
      ? facets?.top_creators_saved
      : query.source === "liked"
        ? facets?.top_creators_liked
        : facets?.top_creators_combined;
  // While the topic/tag-ranked fetch is in flight (or before the first
  // topic/tag pick), fall back to the static global list so the chip row
  // never flashes empty.
  const creators = rankedCreators ?? staticCreators;

  const topics = (facets?.clusters ?? []).filter((c) => c.cluster_id >= 0).slice(0, 30);
  const tags = facets?.top_tags ?? [];

  return (
    <section className="console" aria-label="Filters">
      <form className="console__search" onSubmit={submitSearch}>
        <input
          className="field"
          placeholder="Search your archive — a topic, a phrase, a creator, or #a-tag…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          aria-label="Search"
        />
        <button className="btn btn--primary" type="submit">
          Search
        </button>
        {(query.q || activeTags.length > 0) && (
          <button
            type="button"
            className="btn"
            onClick={() => set({ q: undefined, tags: undefined })}
          >
            Clear
          </button>
        )}
        <select
          className="field"
          style={{ width: "auto" }}
          value={query.sort ?? "relevance"}
          onChange={(e) => set({ sort: e.target.value as Query["sort"] })}
          aria-label="Sort"
        >
          <option value="relevance">Relevance</option>
          <option value="recent">Newest</option>
          <option value="oldest">Oldest</option>
        </select>
      </form>

      {activeTags.length > 0 && (
        <div className="console__row console__row--tags">
          <span className="eyebrow">Tags</span>
          {activeTags.map((t) => (
            <button key={t} className="chip is-active" onClick={() => toggleTag(t)}>
              #{t}
              <span className="chip__x">✕</span>
            </button>
          ))}
        </div>
      )}

      <div className="console__row">
        <span className="eyebrow">Source</span>
        <Seg options={SOURCE} value={query.source ?? "both"} onPick={(v) => set({ source: v, creator: undefined })} />
        <span className="eyebrow" style={{ marginLeft: 6 }}>
          When
        </span>
        <Seg options={TIME} value={query.time_preset ?? ""} onPick={(v) => set({ time_preset: v || undefined })} />
      </div>

      <div className="console__row">
        <span className="eyebrow">Intent</span>
        <Seg options={INTENT} value={query.intent ?? ""} onPick={(v) => set({ intent: v || undefined })} />
        <button
          className={cx("btn", "btn--sm", query.include_ads === false && "is-active")}
          onClick={() => set({ include_ads: query.include_ads === false ? undefined : false })}
        >
          Hide sponsored
        </button>
        <span className="eyebrow" style={{ marginLeft: 6 }}>
          State
        </span>
        {STATUS.map((s) => (
          <button
            key={s}
            className={cx("btn", "btn--sm", query.status === s && "is-active")}
            onClick={() => set({ status: query.status === s ? undefined : s })}
          >
            {s}
          </button>
        ))}
      </div>

      {(topics.length > 0 || tags.length > 0) && (
        <div className="console__facets">
          {topics.length > 0 && (
            <div className="facet-line">
              <span className="eyebrow">Topic</span>
              <div className={cx("facet-line__chips", topicsOpen && "is-open")}>
                {topics.map((c) => (
                  <button
                    key={c.cluster_id}
                    className={cx("chip", query.cluster_id === c.cluster_id && "is-active")}
                    onClick={() =>
                      set({ cluster_id: query.cluster_id === c.cluster_id ? undefined : c.cluster_id })
                    }
                  >
                    {c.name}
                    <span className="chip__n">{c.size}</span>
                  </button>
                ))}
              </div>
              {topics.length > 8 && (
                <button className="btn btn--ghost btn--sm" onClick={() => setTopicsOpen((o) => !o)}>
                  {topicsOpen ? "less" : "all"}
                </button>
              )}
            </div>
          )}

          {creators && creators.length > 0 && (
            <div className="facet-line">
              <span className="eyebrow">{discovering ? "Creators for this" : "Creator"}</span>
              <div className={cx("facet-line__chips", creatorsOpen && "is-open")}>
                {creators.slice(0, 15).map((c) => (
                  <button
                    key={c.creator}
                    className={cx("chip", query.creator === c.creator && "is-active")}
                    onClick={() => set({ creator: query.creator === c.creator ? undefined : c.creator })}
                  >
                    @{c.creator}
                    <span className="chip__n">{c.count}</span>
                  </button>
                ))}
              </div>
              {creators.length > 8 && (
                <button className="btn btn--ghost btn--sm" onClick={() => setCreatorsOpen((o) => !o)}>
                  {creatorsOpen ? "less" : "all"}
                </button>
              )}
            </div>
          )}

          {tags.length > 0 && (
            <div className="facet-line">
              <span className="eyebrow">Tags</span>
              <div className={cx("facet-line__chips", tagsOpen && "is-open")}>
                {tags.slice(0, 40).map((t) => (
                  <button
                    key={t.tag}
                    className={cx("chip", activeTags.includes(t.tag) && "is-active")}
                    onClick={() => toggleTag(t.tag)}
                  >
                    #{t.tag}
                    <span className="chip__n">{t.count}</span>
                  </button>
                ))}
              </div>
              {tags.length > 8 && (
                <button className="btn btn--ghost btn--sm" onClick={() => setTagsOpen((o) => !o)}>
                  {tagsOpen ? "less" : "all"}
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
