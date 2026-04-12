// Expenses.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

const Expenses = () => {
  const navigate = useNavigate();
  const { groupId } = useParams();

  // TEMP DATA (replace with backend later)
  const [expenses] = useState([
    { name: "Groceries", amount: 20, category: "Food", date: "Today" },
    { name: "Internet", amount: 50, category: "Bills", date: "Yesterday" },
  ]);

  return (
    <div className="container py-4">

      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="fw-bold mb-0">Expenses</h2>

        <button
          className="btn btn-outline-secondary"
          onClick={() => navigate(`/household/${groupId}`)}
        >
          ← Back
        </button>
      </div>

      {/* Summary */}
      <div className="d-flex gap-3 mb-4">
        <div className="card p-3 shadow-sm text-center flex-fill">
          <small className="text-muted">You're Owed</small>
          <h5 className="fw-bold">$45.50</h5>
        </div>

        <div className="card p-3 shadow-sm text-center flex-fill">
          <small className="text-muted">You Owe</small>
          <h5 className="fw-bold">$0.00</h5>
        </div>
      </div>

      {/* Expenses List */}
      <div className="card p-3 shadow-sm mb-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h6 className="fw-bold mb-0">Recent Expenses</h6>

          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => navigate(`/household/${groupId}/add-expense`)}
          >
            +
          </button>
        </div>

        {expenses.length === 0 ? (
          <p className="text-muted text-center">No expenses yet</p>
        ) : (
          expenses.map((exp, index) => (
            <div
              key={index}
              className="card p-2 mb-2 shadow-sm"
            >
              <div className="d-flex justify-content-between">
                <div>
                  <strong>{exp.name}</strong>
                  <div className="small text-muted">{exp.date}</div>
                </div>

                <div className="text-end">
                  <div>${exp.amount}</div>
                  <span className="badge bg-secondary">
                    {exp.category}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Actions */}
      <div className="d-flex gap-3 justify-content-center">
        <button className="btn btn-outline-dark">
          Settle Up
        </button>

        <button
          className="btn btn-dark"
          onClick={() => navigate(`/household/${groupId}/add-expense`)}>
          Add Expense
        </button>
      </div>

    </div>
  );
};

export default Expenses;