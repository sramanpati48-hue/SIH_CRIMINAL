'use client';

import React, { useEffect, useRef, useState, useMemo } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
import { GraphResponse, GraphNode, GraphEdge } from '@/types/api';
import { EntityPanel } from './EntityPanel';
import { RelationshipPanel } from './RelationshipPanel';
import { GraphFilters } from './GraphFilters';

// Stable Colors as requested
const NODE_COLORS: Record<string, string> = {
  PERSON: '#3b82f6', // blue
  PHONE: '#a855f7', // purple
  VEHICLE: '#f97316', // orange
  LOCATION: '#22c55e', // green
  ORGANIZATION: '#eab308', // yellow
  BANK_ACCOUNT: '#ef4444', // red
  CASE: '#64748b', // slate
  DOCUMENT: '#06b6d4', // cyan
  EVENT: '#ec4899', // pink
};

interface NetworkGraphProps {
  data: GraphResponse;
}

export function NetworkGraph({ data }: NetworkGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [filters, setFilters] = useState({
    search: '',
    verifiedOnly: false,
    minConfidence: 0.0,
  });

  const resetFilters = () => {
    setFilters({ search: '', verifiedOnly: false, minConfidence: 0.0 });
  };

  // Convert API data to Cytoscape format safely bounded
  const elements = useMemo(() => {
    const nodes = data.nodes.slice(0, 1000).map(n => ({
      data: {
        id: n.id,
        label: n.properties.name || n.properties.title || n.properties.phone_number || n.id,
        entity_type: n.entity_type,
        color: NODE_COLORS[n.entity_type] || '#94a3b8',
        original: n
      }
    }));

    const edges = data.edges.slice(0, 2000).map(e => ({
      data: {
        id: e.id,
        source: e.source_id,
        target: e.target_id,
        label: e.relationship_type,
        verified: e.verified,
        confidence: e.confidence ?? 1.0,
        original: e
      }
    }));

    return { nodes, edges };
  }, [data]);

  // Apply filters without mutating original data
  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    cy.elements().removeClass('hidden');

    // Filter edges
    if (filters.verifiedOnly || filters.minConfidence > 0) {
      cy.edges().forEach(edge => {
        const data = edge.data();
        let hide = false;
        if (filters.verifiedOnly && !data.verified) hide = true;
        if (filters.minConfidence > 0 && data.confidence < filters.minConfidence) hide = true;
        if (hide) edge.addClass('hidden');
      });
    }

    // Filter nodes by search
    if (filters.search.trim()) {
      const term = filters.search.toLowerCase();
      cy.nodes().forEach(node => {
        const data = node.data();
        if (!data.label.toLowerCase().includes(term) && !data.id.toLowerCase().includes(term)) {
          node.addClass('hidden');
        }
      });
    }

  }, [filters]);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-size': 12,
            'text-valign': 'bottom',
            'text-halign': 'center',
            'text-margin-y': 6,
            'width': 32,
            'height': 32,
            'border-width': 2,
            'border-color': '#1e293b'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': 10,
            'color': '#cbd5e1',
            'text-rotation': 'autorotate',
            'text-background-opacity': 1 as any,
            'text-background-color': '#0f172a',
            'text-background-padding': 2 as any
          }
        },
        // Edge statuses
        {
          selector: 'edge[?verified]',
          style: {
            'line-color': '#10b981', // emerald
            'target-arrow-color': '#10b981',
          }
        },
        {
          selector: 'edge[!verified]',
          style: {
            'line-style': 'dashed',
            'line-color': '#f59e0b', // amber
            'target-arrow-color': '#f59e0b',
          }
        },
        {
          selector: 'edge[confidence < 0.5]',
          style: {
            'opacity': 0.4
          }
        },
        // Selections
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#cbd5e1'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'width': 4,
            'line-color': '#cbd5e1',
            'target-arrow-color': '#cbd5e1'
          }
        },
        // Hidden
        {
          selector: '.hidden',
          style: {
            'display': 'none'
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: false,
        randomize: true,
        nodeRepulsion: () => 4000,
        idealEdgeLength: () => 100,
      }
    });

    cy.on('tap', 'node', (evt: EventObject) => {
      setSelectedEdge(null);
      setSelectedNode(evt.target.data('original'));
    });

    cy.on('tap', 'edge', (evt: EventObject) => {
      setSelectedNode(null);
      setSelectedEdge(evt.target.data('original'));
    });

    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNode(null);
        setSelectedEdge(null);
      }
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [elements]);

  return (
    <div className="relative w-full h-[600px] bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-inner">
      <GraphFilters filters={filters} setFilters={setFilters} onReset={resetFilters} />
      
      {data.truncated && (
        <div className="absolute top-4 right-4 z-10 bg-amber-500/10 border border-amber-500/50 text-amber-400 px-3 py-2 rounded shadow-lg flex items-center gap-2 text-sm max-w-sm">
          <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <div>
            <div className="font-semibold">Graph Truncated</div>
            <div className="text-xs text-amber-400/80">Showing first {elements.nodes.length} nodes to ensure browser stability.</div>
          </div>
        </div>
      )}

      {/* Toolbar */}
      <div className="absolute bottom-4 left-4 z-10 flex flex-col gap-2">
        <button onClick={() => cyRef.current?.fit()} className="w-8 h-8 flex items-center justify-center bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-600 shadow" title="Fit to screen">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" /></svg>
        </button>
        <button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.2)} className="w-8 h-8 flex items-center justify-center bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-600 shadow" title="Zoom in">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" /></svg>
        </button>
        <button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)} className="w-8 h-8 flex items-center justify-center bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-600 shadow" title="Zoom out">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" /></svg>
        </button>
      </div>

      <div ref={containerRef} className="w-full h-full" />

      {selectedNode && (
        <EntityPanel entity={selectedNode} onClose={() => setSelectedNode(null)} />
      )}
      
      {selectedEdge && (
        <RelationshipPanel edge={selectedEdge} caseId={data.case_id || ''} onClose={() => setSelectedEdge(null)} />
      )}
    </div>
  );
}
