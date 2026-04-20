import { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8000/api/v1";

const AddExpense = () => {
  const navigate = useNavigate();
  const { groupId } = useParams();
  const location = useLocation();

  const editingExpense = location.state?.expense;

  const [form, setForm] = useState({
    name: editingExpense?.name || "",
    description: editingExpense?.description || "",
    amount: editingExpense?.amount || "",
    splitType: "even",
  });

  const [members, setMembers] = useState([]);
  const [selected, setSelected] = useState([]);
  const [customSplit, setCustomSplit] = useState({});

  useEffect(() => {
    const fetchMembers = async () => {
      const res = await fetch(`${API_BASE}/groups/${groupId}/users`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      const data = await res.json();

      if (res.ok) {
        setMembers(data);
        setSelected(data.map((m) => m.id));
      }
    };

    fetchMembers();
  }, [groupId]);

  const toggleUser = (id) => {
    setSelected((prev) =>
      prev.includes(id)
        ? prev.filter((u) => u !== id)
        : [...prev, id]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");

    // Validate custom %
    if (form.splitType === "custom") {
      const totalPercent = Object.values(customSplit).reduce(
        (sum, p) => sum + Number(p || 0),
        0
      );

      if (totalPercent !== 100) {
        alert("Custom split must equal 100%");
        return;
      }
    }

    let expenseId;

    if (editingExpense) {
      // UPDATE
      const res = await fetch(
        `${API_BASE}/expenses/${editingExpense.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: form.name,
            description: form.description,
            amount: Number(form.amount),
          }),
        }
      );

      const updated = await res.json();
      expenseId = updated.id;

    } else {
      // CREATE
      const res = await fetch(
        `${API_BASE}/expenses/group/${groupId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: form.name,
            description: form.description,
            amount: Number(form.amount),
          }),
        }
      );

      const created = await res.json();
      expenseId = created.id;
    }

    let splits = [];

    if (form.splitType === "even") {
      const splitAmount =
        Number(form.amount) / selected.length;

      splits = selected.map((id) => ({
        user_id: id,
        amount: splitAmount,
      }));
    }

    if (form.splitType === "custom") {
      splits = selected.map((id) => {
        const percent = Number(customSplit[id]) || 0;

        return {
          user_id: id,
          amount: (Number(form.amount) * percent) / 100,
        };
      });
    }

    await fetch(`${API_BASE}/expenses/${expenseId}/splits`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(splits),
    });

    navigate(`/household/${groupId}/expenses`);
  };

  return (
    <div className="container py-4">
      <h2 className="fw-bold mb-4">
        {editingExpense ? "Edit Expense" : "Add Expense"}
      </h2>

      <form onSubmit={handleSubmit}>

        <div className="mb-3">
          <label>Expense Name</label>
          <input
            className="form-control"
            value={form.name}
            onChange={(e) =>
              setForm({ ...form, name: e.target.value })
            }
          />
        </div>

        <div className="mb-3">
          <label>Description</label>
          <input
            className="form-control"
            value={form.description}
            onChange={(e) =>
              setForm({ ...form, description: e.target.value })
            }
          />
        </div>

        <div className="mb-3">
          <label>Amount</label>
          <input
            className="form-control"
            type="text"
            inputMode="decimal"
            value={form.amount}
            onChange={(e) => {
              const value = e.target.value;
              if (/^\d*\.?\d*$/.test(value)) {
                setForm({ ...form, amount: value });
              }
            }}
          />
        </div>

        <div className="mb-3">
          <label>Split Type</label>
          <select
            className="form-control"
            value={form.splitType}
            onChange={(e) =>
              setForm({ ...form, splitType: e.target.value })
            }
          >
            <option value="even">Even</option>
            <option value="custom">Custom %</option>
          </select>
        </div>

        <div className="mb-3">
          <label>Split Between</label>

          {members.map((m) => (
            <div
              key={m.id}
              className="d-flex justify-content-between align-items-center mb-2"
            >
              <div>
                <input
                  type="checkbox"
                  checked={selected.includes(m.id)}
                  onChange={() => toggleUser(m.id)}
                />
                <span className="ms-2">
                  {m.first_name} {m.last_name}
                </span>
              </div>

              {form.splitType === "custom" &&
                selected.includes(m.id) && (
                  <input
                    type="text"
                    inputMode="numeric"
                    placeholder="%"
                    style={{ width: "80px" }}
                    value={customSplit[m.id] || ""}
                    onChange={(e) => {
                      const value = e.target.value;

                      if (/^\d*$/.test(value) && Number(value) <= 100) {
                        setCustomSplit({
                          ...customSplit,
                          [m.id]: value,
                        });
                      }
                    }}
                  />
                )}
            </div>
          ))}
        </div>

        <button className="btn btn-dark w-100">
          {editingExpense ? "Update Expense" : "Add Expense"}
        </button>

      </form>
    </div>
  );
};

export default AddExpense;