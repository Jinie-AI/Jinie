import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "./pages/HomePage";
import WorkspacePage from "./pages/WorkspacePage";
import DeployPage from "./pages/DeployPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/workspace" element={<WorkspacePage />} />
        <Route path="/deploy" element={<DeployPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;