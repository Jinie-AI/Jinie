import React from 'react';

export const InlineEditor: React.FC = () => {
  return (
    <div className="requirement-inline-editor">
      <h3>Edit Requirement</h3>
      <input type="text" defaultValue="The system shall display product details pages." />
      <button>Save Changes</button>
    </div>
  );
};
