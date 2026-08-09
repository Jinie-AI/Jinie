interface PreviewSectionProps {
    onDeploy: () => void;
}

export default function PreviewSection({
    onDeploy,
}: PreviewSectionProps) {
    return (
        <div className="section-card">
            <span className="stage-label">03</span>

            <h1>Your Application</h1>

            <p>
                Your application has been generated. Review the final
                preview before deployment.
            </p>

            <div className="app-preview">
                <div className="preview-window">
                    <div className="preview-bar">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>

                    <div className="preview-body">
                        <h2>Your generated application</h2>
                        <p>Everything is ready to deploy.</p>
                    </div>
                </div>
            </div>

            <button onClick={onDeploy}>
                Deploy Application →
            </button>
        </div>
    );
}