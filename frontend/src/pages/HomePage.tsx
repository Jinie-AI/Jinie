import { useState } from "react";
import { useNavigate } from "react-router-dom";
import jinieLogo from "../assets/logo_jinie.png";
import { generateSRS } from "../services/JinieService";

export default function HomePage() {
    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        setLoading(true);
        setError("");

        try {
            const srs = await generateSRS(prompt);

            localStorage.setItem("jinie_prompt", prompt);
            localStorage.setItem("jinie_srs", JSON.stringify(srs));

            navigate("/workspace");
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Unable to generate the SRS. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="home-page">
            <header className="home-header">
                <div className="logo">
                    <img src={jinieLogo} alt="Jinie" className="logo-image" />
                    <span>Jinie</span>
                </div>

                <div className="header-actions">
                    <button className="secondary-button">Documentation</button>
                    <button className="secondary-button">GitHub</button>
                </div>
            </header>

            <main className="home-content">
                <h1>
                    Turn your idea into an
                    <span> application.</span>
                </h1>

                <p className="hero-description">
                    Describe what you want to build and Jinie will transform
                    your idea into a complete software plan.
                </p>

                <div className="prompt-card">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe the application you want to build..."
                        rows={6}
                        disabled={loading}
                    />

                    <div className="prompt-footer">
                        <span className="prompt-hint">
                            {error && <span className="home-error">{error}</span>}
                        </span>

                        <button
                            className="primary-button"
                            onClick={handleGenerate}
                            disabled={!prompt.trim() || loading}
                        >
                            {loading ? "Generating SRS…" : "Generate SRS"}
                            <span>→</span>
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}