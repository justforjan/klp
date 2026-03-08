import os

from app.config.register_settings import _get_settings, register_setting
from app.config.base import AppSettings as AppSettings
from app.config.local import LocalSettings as LocalSettings
from app.config.local_docker import LocalDockerSettings as LocalDockerSettings
from app.config.prod import ProdSettings as ProdSettings
from app.config.local_test import LocalTestSettings as LocalTestSettings

__all__ = ["settings", "AppSettings", "register_setting"]


_env = os.getenv("ENV", "local_test")
settings = _get_settings(_env)
