interface DesignSectionProps {
    onApprove: () => void;
}

export default function DesignSection({
    onApprove,
}: DesignSectionProps) {
    return (
        <div className="section-card">
            <span className="stage-label">02</span>

            <h1>Application Design</h1>

            <p>
                Based on the approved requirements, Jinie generated the
                application structure and visual design.
            </p>

            <div className="design-preview">
                <div className="mock-screen">
                    <div className="mock-header">Your App</div>

                    <div className="mock-content">
                        <div className="mock-card"></div>
                        <div className="mock-card"></div>
                        <div className="mock-card"></div>
                    </div>
                </div>
            </div>

            <button onClick={onApprove}>
                Approve Design →
            </button>
        </div>
    );
}