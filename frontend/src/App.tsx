// All routes in one place, plus the shared page frame (header and centered column).

import { BrowserRouter, Link, Route, Routes } from "react-router";
import ProtectedRoute from "./components/ProtectedRoute";
import CheckPage from "./pages/CheckPage";
import DiagnosticsPage from "./pages/DiagnosticsPage";
import HomePage from "./pages/HomePage";
import InterviewPage from "./pages/InterviewPage";
import LoginPage from "./pages/LoginPage";
import NewInterviewPage from "./pages/NewInterviewPage";
import NotFoundPage from "./pages/NotFoundPage";
import ReportPage from "./pages/ReportPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="page">
        <header className="site-header">
          <Link className="site-title" to="/">
            IntervueAI
          </Link>
          <span className="muted">Mock interview practice</span>
        </header>
        <main>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
            <Route path="/new" element={<ProtectedRoute><NewInterviewPage /></ProtectedRoute>} />
            <Route path="/interviews/:id/check" element={<ProtectedRoute><CheckPage /></ProtectedRoute>} />
            <Route path="/interviews/:id" element={<ProtectedRoute><InterviewPage /></ProtectedRoute>} />
            <Route path="/reports/:id" element={<ProtectedRoute><ReportPage /></ProtectedRoute>} />
            <Route path="/diagnostics" element={<ProtectedRoute><DiagnosticsPage /></ProtectedRoute>} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
