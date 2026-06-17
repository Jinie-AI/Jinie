import React from 'react';

export const Typography: React.FC = () => {
  return (
    <div className="typography-settings">
      <h3>Select Font Family</h3>
      <select>
        <option value="Roboto">Roboto</option>
        <option value="Inter">Inter</option>
        <option value="Montserrat">Montserrat</option>
      </select>
    </div>
  );
};
