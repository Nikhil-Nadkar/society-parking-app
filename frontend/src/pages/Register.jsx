import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "", email: "", phone: "", room_no: "", parking_no: "", password: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register({ ...form, parking_no: form.parking_no || undefined });
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-xl shadow-md p-8">
        <h1 className="text-2xl font-semibold text-slate-800 mb-1">Create your account</h1>
        <p className="text-sm text-slate-500 mb-6">Register to manage your society parking payments.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Full Name" value={form.name} onChange={update("name")} required />
          <Field label="Email" type="email" value={form.email} onChange={update("email")} required />
          <Field label="Phone" type="tel" value={form.phone} onChange={update("phone")} required />
          <div className="grid grid-cols-2 gap-3">
            <Field label="Room/Flat No" value={form.room_no} onChange={update("room_no")} required />
            <Field label="Parking No (optional)" value={form.parking_no} onChange={update("parking_no")} />
          </div>
          <Field label="Password" type="password" value={form.password} onChange={update("password")} required minLength={8} />

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-slate-800 text-white rounded-md py-2.5 text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
          >
            {submitting ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="text-sm text-slate-500 mt-5 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-slate-800 font-medium hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}

function Field({ label, ...props }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
      <input
        {...props}
        className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      />
    </div>
  );
}

export { Field };
