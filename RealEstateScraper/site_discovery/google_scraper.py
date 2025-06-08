import requests
from requests import RequestException
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0'
GOOGLE_URL = 'https://www.google.com/search'


def google_search(keywords, proxy=None):
    query = '+'.join(keywords)
    params = {'q': query, 'num': 10, 'hl': 'ar'}
    headers = {'User-Agent': USER_AGENT}
    try:
        resp = requests.get(GOOGLE_URL, params=params, headers=headers,
                            timeout=10, proxies={'http': proxy, 'https': proxy} if proxy else None)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
    except RequestException:
        return []
    results = []
    for g in soup.select('div.g'):
        link = g.find('a')
        if link and link.has_attr('href'):
            url = link['href']
            title = link.get_text(strip=True)
            results.append((title, url))
    return results
