import requests
from typing import Dict
from .config import SETTINGS

API_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = (
    "You are a concise social copywriter. "
    "Produce two platform-specific outputs: "
    "1) Twitter: ≤280 characters, punchy, 1 relevant hashtag max, include the article title if useful, no emojis. "
    "2) LinkedIn: ≤1300 characters with a two-sentence hook at the top, then a short paragraph, end with 2-3 relevant hashtags. "
    "Do not include markdown code fences. Keep it neutral and factual, no hype."
)

def _call_llm(user_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {SETTINGS.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 700,
        "stream": False,
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # DeepSeek is OpenAI-compatible
    return data["choices"][0]["message"]["content"]

def draft_copy(item: Dict) -> Dict[str,str]:
    title = item.get("title","").strip()
    link = item.get("link","").strip()
    summary = item.get("summary","").strip()

    user_prompt = (
        f"Article Title: {title}\n"
        f"URL: {link}\n"
        f"Summary: {summary}\n\n"
        "Return the outputs in this plain text format exactly:\n"
        "Twitter:\n<one line tweet text (<=280 chars)>\n"
        "LinkedIn:\n<up to ~1300 chars with a two-sentence hook>\n"
    )
    content = _call_llm(user_prompt)

    # naive split
    tw, li = "", ""
    if "Twitter:" in content and "LinkedIn:" in content:
        segs = content.split("Twitter:",1)[1]
        parts = segs.split("LinkedIn:",1)
        tw = parts[0].strip()
        li = parts[1].strip()
    else:
        # fallback: treat all as LinkedIn
        li = content.strip()

    # hard truncate just in case
    tw = tw[:280]
    li = li[:1300]
    return {"twitter": tw, "linkedin": li}
