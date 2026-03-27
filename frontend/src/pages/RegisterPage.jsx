import AuthLayout from "./AuthLayout";

export default function RegisterPage() {
  return (
    <AuthLayout
      title="Create your workspace"
      description="Set up your phishing detection workspace for demos, team collaboration, and premium threat analysis."
      footerText="Already have an account?"
      footerLink={{ href: "/login", label: "Sign in" }}
    >
      <form className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <input className="input-shell" placeholder="Full name" />
          <input className="input-shell" placeholder="Company" />
        </div>
        <input className="input-shell" type="email" placeholder="team@company.com" />
        <input className="input-shell" type="password" placeholder="Create password" />
        <select className="input-shell">
          <option>Choose plan</option>
          <option>Free</option>
          <option>Pro</option>
          <option>Enterprise</option>
        </select>
        <button className="primary-button w-full">Create Workspace</button>
      </form>
    </AuthLayout>
  );
}
