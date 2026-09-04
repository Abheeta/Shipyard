import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import type { Facets, Item, Query } from "./types";
import { applyTheme, cx, prefersDark, readTheme, type Theme } from "./util";
import { FilterConsole } from "./components/FilterConsole";
import { ItemCard } from "./components/ItemCard";
import { ItemDetail } from "./components/ItemDetail";
import { TodayView } from "./components/TodayView";
import { AskPanel } from "./components/AskPanel";
import { Insights } from "./components/Insights";

type View = "library" | "today" | "ask" | "insights";
const PAGE = 40;
const TABS: [View, string][] = [
  ["library", "Library"],
  ["today", "Today"],
  ["ask", "Ask"],
  ["insights", "Insights"],
];

export function App() {
  const [view, setView] = useState<View>("library");
  const [theme, setTheme] = useState<Theme>(readTheme);
  const [facets, setFacets] = useState<Facets | null>(null);
  const [query, setQuery] = useState<Query>({ source: "both", sort: "relevance" });
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<Item | null>(null);

  useEffect(() => applyTheme(theme), [theme]);
  useEffect(() => {
    api.facets().then(setFacets).catch(console.error);
  }, []);

  const load = useCallback(async (q: Query, nextOffset: number, append: boolean) => {
    setLoading(true);
    try {
      const res = await api.search({ ...q, offset: nextOffset, limit: PAGE });
      setTotal(res.total);
      setOffset(nextOffset);
      setItems((prev) => (append ? [...prev, ...res.items] : res.items));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (view === "library") load(query, 0, false);
  }, [query, view, load]);

  const refreshItem = useCallback((updated: Item) => {
    setItems((prev) => prev.map((it) => (it.id === updated.id ? updated : it)));
    setSelected((s) => (s && s.id === updated.id ? updated : s));
  }, []);

  const openItem = useCallback(async (item: Item) => {
    setSelected(item);
    try {
      setSelected(await api.item(item.id));
    } catch (e) {
      console.error(e);
    }
  }, []);

  const nextTheme = () =>
    setTheme((t) => (t === "system" ? (prefersDark() ? "light" : "dark") : t === "dark" ? "light" : "dark"));

  return (
    <div className="shell">
      <header className="topbar">
        <span className="wordmark">
          SHIP<b>·</b>YARD
        </span>
        <nav className="nav">
          {TABS.map(([v, label]) => (
            <button key={v} className={cx(view === v && "is-active")} onClick={() => setView(v)}>
              {label}
              {v === "today" && facets && <span className="n" />}
            </button>
          ))}
        </nav>
        <div className="corpus-readout">
          {facets && (
            <>
              <span>{facets.total_items.toLocaleString()} items</span>
              <span>·</span>
              <span style={{ color: "var(--saved)" }}>{facets.saved_count} saved</span>
              <span>·</span>
              <span style={{ color: "var(--liked)" }}>{facets.liked_count.toLocaleString()} liked</span>
              {!facets.llm_enabled && <span className="off">heuristic mode</span>}
            </>
          )}
          <button className="theme-toggle" onClick={nextTheme} title="Toggle theme" aria-label="Toggle theme">
            ◐
          </button>
        </div>
      </header>

      <main className="main">
        {view === "library" && (
          <>
            <FilterConsole facets={facets} query={query} onChange={setQuery} />
            <div className="result-count">
              <strong>{loading && !items.length ? "…" : total.toLocaleString()}</strong>
              <span>
                {query.q ? `results for “${query.q}”` : "items"}
                {query.cluster_id != null && facets
                  ? ` · ${facets.clusters.find((c) => c.cluster_id === query.cluster_id)?.name ?? "topic"}`
                  : ""}
                {query.creator ? ` · @${query.creator}` : ""}
              </span>
            </div>
            {!loading && !items.length ? (
              <div className="empty">
                <div className="empty__title">Nothing matches</div>
                <p className="empty__body">Loosen a filter or clear the search.</p>
              </div>
            ) : (
              <div className="grid">
                {items.map((it) => (
                  <ItemCard key={it.id} item={it} onOpen={() => openItem(it)} />
                ))}
              </div>
            )}
            {items.length < total && (
              <div className="loadmore">
                <button className="btn" disabled={loading} onClick={() => load(query, offset + PAGE, true)}>
                  {loading ? "Loading…" : `Load more — ${items.length} of ${total.toLocaleString()}`}
                </button>
              </div>
            )}
          </>
        )}

        {view === "today" && <TodayView onOpen={openItem} facets={facets} />}
        {view === "ask" && <AskPanel facets={facets} onOpen={openItem} />}
        {view === "insights" && (
          <Insights
            facets={facets}
            onCluster={(cluster_id) => {
              setQuery({ source: "both", sort: "relevance", cluster_id });
              setView("library");
            }}
            onCreator={(creator) => {
              setQuery({ source: "both", sort: "relevance", creator });
              setView("library");
            }}
          />
        )}
      </main>

      {selected && (
        <ItemDetail item={selected} onClose={() => setSelected(null)} onUpdated={refreshItem} onOpen={openItem} />
      )}
    </div>
  );
}
