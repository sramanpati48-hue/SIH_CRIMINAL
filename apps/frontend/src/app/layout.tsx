import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "SIH 26189 - Criminal Network Analysis System",
  description:
    "AI-powered multi-modal criminal network analysis, link prediction, and evidence traceability platform (Synthetic Data Prototype).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased dark`}>
      <body className="h-full bg-slate-950 text-slate-100 flex overflow-hidden font-sans">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
          <Header />
          <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 flex items-center justify-center text-[11px] font-medium text-amber-500/90 tracking-wide z-50">
            Development reviewer mode: authentication is not enabled.
          </div>
          <main className="flex-1 overflow-y-auto bg-slate-950 p-6 md:p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
