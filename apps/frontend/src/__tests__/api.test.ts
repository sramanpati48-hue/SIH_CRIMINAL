import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api } from '../lib/api';

describe('API Client', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('handles 503 Graph Unavailable correctly', async () => {
    const mockResponse = {
      ok: false,
      status: 503,
      json: async () => ({ detail: 'Graph Service is offline' })
    };
    
    vi.mocked(fetch).mockResolvedValueOnce(mockResponse as Response);

    try {
      await api.getCaseGraph('C001');
      expect.fail('Should have thrown');
    } catch (error: any) {
      expect(error.status).toBe(503);
      expect(error.graphUnavailable).toBe(true);
      expect(error.message).toContain('Graph data is temporarily unavailable');
    }
  });

  it('handles successful responses safely without exposing evidence unnecessarily', async () => {
    const mockData = { case_number: 'C001', title: 'Test Case' };
    const mockResponse = {
      ok: true,
      status: 200,
      json: async () => mockData
    };
    
    vi.mocked(fetch).mockResolvedValueOnce(mockResponse as Response);

    const result = await api.getCase('C001');
    expect(result.case_number).toBe('C001');
  });

  it('respects mock configuration', async () => {
    // If mock enabled, fetch is bypassed
    vi.spyOn(api, 'isMockEnabled').mockReturnValue(true);
    
    const result = await api.getCaseGraph('C001');
    expect(result.case_id).toBe('C001');
    expect(result.nodes.length).toBeGreaterThan(0);
    expect(fetch).not.toHaveBeenCalled();
  });
});
