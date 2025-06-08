from .custom_crawler import crawl_from_config
from .google_scraper import google_search
from .bing_api import bing_search


def discover_sites(method='config', keywords=None, proxy=None):
    if method == 'google' and keywords:
        return google_search(keywords, proxy)
    if method == 'bing' and keywords:
        return bing_search(keywords, proxy)
    return crawl_from_config()
