import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/common/Header";
import Footer from "../components/common/Footer";
import { generateSRS } from "../services/JinieService";

export default function HomePage() {
    const [prompt, setPrompt] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();

    const samplePrompts = [
        "Create an e-commerce fashion storefront with shopping cart & checkout",
        "Mujhe ek khane ki delivery app banani hai jisme menu aur order place ho sake",
        "Build a Kanban task manager like Trello with drag and drop columns",
        "Create a fitness logger with daily workout tracking and progress charts",
    ];

    const handleGenerate = async () => {
        if (!prompt.trim() || isGenerating) return;

        setIsGenerating(true);
        setErrorMessage("");

        try {
            const srs = await generateSRS(prompt);

            localStorage.setItem("jinie_prompt", prompt);
            localStorage.setItem("jinie_srs", JSON.stringify(srs));
            // A fresh prompt means a fresh run — clear anything left over
            // from a previous session so the workspace doesn't reopen on
            // stale design tokens or an old stage.
            localStorage.removeItem("jinie_design_tokens");
            localStorage.removeItem("jinie_stage");

            navigate("/workspace");
        } catch (error) {
            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "SRS generation failed. Please try again."
            );
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="home-page">
            <Header />

            <main className="home-content">
                <div className="hero-badge">✦ AUTONOMOUS SOFTWARE GENERATION ✦</div>

                <h1>
                    Turn your idea into an
                    <span> application.</span>
                </h1>

                <p className="hero-description">
                    Describe what you want to build and Jinie will transform
                    your idea into a complete, production-ready software plan.
                </p>

                <div className="prompt-card">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe the application you want to build (e.g. 'Build an e-commerce storefront' or 'Mujhe ek delivery app banani hai')..."
                        rows={6}
                        disabled={isGenerating}
                    />

                    <div className="prompt-footer">
                        <span className="prompt-hint">
                            {errorMessage ? (
                                <span className="home-error">{errorMessage}</span>
                            ) : (
                                <span>Try natural language or Roman Urdu</span>
                            )}
                        </span>

                        <button
                            className="primary-button"
                            onClick={handleGenerate}
                            disabled={!prompt.trim() || isGenerating}
                        >
                            {isGenerating ? "Generating…" : "Generate"}
                            <span>→</span>
                        </button>
                    </div>
                </div>

                {/* Sample Prompt Pills */}
                <div className="sample-prompts-container">
                    <span className="sample-label">Need inspiration? Try these:</span>
                    <div className="sample-pills">
                        {samplePrompts.map((pText, idx) => (
                            <button
                                key={idx}
                                className="sample-pill"
                                onClick={() => setPrompt(pText)}
                            >
                                {pText}
                            </button>
                        ))}
                    </div>
                </div>

                {/* How It Works Teaser */}
                <section className="home-teaser-section">
                    <div className="teaser-header">
                        <span className="teaser-badge">HOW IT WORKS</span>
                        <h2>4 Steps from Prompt to Production</h2>
                    </div>

                    <div className="teaser-grid">
                        <div className="teaser-card">
                            <div className="teaser-step-num">01</div>
                            <h3>Prompt Intake</h3>
                            <p>Describe your app concept in plain text or Roman Urdu.</p>
                        </div>
                        <div className="teaser-card">
                            <div className="teaser-step-num">02</div>
                            <h3>SRS Blueprint</h3>
                            <p>Jinie extracts entities, user flows, and technical requirements.</p>
                        </div>
                        <div className="teaser-card">
                            <div className="teaser-step-num">03</div>
                            <h3>Design Tokens</h3>
                            <p>Tailors color palettes, fonts, and component styling.</p>
                        </div>
                        <div className="teaser-card">
                            <div className="teaser-step-num">04</div>
                            <h3>Live Deployment</h3>
                            <p>Compiles and publishes your app to Firebase cloud hosting.</p>
                        </div>
                    </div>

                    <div className="teaser-cta">
                        <button
                            className="secondary-button"
                            onClick={() => navigate("/how-it-works")}
                        >
                            Explore Full 7-Stage Pipeline →
                        </button>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}