import {
  GraphResponse,
  EntityNeighbourResponse,
  RelationshipEvidenceResponse,
  GraphHealthResponse,
  CaseResponse,
  CaseListResponse,
  ApiError,
  AnalyticsRunResponse,
  PatternAlert,
  EntityGraphFeature,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const MOCK_GRAPH_ENABLED = process.env.NEXT_PUBLIC_ENABLE_MOCK_GRAPH === 'true';

class ApiClientError extends Error {
  public status: number;
  public details?: unknown;
  public graphUnavailable?: boolean;

  constructor(error: ApiError) {
    super(error.message);
    this.name = 'ApiClientError';
    this.status = error.status;
    this.details = error.details;
    this.graphUnavailable = error.graphUnavailable;
  }
}

import { getMemoryToken } from '@/context/AuthContext';

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 15000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  const token = getMemoryToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    return response;
  } catch (error: unknown) {
    const err = error as Error;
    if (err.name === 'AbortError') {
      throw new ApiClientError({
        status: 408,
        message: 'Request timed out. Please try again.',
      });
    }
    throw new ApiClientError({
      status: 0,
      message: 'Network error. The backend may be offline.',
    });
  } finally {
    clearTimeout(id);
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = 'An API error occurred.';
    let details = undefined;
    let graphUnavailable = false;

    if (response.status === 503) {
      message = 'Graph data is temporarily unavailable. Case records remain available from PostgreSQL. Retry after Neo4j synchronization is restored.';
      graphUnavailable = true;
    }

    try {
      const errorData = await response.json();
      if (response.status !== 503) {
        message = errorData.detail || errorData.error?.message || message;
      }
      details = errorData;
    } catch {
      // Body is not JSON
    }
    
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new Event('unauthorized'));
      }
    }

    throw new ApiClientError({
      status: response.status,
      message,
      details,
      graphUnavailable,
    });
  }

  // Do not log response body directly to prevent sensitive evidence leakage
  return await response.json() as T;
}

export const api = {
  isMockEnabled: () => MOCK_GRAPH_ENABLED,

  async listCases(skip = 0, limit = 50, status?: string): Promise<CaseListResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (status) {
      params.append('status', status);
    }
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases?${params.toString()}`);
    return handleResponse<CaseListResponse>(response);
  },

  async getCase(caseId: string): Promise<CaseResponse> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}`);
    return handleResponse<CaseResponse>(response);
  },

  async getCaseGraph(caseId: string, limit = 500): Promise<GraphResponse> {
    if (this.isMockEnabled()) {
      const { getMockCaseGraph } = await import('./mockGraphData');
      return getMockCaseGraph(caseId);
    }
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/graph?limit=${limit}`);
    return handleResponse<GraphResponse>(response);
  },

  async getEntityNeighbours(entityId: string, label: string, limit = 100): Promise<EntityNeighbourResponse> {
    const params = new URLSearchParams({
      label,
      limit: limit.toString(),
    });
    const response = await fetchWithTimeout(`${API_BASE_URL}/entities/${entityId}/neighbours?${params.toString()}`);
    return handleResponse<EntityNeighbourResponse>(response);
  },

  async getRelationshipEvidence(relationshipId: string): Promise<RelationshipEvidenceResponse> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/relationships/${relationshipId}/evidence`);
    return handleResponse<RelationshipEvidenceResponse>(response);
  },

  async getGraphHealth(): Promise<GraphHealthResponse> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/graph/health`, undefined, 5000); // Shorter timeout for health check
    return handleResponse<GraphHealthResponse>(response);
  },

  async runAnalytics(caseId: string): Promise<AnalyticsRunResponse> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/analytics`, { method: 'POST' });
    return handleResponse<AnalyticsRunResponse>(response);
  },

  async getCasePatterns(caseId: string): Promise<PatternAlert[]> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/patterns`);
    return handleResponse<PatternAlert[]>(response);
  },

  async getCaseFeatures(caseId: string): Promise<EntityGraphFeature[]> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/features`);
    return handleResponse<EntityGraphFeature[]>(response);
  },

  async reviewAlert(alertId: string, action: string, rationale: string = ""): Promise<unknown> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/alerts/${alertId}/review?action=${action}&rationale=${encodeURIComponent(rationale)}`,
      { method: 'POST' }
    );
    return handleResponse<unknown>(response);
  },

  async checkAnalyticsHealth(): Promise<unknown> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/analytics/health`, undefined, 5000);
    return handleResponse<unknown>(response);
  },

  async getCaseSimilarity(caseId: string, limit: number = 5): Promise<unknown> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/similarity?limit=${limit}`);
    return handleResponse<unknown>(response);
  },

  async runCaseSimilarity(caseId: string, limit: number = 5): Promise<unknown> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/similarity?top_k=${limit}`, { method: 'POST' });
    return handleResponse<unknown>(response);
  },

  async getMLPredictions(caseId: string): Promise<unknown> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/predictions`);
    return handleResponse<unknown>(response);
  },

  async runMLPredictions(caseId: string): Promise<unknown> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/predict`, { method: 'POST' });
    return handleResponse<unknown>(response);
  },

  async getCaseIngestionSummary(caseId: string): Promise<unknown> {
    // Expected endpoint: GET /api/v1/cases/{caseId}/ingestion-summary (Assuming it exists or will be handled gracefully if 404)
    const response = await fetchWithTimeout(`${API_BASE_URL}/cases/${caseId}/ingestion-summary`);
    return handleResponse<unknown>(response);
  },

  // Training & Models
  async getTrainingReadiness() {
    const response = await fetchWithTimeout(`${API_BASE_URL}/extraction/training-readiness`);
    return handleResponse<any>(response);
  },
  async listModels() {
    const response = await fetchWithTimeout(`${API_BASE_URL}/extraction/models`);
    return handleResponse<any[]>(response);
  },
  async getModelMetrics(modelId: string) {
    const response = await fetchWithTimeout(`${API_BASE_URL}/extraction/models/${modelId}/metrics`);
    return handleResponse<any>(response);
  },

  // Auth
  async login(username: string, password: string): Promise<{ access_token: string, user: any }> {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const response = await fetchWithTimeout(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params
    });
    return handleResponse<{ access_token: string, user: any }>(response);
  }
};
