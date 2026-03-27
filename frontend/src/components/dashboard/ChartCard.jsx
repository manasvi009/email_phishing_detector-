export default function ChartCard({ title, description, children }) {
  return (
    <div className="glass-panel rounded-[28px] p-6">
      <div className="mb-5">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        {description ? <p className="mt-2 text-sm text-slate-600">{description}</p> : null}
      </div>
      {children}
    </div>
  );
}
