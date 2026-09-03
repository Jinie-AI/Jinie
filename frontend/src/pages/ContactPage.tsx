import { useState } from "react";
import Header from "../components/common/Header";
import Footer from "../components/common/Footer";

export default function ContactPage() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        subject: "General Inquiry",
        message: "",
    });
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || !formData.email || !formData.message) return;

        setIsSubmitting(true);
        setTimeout(() => {
            setIsSubmitting(false);
            setIsSubmitted(true);
            setFormData({ name: "", email: "", subject: "General Inquiry", message: "" });
        }, 1200);
    };

    return (
        <div className="contact-page">
            <Header />

            <main className="contact-content">
                <section className="contact-hero">
                    <span className="hero-badge">✦ GET IN TOUCH ✦</span>
                    <h1>
                        We'd Love to
                        <span> Hear From You.</span>
                    </h1>
                    <p className="hero-description">
                        Have questions about Jinie, feature requests, or partnership opportunities? Send us a message and our team will get back to you.
                    </p>
                </section>

                <section className="contact-grid-container">
                    {/* Left: Contact Info Cards */}
                    <div className="contact-info-col">
                        <div className="info-card">
                            <div className="info-icon">✉️</div>
                            <h3>Direct Email</h3>
                            <p>Send an email anytime. We respond within 24 hours.</p>
                            <a href="mailto:contact@jinie.ai" className="info-link">
                                contact@jinie.ai →
                            </a>
                        </div>

                        <div className="info-card">
                            <div className="info-icon">💬</div>
                            <h3>Discord Community</h3>
                            <p>Join our Discord to chat live with developers and creators.</p>
                            <a href="https://discord.com" target="_blank" rel="noopener noreferrer" className="info-link">
                                Join Discord →
                            </a>
                        </div>

                        <div className="info-card">
                            <div className="info-icon">🐙</div>
                            <h3>GitHub Repository</h3>
                            <p>Explore the codebase, report bugs, or contribute features.</p>
                            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="info-link">
                                Visit GitHub →
                            </a>
                        </div>
                    </div>

                    {/* Right: Contact Form */}
                    <div className="contact-form-col">
                        <div className="contact-form-card">
                            <h2>Send Us a Message</h2>

                            {isSubmitted ? (
                                <div className="contact-success-box">
                                    <div className="success-icon">✓</div>
                                    <h3>Message Received!</h3>
                                    <p>
                                        Thank you for contacting Jinie. Our team will review your message and reply to your email address shortly.
                                    </p>
                                    <button
                                        className="secondary-button"
                                        onClick={() => setIsSubmitted(false)}
                                    >
                                        Send Another Message
                                    </button>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit} className="contact-form">
                                    <div className="form-group">
                                        <label htmlFor="name">Full Name</label>
                                        <input
                                            id="name"
                                            type="text"
                                            placeholder="Enter your name"
                                            value={formData.name}
                                            onChange={(e) =>
                                                setFormData({ ...formData, name: e.target.value })
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="email">Email Address</label>
                                        <input
                                            id="email"
                                            type="email"
                                            placeholder="you@example.com"
                                            value={formData.email}
                                            onChange={(e) =>
                                                setFormData({ ...formData, email: e.target.value })
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="subject">Topic</label>
                                        <select
                                            id="subject"
                                            value={formData.subject}
                                            onChange={(e) =>
                                                setFormData({ ...formData, subject: e.target.value })
                                            }
                                        >
                                            <option value="General Inquiry">General Inquiry</option>
                                            <option value="Feature Request">Feature Request</option>
                                            <option value="Bug Report">Bug Report</option>
                                            <option value="Partnership">Partnership</option>
                                        </select>
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="message">Message</label>
                                        <textarea
                                            id="message"
                                            rows={5}
                                            placeholder="How can we help you build with Jinie?"
                                            value={formData.message}
                                            onChange={(e) =>
                                                setFormData({ ...formData, message: e.target.value })
                                            }
                                            required
                                        />
                                    </div>

                                    <button
                                        type="submit"
                                        className="primary-button submit-button"
                                        disabled={isSubmitting}
                                    >
                                        {isSubmitting ? "Sending..." : "Submit Message →"}
                                    </button>
                                </form>
                            )}
                        </div>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}
