try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    # Database configuration
    database_username: str
    database_password: str
    database_host: str
    database_port: int
    database_name: str

    # Application configuration
    debug: bool = False
    reload_data: bool = True
    run_geocode: bool = True
    get_embeddings: bool = True
    scrape_schedule: str = "0 6,18 * * *"
    start_date: str = "2025-05-29"
    end_date: str = "2025-06-09"
    year: int = 2025
    data_loader_type: Literal["test", "prod"] = "prod"

    hf_access_token: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)