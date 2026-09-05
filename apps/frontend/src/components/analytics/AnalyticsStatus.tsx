import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Server, Activity, AlertCircle } from 'lucide-react';

interface HealthStatus {
  status: string;
  engine?: string;
}

export function AnalyticsStatus() {
  const [status, setStatus] = useState<HealthStatus | null>(null);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const res = (await api.checkAnalyticsHealth()) as HealthStatus;
        setStatus(res);
      } catch {
        setStatus({ status: 'FAILED' });
      }
    }
    fetchStatus();
    // Poll every 30s
    const id = setInterval(fetchStatus, 30000);
    return () => clearInterval(id);
  }, []);

  if (!status) return <div className="text-xs text-slate-500">Checking Analytics...</div>;

  const isHealthy = status.status === 'healthy';
  const isOffline = status.status === 'GRAPH_UNAVAILABLE';

  return (
    <div className="flex items-center gap-3 text-xs">
      <div className="flex items-center gap-1.5">
        <Server className="w-3.5 h-3.5 text-slate-400" />
        <span className="text-slate-400">Analytics Engine:</span>
        <span className={`font-medium ${isHealthy ? 'text-green-400' : isOffline ? 'text-orange-400' : 'text-red-400'}`}>
          {isHealthy ? 'Online' : isOffline ? 'Graph Offline' : 'Failed'}
        </span>
      </div>
      
      {status.engine && (
        <div className="flex items-center gap-1.5 border-l border-slate-700 pl-3">
          <Activity className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400">Backend:</span>
          <span className="text-slate-300 font-medium">
            {status.engine === 'networkx_fallback' ? 'Python Fallback' : 'Neo4j GDS'}
          </span>
        </div>
      )}

      {isOffline && (
        <div className="flex items-center gap-1.5 border-l border-slate-700 pl-3 text-orange-400">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>Graph analysis unavailable</span>
        </div>
      )}
    </div>
  );
}
