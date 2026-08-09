interface StatusBadgeProps {
    children: React.ReactNode;
}

export default function StatusBadge({
    children,
}: StatusBadgeProps) {
    return <span className="status-badge">{children}</span>;
}