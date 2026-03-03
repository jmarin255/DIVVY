import { useState, useEffect } from "react";
import "./login.css";

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    document.documentElement.setAttribute("data-bs-theme", theme);
  }, [theme]);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    console.log("Submitting:", formData);

    if (!formData.email.includes("@")) {
      setError("Please enter a valid email.");
      return;
    }
  };

  return (
    <>
      {/* NAVBAR */}
    

      {/* LOGIN PAGE */}
      <div className="login-page py-5">

        {/* Background layer (optional) */}
        <div className="login-bg-layer"></div>

        {/* CENTERED CARD */}
        <div style={{ maxWidth: "420px", margin: "0 auto" }}>
          <div className="card login-card shadow-lg border-0">
            <div className="card-body p-4">

              {/* Title */}
              <div className="text-center mb-4">
                <h1 className="h4 fw-bold mb-2">Sign In</h1>
                <p className="small text-secondary fst-italic mb-0">
                  Roommate Expense Manager
                </p>
              </div>

              {/* Error */}
              {error && (
                <div className="alert alert-danger py-2 small text-center">
                  {error}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="text-start">
                <div className="mb-3">
                  <label className="form-label small fw-bold text-uppercase text-secondary">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    className="form-control login-input"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label small fw-bold text-uppercase text-secondary">
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    className="form-control login-input"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 login-btn"
                >
                  Login
                </button>

                <div className="text-center mt-3">
                  <span className="small text-secondary">
                    Don’t have an account? <a href="/register">Register</a>
                  </span>
                </div>
              </form>
            </div>

            {/* Footer */}
            <div className="card-footer bg-body-tertiary border-0 text-center py-3">
              <span className="small fw-bold text-uppercase text-muted">
                DIVVY © 2026
              </span>
            </div>
          </div>
        </div>

      </div>
    </>
  );
};

export default Login;