import React from 'react';

interface FilterState {
  search: string;
  verifiedOnly: boolean;
  minConfidence: number;
}

interface GraphFiltersProps {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  onReset: () => void;
}

export function GraphFilters({ filters, setFilters, onReset }: GraphFiltersProps) {
  return (
    <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 p-4 rounded-lg shadow-lg w-64">
      <h3 className="text-sm font-semibold text-slate-200 mb-3 uppercase tracking-wider">Filters</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Search Nodes</label>
          <input 
            type="text" 
            value={filters.search}
            onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
            placeholder="Name, ID, etc..."
            className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              checked={filters.verifiedOnly}
              onChange={(e) => setFilters(f => ({ ...f, verifiedOnly: e.target.checked }))}
              className="rounded bg-slate-800 border-slate-700 text-blue-500 focus:ring-blue-500/20"
            />
            <span className="text-sm text-slate-300">Verified Relationships Only</span>
          </label>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-slate-400">Min Confidence</label>
            <span className="text-xs text-slate-300">{(filters.minConfidence * 100).toFixed(0)}%</span>
          </div>
          <input 
            type="range" 
            min="0" max="1" step="0.05"
            value={filters.minConfidence}
            onChange={(e) => setFilters(f => ({ ...f, minConfidence: parseFloat(e.target.value) }))}
            className="w-full accent-blue-500"
          />
        </div>

        <button 
          onClick={onReset}
          className="w-full py-1.5 mt-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-sm text-slate-300 font-medium transition-colors"
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
}
