"""Read-only post-deploy checks. Never visits checkout or sends analytics."""
import hashlib
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

SITE = 'https://namastejewelrystore.com'
ROOT = Path(__file__).resolve().parents[1]
REVISION = os.environ.get('GITHUB_SHA', 'manual')


def get(path):
    request = Request(SITE + path + '?release=' + REVISION,
                      headers={'User-Agent': 'NamasteStorefrontDeploymentCheck/1.0'})
    with urlopen(request, timeout=25) as response:
        assert response.status == 200, path
        assert response.url.startswith(SITE + '/'), 'Unexpected redirect: ' + path
        return response.read()


def check():
    home = get('/').decode()
    assert 'data-bookshop-link' in home, 'Updated footer missing'
    assert 'tel:+12126450141' in home, 'Contact link missing'
    assert 'Stocking stuffers under $10' in home, 'Holiday discovery link missing'
    assert '<meta name="robots" content="noindex' not in home, 'Home is noindex'
    assert '<link rel="canonical" href="' + SITE + '/"' in home, 'Canonical mismatch'
    gifts = get('/gifts/stocking-stuffers/').decode()
    assert 'How to choose a small jewelry gift' in gifts, 'Gift guide missing'
    assert SITE + '/sitemap.xml' in get('/robots.txt').decode(), 'Sitemap not advertised'
    sitemap = ET.fromstring(get('/sitemap.xml'))
    urls = {el.text for el in sitemap.findall('.//{*}loc')}
    assert SITE + '/gifts/stocking-stuffers/' in urls, 'Gift guide absent from sitemap'
    assert SITE + '/shop/under-10/' in urls, 'Budget collection absent from sitemap'
    assert SITE + '/cart/' not in urls, 'Cart must not be in sitemap'
    for filename in ('site.js', 'cart.js', 'ga.js'):
        actual = hashlib.sha256(get('/assets/' + filename)).hexdigest()
        expected = hashlib.sha256((ROOT / 'src' / 'assets' / filename).read_bytes()).hexdigest()
        assert actual == expected, 'Published asset differs: ' + filename
    print(f'PASS: live homepage, gift guide, robots, {len(urls)} sitemap URLs and all 3 JavaScript assets; revision {REVISION}')


if __name__ == '__main__':
    for attempt in range(8):
        try:
            check()
            break
        except Exception as error:
            print(f'Attempt {attempt + 1}: {error}', flush=True)
            if attempt == 7:
                raise
            time.sleep(15)
