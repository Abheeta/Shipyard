import type {
  AskResponse,
  CreatorRankResponse,
  Facets,
  Item,
  Query,
  SearchResponse,
  Status,
  Intent,
} from "./types";

// Empty in local dev (vite proxies /api). Set VITE_API_BASE_URL when the
// frontend is deployed separately from the backend.
const BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

function qs(query: Query): string {
  const p = new URLSearchParams();
  Object.entries(query).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    if (Array.isArray(v)) {
      v.forEach((item) => p.append(k, String(item)));
    } else {
      p.set(k, String(v));
    }
  });
  return p.toString();
}

export const api = {
  facets: () => j<Facets>("/api/facets"),
  search: (query: Query) => j<SearchResponse>(`/api/search?${qs(query)}`),
  item: (id: string) => j<Item>(`/api/items/${encodeURIComponent(id)}`),
  similar: (id: string) =>
    j<SearchResponse>(`/api/items/${encodeURIComponent(id)}/similar`),
  creators: (
    query: Pick<
      Query,
      "q" | "source" | "time_preset" | "cluster_id" | "tags" | "include_ads" | "actionable" | "status" | "intent"
    > & { offset?: number; limit?: number },
  ) => j<CreatorRankResponse>(`/api/creators?${qs(query as Query)}`),
  patch: (
    id: string,
    body: {
      user_note?: string | null;
      user_intent?: Intent | null;
      scheduled_at?: string | null;
      status?: Status;
      promote_to_saved?: boolean;
    },
  ) =>
    j<Item>(`/api/items/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  ask: (question: string, source: "saved" | "liked" | "both", k = 10) =>
    j<AskResponse>("/api/ask", {
      method: "POST",
      body: JSON.stringify({ question, source, k }),
    }),
};
