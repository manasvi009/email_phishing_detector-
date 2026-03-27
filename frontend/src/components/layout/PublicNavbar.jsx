import { Menu, Shield, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

export default function PublicNavbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/85 backdrop-blur-2xl">
      <div className="section-wrap flex items-center justify-between py-4">
        <Link to="/" className="flex items-center gap-3">
          <div className="rounded-2xl border border-blue-200 bg-blue-50 p-2.5 text-blue-600 shadow-glow">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="display-title text-base font-bold text-slate-900">PhishGuard AI</div>
            <div className="text-xs uppercase tracking-[0.24em] text-slate-500">AI Email Security</div>
          </div>
        </Link>
        <nav className="hidden items-center gap-7 text-sm text-slate-600 lg:flex">
          <a className="transition hover:text-slate-900" href="#features">Features</a>
          <a className="transition hover:text-slate-900" href="#scanner">Scanner</a>
          <a className="transition hover:text-slate-900" href="#dashboard-preview">Dashboard</a>
          <Link className="transition hover:text-slate-900" to="/pricing">Pricing</Link>
          <Link className="transition hover:text-slate-900" to="/login">Login</Link>
        </nav>
        <div className="hidden items-center gap-3 lg:flex">
          <Link to="/dashboard" className="secondary-button">View Dashboard</Link>
          <Link to="/register" className="primary-button gap-2">
            <Sparkles className="h-4 w-4" />
            Get Started
          </Link>
        </div>
        <button className="rounded-2xl border border-slate-200 bg-white p-3 text-slate-900 lg:hidden">
          <Menu className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
