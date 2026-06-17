import React from 'react';

export const FeedbackCapture: React.FC = () => {
  return (
    <div className="feedback-capture">
      <h3>Flag design issues</h3>
      <textarea placeholder="e.g. Make this navbar text bold..." />
      <button>Submit Feedback</button>
    </div>
  );
};
