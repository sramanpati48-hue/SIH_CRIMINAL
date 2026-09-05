import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { ExtractionModel } from '../../types/api';

export const ModelRegistry: React.FC = () => {
  const [models, setModels] = useState<ExtractionModel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listModels()
      .then(setModels)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading model registry...</div>;

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm">
      <h2 className="text-xl font-bold mb-4">NER Model Registry</h2>
      {models.length === 0 ? (
        <p className="text-gray-500">No custom models registered yet.</p>
      ) : (
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="p-3">Model ID</th>
              <th className="p-3">Provider</th>
              <th className="p-3">Version</th>
              <th className="p-3">Status</th>
              <th className="p-3">Created</th>
            </tr>
          </thead>
          <tbody>
            {models.map(m => (
              <tr key={m.id} className="border-b">
                <td className="p-3 font-mono text-sm">{m.model_id}</td>
                <td className="p-3">{m.provider}</td>
                <td className="p-3">{m.model_version}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    m.status === 'READY' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {m.status}
                  </span>
                </td>
                <td className="p-3 text-sm text-gray-500">
                  {new Date(m.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
