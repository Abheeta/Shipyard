import type { Item } from "../types";
import { cx, relTime } from "../util";

export function ItemCard({
  item,
  onOpen,
  emphasiseNote = false,
}: {
  item: Item;
  onOpen: () => void;
  emphasiseNote?: boolean;
}) {
  const st = item.state.status;
  const note = item.state.user_note;
  const headline = emphasiseNote && note ? note : item.summary;
  const emptyHeadline = !headline;

  return (
    <button className={cx("card", st === "resolved" && "card--resolved")} onClick={onOpen}>
      <div className="card__top">
        <span className="card__creator">@{item.creator || "unknown"}</span>
        <span className="card__age">{relTime(item.timestamp)}</span>
      </div>

      <div className={cx("card__summary", emptyHeadline && "is-empty")}>
        {headline || "no caption — browse by creator or topic"}
      </div>

      {!emphasiseNote && item.tags.length > 0 && (
        <div className="card__tags">
          {item.tags.slice(0, 4).map((t) => (
            <span className="tag" key={t}>
              #{t}
            </span>
          ))}
        </div>
      )}

      <div className="card__foot">
        <span className={`badge badge--${item.source}`}>{item.source}</span>
        {item.cluster_name && <span className="card__topic">{item.cluster_name}</span>}
        {item.is_ad && <span className="badge badge--ad">ad</span>}
        {!item.is_actionable && <span className="badge badge--info">to know</span>}
        {st === "scheduled" && item.state.scheduled_at && (
          <span className="badge badge--scheduled">{item.state.scheduled_at}</span>
        )}
        {st === "resolved" && <span className="badge badge--done">done</span>}
        {item.score != null && <span className="card__score">{item.score.toFixed(2)}</span>}
      </div>
    </button>
  );
}
