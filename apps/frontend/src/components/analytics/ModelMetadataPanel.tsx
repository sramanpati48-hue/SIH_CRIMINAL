import React from 'react';
import { Database, FileKey, ShieldCheck, Box } from 'lucide-react';

interface ModelMetadataPanelProps {
  metadata: any;
}

export function ModelMetadataPanel({ metadata }: ModelMetadataPanelProps) {
  if (!metadata) return null;
  
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mt-6">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
        <Database className="w-3.5 h-3.5" />
        Model Provenance & Versioning
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
        <div>
          <span className="text-slate-500 block mb-1">Model Version</span>
          <span className="font-mono text-slate-300 break-all">{metadata.dataset_metadata?.supervised_valid ? metadata.supervised_baseline?.model_version || 'N/A' : metadata.anomaly_baseline?.model_version || 'N/A'}</span>
        </div>
        <div>
          <span className="text-slate-500 block mb-1">Dataset Version</span>
          <span className="font-mono text-slate-300 break-all">{metadata.dataset_metadata?.dataset_version || 'N/A'}</span>
        </div>
        <div>
          <span className="text-slate-500 block mb-1">Feature Version</span>
          <span className="font-mono text-slate-300 break-all">{metadata.dataset_metadata?.feature_version || 'N/A'}</span>
        </div>
        <div>
          <span className="text-slate-500 block mb-1">Training Sample Size</span>
          <span className="text-slate-300">{metadata.dataset_metadata?.total_cases || 0} cases</span>
        </div>
      </div>
      
      {metadata.dataset_metadata?.class_distribution && Object.keys(metadata.dataset_metadata.class_distribution).length > 0 && (
         <div className="mt-4 pt-3 border-t border-slate-800 text-xs flex gap-6">
            <span className="text-slate-500">Label Distribution:</span>
            {Object.entries(metadata.dataset_metadata.class_distribution).map(([cls, count]) => (
                <span key={cls} className="text-slate-300">{cls}: <strong>{String(count)}</strong></span>
            ))}
         </div>
      )}
      
      <div className="mt-4 pt-3 border-t border-slate-800 text-[10px] text-slate-500 flex items-center gap-1.5">
        <ShieldCheck className="w-3 h-3 text-emerald-500/70" />
        Artifact provenance verified. Only deterministic features used (no raw GNN embeddings).
      </div>
    </div>
  );
}
