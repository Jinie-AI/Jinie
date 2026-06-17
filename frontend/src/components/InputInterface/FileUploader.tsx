import React from 'react';

export const FileUploader: React.FC = () => {
  return (
    <div className="file-uploader">
      <h3>Attach Reference Files</h3>
      <input type="file" multiple />
    </div>
  );
};
