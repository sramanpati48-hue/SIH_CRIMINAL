import React from 'react';
import { PatternAlert } from '@/types/api';
import { PatternAlertCard } from './PatternAlertCard';
import { Filter } from 'lucide-react';

interface PatternAlertListProps {
  alerts: PatternAlert[];
  onReviewStatusChange: (alertId: string, newStatus: string) => void;
}

export function PatternAlertList({ alerts, onReviewStatusChange }: PatternAlertListProps) {
  const [filter, setFilter] = React.useState<string>('OPEN');

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'ALL') return true;
    return a.status === filter;
  });

  if (alerts.length === 0) {
    return (
      <div className="text-center p-8 bg-slate-800/50 rounded-lg border border-slate-700/50">
        <p className="text-slate-400 mb-1">No investigative leads found.</p>
        <p className="text-sm text-slate-500">Run graph analysis to detect patterns.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <Filter className="w-4 h-4 text-slate-400" />
        <select 
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-300 text-sm rounded-md px-2 py-1 outline-none focus:border-blue-500"
        >
          <option value="ALL">All Alerts</option>
          <option value="OPEN">Needs Review (Open)</option>
          <option value="ACCEPTED">Accepted</option>
          <option value="REJECTED">Rejected</option>
          <option value="CORRECTED">Corrected</option>
          <option value="NEEDS_MORE_INFORMATION">Needs Info</option>
        </select>
        <span className="text-xs text-slate-500 ml-auto">{filteredAlerts.length} total</span>
      </div>

      <div className="flex flex-col gap-4">
        {filteredAlerts.map(alert => (
          <PatternAlertCard 
            key={alert.alert_id} 
            alert={alert} 
            onReviewStatusChange={onReviewStatusChange} 
          />
        ))}
        {filteredAlerts.length === 0 && (
          <p className="text-slate-400 text-center py-4 text-sm">No alerts match the selected filter.</p>
        )}
      </div>
    </div>
  );
}
