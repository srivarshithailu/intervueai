"""App settings, read once from environment variables and backend/.env.

Fails closed: dev login is refused at startup unless ENV=development, and
Firebase login is refused at startup without FIREBASE_PROJECT_ID.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file so the server works from any working directory.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    env: Literal["development", "production"] = "development"
    auth_mode: Literal["dev", "firebase"] = "dev"
    firebase_project_id: str = ""

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "intervueai"

    llm_chain: str = "mock"
    llm_chain_report: str = "mock"
    groq_api_key: str = ""
    groq_model_fast: str = ""
    groq_model_report: str = ""
    gemini_api_key: str = ""
    gemini_model_fast: str = ""
    gemini_model_report: str = ""
    nvidia_api_key: str = ""
    nvidia_model: str = ""

    stt_chain: str = "mock"
    groq_stt_model: str = ""
    local_whisper_model: str = "small.en"

    max_upload_mb: int = 5
    max_segment_mb: int = 3
    max_questions_default: int = 8
    time_limit_minutes_default: int = 25
    cors_origins: str = "http://localhost:5173"

    @model_validator(mode="after")
    def check_auth_settings(self) -> "Settings":
        if self.auth_mode == "dev" and self.env != "development":
            raise ValueError("AUTH_MODE=dev is only allowed when ENV=development")
        # Without a project id every token would be checked against nothing; refuse to start instead.
        self.firebase_project_id = self.firebase_project_id.strip()
        if self.auth_mode == "firebase" and not self.firebase_project_id:
            raise ValueError("AUTH_MODE=firebase needs FIREBASE_PROJECT_ID in backend/.env")
        return self

    @staticmethod
    def split_list(value: str) -> list[str]:
        """Turn 'groq, gemini' into ['groq', 'gemini']."""
        return [item.strip().lower() for item in value.split(",") if item.strip()]

    @property
    def llm_chain_list(self) -> list[str]:
        return self.split_list(self.llm_chain)

    @property
    def llm_chain_report_list(self) -> list[str]:
        return self.split_list(self.llm_chain_report)

    @property
    def stt_chain_list(self) -> list[str]:
        return self.split_list(self.stt_chain)

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    # Cached so every module sees the same settings object.
    return Settings()
