import { Link } from "react-router-dom";
import jinieLogo from "../../assets/logo_jinie.png";

export default function Footer() {
    return (
        <footer className="common-footer">
            <div className="footer-gradient-divider" />
            <div className="footer-container">
                <div className="footer-grid">
                    {/* Column 1: Brand */}
                    <div className="footer-brand">
                        <Link to="/" className="logo footer-logo">
                            <img src={jinieLogo} alt="Jinie Logo" className="logo-image-sm" />
                            <span className="logo-text">Jinie</span>
                        </Link>
                        <p className="footer-tagline">
                            Autonomous AI software generation pipeline. Turn natural language prompts into production-ready web applications in seconds.
                        </p>
                        <div className="footer-badges">
                            <span className="gradient-badge">7-Stage Engine</span>
                            <span className="gradient-badge">Firebase Ready</span>
                        </div>
                    </div>

                    {/* Column 2: Quick Links */}
                    <div className="footer-column">
                        <h4 className="footer-title">Navigation</h4>
                        <ul className="footer-links">
                            <li><Link to="/">Home</Link></li>
                            <li><Link to="/features">Features</Link></li>
                            <li><Link to="/how-it-works">How It Works</Link></li>
                            <li><Link to="/showcase">Showcase</Link></li>
                            <li><Link to="/about">About Us</Link></li>
                            <li><Link to="/contact">Contact</Link></li>
                        </ul>
                    </div>

                    {/* Column 3: Contact Us Section */}
                    <div className="footer-column footer-contact-col">
                        <h4 className="footer-title">Contact Us</h4>
                        <p className="footer-contact-desc">
                            Have questions, feedback, or custom requests? Get in touch with our team.
                        </p>
                        <div className="footer-contact-item">
                            <span className="contact-icon">✉</span>
                            <a href="mailto:contact@jinie.ai" className="footer-mail-link">contact@jinie.ai</a>
                        </div>
                        <div className="footer-socials">
                            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-link" title="GitHub">
                                GitHub
                            </a>
                            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link" title="Twitter/X">
                                Twitter
                            </a>
                            <a href="https://discord.com" target="_blank" rel="noopener noreferrer" className="social-link" title="Discord">
                                Discord
                            </a>
                            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link" title="LinkedIn">
                                LinkedIn
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar with exact required credit line */}
                <div className="footer-bottom">
                    <div className="footer-credit">
                        Project by Ansa Anwaar, Chaudry Ali Sher, Kaneez Zehra
                    </div>
                    <div className="footer-copyright">
                        © {new Date().getFullYear()} Jinie AI Inc. All rights reserved.
                    </div>
                </div>
            </div>
        </footer>
    );
}
