import { useMemo, useState } from "react";
import { api } from "../api";
import type { AskResponse, Facets, Item } from "../types";
import { cx } from "../util";

export function AskPanel({
  facets,
  onOpen,
}: {
  facets: Facets | null;
  onOpen: (it: Item) => void;
}) {
  const [q, setQ] = useState("");
  const [source, setSource] = useState<"saved" | "liked" | "both">("both");
  const [res, setRes] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const suggestions = useMemo(() => {
    const names = (facets?.clusters ?? [])
      .filter((c) => c.cluster_id >= 0 && !/misc|fyp|explore|viral/i.test(c.name))
      .slice(0, 4)
      .map((c) => `What have I saved about ${c.name.split(" / ")[0].toLowerCase()}?`);
    return names.length ? names : ["What have I saved about recipes?", "What do I keep meaning to try?"];
  }, [facets]);

  const run = async (question: string) => {
    if (!question.trim()) return;
    setQ(question);
    setLoading(true);
    setErr("");
    try {
      setRes(await api.ask(question.trim(), source));
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  };

  const mix = res
    ? res.citations.reduce(
        (a, c) => ((a[c.source] = (a[c.source] ?? 0) + 1), a),
        {} as Record<string, number>,
      )
    : null;

  return (
    <div className="ask">
      <div className="ask__intro">
        <h2>Ask your archive</h2>
        <p>
          A question in plain language. The answer is built only from your own saved and liked
          posts, cited back to each one.
        </p>
      </div>

      <form
        className="ask__form"
        onSubmit={(e) => {
          e.preventDefault();
          run(q);
        }}
      >
        <input
          className="field"
          placeholder="What have I saved about…?"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Question"
        />
        <select
          className="field"
          style={{ width: "auto" }}
          value={source}
          onChange={(e) => setSource(e.target.value as typeof source)}
        >
          <option value="both">Both</option>
          <option value="saved">Saved</option>
          <option value="liked">Liked</option>
        </select>
        <button className="btn btn--primary" disabled={loading}>
          {loading ? "…" : "Ask"}
        </button>
      </form>

      {!res && !loading && (
        <div className="ask__suggest">
          {suggestions.map((s) => (
            <button key={s} className="chip" onClick={() => run(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {err && <div className="err">{err}</div>}

      {res && (
        <>
          <div className="ask__answer">{res.answer}</div>
          <div className="ask__meta">
            {res.used_llm
              ? mix
                ? `answered from ${Object.entries(mix)
                    .map(([k, v]) => `${v} ${k}`)
                    .join(" + ")} items`
                : null
              : "synthesis is off — set LLM_PROVIDER=anthropic for a written answer"}
          </div>
          <div className="ask__cites">
            {res.citations.map((c, i) => (
              <button
                key={c.id}
                className="cite"
                onClick={async () => {
                  try {
                    onOpen(await api.item(c.id));
                  } catch {
                    /* ignore */
                  }
                }}
              >
                <span className="cite__i">[{i + 1}]</span>
                <span className="cite__body">
                  <b>@{c.creator}</b>{" "}
                  <span className={`badge badge--${c.source}`} style={{ margin: "0 4px" }} />
                  {c.summary}
                </span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
