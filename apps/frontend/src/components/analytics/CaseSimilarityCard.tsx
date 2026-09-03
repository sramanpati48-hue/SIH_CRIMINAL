import React from 'react';
import { SimilarityResponse } from '@/types/api';
import { Link2, Info } from 'lucide-react';
import Link from 'next/link';

interface CaseSimilarityCardProps {
  similarity: SimilarityResponse | null;
  loading: boolean;
  onRunSimilarity: () => void;
}

export function CaseSimilarityCard({ similarity, loading, onRunSimilarity }: CaseSimilarityCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Link2 className="w-4 h-4 text-purple-400" />
          Historical Similarity
        </h3>
        <button
          onClick={onRunSimilarity}
          disabled={loading}
          className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
            loading 
            ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
            : 'bg-purple-600/20 text-purple-400 hover:bg-purple-600/30'
          }`}
        >
          {loading ? 'Computing...' : 'Find Similar Cases'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {!similarity ? (
          <div className="text-center py-6 text-slate-500 text-sm">
            Run similarity analysis to find related historical cases based on network structure.
          </div>
        ) : similarity.results.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-sm">
            No similar historical cases found.
          </div>
        ) : (
          <div className="space-y-4">
            {similarity.results.map((match) => (
              <div key={match.similar_case_id} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <Link href={`/cases/${match.similar_case_id}`} className="font-mono text-blue-400 hover:underline">
                    {match.similar_case_id}
                  </Link>
                  <span className="text-xs font-semibold px-2 py-1 bg-purple-500/20 text-purple-400 rounded-full">
                    {(match.similarity_score * 100).toFixed(1)}% Match
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed border-l-2 border-purple-500/50 pl-2 mb-3">
                  {match.explanation}
                </p>
                {Object.keys(match.matched_features).length > 0 && (
                  <div className="mt-2">
                    <span className="text-[10px] uppercase text-slate-500 font-semibold mb-1 block">Key Shared Features</span>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(match.matched_features).map(([k, v]) => (
                        <span key={k} className="text-[10px] bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded">
                          {k}: {v}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {similarity && similarity.warning && (
        <div className="mt-4 flex items-start gap-2 text-[10px] text-amber-500/80 bg-amber-500/10 p-2 rounded">
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <span>{similarity.warning}</span>
        </div>
      )}
    </div>
  );
}
