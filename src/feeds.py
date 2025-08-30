import feedparser
import yaml
from datetime import datetime, timezone
from typing import List, Dict, Any
from dateutil import parser as dateparser

def load_feed_config(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("feeds", [])

def parse_entries(feed_url: str) -> List[Dict[str, Any]]:
    d = feedparser.parse(feed_url)
    entries = []
    for e in d.entries:
        # Normalize
        published = None
        if getattr(e, "published", None):
            try:
                published = dateparser.parse(e.published)
            except Exception:
                published = None
        entries.append({
            "title": getattr(e, "title", "").strip(),
            "link": getattr(e, "link", ""),
            "summary": getattr(e, "summary", ""),
            "published": published,
            "source": d.feed.get("title", feed_url),
        })
    return entries

def collect_all_entries(feed_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_items = []
    for f in feed_list:
        url = f.get("url")
        if not url:
            continue
        items = parse_entries(url)
        all_items.extend(items)
    return all_items
