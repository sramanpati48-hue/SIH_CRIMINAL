import React, { useEffect, useState } from 'react';

interface ProviderHealth {
  name: string;
  status: string;
  provider_version: string;
  model_version: string;
  reason?: string;
}

export const ExtractionHealth: React.FC = () => {
  const [providers, setProviders] = useState<ProviderHealth[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/extraction/health')
      .then(r => r.json())
      .then(data => {
        setProviders(data.providers || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading provider health...</div>;

  return (
    <div className="bg-white p-4 shadow rounded-lg mb-4 border border-gray-200">
      <h3 className="text-lg font-semibold mb-2 text-gray-800">Extraction Providers</h3>
      <ul className="space-y-2">
        {providers.map(p => (
          <li key={p.name} className="flex flex-col text-sm">
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-700">{p.name}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${p.status === 'AVAILABLE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {p.status}
              </span>
              <span className="text-gray-500 text-xs">Provider v{p.provider_version} | Model {p.model_version}</span>
            </div>
            {p.reason && <p className="text-red-600 text-xs mt-1 ml-2">{p.reason}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
};
