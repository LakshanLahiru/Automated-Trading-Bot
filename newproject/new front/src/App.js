
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './components/login/Login';
import Home from './components/home/Home';
import History from './components/history/History';
import Dashboard from './components/dashboard/Dashboard';
function App() {
  return (
    <div >
      <BrowserRouter>
      
        
        <Routes>
        <Route path="/" element={<Login/>}/>
        <Route path="/home" element={<Home/>}/>
        <Route path="/history" element={<History/>}/>
        <Route path="/dashboard" element={<Dashboard/>}/>
        </Routes>
      </BrowserRouter>
      
    </div>
  );
}

export default App;
