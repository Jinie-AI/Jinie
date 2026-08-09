interface ButtonProps {
    children: React.ReactNode;
    onClick?: () => void;
    variant?: "primary" | "secondary";
    disabled?: boolean;
}

export default function Button({
    children,
    onClick,
    variant = "primary",
    disabled = false,
}: ButtonProps) {
    return (
        <button
            className={`button ${variant}`}
            onClick={onClick}
            disabled={disabled}
        >
            {children}
        </button>
    );
}