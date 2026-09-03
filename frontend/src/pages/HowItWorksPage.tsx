import Header from "../components/common/Header";
import Footer from "../components/common/Footer";
import { useNavigate } from "react-router-dom";

export default function HowItWorksPage() {
    const navigate = useNavigate();

    const pipelineSteps = [
        {
            stage: "01",
            title: "Prompt Intake",
            subtitle: "Natural Language Processing",
            description:
                "Express your app concept in simple English, Roman Urdu, or informal notes. Jinie parses your text to identify core functionalities, user roles, and data structures.",
            details: ["Multi-lingual parsing", "Intent classification", "Constraint identification"],
            icon: "📝",
        },
        {
            stage: "02",
            title: "SRS Generation",
            subtitle: "Software Requirements Specification",
            description:
                "Jinie synthesizes a complete SRS document listing target screens, data models, functional flows, and non-functional guarantees.",
            details: ["Screen mapping", "Data entity schema", "System architecture outline"],
            icon: "📋",
        },
        {
            stage: "03",
            title: "Design Tokens",
            subtitle: "Visual System & Styling",
            description:
                "Automated design system creation tailored to your app theme. Selects color palettes, typography pairs, button variants, and layout rules.",
            details: ["Color hex generation", "Google Font pairing", "Component theme tokens"],
            icon: "🎨",
        },
        {
            stage: "04",
            title: "User Approval",
            subtitle: "Human-in-the-Loop Review",
            description:
                "Review and refine the generated SRS and design specifications in the interactive Jinie workspace before initiating code compilation.",
            details: ["Interactive workspace", "Custom token tweaks", "One-click approval"],
            icon: "✅",
        },
        {
            stage: "05",
            title: "Compilation Engine",
            subtitle: "Code Assembly",
            description:
                "Our refactored compiler engine constructs modular React 19 components, route configurations, state hooks, and CSS styling rules.",
            details: ["React JSX generation", "State hook binding", "Layout synthesis"],
            icon: "⚙️",
        },
        {
            stage: "06",
            title: "Verification Testing",
            subtitle: "Preflight Quality Assurance",
            description:
                "Static AST analysis, route integrity checks, and dependency validation run automatically to guarantee bug-free compilation.",
            details: ["AST tree validation", "Broken link detection", "Accessibility checks"],
            icon: "🧪",
        },
        {
            stage: "07",
            title: "Live Deployment",
            subtitle: "Cloud Publishing",
            description:
                "Your application is bundled and deployed to Firebase cloud hosting with an active public SSL URL ready to share worldwide.",
            details: ["One-click publish", "SSL security", "Production CDN hosting"],
            icon: "🚀",
        },
    ];

    return (
        <div className="how-it-works-page">
            <Header />

            <main className="how-it-works-content">
                <section className="how-it-works-hero">
                    <span className="hero-badge">✦ THE 7-STAGE PIPELINE ✦</span>
                    <h1>
                        How Jinie Builds
                        <span> Your Application.</span>
                    </h1>
                    <p className="hero-description">
                        From raw idea to live deployed web app — explore the autonomous 7-stage engine powering Jinie.
                    </p>
                </section>

                <section className="stepper-section">
                    <div className="vertical-stepper">
                        {pipelineSteps.map((step, idx) => (
                            <div key={idx} className="stepper-item">
                                <div className="stepper-left">
                                    <div className="stepper-circle">
                                        <span>{step.stage}</span>
                                    </div>
                                    {idx < pipelineSteps.length - 1 && (
                                        <div className="stepper-connector" />
                                    )}
                                </div>

                                <div className="stepper-card">
                                    <div className="stepper-card-header">
                                        <span className="stepper-icon">{step.icon}</span>
                                        <div>
                                            <h3 className="stepper-title">{step.title}</h3>
                                            <span className="stepper-subtitle">{step.subtitle}</span>
                                        </div>
                                    </div>
                                    <p className="stepper-desc">{step.description}</p>
                                    <div className="stepper-details">
                                        {step.details.map((detail, dIdx) => (
                                            <span key={dIdx} className="detail-tag">
                                                ✓ {detail}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="stepper-cta">
                    <h2>Test the Pipeline Yourself</h2>
                    <p>Enter a prompt and watch Jinie run through all 7 stages in real-time.</p>
                    <button className="primary-button" onClick={() => navigate("/")}>
                        Launch Workspace →
                    </button>
                </section>
            </main>

            <Footer />
        </div>
    );
}
