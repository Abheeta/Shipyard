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

from .config import settings

_STOPWORDS = set(
    """a an the and or but if then than so of to in on for with without at by from up
    down out over under again further once here there all any both each few more most
    other some such no nor not only own same too very can will just don should now this
    that these those i me my we our you your it its is are was were be been being do does
    did doing have has had as about into your you'll you're it's im i'm get got make made
    how what why when where who new video reel post today one two like really""".split()
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


def _keywords(text: str, n: int = 5) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]{2,}", (text or "").lower())
    freq = Counter(w for w in words if w not in _STOPWORDS)
    return [w for w, _ in freq.most_common(n)]


def _heuristic_actionable(caption: str) -> bool:
    low = (caption or "").lower()
    if any(h in low for h in _ACTIONABLE_HINTS):
        return True
    if any(h in low for h in _INFO_HINTS):
        return False
    return True  # default: assume there's something to do


def _heuristic_enrich_one(item: dict) -> dict:
    caption = item.get("caption") or ""
    tags = [t.lower() for t in (item.get("hashtags") or [])][:5]
    if not tags:
        tags = _keywords(caption, 5)
    summary = _first_sentence(caption)
    if not summary:
        summary = f"Post by {item.get('creator_name') or item.get('creator') or 'unknown'} (no caption)"
    return {
        "summary": summary,
        "tags": tags,
        "is_actionable": _heuristic_actionable(caption),
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
    '{"i": <index>, "summary": "<= 18 words, plain, no hype, only facts present in the caption", '
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
    if not items:
        return ("Q&A needs the Claude API (set LLM_PROVIDER=anthropic and "
                "ANTHROPIC_API_KEY). No items matched this query either.", False)
    lines = [
        "Q&A synthesis is off (no Claude API key). Closest matches from your archive:",
        "",
    ]
    for n, it in enumerate(items, 1):
        lines.append(f"[{n}] @{it.get('creator','?')} — {it.get('summary') or _first_sentence(it.get('caption') or '')}")
    return "\n".join(lines), False
