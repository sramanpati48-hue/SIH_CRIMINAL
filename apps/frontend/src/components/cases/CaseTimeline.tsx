import React from 'react';

export interface TimelineEvent {
  id: string;
  date: string;
  type: string;
  description: string;
  entities: string[];
  sourceDocument: string;
  confidence: number | null;
  verified: boolean;
}

interface CaseTimelineProps {
  events: TimelineEvent[];
}

export function CaseTimeline({ events }: CaseTimelineProps) {
  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 border border-slate-800 border-dashed rounded-lg">
        <svg className="w-12 h-12 mx-auto mb-3 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p>No timeline events available for this case.</p>
        <p className="text-xs mt-1">Note: Only events with explicitly extracted dates are shown here. Missing dates are not inferred.</p>
      </div>
    );
  }

  // Sort events chronologically
  const sortedEvents = [...events].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  return (
    <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
      {sortedEvents.map((event) => (
        <div key={event.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
          {/* Icon */}
          <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-slate-950 bg-slate-800 text-slate-400 group-[.is-active]:text-emerald-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          
          {/* Card */}
          <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-slate-700 bg-slate-900 shadow">
            <div className="flex items-center justify-between mb-2">
              <div className="text-xs font-bold text-blue-400">{new Date(event.date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</div>
              <div className="text-[10px] font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                {event.type}
              </div>
            </div>
            <div className="text-sm font-medium text-slate-200 mb-2">
              {event.description}
            </div>
            
            <div className="flex flex-wrap gap-2 mb-3">
              {event.entities.map(ent => (
                <span key={ent} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                  {ent}
                </span>
              ))}
            </div>

            <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-800">
              <div className="text-xs text-slate-500 flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                {event.sourceDocument}
              </div>
              
              <div className="flex items-center gap-2">
                {event.verified ? (
                  <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-400/10 px-1.5 py-0.5 rounded">Verified</span>
                ) : (
                  <span className="text-[10px] font-semibold text-amber-400 bg-amber-400/10 px-1.5 py-0.5 rounded">Unverified Lead</span>
                )}
                {event.confidence && (
                  <span className="text-[10px] text-slate-400">{(event.confidence * 100).toFixed(0)}%</span>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
