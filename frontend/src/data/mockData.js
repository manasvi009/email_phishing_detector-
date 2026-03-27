export const testimonials = [
  {
    name: "Ava Morgan",
    role: "Founder, MailShield Labs",
    quote:
      "The product looks and feels like a launch-ready security SaaS. It gives us a polished scanner and a dashboard we can actually demo to clients.",
  },
  {
    name: "Daniel Kim",
    role: "Security Analyst",
    quote:
      "The phishing insights are easy to understand, and the dashboard layout mirrors what teams expect from enterprise-grade monitoring tools.",
  },
  {
    name: "Priya Nair",
    role: "Freelancer & Student",
    quote:
      "It helped me present a realistic AI security product in my portfolio with a design that feels trustworthy and modern.",
  },
];

export const pricingPlans = [
  {
    name: "Free",
    price: "$0",
    description: "For demos, testing, and light phishing triage.",
    features: ["25 scans per day", "Basic scan history", "Email paste scanner", "Mock AI explanations"],
  },
  {
    name: "Pro",
    price: "$29",
    description: "For professionals who need deeper insights and unlimited scans.",
    features: ["Unlimited scans", "Advanced analytics", "Full history access", "Priority support"],
    featured: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For organizations that need team workflows and premium monitoring.",
    features: ["Team workspaces", "Admin controls", "API access", "Dedicated onboarding"],
  },
];

export const dashboardStats = [
  { label: "Total scans", value: "24,892", change: "+12.4%" },
  { label: "Phishing detected", value: "1,248", change: "+8.7%" },
  { label: "Safe emails", value: "21,341", change: "+5.2%" },
  { label: "Premium usage", value: "78%", change: "+14.1%" },
  { label: "Scans remaining", value: "420", change: "Pro plan" },
];

export const weeklyScans = [
  { name: "Mon", safe: 280, phishing: 52 },
  { name: "Tue", safe: 310, phishing: 61 },
  { name: "Wed", safe: 344, phishing: 74 },
  { name: "Thu", safe: 298, phishing: 64 },
  { name: "Fri", safe: 360, phishing: 82 },
  { name: "Sat", safe: 188, phishing: 29 },
  { name: "Sun", safe: 204, phishing: 35 },
];

export const threatBreakdown = [
  { name: "Phishing", value: 48 },
  { name: "Safe", value: 39 },
  { name: "Suspicious", value: 13 },
];

export const monthlyThreats = [
  { month: "Jan", threats: 92 },
  { month: "Feb", threats: 118 },
  { month: "Mar", threats: 144 },
  { month: "Apr", threats: 130 },
  { month: "May", threats: 162 },
  { month: "Jun", threats: 176 },
];

export const analyticsOverview = [
  { month: "Jan", phishingRate: 11, safeRatio: 89, suspiciousSenders: 18 },
  { month: "Feb", phishingRate: 14, safeRatio: 86, suspiciousSenders: 24 },
  { month: "Mar", phishingRate: 17, safeRatio: 83, suspiciousSenders: 29 },
  { month: "Apr", phishingRate: 16, safeRatio: 84, suspiciousSenders: 25 },
  { month: "May", phishingRate: 19, safeRatio: 81, suspiciousSenders: 32 },
  { month: "Jun", phishingRate: 21, safeRatio: 79, suspiciousSenders: 37 },
];

export const topDomains = [
  { domain: "verify-billing-mail.net", count: 42 },
  { domain: "microsoft-auth-warning.co", count: 34 },
  { domain: "secure-payments-alert.io", count: 27 },
  { domain: "onedrive-security-check.org", count: 24 },
  { domain: "company-payroll-check.com", count: 21 },
];

export const phishingKeywords = [
  { keyword: "verify now", count: 88 },
  { keyword: "account suspended", count: 64 },
  { keyword: "urgent action", count: 52 },
  { keyword: "password reset", count: 45 },
  { keyword: "invoice overdue", count: 33 },
];

export const scanHistory = [
  {
    id: "SC-1034",
    date: "2026-03-26 10:45",
    target: "security@paypaI-alert.com",
    subject: "Urgent account verification required",
    result: "Phishing",
    riskScore: 92,
  },
  {
    id: "SC-1035",
    date: "2026-03-26 09:21",
    target: "accounts@company.com",
    subject: "Q2 payroll update",
    result: "Safe",
    riskScore: 12,
  },
  {
    id: "SC-1036",
    date: "2026-03-25 17:03",
    target: "admin@microsoftr-support.com",
    subject: "Mailbox storage exceeded",
    result: "Suspicious",
    riskScore: 67,
  },
  {
    id: "SC-1037",
    date: "2026-03-25 14:14",
    target: "billing@vendor-payments.net",
    subject: "Payment issue detected",
    result: "Phishing",
    riskScore: 89,
  },
  {
    id: "SC-1038",
    date: "2026-03-25 11:05",
    target: "events@startup.io",
    subject: "Event registration confirmed",
    result: "Safe",
    riskScore: 9,
  },
];

export const alerts = [
  { title: "Suspicious sender found", description: "A lookalike domain attempted to impersonate a known finance brand.", tone: "danger" },
  { title: "Malicious domain detected", description: "Three risky redirect links were flagged during a scanner run.", tone: "warning" },
  { title: "Scan limit threshold", description: "Your team is close to the monthly API limit for the current plan.", tone: "info" },
  { title: "Premium recommendation", description: "Upgrade to unlock team analytics and shared alert review workflows.", tone: "success" },
];

export const demoPhishingResult = {
  result: "Phishing",
  riskScore: 92,
  suspiciousLinks: 3,
  senderReputation: "Low",
  suspiciousKeywords: ["urgent verification", "account suspension", "password confirmation"],
  domainAnalysis: "Lookalike domain with inconsistent sender behavior",
  recommendedAction: "Do not click links. Quarantine email and report sender.",
  aiExplanation:
    "This email contains urgent language, suspicious domain patterns, and misleading call-to-action links commonly found in phishing attempts.",
};

export const demoSafeResult = {
  result: "Safe",
  riskScore: 12,
  suspiciousLinks: 0,
  senderReputation: "High",
  suspiciousKeywords: ["none"],
  domainAnalysis: "Trusted domain with normal delivery signals",
  recommendedAction: "No immediate action required.",
  aiExplanation:
    "This email appears safe based on its trusted domain, consistent sender data, and absence of manipulative or malicious indicators.",
};

export const notifications = [
  "Mailbox sync completed successfully",
  "Two new phishing alerts require review",
  "Team billing invoice is available",
];
