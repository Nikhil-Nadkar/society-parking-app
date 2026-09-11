import { useState } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../api/auth";
import { Field } from "./Register";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [devToken, setDevToken] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage("");
    setDevToken("");
    try {
      const data = await forgotPassword(email);
      setMessage(data.message);
      // Local/dev convenience: the API returns the token directly since there's no email service yet.
      if (data.reset_token) setDevToken(data.reset_token);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-md p-8">
        <h1 className="text-2xl font-semibold text-slate-800 mb-1">Forgot password</h1>
        <p className="text-sm text-slate-500 mb-6">We'll help you reset it.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-slate-800 text-white rounded-md py-2.5 text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
          >
            {submitting ? "Sending..." : "Send reset link"}
          </button>
        </form>

        {message && <p className="text-sm text-slate-600 mt-4">{message}</p>}
        {devToken && (
          <div className="mt-3 p-3 bg-slate-50 rounded-md border border-slate-200 text-xs break-all">
            <p className="text-slate-500 mb-1">Dev mode (no email service configured yet):</p>
            <Link to={`/reset-password?token=${devToken}`} className="text-slate-800 font-medium hover:underline">
              Click here to reset your password
            </Link>
          </div>
        )}

        <p className="text-sm text-slate-500 mt-5 text-center">
          <Link to="/login" className="text-slate-800 font-medium hover:underline">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
