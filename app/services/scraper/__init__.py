from app.services.scraper.base import BaseScraper
from app.services.scraper.klp_scraper import KLPScraper
from app.services.scraper.test_data_scraper import TestDataScraper
from app.config import settings

__all__ = ["scraper"]


def _get_scraper() -> BaseScraper:
    if settings.data_loader_type == "test":
        return TestDataScraper()
    elif settings.data_loader_type == "prod":
        return KLPScraper()
    else:
        raise ValueError(f"Invalid data_loader_type: {settings.data_loader_type}")

scraper = _get_scraper()



