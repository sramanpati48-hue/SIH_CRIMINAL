import React from 'react';
import { PatternAlert } from '@/types/api';
import { AlertCircle, AlertTriangle, ShieldAlert, Check, X, Edit, HelpCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface PatternAlertCardProps {
  alert: PatternAlert;
  onReviewStatusChange: (alertId: string, newStatus: string) => void;
}

const severityConfig = {
  CRITICAL: { icon: ShieldAlert, color: 'text-red-500', bg: 'bg-red-500/10' },
  HIGH: { icon: AlertCircle, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  MEDIUM: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  LOW: { icon: AlertCircle, color: 'text-blue-500', bg: 'bg-blue-500/10' },
};

export function PatternAlertCard({ alert, onReviewStatusChange }: PatternAlertCardProps) {
  const config = severityConfig[alert.severity] || severityConfig.MEDIUM;
  const Icon = config.icon;
  const [rationale, setRationale] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [reviewAction, setReviewAction] = React.useState<string | null>(null);

  const handleReview = async (action: string) => {
    if (['CORRECT', 'NEEDS_MORE_INFORMATION'].includes(action) && !rationale) {
      setReviewAction(action);
      return;
    }
    try {
      setIsSubmitting(true);
      const res = await api.reviewAlert(alert.alert_id, action, rationale);
      onReviewStatusChange(alert.alert_id, res.new_status);
      setReviewAction(null);
      setRationale('');
    } catch (e) {
      console.error(e);
      window.alert('Failed to submit review');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`p-4 rounded-lg border border-slate-700 bg-slate-800 shadow-sm flex flex-col gap-3`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-md ${config.bg}`}>
            <Icon className={`w-5 h-5 ${config.color}`} />
          </div>
          <div>
            <h4 className="font-medium text-slate-200">{alert.title}</h4>
            <div className="flex items-center gap-2 text-xs mt-1">
              <span className={`px-2 py-0.5 rounded-full font-medium ${config.bg} ${config.color}`}>
                {alert.severity} Priority
              </span>
              {alert.requires_human_verification && (
                <span className="text-slate-400">Requires human verification</span>
              )}
            </div>
          </div>
        </div>
        <span className="text-xs px-2 py-1 bg-slate-700 text-slate-300 rounded-md uppercase tracking-wider">
          {alert.status}
        </span>
      </div>

      <p className="text-sm text-slate-300 leading-relaxed border-l-2 border-slate-600 pl-3">
        {alert.explanation}
      </p>

      {alert.feature_values && Object.keys(alert.feature_values).length > 0 && (
        <div className="text-xs text-slate-400 bg-slate-900/50 p-2 rounded-md">
          <span className="font-semibold text-slate-500 mb-1 block">Feature Values:</span>
          <pre className="whitespace-pre-wrap font-mono">{JSON.stringify(alert.feature_values, null, 2)}</pre>
        </div>
      )}

      {alert.evidence_ids && alert.evidence_ids.length > 0 && (
        <div className="text-xs text-slate-400 flex items-start gap-2">
          <span className="font-semibold text-slate-500 whitespace-nowrap">Evidence IDs:</span>
          <div className="flex flex-wrap gap-1">
            {alert.evidence_ids.map(id => (
              <span key={id} className="bg-slate-700 px-1.5 py-0.5 rounded text-slate-300">{id}</span>
            ))}
          </div>
        </div>
      )}
      
      {(!alert.evidence_ids || alert.evidence_ids.length === 0) && alert.severity !== 'LOW' && (
         <div className="text-xs text-orange-400 bg-orange-400/10 p-2 rounded border border-orange-400/20">
           Warning: No specific evidence records linked. Requires manual context review.
         </div>
      )}

      {alert.status === 'OPEN' && (
        <div className="mt-2 pt-3 border-t border-slate-700">
          {!reviewAction ? (
            <div className="flex flex-wrap gap-2">
              <button 
                onClick={() => handleReview('ACCEPT')}
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded text-xs font-medium transition-colors"
              >
                <Check className="w-4 h-4" /> Accept Lead
              </button>
              <button 
                onClick={() => handleReview('REJECT')}
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded text-xs font-medium transition-colors"
              >
                <X className="w-4 h-4" /> Reject
              </button>
              <button 
                onClick={() => setReviewAction('CORRECT')}
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 rounded text-xs font-medium transition-colors"
              >
                <Edit className="w-4 h-4" /> Correct
              </button>
              <button 
                onClick={() => setReviewAction('NEEDS_MORE_INFORMATION')}
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-600 text-slate-300 hover:bg-slate-500 rounded text-xs font-medium transition-colors"
              >
                <HelpCircle className="w-4 h-4" /> Needs Info
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <span className="text-xs text-slate-400">Please provide a rationale for your action ({reviewAction}):</span>
              <input
                type="text"
                value={rationale}
                onChange={e => setRationale(e.target.value)}
                placeholder="Rationale (required)..."
                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-blue-500"
              />
              <div className="flex justify-end gap-2 mt-1">
                <button 
                  onClick={() => setReviewAction(null)} 
                  className="px-3 py-1 text-xs text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => handleReview(reviewAction)}
                  disabled={!rationale || isSubmitting}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50"
                >
                  Submit
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
