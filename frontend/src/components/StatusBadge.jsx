const STATUS_CONFIG = {
  approved: { emoji: "🟢", label: "Paid", classes: "bg-green-100 text-green-800" },
  pending: { emoji: "🟠", label: "Pending", classes: "bg-orange-100 text-orange-800" },
  overdue: { emoji: "🔴", label: "Overdue", classes: "bg-red-100 text-red-800" },
  rejected: { emoji: "❌", label: "Rejected", classes: "bg-red-100 text-red-800" },
  due: { emoji: "⚪", label: "Due", classes: "bg-slate-100 text-slate-600" },
  not_due: { emoji: "⚫", label: "Not due", classes: "bg-slate-50 text-slate-400" },
};

export default function StatusBadge({ status, size = "md" }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.due;
  const sizeClasses = size === "sm" ? "text-xs px-1.5 py-0.5" : "text-xs px-2 py-1";

  return (
    <span className={`inline-flex items-center gap-1 rounded-full font-medium ${sizeClasses} ${config.classes}`}>
      <span>{config.emoji}</span>
      {config.label}
    </span>
  );
}

export { STATUS_CONFIG };
