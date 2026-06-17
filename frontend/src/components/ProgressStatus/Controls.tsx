import React from 'react';

export const Controls: React.FC = () => {
  return (
    <div className="pipeline-controls">
      <button>Cancel Build</button>
      <button>Retry Stage</button>
    </div>
  );
};
