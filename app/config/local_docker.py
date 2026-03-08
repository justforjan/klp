from app.config.register_settings import register_setting
from app.config import AppSettings

@register_setting("local_docker")
class LocalDockerSettings(AppSettings):
    # Database configuration
    database_username: str = "klp_user"
    database_password: str = "klp_password"
    database_host: str = "klp_db"
    database_port: int = 5432
    database_name: str = "klp_db"

    # Application configuration
    debug: bool = True
    reload_data: bool = False
    run_geocode: bool = False
    get_embeddings: bool = False
