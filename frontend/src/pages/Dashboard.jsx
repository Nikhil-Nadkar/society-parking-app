import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import PaymentModal, { MONTH_NAMES } from "../components/PaymentModal";
import StatusBadge from "../components/StatusBadge";
import { getYearDashboard } from "../api/payments";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [year, setYear] = useState(new Date().getFullYear());
  const [months, setMonths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = () => {
    setLoading(true);
    getYearDashboard(year)
      .then(setMonths)
      .catch(() => setError("Could not load payment dashboard."))
      .finally(() => setLoading(false));
  };

  useEffect(loadDashboard, [year]);

  // "due" or "overdue" (i.e. unpaid) months are eligible for a new submission,
  // but the backend only accepts current + previous month regardless.
  const eligibleMonths = months.filter((m) => ["due", "overdue", "rejected"].includes(m.status));

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
          <div>
            <h1 className="text-xl font-semibold text-slate-800">Payment Dashboard</h1>
            <p className="text-sm text-slate-500">Track your monthly parking payments.</p>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="border border-slate-300 rounded-md px-2 py-1.5 text-sm"
            >
              {[year - 1, year, year + 1].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <button
              onClick={() => setShowModal(true)}
              disabled={eligibleMonths.length === 0}
              className="px-4 py-1.5 text-sm font-medium text-white bg-slate-800 rounded-md hover:bg-slate-700 disabled:opacity-40"
            >
              + Add Payment
            </button>
          </div>
        </div>

        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

        {/* Desktop table */}
        <div className="hidden md:block bg-white rounded-xl shadow-sm border border-slate-200 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="px-4 py-3 font-medium">User Details</th>
                {MONTH_NAMES.map((m) => (
                  <th key={m} className="px-2 py-3 font-medium text-center">{m.slice(0, 3)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-100">
                <td className="px-4 py-3 align-top">
                  <div className="font-medium text-slate-800">{user?.name}</div>
                  <div className="text-xs text-slate-500">Flat {user?.room_no}</div>
                  <div className="text-xs text-slate-500">{user?.phone}</div>
                </td>
                {loading
                  ? MONTH_NAMES.map((m) => <td key={m} className="px-2 py-3 text-center text-slate-300">...</td>)
                  : months.map((m) => (
                      <td key={`${m.year}-${m.month}`} className="px-2 py-3 text-center">
                        <StatusEmoji status={m.status} />
                      </td>
                    ))}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Mobile cards */}
        <div className="md:hidden space-y-2">
          {loading ? (
            <p className="text-sm text-slate-400">Loading...</p>
          ) : (
            months.map((m) => (
              <div
                key={`${m.year}-${m.month}`}
                className="bg-white rounded-lg border border-slate-200 px-4 py-3 flex items-center justify-between"
              >
                <span className="text-sm font-medium text-slate-700">
                  {MONTH_NAMES[m.month - 1]} {m.year}
                </span>
                <StatusBadge status={m.status} size="sm" />
              </div>
            ))
          )}
        </div>

        <div className="mt-6 flex flex-wrap gap-3 text-xs text-slate-500">
          <Legend emoji="🟢" label="Paid/Approved" />
          <Legend emoji="🟠" label="Submitted, pending" />
          <Legend emoji="🔴" label="Overdue" />
          <Legend emoji="❌" label="Rejected" />
          <Legend emoji="⚪" label="Due" />
        </div>
      </div>

      {showModal && (
        <PaymentModal
          eligibleMonths={eligibleMonths}
          onClose={() => setShowModal(false)}
          onSubmitted={() => {
            setShowModal(false);
            loadDashboard();
          }}
        />
      )}
    </div>
  );
}

function StatusEmoji({ status }) {
  const map = { approved: "🟢", pending: "🟠", overdue: "🔴", rejected: "❌", due: "⚪", not_due: "⚫" };
  return <span title={status}>{map[status] || "⚪"}</span>;
}

function Legend({ emoji, label }) {
  return (
    <span className="flex items-center gap-1">
      <span>{emoji}</span> {label}
    </span>
  );
}
