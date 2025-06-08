import requests
from requests import RequestException
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

from ...utils import auth
from ...utils import dedup

SITE_NAME = 'yabaiti'
BASE_URL = 'https://yabaiti.com'


def scrape(selected_fields, save_dir, master_password=None, proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies.update({'http': proxy, 'https': proxy})
    creds = auth.load_credentials(SITE_NAME, master_password)
    try:
        if creds:
            session.post(f'{BASE_URL}/login', data={'username': creds[0], 'password': creds[1]})
        resp = session.get(BASE_URL, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
    except RequestException:
        return []
    listings = []
    for item in soup.select('article'):
        data = {'site': SITE_NAME, 'title': item.get_text(strip=True)}
        if 'price' in selected_fields:
            data['price'] = item.get('data-price')
        if 'description' in selected_fields:
            data['description'] = item.get('data-desc')
        if 'location' in selected_fields:
            data['location'] = item.get('data-city')
        images = []
        if 'images' in selected_fields:
            img = item.find('img')
            if img:
                img_url = img['src']
                date_dir = datetime.now().strftime('%Y%m%d')
                img_dir = Path(save_dir) / SITE_NAME / date_dir
                img_dir.mkdir(parents=True, exist_ok=True)
                title_safe = ''.join(c if c.isalnum() else '_' for c in data['title'])[:50]
                city_safe = ''.join(c if c.isalnum() else '_' for c in data.get('location',''))[:30]
                fname = img_dir / f"{title_safe}_{city_safe}_{len(images)}.jpg"
                try:
                    r = session.get(img_url, timeout=10)
                    if r.ok:
                        fname.write_bytes(r.content)
                        images.append(str(fname))
                except RequestException:
                    pass
        if 'phone' in selected_fields:
            data['phone'] = item.get('data-phone')
        data['images'] = images
        listings.append(data)
    return dedup.deduplicate(listings)
