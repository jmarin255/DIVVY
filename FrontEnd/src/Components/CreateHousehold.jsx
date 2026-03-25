import { useState } from "react";
import { Link } from "react-router-dom";
import{ QRCodeCanvas } from "qrcode.react";

const CreateHousehold = () => {
    const [householdName, setHouseholdName] = useState("");
    const [loading, setLoading] = useState(false);

    const [code, setCode] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        if (!householdName.trim()) {
            alert("Household name required");
            return;
        }

        setLoading(true);
    
        try {
            const response = await fetch(
                "http://127.0.0.1:8000/api/v1/me/groups/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${localStorage.getItem("access_token")}`
                    },
                    body: JSON.stringify({
                        name: householdName
                    })
                }
            );
    
            const data = await response.json();
    
            if (!response.ok) {
                alert(data.detail || "Failed to create household");
                return;
            }
    
            console.log("Created:", data);
    
            // SET REAL CODE FROM BACKEND
            setCode(data.join_code);
    
        } catch (err) {
            console.error(err);
            alert("Server error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="household-page py-5">
            <div className="container">

                <h2 className="text-center fw-bold mb-4">Create Household</h2>

                <div className="card p-4 shadow mx-auto" style={{ maxWidth: "500px" }}>
                    <form onSubmit={handleSubmit}>

                        <div className="mb-3">
                            <label className="form-label">Household Name</label>
                            <input
                                className="form-control"
                                value={householdName}
                                onChange={(e) => {setHouseholdName(e.target.value); setCode("");}}
                                placeholder="Enter household name"
                            />
                        </div>
                        {code &&(
                            <div className="mb-3">
                                <label className="form-label">Household Code</label>
                                <input
                                    className="form-control"
                                    value={code}
                                    readOnly
                                />
                            </div>
                        )}

                        {code && (
                        <div className="qr-box mb-3 text-center">
                            <QRCodeCanvas
                            value={`http://localhost:5173/join-household?code=${encodeURIComponent(code)}`}
                            size={150}
                            />
                            <small className="text-muted d-block mt-2">
                            Scan to join
                            </small>
                        </div>
                        )}

                        <button type="submit" className="btn btn-dark w-100" disabled = {loading || code}>
                            {loading ? "Creating...": code ? "Created": "Create Household"}
                        </button>

                    </form>
                </div>

            </div>
        </div>
    );
};

export default CreateHousehold;