import { useState } from "react";
import { UploadCloud } from "lucide-react";

export default function ScannerForm({ onAnalyze, loading, compact = false }) {
  const [formData, setFormData] = useState({
    subject: "",
    sender: "",
    url: "",
    content: "",
    fileName: "",
  });
  const [errors, setErrors] = useState({});

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  function handleFile(event) {
    const file = event.target.files?.[0];
    setFormData((current) => ({ ...current, fileName: file ? file.name : "" }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const nextErrors = {};
    if (!formData.content && !formData.url && !formData.sender) {
      nextErrors.content = "Add email text, sender details, or a suspicious URL.";
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    onAnalyze(formData);
  }

  return (
    <form onSubmit={handleSubmit} className={`glass-panel rounded-[28px] p-6 ${compact ? "" : "h-full"}`}>
      <div className="grid gap-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Email Subject</label>
          <input name="subject" value={formData.subject} onChange={handleChange} className="input-shell" placeholder="Urgent: Verify your mailbox" />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Sender Email</label>
          <input name="sender" value={formData.sender} onChange={handleChange} className="input-shell" placeholder="security@lookalike-domain.com" />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Suspicious URL</label>
          <input name="url" value={formData.url} onChange={handleChange} className="input-shell" placeholder="https://verify-account.example" />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Email Content</label>
          <textarea
            name="content"
            value={formData.content}
            onChange={handleChange}
            rows={compact ? 6 : 9}
            className="input-shell resize-none"
            placeholder="Paste suspicious email content here..."
          />
          {errors.content ? <p className="mt-2 text-sm text-red-500">{errors.content}</p> : null}
        </div>
        <label className="flex cursor-pointer items-center gap-3 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-4 text-sm text-slate-600 transition hover:border-blue-300 hover:bg-blue-50/50">
          <UploadCloud className="h-5 w-5 text-blue-600" />
          <span>{formData.fileName || "Upload screenshot or email file"}</span>
          <input type="file" className="hidden" onChange={handleFile} />
        </label>
        <button type="submit" disabled={loading} className="primary-button w-full">
          {loading ? "Analyzing..." : "Analyze Now"}
        </button>
      </div>
    </form>
  );
}
