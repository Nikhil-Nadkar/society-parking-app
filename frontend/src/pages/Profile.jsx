import { useState } from "react";
import Navbar from "../components/Navbar";
import { updatePhone } from "../api/users";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [phone, setPhone] = useState(user?.phone || "");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const updated = await updatePhone(phone);
      refreshUser(updated);
      setEditing(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update phone number.");
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-md mx-auto px-4 py-8">
        <h1 className="text-xl font-semibold text-slate-800 mb-6">Profile</h1>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-4">
          <InfoRow label="Name" value={user.name} />
          <InfoRow label="Email" value={user.email} />
          <InfoRow label="Room/Flat No" value={user.room_no} />

          <div>
            <div className="text-xs text-slate-500 mb-1">Phone</div>
            {editing ? (
              <form onSubmit={handleSave} className="flex gap-2">
                <input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="flex-1 border border-slate-300 rounded-md px-3 py-1.5 text-sm"
                />
                <button
                  type="submit"
                  disabled={saving}
                  className="px-3 py-1.5 text-sm font-medium text-white bg-slate-800 rounded-md hover:bg-slate-700 disabled:opacity-50"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => { setEditing(false); setPhone(user.phone); }}
                  className="px-3 py-1.5 text-sm font-medium text-slate-500 rounded-md hover:bg-slate-100"
                >
                  Cancel
                </button>
              </form>
            ) : (
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-800">{user.phone}</span>
                <button
                  onClick={() => setEditing(true)}
                  className="text-xs font-medium text-slate-600 hover:underline"
                >
                  Edit
                </button>
              </div>
            )}
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}
          {success && <p className="text-sm text-green-700">Phone number updated.</p>}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div>
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className="text-sm font-medium text-slate-800">{value}</div>
    </div>
  );
}
