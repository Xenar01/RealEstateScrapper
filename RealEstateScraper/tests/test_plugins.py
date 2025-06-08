import sys
from pathlib import Path
import requests
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from RealEstateScraper.site_scrapers.plugins import ikar, opensooq, yabaiti


def _raise(*args, **kwargs):
    raise requests.RequestException()


@pytest.mark.parametrize('plugin', [ikar, opensooq, yabaiti])
def test_plugin_handles_errors(monkeypatch, tmp_path, plugin):
    monkeypatch.setattr(plugin.requests.Session, 'get', _raise)
    monkeypatch.setattr(plugin.requests.Session, 'post', _raise)
    listings = plugin.scrape(['title'], tmp_path, master_password=None, proxy=None)
    assert listings == []
