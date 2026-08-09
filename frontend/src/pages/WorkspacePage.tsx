import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import WorkflowStepper from "../components/workflow/WorkflowStepper";
import SRSSection from "../components/srs/SRSSection";
import DesignSection from "../components/design/DesignSection";
import PreviewSection from "../components/preview/PreviewSection";

type Stage = "srs" | "design" | "preview";

export default function WorkspacePage() {
    const navigate = useNavigate();

    const [stage, setStage] = useState<Stage>("srs");
    const [prompt, setPrompt] = useState("");
    const [srs, setSrs] = useState<any>(null);

    useEffect(() => {
        const savedPrompt = localStorage.getItem("jinie_prompt");
        const savedSRS = localStorage.getItem("jinie_srs");

        if (!savedPrompt || !savedSRS) {
            navigate("/");
            return;
        }

        try {
            setPrompt(savedPrompt);
            setSrs(JSON.parse(savedSRS));
        } catch {
            localStorage.removeItem("jinie_srs");
            navigate("/");
        }
    }, [navigate]);

    const handleSRSApprove = () => {
        setStage("design");
    };

    const handleDesignApprove = () => {
        setStage("preview");
    };

    const handleDeploy = () => {
        navigate("/deploy");
    };

    if (!srs) {
        return null;
    }

    return (
        <div className="workspace-page">
            <header className="workspace-header">
                <div className="logo">
                    <span className="logo-mark">J</span>
                    <span>Jinie</span>
                </div>

                <div className="workspace-title">
                    <span>Workspace</span>
                    <small>{prompt}</small>
                </div>

                <button
                    className="secondary-button"
                    onClick={() => navigate("/")}
                >
                    Exit
                </button>
            </header>

            <WorkflowStepper currentStage={stage} />

            <main className="workspace-content">
                {stage === "srs" && (
                    <section className="workspace-section">
                        <SRSSection
                            srs={srs}
                            onApprove={handleSRSApprove}
                        />
                    </section>
                )}

                {stage === "design" && (
                    <section className="workspace-section">
                        <DesignSection
                            onApprove={handleDesignApprove}
                        />
                    </section>
                )}

                {stage === "preview" && (
                    <section className="workspace-section">
                        <PreviewSection
                            onDeploy={handleDeploy}
                        />
                    </section>
                )}
            </main>
        </div>
    );
}