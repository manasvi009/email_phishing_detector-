export default function AlertCard({ alert }) {
  const toneClasses = {
    danger: "border-red-200 bg-red-50",
    warning: "border-orange-200 bg-orange-50",
    info: "border-blue-200 bg-blue-50",
    success: "border-emerald-200 bg-emerald-50",
  };

  return (
    <div className={`rounded-3xl border p-4 ${toneClasses[alert.tone] || toneClasses.info}`}>
      <h4 className="font-semibold text-slate-900">{alert.title}</h4>
      <p className="mt-2 text-sm leading-6 text-slate-600">{alert.description}</p>
    </div>
  );
}
