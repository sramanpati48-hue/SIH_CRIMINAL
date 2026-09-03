import React from "react";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">System Settings</h2>
          <p className="text-sm text-slate-400 mt-1">
            Configure extraction thresholds, link prediction confidence cuts, model endpoints, and system parameters.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-700 text-slate-300 border border-slate-600">
          Module in Development
        </span>
      </div>

      <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-8 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-200">
          Configuration Panel Coming Soon
        </h3>
        <p className="text-sm text-slate-400 max-w-md mt-2 leading-relaxed">
          Manage FastAPI backend URL, Neo4j connection parameters, Ollama/vLLM inference settings, and verification threshold parameters.
        </p>
        <div className="mt-6 flex gap-3">
          <div className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono">
            Environment: Local Synthetic Sandbox
          </div>
          <div className="px-3 py-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-xs text-amber-400 font-mono">
            Synthetic Data Only
          </div>
        </div>
      </div>
    </div>
  );
}
