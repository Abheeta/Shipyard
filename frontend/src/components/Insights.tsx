import type { Facets } from "../types";
import { cx } from "../util";

type Row = { key: string | number; label: string; value: number; parts?: { v: number; cls: string }[] };

function Bars({
  rows,
  onPick,
  max,
}: {
  rows: Row[];
  onPick?: (key: string | number) => void;
  max?: number;
}) {
  const m = max ?? Math.max(1, ...rows.map((r) => r.value));
  return (
    <div className="bars">
      {rows.map((r) => (
        <div className="bar" key={r.key}>
          <span
            className={cx("bar__label", onPick && "is-clickable")}
            onClick={() => onPick?.(r.key)}
            title={r.label}
          >
            {r.label}
          </span>
          <span className="bar__track">
            {(r.parts ?? [{ v: r.value, cls: "" }]).map((p, i) => (
              <span
                key={i}
                className={cx("bar__fill", p.cls && `bar__fill--${p.cls}`)}
                style={{ width: `${(p.v / m) * 100}%`, background: p.cls ? undefined : "var(--accent)" }}
              />
            ))}
          </span>
          <span className="bar__n">{r.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}

export function Insights({
  facets,
  onCluster,
  onCreator,
}: {
  facets: Facets | null;
  onCluster: (id: number) => void;
  onCreator: (creator: string) => void;
}) {
  if (!facets) return <div className="spinner">Loading…</div>;
  const b = facets.backlog;
  const months = b.oldest_item_age_days ? Math.floor(Number(b.oldest_item_age_days) / 30) : null;
  const dup = Number(b.near_duplicate_item_count ?? 0);
  const actionablePct = Math.round(Number(b.actionable_share ?? 0) * 100);
  const substantivePct = Math.round(Number(b.substantive_caption_share ?? 0) * 100);
  const adPct = Math.round(Number(b.ad_share ?? 0) * 1000) / 10;
  const resolved = (b.state_counts as Record<string, number>)?.resolved ?? 0;

  const topClusters = facets.clusters.filter((c) => c.cluster_id >= 0).slice(0, 12);
  const splitRows: Row[] = topClusters.map((c) => {
    const s = facets.cluster_split[String(c.cluster_id)] ?? { saved: 0, liked: c.size };
    return {
      key: c.cluster_id,
      label: c.name,
      value: c.size,
      parts: [
        { v: s.saved, cls: "saved" },
        { v: s.liked, cls: "liked" },
      ],
    };
  });

  const ratioRows: Row[] = topClusters
    .map((c) => {
      const s = facets.cluster_split[String(c.cluster_id)] ?? { saved: 0, liked: c.size };
      return { c, ratio: s.saved / Math.max(1, s.saved + s.liked), s };
    })
    .sort((a, z) => z.ratio - a.ratio)
    .slice(0, 10)
    .map(({ c, ratio }) => ({
      key: c.cluster_id,
      label: c.name,
      value: Math.round(ratio * 100),
    }));

  const yearRows: Row[] = Object.entries(facets.year_counts).map(([y, n]) => ({
    key: y,
    label: y,
    value: n,
  }));
  const ageRows: Row[] = Object.entries(facets.age_buckets).map(([k, n]) => ({
    key: k,
    label: k,
    value: n,
  }));
  const gapRows: Row[] = facets.like_save_gap.map((g) => ({
    key: g.creator,
    label: `@${g.creator}`,
    value: g.likes,
  }));

  return (
    <>
      <div className="tiles">
        {[
          [facets.total_items.toLocaleString(), "items in the archive"],
          [facets.saved_count.toLocaleString(), "saved with intent"],
          [facets.liked_count.toLocaleString(), "liked (passive)"],
          [facets.unique_creators.toLocaleString(), "different creators"],
          [months ? `${months} mo` : "—", "oldest unresolved save"],
          [`${resolved}`, "resolved so far"],
        ].map(([n, k]) => (
          <div className="tile" key={k}>
            <div className="tile__n">{n}</div>
            <div className="tile__k">{k}</div>
          </div>
        ))}
      </div>

      <div className="insights">
        <div className="insight">
          <div className="insight__title">Backlog decay</div>
          <div className="insight__hero">
            {months ?? "—"} <small>months</small>
          </div>
          <p className="insight__note">
            Your oldest unresolved save is from {String(b.oldest_item_date ?? "over a year ago")}. Saves
            don't rot loudly — they just sit.
          </p>
          <div style={{ marginTop: 14 }}>
            <Bars rows={ageRows} />
          </div>
        </div>

        <div className="insight">
          <div className="insight__title">Near-duplicate saves</div>
          <div className="insight__hero">{dup.toLocaleString()}</div>
          <p className="insight__note">
            Items that are near-copies of something else you saved. Each one looked worth keeping in
            the moment; together they're an unanswered question.
          </p>
        </div>

        <div className="insight">
          <div className="insight__title">To do vs. to know</div>
          <div className="insight__hero">
            {actionablePct}
            <small>% actionable</small>
          </div>
          <p className="insight__note">
            The rest is stuff to know, not do — "resolve" only really applies to the {actionablePct}%.
          </p>
        </div>

        <div className="insight">
          <div className="insight__title">Caption coverage</div>
          <div className="insight__hero">
            {substantivePct}
            <small>% substantive</small>
          </div>
          <p className="insight__note">
            Extraction quality is capped by the caption — {100 - substantivePct}% of items are too thin
            to summarise well. {adPct}% look sponsored.
          </p>
        </div>

        <div className="insight insight--wide">
          <div className="insight__title">What you actually save about — click a topic to filter</div>
          <Bars rows={splitRows} onPick={(k) => onCluster(Number(k))} />
          <div className="legend">
            <span>
              <i style={{ background: "var(--saved)" }} /> saved
            </span>
            <span>
              <i style={{ background: "var(--liked)" }} /> liked
            </span>
          </div>
        </div>

        <div className="insight">
          <div className="insight__title">Highest-intent topics (save rate)</div>
          <Bars rows={ratioRows} onPick={(k) => onCluster(Number(k))} max={100} />
          <p className="insight__note">
            % of engagement you actually saved, per topic. High = you act on it; low = you scroll past
            and forget.
          </p>
        </div>

        <div className="insight">
          <div className="insight__title">Watch, never save</div>
          {gapRows.length ? (
            <Bars rows={gapRows} onPick={(k) => onCreator(String(k))} />
          ) : (
            <p className="insight__note">No creator you've liked 5+ times is unsaved.</p>
          )}
          <p className="insight__note">
            Creators you've liked repeatedly and never saved from — attention that never became
            intent.
          </p>
        </div>

        <div className="insight">
          <div className="insight__title">By year saved</div>
          <Bars rows={yearRows} />
        </div>

        <div className="insight">
          <div className="insight__title">Top saved creators — click to filter</div>
          <Bars
            rows={facets.top_creators_saved.slice(0, 12).map((c) => ({
              key: c.creator,
              label: `@${c.creator}`,
              value: c.count,
            }))}
            onPick={(k) => onCreator(String(k))}
          />
        </div>

        <div className="insight">
          <div className="insight__title">Top liked creators</div>
          <Bars
            rows={facets.top_creators_liked.slice(0, 12).map((c) => ({
              key: c.creator,
              label: `@${c.creator}`,
              value: c.count,
            }))}
            onPick={(k) => onCreator(String(k))}
          />
          <p className="insight__note">
            {facets.liked_count.toLocaleString()} likes across {facets.unique_creators.toLocaleString()}{" "}
            creators — you don't have favourites, you have a feed.
          </p>
        </div>
      </div>
    </>
  );
}
