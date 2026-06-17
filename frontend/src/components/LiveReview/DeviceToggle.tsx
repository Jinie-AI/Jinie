import React from 'react';

export const DeviceToggle: React.FC<{ onViewportChange: (viewport: string) => void }> = ({ onViewportChange }) => {
  return (
    <div className="device-toggle-bar">
      <button onClick={() => onViewportChange('mobile')}>Mobile</button>
      <button onClick={() => onViewportChange('tablet')}>Tablet</button>
      <button onClick={() => onViewportChange('desktop')}>Desktop</button>
    </div>
  );
};
