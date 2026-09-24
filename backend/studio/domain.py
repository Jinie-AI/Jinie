from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PAGES = ['home', 'products', 'detail', 'cart', 'checkout', 'contact', 'about', 'search', 'settings', 'profile']
BUSINESSES = {
 'clothing': ['clothing', 'fashion', 'kapray', 'kapre', 'کپڑے', 'boutique'],
 'food': ['food', 'restaurant', 'khana', 'کھانا', 'burger', 'biryani'],
 'flowers': ['flower', 'flowers', 'floral', 'bouquet', 'rose', 'roses', 'florist', 'blooms', 'phool'],
 'electronics': ['electronics', 'gadgets', 'laptop', 'الیکٹرانکس'],
 'accessories': ['accessories', 'bags', 'belts'],
 'furniture': ['furniture', 'sofa', 'فرنیچر'],
 'beauty': ['beauty', 'makeup', 'cosmetics', 'salon'],
 'books': ['books', 'bookshop', 'کتاب', 'kitab'],
 'repair': ['repair', 'مرمت'],
 'jewellery': ['jewellery', 'jewelry', 'زیورات'],
 'services': ['services', 'barber', 'booking', 'خدمات'],
}
FEATURES = ['catalog', 'cart', 'checkout', 'search', 'contact', 'about', 'settings', 'profile']
STYLES = ['minimal', 'luxury', 'playful']
LABELS = [f'business:{x}' for x in BUSINESSES] + [f'page:{x}' for x in PAGES] + [f'feature:{x}' for x in FEATURES] + [f'style:{x}' for x in STYLES]
CATALOG = ['ProductCard', 'HeroBanner', 'CategoryChip', 'SearchBar', 'CartItem', 'CheckoutButton', 'PriceTag', 'DiscountBadge', 'RatingStars', 'SectionHeading', 'EmptyState', 'ContactCard', 'AboutCard', 'QuantityControl', 'OrderSummary', 'AddressField', 'NavigationTab', 'StockBadge', 'ServiceCard', 'Divider']

DOMAIN_REQUIREMENTS = {
    'food': {
        'home': 'Showcase dining highlights, chef specials, daily deals, and quick-order categories.',
        'products': 'Browse menu items, combos, and beverages with dietary and spice level filters.',
        'detail': 'Display meal ingredients, portion sizes, calories, and special cooking instructions.',
        'cart': 'Review order basket, add extra sauces/sides, and see delivery fee estimate.',
        'checkout': 'Verify delivery address, phone number, and confirm Cash on Delivery order.',
        'search': 'Fast search across dishes, ingredients, and combo meals.',
        'contact': 'Restaurant hotline, branch locations, and kitchen operating hours.',
        'about': 'Our culinary story, fresh local ingredient pledge, and head chef introduction.'
    },
    'clothing': {
        'home': 'Display curated seasonal lookbook, editorial banner, and trending new arrivals.',
        'products': 'Browse fashion collections with category chips, size tags, and price sorting.',
        'detail': 'Inspect high-res garment photography, fabric composition, size chart, and fit notes.',
        'cart': 'Manage shopping bag, view item quantities, subtotal, and complimentary packaging.',
        'checkout': 'Enter shipping destination, contact details, and complete COD purchase.',
        'search': 'Search apparel by style name, color, collection, or fabric.',
        'contact': 'Customer care concierge, stylist assistance, and exchange inquiries.',
        'about': 'The brand aesthetic, sustainable fabric commitment, and craftsmanship roots.'
    },
    'electronics': {
        'home': 'Feature tech launches, best-selling gadgets, and limited-time warranty deals.',
        'products': 'Explore electronics catalog categorized by devices, specs, and performance ratings.',
        'detail': 'Deep-dive technical specifications, compatibility notes, and customer reviews.',
        'cart': 'Manage hardware cart, review warranty add-ons, and calculate order total.',
        'checkout': 'Confirm courier delivery address and cash-on-delivery payment details.',
        'search': 'Filter gadgets by model, brand, chipset, or price bracket.',
        'contact': 'Technical support desk, warranty verification, and repair inquiries.',
        'about': 'Our authorized hardware guarantee and dedication to authentic gear.'
    },
    'furniture': {
        'home': 'Showcase interior inspiration rooms, modern living sets, and designer collections.',
        'products': 'Browse furniture pieces by room type, wood finish, and dimensions.',
        'detail': 'Examine wood materials, upholstery care, weight capacities, and room fit tips.',
        'cart': 'Review selected furniture items, delivery scheduling info, and total.',
        'checkout': 'Provide delivery address for white-glove courier drop-off with COD.',
        'search': 'Search pieces by room, material, color, or designer collection.',
        'contact': 'Design consultation desk and delivery coordination team.',
        'about': 'Artisan joinery tradition, ethically sourced timber, and durable living ethos.'
    },
    'beauty': {
        'home': 'Highlight radiant skincare routines, dermatological essentials, and top-rated picks.',
        'products': 'Explore beauty essentials filtered by skin concern, finish, and routine step.',
        'detail': 'Inspect active ingredients, clean beauty certifications, and usage instructions.',
        'cart': 'Review cosmetic bag, complimentary sample selection, and subtotal.',
        'checkout': 'Confirm discreet delivery address and cash-on-delivery checkout.',
        'search': 'Find products by skin type, scent, or active ingredient formula.',
        'contact': 'Beauty advisor chat, regimen consultations, and customer support.',
        'about': 'Cruelty-free pledge, clean botanical formulation, and dermatological integrity.'
    },
    'books': {
        'home': 'Curated reading list, staff recommendations, and bestsellers of the month.',
        'products': 'Browse bookstore library by genre, author, and binding format.',
        'detail': 'Read book synopsis, author biography, page count, and reader reviews.',
        'cart': 'Review book bag, bookmark gifts, and total order sum.',
        'checkout': 'Confirm doorstep delivery address and cash-on-delivery payment.',
        'search': 'Search titles, authors, genres, or ISBN numbers.',
        'contact': 'Book club inquiries, bulk orders, and customer service.',
        'about': 'Independent literary mission and passion for print culture.'
    },
    'services': {
        'home': 'Highlight professional services, service packages, and certified staff credentials.',
        'products': 'Browse service menu with duration estimates, pricing, and category filters.',
        'detail': 'Inspect service scope, preparation guidelines, and customer satisfaction ratings.',
        'cart': 'Review selected service appointments and estimate total.',
        'checkout': 'Provide appointment location/address and local demo confirmation.',
        'search': 'Search available services and specialists.',
        'contact': 'Front desk bookings, custom package quotes, and direct assistance.',
        'about': 'Our licensed professional team, quality standard, and customer promise.',
        'settings': 'Configure service reminder notifications, booking preferences, and theme.',
        'profile': 'Manage appointments history, member loyalty points, and client details.'
    },
    'flowers': {
        'home': 'Showcase fresh seasonal bouquets, floral arrangements, and daily bloom specials.',
        'products': 'Browse flower collections by occasion, flower type (roses, lilies, tulips), and stem count.',
        'detail': 'Inspect bloom freshness, vase recommendations, floral scents, and care guidelines.',
        'cart': 'Review floral arrangement, add greeting card message, and choose delivery date.',
        'checkout': 'Confirm recipient doorstep delivery address and cash-on-delivery payment.',
        'search': 'Search bouquets by flower variety, occasion, or color palette.',
        'contact': 'Florist consultation desk, wedding arrangement quotes, and custom inquiries.',
        'about': 'Our artisanal floral studio, ethical farm sourcing, and bloom freshness guarantee.',
        'settings': 'Notification preferences, delivery reminders, and appearance settings.',
        'profile': 'Saved addresses, occasion reminders, and past floral orders.'
    }
}

def extract(prompt):
    text = prompt.casefold()
    scores = {k: sum(w in text for w in words) for k, words in BUSINESSES.items()}
    business = max(scores, key=scores.get) if max(scores.values()) else 'clothing'
    
    # Autonomous baseline: complete commerce flow for the domain
    pages = ['home', 'products', 'detail', 'cart', 'checkout']
    
    # Detect positive triggers for optional/additional screens
    if any(w in text for w in ['contact', 'رابطہ', 'rabta', 'support', 'help', 'call', 'reach']):
        if 'contact' not in pages: pages.append('contact')
    if any(w in text for w in ['about', 'ہمارے', 'hamare', 'story', 'mission', 'about us']):
        if 'about' not in pages: pages.append('about')
    if any(w in text for w in ['search', 'find', 'تلاش', 'dhoond', 'filter']):
        if 'search' not in pages: pages.append('search')
    if any(w in text for w in ['setting', 'settings', 'preference', 'preferences']):
        if 'settings' not in pages: pages.append('settings')
    if any(w in text for w in ['profile', 'account', 'user profile', 'my profile']):
        if 'profile' not in pages: pages.append('profile')
        
    # Check explicit positive inclusion of product screen
    if any(w in text for w in ['product screen', 'products screen', 'catalog screen', 'shop screen', 'menu screen']):
        if 'products' not in pages: pages.insert(1, 'products')
        if 'detail' not in pages: pages.insert(2, 'detail')
        
    # STRICT NEGATIVE EXCLUSIONS:
    neg_patterns = [
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?cart', 'cart'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?checkout', 'checkout'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?(?:products|product|catalog|shop|menu)', 'products'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?detail', 'detail'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?search', 'search'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?contact', 'contact'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?about', 'about'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?settings', 'settings'),
        (r'(?:no|without|not\s+need|exclude|don\'?t\s+want|omit|remove)\s+(?:a\s+|the\s+)?(?:profile|user\s+profile|account)', 'profile'),
    ]
    
    excluded = set()
    for pattern, page in neg_patterns:
        if re.search(pattern, text):
            excluded.add(page)
            
    # If cart is excluded, also exclude checkout
    if 'cart' in excluded:
        excluded.add('checkout')
    # If products is excluded and not specifically forced, also exclude detail
    if 'products' in excluded and 'detail' not in text:
        excluded.add('detail')
        
    pages = [p for p in pages if p not in excluded]
    if not pages:
        pages = ['home']
        
    style = next((s for s in STYLES if s in text), 'minimal')
    
    domain_reqs = DOMAIN_REQUIREMENTS.get(business, DOMAIN_REQUIREMENTS['clothing'])
    page_reqs = {p: domain_reqs.get(p, f'Provide the {p} screen tailored to {business}.') for p in pages}
    
    warnings = []
    if not max(scores.values()):
        warnings.append('Business category was inferred from your brief.')
        
    return {
        'business': business,
        'pages': [p for p in PAGES if p in pages],
        'page_requirements': page_reqs,
        'features': (['catalog'] if any(x in pages for x in ['home', 'products', 'detail']) else []) + [p for p in pages if p in FEATURES and p != 'catalog'],
        'style': style,
        'source': 'rules',
        'confidence': None,
        'warnings': warnings
    }

PRODUCTS = {
 'clothing':[
   ('Everyday linen shirt',2490,'👕','https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80','Best Seller',4.9),
   ('Classic overshirt',3990,'🧥','https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80','New Arrival',4.8),
   ('Relaxed cotton tee',1490,'👚','https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80','Trending',4.7),
   ('Weekend essentials',2990,'👖','https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80','20% OFF',4.9),
 ],
 'food':[
   ('Signature burger',790,'🍔','https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80','Chef Special',4.9),
   ('Fresh garden bowl',590,'🥗','https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80','Healthy',4.7),
   ('Chicken biryani',490,'🍛','https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80','Popular',5.0),
   ('Classic pizza',1290,'🍕','https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80','Wood-Fired',4.8),
 ],
 'electronics':[
   ('Wireless headphones',7990,'🎧','https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80','Noise Cancelling',4.9),
   ('Smart watch',9990,'⌚','https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80','OLED Display',4.8),
   ('Portable speaker',4490,'🔊','https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format&fit=crop&q=80','Waterproof',4.7),
   ('Mechanical keyboard',6490,'⌨️','https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80','RGB Backlit',4.9),
 ],
 'books':[
   ('The design collection',1890,'📚','https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80','Hardcover',4.9),
   ('Learning to build',1490,'📘','https://images.unsplash.com/photo-1532012164546-f432f2e3777a?w=600&auto=format&fit=crop&q=80','Bestseller',4.8),
   ('Creative thinking',990,'📙','https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&auto=format&fit=crop&q=80','Staff Pick',4.7),
   ('Stories of tomorrow',1290,'📗','https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80','New Edition',4.8),
 ],
 'beauty':[
   ('Daily essentials',1990,'🧴','https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80','Hydrating',4.8),
   ('Glow collection',2990,'✨','https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&auto=format&fit=crop&q=80','Vitamin C',4.9),
   ('Natural care',1490,'🌿','https://images.unsplash.com/photo-1608248597359-2ffb299e525a?w=600&auto=format&fit=crop&q=80','Organic',4.7),
   ('Signature fragrance',4990,'🌸','https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&auto=format&fit=crop&q=80','Luxury',5.0),
 ],
 'furniture':[
   ('Velvet accent chair',14990,'🪑','https://images.unsplash.com/photo-1580481077195-c5793e25b849?w=600&auto=format&fit=crop&q=80','Nordic Design',4.9),
   ('Minimal desk lamp',3490,'💡','https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80','Warm Light',4.8),
   ('Comfort lounge sofa',38900,'🛋️','https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=80','Handcrafted',4.9),
   ('Solid wood table',18900,'🪵','https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=600&auto=format&fit=crop&q=80','Oak Finish',4.8),
 ],
 'flowers':[
   ('Elysian Rose Bouquet',3490,'🌹','https://images.unsplash.com/photo-1561181286-d3fee7d55364?w=600&auto=format&fit=crop&q=80','Best Seller',4.9),
   ('Wildflower Pastel Mix',2890,'🌸','https://images.unsplash.com/photo-1526047932273-341f2a7631f9?w=600&auto=format&fit=crop&q=80','New Arrival',4.8),
   ('Sunlit Orchid Harmony',4290,'🌺','https://images.unsplash.com/photo-1508610048659-a06b669e3321?w=600&auto=format&fit=crop&q=80','Premium',5.0),
   ('Vintage Peony Bloom',3190,'💐','https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=600&auto=format&fit=crop&q=80','Seasonal',4.9),
 ],
}
def products(business):
    default_img = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80'
    rows = PRODUCTS.get(business, [
        (f'{business.title()} essential', 1990, '✦', default_img, 'Featured', 4.8),
        ('Signature collection', 3490, '◈', default_img, 'Premium', 4.9),
        ('Everyday favourite', 1490, '✺', default_img, 'Popular', 4.7),
        ('Premium selection', 4990, '❖', default_img, 'Top Rated', 5.0),
    ])
    return [
        dict(
            id=str(i+1),
            name=row[0],
            price=row[1],
            icon=row[2],
            image_url=row[3] if len(row) > 3 else default_img,
            badge=row[4] if len(row) > 4 else ('Featured' if i % 2 else ''),
            rating=row[5] if len(row) > 5 else 4.8,
            category='Featured' if i % 2 else 'Essentials',
            description=f'Thoughtfully selected {row[0].lower()} for your everyday. Premium craftsmanship and durable quality.'
        )
        for i, row in enumerate(rows)
    ]
