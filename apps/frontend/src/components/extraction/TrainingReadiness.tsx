import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { TrainingReadinessStatus } from '../../types/api';

export const TrainingReadiness: React.FC = () => {
  const [status, setStatus] = useState<TrainingReadinessStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getTrainingReadiness()
      .then(setStatus)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Checking training readiness...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;
  if (!status) return null;

  const renderSplit = (name: string, split: any) => (
    <div className="border p-4 rounded bg-white mt-4">
      <h3 className="font-semibold mb-2">{name}</h3>
      {!split.exists ? (
        <p className="text-red-500">Missing</p>
      ) : (
        <>
          <p>Documents: {split.document_count}</p>
          <p>Entities: {split.entity_count}</p>
          <div className="mt-2 text-sm text-gray-600">
            <strong>Label Distribution:</strong>
            <ul className="grid grid-cols-2 gap-2 mt-1">
              {split.label_distribution.map((l: any) => (
                <li key={l.label} className={!l.is_sufficient ? 'text-red-500 font-medium' : ''}>
                  {l.label}: {l.count}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );

  return (
    <div className="p-6 bg-gray-50 rounded-lg">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">NER Fine-Tuning Readiness</h2>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
          status.status === 'READY' ? 'bg-green-100 text-green-800' :
          status.status === 'READY_WITH_WARNINGS' ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {status.status.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="mt-2 text-sm text-gray-600">
        <p>Dataset Version: {status.dataset_version}</p>
        <p>Training Enabled: {status.training_enabled ? 'Yes' : 'No'}</p>
        <p className="mt-1">
          <em>Note: This system relies exclusively on synthetic data. Models trained here are for demonstration and experimental analysis only. Do not use models for claims of guilt or automatic accusations.</em>
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {renderSplit('Train Split', status.train_split)}
        {renderSplit('Validation Split', status.validation_split)}
        {renderSplit('Test Split', status.test_split)}
      </div>

      {status.warnings.length > 0 && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h3 className="text-yellow-800 font-semibold mb-2">Warnings</h3>
          <ul className="list-disc pl-5 text-sm text-yellow-700">
            {status.warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      {status.errors.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
          <h3 className="text-red-800 font-semibold mb-2">Errors (Blocks Training)</h3>
          <ul className="list-disc pl-5 text-sm text-red-700">
            {status.errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        </div>
      )}
      
      <div className="mt-4 text-sm text-gray-500">
        To initiate training, run <code>python scripts/train_spacy_ner.py</code> from the CLI. Training via UI is intentionally disabled for security and resource control.
      </div>
    </div>
  );
};
