"""Synthetic catalog for isolated tests. Never upload this catalog to the store."""
import json
from pathlib import Path


def catalog():
    products = []

    def add(handle, title, price, variants=None, product_type='Pendant'):
        ident = 900000 + len(products)
        products.append({
            'id': ident, 'handle': handle, 'title': title, 'vendor': 'Test supplier',
            'product_type': product_type, 'body_html': '<p>Test fixture only.</p>',
            'created_at': '2026-01-01T00:00:00Z',
            'images': [{'src': f'https://example.invalid/{handle}.jpg'}],
            'variants': variants or [{'id': ident * 10, 'title': 'Default Title',
                                     'price': str(price), 'available': True, 'sku': handle,
                                     'compare_at_price': None}],
        })

    add('test-options', 'Amethyst Adjustable Ring Test Options', 7.99, [
        {'id': 910001, 'title': 'Small', 'price': '7.99', 'compare_at_price': '10.00', 'available': True, 'sku': 'TEST-S'},
        {'id': 910002, 'title': 'Large', 'price': '18.50', 'compare_at_price': None, 'available': True, 'sku': 'TEST-L'},
        {'id': 910003, 'title': 'Sold out option', 'price': '12.50', 'compare_at_price': None, 'available': False, 'sku': 'TEST-O'},
    ], 'Ring')
    for stone in ['Garnet', 'Amethyst', 'Aquamarine', 'Clear Quartz', 'Emerald', 'Moonstone',
                  'Ruby', 'Peridot', 'Sapphire', 'Opal', 'Citrine', 'Turquoise', 'Black Tourmaline']:
        for i in range(6):
            add(f'{stone.lower().replace(" ", "-")}-{i}', f'{stone} Heart Pendant Test {i}',
                [8.95, 12.95, 22.95][i % 3])
    add('rare-tanzanite', 'Tanzanite Pendant Test Rare Stone', 19.95)
    for i in range(4):
        add(f'expensive-earrings-{i}', f'Rose Quartz Heart Earrings Test {i}', 24.95, product_type='Earrings')
    add('evil-eye', 'Evil Eye Bracelet Test', 9.95, product_type='Bracelet')
    add('zodiac', 'Crescent Moon Pendant Test', 9.95)
    add('bracelet', 'Black Tourmaline 8mm Beaded Bracelet Test', 16.95, product_type='Crystal Bead Bracelets')
    return products


def write_data(root, *, pickup=True, ranking=True):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    products = catalog()
    (root / 'all_products.json').write_text(json.dumps(products))
    (root / 'pickup.json').write_text(json.dumps({str(p['variants'][0]['id']): {
        'available': True, 'location': 'Namaste Bookshop', 'ready': 'Usually ready in 2 hours'
    } for p in products} if pickup else {}))
    (root / 'bestsellers.json').write_text(json.dumps({p['handle']: i / len(products)
                                                    for i, p in enumerate(products)} if ranking else {}))
