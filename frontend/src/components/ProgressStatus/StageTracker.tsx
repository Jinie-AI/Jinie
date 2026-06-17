import React from 'react';

export const StageTracker: React.FC = () => {
  return (
    <div className="stage-tracker">
      <h3>Active Pipeline Stage</h3>
      <ul>
        <li>1. Requirements Generation [Completed]</li>
        <li>2. UI Recommendation [Processing]</li>
        <li>3. Component Generation [Pending]</li>
      </ul>
    </div>
  );
};
