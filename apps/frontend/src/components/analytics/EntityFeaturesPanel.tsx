import React from 'react';
import { EntityGraphFeature } from '@/types/api';
import { Activity, GitBranch, GitMerge, Link2 } from 'lucide-react';

interface EntityFeaturesPanelProps {
  features: EntityGraphFeature;
}

export function EntityFeaturesPanel({ features }: EntityFeaturesPanelProps) {
  if (!features) return null;

  return (
    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700 mt-4">
      <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-1.5">
        <Activity className="w-4 h-4 text-blue-400" /> 
        Analytics Metrics
      </h4>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col">
          <span className="text-xs text-slate-500 mb-0.5">Degree</span>
          <div className="flex items-center gap-1.5">
            <Link2 className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-sm text-slate-200 font-medium">{features.degree}</span>
          </div>
        </div>
        
        <div className="flex flex-col">
          <span className="text-xs text-slate-500 mb-0.5">PageRank</span>
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-orange-400" />
            <span className="text-sm text-slate-200 font-medium">
              {features.pagerank_score.toFixed(4)}
            </span>
          </div>
        </div>

        <div className="flex flex-col">
          <span className="text-xs text-slate-500 mb-0.5">Betweenness</span>
          <div className="flex items-center gap-1.5">
            <GitBranch className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-sm text-slate-200 font-medium">
              {features.betweenness_score.toFixed(4)}
            </span>
          </div>
        </div>

        <div className="flex flex-col">
          <span className="text-xs text-slate-500 mb-0.5">Bridge Score</span>
          <div className="flex items-center gap-1.5">
            <GitMerge className="w-3.5 h-3.5 text-green-400" />
            <span className="text-sm text-slate-200 font-medium">
              {features.bridge_score.toFixed(4)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
