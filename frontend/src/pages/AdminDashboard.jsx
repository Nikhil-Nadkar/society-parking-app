import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import {
  approvePayment, assignParkingSlot, createParkingSlot, listParkingSlots,
  listPayments, listUsers, rejectPayment, screenshotUrl,
} from "../api/admin";

const TABS = ["Payments", "Users", "Parking"];

export default function AdminDashboard() {
  const [tab, setTab] = useState("Payments");

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-xl font-semibold text-slate-800 mb-1">Admin Dashboard</h1>
        <p className="text-sm text-slate-500 mb-6">Manage residents, parking slots, and payment approvals.</p>

        <div className="flex gap-1 mb-6 border-b border-slate-200">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px ${
                tab === t ? "border-slate-800 text-slate-800" : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === "Payments" && <PaymentsTab />}
        {tab === "Users" && <UsersTab />}
        {tab === "Parking" && <ParkingTab />}
      </div>
    </div>
  );
}

function PaymentsTab() {
  const [payments, setPayments] = useState([]);
  const [filter, setFilter] = useState("pending");
  const [loading, setLoading] = useState(true);
  const [rejectingId, setRejectingId] = useState(null);
  const [rejectReason, setRejectReason] = useState("");

  const load = () => {
    setLoading(true);
    listPayments(filter === "all" ? undefined : filter)
      .then(setPayments)
      .finally(() => setLoading(false));
  };

  useEffect(load, [filter]);

  const handleApprove = async (id) => {
    await approvePayment(id);
    load();
  };

  const handleReject = async (id) => {
    await rejectPayment(id, rejectReason || undefined);
    setRejectingId(null);
    setRejectReason("");
    load();
  };

  return (
    <div>
      <div className="flex gap-2 mb-4">
        {["pending", "approved", "rejected", "all"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
              filter === f ? "bg-slate-800 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-slate-400">Loading...</p>
      ) : payments.length === 0 ? (
        <p className="text-sm text-slate-400">No payments found.</p>
      ) : (
        <div className="space-y-3">
          {payments.map((p) => (
            <div key={p.id} className="bg-white rounded-lg border border-slate-200 p-4 flex flex-col sm:flex-row sm:items-center gap-4">
              <img
                src={screenshotUrl(p.id)}
                alt="screenshot"
                className="w-20 h-20 object-cover rounded-md border border-slate-200 cursor-pointer"
                onClick={() => window.open(screenshotUrl(p.id), "_blank")}
              />
              <div className="flex-1 text-sm">
                <div className="font-medium text-slate-800">{p.user_name} · Flat {p.room_no}</div>
                <div className="text-slate-500">
                  {String(p.month).padStart(2, "0")}/{p.year} · ₹{p.amount} · {p.status}
                  {p.slot_number && ` · Slot ${p.slot_number}`}
                </div>
                {p.description && <div className="text-slate-400 text-xs mt-0.5">{p.description}</div>}
                {p.rejection_reason && <div className="text-red-500 text-xs mt-0.5">Reason: {p.rejection_reason}</div>}
              </div>

              {p.status === "pending" && (
                <div className="flex flex-col gap-2 sm:items-end">
                  {rejectingId === p.id ? (
                    <div className="flex flex-col gap-2 w-full sm:w-56">
                      <input
                        value={rejectReason}
                        onChange={(e) => setRejectReason(e.target.value)}
                        placeholder="Rejection reason (optional)"
                        className="border border-slate-300 rounded-md px-2 py-1 text-xs"
                      />
                      <div className="flex gap-2 justify-end">
                        <button onClick={() => setRejectingId(null)} className="text-xs text-slate-500 hover:underline">Cancel</button>
                        <button onClick={() => handleReject(p.id)} className="text-xs font-medium text-white bg-red-500 rounded-md px-3 py-1">Confirm reject</button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        onClick={() => setRejectingId(p.id)}
                        className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded-md hover:bg-red-50"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApprove(p.id)}
                        className="px-3 py-1.5 text-xs font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
                      >
                        Approve
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function UsersTab() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listUsers().then(setUsers).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-slate-400">Loading...</p>;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-500">
            <th className="px-4 py-2 font-medium">Name</th>
            <th className="px-4 py-2 font-medium">Email</th>
            <th className="px-4 py-2 font-medium">Phone</th>
            <th className="px-4 py-2 font-medium">Room</th>
            <th className="px-4 py-2 font-medium">Role</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-b border-slate-100">
              <td className="px-4 py-2">{u.name}</td>
              <td className="px-4 py-2 text-slate-500">{u.email}</td>
              <td className="px-4 py-2 text-slate-500">{u.phone}</td>
              <td className="px-4 py-2 text-slate-500">{u.room_no}</td>
              <td className="px-4 py-2 capitalize text-slate-500">{u.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ParkingTab() {
  const [slots, setSlots] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newSlotNumber, setNewSlotNumber] = useState("");
  const [newSlotType, setNewSlotType] = useState("resident");

  const load = () => {
    setLoading(true);
    Promise.all([listParkingSlots(), listUsers()])
      .then(([s, u]) => { setSlots(s); setUsers(u); })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newSlotNumber) return;
    await createParkingSlot({ slot_number: newSlotNumber, type: newSlotType });
    setNewSlotNumber("");
    load();
  };

  const handleAssign = async (slotId, userId) => {
    await assignParkingSlot(slotId, userId ? Number(userId) : null);
    load();
  };

  if (loading) return <p className="text-sm text-slate-400">Loading...</p>;

  return (
    <div>
      <form onSubmit={handleCreate} className="flex flex-wrap gap-2 mb-4">
        <input
          value={newSlotNumber}
          onChange={(e) => setNewSlotNumber(e.target.value)}
          placeholder="Slot number e.g. A-12"
          className="border border-slate-300 rounded-md px-3 py-1.5 text-sm"
        />
        <select
          value={newSlotType}
          onChange={(e) => setNewSlotType(e.target.value)}
          className="border border-slate-300 rounded-md px-3 py-1.5 text-sm"
        >
          <option value="resident">Resident</option>
          <option value="guest">Guest</option>
          <option value="delivery">Delivery</option>
        </select>
        <button type="submit" className="px-4 py-1.5 text-sm font-medium text-white bg-slate-800 rounded-md hover:bg-slate-700">
          + Add Slot
        </button>
      </form>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500">
              <th className="px-4 py-2 font-medium">Slot</th>
              <th className="px-4 py-2 font-medium">Type</th>
              <th className="px-4 py-2 font-medium">Status</th>
              <th className="px-4 py-2 font-medium">Assigned to</th>
            </tr>
          </thead>
          <tbody>
            {slots.map((slot) => (
              <tr key={slot.id} className="border-b border-slate-100">
                <td className="px-4 py-2 font-medium">{slot.slot_number}</td>
                <td className="px-4 py-2 capitalize text-slate-500">{slot.type}</td>
                <td className="px-4 py-2 capitalize text-slate-500">{slot.status}</td>
                <td className="px-4 py-2">
                  <select
                    value={slot.assigned_user_id || ""}
                    onChange={(e) => handleAssign(slot.id, e.target.value)}
                    className="border border-slate-300 rounded-md px-2 py-1 text-xs"
                  >
                    <option value="">Unassigned</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id} disabled={u.parking_slot_id && u.parking_slot_id !== slot.id}>
                        {u.name} (Flat {u.room_no})
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
