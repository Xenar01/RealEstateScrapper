import os
import yaml
import requests
from requests import RequestException

from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config.yaml'
BING_URL = 'https://api.bing.microsoft.com/v7.0/search'


def bing_search(keywords, proxy=None):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    api_key = cfg.get('bing_api_key')
    if not api_key:
        return []
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    query = '+'.join(keywords)
    params = {'q': query, 'mkt': 'ar-SA'}
    try:
        resp = requests.get(BING_URL, headers=headers, params=params, timeout=10,
                            proxies={'http': proxy, 'https': proxy} if proxy else None)
        resp.raise_for_status()
        data = resp.json()
    except RequestException:
        return []
    sites = []
    for w in data.get('webPages', {}).get('value', []):
        sites.append((w.get('name'), w.get('url')))
    return sites
