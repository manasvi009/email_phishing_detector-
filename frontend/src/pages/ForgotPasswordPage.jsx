import AuthLayout from "./AuthLayout";

export default function ForgotPasswordPage() {
  return (
    <AuthLayout
      title="Reset your password"
      description="Enter your work email to receive a reset code and continue to OTP verification."
      footerText="Remembered your password?"
      footerLink={{ href: "/login", label: "Back to login" }}
    >
      <form className="space-y-4">
        <input className="input-shell" type="email" placeholder="analyst@company.com" />
        <button className="primary-button w-full">Send Reset Code</button>
      </form>
    </AuthLayout>
  );
}
