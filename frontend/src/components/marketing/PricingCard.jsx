import { Check, Sparkles } from "lucide-react";

export default function PricingCard({ plan }) {
  return (
    <div className={`glass-panel relative rounded-[28px] p-6 ${plan.featured ? "border-blue-200 shadow-glow" : ""}`}>
      {plan.featured ? (
        <div className="absolute right-5 top-5 inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
          <Sparkles className="h-3.5 w-3.5" />
          Most Popular
        </div>
      ) : null}
      <p className="text-sm font-medium text-blue-600">{plan.name}</p>
      <div className="mt-4 text-4xl font-bold text-slate-900">{plan.price}</div>
      <p className="mt-3 text-sm leading-6 text-slate-600">{plan.description}</p>
      <div className="mt-6 space-y-3">
        {plan.features.map((feature) => (
          <div key={feature} className="flex items-start gap-3 text-sm text-slate-600">
            <Check className="mt-0.5 h-4 w-4 flex-none text-emerald-500" />
            <span>{feature}</span>
          </div>
        ))}
      </div>
      <button className={`mt-8 w-full rounded-2xl px-4 py-3 font-semibold ${plan.featured ? "bg-blue-600 text-white" : "border border-slate-200 bg-white text-slate-900"}`}>
        {plan.featured ? "Upgrade to Pro" : "Choose Plan"}
      </button>
    </div>
  );
}
