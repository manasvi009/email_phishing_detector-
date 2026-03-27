import { motion } from "framer-motion";
import { Shield } from "lucide-react";
import { Link } from "react-router-dom";

export default function AuthLayout({ title, description, children, footerLink, footerText }) {
  return (
    <div className="page-shell min-h-screen">
      <div className="ambient-orb left-[-5rem] top-20 h-56 w-56 bg-sky-300/20" />
      <div className="ambient-orb right-[-3rem] top-40 h-64 w-64 bg-blue-200/30" />
      <div className="section-wrap flex min-h-screen items-center justify-center py-10">
        <div className="grid w-full max-w-6xl gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="hero-panel hidden flex-col justify-between p-10 lg:flex">
            <div>
              <div className="eyebrow-chip gap-3 px-4 py-2">
                <Shield className="h-5 w-5" />
                PhishGuard AI
              </div>
              <h2 className="display-title mt-8 text-4xl font-bold leading-tight text-slate-900">Secure access for analysts, founders, and teams</h2>
              <p className="mt-5 max-w-md text-slate-600">
                Build a polished authentication experience with a bright, trustworthy interface and a professional product tone.
              </p>
            </div>
            <div className="metric-tile">
              <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Security note</div>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                All screens are designed for demo mode and recruiter-friendly presentation, including validation and smooth transitions.
              </p>
            </div>
          </div>
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-panel mx-auto w-full max-w-xl rounded-[32px] p-8 sm:p-10">
            <Link to="/" className="text-sm text-blue-600">Back to home</Link>
            <h1 className="display-title mt-6 text-3xl font-bold text-slate-900">{title}</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            <div className="mt-8">{children}</div>
            <div className="mt-6 text-sm text-slate-600">
              {footerText}{" "}
              <Link to={footerLink.href} className="font-medium text-blue-600">
                {footerLink.label}
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
