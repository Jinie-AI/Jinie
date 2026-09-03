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
                                    <div className="mockup-screen-preview">
                                        <div className="mockup-navbar">
                                            <span className="mockup-brand">ShopVibe</span>
                                            <span className="mockup-cart-badge">Cart (3)</span>
                                        </div>
                                        <div className="mockup-hero-banner">
                                            <span>Summer Luxury Collection</span>
                                        </div>
                                        <div className="mockup-grid">
                                            <div className="mockup-card">Product A</div>
                                            <div className="mockup-card">Product B</div>
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
                        {apps.map((app, idx) => (
                            <div key={idx} className="showcase-card">
                                <div className="showcase-mockup">
                                    <div className="mockup-header">
                                        <span className="mockup-dot dot-red" />
                                        <span className="mockup-dot dot-yellow" />
                                        <span className="mockup-dot dot-green" />
                                    </div>
                                    <div className="mockup-content-placeholder">
                                        <div className="mockup-app-icon">✦</div>
                                        <span className="mockup-app-name">{app.name}</span>
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
                        ))}
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
