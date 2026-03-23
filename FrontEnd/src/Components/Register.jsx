import { useState } from "react";
import "../login.css";
import { Link, useNavigate } from "react-router-dom";

const Register = () => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Handle input changes
  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Basic validation
    if (!formData.email.includes("@")) {
      setError("Enter a valid email");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/users/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            first_name: formData.firstName,
            last_name: formData.lastName,
            email: formData.email,
            password: formData.password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to create account"
        );
        return;
      }

      console.log("User created:", data);

      // Redirect after success
      navigate("/login");

    } catch (err) {
      console.error(err);
      setError("Server error. Try again.");
    }
  };

  return (
    <div className="login-page py-5">
      <div className="login-bg-layer"></div>

      <div style={{ maxWidth: "420px", margin: "0 auto" }}>
        <div className="card login-card shadow-lg border-0">
          <div className="card-body p-4">

            <div className="text-center mb-4">
              <h1 className="h4 fw-bold mb-2">Sign Up</h1>
              <p className="small text-secondary fst-italic mb-0">
                Roommate Expense Manager
              </p>
            </div>

            {error && (
              <div className="alert alert-danger py-2 small text-center">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="text-start">

              <div className="mb-3">
                <label htmlFor="firstName" className="form-label">
                  First Name
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="lastName" className="form-label">
                  Last Name
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="email" className="form-label">
                  Email
                </label>
                <input
                  type="email"
                  className="form-control"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="password" className="form-label">
                  Password
                </label>
                <input
                  type="password"
                  className="form-control"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary w-100">
                Sign Up
              </button>

              <div className="text-center mt-3">
                <span className="small text-secondary">
                  Already have an account?{" "}
                  <Link to="/login">Login</Link>
                </span>
              </div>

            </form>
          </div>

          <div className="card-footer bg-body-tertiary border-0 text-center py-3">
            <span className="small fw-bold text-uppercase text-muted">
              DIVVY © 2026
            </span>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Register;