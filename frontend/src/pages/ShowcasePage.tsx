import Header from "../components/common/Header";
import Footer from "../components/common/Footer";
import { useNavigate } from "react-router-dom";

export default function ShowcasePage() {
    const navigate = useNavigate();

    const featuredApp = {
        name: "ShopVibe Luxury E-Commerce",
        prompt: '"Build an elegant luxury fashion storefront with product filters, shopping cart drawer, dark mode toggle, and checkout workflow."',
        description: "A full-featured e-commerce platform generated from a 2-sentence prompt, complete with responsive product cards, reactive cart state, and order summary.",
        tags: ["E-Commerce", "Firebase Deployed", "React 19", "Featured"],
        stats: { screens: 5, entities: 4, deployTime: "18s" },
    };

    const apps = [
        {
            name: "KhaanaExpress Food Delivery",
            prompt: '"Mujhe ek khane ki delivery app banani hai jisme menu ho, cart ho aur order track ho sake."',
            description: "Roman Urdu prompt input transformed into a dual-language food ordering portal with item customization and live order status.",
            tags: ["Roman Urdu Prompt", "Food Delivery", "Firebase Deployed"],
            category: "Mobile First",
        },
        {
            name: "TaskPulse Kanban Board",
            prompt: '"Create a modern project management workspace like Trello with column drag-and-drop, task priorities, and deadline counters."',
            description: "Productivity application featuring multi-board management, interactive status badges, and localized state persistence.",
            tags: ["Productivity", "Kanban Board", "State Hooks"],
            category: "SaaS App",
        },
        {
            name: "HealthTrack Fitness Hub",
            prompt: '"Build a daily workout logger with progress charts, calorie counter, and weekly goal streaks."',
            description: "Comprehensive fitness dashboard featuring visual data cards, active workout session counters, and dark gradient theme.",
            tags: ["Healthcare", "Dashboard", "Charts"],
            category: "Dashboard",
        },
        {
            name: "PropFinder Real Estate Portal",
            prompt: '"Create a property listing search app with price range sliders, location filters, and agent contact form."',
            description: "Property discovery platform with dynamic filtering, image galleries, and interactive agent inquiry dialogs.",
            tags: ["Real Estate", "Search & Filter", "Firebase Deployed"],
            category: "Marketplace",
        },
        {
            name: "Aegis AI Chat Assistant",
            prompt: '"Build an AI chatbot interface with thread history, code block syntax highlighting, and settings drawer."',
            description: "Conversational AI workspace featuring stream simulation, prompt templates, and customizable model settings.",
            tags: ["AI Tool", "Chat UI", "Dark Theme"],
            category: "AI SaaS",
        },
    ];

    return (
        <div className="showcase-page">
            <Header />

            <main className="showcase-content">
                <section className="showcase-hero">
                    <span className="hero-badge">✦ GENERATED APPLICATION GALLERY ✦</span>
                    <h1>
                        Built by Jinie,
                        <span> Ready for Production.</span>
                    </h1>
                    <p className="hero-description">
                        Explore real applications compiled by Jinie's 7-stage engine from single-sentence prompts.
                    </p>
                </section>

                {/* Featured Card */}
                <section className="featured-section">
                    <div className="featured-card">
                        <div className="featured-badge">⭐ FEATURED GENERATED APP</div>
                        <div className="featured-body">
                            <div className="featured-info">
                                <h2 className="featured-title">{featuredApp.name}</h2>
                                <p className="featured-prompt">{featuredApp.prompt}</p>
                                <p className="featured-desc">{featuredApp.description}</p>

                                <div className="featured-stats">
                                    <div className="stat-box">
                                        <span className="stat-num">{featuredApp.stats.screens}</span>
                                        <span className="stat-label">Screens</span>
                                    </div>
                                    <div className="stat-box">
                                        <span className="stat-num">{featuredApp.stats.entities}</span>
                                        <span className="stat-label">Entities</span>
                                    </div>
                                    <div className="stat-box">
                                        <span className="stat-num">{featuredApp.stats.deployTime}</span>
                                        <span className="stat-label">Gen Time</span>
                                    </div>
                                </div>

                                <div className="featured-tags">
                                    {featuredApp.tags.map((tag, idx) => (
                                        <span key={idx} className="gradient-badge">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="featured-mockup">
                                <div className="mockup-window">
                                    <div className="mockup-header">
                                        <span className="mockup-dot dot-red" />
                                        <span className="mockup-dot dot-yellow" />
                                        <span className="mockup-dot dot-green" />
                                        <span className="mockup-url">https://shopvibe.jinie.app</span>
                                    </div>
                                    <div className="mockup-screen-preview" style={{ padding: 12, background: "#faf8fc" }}>
                                        <div className="mockup-navbar" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                                            <span className="mockup-brand" style={{ fontWeight: 800, color: "#221d32" }}>ShopVibe</span>
                                            <span className="mockup-cart-badge" style={{ background: "#7c5ce0", color: "#fff", padding: "3px 8px", borderRadius: 12, fontSize: 10, fontWeight: 700 }}>Cart (3)</span>
                                        </div>
                                        <div className="mockup-hero-banner" style={{ background: "linear-gradient(135deg, #7c5ce0, #5c3eb8)", color: "#fff", padding: "12px 14px", borderRadius: 12, marginBottom: 12 }}>
                                            <span style={{ fontSize: 10, letterSpacing: 1, opacity: 0.9 }}>SUMMER EDIT</span>
                                            <h4 style={{ margin: "4px 0", fontSize: 14 }}>Luxury Essentials</h4>
                                        </div>
                                        <div className="mockup-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                                            <div className="mockup-card" style={{ background: "#fff", borderRadius: 10, padding: 6, border: "1px solid #eee", boxShadow: "0 2px 6px rgba(0,0,0,0.04)" }}>
                                                <img src="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300&auto=format&fit=crop&q=80" alt="Linen Shirt" style={{ width: "100%", height: 65, objectFit: "cover", borderRadius: 6 }} />
                                                <div style={{ fontSize: 10, fontWeight: 700, marginTop: 4 }}>Linen Overshirt</div>
                                                <div style={{ fontSize: 10, color: "#7c5ce0", fontWeight: 800 }}>Rs. 3,990</div>
                                            </div>
                                            <div className="mockup-card" style={{ background: "#fff", borderRadius: 10, padding: 6, border: "1px solid #eee", boxShadow: "0 2px 6px rgba(0,0,0,0.04)" }}>
                                                <img src="https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&auto=format&fit=crop&q=80" alt="Leather Jacket" style={{ width: "100%", height: 65, objectFit: "cover", borderRadius: 6 }} />
                                                <div style={{ fontSize: 10, fontWeight: 700, marginTop: 4 }}>Classic Jacket</div>
                                                <div style={{ fontSize: 10, color: "#7c5ce0", fontWeight: 800 }}>Rs. 7,490</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Showcase Grid */}
                <section className="showcase-grid-section">
                    <h2 className="section-title">More Generated Showcase Apps</h2>
                    <div className="showcase-grid">
                        {apps.map((app, idx) => {
                            const demoImages = [
                                "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&auto=format&fit=crop&q=80", // food
                                "https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?w=400&auto=format&fit=crop&q=80", // kanban
                                "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=400&auto=format&fit=crop&q=80", // fitness
                                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=400&auto=format&fit=crop&q=80", // real estate
                                "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=80", // ai chat
                            ];
                            const previewImg = demoImages[idx % demoImages.length];

                            return (
                                <div key={idx} className="showcase-card">
                                    <div className="showcase-mockup" style={{ position: "relative", overflow: "hidden", height: 160 }}>
                                        <div className="mockup-header" style={{ position: "relative", zIndex: 2, background: "rgba(255,255,255,0.9)" }}>
                                            <span className="mockup-dot dot-red" />
                                            <span className="mockup-dot dot-yellow" />
                                            <span className="mockup-dot dot-green" />
                                            <span style={{ fontSize: 9, color: "#888", marginLeft: 4 }}>app preview</span>
                                        </div>
                                        <img
                                            src={previewImg}
                                            alt={app.name}
                                            style={{
                                                position: "absolute",
                                                top: 24,
                                                left: 0,
                                                width: "100%",
                                                height: "calc(100% - 24px)",
                                                objectFit: "cover",
                                            }}
                                        />
                                        <div
                                            style={{
                                                position: "absolute",
                                                bottom: 0,
                                                left: 0,
                                                right: 0,
                                                background: "linear-gradient(transparent, rgba(15,23,42,0.85))",
                                                padding: "16px 12px 6px",
                                                color: "#fff",
                                                zIndex: 2,
                                            }}
                                        >
                                            <span style={{ fontSize: 11, fontWeight: 700 }}>{app.name}</span>
                                        </div>
                                    </div>

                                    <div className="showcase-card-body">
                                        <span className="showcase-category">{app.category}</span>
                                        <h3 className="showcase-card-title">{app.name}</h3>
                                        <p className="showcase-prompt-text">{app.prompt}</p>
                                        <p className="showcase-card-desc">{app.description}</p>
                                        <div className="showcase-tags">
                                            {app.tags.map((t, tIdx) => (
                                                <span key={tIdx} className="showcase-tag">
                                                    {t}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>

                <section className="showcase-cta">
                    <h2>Want your app showcased here?</h2>
                    <p>Enter your idea in Jinie and deploy your live web application in seconds.</p>
                    <button className="primary-button" onClick={() => navigate("/")}>
                        Build Your App Now →
                    </button>
                </section>
            </main>

            <Footer />
        </div>
    );
}
