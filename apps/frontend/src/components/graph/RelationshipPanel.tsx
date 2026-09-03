import { GraphEdge } from '@/types/api';
import Link from 'next/link';

interface RelationshipPanelProps {
  edge: GraphEdge;
  caseId: string;
  onClose: () => void;
}

export function RelationshipPanel({ edge, caseId, onClose }: RelationshipPanelProps) {
  return (
    <div className="bg-slate-900 border-l border-slate-700 w-80 h-full flex flex-col shadow-xl z-10 absolute right-0 top-0 overflow-y-auto">
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <span className="w-3 h-3 bg-slate-400 inline-block rotate-45"></span>
          Relationship Details
        </h3>
        <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-4 space-y-4 flex-1">
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Relationship Type</div>
          <div className="text-sm font-medium text-slate-200 bg-slate-800 border border-slate-600 inline-block px-2 py-1 rounded">
            {edge.relationship_type}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 bg-slate-950 p-2 rounded border border-slate-800">
          <div>
            <div className="text-xs text-slate-500 mb-1">Source Node</div>
            <div className="text-xs font-mono text-slate-300 break-all">{edge.source_id}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">Target Node</div>
            <div className="text-xs font-mono text-slate-300 break-all">{edge.target_id}</div>
          </div>
        </div>

        {edge.event_date && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Event Date</div>
            <div className="text-sm font-medium text-slate-200">
              {new Date(edge.event_date).toLocaleString()}
            </div>
          </div>
        )}

        <div>
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Status</div>
          <div className="flex items-center gap-2 mt-1">
            {edge.verified ? (
              <span className="text-xs font-semibold px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                Investigator Verified
              </span>
            ) : (
              <span className="text-xs font-semibold px-2 py-1 bg-amber-500/20 text-amber-400 rounded-full flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                Unverified Lead
              </span>
            )}
          </div>
        </div>

        {edge.confidence !== null && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Confidence Score</div>
            <div className="w-full bg-slate-800 rounded-full h-2 mb-1 mt-2">
              <div 
                className={`h-2 rounded-full ${edge.confidence > 0.8 ? 'bg-emerald-500' : edge.confidence > 0.5 ? 'bg-amber-500' : 'bg-red-500'}`} 
                style={{ width: `${Math.max(10, edge.confidence * 100)}%` }}
              ></div>
            </div>
            <div className="text-xs text-slate-400 text-right">{(edge.confidence * 100).toFixed(0)}%</div>
          </div>
        )}

        {Object.entries(edge.properties).length > 0 && (
          <div className="pt-2 border-t border-slate-800">
            <h4 className="text-xs text-slate-500 uppercase tracking-wider mb-2">Additional Properties</h4>
            {Object.entries(edge.properties).map(([key, value]) => (
              <div key={key} className="mb-2">
                <div className="text-xs text-slate-400">{key.replace(/_/g, ' ')}</div>
                <div className="text-sm text-slate-200">{String(value)}</div>
              </div>
            ))}
          </div>
        )}

        <div className="pt-4 mt-2 border-t border-slate-700">
          <Link 
            href={`/cases/${caseId}/evidence?rel=${edge.id}`}
            className="w-full block text-center py-2 px-4 rounded bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-colors"
          >
            View Source Evidence
          </Link>
          <p className="text-[10px] text-slate-500 mt-2 text-center">
            {edge.source_type ? `Source record type: ${edge.source_type}` : 'Source documentation available'}
          </p>
        </div>
      </div>
    </div>
  );
}
