from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/klp"
    debug: bool = True
    reload_data: bool = True
    geocode: bool = False
    scrape_schedule: str = "0 6,18 * * *"
    start_date: str = "2025-05-29"
    end_date: str = "2025-06-09"
    year: int = 2025

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
