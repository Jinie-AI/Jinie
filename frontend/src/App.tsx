import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";

import HomePage from "./pages/HomePage";
import FeaturesPage from "./pages/FeaturesPage";
import HowItWorksPage from "./pages/HowItWorksPage";
import AboutPage from "./pages/AboutPage";
import ShowcasePage from "./pages/ShowcasePage";
import ContactPage from "./pages/ContactPage";
import WorkspacePage from "./pages/WorkspacePage";
import DeployPage from "./pages/DeployPage";

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/showcase" element={<ShowcasePage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/deploy" element={<DeployPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;