// AddExpense.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";

const AddExpense = () => {
  const navigate = useNavigate();
  const { groupId } = useParams();

  const [form, setForm] = useState({
    name: "",
    amount: "",
    category: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log("Expense:", form);

    // TODO: send to backend

    navigate(`/household/${groupId}/expenses`);
  };

  return (
    <div className="household-page py-5">
      <div className="container">

        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="fw-bold mb-0">Add Expenses</h2>

          <button
            className="btn btn-outline-secondary"
            onClick={() => navigate(`/household/${groupId}/expenses`)}
          >
            ← Back
          </button>
        </div>

        {/* Form Card */}
        <div className="card p-4 shadow mx-auto" style={{ maxWidth: "600px" }}>
          <form onSubmit={handleSubmit}>

            <p className="text-muted text-center mb-4">
              Enter the expense information
            </p>

            <div className="row mb-3">
              <div className="col">
                <label className="form-label">Expense Name</label>
                <input
                  className="form-control"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                />
              </div>

              <div className="col">
                <label className="form-label">Total Amount</label>
                <input
                  className="form-control"
                  name="amount"
                  value={form.amount}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label">Category</label>
              <input
                className="form-control"
                name="category"
                value={form.category}
                onChange={handleChange}
              />
            </div>

            {/* Member row UI (matches your mockup) */}
            <div className="card p-3 mb-4">
              <div className="d-flex justify-content-between align-items-center">
                <div className="d-flex align-items-center gap-2">
                  <div
                    style={{
                      width: "35px",
                      height: "35px",
                      borderRadius: "50%",
                      background: "#ccc",
                    }}
                  />
                  <span className="small text-muted">Member Name</span>
                </div>

                <div
                  style={{
                    width: "40px",
                    height: "10px",
                    background: "#ccc",
                    borderRadius: "5px",
                  }}
                />
              </div>
            </div>

            <button type="submit" className="btn btn-dark w-100">
              Add Expense
            </button>

          </form>
        </div>

      </div>
    </div>
  );
};

export default AddExpense;