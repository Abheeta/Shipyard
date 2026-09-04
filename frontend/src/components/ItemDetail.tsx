import { useEffect, useState } from "react";
import { api } from "../api";
import type { Intent, Item } from "../types";
import { cx, relTime } from "../util";

const INTENTS: [Intent, string][] = [
  ["try", "Try it"],
  ["learn", "Learn"],
  ["do_later", "Do later"],
  ["remember", "Remember"],
];

export function ItemDetail({
  item,
  onClose,
  onUpdated,
  onOpen,
}: {
  item: Item;
  onClose: () => void;
  onUpdated: (it: Item) => void;
  onOpen: (it: Item) => void;
}) {
  const [note, setNote] = useState(item.state.user_note ?? "");
  const [intent, setIntent] = useState<Intent | "">(item.state.user_intent ?? "");
  const [date, setDate] = useState(item.state.scheduled_at ?? "");
  const [similar, setSimilar] = useState<Item[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setNote(item.state.user_note ?? "");
    setIntent(item.state.user_intent ?? "");
    setDate(item.state.scheduled_at ?? "");
    api
      .similar(item.id)
      .then((r) => setSimilar(r.items.filter((s) => s.id !== item.id).slice(0, 6)))
      .catch(() => setSimilar([]));
  }, [item.id, item.state.user_note, item.state.user_intent, item.state.scheduled_at]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const inLoop =
    item.source === "saved" || item.state.status !== "saved" || !!item.state.scheduled_at;

  const save = async (extra?: Parameters<typeof api.patch>[1]) => {
    setBusy(true);
    try {
      onUpdated(
        await api.patch(item.id, {
          user_note: note || null,
          user_intent: intent || null,
          scheduled_at: date || null,
          ...extra,
        }),
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="overlay" onMouseDown={onClose}>
      <aside className="panel" onMouseDown={(e) => e.stopPropagation()} aria-label="Item detail">
        <button className="btn btn--ghost btn--sm panel__close" onClick={onClose}>
          Close ✕
        </button>

        <div className="panel__head">
          <h2>@{item.creator || "unknown"}</h2>
          <div className="panel__sub">
            {item.creator_name && item.creator_name !== item.creator ? `${item.creator_name} · ` : ""}
            you saved this {relTime(item.timestamp)} ·{" "}
            <a href={item.url} target="_blank" rel="noreferrer">
              open on Instagram ↗
            </a>
          </div>
        </div>

        <div className="panel__badges">
          <span className={`badge badge--${item.source}`}>{item.source}</span>
          {item.cluster_name && <span className="badge badge--info">{item.cluster_name}</span>}
          <span className="badge badge--info">{item.is_actionable ? "to do" : "to know"}</span>
          {item.is_ad && <span className="badge badge--ad">sponsored</span>}
        </div>

        {item.summary && <div className="panel__summary">{item.summary}</div>}

        <div className={cx("well", !item.caption && "well--raw")}>
          {item.caption || "No caption in the export — nothing to summarise."}
        </div>

        {item.tags.length > 0 && (
          <div className="card__tags">
            {item.tags.map((t) => (
              <span className="tag" key={t}>
                #{t}
              </span>
            ))}
          </div>
        )}

        {inLoop ? (
          <>
            <div className="panel__section">
              <span className="eyebrow">Note — why keep this</span>
              <textarea
                className="field"
                rows={2}
                placeholder="e.g. try the loose-gauge version this weekend"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
            </div>

            <div className="panel__section">
              <span className="eyebrow">Intent</span>
              <div className="control-row">
                {INTENTS.map(([v, label]) => (
                  <button
                    key={v}
                    className={cx("btn", "btn--sm", intent === v && "is-active")}
                    onClick={() => setIntent(intent === v ? "" : v)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="panel__section">
              <span className="eyebrow">Schedule</span>
              <div className="control-row">
                <input
                  type="date"
                  className="field"
                  style={{ width: "auto" }}
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
                {date && (
                  <button className="btn btn--sm" onClick={() => setDate("")}>
                    clear
                  </button>
                )}
              </div>
            </div>

            <div className="control-row">
              <button className="btn btn--primary" disabled={busy} onClick={() => save()}>
                Save changes
              </button>
              {item.state.status !== "resolved" ? (
                <button className="btn" disabled={busy} onClick={() => save({ status: "resolved" })}>
                  ✓ Mark resolved
                </button>
              ) : (
                <button
                  className="btn"
                  disabled={busy}
                  onClick={() => save({ status: date ? "scheduled" : "saved" })}
                >
                  Reopen
                </button>
              )}
            </div>
          </>
        ) : (
          <div className="panel__section">
            <p className="promote-note">
              A <b>liked</b> post — passive interest. Promote it into the loop to add a note,
              intent and a date.
            </p>
            <button
              className="btn btn--primary"
              disabled={busy}
              onClick={() => save({ promote_to_saved: true })}
            >
              + Pull into the loop
            </button>
          </div>
        )}

        <div className="panel__section">
          <span className="eyebrow">Original metadata</span>
          <dl className="meta-list">
            <dt>saved</dt>
            <dd>{item.saved_date ?? "—"}</dd>
            <dt>source</dt>
            <dd>{item.source}</dd>
            {item.hashtags.length > 0 && (
              <>
                <dt>hashtags</dt>
                <dd style={{ color: "var(--ink-faint)" }}>{item.hashtags.map((h) => `#${h}`).join(" ")}</dd>
              </>
            )}
          </dl>
        </div>

        {similar.length > 0 && (
          <div className="panel__section">
            <span className="eyebrow">More like this</span>
            {similar.map((s) => (
              <button key={s.id} className="mini-item" onClick={() => onOpen(s)}>
                <span className={`badge badge--${s.source}`} />
                <span>
                  @{s.creator} — {s.summary || s.caption.slice(0, 80) || "no caption"}
                </span>
              </button>
            ))}
          </div>
        )}
      </aside>
    </div>
  );
}
