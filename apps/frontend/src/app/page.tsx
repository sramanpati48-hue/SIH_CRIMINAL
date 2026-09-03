import Link from "next/link";
import React from "react";

export default function DashboardOverview() {
  const stats = [
    {
      title: "Total Cases",
      value: "0",
      description: "Indexed synthetic case files",
      icon: (
        <svg
          className="w-6 h-6 text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
          />
        </svg>
      ),
      borderColor: "border-blue-500/30",
      iconBg: "bg-blue-500/10",
    },
    {
      title: "Active Investigations",
      value: "0",
      description: "Ongoing network analysis tasks",
      icon: (
        <svg
          className="w-6 h-6 text-indigo-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
      borderColor: "border-indigo-500/30",
      iconBg: "bg-indigo-500/10",
    },
    {
      title: "Pending Verifications",
      value: "0",
      description: "Awaiting human-in-the-loop review",
      icon: (
        <svg
          className="w-6 h-6 text-amber-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      borderColor: "border-amber-500/30",
      iconBg: "bg-amber-500/10",
    },
    {
      title: "Entities Extracted",
      value: "0",
      description: "Nodes identified in knowledge graph",
      icon: (
        <svg
          className="w-6 h-6 text-emerald-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      ),
      borderColor: "border-emerald-500/30",
      iconBg: "bg-emerald-500/10",
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Prominent Legal & Ethics Notice Banner */}
      <div className="rounded-xl bg-gradient-to-r from-blue-950/70 via-slate-900 to-slate-900 border border-blue-500/40 p-5 shadow-lg">
        <div className="flex items-start gap-4">
          <div className="p-2.5 rounded-lg bg-blue-500/20 text-blue-400 shrink-0 mt-0.5 border border-blue-500/30">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-slate-100">
                Operational Disclaimer & Prototype Notice
              </h2>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded">
                Synthetic Benchmark
              </span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed font-medium">
              This system uses synthetic data only and provides investigative leads to identify patterns that may deserve investigator review.
            </p>
            <p className="text-xs text-slate-400 leading-relaxed">
              All outputs are decision-support intelligence artifacts subject to mandatory human-in-the-loop review by authorized investigating officers.
            </p>
          </div>
        </div>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className={`rounded-xl bg-slate-900/90 border ${stat.borderColor} p-5 shadow-sm hover:border-slate-600 transition-colors`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {stat.title}
              </span>
              <div className={`p-2 rounded-lg ${stat.iconBg}`}>
                {stat.icon}
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold tracking-tight text-slate-100 font-mono">
                {stat.value}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">{stat.description}</p>
          </div>
        ))}
      </div>

      {/* Main Grid: Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Launchpad */}
        <div className="lg:col-span-1 rounded-xl bg-slate-900/90 border border-slate-800 p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-100 mb-1">
              Quick Actions
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Access core criminal intelligence workflows
            </p>

            <div className="space-y-3">
              <Link
                href="/cases"
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/60 border border-slate-700 hover:border-blue-500 hover:bg-slate-800 transition group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-200 group-hover:text-blue-400 transition">
                      Ingest Case Files
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Upload FIRs, CDRs, Forensics
                    </div>
                  </div>
                </div>
                <svg className="w-4 h-4 text-slate-500 group-hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </Link>

              <Link
                href="/graph"
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/60 border border-slate-700 hover:border-blue-500 hover:bg-slate-800 transition group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-200 group-hover:text-indigo-400 transition">
                      Explore Graph
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Entity links & communities
                    </div>
                  </div>
                </div>
                <svg className="w-4 h-4 text-slate-500 group-hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </Link>

              <Link
                href="/evidence"
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/60 border border-slate-700 hover:border-blue-500 hover:bg-slate-800 transition group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-200 group-hover:text-emerald-400 transition">
                      Evidence Traceability
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Document hashes & provenance
                    </div>
                  </div>
                </div>
                <svg className="w-4 h-4 text-slate-500 group-hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Backend API Status</span>
              <span className="text-emerald-400 font-mono font-medium">Ready</span>
            </div>
          </div>
        </div>

        {/* Recent Activity Section */}
        <div className="lg:col-span-2 rounded-xl bg-slate-900/90 border border-slate-800 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-semibold text-slate-100">
                  Recent Activity
                </h3>
                <p className="text-xs text-slate-400">
                  Ingestion jobs, entity resolutions, and audit records
                </p>
              </div>
              <span className="text-xs font-mono text-slate-500">Live Log</span>
            </div>

            {/* Empty state / placeholder */}
            <div className="flex flex-col items-center justify-center py-12 px-4 rounded-lg bg-slate-950/50 border border-dashed border-slate-800 text-center">
              <div className="w-12 h-12 rounded-full bg-slate-800/80 flex items-center justify-center text-slate-500 mb-3">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                  />
                </svg>
              </div>
              <p className="text-sm font-medium text-slate-300">
                No recent activity. Upload synthetic case files to begin.
              </p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Once files are uploaded, entity extraction pipelines and graph construction logs will appear here.
              </p>
              <Link
                href="/cases"
                className="mt-4 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition"
              >
                Go to Cases & Ingestion
              </Link>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
            <span>Audit Trail Enabled: SHA-256 Provenance Hashing</span>
            <span>SIH 26189 Prototype</span>
          </div>
        </div>
      </div>
    </div>
  );
}
