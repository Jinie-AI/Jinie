import { useState } from "react";

import {
    mockSRS,
    mockDesign,
    mockPreview,
    mockDeployment,
} from "../data/mockProject";

import type {
    WorkflowStage,
    SRSData,
    DesignData,
    PreviewData,
    DeploymentData,
} from "../types/project.types";

export default function useJinieWorkflow() {
    const [stage, setStage] =
        useState<WorkflowStage>("idle");

    const [prompt, setPrompt] = useState("");

    const [srs, setSRS] =
        useState<SRSData | null>(null);

    const [design, setDesign] =
        useState<DesignData | null>(null);

    const [preview, setPreview] =
        useState<PreviewData | null>(null);

    const [deployment, setDeployment] =
        useState<DeploymentData | null>(null);

    const generate = (userPrompt: string) => {
        setPrompt(userPrompt);

        // Temporary mock response.
        // Replace with your backend API later.
        setSRS(mockSRS);

        setStage("srs");
    };

    const approveSRS = () => {
        setDesign(mockDesign);
        setStage("design");
    };

    const approveDesign = () => {
        setPreview(mockPreview);
        setStage("preview");
    };

    const approvePreview = () => {
        setDeployment(mockDeployment);
        setStage("deployment");
    };

    return {
        stage,
        prompt,
        srs,
        design,
        preview,
        deployment,

        generate,
        approveSRS,
        approveDesign,
        approvePreview,
    };
}