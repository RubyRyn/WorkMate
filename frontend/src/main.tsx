import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "./app/contexts/AuthContext";
import { Toaster } from "./app/components/ui/sonner";
import App from "./app/App";
import { PublicLayout } from "./public/layouts/PublicLayout";
import { LandingPage } from "./public/pages/LandingPage";
import { AboutPage } from "./public/pages/AboutPage";
import { PricingPage } from "./public/pages/PricingPage";
import { DocsPage } from "./public/pages/DocsPage";
import { DemoPage } from "./public/pages/DemoPage";
import { ContactPage } from "./public/pages/ContactPage";
import { LoginPage } from "./app/pages/LoginPage";
import "./styles/index.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AuthProvider>
        <Routes>
          {/* Public marketing site */}
          <Route element={<PublicLayout />}>
            <Route index element={<LandingPage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="pricing" element={<PricingPage />} />
            <Route path="docs" element={<DocsPage />} />
            <Route path="demo" element={<DemoPage />} />
            <Route path="contact" element={<ContactPage />} />
          </Route>

          {/* Auth */}
          <Route path="login" element={<LoginPage />} />

          {/* Authenticated app */}
          <Route path="app/*" element={<App />} />
        </Routes>
        <Toaster position="bottom-right" richColors />
      </AuthProvider>
    </ThemeProvider>
  </BrowserRouter>
);
