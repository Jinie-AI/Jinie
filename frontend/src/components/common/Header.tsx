import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import jinieLogo from "../../assets/logo_jinie.png";
import { useTheme } from "../../context/ThemeContext";

export default function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();

    const handleGetStarted = () => {
        setMobileMenuOpen(false);
        navigate("/");
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const toggleMobileMenu = () => {
        setMobileMenuOpen((prev) => !prev);
    };

    const closeMobileMenu = () => {
        setMobileMenuOpen(false);
    };

    return (
        <header className="home-header common-header">
            <Link to="/" className="logo" onClick={closeMobileMenu}>
                <img src={jinieLogo} alt="Jinie Logo" className="logo-image-sm" />
                <span className="logo-text">Jinie</span>
            </Link>

            <nav className={`nav-links ${mobileMenuOpen ? "mobile-open" : ""}`}>
                <NavLink
                    to="/"
                    end
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={closeMobileMenu}
                >
                    Home
                </NavLink>
                <NavLink
                    to="/features"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={closeMobileMenu}
                >
                    Features
                </NavLink>
                <NavLink
                    to="/how-it-works"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={closeMobileMenu}
                >
                    How It Works
                </NavLink>
                <NavLink
                    to="/showcase"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={closeMobileMenu}
                >
                    Showcase
                </NavLink>
                <NavLink
                    to="/about"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={closeMobileMenu}
                >
                    About
                </NavLink>
                <NavLink
                    to="/contact"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                    onClick={closeMobileMenu}
                >
                    Contact
                </NavLink>

                <div className="mobile-cta-wrapper">
                    <button className="theme-toggle-button" onClick={toggleTheme} aria-label="Toggle Theme">
                        {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
                    </button>
                    <button className="primary-button cta-button" onClick={handleGetStarted}>
                        Get Started ✦
                    </button>
                </div>
            </nav>

            <div className="header-right">
                <button
                    className="theme-toggle-button desktop-theme-toggle"
                    onClick={toggleTheme}
                    title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
                >
                    {theme === "light" ? "🌙 Dark" : "☀️ Light"}
                </button>

                <button className="primary-button desktop-cta" onClick={handleGetStarted}>
                    Get Started ✦
                </button>

                <button
                    className={`hamburger-button ${mobileMenuOpen ? "open" : ""}`}
                    onClick={toggleMobileMenu}
                    aria-label="Toggle Navigation Menu"
                >
                    <span className="hamburger-line"></span>
                    <span className="hamburger-line"></span>
                    <span className="hamburger-line"></span>
                </button>
            </div>
        </header>
    );
}
