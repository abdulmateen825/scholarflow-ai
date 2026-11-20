from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "ScholarFlow AI"
    debug: bool = False
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    tavily_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    google_classroom_mcp_url: str = "https://classroommcp.googleapis.com/mcp/v1"
    google_drive_mcp_url: str = "https://drivemcp.googleapis.com/mcp/v1"
    google_mcp_access_token: str = ""
    upload_dir: Path = ROOT.parent / "uploads"
    database_path: Path = ROOT.parent / "data" / "scholarflow.sqlite3"
    max_upload_mb: int = 15

    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return list(dict.fromkeys([self.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"]))

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
