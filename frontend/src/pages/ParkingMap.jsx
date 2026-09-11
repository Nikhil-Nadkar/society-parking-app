import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { getParkingMap } from "../api/payments";

const SLOT_COLORS = {
  guest: "bg-yellow-300 border-yellow-500",
  delivery: "bg-yellow-300 border-yellow-500",
  unused: "bg-slate-200 border-slate-300",
  approved: "bg-green-400 border-green-600",
  pending: "bg-orange-300 border-orange-500",
  overdue: "bg-red-400 border-red-600",
  rejected: "bg-red-400 border-red-600",
  due: "bg-slate-200 border-slate-300",
  not_due: "bg-slate-200 border-slate-300",
};

function colorForSlot(slot) {
  if (slot.type === "guest" || slot.type === "delivery") return SLOT_COLORS.guest;
  if (slot.status === "unused" || !slot.assigned_user_id) return SLOT_COLORS.unused;
  return SLOT_COLORS[slot.payment_status] || SLOT_COLORS.unused;
}

export default function ParkingMap() {
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    getParkingMap()
      .then(setSlots)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-xl font-semibold text-slate-800 mb-1">Parking Map</h1>
        <p className="text-sm text-slate-500 mb-6">Live view of slot occupancy and payment status.</p>

        {loading ? (
          <p className="text-sm text-slate-400">Loading...</p>
        ) : slots.length === 0 ? (
          <p className="text-sm text-slate-400">No parking slots configured yet.</p>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3">
              {slots.map((slot) => (
                <button
                  key={slot.id}
                  onClick={() => setSelected(slot)}
                  className={`aspect-[3/2] rounded-md border-2 flex flex-col items-center justify-center text-xs font-semibold text-slate-800 hover:opacity-80 transition ${colorForSlot(slot)}`}
                >
                  {slot.slot_number}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 flex flex-wrap gap-4 text-xs text-slate-600">
          <LegendSwatch color="bg-green-400" label="Paid" />
          <LegendSwatch color="bg-red-400" label="Overdue" />
          <LegendSwatch color="bg-orange-300" label="Pending approval" />
          <LegendSwatch color="bg-slate-200" label="Unused" />
          <LegendSwatch color="bg-yellow-300" label="Guest/Delivery" />
        </div>

        {selected && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-30 p-4" onClick={() => setSelected(null)}>
            <div className="bg-white rounded-xl shadow-xl w-full max-w-xs p-6" onClick={(e) => e.stopPropagation()}>
              <h2 className="text-lg font-semibold text-slate-800 mb-3">Slot {selected.slot_number}</h2>
              <div className="text-sm text-slate-600 space-y-1">
                <p><span className="text-slate-400">Type:</span> {selected.type}</p>
                <p><span className="text-slate-400">Status:</span> {selected.status}</p>
                {selected.resident_name && <p><span className="text-slate-400">Resident:</span> {selected.resident_name}</p>}
                {selected.payment_status && <p><span className="text-slate-400">This month:</span> {selected.payment_status}</p>}
              </div>
              <button
                onClick={() => setSelected(null)}
                className="mt-4 w-full px-3 py-1.5 text-sm font-medium text-white bg-slate-800 rounded-md hover:bg-slate-700"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function LegendSwatch({ color, label }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className={`w-3 h-3 rounded-sm border border-black/10 ${color}`} />
      {label}
    </span>
  );
}
