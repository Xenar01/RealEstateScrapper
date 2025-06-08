import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from RealEstateScraper.site_discovery.custom_crawler import crawl_from_config
from RealEstateScraper.site_discovery import discover_sites


def test_crawl_from_config():
    sites = crawl_from_config()
    assert ('ikar', 'https://ikar.sy') in sites
    assert ('opensooq', 'https://sy.opensooq.com') in sites
    assert ('yabaiti', 'https://yabaiti.com') in sites


def test_discover_sites_default():
    sites = discover_sites()
    assert len(sites) >= 3
