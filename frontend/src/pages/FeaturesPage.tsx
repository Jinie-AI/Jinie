import Header from "../components/common/Header";
import Footer from "../components/common/Footer";
import { useNavigate } from "react-router-dom";

export default function FeaturesPage() {
    const navigate = useNavigate();

    const features = [
        {
            icon: "⚡",
            badge: "Natural Language AI",
            title: "NLP Requirement Extraction",
            description:
                "Transforms conversational prompts into detailed Software Requirements Specifications (SRS) with entities, user journeys, and technical constraints.",
            tags: ["GPT-4o", "SRS Spec", "Entity Mapping"],
        },
        {
            icon: "🎨",
            badge: "Visual System",
            title: "Design Token Picker",
            description:
                "Curates cohesive visual themes, custom color palettes, typography pairings, and layout structures tailored to your app idea.",
            tags: ["Color Palettes", "Google Fonts", "Dark/Light Modes"],
        },
        {
            icon: "💻",
            badge: "Production Code",
            title: "React & TypeScript Synthesis",
            description:
                "Generates clean, maintainable, modular React code with state management, interactive hooks, and responsive CSS styling.",
            tags: ["React 19", "TypeScript", "Modular JSX"],
        },
        {
            icon: "🛡️",
            badge: "Quality Control",
            title: "Preflight Verification Testing",
            description:
                "Executes static analysis, syntax validation, and route integrity checks prior to deployment to ensure zero runtime breaks.",
            tags: ["AST Check", "Route Validation", "Linter Clean"],
        },
        {
            icon: "🚀",
            badge: "Cloud Hosting",
            title: "Firebase Live Deployment",
            description:
                "Publishes your generated application directly to production cloud hosting with live public URLs and instant updates.",
            tags: ["Firebase Hosting", "SSL Included", "CDN Speed"],
        },
        {
            icon: "🌐",
            badge: "Global Input",
            title: "Multilingual Prompt Support",
            description:
                "Full support for English, Roman Urdu, and colloquial descriptions. Speak naturally in your native phrasing.",
            tags: ["Roman Urdu", "English", "Multilingual NLP"],
        },
    ];

    return (
        <div className="features-page">
            <Header />

            <main className="features-content">
                <section className="features-hero">
                    <span className="hero-badge">✦ POWERFUL CAPABILITIES ✦</span>
                    <h1>
                        Built for Modern
                        <span> Software Generation.</span>
                    </h1>
                    <p className="hero-description">
                        Jinie combines deep NLP requirement analysis with automated code compilation to transform raw ideas into live, production-ready applications.
                    </p>
                </section>

                <section className="features-grid-section">
                    <div className="features-grid">
                        {features.map((item, idx) => (
                            <div key={idx} className="feature-card">
                                <div className="feature-card-header">
                                    <div className="feature-icon-wrapper">
                                        <span className="feature-icon">{item.icon}</span>
                                    </div>
                                    <span className="feature-badge">{item.badge}</span>
                                </div>
                                <h3 className="feature-title">{item.title}</h3>
                                <p className="feature-description">{item.description}</p>
                                <div className="feature-tags">
                                    {item.tags.map((tag, tIdx) => (
                                        <span key={tIdx} className="feature-tag">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="capabilities-banner">
                    <div className="capabilities-card">
                        <div className="capabilities-info">
                            <h2>Ready to turn your prompt into software?</h2>
                            <p>
                                Join thousands of creators building applications automatically with Jinie's 7-stage engine.
                            </p>
                        </div>
                        <button className="primary-button" onClick={() => navigate("/")}>
                            Start Building Now →
                        </button>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}
