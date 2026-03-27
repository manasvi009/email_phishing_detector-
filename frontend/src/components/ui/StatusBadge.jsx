const tones = {
  phishing: "border-red-200 bg-red-50 text-red-600",
  suspicious: "border-orange-200 bg-orange-50 text-orange-600",
  safe: "border-emerald-200 bg-emerald-50 text-emerald-600",
  info: "border-blue-200 bg-blue-50 text-blue-600",
};

export default function StatusBadge({ label }) {
  const toneKey = label.toLowerCase();
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${tones[toneKey] || tones.info}`}>
      {label}
    </span>
  );
}
