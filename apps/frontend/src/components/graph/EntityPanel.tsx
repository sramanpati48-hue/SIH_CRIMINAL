import { useEffect, useState } from 'react';
import { GraphNode, EntityGraphFeature } from '@/types/api';
import { api } from '@/lib/api';
import { EntityFeaturesPanel } from '../analytics/EntityFeaturesPanel';

interface EntityPanelProps {
  entity: GraphNode;
  onClose: () => void;
}

export function EntityPanel({ entity, onClose }: EntityPanelProps) {
  const [features, setFeatures] = useState<EntityGraphFeature | null>(null);

  useEffect(() => {
    if (!entity.case_id) return;
    
    // Only fetch features if graph isn't mock
    if (api.isMockEnabled()) return;

    api.getCaseFeatures(entity.case_id)
      .then(feats => {
        const feat = feats.find(f => f.entity_id === entity.id);
        if (feat) setFeatures(feat);
      })
      .catch(console.error);
  }, [entity.id, entity.case_id]);

  return (
    <div className="bg-slate-900 border-l border-slate-700 w-80 h-full flex flex-col shadow-xl z-10 absolute right-0 top-0 overflow-y-auto">
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-500 inline-block"></span>
          Entity Details
        </h3>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-4 space-y-4 flex-1">
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Entity Type</div>
          <div className="text-sm font-medium text-slate-200 bg-slate-800 inline-block px-2 py-1 rounded">
            {entity.entity_type}
          </div>
        </div>

        <div>
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Entity ID</div>
          <div className="text-sm font-mono text-slate-300 break-all">{entity.id}</div>
        </div>

        {Object.entries(entity.properties).map(([key, value]) => (
          <div key={key}>
            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">
              {key.replace(/_/g, ' ')}
            </div>
            <div className="text-sm font-medium text-slate-200">{String(value)}</div>
          </div>
        ))}

        {entity.source_document_ids && entity.source_document_ids.length > 0 && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Source Documents</div>
            <ul className="space-y-1">
              {entity.source_document_ids.map(docId => (
                <li key={docId} className="text-sm text-blue-400 hover:underline cursor-pointer">
                  {docId}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {entity.case_id && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Case Context</div>
            <div className="text-sm font-mono text-slate-300">{entity.case_id}</div>
          </div>
        )}

        {features && (
          <EntityFeaturesPanel features={features} />
        )}
      </div>
    </div>
  );
}
