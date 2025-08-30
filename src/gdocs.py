from __future__ import annotations
import os
from typing import Optional
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .config import SETTINGS
from .render import today_doc_title

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

def _get_creds() -> Credentials:
    """Load or create OAuth credentials and persist token.json."""
    creds: Optional[Credentials] = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return creds

def _ensure_folder(drive, name: str) -> str:
    """Return the Drive folder ID; create if missing (unless GOOGLE_FOLDER_ID is provided)."""
    if SETTINGS.google_folder_id:
        return SETTINGS.google_folder_id

    q = (
        f"name = '{name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"trashed = false"
    )
    resp = drive.files().list(q=q, spaces="drive", fields="files(id,name)").execute()
    files = resp.get("files", []) or []
    if files:
        return files[0]["id"]
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    f = drive.files().create(body=meta, fields="id").execute()
    return f["id"]

def _find_doc_in_folder(drive, folder_id: str, title: str) -> Optional[str]:
    """Return the doc ID by title within a folder, or None."""
    q = (
        f"name = '{title}' and "
        f"'{folder_id}' in parents and "
        f"mimeType = 'application/vnd.google-apps.document' and trashed = false"
    )
    resp = drive.files().list(q=q, spaces="drive", fields="files(id,name)").execute()
    files = resp.get("files", []) or []
    if files:
        return files[0]["id"]
    return None

def _create_doc_in_folder(docs, drive, folder_id: str, title: str) -> str:
    """Create a new Google Doc with title and move it into the folder; return doc ID."""
    doc = docs.documents().create(body={"title": title}).execute()
    file_id = doc["documentId"]
    # Move from root to the target folder (ignore errors if already in place)
    drive.files().update(fileId=file_id, addParents=folder_id, removeParents="root").execute()
    return file_id

def upsert_daily_doc(items) -> str:
    """
    Write today's content to the Google Doc named 'Daily Social Posts - YYYY-MM-DD'
    in the configured folder.

    Behavior is controlled by GDOC_MODE (env var):
      - 'append'   (default): append content at end (safest)
      - 'recreate'           : delete today's doc (if exists), create fresh, insert
      - 'overwrite'          : replace body in-place (safe range calc)
    """
    creds = _get_creds()
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    folder_id = _ensure_folder(drive, SETTINGS.google_folder_name)
    title = today_doc_title()
    mode = os.getenv("GDOC_MODE", "append").strip().lower()

    # Build today's text
    from .render import render_doc_body
    date_str = datetime.now().strftime("%Y-%m-%d")
    text = render_doc_body(date_str, items)
    if not text.endswith("\n"):
        text += "\n"

    if mode == "recreate":
        # Delete today's doc if present, then create fresh and insert
        existing_id = _find_doc_in_folder(drive, folder_id, title)
        if existing_id:
            drive.files().delete(fileId=existing_id).execute()
        file_id = _create_doc_in_folder(docs, drive, folder_id, title)
        requests = [{"insertText": {"location": {"index": 1}, "text": text}}]
        docs.documents().batchUpdate(documentId=file_id, body={"requests": requests}).execute()
        return f"https://docs.google.com/document/d/{file_id}/edit"

    # Else ensure doc exists (append/overwrite both need an ID)
    file_id = _find_doc_in_folder(drive, folder_id, title)
    if not file_id:
        file_id = _create_doc_in_folder(docs, drive, folder_id, title)

    # Fetch current structure once
    document = docs.documents().get(documentId=file_id).execute()
    body = document.get("body", {}) or {}
    content = body.get("content", []) or []

    if mode == "overwrite":
        # Calculate a delete range that avoids the trailing section break.
        # Strategy: delete from 1 to startIndex of the last segment (if available),
        # otherwise use endIndex - 1 as a fallback.
        start_idx = 1
        if len(content) >= 2:
            delete_end = max(start_idx + 1, content[-1].get("startIndex", start_idx + 1))
        else:
            end_idx = (content[-1].get("endIndex", start_idx + 1) if content else start_idx + 1)
            delete_end = max(start_idx + 1, end_idx - 1)

        requests = [
            {"deleteContentRange": {"range": {"startIndex": start_idx, "endIndex": delete_end}}},
            {"insertText": {"location": {"index": start_idx}, "text": text}},
        ]
        docs.documents().batchUpdate(documentId=file_id, body={"requests": requests}).execute()
        return f"https://docs.google.com/document/d/{file_id}/edit"

    # Default: append (safe)
    # Insert before trailing section break: endIndex - 1
    insert_index = (content[-1].get("endIndex", 1) - 1) if content else 1
    if insert_index < 1:
        insert_index = 1

    requests = [{"insertText": {"location": {"index": insert_index}, "text": text}}]
    docs.documents().batchUpdate(documentId=file_id, body={"requests": requests}).execute()
    return f"https://docs.google.com/document/d/{file_id}/edit"
