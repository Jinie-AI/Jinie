import { useState } from 'react';
import HtmlScreenMockup, { type ScreenConfigData } from './HtmlScreenMockup';

interface Requirement {
  id: string;
  page: string;
  text: string;
  approved: boolean;
}

interface Design {
  primary: string;
  secondary?: string;
  accent?: string;
  bodyFont?: string;
  navigation?: string;
  theme: string;
  font: string;
  layout: string;
}

interface Project {
  id: string;
  name: string;
  spec: {
    business: string;
    business_label?: string;
    pages: string[];
    products?: any[];
    screen_configs?: Record<string, ScreenConfigData>;
  };
  screen_configs?: Record<string, ScreenConfigData>;
  design: Design;
  requirements: Requirement[];
  status: string;
  stage: string;
}

interface ScreenShowcaseSectionProps {
  project: Project;
  screenConfigs: Record<string, ScreenConfigData>;
  onUpdateScreenConfig: (page: string, config: Partial<ScreenConfigData>) => void;
  onUpdateRequirement: (page: string, text: string) => void;
  onUpdateDesign: (change: Partial<Design>) => void;
  onBuildApp: () => void;
  busy: boolean;
  active: boolean;
}

export default function ScreenShowcaseSection({
  project,
  screenConfigs,
  onUpdateScreenConfig,
  onUpdateRequirement,
  onUpdateDesign,
  onBuildApp,
  busy,
  active,
}: ScreenShowcaseSectionProps) {
  const pages = project.spec.pages || ['home', 'products', 'detail', 'cart', 'checkout'];
  const [selectedScreen, setSelectedScreen] = useState<string>(pages[0] || 'home');
  const [viewMode, setViewMode] = useState<'single' | 'gallery'>('single');

  const currentConfig: ScreenConfigData = screenConfigs[selectedScreen] || {
    title: '',
    subtitle: '',
    layout: (project.design.layout as any) || 'grid',
    show_hero: true,
    show_search: true,
    show_badges: true,
  };

  const currentReq = project.requirements.find((r) => r.page === selectedScreen);
  const screenIndex = pages.indexOf(selectedScreen);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Top Banner with Actions */}
      <div
        style={{
          background: 'var(--surface, #ffffff)',
          border: '1px solid var(--edge, #e2e5ec)',
          borderRadius: 22,
          padding: '24px 28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 20,
          boxShadow: '0 4px 20px rgba(20, 24, 41, 0.03)',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ maxWidth: 650 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 9,
              letterSpacing: 1.5,
              fontWeight: 800,
              color: 'var(--accent, #7155d9)',
              marginBottom: 8,
              textTransform: 'uppercase',
            }}
          >
            <span>✦</span>
            <span>Multi-Screen Architecture & Live Customizer</span>
          </div>
          <h2 style={{ fontSize: 24, fontWeight: 700, color: 'var(--ink, #20232b)', margin: '0 0 6px' }}>
            Interactive Screen Flow for {project.name}
          </h2>
          <p style={{ fontSize: 12, color: 'var(--soft, #646b79)', margin: 0, lineHeight: 1.6 }}>
            Jinie autonomously generated {pages.length} necessary screens based on your request.
            Customize each screen in real-time HTML/CSS below, or view them side-by-side before compiling your full React Native application.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          {/* View Mode Toggle */}
          <div
            style={{
              display: 'inline-flex',
              background: 'var(--raised, #f0f2f6)',
              padding: 4,
              borderRadius: 14,
              border: '1px solid var(--edge, #e2e5ec)',
            }}
          >
            <button
              type="button"
              onClick={() => setViewMode('single')}
              style={{
                padding: '8px 16px',
                borderRadius: 10,
                fontSize: 11,
                fontWeight: 700,
                background: viewMode === 'single' ? 'var(--surface, #ffffff)' : 'transparent',
                color: viewMode === 'single' ? 'var(--accent, #7155d9)' : 'var(--soft, #646b79)',
                boxShadow: viewMode === 'single' ? '0 2px 8px rgba(0,0,0,0.06)' : 'none',
                cursor: 'pointer',
              }}
            >
              📱 Focus & Customize
            </button>
            <button
              type="button"
              onClick={() => setViewMode('gallery')}
              style={{
                padding: '8px 16px',
                borderRadius: 10,
                fontSize: 11,
                fontWeight: 700,
                background: viewMode === 'gallery' ? 'var(--surface, #ffffff)' : 'transparent',
                color: viewMode === 'gallery' ? 'var(--accent, #7155d9)' : 'var(--soft, #646b79)',
                boxShadow: viewMode === 'gallery' ? '0 2px 8px rgba(0,0,0,0.06)' : 'none',
                cursor: 'pointer',
              }}
            >
              ▦ All Screens ({pages.length})
            </button>
          </div>

          {/* Primary Build CTA */}
          <button
            type="button"
            className="primary"
            disabled={busy || active}
            onClick={onBuildApp}
            style={{
              padding: '14px 24px',
              borderRadius: 24,
              fontSize: 13,
              fontWeight: 700,
              background: 'var(--accent, #7356da)',
              color: 'white',
              boxShadow: '0 6px 20px rgba(115, 86, 218, 0.35)',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span>{busy ? 'Compiling…' : 'Approve Screens & Build Application'}</span>
            <span style={{ fontSize: 16 }}>↗</span>
          </button>
        </div>
      </div>

      {/* Screen Selector Pills */}
      <div
        style={{
          display: 'flex',
          gap: 10,
          overflowX: 'auto',
          paddingBottom: 4,
          alignItems: 'center',
        }}
      >
        <span style={{ fontSize: 10, fontWeight: 800, color: 'var(--soft, #646b79)', letterSpacing: 1.2, textTransform: 'uppercase', marginRight: 4 }}>
          Screens:
        </span>
        {pages.map((p, idx) => {
          const isSelected = p === selectedScreen;
          return (
            <button
              key={p}
              type="button"
              onClick={() => {
                setSelectedScreen(p);
                setViewMode('single');
              }}
              style={{
                padding: '10px 18px',
                borderRadius: 16,
                border: isSelected ? '1px solid var(--accent, #7155d9)' : '1px solid var(--edge, #e2e5ec)',
                background: isSelected ? 'var(--accent, #7155d9)' : 'var(--surface, #ffffff)',
                color: isSelected ? '#ffffff' : 'var(--ink, #20232b)',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                boxShadow: isSelected ? '0 4px 14px rgba(113, 85, 217, 0.25)' : 'none',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap',
              }}
            >
              <span
                style={{
                  width: 18,
                  height: 18,
                  borderRadius: '50%',
                  background: isSelected ? 'rgba(255,255,255,0.25)' : 'var(--raised, #f0f2f6)',
                  color: isSelected ? '#ffffff' : 'var(--soft, #646b79)',
                  fontSize: 10,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                }}
              >
                {idx + 1}
              </span>
              <span style={{ textTransform: 'capitalize' }}>
                {p === 'products' ? 'Catalog & Menu' : p}
              </span>
            </button>
          );
        })}
      </div>

      {/* SINGLE SCREEN CUSTOMIZER VIEW */}
      {viewMode === 'single' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(340px, 1fr) 380px',
            gap: 24,
            alignItems: 'start',
          }}
        >
          {/* Left Column: Screen Customizer Form Controls */}
          <div
            style={{
              background: 'var(--surface, #ffffff)',
              border: '1px solid var(--edge, #e2e5ec)',
              borderRadius: 22,
              padding: 26,
              boxShadow: '0 4px 20px rgba(20, 24, 41, 0.03)',
              display: 'flex',
              flexDirection: 'column',
              gap: 20,
            }}
          >
            {/* Screen Meta Header */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid var(--edge, #e2e5ec)',
                paddingBottom: 16,
              }}
            >
              <div>
                <span
                  style={{
                    fontSize: 10,
                    letterSpacing: 1.5,
                    fontWeight: 800,
                    color: 'var(--accent, #7155d9)',
                    textTransform: 'uppercase',
                  }}
                >
                  Screen {screenIndex + 1} of {pages.length} · {selectedScreen.toUpperCase()}
                </span>
                <h3 style={{ fontSize: 20, fontWeight: 800, color: 'var(--ink, #20232b)', margin: '4px 0 0' }}>
                  Customize {selectedScreen.charAt(0).toUpperCase() + selectedScreen.slice(1)} Screen
                </h3>
              </div>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  color: '#15803d',
                  background: 'rgba(22, 163, 74, 0.12)',
                  padding: '6px 12px',
                  borderRadius: 20,
                }}
              >
                ● Live Preview Active
              </span>
            </div>

            {/* Title Customization */}
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: 10,
                  fontWeight: 800,
                  letterSpacing: 1.2,
                  color: 'var(--soft, #646b79)',
                  marginBottom: 8,
                  textTransform: 'uppercase',
                }}
              >
                Screen Headline / Title
              </label>
              <input
                type="text"
                value={currentConfig.title || ''}
                placeholder={
                  selectedScreen === 'home'
                    ? 'Good things. Great discoveries.'
                    : selectedScreen === 'products'
                    ? 'The Full Collection'
                    : selectedScreen === 'cart'
                    ? 'Your Bag'
                    : `${selectedScreen.charAt(0).toUpperCase() + selectedScreen.slice(1)} Screen`
                }
                onChange={(e) => onUpdateScreenConfig(selectedScreen, { title: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: 12,
                  border: '1px solid var(--edge, #e2e5ec)',
                  fontSize: 13,
                  color: 'var(--ink, #20232b)',
                  background: 'var(--canvas, #f7f8fa)',
                  fontWeight: 600,
                }}
              />
            </div>

            {/* Subtitle Customization */}
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: 10,
                  fontWeight: 800,
                  letterSpacing: 1.2,
                  color: 'var(--soft, #646b79)',
                  marginBottom: 8,
                  textTransform: 'uppercase',
                }}
              >
                Screen Subtitle / Tagline
              </label>
              <textarea
                rows={2}
                value={currentConfig.subtitle || ''}
                placeholder={`Explore our carefully curated ${project.spec.business} selection.`}
                onChange={(e) => onUpdateScreenConfig(selectedScreen, { subtitle: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: 12,
                  border: '1px solid var(--edge, #e2e5ec)',
                  fontSize: 13,
                  color: 'var(--ink, #20232b)',
                  background: 'var(--canvas, #f7f8fa)',
                  lineHeight: 1.5,
                }}
              />
            </div>

            {/* Layout Variant Switcher (relevant for Home and Products) */}
            {['home', 'products', 'search'].includes(selectedScreen) && (
              <div>
                <label
                  style={{
                    display: 'block',
                    fontSize: 10,
                    fontWeight: 800,
                    letterSpacing: 1.2,
                    color: 'var(--soft, #646b79)',
                    marginBottom: 8,
                    textTransform: 'uppercase',
                  }}
                >
                  Screen Layout Variant
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                  {[
                    { id: 'grid', label: 'Grid', icon: '▦', desc: '2-column balanced' },
                    { id: 'cards', label: 'Cards', icon: '☰', desc: 'Horizontal rows' },
                    { id: 'editorial', label: 'Editorial', icon: '▤', desc: 'Full-width hero' },
                  ].map((l) => {
                    const isChosen = currentConfig.layout === l.id;
                    return (
                      <button
                        key={l.id}
                        type="button"
                        onClick={() => onUpdateScreenConfig(selectedScreen, { layout: l.id as any })}
                        style={{
                          padding: '12px 10px',
                          borderRadius: 14,
                          border: isChosen ? '2px solid var(--accent, #7155d9)' : '1px solid var(--edge, #e2e5ec)',
                          background: isChosen ? 'rgba(113, 85, 217, 0.08)' : 'var(--canvas, #f7f8fa)',
                          color: isChosen ? 'var(--accent, #7155d9)' : 'var(--ink, #20232b)',
                          cursor: 'pointer',
                          textAlign: 'center',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <div style={{ fontSize: 18, marginBottom: 4 }}>{l.icon}</div>
                        <div style={{ fontSize: 11, fontWeight: 800 }}>{l.label}</div>
                        <div style={{ fontSize: 9, color: 'var(--soft, #646b79)', marginTop: 2 }}>{l.desc}</div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Visual Section Toggles */}
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: 10,
                  fontWeight: 800,
                  letterSpacing: 1.2,
                  color: 'var(--soft, #646b79)',
                  marginBottom: 10,
                  textTransform: 'uppercase',
                }}
              >
                Screen Elements & Sections
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {selectedScreen === 'home' && (
                  <label
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      borderRadius: 12,
                      background: 'var(--canvas, #f7f8fa)',
                      border: '1px solid var(--edge, #e2e5ec)',
                      fontSize: 12,
                      fontWeight: 600,
                      color: 'var(--ink, #20232b)',
                      cursor: 'pointer',
                    }}
                  >
                    <span>Show Hero Promotional Banner</span>
                    <input
                      type="checkbox"
                      checked={currentConfig.show_hero !== false}
                      onChange={(e) => onUpdateScreenConfig(selectedScreen, { show_hero: e.target.checked })}
                      style={{ width: 18, height: 18, accentColor: 'var(--accent, #7155d9)' }}
                    />
                  </label>
                )}

                {['home', 'products', 'search'].includes(selectedScreen) && (
                  <label
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      borderRadius: 12,
                      background: 'var(--canvas, #f7f8fa)',
                      border: '1px solid var(--edge, #e2e5ec)',
                      fontSize: 12,
                      fontWeight: 600,
                      color: 'var(--ink, #20232b)',
                      cursor: 'pointer',
                    }}
                  >
                    <span>Show Search Input Bar</span>
                    <input
                      type="checkbox"
                      checked={currentConfig.show_search !== false}
                      onChange={(e) => onUpdateScreenConfig(selectedScreen, { show_search: e.target.checked })}
                      style={{ width: 18, height: 18, accentColor: 'var(--accent, #7155d9)' }}
                    />
                  </label>
                )}

                <label
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: 12,
                    background: 'var(--canvas, #f7f8fa)',
                    border: '1px solid var(--edge, #e2e5ec)',
                    fontSize: 12,
                    fontWeight: 600,
                    color: 'var(--ink, #20232b)',
                    cursor: 'pointer',
                  }}
                >
                  <span>Show Badges & Customer Ratings</span>
                  <input
                    type="checkbox"
                    checked={currentConfig.show_badges !== false}
                    onChange={(e) => onUpdateScreenConfig(selectedScreen, { show_badges: e.target.checked })}
                    style={{ width: 18, height: 18, accentColor: 'var(--accent, #7155d9)' }}
                  />
                </label>
              </div>
            </div>

            {/* Quick Theme Color Adjustment */}
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: 10,
                  fontWeight: 800,
                  letterSpacing: 1.2,
                  color: 'var(--soft, #646b79)',
                  marginBottom: 8,
                  textTransform: 'uppercase',
                }}
              >
                Signature Palette (Live Update)
              </label>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <input
                    type="color"
                    value={project.design.primary}
                    onChange={(e) => onUpdateDesign({ primary: e.target.value })}
                    style={{ width: 34, height: 34, padding: 0, border: 'none', borderRadius: 8, cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--soft, #646b79)' }}>Primary</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <input
                    type="color"
                    value={project.design.accent || '#b98849'}
                    onChange={(e) => onUpdateDesign({ accent: e.target.value })}
                    style={{ width: 34, height: 34, padding: 0, border: 'none', borderRadius: 8, cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--soft, #646b79)' }}>Accent</span>
                </div>
              </div>
            </div>

            {/* Associated Functional Requirement Box */}
            {currentReq && (
              <div
                style={{
                  borderTop: '1px solid var(--edge, #e2e5ec)',
                  paddingTop: 16,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span
                      style={{
                        background: 'rgba(113, 85, 217, 0.12)',
                        color: 'var(--accent, #7155d9)',
                        fontWeight: 800,
                        fontSize: 10,
                        padding: '3px 8px',
                        borderRadius: 6,
                      }}
                    >
                      {currentReq.id}
                    </span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--ink, #20232b)' }}>
                      Functional Requirement
                    </span>
                  </div>
                  <span style={{ fontSize: 10, fontWeight: 700, color: '#15803d' }}>
                    ✓ Active & Integrated
                  </span>
                </div>
                <textarea
                  rows={2}
                  value={currentReq.text}
                  onChange={(e) => onUpdateRequirement(selectedScreen, e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 10,
                    border: '1px solid var(--edge, #e2e5ec)',
                    fontSize: 11,
                    color: 'var(--ink, #20232b)',
                    background: 'var(--canvas, #f7f8fa)',
                    lineHeight: 1.5,
                  }}
                />
              </div>
            )}

            {/* Bottom Action inside customizer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 10 }}>
              <span style={{ fontSize: 11, color: 'var(--soft, #646b79)' }}>
                Changes update in real-time HTML/CSS
              </span>
              <button
                type="button"
                className="primary"
                disabled={busy || active}
                onClick={onBuildApp}
                style={{
                  padding: '12px 20px',
                  borderRadius: 20,
                  fontSize: 12,
                  fontWeight: 700,
                  background: 'var(--accent, #7356da)',
                  color: 'white',
                  cursor: 'pointer',
                }}
              >
                Approve & Build ↗
              </button>
            </div>
          </div>

          {/* Right Column: Live HTML/CSS Phone Mockup */}
          <div
            style={{
              position: 'sticky',
              top: 24,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <HtmlScreenMockup
              page={selectedScreen}
              screenConfig={currentConfig}
              projectName={project.name}
              business={project.spec.business}
              products={project.spec.products}
              primaryColor={project.design.primary}
              accentColor={project.design.accent || '#b98849'}
              secondaryColor={project.design.secondary || '#ede5f7'}
              pages={pages}
              onSelectScreen={(newPage) => setSelectedScreen(newPage)}
            />
            <div
              style={{
                fontSize: 10,
                color: 'var(--soft, #646b79)',
                fontWeight: 600,
                textAlign: 'center',
                letterSpacing: 0.5,
              }}
            >
              Interactive HTML/CSS Preview · Export format: React Native
            </div>
          </div>
        </div>
      )}

      {/* SIDE-BY-SIDE ALL SCREENS GALLERY VIEW */}
      {viewMode === 'gallery' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 28,
            justifyItems: 'center',
            background: 'var(--surface, #ffffff)',
            border: '1px solid var(--edge, #e2e5ec)',
            borderRadius: 24,
            padding: '32px 24px',
            boxShadow: '0 4px 20px rgba(20, 24, 41, 0.03)',
          }}
        >
          {pages.map((p, idx) => {
            const config = screenConfigs[p] || {};
            return (
              <div
                key={p}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 12,
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    width: 320,
                    padding: '0 8px',
                  }}
                >
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 800,
                      color: 'var(--ink, #20232b)',
                      textTransform: 'capitalize',
                    }}
                  >
                    Screen {idx + 1}: {p}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedScreen(p);
                      setViewMode('single');
                    }}
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: 'var(--accent, #7155d9)',
                      background: 'rgba(113, 85, 217, 0.1)',
                      border: 'none',
                      borderRadius: 12,
                      padding: '5px 12px',
                      cursor: 'pointer',
                    }}
                  >
                    Customize ✎
                  </button>
                </div>

                <HtmlScreenMockup
                  page={p}
                  screenConfig={config}
                  projectName={project.name}
                  business={project.spec.business}
                  products={project.spec.products}
                  primaryColor={project.design.primary}
                  accentColor={project.design.accent || '#b98849'}
                  secondaryColor={project.design.secondary || '#ede5f7'}
                  pages={pages}
                  onSelectScreen={(newPage) => {
                    setSelectedScreen(newPage);
                    setViewMode('single');
                  }}
                />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
