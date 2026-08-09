import type { DeploymentData } from "../../types/project.types";
import Section from "../common/Section";

interface DeploymentSectionProps {
    data: DeploymentData;
}

export default function DeploymentSection({
    data,
}: DeploymentSectionProps) {
    return (
        <Section
            eyebrow="04 · Deployment"
            title="Your app is ready."
        >
            <div className="deployment-card">

                <div className="deployment-icon">
                    ✓
                </div>

                <h3>
                    Successfully deployed
                </h3>

                <p>
                    Your application has been compiled and deployed.
                </p>

                <a
                    href={data.url}
                    target="_blank"
                    rel="noreferrer"
                    className="deployment-link"
                >
                    {data.url}
                    <span>↗</span>
                </a>

                <a
                    href={data.url}
                    target="_blank"
                    rel="noreferrer"
                    className="open-app"
                >
                    Open App
                </a>

            </div>
        </Section>
    );
}