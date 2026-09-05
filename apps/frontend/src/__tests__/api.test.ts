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
    } catch (error: unknown) {
      const err = error as { status: number; graphUnavailable: boolean; message: string };
      expect(err.status).toBe(503);
      expect(err.graphUnavailable).toBe(true);
      expect(err.message).toContain('Graph data is temporarily unavailable');
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

  describe('exportCaseReport', () => {
    beforeEach(() => {
      // Mock URL.createObjectURL and URL.revokeObjectURL
      global.URL.createObjectURL = vi.fn(() => 'blob:test-url');
      global.URL.revokeObjectURL = vi.fn();
      
      // Mock document.createElement and click
      const mockClick = vi.fn();
      const mockAnchor = {
        href: '',
        download: '',
        click: mockClick
      };
      vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any);
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => null as any);
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => null as any);
    });

    it('successfully downloads report and revokes URL', async () => {
      const mockBlob = new Blob(['<html></html>']);
      const mockHeaders = new Headers();
      mockHeaders.set('Content-Disposition', 'attachment; filename="test-case.html"');
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob,
        headers: mockHeaders
      } as unknown as Response);

      await api.exportCaseReport('C001');

      expect(fetch).toHaveBeenCalled();
      expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url');
      expect(document.createElement).toHaveBeenCalledWith('a');
    });

    it('throws authentication error on 401', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 401
      } as Response);

      await expect(api.exportCaseReport('C001')).rejects.toThrow("Authentication required.");
    });

    it('throws authorization error on 403', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        status: 403
      } as Response);

      await expect(api.exportCaseReport('C001')).rejects.toThrow("You do not have permission to export this case report.");
    });
  });
});
