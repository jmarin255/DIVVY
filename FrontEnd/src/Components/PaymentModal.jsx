import { useState } from "react";

const paymentMethods = ["Apple Pay", "Cash App", "PayPal"];

const PaymentModal = ({ expense, amount, onClose }) => {
  const [selectedMethod, setSelectedMethod] = useState("Apple Pay");
  const [status, setStatus] = useState("ready");

  if (!expense) return null;

  const expenseName =
    expense.name || expense.description || "Unnamed Expense";

  const payee =
    expense.paid_by_name ||
    expense.created_by_name ||
    expense.creator_name ||
    "the expense creator";

  const handlePayment = () => {
    setStatus("processing");

    setTimeout(() => {
      setStatus("success");
    }, 900);
  };

  return (
    <div className="payment-modal-backdrop" onClick={onClose}>
      <div
        className="payment-modal card shadow-lg"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h4 className="fw-bold mb-1">Settle Up</h4>
            <p className="text-muted mb-0">
              Simulated payment for this demo
            </p>
          </div>

          <button
            type="button"
            className="btn-close"
            aria-label="Close"
            onClick={onClose}
          />
        </div>

        {status === "success" ? (
          <div className="text-center py-4">
            <div className="payment-success-circle mx-auto mb-3">✓</div>

            <h5 className="fw-bold">Payment Initiated</h5>

            <p className="text-muted mb-4">
              Your ${Number(amount).toFixed(2)} payment for{" "}
              <strong>{expenseName}</strong> was simulated with{" "}
              <strong>{selectedMethod}</strong>.
            </p>

            <button className="btn btn-dark w-100" onClick={onClose}>
              Done
            </button>
          </div>
        ) : (
          <>
            <div className="payment-summary rounded-4 p-3 mb-3">
              <small className="text-muted d-block">Paying</small>
              <div className="fw-bold">{payee}</div>

              <hr />

              <div className="d-flex justify-content-between">
                <span className="text-muted">Expense</span>
                <span className="fw-semibold">{expenseName}</span>
              </div>

              <div className="d-flex justify-content-between mt-2">
                <span className="text-muted">Amount</span>
                <span className="fw-bold">
                  ${Number(amount).toFixed(2)}
                </span>
              </div>
            </div>

            <h6 className="fw-bold mb-2">Payment Method</h6>

            <div className="d-grid gap-2 mb-4">
              {paymentMethods.map((method) => (
                <button
                  key={method}
                  type="button"
                  className={
                    selectedMethod === method
                      ? "payment-method-option selected"
                      : "payment-method-option"
                  }
                  onClick={() => setSelectedMethod(method)}
                >
                  {method}
                </button>
              ))}
            </div>

            <button
              className="btn btn-dark w-100"
              onClick={handlePayment}
              disabled={status === "processing"}
            >
              {status === "processing"
                ? "Processing..."
                : `Pay $${Number(amount).toFixed(2)}`}
            </button>

            <button
              className="btn btn-outline-secondary w-100 mt-2"
              onClick={onClose}
              disabled={status === "processing"}
            >
              Cancel
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default PaymentModal;