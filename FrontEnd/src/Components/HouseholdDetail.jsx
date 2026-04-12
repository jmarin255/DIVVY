import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { QRCodeCanvas } from "qrcode.react";
import { useNavigate } from "react-router-dom";

const HouseholdDetail = () => {
  const { groupId } = useParams();
  const navigate = useNavigate(); // expenses page navigation

  const [group, setGroup] = useState(null);
  const [members, setMembers] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHouseholdData = async () => {
      try {
        const token = localStorage.getItem("access_token");

        const [groupRes, membersRes, expensesRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/v1/groups/${groupId}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch(`http://127.0.0.1:8000/api/v1/groups/${groupId}/users`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch(`http://127.0.0.1:8000/api/v1/expenses/group/${groupId}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
        ]);

        const groupData = await groupRes.json();
        const membersData = await membersRes.json();
        const expensesData = await expensesRes.json();

        if (groupRes.ok) {
          setGroup(groupData);
        } else {
          console.error("Group error:", groupData);
        }

        if (membersRes.ok) {
          setMembers(membersData);
        } else {
          console.error("Members error:", membersData);
        }

        if (expensesRes.ok) {
          setExpenses(expensesData);
        } else {
          console.error("Expenses error:", expensesData);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHouseholdData();
  }, [groupId]);

  if (loading) {
    return <div className="container py-4">Loading...</div>;
  }

  if (!group) {
    return <div className="container py-4">Household not found.</div>;
  }

  return (
    <div className="container py-4">
      <h1 className="text-center fw-bold mb-4">{group.name}</h1>

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card p-3 shadow-sm mb-4">
            <h5 className="mb-3">Household Code</h5>

            <div className="d-flex justify-content-between align-items-center border rounded p-3 bg-light mb-3">
              <span className="fw-bold">{group.join_code}</span>
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={() => navigator.clipboard.writeText(group.join_code)}
              >
                Copy
              </button>
            </div>

            <div className="text-center">
              <QRCodeCanvas
                value={`http://localhost:5173/join-household?code=${group.join_code}`}
                size={150}
              />
              <div className="mt-3">
                <button className="btn btn-dark btn-sm">Share</button>
              </div>
            </div>
          </div>

          <div className="card p-3 shadow-sm">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="mb-0">Expenses</h5>
              <button className="btn btn-dark btn-sm" onClick={() => navigate(`/household/${groupId}/expenses`)}>
                See More
  </button>
            </div>

            {expenses.length === 0 ? (
              <p className="text-muted mb-0">No expenses yet.</p>
            ) : (
              expenses.map((expense) => (
                <div
                  key={expense.id}
                  className="border rounded p-3 mb-2 d-flex justify-content-between align-items-center"
                >
                  <div>
                    <div className="fw-bold">
                      {expense.name || expense.title || "Expense"}
                    </div>
                    <small className="text-muted">
                      {expense.created_at
                        ? new Date(expense.created_at).toLocaleDateString()
                        : expense.date || ""}
                    </small>
                  </div>

                  <button className="btn btn-primary btn-sm w-auto">
                    Open
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card p-3 shadow-sm">
            <h5 className="mb-3">Members ({members.length})</h5>

            {members.length === 0 ? (
              <p className="text-muted mb-0">No members found.</p>
            ) : (
              members.map((member) => (
                <div
                  key={member.id}
                  className="border rounded p-3 mb-2 d-flex justify-content-between align-items-center"
                >
                  <div className="d-flex align-items-center">
                    <div
                      style={{
                        width: "42px",
                        height: "42px",
                        borderRadius: "50%",
                        backgroundColor: "#dee2e6",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        marginRight: "12px",
                        fontWeight: "bold",
                      }}
                    >
                      {member.first_name?.charAt(0)}
                    </div>

                    <div>
                      <div className="fw-semibold">
                        {member.first_name} {member.last_name}
                      </div>
                    </div>
                  </div>

                  <span className="badge text-bg-secondary">Member</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="text-center mt-5">
        <button className="btn btn-outline-danger px-5">
          Leave Household
        </button>
      </div>
    </div>
  );
};

export default HouseholdDetail;