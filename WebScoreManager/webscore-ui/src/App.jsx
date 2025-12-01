import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import StudentsPage from './pages/StudentsPage';
import ScoresPage from './pages/ScoresPage';
import CoursesPage from './pages/CoursesPage';
import StatisticsPage from './pages/StatisticsPage';
import LoginPage from './pages/LoginPage';
import { AppStateProvider } from './context/AppStateContext';

function App() {
  return (
    <BrowserRouter>
      <AppStateProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/students" element={<StudentsPage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/scores" element={<ScoresPage />} />
            <Route path="/statistics" element={<StatisticsPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </AppStateProvider>
    </BrowserRouter>
  );
}

export default App;
