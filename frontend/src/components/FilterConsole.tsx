import { useEffect, useState } from "react";
import type { Facets, Query } from "../types";
import { cx } from "../util";

const TIME: [string, string][] = [
  ["", "All time"],
  ["this_year", "This year"],
  ["last_year", "Last year"],
  ["older", "Older"],
];
const KIND: [NonNullable<Query["actionable"]>, string][] = [
  ["all", "Everything"],
  ["actionable", "To do"],
  ["info", "To know"],
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

  useEffect(() => setText(query.q ?? ""), [query.q]);
  const set = (patch: Partial<Query>) => onChange({ ...query, ...patch });

  const creators =
    query.source === "saved"
      ? facets?.top_creators_saved
      : query.source === "liked"
        ? facets?.top_creators_liked
        : facets?.top_creators_combined;

  const topics = (facets?.clusters ?? []).filter((c) => c.cluster_id >= 0).slice(0, 30);

  return (
    <section className="console" aria-label="Filters">
      <form
        className="console__search"
        onSubmit={(e) => {
          e.preventDefault();
          set({ q: text.trim() || undefined });
        }}
      >
        <input
          className="field"
          placeholder="Search your archive — a topic, a phrase, a creator…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          aria-label="Search"
        />
        <button className="btn btn--primary" type="submit">
          Search
        </button>
        {query.q && (
          <button type="button" className="btn" onClick={() => set({ q: undefined })}>
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

      <div className="console__row">
        <span className="eyebrow">Source</span>
        <Seg options={SOURCE} value={query.source ?? "both"} onPick={(v) => set({ source: v, creator: undefined })} />
        <span className="eyebrow" style={{ marginLeft: 6 }}>
          When
        </span>
        <Seg options={TIME} value={query.time_preset ?? ""} onPick={(v) => set({ time_preset: v || undefined })} />
      </div>

      <div className="console__row">
        <span className="eyebrow">Kind</span>
        <Seg options={KIND} value={query.actionable ?? "all"} onPick={(v) => set({ actionable: v })} />
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

      {topics.length > 0 && (
        <div className="console__facets">
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

          {creators && creators.length > 0 && (
            <div className="facet-line">
              <span className="eyebrow">Creator</span>
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
        </div>
      )}
    </section>
  );
}
