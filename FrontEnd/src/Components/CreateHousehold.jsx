import { useState } from "react";
import { Link } from "react-router-dom";

const CreateHousehold = () => {
    const [householdName, setHouseholdName] = useState("");

    const code = "DIVVY-2K26";

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!householdName.trim()) {
            alert("Household name required");
            return;
        }

        console.log({ householdName, code });
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
                                onChange={(e) => setHouseholdName(e.target.value)}
                                placeholder="Enter household name"
                            />
                        </div>

                        <div className="mb-3">
                            <label className="form-label">Household Code</label>
                            <input
                                className="form-control"
                                value={code}
                                readOnly
                            />
                        </div>

                        <div className="qr-box mb-3 text-center">
                            <div className="qr-placeholder">QR Code</div>
                        </div>

                        <button type="submit" className="btn btn-dark w-100">
                            Create Household
                        </button>

                    </form>
                </div>

            </div>
        </div>
    );
};

export default CreateHousehold;