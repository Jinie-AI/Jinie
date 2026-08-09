import { useState } from "react";
import { useNavigate } from "react-router-dom";

type BuildStatus = "idle" | "building" | "success";

export default function DeployPage() {
    const navigate = useNavigate();

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
                <div className="logo">
                    <span className="logo-mark">J</span>
                    <span>Jinie</span>
                </div>

                <button
                    className="secondary-button"
                    onClick={() => navigate("/workspace")}
                >
                    ← Back to Workspace
                </button>
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
                        ? "Jinie successfully generated your application."
                        : "Review your application and build the final project."}
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
        </div>
    );
}