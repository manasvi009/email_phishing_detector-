import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
import StatusBadge from "../ui/StatusBadge";

export default function ResultCard({ result }) {
  if (!result) {
    return (
      <div className="glass-panel flex h-full min-h-[440px] items-center justify-center rounded-[28px] p-8">
        <div className="text-center">
          <ShieldAlert className="mx-auto h-12 w-12 text-blue-600" />
          <h3 className="display-title mt-5 text-xl font-semibold text-slate-900">AI analysis results will appear here</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Submit an email, suspicious URL, or sender details to preview a phishing risk assessment.
          </p>
        </div>
      </div>
    );
  }

  const dangerous = result.result.toLowerCase() === "phishing";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel-strong h-full rounded-[28px] p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm uppercase tracking-[0.2em] text-slate-400">AI Result Summary</div>
          <h3 className="display-title mt-2 text-2xl font-semibold text-slate-900">{result.subject}</h3>
          <p className="mt-2 text-sm text-slate-600">{result.sender}</p>
        </div>
        <StatusBadge label={result.result} />
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="metric-tile">
          <div className="text-sm text-slate-400">Risk Score</div>
          <div className={`display-title mt-3 text-4xl font-bold ${dangerous ? "text-red-500" : "text-emerald-500"}`}>{result.riskScore}%</div>
          <div className="mt-4 h-3 rounded-full bg-slate-200">
            <div
              className={`h-3 rounded-full ${dangerous ? "bg-gradient-to-r from-red-400 via-amber-300 to-red-500" : "bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300"}`}
              style={{ width: `${result.riskScore}%` }}
            />
          </div>
        </div>
        <div className="metric-tile">
          <div className="text-sm text-slate-400">Sender Trust</div>
          <div className="display-title mt-3 text-2xl font-semibold text-slate-900">{result.senderReputation}</div>
          <div className="mt-3 flex items-center gap-2 text-sm text-slate-600">
            {dangerous ? <AlertTriangle className="h-4 w-4 text-red-300" /> : <CheckCircle2 className="h-4 w-4 text-emerald-300" />}
            Suspicious links found: {result.suspiciousLinks}
          </div>
        </div>
      </div>
      <div className="mt-6 grid gap-4">
        <div className="metric-tile">
          <div className="text-sm font-medium text-slate-900">Top Risk Factors</div>
          <div className="mt-4 flex flex-wrap gap-2">
            {result.suspiciousKeywords.map((item) => (
              <span key={item} className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600">
                {item}
              </span>
            ))}
          </div>
        </div>
        <div className="metric-tile">
          <div className="text-sm font-medium text-slate-900">Domain Analysis</div>
          <p className="mt-3 text-sm leading-6 text-slate-600">{result.domainAnalysis}</p>
        </div>
        <div className="metric-tile">
          <div className="text-sm font-medium text-slate-900">AI Explanation</div>
          <p className="mt-3 text-sm leading-6 text-slate-600">{result.aiExplanation}</p>
        </div>
        <div className="metric-tile">
          <div className="text-sm font-medium text-slate-900">Recommended Action</div>
          <p className="mt-3 text-sm leading-6 text-slate-600">{result.recommendedAction}</p>
        </div>
      </div>
    </motion.div>
  );
}
