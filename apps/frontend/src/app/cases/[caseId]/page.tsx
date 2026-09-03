'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { CaseResponse, GraphHealthResponse, SimilarityResponse, MLRunResponse } from '@/types/api';
import { PatternAlertList } from '@/components/analytics/PatternAlertList';
import { AnalyticsStatus } from '@/components/analytics/AnalyticsStatus';
import { CaseSimilarityCard } from '@/components/analytics/CaseSimilarityCard';
import { ModelPredictionCard } from '@/components/analytics/ModelPredictionCard';
import { ModelMetadataPanel } from '@/components/analytics/ModelMetadataPanel';

export default function CaseOverviewPage() {
  const { caseId } = useParams() as { caseId: string };
  const [caseData, setCaseData] = useState<CaseResponse | null>(null);
  const [health, setHealth] = useState<GraphHealthResponse | null>(null);
  const [patterns, setPatterns] = useState<any[]>([]);
  
  const [similarity, setSimilarity] = useState<SimilarityResponse | null>(null);
  const [isComputingSimilarity, setIsComputingSimilarity] = useState(false);
  
  const [mlData, setMlData] = useState<MLRunResponse | null>(null);
  const [isRunningMl, setIsRunningMl] = useState(false);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRunningAnalytics, setIsRunningAnalytics] = useState(false);

  const handleRunAnalytics = async () => {
    try {
      setIsRunningAnalytics(true);
      await api.runAnalytics(caseId);
      const updatedPatterns = await api.getCasePatterns(caseId);
      setPatterns(updatedPatterns);
    } catch (e: any) {
      alert(`Analytics failed: ${e.message}`);
    } finally {
      setIsRunningAnalytics(false);
    }
  };

  const handleRunSimilarity = async () => {
    try {
      setIsComputingSimilarity(true);
      const result = await api.runCaseSimilarity(caseId, 5);
      setSimilarity(result);
    } catch (e: any) {
      alert(`Similarity failed: ${e.message}`);
    } finally {
      setIsComputingSimilarity(false);
    }
  };

  const handleRunMl = async () => {
    try {
      setIsRunningMl(true);
      const result = await api.runMLPredictions(caseId);
      setMlData(result);
    } catch (e: any) {
      alert(`ML run failed: ${e.message}`);
    } finally {
      setIsRunningMl(false);
    }
  };

  const handleReviewStatusChange = (alertId: string, newStatus: string) => {
    setPatterns(prev => prev.map(p => p.alert_id === alertId ? { ...p, status: newStatus } : p));
  };

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [caseRes, healthRes, patternsRes, simRes, mlRes] = await Promise.all([
          api.getCase(caseId),
          api.getGraphHealth().catch(() => null),
          api.getCasePatterns(caseId).catch(() => []),
          api.getCaseSimilarity(caseId).catch(() => null),
          api.getMLPredictions(caseId).catch(() => null)
        ]);
        setCaseData(caseRes);
        setHealth(healthRes);
        setPatterns(patternsRes || []);
        if (simRes && simRes.results?.length > 0) setSimilarity(simRes);
        
        // Fetch ML Data if it exists, for simplicity we just rely on state if already run in this session
        // A production app would reconstruct MLRunResponse from /predictions and /model-metadata
      } catch (err: any) {
        setError(err.message || 'Failed to load case data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [caseId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-lg flex items-center gap-3">
        <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        {error || 'Case not found.'}
      </div>
    );
  }

  const isGraphAvailable = health?.neo4j_available || api.isMockEnabled();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 text-sm text-slate-400 mb-2">
        <Link href="/cases" className="hover:text-slate-200">Cases</Link>
        <span>/</span>
        <span className="text-slate-200 font-mono">{caseData.case_number}</span>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">{caseData.title}</h2>
          <div className="flex gap-2 mt-2">
            <span className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-slate-300">
              ID: {caseData.id}
            </span>
            <span className={`text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider
              ${caseData.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
              {caseData.status}
            </span>
            <span className={`text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider
              ${caseData.priority === 'CRITICAL' ? 'bg-red-500/10 text-red-400' : 
                caseData.priority === 'HIGH' ? 'bg-amber-500/10 text-amber-400' : 'bg-slate-800 text-slate-400'}`}>
              {caseData.priority}
            </span>
          </div>
        </div>
      </div>

      {!isGraphAvailable && (
        <div className="bg-amber-500/10 border border-amber-500/30 text-amber-400 p-4 rounded-lg flex items-start gap-3">
          <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <div>
            <h4 className="font-semibold">Graph Synchronization Offline</h4>
            <p className="text-sm mt-1 opacity-90">Neo4j graph services are currently unreachable. You can still view PostgreSQL case metadata, but network analysis features are disabled.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Case Details</h3>
          <p className="text-sm text-slate-400 mb-6">{caseData.description || 'No description provided.'}</p>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm border-b border-slate-800 pb-2">
              <span className="text-slate-500">Created At</span>
              <span className="text-slate-200">{new Date(caseData.created_at).toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-slate-800 pb-2">
              <span className="text-slate-500">Last Updated</span>
              <span className="text-slate-200">{new Date(caseData.updated_at).toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-slate-800 pb-2">
              <span className="text-slate-500">PostgreSQL Status</span>
              <span className="text-emerald-400 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Primary Store Online</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Analysis Modules</h3>
          
          <div className="space-y-4">
            <Link 
              href={`/cases/${caseId}/graph`}
              className={`block p-4 rounded-lg border transition ${isGraphAvailable ? 'bg-indigo-500/10 border-indigo-500/30 hover:bg-indigo-500/20' : 'bg-slate-800/50 border-slate-700 opacity-50 cursor-not-allowed pointer-events-none'}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded flex items-center justify-center ${isGraphAvailable ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-700 text-slate-500'}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  </div>
                  <div>
                    <h4 className={`font-medium ${isGraphAvailable ? 'text-indigo-400' : 'text-slate-400'}`}>Interactive Network Graph</h4>
                    <p className="text-xs text-slate-500 mt-1">Explore entity relationships and communities</p>
                  </div>
                </div>
                <svg className={`w-5 h-5 ${isGraphAvailable ? 'text-indigo-500/50' : 'text-slate-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
              </div>
            </Link>

            <Link 
              href={`/cases/${caseId}/evidence`}
              className="block p-4 rounded-lg border bg-emerald-500/10 border-emerald-500/30 hover:bg-emerald-500/20 transition"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded flex items-center justify-center bg-emerald-500/20 text-emerald-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                  </div>
                  <div>
                    <h4 className="font-medium text-emerald-400">Evidence & Traceability</h4>
                    <p className="text-xs text-slate-400 mt-1">Verify relationships against source records</p>
                  </div>
                </div>
                <svg className="w-5 h-5 text-emerald-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
              </div>
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-[450px]">
          <CaseSimilarityCard 
            similarity={similarity}
            loading={isComputingSimilarity}
            onRunSimilarity={handleRunSimilarity}
          />
        </div>
        <div className="h-[450px]">
          <ModelPredictionCard 
            anomalyPrediction={mlData?.anomaly_baseline || null}
            supervisedPrediction={mlData?.supervised_baseline || null}
            datasetMetadata={mlData?.dataset_metadata}
            loading={isRunningMl}
            onRunModel={handleRunMl}
          />
        </div>
      </div>
      
      {mlData && <ModelMetadataPanel metadata={mlData} />}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              Investigative Leads & Patterns
            </h3>
            <p className="text-sm text-slate-400 mt-1">AI-detected anomalies and critical network patterns requiring human review.</p>
          </div>
          <div className="flex items-center gap-4">
            <AnalyticsStatus />
            <button
              onClick={handleRunAnalytics}
              disabled={isRunningAnalytics || !isGraphAvailable}
              className={`px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition ${
                isRunningAnalytics || !isGraphAvailable 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-500'
              }`}
            >
              {isRunningAnalytics ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  Run Analysis
                </>
              )}
            </button>
          </div>
        </div>

        {mlData?.comparison && (
          <div className="mb-6 p-4 rounded-lg bg-blue-900/20 border border-blue-500/30 text-blue-200 text-sm">
             <strong>Analysis Summary ({mlData.comparison.status}):</strong> {mlData.comparison.explanation}
          </div>
        )}

        <PatternAlertList 
          alerts={patterns} 
          onReviewStatusChange={handleReviewStatusChange} 
        />
      </div>
    </div>
  );
}
