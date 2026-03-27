import {
  BarChart3,
  CreditCard,
  History,
  LayoutDashboard,
  LogOut,
  ScanSearch,
  Settings,
  ShieldAlert,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Scan Email", href: "/scanner", icon: ScanSearch },
  { label: "URL Check", href: "/scanner?mode=url", icon: ShieldAlert },
  { label: "History", href: "/history", icon: History },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Pricing", href: "/pricing", icon: CreditCard },
  { label: "Settings", href: "/settings", icon: Settings },
];

export default function DashboardSidebar() {
  const location = useLocation();

  return (
    <aside className="glass-panel hidden h-[calc(100vh-2.5rem)] w-72 flex-col rounded-[32px] p-5 lg:flex">
      <div className="mb-8">
        <div className="eyebrow-chip mb-4 w-fit">Command Center</div>
        <div className="display-title text-2xl font-bold text-slate-900">PhishGuard AI</div>
        <div className="mt-1 text-sm text-slate-500">Security operations workspace</div>
      </div>
      <div className="space-y-2">
        {navItems.map(({ label, href, icon: Icon }) => {
          const isActive = location.pathname === href;
          return (
            <Link
              key={label}
              to={href}
              className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition ${
                isActive
                  ? "bg-blue-50 text-blue-700 shadow-glow"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </div>
      <div className="mt-auto rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 to-sky-50 p-4">
        <div className="display-title text-sm font-semibold text-slate-900">Premium plan</div>
        <p className="mt-2 text-xs leading-5 text-slate-600">Upgrade for team reports, live monitoring, and analyst workflows.</p>
      </div>
      <button className="mt-4 flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-slate-500 hover:bg-slate-50 hover:text-slate-900">
        <LogOut className="h-4 w-4" />
        Logout
      </button>
    </aside>
  );
}
