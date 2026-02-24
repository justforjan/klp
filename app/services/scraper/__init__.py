from app.services.scraper.base import BaseScraper
from app.services.scraper.klp_scraper import KLPScraper
from app.services.scraper.test_data_scraper import TestDataScraper
from app.config import AppSettings

__all__ = ["get_scraper"]

def get_scraper(scraper_type: str) -> BaseScraper:
    if scraper_type == "test":
        return TestDataScraper()
    elif scraper_type == "prod":
        return KLPScraper()
    else:
        raise ValueError(f"Invalid data_loader_type: {scraper_type}")



