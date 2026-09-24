
export interface ScreenConfigData {
  title?: string;
  subtitle?: string;
  layout?: 'grid' | 'cards' | 'editorial' | 'compact';
  show_hero?: boolean;
  show_search?: boolean;
  show_badges?: boolean;
}

export interface HtmlScreenMockupProps {
  page: string;
  screenConfig?: ScreenConfigData;
  projectName: string;
  business: string;
  products?: Array<{
    id: string;
    name: string;
    price: number;
    image_url?: string;
    icon?: string;
    badge?: string;
    rating?: number;
    category?: string;
    description?: string;
  }>;
  primaryColor?: string;
  accentColor?: string;
  secondaryColor?: string;
  pages?: string[];
  onSelectScreen?: (page: string) => void;
  scale?: number;
}

export default function HtmlScreenMockup({
  page,
  screenConfig = {},
  projectName,
  business,
  products = [],
  primaryColor = '#7c5ce0',
  accentColor = '#b98849',
  secondaryColor = '#ede5f7',
  pages = ['home', 'products', 'detail', 'cart', 'checkout'],
  onSelectScreen,
  scale = 1,
}: HtmlScreenMockupProps) {
  const currentLayout = screenConfig.layout || 'grid';
  const showHero = screenConfig.show_hero !== false;
  const showSearch = screenConfig.show_search !== false;
  const showBadges = screenConfig.show_badges !== false;

  const demoProducts = products.length > 0 ? products : [
    {
      id: '1',
      name: `${business.charAt(0).toUpperCase() + business.slice(1)} Signature`,
      price: 2490,
      image_url: 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80',
      badge: 'Best Seller',
      rating: 4.9,
      category: 'Featured',
      description: 'Handcrafted with meticulous attention to detail and premium materials.',
    },
    {
      id: '2',
      name: 'Curated Classic',
      price: 3990,
      image_url: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80',
      badge: 'New Arrival',
      rating: 4.8,
      category: 'Essentials',
      description: 'An elevated daily favorite designed for effortless everyday style.',
    },
    {
      id: '3',
      name: 'Weekend Edition',
      price: 1890,
      image_url: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80',
      badge: 'Trending',
      rating: 4.7,
      category: 'Featured',
      description: 'Comfortable, versatile, and thoughtfully crafted for modern living.',
    },
    {
      id: '4',
      name: 'Prime Selection',
      price: 4990,
      image_url: 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80',
      badge: '20% OFF',
      rating: 5.0,
      category: 'Essentials',
      description: 'Our top-rated offering made with authentic craftsmanship.',
    },
  ];

  const selectedProduct = demoProducts[0];
  const navPages = pages.filter((p) => p !== 'detail' && p !== 'checkout');

  return (
    <div
      style={{
        width: 320,
        height: 640,
        borderRadius: 40,
        background: '#12101b',
        border: '10px solid #1c1928',
        boxShadow: '0 25px 60px rgba(18, 16, 27, 0.45), inset 0 0 0 1px rgba(255,255,255,0.1)',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        userSelect: 'none',
        transform: scale !== 1 ? `scale(${scale})` : undefined,
        transformOrigin: 'top center',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      {/* Dynamic Island & Status Bar */}
      <div
        style={{
          padding: '10px 18px 6px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#fcfaf7',
          borderBottom: '1px solid rgba(0,0,0,0.05)',
          zIndex: 10,
        }}
      >
        <span style={{ fontSize: 11, fontWeight: 700, color: '#1a1824' }}>9:41</span>
        <div
          style={{
            width: 72,
            height: 16,
            borderRadius: 20,
            background: '#090710',
            boxShadow: 'inset 0 1px 2px rgba(255,255,255,0.2)',
          }}
        />
        <span style={{ fontSize: 10, fontWeight: 600, color: '#686278' }}>5G 􀛨</span>
      </div>

      {/* App Header */}
      <div
        style={{
          padding: '12px 18px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#fcfaf7',
          borderBottom: '1px solid rgba(0,0,0,0.04)',
        }}
      >
        <div>
          <div style={{ fontSize: 8, letterSpacing: 1.5, fontWeight: 800, color: primaryColor, textTransform: 'uppercase' }}>
            Curated For You
          </div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824', letterSpacing: -0.5 }}>
            {projectName || 'Jinie App'}
          </div>
        </div>
        {pages.includes('cart') && (
          <div
            onClick={() => onSelectScreen && onSelectScreen('cart')}
            style={{
              background: secondaryColor || 'rgba(124, 92, 224, 0.12)',
              color: '#1a1824',
              borderRadius: 20,
              padding: '5px 12px',
              fontSize: 11,
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <span>🛍️</span>
            <span>Bag · 1</span>
          </div>
        )}
      </div>

      {/* Screen Content Body */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          background: '#fcfaf7',
          padding: '14px 16px 20px',
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
        }}
      >
        {/* HOME SCREEN */}
        {page === 'home' && (
          <>
            {showHero && (
              <div
                style={{
                  background: `linear-gradient(135deg, ${primaryColor}, ${primaryColor}dd)`,
                  borderRadius: 20,
                  padding: '18px 16px',
                  color: 'white',
                  boxShadow: `0 8px 24px ${primaryColor}35`,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <div style={{ fontSize: 8, letterSpacing: 1.5, fontWeight: 800, opacity: 0.85 }}>
                  A LITTLE EVERYDAY EXTRAORDINARY
                </div>
                <div style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.2, margin: '8px 0 6px', whiteSpace: 'pre-line' }}>
                  {screenConfig.title || 'Good things.\nGreat discoveries.'}
                </div>
                <div style={{ fontSize: 11, opacity: 0.9, lineHeight: 1.4, marginBottom: 12 }}>
                  {screenConfig.subtitle || `Explore our carefully chosen ${business} collection.`}
                </div>
                {pages.includes('products') && (
                  <button
                    type="button"
                    onClick={() => onSelectScreen && onSelectScreen('products')}
                    style={{
                      background: 'rgba(255,255,255,0.95)',
                      color: primaryColor,
                      border: 'none',
                      borderRadius: 12,
                      padding: '7px 14px',
                      fontSize: 11,
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    Explore collection →
                  </button>
                )}
              </div>
            )}

            {/* Search input */}
            {showSearch && (
              <div
                style={{
                  background: 'white',
                  border: '1px solid rgba(0,0,0,0.08)',
                  borderRadius: 12,
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: 12,
                  color: '#8b849c',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                }}
              >
                <span>🔍</span>
                <span>Search {business} products…</span>
              </div>
            )}

            {/* Category Chips */}
            <div style={{ display: 'flex', gap: 6, overflowX: 'auto', paddingBottom: 2 }}>
              {['All', 'Featured', 'Essentials', 'New'].map((cat, idx) => (
                <div
                  key={cat}
                  style={{
                    padding: '5px 12px',
                    borderRadius: 20,
                    fontSize: 10,
                    fontWeight: 700,
                    background: idx === 0 ? primaryColor : '#eeeaf5',
                    color: idx === 0 ? 'white' : '#453d52',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {cat}
                </div>
              ))}
            </div>

            {/* Heading */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
              <span style={{ fontSize: 15, fontWeight: 800, color: '#1a1824' }}>
                {screenConfig.title ? screenConfig.title.split('\n')[0] : 'The Latest Selection'}
              </span>
              <span style={{ fontSize: 10, color: primaryColor, fontWeight: 700 }}>See all ({demoProducts.length})</span>
            </div>

            {/* Catalog Layout */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: currentLayout === 'editorial' ? '1fr' : currentLayout === 'cards' ? '1fr' : 'repeat(2, 1fr)',
                gap: 10,
              }}
            >
              {demoProducts.map((prod) => (
                <div
                  key={prod.id}
                  onClick={() => onSelectScreen && onSelectScreen('detail')}
                  style={{
                    background: 'white',
                    borderRadius: 16,
                    border: '1px solid rgba(0,0,0,0.06)',
                    padding: 8,
                    display: 'flex',
                    flexDirection: currentLayout === 'cards' ? 'row' : 'column',
                    gap: 8,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.03)',
                    cursor: 'pointer',
                    position: 'relative',
                  }}
                >
                  <div
                    style={{
                      width: currentLayout === 'cards' ? 80 : '100%',
                      height: currentLayout === 'cards' ? 80 : currentLayout === 'editorial' ? 140 : 100,
                      borderRadius: 12,
                      overflow: 'hidden',
                      position: 'relative',
                      background: '#ede9f4',
                    }}
                  >
                    <img
                      src={prod.image_url}
                      alt={prod.name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                    {showBadges && prod.badge && (
                      <span
                        style={{
                          position: 'absolute',
                          top: 6,
                          left: 6,
                          background: primaryColor,
                          color: 'white',
                          fontSize: 8,
                          fontWeight: 800,
                          padding: '2px 6px',
                          borderRadius: 6,
                        }}
                      >
                        {prod.badge}
                      </span>
                    )}
                  </div>

                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 9, color: '#887d99', fontWeight: 700, textTransform: 'uppercase' }}>
                          {prod.category}
                        </span>
                        {prod.rating && (
                          <span style={{ fontSize: 9, fontWeight: 700, color: '#eab308' }}>★ {prod.rating}</span>
                        )}
                      </div>
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#1a1824', marginTop: 2, lineHeight: 1.3 }}>
                        {prod.name}
                      </div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
                      <span style={{ fontSize: 12, fontWeight: 800, color: accentColor }}>
                        Rs. {prod.price.toLocaleString()}
                      </span>
                      <span
                        style={{
                          width: 22,
                          height: 22,
                          borderRadius: 8,
                          background: primaryColor,
                          color: 'white',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 13,
                          fontWeight: 700,
                        }}
                      >
                        +
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* PRODUCTS SCREEN */}
        {page === 'products' && (
          <>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
                {screenConfig.title || 'All Products & Menu'}
              </div>
              <div style={{ fontSize: 11, color: '#7a708a', marginTop: 2 }}>
                {screenConfig.subtitle || `Browse our complete ${business} catalogue`}
              </div>
            </div>

            {/* Search Input */}
            {showSearch && (
              <div
                style={{
                  background: 'white',
                  border: '1px solid rgba(0,0,0,0.08)',
                  borderRadius: 12,
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: 12,
                  color: '#8b849c',
                }}
              >
                <span>🔍</span>
                <span>Filter items…</span>
              </div>
            )}

            {/* Category Pills */}
            <div style={{ display: 'flex', gap: 6, overflowX: 'auto' }}>
              {['All', 'Featured', 'Popular', 'Deals', 'New'].map((cat, idx) => (
                <div
                  key={cat}
                  style={{
                    padding: '5px 12px',
                    borderRadius: 20,
                    fontSize: 10,
                    fontWeight: 700,
                    background: idx === 0 ? primaryColor : '#eeeaf5',
                    color: idx === 0 ? 'white' : '#453d52',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {cat}
                </div>
              ))}
            </div>

            {/* Products List */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: currentLayout === 'editorial' ? '1fr' : currentLayout === 'cards' ? '1fr' : 'repeat(2, 1fr)',
                gap: 10,
              }}
            >
              {demoProducts.map((prod) => (
                <div
                  key={prod.id}
                  onClick={() => onSelectScreen && onSelectScreen('detail')}
                  style={{
                    background: 'white',
                    borderRadius: 16,
                    border: '1px solid rgba(0,0,0,0.06)',
                    padding: 8,
                    display: 'flex',
                    flexDirection: currentLayout === 'cards' ? 'row' : 'column',
                    gap: 8,
                    cursor: 'pointer',
                  }}
                >
                  <div
                    style={{
                      width: currentLayout === 'cards' ? 80 : '100%',
                      height: currentLayout === 'cards' ? 80 : 110,
                      borderRadius: 12,
                      overflow: 'hidden',
                      position: 'relative',
                    }}
                  >
                    <img src={prod.image_url} alt={prod.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    {showBadges && prod.badge && (
                      <span
                        style={{
                          position: 'absolute',
                          top: 6,
                          left: 6,
                          background: primaryColor,
                          color: 'white',
                          fontSize: 8,
                          fontWeight: 800,
                          padding: '2px 6px',
                          borderRadius: 6,
                        }}
                      >
                        {prod.badge}
                      </span>
                    )}
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#1a1824' }}>{prod.name}</div>
                      <div style={{ fontSize: 9, color: '#7a708a', marginTop: 2 }}>{prod.description?.slice(0, 45)}…</div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
                      <span style={{ fontSize: 12, fontWeight: 800, color: accentColor }}>Rs. {prod.price.toLocaleString()}</span>
                      <span style={{ fontSize: 10, color: primaryColor, fontWeight: 700 }}>+ Add</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* DETAIL SCREEN */}
        {page === 'detail' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div
              style={{
                width: '100%',
                height: 180,
                borderRadius: 20,
                overflow: 'hidden',
                position: 'relative',
                boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
              }}
            >
              <img
                src={selectedProduct.image_url}
                alt={selectedProduct.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              {selectedProduct.badge && (
                <div
                  style={{
                    position: 'absolute',
                    top: 12,
                    left: 12,
                    background: primaryColor,
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: 12,
                    fontSize: 10,
                    fontWeight: 800,
                  }}
                >
                  {selectedProduct.badge}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 9, letterSpacing: 1.5, fontWeight: 800, color: primaryColor, textTransform: 'uppercase' }}>
                {selectedProduct.category || 'Featured Collection'}
              </span>
              <span style={{ fontSize: 11, fontWeight: 700, color: '#eab308' }}>★ {selectedProduct.rating} Rating</span>
            </div>

            <div style={{ fontSize: 19, fontWeight: 800, color: '#1a1824' }}>{selectedProduct.name}</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: accentColor }}>
              Rs. {selectedProduct.price.toLocaleString()}
            </div>
            <div style={{ fontSize: 11, color: '#685f78', lineHeight: 1.6 }}>
              {selectedProduct.description}
            </div>

            {pages.includes('cart') && (
              <button
                type="button"
                onClick={() => onSelectScreen && onSelectScreen('cart')}
                style={{
                  background: primaryColor,
                  color: 'white',
                  border: 'none',
                  borderRadius: 14,
                  padding: '12px',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: 'pointer',
                  marginTop: 6,
                  boxShadow: `0 4px 16px ${primaryColor}40`,
                }}
              >
                Add to bag · Rs. {selectedProduct.price.toLocaleString()}
              </button>
            )}

            <button
              type="button"
              onClick={() => onSelectScreen && onSelectScreen('products')}
              style={{
                background: '#eeeaf5',
                color: '#403850',
                border: 'none',
                borderRadius: 14,
                padding: '10px',
                fontSize: 11,
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              ← Back to collection
            </button>
          </div>
        )}

        {/* CART SCREEN */}
        {page === 'cart' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || 'Your Shopping Bag'}
            </div>
            <div style={{ fontSize: 11, color: '#7a708a' }}>1 item in your demo cart</div>

            <div
              style={{
                background: 'white',
                borderRadius: 16,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 10,
                display: 'flex',
                gap: 10,
                alignItems: 'center',
              }}
            >
              <div style={{ width: 54, height: 54, borderRadius: 12, overflow: 'hidden', flexShrink: 0 }}>
                <img src={selectedProduct.image_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>{selectedProduct.name}</div>
                <div style={{ fontSize: 11, color: '#7a708a' }}>Rs. {selectedProduct.price.toLocaleString()}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: '#7a708a', cursor: 'pointer' }}>−</span>
                <span style={{ fontSize: 12, fontWeight: 800, color: '#1a1824' }}>1</span>
                <span style={{ fontSize: 14, fontWeight: 700, color: primaryColor, cursor: 'pointer' }}>+</span>
              </div>
            </div>

            <div
              style={{
                background: '#f4f1fa',
                borderRadius: 16,
                padding: 14,
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
                marginTop: 8,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#635b75' }}>
                <span>Subtotal</span>
                <span>Rs. {selectedProduct.price.toLocaleString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#635b75' }}>
                <span>Standard Delivery</span>
                <span style={{ color: '#15803d', fontWeight: 700 }}>FREE</span>
              </div>
              <div style={{ borderTop: '1px solid rgba(0,0,0,0.08)', paddingTop: 8, display: 'flex', justifyContent: 'space-between', fontSize: 15, fontWeight: 800, color: '#1a1824' }}>
                <span>Total</span>
                <span>Rs. {selectedProduct.price.toLocaleString()}</span>
              </div>
            </div>

            {pages.includes('checkout') && (
              <button
                type="button"
                onClick={() => onSelectScreen && onSelectScreen('checkout')}
                style={{
                  background: primaryColor,
                  color: 'white',
                  border: 'none',
                  borderRadius: 14,
                  padding: '12px',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: 'pointer',
                  boxShadow: `0 4px 16px ${primaryColor}40`,
                }}
              >
                Proceed to Checkout →
              </button>
            )}
          </div>
        )}

        {/* CHECKOUT SCREEN */}
        {page === 'checkout' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || 'Checkout & Delivery'}
            </div>
            <div style={{ fontSize: 11, color: '#7a708a' }}>Cash on Delivery (COD) · Local order demo</div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <span style={{ fontSize: 10, fontWeight: 700, color: '#685f78' }}>Full Name</span>
              <input
                readOnly
                value="Ahmed Khan"
                style={{
                  background: 'white',
                  border: '1px solid rgba(0,0,0,0.1)',
                  borderRadius: 10,
                  padding: '9px 12px',
                  fontSize: 12,
                  color: '#1a1824',
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <span style={{ fontSize: 10, fontWeight: 700, color: '#685f78' }}>Delivery Address</span>
              <input
                readOnly
                value="House 42, Street 8, F-7/2, Islamabad"
                style={{
                  background: 'white',
                  border: '1px solid rgba(0,0,0,0.1)',
                  borderRadius: 10,
                  padding: '9px 12px',
                  fontSize: 12,
                  color: '#1a1824',
                }}
              />
            </div>

            <div
              style={{
                background: 'rgba(124, 92, 224, 0.08)',
                border: `1px solid ${primaryColor}30`,
                borderRadius: 12,
                padding: '10px 12px',
                display: 'flex',
                gap: 8,
                alignItems: 'center',
                marginTop: 4,
              }}
            >
              <span style={{ fontSize: 18 }}>💵</span>
              <div>
                <div style={{ fontSize: 11, fontWeight: 800, color: '#1a1824' }}>Cash on Delivery</div>
                <div style={{ fontSize: 9, color: '#7a708a' }}>Pay upon doorstep arrival. Zero online risk.</div>
              </div>
            </div>

            <button
              type="button"
              style={{
                background: primaryColor,
                color: 'white',
                border: 'none',
                borderRadius: 14,
                padding: '12px',
                fontSize: 13,
                fontWeight: 700,
                cursor: 'pointer',
                marginTop: 10,
                boxShadow: `0 4px 16px ${primaryColor}40`,
              }}
            >
              Place Demo Order · Rs. {selectedProduct.price.toLocaleString()}
            </button>
          </div>
        )}

        {/* SEARCH SCREEN */}
        {page === 'search' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || 'Search & Discover'}
            </div>
            <div
              style={{
                background: 'white',
                border: '1px solid rgba(0,0,0,0.1)',
                borderRadius: 12,
                padding: '10px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                fontSize: 12,
                color: '#1a1824',
              }}
            >
              <span>🔍</span>
              <span>Find your favourite {business}…</span>
            </div>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#685f78', marginTop: 6 }}>Popular Searches</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {['Top Rated', 'Deals', 'Essentials', 'Combos'].map((tag) => (
                <div
                  key={tag}
                  style={{
                    padding: '4px 10px',
                    borderRadius: 14,
                    background: '#ede9f5',
                    color: '#463c55',
                    fontSize: 10,
                    fontWeight: 600,
                  }}
                >
                  {tag}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CONTACT SCREEN */}
        {page === 'contact' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || "Let's Talk"}
            </div>
            <div style={{ fontSize: 11, color: '#7a708a' }}>
              {screenConfig.subtitle || `We would love to help you find the right fit for your ${business} needs.`}
            </div>
            <div
              style={{
                background: 'white',
                border: '1px solid rgba(0,0,0,0.06)',
                borderRadius: 14,
                padding: 12,
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
              }}
            >
              <span style={{ fontSize: 10, fontWeight: 700, color: primaryColor }}>EMAIL US</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>concierge@{projectName.toLowerCase().replace(/\s+/g, '') || 'jinie'}.com</span>
            </div>
            <div
              style={{
                background: 'white',
                border: '1px solid rgba(0,0,0,0.06)',
                borderRadius: 14,
                padding: 12,
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
              }}
            >
              <span style={{ fontSize: 10, fontWeight: 700, color: primaryColor }}>OPERATING HOURS</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>Mon – Sat · 9:00 AM – 9:00 PM</span>
            </div>
          </div>
        )}

        {/* ABOUT SCREEN */}
        {page === 'about' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || 'A Thoughtful Collection'}
            </div>
            <div style={{ fontSize: 11, color: '#685f78', lineHeight: 1.6 }}>
              {screenConfig.subtitle || `${projectName} brings together carefully selected ${business} essentials. Built with care, made for everyday life.`}
            </div>
            <div
              style={{
                background: `linear-gradient(135deg, ${primaryColor}15, ${accentColor}15)`,
                border: `1px solid ${primaryColor}30`,
                borderRadius: 16,
                padding: 14,
              }}
            >
              <div style={{ fontSize: 12, fontWeight: 800, color: '#1a1824' }}>Our Quality Promise</div>
              <div style={{ fontSize: 10, color: '#685f78', marginTop: 4, lineHeight: 1.5 }}>
                Authentic sourcing, community integrity, and long-lasting durability across every piece.
              </div>
            </div>
          </div>
        )}

        {/* SETTINGS SCREEN */}
        {page === 'settings' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || 'App Settings & Preferences'}
            </div>
            <div style={{ fontSize: 11, color: '#7a708a' }}>
              {screenConfig.subtitle || 'Customize your application experience and regional options.'}
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 14,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 12,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>Push Notifications</div>
                <div style={{ fontSize: 10, color: '#7a708a' }}>Order status alerts and promotions</div>
              </div>
              <div
                style={{
                  background: primaryColor,
                  color: 'white',
                  borderRadius: 12,
                  padding: '4px 10px',
                  fontSize: 10,
                  fontWeight: 700,
                }}
              >
                ON
              </div>
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 14,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 12,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>Currency & Region</div>
                <div style={{ fontSize: 10, color: '#7a708a' }}>Pakistani Rupee (PKR · Rs.)</div>
              </div>
              <span style={{ fontSize: 11, fontWeight: 800, color: primaryColor }}>PKR 🇵🇰</span>
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 14,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 12,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>Language</div>
                <div style={{ fontSize: 10, color: '#7a708a' }}>Primary display language</div>
              </div>
              <span style={{ fontSize: 11, fontWeight: 700, color: '#1a1824' }}>English</span>
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 14,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 12,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#1a1824' }}>Data & Privacy</div>
                <div style={{ fontSize: 10, color: '#7a708a' }}>Local storage on this device</div>
              </div>
              <span
                style={{
                  background: '#fee2e2',
                  color: '#dc2626',
                  borderRadius: 8,
                  padding: '4px 8px',
                  fontSize: 10,
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                Clear Data
              </span>
            </div>
          </div>
        )}

        {/* PROFILE SCREEN */}
        {page === 'profile' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#1a1824' }}>
              {screenConfig.title || 'My Profile'}
            </div>
            <div style={{ fontSize: 11, color: '#7a708a' }}>
              {screenConfig.subtitle || 'Account overview and order history'}
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 14,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 14,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 22,
                  background: primaryColor,
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: 16,
                }}
              >
                AK
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 800, color: '#1a1824' }}>Ahmed Khan</div>
                <div style={{ fontSize: 10, color: '#7a708a' }}>ahmed.khan@example.com</div>
                <span
                  style={{
                    display: 'inline-block',
                    marginTop: 4,
                    background: `${primaryColor}20`,
                    color: primaryColor,
                    padding: '2px 8px',
                    borderRadius: 6,
                    fontSize: 9,
                    fontWeight: 700,
                  }}
                >
                  ★ Gold Member · 12 Orders
                </span>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <div
                style={{
                  flex: 1,
                  background: 'white',
                  borderRadius: 12,
                  padding: 10,
                  textAlign: 'center',
                  border: '1px solid rgba(0,0,0,0.06)',
                }}
              >
                <div style={{ fontSize: 16, fontWeight: 800, color: primaryColor }}>12</div>
                <div style={{ fontSize: 9, color: '#7a708a' }}>Orders</div>
              </div>
              <div
                style={{
                  flex: 1,
                  background: 'white',
                  borderRadius: 12,
                  padding: 10,
                  textAlign: 'center',
                  border: '1px solid rgba(0,0,0,0.06)',
                }}
              >
                <div style={{ fontSize: 16, fontWeight: 800, color: primaryColor }}>5</div>
                <div style={{ fontSize: 9, color: '#7a708a' }}>Wishlist</div>
              </div>
              <div
                style={{
                  flex: 1,
                  background: 'white',
                  borderRadius: 12,
                  padding: 10,
                  textAlign: 'center',
                  border: '1px solid rgba(0,0,0,0.06)',
                }}
              >
                <div style={{ fontSize: 16, fontWeight: 800, color: primaryColor }}>450</div>
                <div style={{ fontSize: 9, color: '#7a708a' }}>Points</div>
              </div>
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 12,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 12,
              }}
            >
              <div style={{ fontSize: 9, fontWeight: 800, color: primaryColor, letterSpacing: 1 }}>DEFAULT SHIPPING ADDRESS</div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#1a1824', marginTop: 4 }}>House 42, Street 8, F-7/2, Islamabad</div>
            </div>
            <div
              style={{
                background: 'white',
                borderRadius: 12,
                border: '1px solid rgba(0,0,0,0.06)',
                padding: 12,
              }}
            >
              <div style={{ fontSize: 9, fontWeight: 800, color: primaryColor, letterSpacing: 1 }}>PAYMENT METHOD</div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#1a1824', marginTop: 4 }}>Cash on Delivery (Default)</div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom App Navigation Bar */}
      {navPages.length > 1 && (
        <div
          style={{
            background: 'white',
            borderTop: '1px solid rgba(0,0,0,0.06)',
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            padding: '8px 6px',
            zIndex: 10,
          }}
        >
          {navPages.map((navPage) => {
            const isCurrent = navPage === page;
            const icon =
              navPage === 'home' ? '⌂' :
              navPage === 'products' ? '🛍️' :
              navPage === 'cart' ? '🛒' :
              navPage === 'search' ? '🔍' :
              navPage === 'contact' ? '📞' :
              navPage === 'settings' ? '⚙️' :
              navPage === 'profile' ? '👤' : '✦';
            return (
              <div
                key={navPage}
                onClick={() => onSelectScreen && onSelectScreen(navPage)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 2,
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: 8,
                  background: isCurrent ? `${primaryColor}15` : 'transparent',
                }}
              >
                <span style={{ fontSize: 14, color: isCurrent ? primaryColor : '#887d99' }}>{icon}</span>
                <span
                  style={{
                    fontSize: 8,
                    fontWeight: 700,
                    textTransform: 'capitalize',
                    color: isCurrent ? primaryColor : '#887d99',
                  }}
                >
                  {navPage === 'products' ? 'Shop' : navPage}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Home Indicator Bar */}
      <div
        style={{
          background: 'white',
          padding: '4px 0 6px',
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <div style={{ width: 90, height: 4, borderRadius: 3, background: '#1c1928' }} />
      </div>
    </div>
  );
}
