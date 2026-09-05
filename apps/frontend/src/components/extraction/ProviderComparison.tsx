import React, { useState } from 'react';
import { ProviderComparisonResult } from '../../types/api';

interface Props {
  documentId: string;
}

export const ProviderComparison: React.FC<Props> = ({ documentId }) => {
  const [comparing, setComparing] = useState(false);
  const [result, setResult] = useState<ProviderComparisonResult | null>(null);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    setComparing(true);
    setError('');
    try {
      const res = await fetch(`/api/v1/documents/${documentId}/compare-providers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(["MOCK", "SPACY_LOCAL"]),
      });
      if (!res.ok) throw new Error("Comparison failed");
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="bg-white p-4 shadow rounded-lg mb-4 border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Compare Providers (Memory Only)</h3>
        <button
          onClick={handleCompare}
          disabled={comparing}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {comparing ? 'Comparing...' : 'Run Comparison'}
        </button>
      </div>
      
      {error && <div className="text-red-600 mb-4">{error}</div>}
      
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {result.providers.map(p => (
            <div key={p.provider} className="border border-gray-200 rounded p-4">
              <h4 className="font-bold text-gray-800 flex justify-between">
                {p.provider}
                <span className={`text-xs px-2 py-0.5 rounded ${p.provider_status === 'AVAILABLE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {p.provider_status}
                </span>
              </h4>
              <p className="text-xs text-gray-500 mb-3">Model: {p.model_version} | Extr: {p.extraction_version}</p>
              
              {p.warnings && p.warnings.map((w: string, i: number) => (
                <div key={i} className="text-xs text-red-600 bg-red-50 p-2 rounded mb-2">{w}</div>
              ))}
              
              {p.entity_metrics && (
                <div className="mb-2">
                  <h5 className="font-semibold text-sm text-gray-700">Entity Metrics (vs Synthetic)</h5>
                  <div className="grid grid-cols-3 gap-2 text-xs mt-1">
                    <div className="bg-gray-50 p-1 text-center">F1: {p.entity_metrics.f1.toFixed(3)}</div>
                    <div className="bg-gray-50 p-1 text-center">P: {p.entity_metrics.precision.toFixed(3)}</div>
                    <div className="bg-gray-50 p-1 text-center">R: {p.entity_metrics.recall.toFixed(3)}</div>
                  </div>
                </div>
              )}
              
              {p.confidence_distribution && (
                <div>
                  <h5 className="font-semibold text-sm text-gray-700 mt-3">Confidence Distribution</h5>
                  <div className="flex space-x-2 text-xs mt-1">
                    <span className="text-red-600">Low: {p.confidence_distribution.LOW}</span>
                    <span className="text-yellow-600">Med: {p.confidence_distribution.MEDIUM}</span>
                    <span className="text-green-600">High: {p.confidence_distribution.HIGH}</span>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 italic">Confidence means provider confidence, not factual correctness.</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
