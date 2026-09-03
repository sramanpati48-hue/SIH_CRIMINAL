'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { CaseResponse } from '@/types/api';

export default function CasesPage() {
  const [cases, setCases] = useState<CaseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  useEffect(() => {
    async function loadCases() {
      try {
        setLoading(true);
        setError(null);
        // The mock or actual listcases
        const res = await api.listCases(0, 100, statusFilter || undefined);
        setCases(res.cases);
      } catch (err: any) {
        setError(err.message || 'Failed to load cases');
      } finally {
        setLoading(false);
      }
    }
    loadCases();
  }, [statusFilter]);

  const filteredCases = cases.filter(c => {
    if (priorityFilter && c.priority !== priorityFilter) return false;
    if (search && !c.title.toLowerCase().includes(search.toLowerCase()) && !c.case_number.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Cases & Investigations</h2>
          <p className="text-sm text-slate-400 mt-1">
            Browse and manage synthetic case files and active investigations.
          </p>
        </div>
        <Link 
          href="/cases/new" 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded transition"
        >
          + New Case
        </Link>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex gap-4">
        <input 
          type="text" 
          placeholder="Search by case number or title..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 bg-slate-800 border border-slate-700 rounded px-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <select 
          value={statusFilter} 
          onChange={e => setStatusFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">ACTIVE</option>
          <option value="CLOSED">CLOSED</option>
          <option value="ARCHIVED">ARCHIVED</option>
        </select>
        <select 
          value={priorityFilter} 
          onChange={e => setPriorityFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Priorities</option>
          <option value="LOW">LOW</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="HIGH">HIGH</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-400">Loading cases...</p>
        </div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-lg flex items-center gap-3">
          <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          {error}
        </div>
      ) : filteredCases.length === 0 ? (
        <div className="text-center py-12 bg-slate-900/50 border border-slate-800 border-dashed rounded-xl">
          <p className="text-slate-400">No cases found matching your criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCases.map(c => (
            <Link key={c.id} href={`/cases/${c.id}`} className="block group">
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 hover:border-blue-500/50 transition h-full flex flex-col">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-slate-300">
                    {c.case_number}
                  </span>
                  <div className="flex gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider
                      ${c.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                      {c.status}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider
                      ${c.priority === 'CRITICAL' ? 'bg-red-500/10 text-red-400' : 
                        c.priority === 'HIGH' ? 'bg-amber-500/10 text-amber-400' : 'bg-slate-800 text-slate-400'}`}>
                      {c.priority}
                    </span>
                  </div>
                </div>
                <h3 className="text-base font-semibold text-slate-100 group-hover:text-blue-400 transition mb-2">
                  {c.title}
                </h3>
                <p className="text-sm text-slate-400 flex-1 line-clamp-2">
                  {c.description || 'No description provided.'}
                </p>
                <div className="mt-4 pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
                  <span>Created {new Date(c.created_at).toLocaleDateString()}</span>
                  <span className="flex items-center gap-1 group-hover:text-blue-400 transition">
                    View Details <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
