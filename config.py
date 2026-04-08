from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    fred_api_key: Optional[str] = Field(default=None, env="FRED_API_KEY")
    cache_dir: str = Field(default=".cache", env="CACHE_DIR")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    app_env: str = Field(default="development", env="APP_ENV")
    request_timeout: int = 15

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def has_fred(self) -> bool:
        return bool(self.fred_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Fed funds rate — update this single value each quarter from https://fred.stlouisfed.org/series/FEDFUNDS
# Q1 2025: 4.33% (after Jan 2025 cut). Using 5.33 as of Q4 2024.
FEDERAL_FUNDS_RATE: float = 5.33
