from app.config.register_settings import register_setting
from app.config import AppSettings
try:
    from typing import Literal
except Exception:
    from typing_extensions import Literal  # type: ignore

@register_setting("local")
class LocalSettings(AppSettings):
    # Database configuration
    database_username: str = "klp_user"
    database_password: str = "klp_password"
    database_host: str = "localhost"
    database_port: int = 5433
    database_name: str = "klp_db"

    # Application configuration
    debug: bool = True
    reload_data: bool = True
    run_geocode: bool = False
    get_embeddings: bool = False

    data_loader_type: Literal["test", "prod"] = "prod"