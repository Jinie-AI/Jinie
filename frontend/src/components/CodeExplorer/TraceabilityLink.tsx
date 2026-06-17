import React from 'react';

export const TraceabilityLink: React.FC<{ requirementId: string }> = ({ requirementId }) => {
  return (
    <div className="traceability-link">
      <span>Traced to: {requirementId}</span>
    </div>
  );
};
