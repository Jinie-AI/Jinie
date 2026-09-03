import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "../components/common/Footer";
import jinieLogo from "../assets/logo_jinie.png";
import { useTheme } from "../context/ThemeContext";

type BuildStatus = "idle" | "building" | "success";

export default function DeployPage() {
    const navigate = useNavigate();
    const { theme, toggleTheme } = useTheme();

    const [status, setStatus] = useState<BuildStatus>("idle");

    const startBuild = () => {
        setStatus("building");

        setTimeout(() => {
            setStatus("success");
        }, 2500);
    };

    return (
        <div className="deploy-page">
            <header className="workspace-header">
                <div className="logo" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
                    <img src={jinieLogo} alt="Jinie Logo" className="logo-image-sm" />
                    <span className="logo-text">Jinie</span>
                </div>

                <div className="header-actions">
                    <button className="theme-toggle-button" onClick={toggleTheme}>
                        {theme === "light" ? "🌙 Dark" : "☀️ Light"}
                    </button>
                    <button
                        className="secondary-button"
                        onClick={() => navigate("/workspace")}
                    >
                        ← Back to Workspace
                    </button>
                </div>
            </header>

            <main className="deploy-content">
                <div className="deploy-icon">
                    {status === "success" ? "✓" : "🚀"}
                </div>

                <h1>
                    {status === "success"
                        ? "Your application is ready!"
                        : "Deploy your application"}
                </h1>

                <p>
                    {status === "success"
                        ? "Jinie successfully generated and deployed your application to Firebase cloud hosting."
                        : "Review your application parameters and trigger live compilation & deployment."}
                </p>

                <div className="deployment-card">
                    <div className="deployment-row">
                        <div>
                            <strong>Application</strong>
                            <span>Jinie Generated App</span>
                        </div>

                        <span className="status-badge">
                            {status === "success" ? "Ready" : "Not deployed"}
                        </span>
                    </div>

                    <div className="deployment-row">
                        <div>
                            <strong>Build</strong>
                            <span>
                                {status === "building"
                                    ? "Building application..."
                                    : status === "success"
                                        ? "Build completed successfully"
                                        : "Ready to build"}
                            </span>
                        </div>

                        {status === "building" && (
                            <div className="loading-spinner" />
                        )}
                    </div>

                    <div className="deployment-row">
                        <div>
                            <strong>Environment</strong>
                            <span>Production</span>
                        </div>

                        <span className="environment-badge">
                            Production
                        </span>
                    </div>
                </div>

                {status === "idle" && (
                    <button
                        className="primary-button deploy-button"
                        onClick={startBuild}
                    >
                        Build & Deploy
                        <span>→</span>
                    </button>
                )}

                {status === "building" && (
                    <button
                        className="primary-button deploy-button"
                        disabled
                    >
                        Building...
                    </button>
                )}

                {status === "success" && (
                    <div className="success-actions">
                        <button className="primary-button">
                            Open Application ↗
                        </button>

                        <button
                            className="secondary-button"
                            onClick={() => navigate("/")}
                        >
                            Create Another App
                        </button>
                    </div>
                )}
            </main>

            <Footer />
        </div>
    );
}