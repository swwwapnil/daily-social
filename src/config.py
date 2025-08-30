import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    smtp_sender: str = os.getenv("SMTP_SENDER", "")
    smtp_app_password: str = os.getenv("SMTP_APP_PASSWORD", "")
    smtp_to: str = os.getenv("SMTP_TO", "")
    google_folder_name: str = os.getenv("GOOGLE_FOLDER_NAME", "Daily Social Posts")
    google_folder_id: str = os.getenv("GOOGLE_FOLDER_ID", "")
    tz_schedule: str = os.getenv("TZ_SCHEDULE", "Asia/Singapore")

SETTINGS = Settings()
