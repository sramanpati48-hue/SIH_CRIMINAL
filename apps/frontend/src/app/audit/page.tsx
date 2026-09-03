import React from "react";

export default function AuditPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Verification & Audit Logs</h2>
          <p className="text-sm text-slate-400 mt-1">
            Human-in-the-loop review queues, officer approval trails, and immutable compliance audit logs.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          Module in Development
        </span>
      </div>

      <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-8 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-200">
          Human Verification Queue & Audit Pipeline Coming Soon
        </h3>
        <p className="text-sm text-slate-400 max-w-md mt-2 leading-relaxed">
          Review system confidence scores, accept or reject suggested entity merges, and record officer sign-offs in compliance with law enforcement audit standards.
        </p>
        <div className="mt-6 flex gap-3">
          <div className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono">
            Immutable Audit Trail
          </div>
          <div className="px-3 py-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-xs text-amber-400 font-mono">
            Synthetic Data Only
          </div>
        </div>
      </div>
    </div>
  );
}
