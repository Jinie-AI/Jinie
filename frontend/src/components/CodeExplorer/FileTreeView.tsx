import React from 'react';

export const FileTreeView: React.FC = () => {
  return (
    <div className="file-tree-view">
      <h3>Project File Structure</h3>
      <ul>
        <li>📁 src/</li>
        <li>  📄 App.tsx</li>
        <li>📄 package.json</li>
        <li>📄 app.json</li>
      </ul>
    </div>
  );
};
