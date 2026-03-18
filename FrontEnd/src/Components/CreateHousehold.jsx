import { useState } from "react";
import { useNavigate } from "react-router-dom";

function CreateHousehold() {
    const [name, setName] = useState("");
    const navigate = useNavigate();

    const handleCreate = () => {
        if (!name) {
            alert("Please enter a household name.");
            return;
        }

        const household = {
            id: Date.now(),
            name: name
        };

        localStorage.setItem("houehold", JSON.stringify(household));
        navigate("/dashboard");
    }

    return (
        <div className="login-page py-5">
            <div style={{ maxWidth: "420px", margin: "0 auto" }}>
                <div className="card shadow-lg border-0">
                    <div className="card-body p-4">
                        <h2 className="text-center mb-4">Create Household</h2>
                        <div className="mb-3">
                            <label htmlFor="householdName" className="form-label">Household Name</label>
                            <input
                                type="text"
                                className="form-control"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Enter household name"
                            />
                        </div>

                        <button className="btn btn-primary w-100" onClick={handleCreate}>
                            Create
                        </button>
                    </div>

                </div>
            </div>
        </div>


    );
       
    
}

export default CreateHousehold;