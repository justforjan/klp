import os

from app.config.base import AppSettings
from app.config.local import LocalSettings
from app.config.local_docker import LocalDockerSettings
from app.config.prod import ProdSettings
from app.config.local_test import LocalTestSettings

__all__ = ["settings", "AppSettings"]

def _get_settings(env: str) -> AppSettings:
    if env == "local":
        return LocalSettings()
    if env == "local_test":
        return LocalTestSettings()
    elif env == "local_docker":
        return LocalDockerSettings()
    elif env == "prod":
        return ProdSettings()
    else:
        raise ValueError(f"Invalid environment: {env}")

_env = os.getenv("ENV", "local_test")
settings = _get_settings(_env)
