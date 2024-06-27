// import logo from './logo.svg';
// import './App.css';
// import Example from './components/light_sidebar_with_header';
import Register from './components/auth/Register';
import Login from './components/auth/Login';
import Dashboard from './components/Dashboard';

import { Route, Routes } from 'react-router-dom'

function App() {
  return (
    <div>
      <Routes>
        <Route exact path="/" element={<Dashboard/>}/>
        <Route exact path="/register" element={<Register/>}/>
        <Route exact path="/login" element={<Login/>}/>
        <Route exact path="/logout" element={<Login/>}/>
      </Routes>
    </div>
  );
}

export default App;
