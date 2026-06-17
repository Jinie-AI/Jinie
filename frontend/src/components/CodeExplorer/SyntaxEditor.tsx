import React from 'react';

export const SyntaxEditor: React.FC = () => {
  return (
    <div className="syntax-editor">
      <h3>File Source Viewer</h3>
      <pre style={{ border: '1px solid #ccc', padding: '10px' }}>
        {`import React from 'react';
import { View, Text } from 'react-native';

export default function App() {
  return (
    <View>
      <Text>Hello Jinie App</Text>
    </View>
  );
}`}
      </pre>
    </div>
  );
};
