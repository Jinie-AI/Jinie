import React from 'react';

export const ComponentPreview: React.FC = () => {
  return (
    <div className="component-preview-panel">
      <h3>UI Component Isolation View</h3>
      <div style={{ border: '1px dashed #ccc', padding: '20px' }}>
        <button style={{ background: '#6200EE', color: 'white', padding: '10px' }}>Generated Button</button>
      </div>
    </div>
  );
};
