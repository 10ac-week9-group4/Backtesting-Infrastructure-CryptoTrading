import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import Register from './components/auth/Register';
import Login from './components/auth/Login';
import Dashboard from './components/Dashboard';
// import useAuth from './hooks/useAuth'; // Import the useAuth hook

function App() {
  // const isAuthenticated = useAuth(); // Use the hook to check auth status
  // console.log(isAuthenticated)

  return (
    <div>
      <Routes>
        <Route exact path="/" element={<Dashboard />} />
        <Route exact path="/register" element={<Register />} />
        <Route exact path="/login" element={<Login />} />
        {/* Redirect /logout to /login for simplicity, handle logout logic elsewhere */}
        <Route exact path="/logout" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
}

export default App;