export default function LoadingSkeleton({ className = "h-24" }) {
  return <div className={`animate-pulse rounded-3xl border border-slate-200 bg-slate-100 ${className}`} />;
}
