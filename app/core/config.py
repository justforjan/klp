from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database configuration
    database_username: str = "klp_user"
    database_password: str = "klp_password"
    database_host: str = "localhost"
    database_port: int = 5433
    database_name: str = "klp_db"

    # Application configuration
    debug: bool = True
    reload_data: bool = False
    run_geocode: bool = True
    get_embeddings: bool = True
    scrape_schedule: str = "0 6,18 * * *"
    start_date: str = "2025-05-29"
    end_date: str = "2025-06-09"
    year: int = 2025

    hf_access_token: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
