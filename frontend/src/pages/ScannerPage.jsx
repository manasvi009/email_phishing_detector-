import { useState } from "react";
import DashboardLayout from "./DashboardLayout";
import SectionHeading from "../components/ui/SectionHeading";
import ScannerForm from "../components/scanner/ScannerForm";
import ResultCard from "../components/scanner/ResultCard";
import { analyzeEmail } from "../services/api";
import { demoSafeResult } from "../data/mockData";

export default function ScannerPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState({ ...demoSafeResult, subject: "Event registration confirmed", sender: "events@startup.io" });

  async function handleAnalyze(payload) {
    setLoading(true);
    const response = await analyzeEmail(payload);
    setResult(response);
    setLoading(false);
  }

  return (
    <DashboardLayout>
      <SectionHeading eyebrow="Scanner" title="Scan a suspicious email or URL" description="Run a realistic AI phishing analysis with mock API structure, animated loading, and premium result states." />
      <div className="mt-8 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <ScannerForm onAnalyze={handleAnalyze} loading={loading} />
        <ResultCard result={result} />
      </div>
    </DashboardLayout>
  );
}
