from typing import List, Dict
from datetime import datetime, timezone
import math

# Simple heuristic scorer:
# - recency boost (last 36h)
# - title length & keyword presence
# - source diversity handled by later top-k filter

KEYWORDS = [
    "AI","LLM","DeepSeek","OpenAI","Google","Microsoft", "startup","model",
    "privacy","security","research","launch","update","bug","breach",
    "cloud","data","vision","robot","chip","GPU","NVIDIA","Meta",
]

def score_items(items: List[Dict]) -> List[Dict]:
    now = datetime.now(timezone.utc)
    scored = []
    for it in items:
        s = 0.0
        title = (it.get("title") or "").strip()
        summary = (it.get("summary") or "").strip()

        # recency (hours ago)
        published = it.get("published")
        if published:
            age_hours = (now - published.astimezone(timezone.utc)).total_seconds() / 3600.0
            # decay after 36h
            s += max(0.0, 1.5 - (age_hours / 36.0))

        # title quality
        if 30 <= len(title) <= 120:
            s += 0.5
        elif len(title) > 0:
            s += 0.2

        # keyword hits
        text = f"{title} {summary}".lower()
        hits = sum(1 for kw in KEYWORDS if kw.lower() in text)
        s += min(1.5, 0.2 * hits)

        scored.append({**it, "score": round(s, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored

def top_k_diverse(scored: List[Dict], k: int = 3) -> List[Dict]:
    seen_sources = set()
    chosen = []
    for it in scored:
        src = it.get("source","")
        if src in seen_sources and len(chosen) < k:
            # allow duplicates only if we don't reach k otherwise
            pass
        chosen.append(it)
        seen_sources.add(src)
        if len(chosen) == k:
            break
    return chosen[:k]
