import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import AuthLayout from "./AuthLayout";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to review phishing reports, monitor alerts, and manage your AI security workspace."
      footerText="Don't have an account?"
      footerLink={{ href: "/register", label: "Create one" }}
    >
      <form className="space-y-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Work email</label>
          <input className="input-shell" type="email" placeholder="analyst@company.com" />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
          <div className="relative">
            <input className="input-shell pr-12" type={showPassword ? "text" : "password"} placeholder="Enter your password" />
            <button type="button" onClick={() => setShowPassword((current) => !current)} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
        <div className="flex items-center justify-between text-sm text-slate-600">
          <label className="flex items-center gap-2">
            <input type="checkbox" className="rounded border-slate-300 bg-white" />
            Remember me
          </label>
          <a href="/forgot-password" className="text-blue-600">Forgot password?</a>
        </div>
        <button className="primary-button w-full">Sign In</button>
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          Validation preview: invalid credentials or OTP challenge messages would appear here.
        </div>
      </form>
    </AuthLayout>
  );
}
