import './App.css'
import { useState, useEffect } from "react";
import Login from "./Login";

function App() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    document.documentElement.setAttribute("data-bs-theme", theme);
  }, [theme]);

  return (
    <div>
      <nav className = "navbar navbar-expand-lg bg-body-tertiary px-4">
        <div className = "container-fluid">
          <a className = "navbar-brand" href= "#">DIVVY</a> 
          <button
            className="btn btn-secondary m-3"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            Switch to {theme === "light" ? "Dark" : "Light"} Mode
          </button>
        </div>
      </nav>

      <Login />
    </div>
  );
}

export default App;