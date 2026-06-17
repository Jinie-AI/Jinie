import React from 'react';

export const SyntaxEditor: React.FC = () => {
  return (
    <div className="syntax-editor">
      <h3>File Source Viewer</h3>
      <pre style={{ border: '1px solid #ccc', padding: '10px' }}>
        {`void main() {
  runApp(const MyApp());
}`}
      </pre>
    </div>
  );
};
