"""Namaste Jewelry Store (namastejewelrystore.com): crystal jewelry gifts and best values under $30. All copy is written for this site only."""
import re, collections
from copybase import E, stone_color, intent_color, kinds_phrase, kind_one, plist, tradition, hood_list, HOODS as HOOD_DATA

AISLES = {
 'u10': ('Under $10', 'Under $10', 'under-10', 'Stocking stuffers, charms, cord pendants and add-ons for less than ten dollars.', '#2ec4b6'),
 'u20': ('$10 to $20', '$10 to $20', '10-to-20', 'Beaded bracelets, adjustable rings, earrings and pendants in the sweet spot.', '#ff7a59'),
 'u30': ('$20 to $30', '$20 to $30', '20-to-30', 'Bigger stones, sterling minis and gift-worthy pieces just under thirty.', '#7b5cd6'),
}
def assign(x):
    if x['base'] in ('meditation', 'beads') or x['price'] >= 30: return None
    return 'u10' if x['price'] < 10 else 'u20' if x['price'] < 20 else 'u30'
LABELS = {'stone': 'Stone', 'metal': 'Metal'}
PRICE_BANDS = [('0-5', 'Under $5'), ('0-10', 'Under $10'), ('0-15', 'Under $15'), ('0-20', 'Under $20'), ('20-30', '$20 to $30')]
BRAND_BANDS = [('Under $10', 0, 10), ('$10 to $20', 10, 20), ('$20 to $30', 20, 30)]
STONE_MIN = 6; INTENT_MIN = 6; NAV_INTENTS = True

VISIT_EYEBROW = 'Grab a gift on 14th Street'
def STORE_DESC(S): return f'Affordable crystal jewelry and gift shop by Union Square in Manhattan: about {S.ABOUT_N:,} rings, bracelets, pendants and earrings, all under $30.'
REVIEW_TITLE = 'Picked up a gift here?'
REVIEW_TEXT = 'Tell people what you found for under thirty dollars. Google reviews help other shoppers near Union Square find us.'
LOGO_SVG = '<svg viewBox="0 0 40 40"><rect x="10" y="9" width="20" height="22" rx="4" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="17" cy="15" r="2.6" fill="#ff7a59"/><path d="M14 25h12" stroke="#ff7a59" stroke-width="2.4" stroke-linecap="round"/></svg>'
WORDMARK = 'Namaste <b>Jewelry Store</b>'
BAR_TEXT = 'Everything under $30 at 2 West 14th Street'
SEARCH_PLACEHOLDER = 'Search gifts: evil eye, rose quartz, rings'

QUIZ = {
 'slug': 'gift-finder', 'nav': 'Gift finder', 'cta': 'Find a gift',
 'title': 'Crystal Jewelry Gift Finder Under $30', 'desc': 'Three questions and we suggest crystal jewelry gifts under $30 that are in stock at 2 West 14th Street near Union Square.',
 'h1': 'Gift finder', 'lead': 'Answer three quick questions and we will pull in-stock gifts. Nothing is stored; it all happens in your browser.', 'submit': 'Show gift ideas',
 'questions': [
  {'q': 'What do they like to wear?', 'options': [{'label': 'Bracelets', 'filter': {'base': ['beaded', 'bracelet']}}, {'label': 'Necklaces', 'filter': {'base': ['pendant', 'necklace', 'chain']}},
    {'label': 'Rings', 'filter': {'base': ['ring']}}, {'label': 'Earrings', 'filter': {'base': ['earrings']}}, {'label': 'Not sure', 'filter': {}}]},
  {'q': 'What is the occasion?', 'options': [{'label': 'Love or anniversary', 'filter': {'intent': ['love']}}, {'label': 'Good luck for a new start', 'filter': {'intent': ['abundance']}},
    {'label': 'Something protective', 'filter': {'intent': ['protection']}}, {'label': 'Just because', 'filter': {}}]},
  {'q': 'Spend up to', 'options': [{'label': '$10', 'filter': {'maxp': 10}}, {'label': '$20', 'filter': {'maxp': 20}}, {'label': '$30', 'filter': {'maxp': 30}}]},
 ]}
def FOOTER_EXPLORE(S):
    return [('Gift finder', '/gift-finder/'), ('Birthstone gifts', '/birthstones/'), ('Gifts under $10', '/shop/under-10/'), ('Evil eye gifts', '/gifts/evil-eye/'),
            ('Zodiac jewelry', '/gifts/zodiac/'), ('Stocking stuffers', '/gifts/stocking-stuffers/'), ('Shop by intention', '/intentions/'), ('Cheap jewelry in Manhattan', '/affordable-jewelry-manhattan/')]
FOOT_BLURB = 'Real-stone jewelry for gifting and treating yourself, all under thirty dollars, on 14th Street by Union Square.'
HERO_BASES = ('beaded', 'ring', 'pendant', 'earrings')
def HERO(S):
    return {'eyebrow': 'Everything under $30 &middot; 2 West 14th Street &middot; Union Square',
            'h1': 'Crystal jewelry gifts, <em>all under $30.</em>',
            'lede': f'{S.N:,} rings, bracelets, pendants and earrings with real stones, {S.UNDER10:,} under $10 and the rest under $30. Pick a gift online, then grab it on 14th Street on your way.' + (f' Pickup orders are {S.READY.lower()}.' if S.PICKUP_ON else ''),
            'shop_cta': 'Shop gifts'}
BIRTH = [('january', 'January', 'garnet', ['garnet']), ('february', 'February', 'amethyst', ['amethyst']), ('march', 'March', 'aquamarine', ['aquamarine', 'bloodstone']),
         ('april', 'April', 'diamond (try clear quartz or Herkimer diamond quartz)', ['clear-quartz', 'herkimer']), ('may', 'May', 'emerald', ['emerald', 'aventurine', 'jade']),
         ('june', 'June', 'pearl and moonstone', ['pearl', 'moonstone']), ('july', 'July', 'ruby', ['ruby', 'carnelian']), ('august', 'August', 'peridot', ['peridot']),
         ('september', 'September', 'sapphire', ['sapphire', 'lapis']), ('october', 'October', 'opal and tourmaline', ['opal', 'tourmaline', 'opalite']),
         ('november', 'November', 'topaz and citrine', ['topaz', 'citrine']), ('december', 'December', 'turquoise and tanzanite', ['turquoise', 'tanzanite'])]
def _birth(S):
    tiles = ''.join(f'<a class="scent" href="/birthstones/{k}/" style="--c:{stone_color(st[0])}"><b>{m}</b><span>{E(name.split(" (")[0].capitalize())}</span><small>{sum(1 for x in S.products if set(st) & set(x["stones"]))} gifts</small></a>' for k, m, name, st in BIRTH if any(set(st) & set(x['stones']) for x in S.products))
    return f'<section class="wrap"><div class="sechead"><h2>Birthstone gifts</h2><a href="/birthstones/">All months &rarr;</a></div><div class="scents">{tiles}</div></section>'
def _near(S): return f'<section class="wrap"><div class="sechead"><h2>On your way? Directions from</h2></div>{hood_list(S, "/near/")}</section>'
def _whys(S):
    return [('Nothing over $30', 'Every piece on this site is under thirty dollars, and the price on the card is the price.'),
            (f'{S.UNDER10:,} gifts under $10', 'Charms, cord pendants, adjustable rings and mini bracelets for stockings and goody bags.'),
            (('Pick up in about 2 hours', f'Order on your phone, choose Pickup and collect on 14th Street. Orders are {S.READY.lower()}.') if S.PICKUP_ON else ('', '')),
            ('Real stones', 'Amethyst, rose quartz, tiger\'s eye and dozens more, named on every listing.'),
            ('Open late on weekends', 'Until 9 PM Friday and Saturday for last-minute presents.'),
            ('Easy to find', 'On 14th Street at Fifth Avenue, steps from Union Square.')]
def _best(S): return S.by_rank(S.leaders)[:8]
def _u10(S): return S.by_rank([x for x in S.leaders if x['price'] < 10 and not x['noimg']])[:8]
def _sale(S): return S.by_rank([x for x in S.leaders if x['compare'] and not x['noimg']])[:8]
HOME_SECTIONS = [
 {'type': 'grid', 'title': 'Best sellers under $30', 'select': _best, 'href': '/shop/', 'link': 'All gifts', 'intro': 'Ranked by sales on namastebookshop.com and refreshed daily.'},
 {'type': 'collections', 'title': 'Gift guides', 'items': [
   {'title': 'Under $10', 'blurb': 'Stocking stuffers and add-ons.', 'href': '/shop/under-10/', 'filter': {'maxp': 10}},
   {'title': 'Evil eye gifts', 'blurb': 'Bracelets, rings and pendants.', 'href': '/gifts/evil-eye/', 'filter': {'style': ['Evil eye & hamsa']}},
   {'title': 'For someone you love', 'blurb': 'Rose quartz and hearts.', 'href': '/intentions/love/', 'filter': {'intent': ['love']}},
   {'title': 'Zodiac & celestial', 'blurb': 'Signs, moons and stars.', 'href': '/gifts/zodiac/', 'filter': {'style': ['Moon & celestial']}},
   {'title': 'Adjustable rings', 'blurb': 'No ring size needed.', 'href': '/gifts/adjustable-rings/', 'filter': {'base': ['ring'], 'q': 'adjustable'}},
   {'title': 'Bracelet stacks', 'blurb': 'Mix two or three.', 'href': '/gifts/bracelets/', 'filter': {'base': ['beaded']}}]},
 {'type': 'html', 'html': _birth},
 {'type': 'visit'},
 {'type': 'grid', 'title': 'Gifts under $10', 'select': _u10, 'href': '/shop/under-10/', 'link': 'See all under $10'},
 {'type': 'whys', 'title': 'Why gift from here', 'items': _whys},
 {'type': 'quiz', 'title': 'Stuck on a gift?', 'text': 'Three questions, a handful of real in-stock ideas.'},
 {'type': 'grid', 'title': 'Marked down', 'select': _sale, 'href': '/shop/', 'link': 'Shop all'},
 {'type': 'html', 'html': _near},
 {'type': 'brands', 'title': 'Brands under $30', 'n': 10},
 {'type': 'review'},
 {'type': 'band', 'title': 'Order now, grab it later', 'text': lambda S: 'Every listing shows its live price and stock. Reserve a gift and pick it up on 14th Street, or ship it from New York City.',
  'steps': lambda S: [('Choose a gift', 'Filter by stone, price, metal, style or brand.'), ('Pick Pickup at checkout', f'Pay securely on Shopify. {S.READY or "Ready the same day in most cases"}.'), ('Grab it', S.STORE_ADDR + '.')]},
]
def HOME_TITLE(S): return 'Namaste Jewelry Store | Crystal Jewelry Gifts Under $30 near Union Square NYC'
def HOME_DESC(S): return f'{S.N:,} crystal jewelry gifts under $30 at {S.STORE_ADDR}, by Union Square: beaded bracelets, adjustable rings, pendants, earrings and birthstone gifts. Pickup in about 2 hours.'
def SHOP_TITLE(S): return 'Shop Crystal Jewelry Under $30 | Namaste Jewelry Store NYC'
def SHOP_DESC(S): return f'Browse {S.N:,} affordable crystal jewelry gifts from {S.money(S.MIN_PRICE)}, all under $30. Pick up at 2 West 14th Street, Manhattan, or ship.'
SHOP_H1 = 'All gifts under $30'
def SHOP_SUB(S): return f'{S.N:,} pieces, sorted into three price aisles. Filter by stone, metal, style or brand.'
def AISLE_TITLE(S, k): return f'Crystal Jewelry {AISLES[k][0]} | Namaste Jewelry Store NYC'
def AISLE_DESC(S, k): return f'{AISLES[k][3]} {S.cat_count[k]} pieces at 2 West 14th Street near Union Square.'
ZOD = 'aries|taurus|gemini|cancer|\\bleo\\b|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces|zodiac'
def LANDINGS(S):
    L = [
     {'path': '/gifts/evil-eye/', 'title': 'Evil Eye Jewelry Gifts Under $30 | Namaste Jewelry Store NYC', 'desc': 'Evil eye and hamsa bracelets, rings, pendants and earrings under $30 at 2 West 14th Street.', 'h1': 'Evil eye gifts', 'sub': 'A folk symbol many people give for good wishes and protection.', 'filter': {'style': ['Evil eye & hamsa']}},
     {'path': '/gifts/zodiac/', 'title': 'Zodiac & Celestial Jewelry Gifts | Namaste Jewelry Store NYC', 'desc': 'Zodiac, moon and star jewelry gifts under $30 near Union Square.', 'h1': 'Zodiac & celestial gifts', 'sub': 'Star signs, crescents and constellations.', 'filter': {'style': ['Moon & celestial']}},
     {'path': '/gifts/adjustable-rings/', 'title': 'Adjustable Crystal Rings Under $30 | Namaste Jewelry Store', 'desc': 'Adjustable gemstone rings that fit most fingers, great for gifts when you do not know a size.', 'h1': 'Adjustable rings', 'sub': 'No ring size needed.', 'filter': {'base': ['ring'], 'q': 'adjustable'}},
     {'path': '/gifts/bracelets/', 'title': 'Beaded Crystal Bracelet Gifts Under $30 | Namaste Jewelry Store', 'desc': 'Stretch beaded crystal bracelets under $30, perfect for stacking and gifting.', 'h1': 'Bracelet gifts', 'sub': 'Stretch bracelets that fit most wrists.', 'filter': {'base': ['beaded']}},
     {'path': '/gifts/stocking-stuffers/', 'title': 'Crystal Jewelry Stocking Stuffers Under $10 | Namaste Jewelry Store', 'desc': 'Crystal charms, cord pendants and small gifts under $10 at 2 West 14th Street.', 'h1': 'Stocking stuffers', 'sub': 'Small, real-stone gifts under $10.', 'filter': {'maxp': 10}},
     {'path': '/gifts/for-her/', 'title': 'Crystal Jewelry Gifts for Her Under $30 | Namaste Jewelry Store', 'desc': 'Rose quartz, moonstone, amethyst and heart jewelry gifts under $30 near Union Square.', 'h1': 'Gifts for her', 'sub': 'Hearts, florals and soft-colored stones.', 'filter': {'q': 'heart|flower|butterfly|rose quartz|moonstone|pearl|amethyst'}},
     {'path': '/gifts/for-him/', 'title': 'Crystal Jewelry Gifts for Him Under $30 | Namaste Jewelry Store', 'desc': 'Tiger eye, onyx, lava, hematite and copper jewelry gifts under $30 at 2 West 14th Street.', 'h1': 'Gifts for him', 'sub': 'Darker stones, copper and leather.', 'filter': {'q': "tiger.?s? ?eye|onyx|lava|hematite|obsidian|copper|leather|black tourmaline|stainless"}},
     {'path': '/birthstones/', 'title': 'Birthstone Jewelry Gifts by Month Under $30 | Namaste Jewelry Store', 'desc': 'Birthstone gifts for every month under $30, from garnet to turquoise, at 2 West 14th Street.', 'h1': 'Birthstone gifts by month', 'sub': 'Modern birthstones, plus popular alternatives.',
      'filter': {'stone': sorted({s for _, _, _, st in BIRTH for s in st})}, 'intro': '<p class="intro">' + ' &middot; '.join(f'<a href="/birthstones/{k}/">{m}</a>' for k, m, _, _ in BIRTH) + '</p>'},
    ]
    for k, m, name, st in BIRTH:
        L.append({'path': f'/birthstones/{k}/', 'title': f'{m} Birthstone Jewelry Gifts Under $30 | Namaste Jewelry Store', 'desc': f'{m} birthstone gifts: {name.split(" (")[0]} jewelry under $30 at 2 West 14th Street near Union Square.',
                  'h1': f'{m} birthstone gifts', 'sub': f'The {m} birthstone is {name}.', 'filter': {'stone': st}})
    return L

def stone_tile(S, k): return f'From {S.money(min(x["price"] for x in S.products if k in x["stones"]))}'
def STONE_PAGE(S, k, xs):
    n = S.STONE_NAME[k]; tr = tradition(S, k); lo = min(x['price'] for x in xs); u10 = sum(1 for x in xs if x['price'] < 10)
    return {'title': f'{n} Jewelry Gifts Under $30 | Namaste Jewelry Store NYC', 'desc': f'{len(xs)} {n.lower()} gifts from {S.money(lo)}, all under $30, at 2 West 14th Street by Union Square.',
            'h1': f'{n} gifts under $30', 'sub': f'{len(xs)} pieces from {S.money(lo)}' + (f', {u10} under $10' if u10 else ''),
            'intro': (f'<p class="note-belief">Gift note: many people give {E(n.lower())} for {plist(tr)}, following crystal tradition. It is a sweet sentiment, not a proven effect.</p>' if tr else ''),
            'faq': [(f'What is the cheapest {n.lower()} jewelry you have?', f'Right now {n.lower()} starts at {S.money(lo)}.'), (f'Can I pick up {n.lower()} jewelry today?', f'Order online and choose Pickup; orders are {S.READY.lower() or "usually ready the same day"}. We are at {S.STORE_ADDR}.')], 'faq_title': 'Quick answers'}
def intent_tile(S, k): return f'{S.intent_count[k]} gifts'
def INTENT_PAGE(S, k, xs):
    n = S.INTENT_NAME[k]; lo = min(x['price'] for x in xs)
    return {'title': f'{n} Crystal Jewelry Gifts Under $30 | Namaste Jewelry Store', 'desc': f'{len(xs)} crystal jewelry gifts for {n.lower()} under $30, at 2 West 14th Street, NYC.',
            'h1': f'Gifts for {n.lower()}', 'sub': f'{len(xs)} pieces from {S.money(lo)}', 'intro': '<p class="note-belief">The stones here are the ones crystal traditions connect with this wish. A lovely meaning to share with a gift, but tradition, not science.</p>',
            'faq': [(f'Is this a good gift for {n.lower()}?', 'Many people choose these stones for the meaning tradition gives them. Pair the gift with a note; it is the thought that counts.')]}
def STONES_HUB(S): return {'title': 'Crystal Jewelry Gifts by Stone | Namaste Jewelry Store', 'desc': 'Shop affordable crystal jewelry gifts by stone, all under $30.', 'h1': 'Gifts by stone', 'lead': 'Pick a stone, then pick a price. Everything is under $30.'}
def INTENTS_HUB(S): return {'title': 'Crystal Jewelry Gifts by Intention | Namaste Jewelry Store', 'desc': 'Gifts grouped by the wish behind them: love, luck, protection, calm and more, under $30.', 'h1': 'Gifts by intention', 'lead': 'Grouped by the meanings crystal traditions give each stone, shared as tradition only.'}

def brand_intro(S, k, st):
    name = S.BRAND_NAME[k]; xs = st['xs']
    return f'<p>{st["n"]} {E(name)} gift{"s" if st["n"] != 1 else ""} under $30: {kinds_phrase(S.kinds_of(xs))}, starting at {S.money(st["min"])}.' + (' Order for pickup on 14th Street.' if st['pickup'] else '') + '</p>'
def brand_faq(S, k, st):
    name = S.BRAND_NAME[k]
    return [(f'Where can I buy {name} jewelry near Union Square?', f'Namaste Jewelry Store, {S.STORE_ADDR}. {st["n"]} pieces under $30 today.')]
def BRAND_H1(S, k): return f'{S.BRAND_NAME[k]} under $30'
def BRAND_TITLE(S, k, st): return f'{S.BRAND_NAME[k]} Jewelry Under $30 | Namaste Jewelry Store NYC'
def BRAND_DESC(S, k, st): return f'{st["n"]} {S.BRAND_NAME[k]} jewelry gifts from {S.money(st["min"])}, all under $30, at 2 West 14th Street.'
def BRANDS_TITLE(S): return 'Jewelry Brands Under $30 A to Z | Namaste Jewelry Store'
def BRANDS_DESC(S): return 'Named jewelry brands with gifts under $30 at Namaste Jewelry Store, 2 West 14th Street.'
BRANDS_H1 = 'Brands A to Z'
def BRANDS_LEAD(S, n): return f'{n} named brands with pieces under $30. Most of our value jewelry comes from independent suppliers and is easiest to browse <a href="/stones/">by stone</a> or <a href="/shop/">by price</a>.'
PAIR = {'beaded': ['beaded', 'ring'], 'ring': ['beaded'], 'pendant': ['earrings', 'chain'], 'earrings': ['pendant'], 'necklace': ['earrings'], 'bracelet': ['ring'], 'chain': ['pendant'], 'anklet': ['beaded'], 'charm': ['chain'], 'mala': ['beaded']}
REL_BRAND = 'More {brand} under $30'
REL_SCENT = 'More {scent} gifts'
REL_PAIR = 'Add a second gift'
REL_MORE = 'More gifts {aisle}'
def describe(S, x):
    k = x['base']; stn = x['stones']
    s = [f"Gift idea: {E(x['title'])}, a {kind_one(k)}" + (f" with {E(plist([S.STONE_NAME[t] for t in stn[:2]]).lower())}" if stn else '') + (f" ({x['metal'].lower()})" if x['metal'] and x['metal'] != 'Cord, elastic & leather' else '') + f" for {S.money(x['price'])}."]
    if k == 'ring' and re.search('adjustable', x['title'], re.I): s.append('It adjusts to fit most fingers, so you do not need to know a ring size.')
    elif x['size']: s.append(f'Ring size {E(x["size"])}.')
    if k == 'beaded': s.append('Stretch bracelets fit most adult wrists; roll it on rather than pulling.')
    if stn and stn[0] not in S.NON_STONE and tradition(S, stn[0]): s.append(f'Write it in the card: crystal tradition ties {E(S.STONE_NAME[stn[0]].lower())} to {plist(tradition(S, stn[0]))}. A meaning, not a medical claim.')
    s.append('Natural stones vary, so every piece is a little one-of-a-kind.')
    s.append('Pick it up at 2 West 14th Street by Union Square or have it shipped from NYC; checkout is on Shopify through namastebookshop.com.')
    return s
def PRODUCT_DESC(S, x, v0): return f"{x['title']}: a {S.money(v0['price'])} crystal jewelry gift. " + ('Pick up at 2 West 14th Street by Union Square or ship.' if x['pickup'] else 'At 2 West 14th Street, NYC.')
def ABOUT_DESC(S): return 'About Namaste Jewelry Store, the under-$30 crystal jewelry gift shop at 2 West 14th Street by Union Square. A brand of Wealth Edge Ventures Inc.'
ABOUT_H1 = 'About Namaste Jewelry Store'
def ABOUT(S):
    return f'''<p class="lead">Namaste Jewelry Store is the value side of our jewelry counter at {S.STORE_ADDR}: real-stone jewelry where nothing costs $30 or more.</p>
<p>We built this site for gift shopping. {S.N:,} pieces are sorted by price first, then by stone, birthstone and occasion, with live prices and stock.{" Order online and pick it up in store on your way." if S.PICKUP_ON else ""}</p>
<h2>Find us</h2><p>{S.STORE_ADDR}. Call <a href="tel:{S.TEL}">{S.PHONE}</a>.</p>{S.hours_html()}{S.visit_buttons()}
<h2>Who we are</h2><p>{S.LEGAL} Checkout and fulfillment run on Shopify through <a href="{S.SHOP}" rel="noopener">namastebookshop.com</a>.</p>
<h2>Stone meanings</h2><p>We mention the meanings crystal traditions give to stones because they make gifts personal. They are traditions, not promises.</p>'''
VISIT_TITLE = 'Visit Our Gift Shop near Union Square'
def VISIT_DESC(S): return f'Hours, directions and gift pickup for Namaste Jewelry Store at {S.STORE_ADDR}, by Union Square.'
def VISIT_LEAD(S): return f'Grab your gift at {S.STORE_ADDR}, on 14th Street just west of Fifth Avenue.'
def FAQ_DESC(S): return 'Gift shopping answers: prices, pickup timing, ring sizes, gift ideas and returns at Namaste Jewelry Store.'
FAQ_H1 = 'Gift shopping questions'
def FAQ(S):
    return [('Is everything really under $30?', 'Yes. This site only lists pieces under $30. Prices update every day.'),
            ('How fast can I pick up a gift?', 'Choose Pickup at checkout.' + (f' Orders are {S.READY.lower()}.' if S.READY else '') + f' We are at {S.STORE_ADDR}.'),
            ('I do not know their ring size. What should I get?', 'Try an <a href="/gifts/adjustable-rings/">adjustable ring</a> or a stretch <a href="/gifts/bracelets/">bracelet</a>.'),
            ('What is their birthstone?', 'See <a href="/birthstones/">birthstone gifts by month</a>, with popular alternatives for pricey stones.'),
            ('Are these real stones?', 'Listings name the stone as our suppliers describe it. Some favorites, like goldstone and opalite, are man-made glass by nature.'),
            ('Can I return a gift?', f'Returns follow the store refund policy; see <a href="/returns/">returns</a>.'),
            ('When are you open?', 'Daily from 11 AM: until 8 PM Monday to Thursday, 9 PM Friday and Saturday, and 7 PM Sunday.')]
def GUIDES(S):
    return [{'path': '/affordable-jewelry-manhattan/', 'title': 'Affordable Crystal Jewelry in Manhattan near Union Square', 'store_ld': True,
             'desc': f'Cheap crystal jewelry gifts in Manhattan: {S.N:,} pieces under $30 at {S.STORE_ADDR}, by Union Square.', 'h1': 'Affordable jewelry gifts in Manhattan',
             'html': f'<p class="lead">Need a real-stone gift without spending much? {S.N:,} pieces, all under $30, {S.UNDER10:,} under $10, on 14th Street at Fifth Avenue.</p><h2>Gift ideas</h2><ul><li><a href="/birthstones/">Birthstone gifts</a></li><li><a href="/gifts/evil-eye/">Evil eye</a></li><li><a href="/gifts/stocking-stuffers/">Stocking stuffers</a></li><li><a href="/gift-finder/">Gift finder quiz</a></li></ul><h2>Directions</h2>{hood_list(S, "/near/")}{S.visit_block()}'}]
HOOD_LINE = {'union-square': 'Running late for a party near Union Square? The gift shelf is a 4-minute walk.', 'east-village': 'Heading to a birthday in the East Village? Order now, grab it on 14th Street.',
             'chelsea': 'From Chelsea Market, walk east on 14th Street for a quick gift.', 'flatiron': 'Office gift exchange in Flatiron? Most pieces are under $20.',
             'greenwich-village': 'Near NYU and Washington Square, a gift under $30 is a short walk up Fifth.', 'midtown': 'From Midtown, a short ride down for gifts that do not cost much.'}
def HOODS(S):
    picks = S.by_rank([x for x in S.leaders if not x['noimg'] and x['price'] < 20])[:8]
    return [{'path': f'/near/{k}/', 'title': f'Jewelry Gifts Under $30 near {n} | Namaste Jewelry Store', 'h1': f'Gifts under $30 near {n}',
             'desc': f'Affordable crystal jewelry gifts near {n}: {S.N:,} pieces under $30 at {S.STORE_ADDR}. Pickup in about 2 hours.',
             'html': f'<p class="lead">{E(HOOD_LINE[k])}</p><h2>How to get here from {E(n)}</h2><p>{E(route)}</p><h2>Popular gifts under $20</h2>{S.grid(picks)}{S.visit_block()}<h2>Other neighborhoods</h2>{hood_list(S, "/near/", k)}'}
            for k, n, route in HOOD_DATA]
NOT_FOUND = 'That gift has been snapped up'
