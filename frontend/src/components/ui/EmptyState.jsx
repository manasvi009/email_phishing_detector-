import { ShieldAlert } from "lucide-react";

export default function EmptyState({ title, description }) {
  return (
    <div className="glass-panel flex flex-col items-center justify-center px-6 py-14 text-center">
      <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
        <ShieldAlert className="h-8 w-8 text-blue-600" />
      </div>
      <h3 className="mt-5 text-xl font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-slate-600">{description}</p>
    </div>
  );
}
