import os
from dataclasses import dataclass

def _int(name, default=0):
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default

@dataclass
class Config:
    api_id: int
    api_hash: str
    session_string: str
    owner_id: int
    db_path: str
    workdir: str
    bot_name: str
    gemini_api_key: str
    gemini_model: str
    tmdb_api_key: str
    ocr_api_key: str
    timezone: str

    @classmethod
    def from_env(cls):
        return cls(
            api_id=_int("API_ID"),
            api_hash=os.getenv("API_HASH", "").strip(),
            session_string=os.getenv("SESSION_STRING", "").strip(),
            owner_id=_int("OWNER_ID"),
            db_path=os.getenv("DB_PATH", "ubot.db").strip() or "ubot.db",
            workdir=os.getenv("WORKDIR", ".").strip() or ".",
            bot_name=os.getenv("BOT_NAME", "UBot").strip() or "UBot",
            gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash",
            tmdb_api_key=os.getenv("TMDB_API_KEY", "").strip(),
            ocr_api_key=os.getenv("OCR_API_KEY", "").strip(),
            timezone=os.getenv("TIMEZONE", "Asia/Jakarta").strip() or "Asia/Jakarta",
        )
