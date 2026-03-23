import "./App.css";
import { useState, useEffect } from "react";
import { Routes, Route, useLocation, Link, useNavigate } from "react-router-dom";

import Login from "./Components/Login";
import Register from "./Components/Register";
import HouseholdChoice from "./Components/HouseholdChoice";
import CreateHousehold from "./Components/CreateHousehold";
import JoinHousehold from "./Components/JoinHousehold";
import AuthRedirect from "./Components/AuthRedirect";
import HouseholdDashboard from "./Components/HouseholdDashboard";
import ProtectedRoute from "./Components/ProtectedRoute";

function App() {
  const location = useLocation();
  const navigate = useNavigate();

  const [theme, setTheme] = useState("light");
  const [user, setUser] = useState(null);
  const [hasGroups, setHasGroups] = useState(false);
  const [loadingUser, setLoadingUser] = useState(true);

  // Theme
  useEffect(() => {
    document.documentElement.setAttribute("data-bs-theme", theme);
  }, [theme]);

  // Load user
  useEffect(() => {
    const storedUser = localStorage.getItem("user");

    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    setLoadingUser(false);
  }, []);

  // Fetch groups → decide back button behavior
  useEffect(() => {
    const fetchGroups = async () => {
      if (!user) return;

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/v1/groups/",
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );

        const data = await response.json();

        if (response.ok) {
          setHasGroups(data.length > 0);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchGroups();
  }, [user]);

  // Logout
  const handleLogout = async () => {
    try {
      await fetch("http://127.0.0.1:8000/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error(err);
    }

    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/login"); //  no full reload
  };

  // Back button logic
  const backPath = hasGroups ? "/dashboard" : "/household";

  const showBackButton = [
    "/create-household",
    "/join-household",
    "/household",
  ].includes(location.pathname);

  // Prevent flicker / bad redirects
  if (loadingUser) {
    return null;
  }

  return (
    <>
      {/* Redirect only on entry */}
      {user &&
        (location.pathname === "/" || location.pathname === "/login") && (
          <AuthRedirect user={user} />
        )}

      <nav className="navbar navbar-expand-lg bg-body-tertiary px-4">
        <div className="container-fluid">

          {/* LEFT SIDE */}
          {showBackButton ? (
            <Link className="navbar-brand" to={backPath}>
              ← DIVVY
            </Link>
          ) : (
            <Link className="navbar-brand" to="/">
              DIVVY
            </Link>
          )}

          {/* RIGHT SIDE */}
          <div className="d-flex align-items-center">

            {/* Theme toggle */}
            <button
              className="btn btn-secondary me-3"
              onClick={() =>
                setTheme(theme === "light" ? "dark" : "light")
              }
            >
              {theme === "light" ? "Dark" : "Light"}
            </button>

            {/* User dropdown */}
            {user && (
              <div className="dropdown">
                <button
                  className="btn d-flex align-items-center"
                  data-bs-toggle="dropdown"
                >
                  {/* Avatar */}
                  <div
                    style={{
                      width: "35px",
                      height: "35px",
                      borderRadius: "50%",
                      backgroundColor: "#ccc",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginRight: "8px",
                      fontWeight: "bold",
                    }}
                  >
                    {user.first_name?.charAt(0)}
                  </div>

                  {/* Name */}
                  <span>{user.first_name}</span>
                </button>

                <ul className="dropdown-menu dropdown-menu-end">
                  <li>
                    <button
                      className="dropdown-item"
                      onClick={handleLogout}
                    >
                      Logout
                    </button>
                  </li>
                </ul>
              </div>
            )}

          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <ProtectedRoute user={user}>
              <HouseholdDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute user={user}>
              <HouseholdDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/household"
          element={
            <ProtectedRoute user={user}>
              <HouseholdChoice />
            </ProtectedRoute>
          }
        />

        <Route
          path="/create-household"
          element={
            <ProtectedRoute user={user}>
              <CreateHousehold />
            </ProtectedRoute>
          }
        />

        <Route
          path="/join-household"
          element={
            <ProtectedRoute user={user}>
              <JoinHousehold />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;