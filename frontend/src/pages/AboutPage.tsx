import Header from "../components/common/Header";
import Footer from "../components/common/Footer";

export default function AboutPage() {
    const team = [
        {
            name: "Ansa Anwaar",
            role: "AI Systems Lead & NLP Specialist",
            avatar: "AA",
            gradient: "linear-gradient(135deg, #a855f7, #6b21a8)",
            bio: "Focuses on prompt decomposition, natural language requirement extraction, and multi-lingual intent parsing.",
            socials: { github: "#", linkedin: "#" },
        },
        {
            name: "Chaudry Ali Sher",
            role: "Compiler Architecture & Systems Engineer",
            avatar: "CA",
            gradient: "linear-gradient(135deg, #6b21a8, #f5c518)",
            bio: "Architected the 7-stage refactored compiler engine, component generator, AST preflight verification, and Firebase deployment pipeline.",
            socials: { github: "#", linkedin: "#" },
        },
        {
            name: "Kaneez Zehra",
            role: "Frontend Architect & Design System Specialist",
            avatar: "KZ",
            gradient: "linear-gradient(135deg, #f5c518, #a855f7)",
            bio: "Leads the purple-gold design token framework, component styling hierarchy, and interactive workspace UI/UX.",
            socials: { github: "#", linkedin: "#" },
        },
    ];

    return (
        <div className="about-page">
            <Header />

            <main className="about-content">
                <section className="about-hero">
                    <span className="hero-badge">✦ OUR MISSION & TEAM ✦</span>
                    <h1>
                        Reinventing How
                        <span> Software is Built.</span>
                    </h1>
                    <p className="hero-description">
                        Jinie was created to bridge the gap between human imagination and software engineering — empowering anyone to turn natural language prompts into live, production-grade applications.
                    </p>
                </section>

                <section className="story-section">
                    <div className="story-card">
                        <div className="story-badge">THE JINIE STORY</div>
                        <h2>Autonomous App Generation from First Principles</h2>
                        <p>
                            Traditional software development requires weeks of requirements gathering, design system design, component scaffolding, and deployment configuration. Jinie automates this entire lifecycle into a seamless 7-stage engine.
                        </p>
                        <p>
                            By combining large language models for SRS extraction with a deterministic React compiler, Jinie guarantees both creative freedom in prompting and structural rigor in generated code.
                        </p>
                    </div>
                </section>

                <section className="team-section">
                    <div className="team-header">
                        <span className="section-eyebrow">CONTRIBUTORS</span>
                        <h2>Meet the Creators</h2>
                        <p>The team behind Jinie's autonomous software generation engine.</p>
                    </div>

                    <div className="team-grid">
                        {team.map((member, idx) => (
                            <div key={idx} className="team-card">
                                <div
                                    className="team-avatar"
                                    style={{ background: member.gradient }}
                                >
                                    {member.avatar}
                                </div>
                                <h3 className="team-name">{member.name}</h3>
                                <span className="team-role">{member.role}</span>
                                <p className="team-bio">{member.bio}</p>
                                <div className="team-footer-tag">Project Contributor</div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="tech-stack-section">
                    <h2>Engineered with Modern Tech Stack</h2>
                    <div className="tech-pills">
                        <span className="tech-pill">React 19</span>
                        <span className="tech-pill">TypeScript</span>
                        <span className="tech-pill">Vite</span>
                        <span className="tech-pill">Python FastAPI</span>
                        <span className="tech-pill">AST Validation</span>
                        <span className="tech-pill">Firebase Hosting</span>
                        <span className="tech-pill">Design Tokens</span>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}
