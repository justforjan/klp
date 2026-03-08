from app.config.register_settings import register_setting
from app.config import AppSettings

@register_setting("prod")
class ProdSettings(AppSettings):
    pass