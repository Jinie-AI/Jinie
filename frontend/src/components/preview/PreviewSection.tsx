interface PreviewSectionProps {
    onDeploy: () => void;
}

export default function PreviewSection({
    onDeploy,
}: PreviewSectionProps) {
    return (
        <div className="section-card preview-panel">
            <div className="preview-panel__header">
                <div>
                    <span className="stage-label">04 · Preview</span>
                    <h1>Your application is ready</h1>
                    <p>
                        Review the final product experience before deploying it.
                    </p>
                </div>

                <span className="preview-ready-badge">
                    <span /> Ready to deploy
                </span>
            </div>

            <div className="app-preview">
                <div className="preview-window">
                    <div className="preview-bar">
                        <div className="preview-dots">
                            <span />
                            <span />
                            <span />
                        </div>

                        <div className="preview-address">your-app.jinie.local</div>
                    </div>

                    <div className="preview-body">
                        <aside className="preview-nav">
                            <div className="preview-brand">
                                <span>J</span>
                                Your App
                            </div>

                            <button className="preview-nav-item active">Overview</button>
                            <button className="preview-nav-item">Projects</button>
                            <button className="preview-nav-item">Activity</button>
                            <button className="preview-nav-item">Settings</button>
                        </aside>

                        <main className="preview-main">
                            <span className="preview-main__eyebrow">WORKSPACE</span>
                            <h2>Welcome back.</h2>
                            <p>Here is a quick overview of your application.</p>

                            <div className="preview-metrics">
                                <div>
                                    <span>Projects</span>
                                    <strong>12</strong>
                                    <small>+3 this week</small>
                                </div>

                                <div>
                                    <span>Tasks completed</span>
                                    <strong>84%</strong>
                                    <small>On track</small>
                                </div>

                                <div>
                                    <span>Team members</span>
                                    <strong>8</strong>
                                    <small>All active</small>
                                </div>
                            </div>

                            <div className="preview-activity">
                                <div className="preview-activity__heading">
                                    <strong>Recent activity</strong>
                                    <span>View all</span>
                                </div>

                                <div className="preview-activity__item">
                                    <span className="activity-icon">✓</span>
                                    <p>
                                        <strong>Project requirements approved</strong>
                                        <span>Just now</span>
                                    </p>
                                </div>

                                <div className="preview-activity__item">
                                    <span className="activity-icon">✦</span>
                                    <p>
                                        <strong>New design created</strong>
                                        <span>Today</span>
                                    </p>
                                </div>
                            </div>
                        </main>
                    </div>
                </div>
            </div>

            <div className="preview-actions">
                <div>
                    <strong>Everything looks good.</strong>
                    <span>Deploy your application whenever you are ready.</span>
                </div>

                <button className="primary-button" onClick={onDeploy}>
                    Deploy Application <span>→</span>
                </button>
            </div>
        </div>
    );
}