export default function TestimonialCard({ item }) {
  return (
    <div className="glass-panel rounded-[28px] p-6">
      <p className="text-sm leading-7 text-slate-600">"{item.quote}"</p>
      <div className="mt-6">
        <div className="font-semibold text-slate-900">{item.name}</div>
        <div className="text-sm text-slate-400">{item.role}</div>
      </div>
    </div>
  );
}
