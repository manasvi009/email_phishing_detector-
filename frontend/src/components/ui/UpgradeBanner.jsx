import { ArrowRight, Sparkles } from "lucide-react";

export default function UpgradeBanner() {
  return (
    <div className="glass-panel-strong flex flex-col gap-4 rounded-[28px] p-6 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-blue-600">
          <Sparkles className="h-3.5 w-3.5" />
          Premium Upgrade
        </div>
        <h3 className="mt-4 text-2xl font-semibold text-slate-900">Unlock shared analyst workflows and deeper security insights</h3>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          Upgrade for real-time monitoring, team dashboards, advanced reports, and premium alert routing.
        </p>
      </div>
      <button className="primary-button gap-2">
        Upgrade Now
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  );
}
