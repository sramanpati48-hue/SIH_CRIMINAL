import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NetworkGraph } from '../components/graph/NetworkGraph';
import { GraphResponse } from '../types/api';
import React from 'react';

// Mock cytoscape entirely for JSDom tests
vi.mock('cytoscape', () => {
  return {
    default: vi.fn(() => ({
      elements: vi.fn().mockReturnThis(),
      removeClass: vi.fn(),
      edges: vi.fn(() => []),
      nodes: vi.fn(() => []),
      on: vi.fn(),
      destroy: vi.fn(),
      fit: vi.fn(),
      zoom: vi.fn(() => 1),
    }))
  };
});

describe('NetworkGraph UI Component', () => {
  it('renders graph truncated warning when data.truncated is true', () => {
    const mockData: GraphResponse = {
      case_id: 'C001',
      nodes: [],
      edges: [],
      generated_at: '2025-01-01',
      truncated: true
    };
    
    render(<NetworkGraph data={mockData} />);
    expect(screen.getByText(/Graph Truncated/i)).toBeInTheDocument();
  });

  it('renders filter panel correctly', () => {
    const mockData: GraphResponse = {
      case_id: 'C001',
      nodes: [],
      edges: [],
      generated_at: '2025-01-01',
      truncated: false
    };
    
    render(<NetworkGraph data={mockData} />);
    expect(screen.getAllByText(/Filters/i).length).toBeGreaterThan(0);
    expect(screen.getByPlaceholderText(/Name, ID, etc.../i)).toBeInTheDocument();
  });
});
