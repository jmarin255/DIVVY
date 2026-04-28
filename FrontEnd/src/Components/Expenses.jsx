import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import PaymentModal from "./PaymentModal";

const API_BASE = "http://127.0.0.1:8000/api/v1";

const Expenses = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();

  const [expenses, setExpenses] = useState([]);
  const [expenseSplits, setExpenseSplits] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [paymentDetails, setPaymentDetails] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("access_token");

      const [meRes, expRes, splitsRes] = await Promise.all([
        fetch(`${API_BASE}/me`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_BASE}/expenses/group/${groupId}`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${API_BASE}/me/expense-splits`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      const meData = await meRes.json();
      const expData = await expRes.json();
      const splitData = await splitsRes.json();

      if (meRes.ok) setCurrentUser(meData);
      if (expRes.ok) setExpenses(expData);
      if (splitsRes.ok) setExpenseSplits(splitData);
    };

    fetchData();
  }, [groupId]);

  const splitByExpenseId = expenseSplits.reduce((map, split) => {
    map.set(split.expense_id, Number(split.amount) || 0);
    return map;
  }, new Map());

  const youAreOwed = expenses.reduce((sum, expense) => {
    if (!currentUser || expense.created_by !== currentUser.id) {
      return sum;
    }

    const totalAmount = Number(expense.amount ?? expense.total_amount ?? 0);
    const yourShare = splitByExpenseId.get(expense.id) || 0;

    return sum + Math.max(totalAmount - yourShare, 0);
  }, 0);

  const youOwe = expenseSplits.reduce(
    (sum, split) => sum + (Number(split.amount) || 0),
    0,
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
            <span className="fw-bold text-danger">${youOwe.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Expenses List */}
      <div className="card p-3">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h6 className="mb-0 fw-bold">Recent Expenses</h6>

          <button
            className="btn btn-dark btn-sm"
            onClick={() => navigate(`/household/${groupId}/add-expense`)}
          >
            +
          </button>
        </div>

        {expenses.length === 0 ? (
          <div className="text-muted text-center py-3">No expenses yet</div>
        ) : (
          expenses.slice(0, 5).map((expense) => {
            const totalAmount = Number(
              expense.amount ?? expense.total_amount ?? 0,
            );
            const userShare = splitByExpenseId.get(expense.id) || 0;
            const displayAmount =
              currentUser && expense.created_by === currentUser.id
                ? Math.max(totalAmount - userShare, 0)
                : userShare;

            return (
              <div key={expense.id} className="border rounded p-3 mb-3">
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
                          navigate(`/household/${groupId}/add-expense`, {
                            state: { expense },
                          })
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
