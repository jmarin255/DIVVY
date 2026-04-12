import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const HouseholdDashboard = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/v1/me/groups/",
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          console.error(data);
          return;
        }

        setGroups(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchGroups();
  }, []);

  const handleOpenGroup = (group) => {
    console.log("Selected group:", group);
    // future: navigate(`/group/${group.id}`);
  };

  return (
    <div className="container py-4">

    
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="fw-bold mb-0">My Households</h2>

        <button
          className="btn btn-dark"
          onClick={() => navigate("/household")}
        >
          + Create / Join
        </button>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : groups.length === 0 ? (
        <div className="text-center text-muted">
          <p>No households yet</p>
          <button
            className="btn btn-dark mt-2"
            onClick={() => navigate("/household")}
          >
            Create or Join Household
          </button>
        </div>
      ) : (
        <div className="row">
          {groups.map((group) => (
            <div key={group.id} className="col-md-4 mb-3">
              <div
                className="card p-3 shadow-sm h-100"
                style={{ cursor: "pointer" }}
                onClick={() => handleOpenGroup(group)}
              >
                <h5 className="text-center fw-bold">{group.name}</h5>

                <p className="text-muted small mb-1">
                  Code: {group.join_code}
                </p>
               


               
                <div className="card p-3 shadow-sm h-40">
                  <h6 className = "fw-bold" > Expense Name</h6>
                  <h7 className="text-muted small mb-1">Date</h7>
                </div>
                <div className="text-center mt-2">
                  <button
                    className="btn btn-dark btn-sm w-auto mt-2"
                    onClick={() => navigate(`/household/${group.id}`)}
                  >
                    Open
                  </button>
                </div>

              </div>
            </div>

          ))}
        </div>
      )}
    </div>
  );
};

export default HouseholdDashboard;