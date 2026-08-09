interface DesignSectionProps {
    onApprove: () => void;
}

export default function DesignSection({
    onApprove,
}: DesignSectionProps) {
    return (
        <div className="section-card design-panel">
            <div className="design-panel__header">
                <div>
                    <span className="stage-label">03 · Design</span>
                    <h1>Application Design</h1>
                    <p>
                        Jinie turned your requirements into a clear interface
                        structure ready for implementation.
                    </p>
                </div>

                <div className="design-panel__status">
                    <span className="design-panel__status-dot" />
                    Design ready
                </div>
            </div>

            <div className="design-layout">
                <div className="design-sidebar">
                    <span className="design-sidebar__label">Design system</span>

                    <div className="design-color-row">
                        <span className="color-swatch color-swatch--primary" />
                        <span className="color-swatch color-swatch--soft" />
                        <span className="color-swatch color-swatch--dark" />
                    </div>

                    <div className="design-detail">
                        <span>Style</span>
                        <strong>Modern & clean</strong>
                    </div>

                    <div className="design-detail">
                        <span>Layout</span>
                        <strong>Mobile first</strong>
                    </div>

                    <div className="design-detail">
                        <span>Components</span>
                        <strong>Cards, forms & lists</strong>
                    </div>
                </div>

                <div className="design-preview">
                    <div className="mock-screen">
                        <div className="mock-header">
                            <div className="mock-logo">J</div>
                            <span>Your App</span>
                            <div className="mock-avatar" />
                        </div>

                        <div className="mock-content">
                            <span className="mock-eyebrow">WELCOME BACK</span>
                            <h3>Everything in one place.</h3>
                            <div className="mock-search">Search your workspace</div>

                            <div className="mock-stat-grid">
                                <div className="mock-stat">
                                    <strong>24</strong>
                                    <span>Active items</span>
                                </div>

                                <div className="mock-stat">
                                    <strong>86%</strong>
                                    <span>Progress</span>
                                </div>
                            </div>

                            <div className="mock-card">
                                <div className="mock-card__icon">✦</div>
                                <div>
                                    <strong>Recent activity</strong>
                                    <span>Your project is ready to review</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="design-actions">
                <div>
                    <strong>Happy with the direction?</strong>
                    <span>You can continue to the interactive preview.</span>
                </div>

                <button className="primary-button" onClick={onApprove}>
                    Approve Design <span>→</span>
                </button>
            </div>
        </div>
    );
}