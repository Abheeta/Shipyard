"""LLM layer with a no-key fallback.

Two providers:
  * "none"      — pure-Python heuristics. Runs anywhere, zero cost, lower quality.
  * "anthropic" — Claude for enrichment + Q&A. Enabled when LLM_PROVIDER=anthropic
                  and ANTHROPIC_API_KEY is set.

Callers never branch on the provider — they call the module functions and get
the best answer the current configuration can produce.
"""
from __future__ import annotations

import json
import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from .config import settings

# sklearn's general-English list (articles, prepositions, pronouns — "her",
# "she", "they", "who"...) plus caption-specific filler that isn't in a
# standard stopword list but still isn't a topic ("video", "reel", "today",
# "im"/"i'm" contractions without the apostrophe once tokenized, etc.).
_STOPWORDS = set(ENGLISH_STOP_WORDS) | set(
    """don should now im get got make made how new video reel post today one
    two like really via cc just people time thing things""".split()
)

# Instagram/TikTok cross-posting boilerplate: high document-frequency across
# almost any personal export, so they never carry topical signal even though
# they look like content words. Filtered out of cluster names and keyword tags
# (but NOT out of full-text search/embeddings — a literal search for "fyp"
# should still work).
_SOCIAL_NOISE = set(
    """fyp fypp fypage foryou foryoupage explore explorepage viral viralvideo
    viralreels trending trend reels reel reelsinstagram reelitfeelit instagram
    instagood instadaily instalike tiktok video videos repost share shares
    comment comments follow followers following subscribe subscribers like
    likes linkinbio dm dmforcollab collab collaboration ad sponsored paid
    partnership presave preorder linkinbio bio credit creditcc cc via
    duet stitch capcut""".split()
)

_ACTIONABLE_HINTS = (
    "how to", "tutorial", "recipe", "pattern", "diy", "step by step", "steps",
    "workout", "routine", "guide", "tips", "technique", "instructions", "make",
    "try this", "learn", "exercise", "stretch", "drill", "practice",
)
_INFO_HINTS = (
    "breaking", "news", "opinion", "commentary", "reminder that", "did you know",
    "fun fact", "history of", "explained", "thread on", "hot take",
)


# ─────────────────────────── heuristic helpers ───────────────────────────

def _first_sentence(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""
    m = re.split(r"(?<=[.!?])\s", text, maxsplit=1)
    s = m[0]
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # symbols/pictographs/emoticons/transport/supplemental
    "\U00002600-\U000027BF"  # misc symbols & dingbats
    "\U0001F1E6-\U0001F1FF"  # regional indicators (flags)
    "\U00002190-\U000021FF"  # arrows
    "\U0000FE0F"  # variation selector
    "]+",
    flags=re.UNICODE,
)


def _is_garbled(text: str) -> bool:
    """Some exports double-mangle a caption so badly that even the mojibake
    repair in ingest.py can't recover it (leftover Latin-1-supplement soup
    like "ð¤¦ð»ââï¸"). Detect and reject that rather than show gibberish."""
    if not text:
        return False
    suspect = sum(1 for c in text if 0x80 <= ord(c) <= 0xFF)
    return suspect / len(text) > 0.3


def _clean_caption(text: str, limit: int = 100) -> str:
    """A trimmed, readable lead-in from the caption itself: strip hashtags,
    @mentions, links, emoji and boilerplate noise, then take the first
    sentence/clause. Empty if nothing legible is left."""
    text = text or ""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"#\S+", "", text)
    text = re.sub(r"(?<!\w)@\w+", "", text)
    text = _EMOJI_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" \t\n-–—·•|.,:;")
    if not text or _is_garbled(text):
        return ""
    # cut at the first sentence end, or first newline/pipe-style separator
    m = re.split(r"(?<=[.!?])\s|(?:\s[-–—|]\s)", text, maxsplit=1)
    s = m[0].strip()
    if len(s) < 3 or _is_garbled(s):
        return ""
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def _dedupe_stems(words: list[str], n: int) -> list[str]:
    """Drop a candidate that's just a stem/plural/typo variant of one already
    kept (e.g. "beyonce" / "beyonc" / "beyhive" all collapsing to one entry)."""
    kept: list[str] = []
    for w in words:
        if any(w[:5] == k[:5] or w in k or k in w for k in kept):
            continue
        kept.append(w)
        if len(kept) >= n:
            break
    return kept


def _keywords(text: str, n: int = 5) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}", (text or "").lower())
    freq = Counter(w for w in words if w not in _STOPWORDS and w not in _SOCIAL_NOISE)
    ranked = [w for w, _ in freq.most_common(n * 3)]
    return _dedupe_stems(ranked, n)


def _heuristic_actionable(caption: str) -> bool:
    low = (caption or "").lower()
    if any(h in low for h in _ACTIONABLE_HINTS):
        return True
    if any(h in low for h in _INFO_HINTS):
        return False
    return True  # default: assume there's something to do


def _heuristic_summary(caption: str, tags: list[str]) -> str:
    """A short, clean one-liner for the card title: the caption's opening
    clause with hashtags/mentions/links/emoji/boilerplate stripped out — not
    the full caption (that's shown when the card is opened). Falls back to a
    topic-keyword label when the caption has nothing legible left over."""
    cleaned = _clean_caption(caption)
    if cleaned:
        return cleaned
    topic_words = tags[:3] or _keywords(caption, 3)
    if not topic_words:
        return ""
    return " · ".join(w.title() for w in topic_words)


def _heuristic_enrich_one(item: dict) -> dict:
    caption = item.get("caption") or ""
    hashtags = [t.lower() for t in (item.get("hashtags") or []) if t]
    tags = _dedupe_stems([t for t in hashtags if t not in _SOCIAL_NOISE], 5)
    if not tags:
        tags = _keywords(caption, 5)
    is_actionable = _heuristic_actionable(caption)
    summary = _heuristic_summary(caption, tags)
    if not summary:
        summary = f"Post by {item.get('creator_name') or item.get('creator') or 'unknown'} (no caption)"
    return {
        "summary": summary,
        "tags": tags,
        "is_actionable": is_actionable,
    }


def _heuristic_cluster_name(sample_captions: list[str]) -> str:
    blob = " ".join(sample_captions)
    kw = _keywords(blob, 4)
    return " / ".join(kw[:3]).title() if kw else "Misc"


# ─────────────────────────── anthropic client ───────────────────────────

def _client():
    from anthropic import Anthropic

    return Anthropic(api_key=settings.anthropic_api_key)


def _extract_json(text: str):
    m = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON in model output: {text[:200]}")
    return json.loads(m.group(0))


_ENRICH_SYS = (
    "You label saved social-media posts for a personal library. "
    "For each post you get an index, the caption text, and hashtags. "
    "Return ONLY a JSON array; one object per input in the same order, each: "
    '{"i": <index>, "summary": "<= 12 words, a plain description of what the post is ABOUT '
    "(topic/subject), not a paraphrase or quote of the caption text, no hype\", "
    '"tags": ["3-6 lowercase topic tags"], '
    '"is_actionable": <true if the post is something to DO/try/make/follow, '
    "false if it is just information to know>}. "
    "Never invent details the caption does not contain."
)


def _anthropic_enrich(items: list[dict]) -> list[dict]:
    client = _client()
    model = settings.enrich_model
    out: list[dict] = []
    BATCH = 12
    for start in range(0, len(items), BATCH):
        chunk = items[start : start + BATCH]
        payload = [
            {
                "i": start + j,
                "caption": (it.get("caption") or "")[:1200],
                "hashtags": (it.get("hashtags") or [])[:12],
            }
            for j, it in enumerate(chunk)
        ]
        msg = client.messages.create(
            model=model,
            max_tokens=2000,
            system=_ENRICH_SYS,
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        )
        text = "".join(b.text for b in msg.content if b.type == "text")
        try:
            parsed = _extract_json(text)
            by_i = {int(o["i"]): o for o in parsed}
        except Exception:
            by_i = {}
        for j, it in enumerate(chunk):
            o = by_i.get(start + j)
            if o:
                out.append(
                    {
                        "summary": str(o.get("summary") or "").strip()
                        or _first_sentence(it.get("caption") or ""),
                        "tags": [str(t).lower().strip() for t in (o.get("tags") or [])][:6]
                        or _keywords(it.get("caption") or "", 5),
                        "is_actionable": bool(o.get("is_actionable", True)),
                    }
                )
            else:
                out.append(_heuristic_enrich_one(it))
    return out


_CLUSTER_SYS = (
    "You name topic clusters for a personal saved-content library. "
    "Given a cluster id and sample captions, reply ONLY with JSON: "
    '{"name": "<2-5 word human label, Title Case>"}. Be specific and concrete.'
)


def _anthropic_name_cluster(cluster_id: int, sample_captions: list[str]) -> str:
    client = _client()
    body = "\n---\n".join(c[:400] for c in sample_captions[:10])
    msg = client.messages.create(
        model=settings.enrich_model,
        max_tokens=200,
        system=_CLUSTER_SYS,
        messages=[{"role": "user", "content": f"cluster {cluster_id}:\n{body}"}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    try:
        return str(_extract_json(text).get("name") or "").strip() or _heuristic_cluster_name(sample_captions)
    except Exception:
        return _heuristic_cluster_name(sample_captions)


_ASK_SYS = (
    "You answer questions about the user's OWN saved/liked Instagram posts. "
    "Use ONLY the numbered items provided as context. Cite every claim with the "
    "item number in square brackets, e.g. [3]. If the items do not answer the "
    "question, say so plainly. Keep it to a short paragraph or a tight list."
)


def _anthropic_answer(question: str, items: list[dict]) -> str:
    client = _client()
    ctx = "\n\n".join(
        f"[{n}] (@{it.get('creator','?')}, {it.get('source')}, {it.get('saved_date')})\n"
        f"{(it.get('caption') or it.get('summary') or '').strip()[:700]}"
        for n, it in enumerate(items, 1)
    )
    msg = client.messages.create(
        model=settings.llm_model,
        max_tokens=1200,
        system=_ASK_SYS,
        messages=[{"role": "user", "content": f"Question: {question}\n\nItems:\n{ctx}"}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


# ─────────────────────────── public interface ───────────────────────────

def enrich_items(items: list[dict]) -> list[dict]:
    """[{summary, tags, is_actionable}] aligned with `items`."""
    if settings.llm_enabled:
        try:
            return _anthropic_enrich(items)
        except Exception as e:  # pragma: no cover - network/credit failure
            print(f"  ! anthropic enrich failed ({e}); falling back to heuristics")
    return [_heuristic_enrich_one(it) for it in items]


def name_cluster(cluster_id: int, sample_captions: list[str]) -> str:
    if settings.llm_enabled:
        try:
            return _anthropic_name_cluster(cluster_id, sample_captions)
        except Exception as e:  # pragma: no cover
            print(f"  ! anthropic cluster-name failed ({e}); using keywords")
    return _heuristic_cluster_name(sample_captions)


def answer_question(question: str, items: list[dict]) -> tuple[str, bool]:
    """(answer_text, used_llm)."""
    if settings.llm_enabled:
        try:
            return _anthropic_answer(question, items), True
        except Exception as e:  # pragma: no cover
            print(f"  ! anthropic answer failed ({e})")
    return _heuristic_answer(question, items), False


def _heuristic_answer(question: str, items: list[dict]) -> str:
    """No-LLM synthesis: no reasoning, but groups + dedupes the retrieved
    items into something more like an answer than a raw ranked dump."""
    if not items:
        return (
            "Nothing in your archive matches that closely. Try different "
            "wording, or set LLM_PROVIDER=anthropic for real synthesis over "
            "sparser matches."
        )

    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for it in items:
        key = it.get("cluster_name") or "Ungrouped"
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(it)

    n_actionable = sum(1 for it in items if it.get("is_actionable", True))
    creators = {it.get("creator") for it in items if it.get("creator")}

    head = (
        f"Q&A synthesis is off (LLM_PROVIDER=none) — grouping your {len(items)} "
        f"closest matches instead of reasoning over them "
        f"({n_actionable} to-do, {len(items) - n_actionable} to-know, "
        f"from {len(creators)} creator{'s' if len(creators) != 1 else ''})."
    )
    lines = [head, ""]
    for key in order:
        group = groups[key]
        lines.append(f"{key} ({len(group)})")
        for it in group[:5]:
            summary = it.get("summary") or _first_sentence(it.get("caption") or "") or "(no caption)"
            lines.append(f"  · @{it.get('creator', '?')} — {summary}")
        if len(group) > 5:
            lines.append(f"  · …and {len(group) - 5} more")
        lines.append("")
    return "\n".join(lines).rstrip()
