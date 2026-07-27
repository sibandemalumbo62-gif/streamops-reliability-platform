import type { ReactNode } from "react";
import Navigation from "../Navigation";

interface Props {
  children: ReactNode;
}

export default function DashboardLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-slate-100">

      <Navigation />

      <main className="p-6">
        {children}
      </main>

    </div>
  );
}