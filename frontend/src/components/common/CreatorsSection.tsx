export interface Creator {
  name: string;
  initials: string;
  role: string;
  introduction: string;
  gradient: string;
  skills: string[];
}

const CREATORS: Creator[] = [
  {
    name: 'Ansa Anwaar',
    initials: 'AA',
    role: 'AI Intelligence & Architecture Lead',
    introduction:
      'Spearheads the generative AI intelligence pipeline, prompt-to-specification domain modeling, and autonomous multi-screen requirement synthesis for adaptive app workflows.',
    gradient: 'linear-gradient(135deg, #7c5ce0, #a855f7)',
    skills: ['NLP Reasoning', 'Domain Architecture', 'Intent Extraction'],
  },
  {
    name: 'Chaudry Ali Sher',
    initials: 'AS',
    role: 'Systems & Compiler Engineer',
    introduction:
      'Leads the deterministic React Native compilation engine, local-first runtime architecture, and end-to-end device acceptance verification systems for production-ready builds.',
    gradient: 'linear-gradient(135deg, #2563eb, #38bdf8)',
    skills: ['React Native', 'Compiler Pipeline', 'Local-First Runtime'],
  },
  {
    name: 'Kaneez Zehra',
    initials: 'KZ',
    role: 'Product Experience & UI/UX Lead',
    introduction:
      'Directs the interactive multi-screen customizer ergonomics, dynamic HTML/CSS preview fidelity, and intelligent design token formulation across varied commerce categories.',
    gradient: 'linear-gradient(135deg, #ec4899, #f43f5e)',
    skills: ['Interactive UI/UX', 'Design Tokens', 'Screen Systems'],
  },
];

export default function CreatorsSection() {
  return (
    <section
      className="panel creators-section"
      style={{
        marginTop: 24,
        marginBottom: 24,
        padding: '28px 32px',
        borderRadius: 20,
        background: 'var(--surface, #ffffff)',
        border: '1px solid var(--edge, #e2e5ec)',
        boxShadow: '0 4px 20px rgba(20, 24, 41, 0.03)',
      }}
    >
      {/* Section Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: 16,
          marginBottom: 24,
        }}
      >
        <div>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 9,
              letterSpacing: 1.5,
              fontWeight: 800,
              color: 'var(--accent, #7155d9)',
              textTransform: 'uppercase',
              marginBottom: 8,
            }}
          >
            <span>✦</span>
            <span>The Team Behind Jinie</span>
          </div>
          <h2
            style={{
              fontSize: 24,
              fontWeight: 700,
              margin: 0,
              color: 'var(--ink, #20232b)',
              letterSpacing: -0.5,
            }}
          >
            Creators
          </h2>
          <p
            style={{
              fontSize: 13,
              color: 'var(--soft, #646b79)',
              margin: '6px 0 0',
              maxWidth: 720,
              lineHeight: 1.6,
            }}
          >
            Jinie was conceptualized, designed, and engineered by our collaborative team. We unite generative AI reasoning, local-first compilation, and high-fidelity interactive user experiences to transform natural language briefs into verified, production-ready applications.
          </p>
        </div>

        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            background: 'rgba(113, 85, 217, 0.08)',
            color: 'var(--accent, #7155d9)',
            border: '1px solid rgba(113, 85, 217, 0.2)',
            padding: '6px 14px',
            borderRadius: 20,
            fontSize: 11,
            fontWeight: 700,
          }}
        >
          <span>◈</span>
          <span>Core Engineering Team</span>
        </div>
      </div>

      {/* Creators Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 20,
        }}
      >
        {CREATORS.map((creator) => (
          <div
            key={creator.name}
            style={{
              background: 'var(--canvas, #f8f9fc)',
              border: '1px solid var(--edge, #e4e7ee)',
              borderRadius: 18,
              padding: '22px 20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: 16,
              transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            }}
          >
            {/* Header: Avatar + Name + Role */}
            <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 16,
                  background: creator.gradient,
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: 18,
                  letterSpacing: -0.5,
                  boxShadow: '0 4px 14px rgba(0, 0, 0, 0.12)',
                  flexShrink: 0,
                }}
              >
                {creator.initials}
              </div>

              <div style={{ minWidth: 0, flex: 1 }}>
                <h3
                  style={{
                    fontSize: 17,
                    fontWeight: 800,
                    margin: 0,
                    color: 'var(--ink, #20232b)',
                    letterSpacing: -0.3,
                  }}
                >
                  {creator.name}
                </h3>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: 'var(--accent, #7155d9)',
                    marginTop: 3,
                  }}
                >
                  {creator.role}
                </div>
              </div>
            </div>

            {/* Dummy Introduction */}
            <p
              style={{
                fontSize: 12,
                color: 'var(--soft, #646b79)',
                lineHeight: 1.65,
                margin: 0,
                flex: 1,
              }}
            >
              {creator.introduction}
            </p>

            {/* Skills / Key Contributions Tag Cloud */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, paddingTop: 6, borderTop: '1px solid var(--edge, #e4e7ee)' }}>
              {creator.skills.map((skill) => (
                <span
                  key={skill}
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: '3px 8px',
                    borderRadius: 8,
                    background: 'var(--surface, #ffffff)',
                    color: 'var(--soft, #646b79)',
                    border: '1px solid var(--edge, #e2e5ec)',
                  }}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
