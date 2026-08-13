import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import WorkflowStepper from "../components/workflow/WorkflowStepper";
import SRSSection from "../components/srs/SRSSection";
import DesignSection, { type DesignTokens } from "../components/design/DesignSection";
import GeneratedComponentsSection, {
    type GeneratedComponent,
} from "../components/generatedComponents/GeneratedComponentsSection";
import PreviewSection from "../components/preview/PreviewSection";

type Stage = "srs" | "design" | "components" | "preview";

export default function WorkspacePage() {
    const navigate = useNavigate();

    const [stage, setStage] = useState<Stage>("srs");
    const [prompt, setPrompt] = useState("");
    const [srs, setSrs] = useState<any>(null);
    const [designTokens, setDesignTokens] = useState<DesignTokens | null>(null);
    const [generatedComponents, setGeneratedComponents] = useState<GeneratedComponent[]>([]);

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
            return;
        }

        const savedDesignTokens = localStorage.getItem("jinie_design_tokens");
        if (savedDesignTokens) {
            try {
                setDesignTokens(JSON.parse(savedDesignTokens));
            } catch {
                localStorage.removeItem("jinie_design_tokens");
            }
        }

        const savedStage = localStorage.getItem("jinie_stage") as Stage | null;
        if (savedStage === "design" || savedStage === "components" || savedStage === "preview") {
            setStage(savedStage);
        }
    }, [navigate]);

    useEffect(() => {
        localStorage.setItem("jinie_stage", stage);
    }, [stage]);

    const handleSRSApprove = () => {
        setStage("design");
    };

    const handleDesignApprove = (tokens: DesignTokens) => {
        setDesignTokens(tokens);
        localStorage.setItem("jinie_design_tokens", JSON.stringify(tokens));
        // Real component generation happens on the next stage — this
        // click just carries the srs + design tokens forward to it.
        setStage("components");
    };

    const handleComponentsApprove = (components: GeneratedComponent[]) => {
        setGeneratedComponents(components);
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
                            srs={srs}
                            onApprove={handleDesignApprove}
                        />
                    </section>
                )}

                {stage === "components" && designTokens && (
                    <section className="workspace-section">
                        <GeneratedComponentsSection
                            srs={srs}
                            designTokens={designTokens}
                            onApprove={handleComponentsApprove}
                        />
                    </section>
                )}

                {stage === "preview" && (
                    <section className="workspace-section">
                        <PreviewSection
                            srs={srs}
                            designTokens={designTokens}
                            generatedComponents={generatedComponents}
                            onDeploy={handleDeploy}
                        />
                    </section>
                )}
            </main>
        </div>
    );
}