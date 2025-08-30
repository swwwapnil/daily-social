from datetime import datetime
from typing import List, Dict

def today_doc_title() -> str:
    return datetime.now().strftime("Daily Social Posts - %Y-%m-%d")

def render_doc_body(date_str: str, items: List[Dict]) -> str:
    # Plain text; Docs API will insert as paragraphs
    lines = [f"Daily Social Posts – {date_str}", ""]
    for i, it in enumerate(items, start=1):
        lines.append(f"{i}. {it.get('title','')}")
        lines.append(f"   Source: {it.get('source','')}")
        lines.append(f"   URL: {it.get('link','')}")
        lines.append("")
        lines.append("   Twitter:")
        lines.append(f"   {it['generated']['twitter']}")
        lines.append("")
        lines.append("   LinkedIn:")
        lines.append(f"   {it['generated']['linkedin']}")
        lines.append("")
    return "\n".join(lines)

def render_email_summary(date_str: str, items: List[Dict], doc_url: str) -> str:
    lines = [f"Daily Social Picks – {date_str}", ""]
    for i, it in enumerate(items, start=1):
        lines.append(f"{i}) {it.get('title','')}")
        lines.append(f"   {it.get('link','')}")
        lines.append(f"   Tweet: {it['generated']['twitter'][:200]}{'...' if len(it['generated']['twitter'])>200 else ''}")
        lines.append("")
    lines.append(f"Google Doc: {doc_url}")
    return "\n".join(lines)
