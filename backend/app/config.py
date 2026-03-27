from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    cors_origins: str = "https://solvia.app"

    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    google_cse_api_key: str = ""
    google_cse_id: str = ""

    firecrawl_api_key: str = ""

    scrape_timeout_sec: float = 120.0
    llm_timeout_sec: float = 120.0
    serp_timeout_sec: float = 60.0
    llm_max_output_tokens: int = 8192

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
