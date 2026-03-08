from app.config.register_settings import register_setting

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

@register_setting("base")
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

    hf_access_token: str = "" # TODO: Remove the default value and handle it differenlty depending on the environment (prod, tests, pipeline)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_username}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"