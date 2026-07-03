"""Ortam değişkenlerinden okunan uygulama ayarları."""
import os

from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "evet")


OBD_MOCK_MODE: bool = _bool_env("OBD_MOCK_MODE", True)
OBD_ADAPTER_PORT: str | None = os.getenv("OBD_ADAPTER_PORT") or None

ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8")

DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/history.db")

CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
