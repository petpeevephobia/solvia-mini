from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    cors_origins: str = "https://solvia.app"

    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    serper_api_key: str = ""

    firecrawl_api_key: str = ""

    scrape_timeout_sec: float = 120.0
    llm_timeout_sec: float = 120.0
    serp_timeout_sec: float = 60.0
    llm_max_output_tokens: int = 8192

    # Admin dashboard
    admin_secret: str = ""

    # Zoho SMTP — transactional email delivery
    smtp_host: str = "smtp.zoho.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Solvia Labs"
    smtp_use_tls: bool = True
    smtp_reply_to: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def smtp_configured(self) -> bool:
        return bool(
            self.smtp_host.strip()
            and self.smtp_username.strip()
            and self.smtp_password.strip()
            and self.smtp_from_email.strip()
        )


settings = Settings()
