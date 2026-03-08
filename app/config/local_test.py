from app.config.local import LocalSettings
from app.config.register_settings import register_setting
try:
    from typing import Literal
except Exception:
    from typing_extensions import Literal  # type: ignore


@register_setting("local_test")
class LocalTestSettings(LocalSettings):

    # Application configuration
    debug: bool = True
    reload_data: bool = True
    run_geocode: bool = False
    get_embeddings: bool = False

    start_date: str = "2024-07-01"
    end_date: str = "2025-07-02"
    year: int = 2024

    data_loader_type: Literal["test", "prod"] = "test"