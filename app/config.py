from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    google_cloud_project: str | None = Field(default=None, alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="global", alias="GOOGLE_CLOUD_LOCATION")
    google_genai_use_vertexai: bool = Field(default=True, alias="GOOGLE_GENAI_USE_VERTEXAI")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")

    parallel_api_key: str | None = Field(default=None, alias="PARALLEL_API_KEY")

    demo_mode: bool = Field(default=False, alias="SETWATCH_DEMO_MODE")
    max_search_results: int = Field(default=5, alias="SETWATCH_MAX_SEARCH_RESULTS", ge=1, le=10)
    search_mode: str = Field(default="fast", alias="SETWATCH_SEARCH_MODE")

    @property
    def live_ready(self) -> bool:
        return bool(self.google_cloud_project and self.parallel_api_key and not self.demo_mode)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
