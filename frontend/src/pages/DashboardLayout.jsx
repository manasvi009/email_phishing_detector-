import DashboardSidebar from "../components/layout/DashboardSidebar";
import DashboardTopbar from "../components/layout/DashboardTopbar";

export default function DashboardLayout({ children }) {
  return (
    <div className="page-shell min-h-screen">
      <div className="ambient-orb left-[-5rem] top-24 h-72 w-72 bg-sky-300/20" />
      <div className="ambient-orb bottom-16 right-0 h-72 w-72 bg-blue-200/30" />
      <div className="section-wrap flex gap-6 py-5">
        <DashboardSidebar />
        <div className="min-w-0 flex-1">
          <DashboardTopbar />
          {children}
        </div>
      </div>
    </div>
  );
}
