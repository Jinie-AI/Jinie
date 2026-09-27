import type { PointerEventHandler } from "react";

interface Props {
  onPointerMove: PointerEventHandler<HTMLDivElement>;
  onPointerLeave: PointerEventHandler<HTMLDivElement>;
}

export default function PromptHero({ onPointerMove, onPointerLeave }: Props) {
  return (
    <div className="hero-studio">
      <div className="hero-copy">
        <div className="eyebrow">
          <span /> JINIE / DESIGN TO NATIVE
        </div>
        <h1>
          Dream it.
          <br />
          <em>Make it real.</em>
        </h1>
        <p>
          Your next mobile experience starts with a conversation. Describe it,
          shape the details, and bring it to life.
        </p>
        <div className="hero-tags">
          <span>✦ React Native output</span>
          <span>◈ Traceable by design</span>
        </div>
      </div>
      <div
        className="hero-scene"
        aria-hidden="true"
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
      >
        <div className="scene-aura" />
        <div className="star-field">
          <i />
          <i />
          <i />
          <i />
          <i />
        </div>
        <div className="orbit orbit-one" />
        <div className="orbit orbit-two" />
        <div className="scene-glow" />
        <div className="floating-card badge-one">
          <span>✧</span>
          <div>
            Idea, meet interface.
            <small>Designed around your brief</small>
          </div>
        </div>
        <div className="phone-float">
          <div className="scene-phone">
            <div className="phone-island" />
            <div className="mini-brand">
              THE EVERYDAY EDIT <span>◈</span>
            </div>
            <div className="mini-hero">
              <small>A NEW PERSPECTIVE</small>
              <b>
                Less ordinary.
                <br />
                More you.
              </b>
              <span>Explore collection ↗</span>
              <div className="sculpture">
                <i />
                <i />
                <i />
              </div>
            </div>
            <div className="mini-label">
              Made for your everyday <span>→</span>
            </div>
            <div className="mini-products">
              <div>
                <span>✺</span>
                <small>The essentials</small>
                <b>Rs. 2,490</b>
              </div>
              <div>
                <span>◈</span>
                <small>New discoveries</small>
                <b>Rs. 3,990</b>
              </div>
            </div>
            <div className="mini-nav">⌂ ◇ ⌕ ♡</div>
          </div>
        </div>
        <div className="floating-card badge-two">
          <span>✓</span>
          <div>
            Beyond a mockup.<small>Editable native source</small>
          </div>
        </div>
        <div className="scene-caption">YOUR NEXT APP, TAKING SHAPE</div>
      </div>
    </div>
  );
}
