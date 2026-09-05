import React, { useState } from 'react';
import { ProviderComparisonResult } from '../../types/api';

export const EvaluationMetrics: React.FC = () => {
  const [evaluating, setEvaluating] = useState(false);
  const [result, setResult] = useState<ProviderComparisonResult | null>(null);

  const runEvaluation = async () => {
    setEvaluating(true);
    try {
      const res = await fetch('/api/v1/extraction/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(["MOCK", "SPACY_LOCAL"])
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="bg-white p-4 shadow rounded-lg mb-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Synthetic Evaluation Metrics</h3>
        <button onClick={runEvaluation} disabled={evaluating} className="bg-purple-600 text-white px-4 py-2 rounded text-sm font-medium">
          {evaluating ? 'Running...' : 'Run Test Split Evaluation'}
        </button>
      </div>

      {result && (
        <div>
          <p className="text-xs text-gray-500 mb-4">Dataset: {result.dataset_version} | Docs: {result.test_document_ids.length}</p>
          {result.providers.map((p, i) => (
             <div key={i} className="mb-4 pb-4 border-b">
               <h4 className="font-bold">{p.provider} <span className="text-sm font-normal text-gray-500">({p.provider_status})</span></h4>
               {p.entity_metrics && (
                 <div className="mt-2 text-sm">
                   <strong>Entities:</strong> F1: {p.entity_metrics.f1.toFixed(3)} | Precision: {p.entity_metrics.precision.toFixed(3)} | Recall: {p.entity_metrics.recall.toFixed(3)}
                 </div>
               )}
               {p.relationship_metrics && (
                 <div className="mt-1 text-sm">
                   <strong>Relationships:</strong> F1: {p.relationship_metrics.exact_relationship_f1.toFixed(3)} | Precision: {p.relationship_metrics.exact_relationship_precision.toFixed(3)} | Recall: {p.relationship_metrics.exact_relationship_recall.toFixed(3)}
                 </div>
               )}
               {p.limitations && p.limitations.length > 0 && (
                 <div className="mt-2 p-2 bg-yellow-50 text-yellow-800 text-xs rounded">
                   {p.limitations[0]}
                 </div>
               )}
             </div>
          ))}
        </div>
      )}
    </div>
  );
};
