import './App.css'
import { useState, useEffect } from "react";
import { Routes, Route, useLocation, Link } from "react-router-dom";

import Login from "./components/Login";
import Register from "./Components/Register";
import HouseholdChoice from "./components/HouseholdChoice";
import CreateHousehold from "./components/CreateHousehold";
import JoinHousehold from "./components/JoinHousehold";

function App() {
  const location = useLocation();
  
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    document.documentElement.setAttribute("data-bs-theme", theme);
  }, [theme]);

  return (
    <>
      <nav className="navbar navbar-expand-lg bg-body-tertiary px-4">
        <div className="container-fluid">
          {location.pathname === "/create-household" || location.pathname === "/household" ? (
            <Link className="navbar-brand" to="/household">
            ← DIVVY
            </Link>
          ) : (
            <a className="navbar-brand" href="#">DIVVY</a>
          )}
          <button
            className="btn btn-secondary m-3"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            Switch to {theme === "light" ? "Dark" : "Light"} Mode
          </button>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Login />} />   
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/join" element={<JoinHousehold />} />
        <Route path="/household" element={<HouseholdChoice />} />
        <Route path="/create-household" element={<CreateHousehold />} />
      </Routes>
    </>
  );
}

export default App;