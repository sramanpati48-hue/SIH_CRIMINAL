import React, { useEffect, useState } from 'react';
import { ExtractionRun } from '../../types/api';

interface Props {
  documentId: string;
}

export const ExtractionRunList: React.FC<Props> = ({ documentId }) => {
  const [runs, setRuns] = useState<ExtractionRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/v1/documents/${documentId}/extraction-runs`)
      .then(r => r.json())
      .then(data => {
        setRuns(data.runs || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [documentId]);

  if (loading) return <div className="text-sm text-gray-500">Loading extraction history...</div>;
  if (!runs.length) return <div className="text-sm text-gray-500">No extraction runs recorded for this document.</div>;

  return (
    <div className="bg-white p-4 shadow rounded-lg mb-4 border border-gray-200">
      <h3 className="text-lg font-semibold mb-3 text-gray-800">Extraction History</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="text-xs text-gray-700 bg-gray-50 uppercase">
            <tr>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Provider</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Entities</th>
              <th className="px-4 py-2">Relationships</th>
            </tr>
          </thead>
          <tbody>
            {runs.map(run => (
              <tr key={run.extraction_run_id} className="border-b">
                <td className="px-4 py-2 text-gray-600">
                  {run.completed_at ? new Date(run.completed_at).toLocaleString() : 'N/A'}
                </td>
                <td className="px-4 py-2 text-gray-800 font-medium">
                  {run.provider} v{run.provider_version} (Model: {run.model_version})
                </td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    run.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                    run.status === 'PROVIDER_UNAVAILABLE' ? 'bg-yellow-100 text-yellow-800' :
                    run.status === 'FAILED' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {run.status}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-700">{run.entity_candidate_count}</td>
                <td className="px-4 py-2 text-gray-700">{run.relationship_candidate_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
