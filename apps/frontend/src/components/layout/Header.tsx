"use client";

import { usePathname } from "next/navigation";
import React from "react";

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/": {
    title: "Dashboard Overview",
    subtitle: "Real-time overview of criminal network synthesis & investigative leads",
  },
  "/cases": {
    title: "Cases & Ingestion",
    subtitle: "Upload synthetic multi-modal FIRs, CDRs, forensics, and interrogation records",
  },
  "/graph": {
    title: "Network Graph",
    subtitle: "Interactive entity-relationship exploration & community detection",
  },
  "/evidence": {
    title: "Evidence & Traceability",
    subtitle: "Cryptographic provenance, source citations, and immutable audit chains",
  },
  "/audit": {
    title: "Verification & Audit",
    subtitle: "Human-in-the-loop validation, officer approvals, and compliance logs",
  },
  "/settings": {
    title: "System Settings",
    subtitle: "Pipeline configuration, model parameters, and access controls",
  },
};

export function Header() {
  const pathname = usePathname();

  // Determine current page info
  const currentRoute =
    pageTitles[pathname] ||
    Object.entries(pageTitles).find(([route]) =>
      route !== "/" && pathname.startsWith(route)
    )?.[1] || {
      title: "Investigative Workspace",
      subtitle: "Law enforcement decision-support intelligence platform",
    };

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800 px-8 flex items-center justify-between sticky top-0 z-30">
      <div>
        <h1 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          {currentRoute.title}
        </h1>
      </div>

      <div className="flex items-center gap-4">
        {/* System Status Indicator */}
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60 shadow-inner">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-medium text-slate-300">
            System Status: <span className="text-emerald-400 font-semibold">Online</span>
          </span>
        </div>

        {/* Prototype Version Tag */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 text-slate-400 text-xs font-mono border border-slate-700/50">
          <span>SIH-26189 v0.1.0</span>
        </div>
      </div>
    </header>
  );
}
