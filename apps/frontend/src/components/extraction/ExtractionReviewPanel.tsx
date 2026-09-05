"use client";

import React, { useState, useEffect, useCallback } from "react";
import ExtractionCandidateCard, { EntityCandidate, VerificationStatus } from "./ExtractionCandidateCard";
import RelationshipCandidateCard, { RelationshipCandidate } from "./RelationshipCandidateCard";

import ExtractionStatus from "./ExtractionStatus";

interface Props {
  documentId: string;
}

export default function ExtractionReviewPanel({ documentId }: Props) {
  const [entities, setEntities] = useState<EntityCandidate[]>([]);
  const [relationships, setRelationships] = useState<RelationshipCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCandidates = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/documents/${documentId}/extraction-candidates`);
      if (!res.ok) throw new Error("Failed to fetch candidates");
      const data = await res.json();
      setEntities(data.entities || []);
      setRelationships(data.relationships || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to fetch candidates");
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  useEffect(() => {
    let active = true;
    fetch(`/api/v1/documents/${documentId}/extraction-candidates`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch candidates");
        return res.json();
      })
      .then(data => {
        if (active) {
          setEntities(data.entities || []);
          setRelationships(data.relationships || []);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to fetch candidates");
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [documentId]);

  const handleReview = async (type: "entity" | "relationship", id: string, status: VerificationStatus, correctedValue?: string, rationale?: string) => {
    try {
      const res = await fetch(`/api/v1/extraction-candidates/${type}/${id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ verification_status: status, corrected_value: correctedValue, rationale })
      });
      if (!res.ok) throw new Error("Review failed");
      
      // Update local state
      if (type === "entity") {
        setEntities(prev => prev.map(e => e.id === id ? { ...e, verification_status: status } : e));
      } else {
        setRelationships(prev => prev.map(r => r.id === id ? { ...r, verification_status: status } : r));
      }
    } catch (err: unknown) {
      alert("Error: " + (err instanceof Error ? err.message : String(err)));
    }
  };

  const handleSync = async () => {
    try {
      const res = await fetch(`/api/v1/documents/${documentId}/sync-approved`, { method: "POST" });
      if (!res.ok) throw new Error("Sync failed");
      const data = await res.json();
      alert("Sync completed: " + data.status);
    } catch (err: unknown) {
      alert("Sync Error: " + (err instanceof Error ? err.message : String(err)));
    }
  };

  const handleExtract = async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/documents/${documentId}/extract`, { method: "POST" });
      if (!res.ok) throw new Error("Extraction failed");
      await fetchCandidates();
    } catch (err: unknown) {
      alert("Extraction Error: " + (err instanceof Error ? err.message : String(err)));
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4 text-center">Loading extraction candidates...</div>;
  if (error) return <div className="p-4 text-red-400">Error: {error}</div>;

  const pendingCount = [...entities, ...relationships].filter(x => x.verification_status === "UNREVIEWED").length;

  return (
    <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-[var(--color-text-primary)]">NLP Document Extraction Review</h2>
        <div className="space-x-2">
          <button onClick={handleExtract} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-white">
            Run Extraction
          </button>
          <button 
            onClick={handleSync} 
            disabled={pendingCount > 0}
            className={`px-4 py-2 rounded text-white ${pendingCount > 0 ? "bg-gray-600 cursor-not-allowed" : "bg-green-600 hover:bg-green-500"}`}
          >
            Sync Verified to Graph
          </button>
        </div>
      </div>

      <div className="bg-yellow-900 border-l-4 border-yellow-500 p-4 mb-6">
        <p className="text-yellow-200 text-sm font-bold">Synthetic Data &amp; Verification Warning</p>
        <p className="text-yellow-100 text-sm mt-1">
          Models trained on synthetic data do not represent real-world accuracy. Predictions are for investigative prioritization only and require human verification. Do not interpret as claims of wrongdoing.
        </p>
      </div>

      <ExtractionStatus
        totalCandidates={entities.length + relationships.length}
        unreviewedCandidates={pendingCount}
        acceptedCandidates={[...entities, ...relationships].filter(x => x.verification_status === "ACCEPTED").length}
        correctedCandidates={[...entities, ...relationships].filter(x => x.verification_status === "CORRECTED").length}
        rejectedCandidates={[...entities, ...relationships].filter(x => x.verification_status === "REJECTED").length}
        isComplete={entities.length + relationships.length > 0 && pendingCount === 0}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-4 border-b border-[var(--color-border)] pb-2">Extracted Entities</h3>
          {entities.length === 0 ? <p className="text-sm opacity-60">No entities extracted.</p> : (
            entities.map(ent => (
              <ExtractionCandidateCard 
                key={ent.id} 
                candidate={ent} 
                onReview={(id, status, correctedValue, rationale) => handleReview("entity", id, status, correctedValue, rationale)} 
              />
            ))
          )}
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4 border-b border-[var(--color-border)] pb-2">Extracted Relationships</h3>
          {relationships.length === 0 ? <p className="text-sm opacity-60">No relationships extracted.</p> : (
            relationships.map(rel => (
              <RelationshipCandidateCard 
                key={rel.id} 
                candidate={rel} 
                onReview={(id, status, correctedValue, rationale) => handleReview("relationship", id, status, correctedValue, rationale)} 
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
