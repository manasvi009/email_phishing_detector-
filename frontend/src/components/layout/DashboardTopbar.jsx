import { Bell, Crown, Search, ShieldCheck } from "lucide-react";
import { notifications } from "../../data/mockData";

export default function DashboardTopbar() {
  return (
    <div className="glass-panel mb-6 flex flex-col gap-4 rounded-[28px] p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="relative w-full max-w-xl">
        <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input className="input-shell pl-11" placeholder="Search scans, alerts, sender domains..." />
      </div>
      <div className="flex items-center gap-3 self-end sm:self-auto">
        <button className="secondary-button relative p-3">
          <Bell className="h-4 w-4" />
          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {notifications.length}
          </span>
        </button>
        <button className="secondary-button gap-2">
          <ShieldCheck className="h-4 w-4" />
          Quick Scan
        </button>
        <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2">
          <div className="rounded-full bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-600">
            <span className="inline-flex items-center gap-1">
              <Crown className="h-3 w-3" />
              Pro
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <div className="text-sm font-semibold text-slate-900">Analyst Mode</div>
              <div className="text-xs text-slate-500">Threat queue active</div>
            </div>
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-600 to-sky-400" />
          </div>
        </div>
      </div>
    </div>
  );
}
