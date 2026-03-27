import { Github, Linkedin, Shield } from "lucide-react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white/70">
      <div className="section-wrap grid gap-10 py-12 lg:grid-cols-[1.2fr_repeat(3,1fr)]">
        <div>
          <Link to="/" className="flex items-center gap-3 text-slate-900">
            <div className="rounded-2xl border border-blue-200 bg-blue-50 p-2">
              <Shield className="h-5 w-5 text-blue-600" />
            </div>
            <span className="display-title text-lg font-semibold">PhishGuard AI</span>
          </Link>
          <p className="mt-4 max-w-sm text-sm leading-6 text-slate-600">
            AI-powered phishing detection for modern teams. Built for demos, client presentations, and startup-grade product showcases.
          </p>
          <div className="mt-5 flex items-center gap-4 text-slate-500">
            <Github className="h-5 w-5" />
            <Linkedin className="h-5 w-5" />
          </div>
        </div>
        {[
          ["Product", ["Features", "Scanner", "Dashboard", "Analytics"]],
          ["Company", ["Pricing", "Security", "Privacy Policy", "Contact"]],
          ["Resources", ["Documentation", "GitHub", "Demo", "Support"]],
        ].map(([title, items]) => (
          <div key={title}>
            <h4 className="font-semibold text-slate-900">{title}</h4>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              {items.map((item) => (
                <div key={item}>{item}</div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </footer>
  );
}
