import AuthLayout from "./AuthLayout";

export default function VerifyOtpPage() {
  return (
    <AuthLayout
      title="Verify OTP"
      description="Enter the one-time code sent to your email and set a new password."
      footerText="Need a new code?"
      footerLink={{ href: "/forgot-password", label: "Resend OTP" }}
    >
      <form className="space-y-4">
        <div className="grid grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((item) => (
            <input key={item} className="input-shell text-center text-lg" maxLength={1} />
          ))}
        </div>
        <input className="input-shell" type="password" placeholder="New password" />
        <button className="primary-button w-full">Verify and Reset</button>
      </form>
    </AuthLayout>
  );
}
