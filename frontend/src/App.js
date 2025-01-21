import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import YouTubeAnalytics from './components/YouTubeAnalytics';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Barre de navigation */}
        <nav className="bg-red-600 text-white py-4">
          <div className="max-w-7xl mx-auto px-4">
            <h1 className="text-2xl font-bold text-center">Content Creator AI</h1>
          </div>
        </nav>

        {/* Contenu principal */}
        <main>
          <Routes>
            <Route path="/" element={<YouTubeAnalytics />} />
          </Routes>
        </main>

        {/* Notifications */}
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;
