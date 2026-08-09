interface SectionProps {
    eyebrow: string;
    title: string;
    children: React.ReactNode;
}

export default function Section({
    eyebrow,
    title,
    children,
}: SectionProps) {
    return (
        <section className="workflow-section">
            <div className="section-heading">
                <span className="eyebrow">{eyebrow}</span>
                <h2>{title}</h2>
            </div>

            {children}
        </section>
    );
}