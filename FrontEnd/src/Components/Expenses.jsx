import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import PaymentModal from "./PaymentModal";

const API_BASE = "http://127.0.0.1:8000/api/v1";

const Expenses = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();

  const [expenses, setExpenses] = useState([]);
  const [balances, setBalances] = useState([]);
  const [paymentDetails, setPaymentDetails] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("access_token");

      const [expRes, owedRes] = await Promise.all([
        fetch(`${API_BASE}/expenses/group/${groupId}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_BASE}/me/owed-expenses`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      const expData = await expRes.json();
      const owedData = await owedRes.json();

      if (expRes.ok) setExpenses(expData);
      if (owedRes.ok) setBalances(owedData);
    };

    fetchData();
  }, [groupId]);

  // totals
  const youAreOwed = balances.reduce(
    (sum, b) => sum + (b.amount_owed_to_you || 0),
    0
  );

  const youOwe = balances.reduce(
    (sum, b) => sum + (b.amount_you_owe || 0),
    0
  );

  return (
    <div className="container py-4">

      <h2 className="text-center fw-bold mb-4">Expenses</h2>

      {/* Summary */}
      <div className="card p-4 mb-4 text-center">
        <div className="d-flex justify-content-center gap-5">
          <div>
            <small className="text-muted d-block">You're owed</small>
            <span className="fw-bold text-success">
              ${youAreOwed.toFixed(2)}
            </span>
          </div>

          <div>
            <small className="text-muted d-block">You owe</small>
            <span className="fw-bold text-danger">
              ${youOwe.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Expenses List */}
      <div className="card p-3">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h6 className="mb-0 fw-bold">Recent Expenses</h6>

          <button
            className="btn btn-dark btn-sm"
            onClick={() =>
              navigate(`/household/${groupId}/add-expense`)
            }
          >
            +
          </button>
        </div>

        {expenses.length === 0 ? (
          <div className="text-muted text-center py-3">
            No expenses yet
          </div>
        ) : (
          expenses.slice(0, 5).map((expense) => {
            const balance = balances.find(
              (b) =>
                b.expense_id === expense.id ||
                b.expenseId === expense.id
            );

            const userOwes = balance?.amount_you_owe || 0;
            const userIsOwed = balance?.amount_owed_to_you || 0;

            const displayAmount = userOwes + userIsOwed;

            return (
              <div
                key={expense.id}
                className="border rounded p-3 mb-3"
              >
                <div className="d-flex justify-content-between align-items-start">

                  {/* LEFT */}
                  <div>
                    <div className="fw-bold">
                      {expense.name || expense.description || "Unnamed Expense"}
                    </div>

                    {expense.description && (
                      <div className="text-muted small">
                        {expense.description}
                      </div>
                    )}

                    <small className="text-muted">
                      {expense.created_at
                        ? new Date(expense.created_at).toLocaleDateString()
                        : ""}
                    </small>
                  </div>

                  {/* RIGHT */}
                  <div className="text-end">
                    <div className="fw-semibold">
                      ${Number(displayAmount).toFixed(2)}
                    </div>

                    <div className="d-flex gap-2 mt-2 justify-content-end">

                      <button
                        className="btn btn-sm btn-outline-dark"
                        onClick={() =>
                          setPaymentDetails({
                            expense,
                            amount: displayAmount,
                          })
                        }
                      >
                        Settle Up
                      </button>

                      <button
                        className="btn btn-sm btn-dark"
                        onClick={() =>
                          navigate(
                            `/household/${groupId}/add-expense`,
                            { state: { expense } }
                          )
                        }
                      >
                        Edit
                      </button>

                    </div>
                  </div>

                </div>
              </div>
            );
          })
        )}
      </div>

      {paymentDetails && (
        <PaymentModal
          expense={paymentDetails.expense}
          amount={paymentDetails.amount}
          onClose={() => setPaymentDetails(null)}
        />
      )}
    </div>
  );
};

export default Expenses;