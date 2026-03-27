import { motion } from "framer-motion";
import {
  Activity,
  BellRing,
  ChartNoAxesCombined,
  FileSearch,
  GlobeLock,
  Link2,
  MailCheck,
  Radar,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
import PublicNavbar from "../components/layout/PublicNavbar";
import FeatureCard from "../components/marketing/FeatureCard";
import Footer from "../components/marketing/Footer";
import PricingCard from "../components/marketing/PricingCard";
import TestimonialCard from "../components/marketing/TestimonialCard";
import ScannerForm from "../components/scanner/ScannerForm";
import ResultCard from "../components/scanner/ResultCard";
import SectionHeading from "../components/ui/SectionHeading";
import { pricingPlans, testimonials, demoPhishingResult, dashboardStats, scanHistory } from "../data/mockData";
import { analyzeEmail } from "../services/api";

const features = [
  { icon: MailCheck, title: "AI Email Analysis", description: "Analyze suspicious content, tone, and phishing intent in seconds." },
  { icon: Link2, title: "Malicious URL Detection", description: "Inspect risky URLs, redirects, and lookalike domains before users click." },
  { icon: GlobeLock, title: "Sender Trust Scoring", description: "Profile sender identity, domain consistency, and brand impersonation signals." },
  { icon: FileSearch, title: "Header Inspection", description: "Surface authentication issues, reply-to mismatches, and mailbox anomalies." },
  { icon: Activity, title: "Scan History", description: "Keep track of previous scans, outcomes, and analyst actions in one place." },
  { icon: ChartNoAxesCombined, title: "Dashboard Analytics", description: "Review phishing trends, top threats, and safe-vs-risk ratios." },
  { icon: Radar, title: "Premium Monitoring", description: "Simulate enterprise-grade alerting and continuous inbound email review." },
  { icon: BellRing, title: "Threat Alerts", description: "Highlight suspicious senders, malicious patterns, and urgent escalations." },
];

export default function LandingPage() {
  const [result, setResult] = useState({ ...demoPhishingResult, subject: "Urgent account verification required", sender: "security@paypaI-alert.com" });
  const [loading, setLoading] = useState(false);

  async function handleAnalyze(payload) {
    setLoading(true);
    const response = await analyzeEmail(payload);
    setResult(response);
    setLoading(false);
  }

  return (
    <div className="page-shell">
      <div className="absolute inset-0 opacity-25">
        <div className="grid-overlay h-full w-full" />
      </div>
      <div className="ambient-orb left-[-5rem] top-12 h-72 w-72 bg-sky-300/20" />
      <div className="ambient-orb right-[-4rem] top-28 h-80 w-80 bg-blue-200/30" />
      <PublicNavbar />
      <main className="relative">
        <section className="section-wrap grid gap-10 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:py-24">
          <div className="flex flex-col justify-center">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              <span className="eyebrow-chip">
                AI Email Security Platform
              </span>
              <h1 className="display-title mt-6 text-5xl font-black tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
                Detect phishing emails with a clean, professional workspace
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
                A modern email security platform for analyzing suspicious messages, surfacing risky links, and presenting results in a light interface that feels polished, trustworthy, and business-ready.
              </p>
            </motion.div>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/scanner" className="primary-button">Try Scanner</Link>
              <Link to="/dashboard" className="secondary-button">View Dashboard</Link>
              <Link to="/register" className="secondary-button">Get Started</Link>
            </div>
            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {dashboardStats.slice(0, 3).map((stat) => (
                <div key={stat.label} className="metric-tile">
                  <div className="text-sm uppercase tracking-[0.18em] text-slate-500">{stat.label}</div>
                  <div className="mt-3 display-title text-3xl font-bold text-slate-900">{stat.value}</div>
                  <div className="mt-2 text-sm text-blue-600">{stat.change}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="hero-panel p-6">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Threat Analysis Console</div>
                <div className="display-title mt-1 text-lg font-semibold text-slate-900">Live phishing detection snapshot</div>
              </div>
              <span className="rounded-full border border-red-200 bg-red-50 px-3 py-1 text-xs font-semibold text-red-600">High Risk</span>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="metric-tile">
                <div className="text-sm text-slate-400">Detection accuracy</div>
                <div className="display-title mt-3 text-4xl font-bold text-slate-900">99.2%</div>
              </div>
              <div className="metric-tile">
                <div className="text-sm text-slate-400">Threats blocked</div>
                <div className="display-title mt-3 text-4xl font-bold text-red-500">1,248</div>
              </div>
            </div>
            <div className="metric-tile mt-4">
              <div className="text-sm text-slate-400">Latest suspicious email</div>
              <div className="display-title mt-3 text-xl font-semibold text-slate-900">Mailbox storage exceeded</div>
              <div className="mt-2 text-sm text-slate-400">admin@microsoftr-support.com</div>
              <div className="mt-4 h-2 rounded-full bg-slate-200">
                <div className="h-2 w-[82%] rounded-full bg-gradient-to-r from-red-400 via-amber-300 to-red-500" />
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-600">
                Multiple risky keywords, brand impersonation, and malicious redirect patterns were detected.
              </p>
            </div>
          </div>
        </section>

        <section id="features" className="section-wrap py-20">
          <SectionHeading eyebrow="Capabilities" title="Purpose-built for modern phishing analysis" description="Everything you need to demo a realistic AI cybersecurity SaaS platform with trust, depth, and premium UX." align="center" />
          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {features.map((feature) => <FeatureCard key={feature.title} {...feature} />)}
          </div>
        </section>

        <section id="scanner" className="section-wrap py-20">
          <SectionHeading eyebrow="Live Demo Scanner" title="Scan suspicious emails, sender identity, and risky links" description="Paste suspicious content or upload evidence and preview a realistic phishing risk response with AI explanation." />
          <div className="mt-12 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
            <ScannerForm onAnalyze={handleAnalyze} loading={loading} compact />
            <ResultCard result={result} />
          </div>
        </section>

        <section className="section-wrap py-20">
          <SectionHeading eyebrow="How It Works" title="Simple workflow, enterprise-grade presentation" description="A clean, recruiter-friendly experience that still feels realistic and product-focused." align="center" />
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {[
              ["1", "Upload or paste suspicious content", "Add sender data, suspicious URLs, screenshots, or full email text."],
              ["2", "AI and ML inspect the message", "Analyze threat language, sender trust, links, headers, and phishing patterns."],
              ["3", "Get instant risk scoring", "Review a phishing verdict, suspicious indicators, and a recommended next action."],
            ].map(([step, title, description]) => (
              <div key={step} className="glass-panel rounded-[28px] p-6">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-lg font-bold text-blue-600">{step}</div>
                <h3 className="display-title mt-5 text-xl font-semibold text-slate-900">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="dashboard-preview" className="section-wrap py-20">
          <SectionHeading eyebrow="Dashboard Preview" title="A realistic cybersecurity SaaS dashboard" description="Threat metrics, charts, alerts, and scan history in a polished workspace built for portfolio presentations and startup demos." />
          <div className="mt-12 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="glass-panel rounded-[28px] p-6">
              <div className="grid gap-4 sm:grid-cols-4">
                {[
                  ["Total scans", "24,892"],
                  ["Safe emails", "21,341"],
                  ["Phishing detected", "1,248"],
                  ["Weekly trend", "+18%"],
                ].map(([label, value]) => (
                  <div key={label} className="metric-tile p-4">
                    <div className="text-sm text-slate-400">{label}</div>
                    <div className="display-title mt-2 text-2xl font-bold text-slate-900">{value}</div>
                  </div>
                ))}
              </div>
              <div className="metric-tile mt-6">
                <div className="text-sm text-slate-400">Recent scan list</div>
                <div className="mt-4 space-y-3">
                  {scanHistory.slice(0, 4).map((item) => (
                    <div key={item.id} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3">
                      <div>
                        <div className="font-medium text-slate-900">{item.subject}</div>
                        <div className="text-sm text-slate-500">{item.target}</div>
                      </div>
                      <div className="text-sm text-slate-600">{item.riskScore}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="glass-panel rounded-[28px] p-6">
              <div className="display-title text-lg font-semibold text-slate-900">Threat categories</div>
              <div className="mt-6 space-y-4">
                {[
                  ["Credential harvesting", "42%"],
                  ["Domain impersonation", "31%"],
                  ["Invoice phishing", "18%"],
                  ["Account takeover", "9%"],
                ].map(([name, value]) => (
                  <div key={name}>
                    <div className="mb-2 flex items-center justify-between text-sm text-slate-600">
                      <span>{name}</span>
                      <span>{value}</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-200">
                      <div className="h-2 rounded-full bg-gradient-to-r from-blue-600 to-sky-400" style={{ width: value }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="section-wrap py-20">
          <SectionHeading eyebrow="Pricing" title="Simple plans for individuals and teams" description="Clean, high-converting pricing designed like a real cybersecurity SaaS product." align="center" />
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {pricingPlans.map((plan) => <PricingCard key={plan.name} plan={plan} />)}
          </div>
        </section>

        <section className="section-wrap py-20">
          <SectionHeading eyebrow="Testimonials" title="Teams trust the product presentation" description="Three realistic voices that make the product feel credible for demos and portfolio reviews." align="center" />
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {testimonials.map((item) => <TestimonialCard key={item.name} item={item} />)}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
