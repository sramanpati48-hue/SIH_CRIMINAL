import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

import { Providers } from "@/providers/Providers";

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
        <Providers>
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto bg-slate-950 p-6 md:p-8">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
