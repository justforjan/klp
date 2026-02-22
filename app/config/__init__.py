import os

from app.config.base import AppSettings
from app.config.local import LocalSettings
from app.config.local_docker import LocalDockerSettings
from app.config.prod import ProdSettings

__all__ = ["settings"]

def _get_settings(env: str) -> AppSettings:
    if env == "local":
        return LocalSettings()
    elif env == "local_docker":
        return LocalDockerSettings()
    elif env == "prod":
        return ProdSettings()
    else:
        raise ValueError(f"Invalid environment: {env}")

_env = os.getenv("ENV", "local")
settings = _get_settings(_env)