import { useState } from "react";
import "../login.css";

const JoinHousehold = () => {
  const [mode, setMode] = useState("code"); // "code" or "qr"
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const handleJoin = () => {
    setError("");

    if (mode === "code" && !code) {
      setError("Please enter a household code");
      return;
    }

    console.log("Joining household with:", code);

    // 🔥 Later: call backend here
  };

  return (
    <div className="login-page py-5">
      <div className="login-bg-layer"></div>

      <div style={{ maxWidth: "500px", margin: "0 auto" }}>
        <div className="card login-card shadow-lg border-0">
          <div className="card-body p-4">

            {/* Title */}
            <div className="text-center mb-4">
              <h1 className="h4 fw-bold">Join a Household</h1>
            </div>

            {/* Toggle buttons */}
            <div className="d-flex justify-content-center mb-3">
              <button
                className={`btn ${mode === "code" ? "btn-dark" : "btn-outline-dark"} me-2`}
                onClick={() => setMode("code")}
              >
                Enter Code
              </button>

              <button
                className={`btn ${mode === "qr" ? "btn-dark" : "btn-outline-dark"}`}
                onClick={() => setMode("qr")}
              >
                Scan Code
              </button>
            </div>

            {/* Error */}
            {error && (
              <div className="alert alert-danger py-2 small text-center">
                {error}
              </div>
            )}

            {/* CODE MODE */}
            {mode === "code" && (
              <>
                <div className="mb-3">
                  <input
                    type="text"
                    className="form-control text-center"
                    placeholder="DIVVY-XXXX"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                  />
                  <small className="text-muted">
                    Enter the code shared with you
                  </small>
                </div>
              </>
            )}

            {/* QR MODE */}
            {mode === "qr" && (
              <div className="text-center mb-3">
                <div
                  style={{
                    width: "150px",
                    height: "150px",
                    margin: "0 auto",
                    backgroundColor: "#eee",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: "10px",
                  }}
                >
                  QR Code
                </div>
                <small className="text-muted d-block mt-2">
                  Scan QR code to join
                </small>
              </div>
            )}

            {/* Join button */}
            <button
              className="btn btn-dark w-100 mt-3"
              onClick={handleJoin}
            >
              Join Household
            </button>
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
  );
};

export default JoinHousehold;