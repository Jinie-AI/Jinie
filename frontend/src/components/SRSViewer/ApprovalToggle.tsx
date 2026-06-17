import React from 'react';

export const ApprovalToggle: React.FC = () => {
  return (
    <div className="requirement-approval-toggle">
      <label>
        <input type="checkbox" defaultChecked />
        Approve requirement specs for compilation
      </label>
    </div>
  );
};
