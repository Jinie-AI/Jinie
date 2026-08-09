import { useState } from "react";
import { useNavigate } from "react-router-dom";
import jinieLogo from "../assets/logo_jinie.png";

export default function HomePage() {
    const [prompt, setPrompt] = useState("");
    const navigate = useNavigate();

    const handleGenerate = () => {
        if (!prompt.trim()) return;

        localStorage.setItem("jinie_prompt", prompt);

        navigate("/workspace");
    };

    return (
        <div className="home-page">
            <header className="home-header">
                <div className="logo">
                    <img src={jinieLogo} alt="Jinie" className="logo-image" />
                    <span>Jinie</span>
                </div>

                <div className="header-actions">
                    <button className="secondary-button">
                        Documentation
                    </button>

                    <button className="secondary-button">
                        GitHub
                    </button>
                </div>
            </header>

            <main className="home-content">

                <h1>
                    Turn your idea into an
                    <span> application.</span>
                </h1>

                <p className="hero-description">
                    Describe what you want to build and Jinie will transform
                    your idea into a deployed application.
                </p>

                <div className="prompt-card">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe the application you want to build..."
                        rows={6}
                    />

                    <div className="prompt-footer">
                        <span className="prompt-hint">

                        </span>

                        <button
                            className="primary-button"
                            onClick={handleGenerate}
                            disabled={!prompt.trim()}
                        >
                            Generate
                            <span>→</span>
                        </button>
                    </div>
                </div>

            </main>
        </div>
    );
}