import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Catalog from './components/Catalog';
import Login from './components/Login';
import Register from './components/Register'; // unused - keep commented for future use
import Navigation from './components/Navigation';
import './App.css';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/*"
          element={
            <div className="min-h-screen bg-gray-50">
              <Navigation />
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/catalog" element={<Catalog />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </div>
          }
        />
      </Routes>
    </Router>
  );
}
