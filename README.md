# namastejewelrystore.com

Namaste Jewelry Store: static storefront built daily from the public namastebookshop.com catalog and deployed to GitHub Pages.
Namaste Jewelry Store is a brand of Wealth Edge Ventures Inc.

- `site/config.json`: site settings. Set `REVIEW_URL` (Google review link) to show the "Review us on Google" button and QR code; set `GOOGLE_SITE_VERIFICATION` to the Search Console HTML-tag value. Both stay hidden while empty. `kinds`, `max_price` and `best_collections` limit what the daily pickup and best-seller checks fetch.
- `site/sitecopy.py`: aisles, product mix rules and all copy for this site.
- `site/theme.css`, `site/favicon.svg`: this site's design.
- `scripts/`: shared jewelry/bead engine (fetch with pagination and 429 backoff, Shopify pickup check, best sellers, build).
- Checkout: the browser cart creates `namastebookshop.com/cart/<variant>:<quantity>,…` links with the existing `attributes[Storefront]`, `attributes[Site]`, `note`, and `ref` source markers. Verify their persistence on completed Shopify orders before treating them as measured sales.

## Local checks

Use Python 3.12+ and Node 22+:

```sh
python3 -m pip install -r tests/requirements.txt
python3 -m playwright install chromium
python3 -m unittest discover -s tests -v
```

Tests build a temporary copy using synthetic products, block external browser requests, and prevent checkout navigation. They do not change the real catalog or send analytics. Set `CHROMIUM_PATH` to use a specific browser; otherwise tests use system Chromium when available, then Playwright's installed browser. `.github/workflows/checks.yml` runs these checks for pull requests and manual checks without deploying.

Use `python3 scripts/build.py --preview` for a manual preview after obtaining the real public catalog with the existing fetch scripts. Preview mode suppresses GA4 and indexing. Do not publish synthetic test catalogs. The production workflow remains separate and deploys on `main` changes, its daily schedule, or an explicit manual run.

## Attribution and maintenance

The existing GA4 measurement ID is `G-Y7R5K9NMW0`. Keep one loader. `view_item`, `add_to_cart`, `begin_checkout`, and contact-link `generate_lead` events describe browser actions; they are not confirmed sales or bookings. The footer link to Namaste Bookshop includes `utm_source=namastejewelrystore.com`, `utm_medium=referral`, `utm_campaign=namaste_network`, and `utm_content=footer`, and sends a `storefront_referral` event through the same GA4 tag.

Before interpreting events as sales, verify their receipt in GA4 and source markers on actual Shopify orders.
