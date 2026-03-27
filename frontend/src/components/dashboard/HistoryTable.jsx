import { Eye, Trash2 } from "lucide-react";
import StatusBadge from "../ui/StatusBadge";

export default function HistoryTable({ rows }) {
  return (
    <div className="glass-panel overflow-hidden rounded-[28px]">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-500">
            <tr>
              <th className="px-5 py-4 font-medium">Date</th>
              <th className="px-5 py-4 font-medium">Email / URL</th>
              <th className="px-5 py-4 font-medium">Subject</th>
              <th className="px-5 py-4 font-medium">Result</th>
              <th className="px-5 py-4 font-medium">Risk Score</th>
              <th className="px-5 py-4 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-slate-100 text-slate-600">
                <td className="px-5 py-4">{row.date}</td>
                <td className="px-5 py-4">{row.target}</td>
                <td className="px-5 py-4">{row.subject}</td>
                <td className="px-5 py-4">
                  <StatusBadge label={row.result} />
                </td>
                <td className="px-5 py-4">{row.riskScore}%</td>
                <td className="px-5 py-4">
                  <div className="flex gap-2">
                    <button className="rounded-xl border border-slate-200 bg-white p-2 text-slate-600">
                      <Eye className="h-4 w-4" />
                    </button>
                    <button className="rounded-xl border border-slate-200 bg-white p-2 text-slate-600">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
