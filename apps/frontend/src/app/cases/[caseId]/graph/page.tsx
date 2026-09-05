'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { CaseResponse, GraphResponse } from '@/types/api';
import { NetworkGraph } from '@/components/graph/NetworkGraph';

export default function GraphPage() {
  const { caseId } = useParams() as { caseId: string };
  const [caseData, setCaseData] = useState<CaseResponse | null>(null);
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string, graphUnavailable: boolean } | null>(null);
  const [depth, setDepth] = useState(500); // UI max bound for limit

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        setError(null);
        const caseRes = await api.getCase(caseId);
        setCaseData(caseRes);
        
        const graphRes = await api.getCaseGraph(caseId, depth);
        setGraphData(graphRes);
      } catch (err: unknown) {
        const errorObj = err as { message?: string; graphUnavailable?: boolean };
        setError({
          message: errorObj.message || 'An error occurred loading the graph.',
          graphUnavailable: errorObj.graphUnavailable || false
        });
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [caseId, depth]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh]">
        <div className="animate-spin w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full mb-4"></div>
        <p className="text-slate-400 font-medium">Constructing knowledge graph...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
            <Link href="/cases" className="hover:text-slate-200">Cases</Link>
            <span>/</span>
            <Link href={`/cases/${caseId}`} className="hover:text-slate-200">{caseData?.case_number || caseId}</Link>
            <span>/</span>
            <span className="text-slate-200">Graph</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-3">
            {caseData?.title || 'Case Graph'}
            {api.isMockEnabled() && (
              <span className="text-[10px] font-bold uppercase tracking-wider bg-purple-500/20 text-purple-400 border border-purple-500/40 px-2 py-0.5 rounded">
                Mock Mode
              </span>
            )}
          </h2>
        </div>

        {graphData && (
          <div className="flex items-center gap-4 bg-slate-900 border border-slate-700 px-4 py-2 rounded-lg text-sm">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="text-slate-300">Neo4j Online</span>
            </div>
            <div className="w-px h-4 bg-slate-700"></div>
            <div className="text-slate-400">
              <span className="text-slate-200 font-mono font-medium">{graphData.nodes.length}</span> nodes
            </div>
            <div className="w-px h-4 bg-slate-700"></div>
            <div className="text-slate-400">
              <span className="text-slate-200 font-mono font-medium">{graphData.edges.length}</span> edges
            </div>
            <div className="w-px h-4 bg-slate-700"></div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Depth Limit:</span>
              <select 
                value={depth} 
                onChange={(e) => setDepth(Number(e.target.value))}
                className="bg-slate-800 border border-slate-600 text-slate-200 text-xs rounded px-2 py-1 outline-none focus:border-indigo-500"
              >
                <option value={100}>100 (Safe)</option>
                <option value={500}>500 (Standard)</option>
                <option value={1000}>1000 (Dense)</option>
                <option value={2000}>2000 (Max limit)</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {error ? (
        <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/50 p-8 text-center">
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 ${error.graphUnavailable ? 'bg-amber-500/10 text-amber-500 border border-amber-500/30' : 'bg-red-500/10 text-red-500 border border-red-500/30'}`}>
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className={`text-lg font-semibold mb-2 ${error.graphUnavailable ? 'text-amber-400' : 'text-red-400'}`}>
            {error.graphUnavailable ? 'Graph Synchronization Offline' : 'Failed to Load Graph'}
          </h3>
          <p className="text-slate-400 max-w-md mb-6">{error.message}</p>
          <button 
            onClick={() => setDepth(depth)} // re-trigger effect
            className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-lg transition border border-slate-700"
          >
            Retry Connection
          </button>
        </div>
      ) : graphData?.nodes.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/50 p-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 text-indigo-500 border border-indigo-500/30 flex items-center justify-center mb-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <h3 className="text-lg font-semibold text-slate-200 mb-2">No Graph Data Available</h3>
          <p className="text-slate-400 max-w-md">No graph relationships are currently available for this case. Check ingestion and synchronization status on the case overview page.</p>
        </div>
      ) : graphData ? (
        <div className="flex-1 min-h-0 relative">
          <NetworkGraph data={graphData} />
          
          {/* Legend */}
          <div className="absolute bottom-4 right-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 p-3 rounded-lg shadow-lg">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Legend</h4>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2">
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-blue-500"></span> Person</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-purple-500"></span> Phone</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Vehicle</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-green-500"></span> Location</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-yellow-500"></span> Organization</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-red-500"></span> Bank Account</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-slate-500"></span> Case</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><span className="w-3 h-3 rounded-full bg-cyan-500"></span> Document</div>
            </div>
            <div className="mt-3 pt-2 border-t border-slate-700 flex flex-col gap-2">
              <div className="flex items-center gap-2 text-xs text-slate-400"><div className="w-4 h-0.5 bg-emerald-500"></div> Verified Edge</div>
              <div className="flex items-center gap-2 text-xs text-slate-400"><div className="w-4 h-0.5 border-t-2 border-dashed border-amber-500"></div> Unverified Edge</div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
