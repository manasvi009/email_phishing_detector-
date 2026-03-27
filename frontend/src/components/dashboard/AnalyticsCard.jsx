export default function AnalyticsCard({ stat }) {
  return (
    <div className="glass-panel rounded-[28px] p-5">
      <div className="text-sm text-slate-400">{stat.label}</div>
      <div className="mt-3 text-3xl font-bold text-slate-900">{stat.value}</div>
      <div className="mt-2 text-sm text-blue-600">{stat.change}</div>
    </div>
  );
}
