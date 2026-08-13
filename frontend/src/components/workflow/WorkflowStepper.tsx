type StageId = "prompt" | "srs" | "design" | "components" | "preview";

interface WorkflowStepperProps {
    currentStage: StageId;
}

const stages: {
    id: StageId;
    number: string;
    title: string;
    description: string;
}[] = [
        {
            id: "prompt",
            number: "01",
            title: "Prompt",
            description: "Describe your idea",
        },
        {
            id: "srs",
            number: "02",
            title: "Requirements",
            description: "Generate SRS",
        },
        {
            id: "design",
            number: "03",
            title: "Design",
            description: "Create UI",
        },
        {
            id: "components",
            number: "04",
            title: "Components",
            description: "Generate components",
        },
        {
            id: "preview",
            number: "05",
            title: "Preview",
            description: "Review application",
        },
    ];

export default function WorkflowStepper({
    currentStage,
}: WorkflowStepperProps) {
    const currentIndex = stages.findIndex(
        (stage) => stage.id === currentStage
    );

    return (
        <div className="workflow-stepper">
            {stages.map((stage, index) => {
                const isActive = stage.id === currentStage;
                const isCompleted = index < currentIndex;

                return (
                    <div
                        key={stage.id}
                        className={`workflow-step ${isActive ? "active" : ""
                            } ${isCompleted ? "completed" : ""}`}
                    >
                        <div className="workflow-step-number">
                            {isCompleted ? "✓" : stage.number}
                        </div>

                        <div className="workflow-step-info">
                            <strong>{stage.title}</strong>
                            <span>{stage.description}</span>
                        </div>

                        {index !== stages.length - 1 && (
                            <div
                                className={`workflow-line ${isCompleted ? "completed" : ""
                                    }`}
                            />
                        )}
                    </div>
                );
            })}
        </div>
    );
}