import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  const linkClass = "px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100";

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
        <div className="flex items-center gap-1">
          <span className="font-semibold text-slate-800 mr-4">🅿️ Society Parking</span>
          <Link to="/dashboard" className={linkClass}>Dashboard</Link>
          <Link to="/parking-map" className={linkClass}>Parking Map</Link>
          {user.role === "admin" && <Link to="/admin" className={linkClass}>Admin</Link>}
          <Link to="/profile" className={linkClass}>Profile</Link>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-500 hidden sm:inline">{user.name}</span>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 text-sm font-medium text-white bg-slate-800 rounded-md hover:bg-slate-700"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
