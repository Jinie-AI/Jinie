import React from 'react';

export const ColorPalette: React.FC = () => {
  return (
    <div className="color-palette">
      <h3>Select Theme Colors</h3>
      <input type="color" defaultValue="#6200EE" />
      <input type="color" defaultValue="#03DAC6" />
    </div>
  );
};
