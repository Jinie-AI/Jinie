import React from 'react';

export const LayoutMode: React.FC = () => {
  return (
    <div className="layout-mode-settings">
      <h3>Navigation Layout Style</h3>
      <select>
        <option value="tabs">Bottom Navigation Tabs</option>
        <option value="drawer">Navigation Drawer</option>
        <option value="both">Tabs + Drawer</option>
      </select>
    </div>
  );
};
