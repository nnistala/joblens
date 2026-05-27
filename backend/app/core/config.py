from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "JobLens"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    # ── Database / Cache / Search ────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/joblens"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENSEARCH_URL: str = "http://localhost:9200"

    # ── JWT / Auth ───────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Google OAuth ─────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── Crawler ──────────────────────────────────────────────────
    CRAWL_USER_AGENT: str = "JobLensBot/0.1 (+https://joblens.in)"
    CRAWL_DELAY_SECONDS: int = 2


settings = Settings()
