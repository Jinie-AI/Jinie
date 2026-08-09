import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import WorkflowStepper from "../components/workflow/WorkflowStepper";
import PromptComposer from "../components/prompt/PromptComposer";
import SRSSection from "../components/srs/SRSSection";
import DesignSection from "../components/design/DesignSection";
import PreviewSection from "../components/preview/PreviewSection";

type Stage = "prompt" | "srs" | "design" | "preview";

export default function WorkspacePage() {
    const navigate = useNavigate();

    const [stage, setStage] = useState<Stage>("prompt");
    const [prompt, setPrompt] = useState("");
    const [srs, setSrs] = useState<any>(null);

    useEffect(() => {
        const savedPrompt = localStorage.getItem("jinie_prompt");

        if (savedPrompt) {
            setPrompt(savedPrompt);
        }
    }, []);

    const handlePromptSubmit = (value: string, generatedSRS: any) => {
        setPrompt(value);
        setSrs(generatedSRS);

        localStorage.setItem("jinie_prompt", value);

        setStage("srs");
    };

    const handleSRSApprove = () => {
        setStage("design");
    };

    const handleDesignApprove = () => {
        setStage("preview");
    };

    const handleDeploy = () => {
        navigate("/deploy");
    };

    return (
        <div className="workspace-page">
            <header className="workspace-header">
                <div className="logo">
                    <span className="logo-mark">J</span>
                    <span>Jinie</span>
                </div>

                <div className="workspace-title">
                    <span>Workspace</span>
                    <small>{prompt || "New Project"}</small>
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
                {stage === "prompt" && (
                    <section className="workspace-section">
                        <PromptComposer
                            initialPrompt={prompt}
                            onSubmit={handlePromptSubmit}
                        />
                    </section>
                )}

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