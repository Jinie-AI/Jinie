import React from 'react';

export const FullAppPreview: React.FC = () => {
  return (
    <div className="full-app-preview-panel">
      <h3>Full Screen Simulator</h3>
      <iframe title="App Preview Sandbox" src="about:blank" style={{ width: '360px', height: '640px', border: '1px solid #ccc' }} />
    </div>
  );
};
