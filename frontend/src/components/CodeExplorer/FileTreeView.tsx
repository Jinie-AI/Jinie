import React from 'react';

export const FileTreeView: React.FC = () => {
  return (
    <div className="file-tree-view">
      <h3>Project File Structure</h3>
      <ul>
        <li>📁 lib/</li>
        <li>  📄 main.dart</li>
        <li>📄 pubspec.yaml</li>
      </ul>
    </div>
  );
};
