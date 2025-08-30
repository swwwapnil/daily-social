# daily-social
Automation service that fetches RSS feeds daily, generates social copy with DeepSeek, saves to Google Docs, and emails summaries.
=======
# Daily Social Automation

Automation service that fetches RSS feeds daily, generates social copy with DeepSeek, saves to Google Docs, and emails a summary to the marketing alias every morning at **08:00 SGT**.

## ✨ Features
- Polls multiple RSS feeds
- Scores and selects up to 3 trending stories
- Generates copy for:
  - Twitter (≤ 280 chars)
  - LinkedIn (≤ 1300 chars, with hook + CTA)
- Creates a daily Google Doc in “Daily Social Posts”
- Emails a summary + doc link automatically

## 🚀 How to run
1. Create venv & activate  
2. `pip install` requirements  
3. Set `.env` and `config.yaml`  
4. Put `credentials.json` in project root  
5. Authorize once:
   ```bash
   python app.py --once

