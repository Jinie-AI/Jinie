import { useEffect, useState } from "react";

import {
    generateSRSWithProgress,
    type SRSProgress,
} from "../../services/JinieService";


interface PromptComposerProps {
    initialPrompt?: string;

    onSubmit: (
        prompt: string,
        srs: any
    ) => void;
}


const stages = [
    {
        key: "requirements",
        label: "Analyzing project requirements",
    },
    {
        key: "functional",
        label: "Generating functional requirements",
    },
    {
        key: "non_functional",
        label: "Generating non-functional requirements",
    },
    {
        key: "sitemap",
        label: "Building application screens",
    },
    {
        key: "entities",
        label: "Identifying data entities",
    },
    {
        key: "component_tree",
        label: "Building component structure",
    },
    {
        key: "tech_stack",
        label: "Selecting technology stack",
    },
];


export default function PromptComposer({
    initialPrompt = "",
    onSubmit,
}: PromptComposerProps) {

    const [prompt, setPrompt] =
        useState(initialPrompt);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    const [progress, setProgress] =
        useState(0);

    const [currentStage, setCurrentStage] =
        useState("");


    useEffect(() => {

        setPrompt(initialPrompt);

    }, [initialPrompt]);


    const handleProgress = (
        update: SRSProgress
    ) => {

        console.log(
            "FRONTEND PROGRESS:",
            update
        );

        if (
            update.progress !== undefined
        ) {

            setProgress(
                update.progress
            );
        }

        if (update.stage) {

            setCurrentStage(
                update.stage
            );
        }
    };


    const handleGenerate = async () => {

        if (!prompt.trim()) {

            setError(
                "Please enter a project description."
            );

            return;
        }


        console.log(
            "STARTING SRS GENERATION"
        );

        setLoading(true);

        setError("");

        setProgress(5);

        setCurrentStage(
            "requirements"
        );


        try {

            const result =
                await generateSRSWithProgress(
                    prompt,
                    handleProgress
                );


            console.log(
                "SRS RESULT:",
                result
            );


            if (!result) {

                throw new Error(
                    "Backend returned no SRS result."
                );
            }


            setProgress(100);

            setCurrentStage(
                "complete"
            );


            console.log(
                "SRS GENERATION COMPLETE"
            );


            onSubmit(
                prompt,
                result
            );


        } catch (err) {

            console.error(
                "SRS GENERATION ERROR:",
                err
            );


            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to generate SRS."
            );


        } finally {

            setLoading(false);

        }
    };


    const currentIndex =
        stages.findIndex(
            (stage) =>
                stage.key === currentStage
        );


    return (

        <div className="prompt-composer">


            {/* PROMPT */}

            {!loading && (

                <div className="prompt-composer__card">

                    <textarea
                        value={prompt}
                        onChange={(e) =>
                            setPrompt(
                                e.target.value
                            )
                        }
                        placeholder="Describe the application you want to build..."
                    />

                    <div className="prompt-composer__footer">

                        <span className="prompt-composer__count">
                            {prompt.length} characters
                        </span>

                        <button
                            className="primary-button prompt-composer__submit"
                            onClick={handleGenerate}
                            disabled={!prompt.trim()}
                        >
                            Generate SRS →
                        </button>

                    </div>

                </div>

            )}


            {/* LOADING */}

            {loading && (

                <div className="srs-progress">

                    <div className="srs-progress-header">

                        <div>

                            <strong>
                                Generating your SRS
                            </strong>

                            <p>
                                {stages.find(
                                    (stage) =>
                                        stage.key === currentStage
                                )?.label
                                    || "Jinie is processing your project..."}
                            </p>

                        </div>


                        <strong>
                            {progress}%
                        </strong>

                    </div>


                    <div className="srs-progress-bar">

                        <div
                            className="srs-progress-fill"
                            style={{
                                width:
                                    `${progress}%`,
                            }}
                        />

                    </div>


                    <div className="srs-stage-list">

                        {stages.map(
                            (
                                stage,
                                index
                            ) => {

                                const completed =
                                    index <
                                    currentIndex;

                                const active =
                                    index ===
                                    currentIndex;


                                return (

                                    <div
                                        key={
                                            stage.key
                                        }
                                        className={
                                            `srs-stage ${completed
                                                ? "completed"
                                                : ""
                                            } ${active
                                                ? "active"
                                                : ""
                                            }`
                                        }
                                    >

                                        <span className="stage-icon">

                                            {completed
                                                ? "✓"
                                                : active
                                                    ? "●"
                                                    : "○"}

                                        </span>


                                        <span>
                                            {stage.label}
                                        </span>

                                    </div>

                                );

                            }
                        )}

                    </div>

                </div>

            )}


            {/* ERROR */}

            {error && (

                <div className="srs-error">

                    {error}

                </div>

            )}

        </div>
    );
}