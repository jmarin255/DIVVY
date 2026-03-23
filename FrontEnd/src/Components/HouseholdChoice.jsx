import { Link } from "react-router-dom";

const HouseholdChoice = () => {
    return (
        <div className="household-page py-5">
            <div className="container text-center">

                <h1 className="fw-bold mb-5">DIVVY</h1>

                <div className="row justify-content-center gap-4">

                    <div className="col-md-4">
                        <div className="card shadow-sm p-4">
                            <h4 className="fw-bold">Join Household</h4>
                            <p className="small text-secondary">
                                Enter an invite code or scan a QR code
                            </p>

                            <Link to="/join-household" className="btn btn-outline-dark">
                                Join
                            </Link>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="card shadow-sm p-4">
                            <h4 className="fw-bold">Create Household</h4>
                            <p className="small text-secondary">
                                Start a new household and invite roommates
                            </p>

                            <Link to="/create-household" className="btn btn-dark">
                                Create
                            </Link>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default HouseholdChoice;