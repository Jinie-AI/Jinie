import "../styles/brand.css";

export default function BrandLogo() {
  return (
    <span className="brand-logo" role="img" aria-label="Jinie">
      <img className="brand-logo-dark" src="/branding/jinie-dark.png" alt="" width="853" height="382" />
      <img className="brand-logo-purple" src="/branding/jinie-purple.png" alt="" width="853" height="382" />
    </span>
  );
}
