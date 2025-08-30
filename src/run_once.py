from datetime import datetime
from .config import SETTINGS
from .feeds import load_feed_config, collect_all_entries
from .scorer import score_items, top_k_diverse
from .deepseek_client import draft_copy
from .gdocs import upsert_daily_doc
from .render import render_email_summary
from .emailer import send_summary

def run_once():
    feeds = load_feed_config("feeds.yaml")
    items = collect_all_entries(feeds)
    if not items:
        print("No items found from feeds.")
        return

    scored = score_items(items)
    top = top_k_diverse(scored, k=3)

    # Generate copy
    for it in top:
        it["generated"] = draft_copy(it)

    # Write to Google Doc
    doc_url = upsert_daily_doc(top)

    # Email summary
    date_str = datetime.now().strftime("%Y-%m-%d")
    email_body = render_email_summary(date_str, top, doc_url)
    subject = f"Daily Social Picks – {date_str}"
    send_summary(subject, email_body)

    print("Done. Doc:", doc_url)

if __name__ == "__main__":
    run_once()
