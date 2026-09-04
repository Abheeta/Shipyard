import { useEffect, useState } from "react";
import { api } from "../api";
import type { Facets, Item } from "../types";
import { ItemCard } from "./ItemCard";

const todayISO = () => new Date().toISOString().slice(0, 10);

export function TodayView({
  onOpen,
  facets,
}: {
  onOpen: (it: Item) => void;
  facets: Facets | null;
}) {
  const [items, setItems] = useState<Item[]>([]);
  const [buried, setBuried] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .today()
      .then((r) => setItems(r.items))
      .finally(() => setLoading(false));
    api
      .search({ source: "saved", sort: "oldest", status: "saved", limit: 6 })
      .then((r) => setBuried(r.items))
      .catch(() => setBuried([]));
  }, []);

  const t = todayISO();
  const overdue = items.filter((i) => (i.state.scheduled_at ?? "") < t);
  const due = items.filter((i) => (i.state.scheduled_at ?? "") >= t);

  if (loading) return <div className="spinner">Loading…</div>;

  if (!items.length) {
    const oldest = facets?.backlog?.oldest_item_date as string | undefined;
    const months = facets?.backlog?.oldest_item_age_days
      ? Math.floor(Number(facets.backlog.oldest_item_age_days) / 30)
      : null;
    return (
      <>
        <div className="empty">
          <div className="empty__title">Nothing scheduled — and that's the backlog</div>
          <p className="empty__body">
            You've saved {facets?.saved_count ?? "—"} things and resolved none of them. The oldest
            has been waiting since {oldest ?? "over a year ago"}
            {months ? ` — ${months} months` : ""}. Open one, give it a date, and it shows up here.
          </p>
        </div>
        {buried.length > 0 && (
          <div className="today-section" style={{ marginTop: 24 }}>
            <div className="today-section__head">
              <h2>Been sitting longest</h2>
              <span className="mono">oldest unresolved saves</span>
            </div>
            <div className="grid">
              {buried.map((it) => (
                <ItemCard key={it.id} item={it} onOpen={() => onOpen(it)} emphasiseNote />
              ))}
            </div>
          </div>
        )}
      </>
    );
  }

  return (
    <>
      {overdue.length > 0 && (
        <div className="today-section">
          <div className="today-section__head is-overdue">
            <h2>Overdue</h2>
            <span className="mono">{overdue.length}</span>
          </div>
          <div className="grid">
            {overdue.map((it) => (
              <ItemCard key={it.id} item={it} onOpen={() => onOpen(it)} emphasiseNote />
            ))}
          </div>
        </div>
      )}
      {due.length > 0 && (
        <div className="today-section">
          <div className="today-section__head">
            <h2>Today</h2>
            <span className="mono">{due.length}</span>
          </div>
          <div className="grid">
            {due.map((it) => (
              <ItemCard key={it.id} item={it} onOpen={() => onOpen(it)} emphasiseNote />
            ))}
          </div>
        </div>
      )}
    </>
  );
}
