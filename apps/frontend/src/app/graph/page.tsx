import React from "react";

export default function NetworkGraphPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Network Graph</h2>
          <p className="text-sm text-slate-400 mt-1">
            Interactive knowledge graph visualization of synthetic criminal networks, co-offender linkages, and central nodes.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
          Module in Development
        </span>
      </div>

      <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-8 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-200">
          Interactive Graph Visualization Coming Soon
        </h3>
        <p className="text-sm text-slate-400 max-w-md mt-2 leading-relaxed">
          Interactive entity-relationship graph canvas backed by Neo4j graph queries, community detection algorithms, and link prediction confidence scores.
        </p>
        <div className="mt-6 flex gap-3">
          <div className="px-3 py-1.5 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono">
            Neo4j & Cytoscape.js Powered
          </div>
          <div className="px-3 py-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-xs text-amber-400 font-mono">
            Synthetic Data Only
          </div>
        </div>
      </div>
    </div>
  );
}
