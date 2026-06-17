import React from 'react';

export const IDBadgeDisplay: React.FC<{ requirementId: string }> = ({ requirementId }) => {
  return (
    <span className="id-badge-display" style={{ background: '#eee', padding: '2px 6px', borderRadius: '4px' }}>
      {requirementId}
    </span>
  );
};
