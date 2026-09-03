import React from 'react';

interface AnomalyExplanationProps {
  features: Record<string, any>;
}

export function AnomalyExplanation({ features }: AnomalyExplanationProps) {
  return (
    <div className="space-y-2">
      <span className="text-[10px] uppercase text-slate-500 font-semibold block">Key Factors</span>
      <div className="space-y-2">
        {Object.entries(features).map(([name, data]) => (
          <div key={name} className="bg-slate-800/80 rounded p-2 text-xs border border-slate-700/50">
            <div className="flex justify-between items-start mb-1">
              <span className="font-mono text-slate-300">{name}</span>
              <span className="text-slate-400">Value: {data.value.toFixed(2)}</span>
            </div>
            <div className="text-slate-500 text-[10px]">
              {data.direction === 'higher' || data.direction === 'lower' ? (
                <>
                  <span className={data.direction === 'higher' ? 'text-orange-400' : 'text-blue-400'}>
                    {data.direction.toUpperCase()}
                  </span>
                  {' '}than baseline ({data.baseline.toFixed(2)}) - {data.reason}
                </>
              ) : (
                <span className="text-emerald-400/80">{data.direction}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
