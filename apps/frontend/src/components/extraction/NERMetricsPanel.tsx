import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { ExtractionModelMetrics } from '../../types/api';

export const NERMetricsPanel: React.FC<{ modelId: string }> = ({ modelId }) => {
  const [metrics, setMetrics] = useState<ExtractionModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getModelMetrics(modelId)
      .then(setMetrics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [modelId]);

  if (loading) return <div>Loading metrics for {modelId}...</div>;
  if (!metrics) return <div>Failed to load metrics.</div>;

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm mt-4 border border-gray-200">
      <h3 className="text-lg font-bold mb-4">Held-out Evaluation Metrics: {modelId}</h3>
      <p className="text-sm text-gray-500 mb-4">
        These metrics represent performance on the strictly held-out test split of the synthetic dataset.
      </p>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <h4 className="font-semibold text-blue-800 mb-2">Entity Metrics</h4>
          <p><strong>F1 Score:</strong> {metrics.test_metrics.entity_f1?.toFixed(4) || 'N/A'}</p>
          <p><strong>Precision:</strong> {metrics.test_metrics.entity_precision?.toFixed(4) || 'N/A'}</p>
          <p><strong>Recall:</strong> {metrics.test_metrics.entity_recall?.toFixed(4) || 'N/A'}</p>
        </div>
        
        <div className="bg-purple-50 p-4 rounded">
          <h4 className="font-semibold text-purple-800 mb-2">Relationship Metrics</h4>
          <p><strong>Exact Topology F1:</strong> {metrics.test_metrics.relationship_f1?.toFixed(4) || 'N/A'}</p>
        </div>
      </div>
      
      <div className="mt-4 p-4 bg-gray-50 border rounded text-sm text-gray-700">
        <h4 className="font-semibold mb-1">Limitations</h4>
        <p>Models are evaluated purely against synthetic generation baselines. Actual production performance requires in-context verification. No outputs from this model constitute statements of fact.</p>
      </div>
    </div>
  );
};
