import { useState, useEffect, useRef } from "react";
import "../login.css";
import { useNavigate } from "react-router-dom";
import {Html5QrcodeScanner} from "html5-qrcode";


const JoinHousehold = () => {

  const navigate = useNavigate();
  const [mode, setMode] = useState("code"); // "code" or "qr"
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const scannerRef = useRef(null);

  const handleJoin = async (overrideCode = null) => {
    setError("");
  
    const finalCode = overrideCode || code;
  
    if (!finalCode.trim()) {
      setError("Please enter a join code");
      return;
    }
  
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/groups/join/${finalCode}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
          }
        }
      );
  
      const data = await response.json();
  
      if (!response.ok) {
        setError(data.detail || "Failed to join household.");
        return;
      }
  
      console.log(data);
  
      navigate("/dashboard");
  
    } catch (err) {
      console.error(err);
      setError("Server error. Try again.");
    }
  };


  useEffect(() => {
    if (mode !== "qr") return;
  
    if (scannerRef.current) return; // prevent duplicates
  
    const scanner = new Html5QrcodeScanner(
      "qr-reader",
      { fps: 10, qrbox: 250 },
      false
    );
  
    scannerRef.current = scanner;
  
    scanner.render(
      (decodedText) => {
        console.log("QR Result:", decodedText);
  
        let scannedCode = "";
  
        try {
          const url = new URL(decodedText);
          scannedCode = url.searchParams.get("code");
        } catch {
          scannedCode = decodedText;
        }
  
        if (scannedCode) {
          setCode(scannedCode);
          handleJoin(scannedCode);
          scanner.clear();
          scannerRef.current = null;
        }
      },
      () => {}
    );
  
    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(() => {});
        scannerRef.current = null;
      }
    };
  }, [mode]);




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

                <div id="qr-reader" style={{ width: "100%" }} />

                <small className="text-muted d-block mt-2">
                  Scan QR code to join
                </small>
              </div>
            )}

            {/* Join button */}
            {mode === "code" && (
              <button
                className="btn btn-dark w-100 mt-3"
                onClick={() => handleJoin()}
              >
                Join Household
              </button>
            )}
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