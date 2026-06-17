import React from 'react';

export const PromptInputBox: React.FC = () => {
  return (
    <div className="prompt-input-box">
      <h3>Describe your application</h3>
      <textarea placeholder="e.g. A clothing brand app with a home screen and cart..." />
    </div>
  );
};
