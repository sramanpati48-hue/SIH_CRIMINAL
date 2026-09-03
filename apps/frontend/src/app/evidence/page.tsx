import React from "react";

export default function EvidencePage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Evidence & Traceability</h2>
          <p className="text-sm text-slate-400 mt-1">
            End-to-end evidence provenance, document SHA-256 integrity hashes, and sentence-level source citations.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          Module in Development
        </span>
      </div>

      <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-8 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-200">
          Evidence Traceability & Provenance View Coming Soon
        </h3>
        <p className="text-sm text-slate-400 max-w-md mt-2 leading-relaxed">
          Inspect cryptographic hash verifications, exact page/paragraph offsets for every extracted entity, and chain-of-custody audit logs.
        </p>
        <div className="mt-6 flex gap-3">
          <div className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono">
            SHA-256 Integrity Verification
          </div>
          <div className="px-3 py-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-xs text-amber-400 font-mono">
            Synthetic Data Only
          </div>
        </div>
      </div>
    </div>
  );
}
