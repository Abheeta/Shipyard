export type Source = "saved" | "liked";
export type Intent = "try" | "learn" | "do_later" | "remember";
export type Status = "saved" | "scheduled" | "resolved";

export interface ItemState {
  user_note: string | null;
  user_intent: Intent | null;
  scheduled_at: string | null;
  status: Status;
  resolved_at: string | null;
  updated_at: string | null;
}

export interface Item {
  id: string;
  source: Source;
  url: string;
  caption: string;
  title: string;
  creator: string;
  creator_name: string;
  timestamp: number;
  saved_date: string | null;
  year: number | null;
  hashtags: string[];
  summary: string;
  tags: string[];
  cluster_id: number;
  cluster_name: string;
  is_ad: boolean;
  is_actionable: boolean;
  state: ItemState;
  score: number | null;
}

export interface SearchResponse {
  total: number;
  offset: number;
  limit: number;
  items: Item[];
}

export interface Cluster {
  cluster_id: number;
  name: string;
  size: number;
}

export interface CreatorFacet {
  creator: string;
  creator_name: string;
  count: number;
}

export interface TagFacet {
  tag: string;
  count: number;
}

export interface Facets {
  total_items: number;
  saved_count: number;
  liked_count: number;
  unique_creators: number;
  unique_creators_saved: number;
  clusters: Cluster[];
  top_creators_saved: CreatorFacet[];
  top_creators_liked: CreatorFacet[];
  top_creators_combined: CreatorFacet[];
  top_tags: TagFacet[];
  like_save_gap: { creator: string; likes: number }[];
  year_counts: Record<string, number>;
  cluster_split: Record<string, { saved: number; liked: number }>;
  age_buckets: Record<string, number>;
  backlog: Record<string, unknown>;
  llm_enabled: boolean;
}

export interface AskCitation {
  id: string;
  creator: string;
  url: string;
  summary: string;
  source: Source;
}

export interface AskResponse {
  answer: string;
  citations: AskCitation[];
  used_llm: boolean;
}

export interface Query {
  q?: string;
  source?: "saved" | "liked" | "both";
  time_preset?: string;
  creator?: string;
  cluster_id?: number;
  tags?: string[];
  include_ads?: boolean;
  actionable?: "all" | "actionable" | "info";
  status?: Status;
  sort?: "relevance" | "recent" | "oldest";
  offset?: number;
  limit?: number;
}
