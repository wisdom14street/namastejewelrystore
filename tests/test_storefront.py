"""Build and browser regressions with synthetic products and blocked external traffic.

Run: python3 -m unittest discover -s tests -v
Requires Python 3.12+, Pillow, Playwright and Chromium (or CHROMIUM_PATH).
"""
import functools
import http.server
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse
import xml.etree.ElementTree as ET

from fixtures import write_data
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class QuietServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class StorefrontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='jewelry-tests-')
        cls.root = Path(cls.temp.name)
        for name in ('scripts', 'site', 'src'):
            shutil.copytree(ROOT / name, cls.root / name)
        write_data(cls.root / 'data')
        subprocess.run(['python3', 'scripts/build.py'], cwd=cls.root, check=True, capture_output=True)
        cls.dist = cls.root / 'dist'
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0),
            functools.partial(QuietServer, directory=str(cls.dist)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),
                                            headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp.cleanup()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        self.live_response = None
        self.catalog_response = None
        self.block_catalog = False
        self.context.route('**/*', self.route)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [], 'Browser JavaScript errors')

    def route(self, route):
        url = urlparse(route.request.url)
        if url.hostname == '127.0.0.1':
            if url.path == '/data/catalog.json':
                if self.block_catalog:
                    return route.fulfill(status=503, body='Unavailable')
                if self.catalog_response is not None:
                    return route.fulfill(json=self.catalog_response)
            return route.continue_()
        if url.hostname == 'namastebookshop.com' and url.path.endswith('.js') and self.live_response is not None:
            return route.fulfill(json=self.live_response, headers={'Access-Control-Allow-Origin': '*'})
        # Includes Shopify, analytics, fonts, images and maps. No live writes or test hits.
        return route.abort()

    def visit(self, path):
        self.page.goto(self.base + path)

    def events(self, event):
        return self.page.evaluate('(name)=>(window.dataLayer||[]).filter(x=>x[0]==="event"&&x[1]===name).map(x=>x[2])', event)

    def test_generated_metadata_contact_and_referral(self):
        xml = ET.parse(self.dist / 'sitemap.xml')
        for loc in xml.findall('.//{*}loc'):
            target = self.dist / urlparse(loc.text).path.strip('/') / 'index.html'
            self.assertTrue(target.exists(), loc.text)
        for path in self.dist.rglob('*.html'):
            tags = Tags(path.read_text()).tags
            for key in ('og:image:width', 'og:image:height', 'og:image:alt'):
                self.assertLessEqual(sum(t == 'meta' and a.get('property') == key for t, a in tags), 1, str(path))
            text = path.read_text()
            self.assertNotIn('646-876-1401', text)
        for filename in ('cart/index.html', '404.html'):
            tags = Tags((self.dist / filename).read_text()).tags
            self.assertEqual([a['content'] for t, a in tags if t == 'meta' and a.get('name') == 'robots'], ['noindex'])
        self.visit('/')
        self.assertEqual(self.page.locator('script[src*="googletagmanager.com/gtag/js"]').count(), 1)
        self.assertIn('G-Y7R5K9NMW0', self.page.locator('script[src*="googletagmanager.com/gtag/js"]').get_attribute('src'))
        self.assertGreater(self.page.locator('a[href="tel:+12126450141"]').count(), 0)
        link = self.page.locator('[data-bookshop-link]')
        dest = urlparse(link.get_attribute('href'))
        self.assertEqual(dest.hostname, 'namastebookshop.com')
        self.assertEqual(parse_qs(dest.query)['utm_source'], ['namastejewelrystore.com'])
        self.page.evaluate('document.addEventListener("click", e=>e.preventDefault())')
        link.click()
        self.assertEqual(len(self.events('storefront_referral')), 1)
        self.assertEqual(self.events('purchase'), [])

    def test_variant_fallback_cart_and_checkout_attribution(self):
        self.visit('/products/test-options/')
        self.page.wait_for_function('document.querySelector("#stock").textContent.includes("Live stock unavailable")')
        self.assertEqual(self.page.locator('#price').inner_text(), '$7.99')
        self.page.select_option('#variant', '910002')
        self.assertEqual(self.page.locator('#price').inner_text(), '$18.50')
        self.assertEqual(self.page.locator('#buy').get_attribute('data-p'), '18.50')
        self.assertTrue(self.page.locator('#cmp').is_hidden())
        self.page.click('#buy')
        self.page.wait_for_selector('#cart:not([hidden])')
        self.assertIn('Large', self.page.locator('#cart .cit').inner_text())
        self.assertEqual(self.page.locator('#cart .cip').inner_text(), '$18.50 each')
        url = urlparse(self.page.evaluate('window.NI_CART_URL()'))
        self.assertEqual(url.hostname, 'namastebookshop.com')
        self.assertEqual(url.path, '/cart/910002:1')
        params = parse_qs(url.query)
        self.assertEqual(params['attributes[Storefront]'], ['Namaste Jewelry Store'])
        self.assertEqual(params['attributes[Site]'], ['namastejewelrystore.com'])
        self.assertEqual(params['ref'], ['namastejewelrystore'])
        self.assertIn('Namaste Jewelry Store', params['note'][0])
        self.assertEqual(len(self.events('view_item')), 1)
        self.assertEqual(len(self.events('add_to_cart')), 1)
        self.assertEqual(self.events('add_to_cart')[0]['value'], 18.5)
        self.assertEqual(self.events('begin_checkout'), [])
        self.page.evaluate('document.addEventListener("click", e=>e.preventDefault())')
        self.page.locator('#cart [data-checkout]').click()
        self.assertEqual(len(self.events('begin_checkout')), 1)
        self.assertEqual(self.events('purchase'), [])
        self.assertEqual(self.page.url, self.base + '/products/test-options/')

    def test_live_variant_price_and_removed_option(self):
        self.live_response = {'variants': [
            {'id': 910001, 'title': 'Small', 'price': 999, 'compare_at_price': 1200, 'available': True},
            {'id': 910002, 'title': 'Large', 'price': 1850, 'available': False},
        ]}
        self.visit('/products/test-options/')
        self.page.wait_for_function('document.querySelector("#price").textContent==="$9.99"')
        self.assertEqual(self.page.locator('#cmp').inner_text(), '$12.00')
        self.assertTrue(self.page.locator('#variant option[value="910002"]').evaluate('(x)=>x.disabled'))
        self.assertTrue(self.page.locator('#variant option[value="910003"]').evaluate('(x)=>x.disabled'))
        self.live_response = {'variants': [{'id': 999999, 'title': 'Replacement', 'price': 1999, 'available': True}]}
        self.page.reload()
        self.page.wait_for_function('document.querySelector("#buy").disabled')
        self.assertIn('no longer available', self.page.locator('#stock').inner_text())

    def test_cached_product_page_keeps_its_original_option_usable(self):
        self.page.add_init_script('''let legacyProduct;
            Object.defineProperty(window, 'NI_PRODUCT', {
                get(){return legacyProduct}, set(value){delete value.variants; legacyProduct=value}
            });''')
        self.visit('/products/test-options/')
        self.page.wait_for_function('document.querySelector("#stock").textContent.includes("Live stock unavailable")')
        self.assertFalse(self.page.locator('#buy').is_disabled())
        self.assertEqual(self.page.locator('#price').inner_text(), '$7.99')
        self.page.select_option('#variant', '910002')
        self.assertTrue(self.page.locator('#buy').is_disabled())
        self.assertIn('Reload this page', self.page.locator('#stock').inner_text())

    def test_search_suggestions_only_link_to_generated_stone_pages(self):
        self.visit('/')
        self.page.fill('#hq', 'tanzanite')
        self.page.wait_for_selector('#sugg:not([hidden])')
        links = self.page.locator('#sugg a').evaluate_all('(els)=>els.map(x=>x.getAttribute("href"))')
        self.assertNotIn('/stones/tanzanite/', links)
        self.assertIn('/products/rare-tanzanite/', links)
        self.page.fill('#hq', 'amethyst')
        self.page.wait_for_selector('#sugg a[href="/stones/amethyst/"]')
        self.page.locator('#hq').press('ArrowDown')
        self.page.locator('#hq').press('Escape')
        self.assertIsNone(self.page.locator('#hq').get_attribute('aria-activedescendant'))

    def test_generated_internal_links_and_structured_data(self):
        broken = set()
        for path in self.dist.rglob('*.html'):
            text = path.read_text()
            for tag, attrs in Tags(text).tags:
                href = attrs.get('href', '')
                if tag != 'a' or not href.startswith('/') or href.startswith('//'):
                    continue
                pathname = urlparse(href).path
                target = self.dist / pathname.lstrip('/')
                if pathname.endswith('/'):
                    target /= 'index.html'
                if not target.exists():
                    broken.add(pathname)
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
                self.assertIsInstance(json.loads(block), dict, str(path))
        self.assertEqual(sorted(broken), [])

    def test_gift_finder_keeps_budget_when_relaxing_other_preferences(self):
        self.visit('/gift-finder/')
        self.page.check('input[name=q0][value="3"]')  # earrings, only expensive matches in fixture
        self.page.check('input[name=q1][value="0"]')
        self.page.check('input[name=q2][value="0"]')  # under $10
        self.page.click('#quiz button[type=submit]')
        self.page.wait_for_selector('#quizout .card')
        prices = self.page.locator('#quizout .price').all_inner_texts()
        self.assertTrue(prices)
        self.assertTrue(all(float(p.split('$')[-1]) < 10 for p in prices), prices)
        self.assertIn('keeping your budget', self.page.locator('#quizout').inner_text())

    def test_gift_finder_empty_budget_and_catalog_failure(self):
        self.catalog_response = json.loads((self.dist / 'data/catalog.json').read_text())
        for item in self.catalog_response:
            item['p'] = 25
        self.visit('/gift-finder/')
        for name in ('q0', 'q1', 'q2'):
            self.page.check(f'input[name={name}][value="0"]')
        self.page.click('#quiz button[type=submit]')
        self.page.wait_for_selector('#quizout h2')
        self.assertEqual(self.page.locator('#quizout .card').count(), 0)
        self.assertIn('No gifts match that budget', self.page.locator('#quizout').inner_text())
        self.block_catalog = True
        self.visit('/shop/')
        self.page.wait_for_function('document.querySelector("#count").textContent.includes("could not load")')
        self.assertGreater(self.page.locator('#grid .card').count(), 0)
        self.assertTrue(self.page.locator('#q').is_disabled())

    def test_mobile_menu_and_cart_without_analytics(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.visit('/shop/')
        self.page.wait_for_function('document.querySelector("#count").textContent.includes("items")')
        self.page.evaluate('window.gtag=undefined')
        self.page.click('.menu')
        self.assertEqual(self.page.locator('.menu').get_attribute('aria-expanded'), 'true')
        self.page.click('.menu')
        self.page.locator('#grid [data-atc]').first.click()
        self.assertTrue(self.page.locator('#cart').is_visible())
        self.page.keyboard.press('Escape')
        self.page.wait_for_selector('#cart', state='hidden')
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_no_pickup_or_ranking_claims_without_data(self):
        with tempfile.TemporaryDirectory(prefix='jewelry-no-data-') as tmp:
            for name in ('scripts', 'site', 'src'):
                shutil.copytree(ROOT / name, Path(tmp) / name)
            write_data(Path(tmp) / 'data', pickup=False, ranking=False)
            subprocess.run(['python3', 'scripts/build.py', '--preview'], cwd=tmp, check=True, capture_output=True)
            home = (Path(tmp) / 'dist/index.html').read_text()
            visit = (Path(tmp) / 'dist/visit/index.html').read_text()
            self.assertNotIn('2 hours', home + visit)
            self.assertNotIn('Best sellers under $30', home)
            self.assertIn('Gift picks under $30', home)
            self.assertNotIn('googletagmanager.com', home)
            self.assertIn('noindex,nofollow', home)
            self.assertIn('Disallow: /', (Path(tmp) / 'dist/robots.txt').read_text())


if __name__ == '__main__':
    unittest.main()
