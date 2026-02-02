import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { HomePage } from "./pages/HomePage";
import { GetQuotePage } from "./pages/GetQuotePage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import ResourcesPage from "./pages/ResourcesPage";
import GlossaryPage from "./pages/resources/GlossaryPage";
import ChooseHealthInsurancePage from "./pages/resources/ChooseHealthInsurancePage";
import Top5MistakesPage from "./pages/resources/Top5MistakesPage";
import DeductiblesPage from "./pages/resources/DeductiblesPage";
import ClaimsGuidePage from "./pages/resources/ClaimsGuidePage";
import TermVsWholeLifePage from "./pages/resources/TermVsWholeLifePage";

const theme = createTheme({
  palette: {
    primary: {
      main: "#10b981",
      light: "#6ee7b7",
      dark: "#047857",
    },
    secondary: {
      main: "#3b82f6",
    },
    success: {
      main: "#10b981",
    },
    warning: {
      main: "#f59e0b",
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h4: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/get-quote" element={<GetQuotePage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/resources/glossary" element={<GlossaryPage />} />
          <Route
            path="/resources/choose-health-insurance"
            element={<ChooseHealthInsurancePage />}
          />
          <Route
            path="/resources/top-5-mistakes"
            element={<Top5MistakesPage />}
          />
          <Route
            path="/resources/understanding-deductibles"
            element={<DeductiblesPage />}
          />
          <Route path="/resources/claims-guide" element={<ClaimsGuidePage />} />
          <Route
            path="/resources/term-vs-whole-life"
            element={<TermVsWholeLifePage />}
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
