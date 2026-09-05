"use client";

import React, { useState } from "react";

export type VerificationStatus = "UNREVIEWED" | "ACCEPTED" | "REJECTED" | "CORRECTED" | "NEEDS_MORE_INFORMATION";

export interface EntityCandidate {
  id: string;
  entity_type: string;
  original_value: string;
  normalized_value: string;
  source_text: string;
  start_offset: number;
  end_offset: number;
  confidence: number;
  verification_status: VerificationStatus;
  extraction_provider: string;
  extraction_version: string;
}

interface Props {
  candidate: EntityCandidate;
  onReview: (id: string, status: VerificationStatus, correctedValue?: string, rationale?: string) => void;
}

export default function ExtractionCandidateCard({ candidate, onReview }: Props) {
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [correctedValue, setCorrectedValue] = useState(candidate.normalized_value);
  const [rationale, setRationale] = useState("");

  const handleStatusChange = (status: VerificationStatus) => {
    if (status === "CORRECTED" && !isCorrecting) {
      setIsCorrecting(true);
      return;
    }
    
    if (status === "CORRECTED" || status === "NEEDS_MORE_INFORMATION") {
      if (!rationale.trim()) {
        alert("Rationale is required for this action.");
        return;
      }
    }
    
    onReview(candidate.id, status, status === "CORRECTED" ? correctedValue : undefined, rationale);
    setIsCorrecting(false);
  };

  const getStatusColor = (status: VerificationStatus) => {
    switch (status) {
      case "ACCEPTED": return "bg-green-900 text-green-300 border-green-700";
      case "REJECTED": return "bg-red-900 text-red-300 border-red-700";
      case "CORRECTED": return "bg-blue-900 text-blue-300 border-blue-700";
      case "UNREVIEWED": return "bg-yellow-900 text-yellow-300 border-yellow-700";
      default: return "bg-gray-800 text-gray-300 border-gray-600";
    }
  };

  return (
    <div className={`p-4 border rounded mb-4 ${getStatusColor(candidate.verification_status)}`}>
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="font-bold text-lg">{candidate.normalized_value}</span>
          <span className="ml-2 px-2 py-1 bg-black bg-opacity-30 rounded text-xs">
            {candidate.entity_type}
          </span>
        </div>
        <span className="text-sm opacity-75">Confidence: {(candidate.confidence * 100).toFixed(0)}%</span>
      </div>

      <div className="mb-4 text-sm opacity-90 italic border-l-4 border-opacity-50 border-white pl-2">
        &ldquo;...{candidate.source_text}...&rdquo;
      </div>
      
      <div className="text-xs opacity-60 mb-4 flex justify-between">
        <span>Provider: {candidate.extraction_provider} v{candidate.extraction_version}</span>
        <span>Offsets: {candidate.start_offset} - {candidate.end_offset}</span>
      </div>

      {isCorrecting && (
        <div className="mb-4 space-y-2">
          <input 
            type="text" 
            value={correctedValue} 
            onChange={(e) => setCorrectedValue(e.target.value)}
            className="w-full p-2 bg-gray-900 text-white rounded border border-gray-600"
            placeholder="Corrected Value"
          />
          <input 
            type="text" 
            value={rationale} 
            onChange={(e) => setRationale(e.target.value)}
            className="w-full p-2 bg-gray-900 text-white rounded border border-gray-600"
            placeholder="Rationale (required)"
          />
        </div>
      )}

      {candidate.verification_status === "UNREVIEWED" && (
        <div className="flex gap-2 mt-2">
          {!isCorrecting ? (
            <>
              <button onClick={() => handleStatusChange("ACCEPTED")} className="px-3 py-1 bg-green-600 hover:bg-green-500 rounded text-white text-sm">Accept</button>
              <button onClick={() => handleStatusChange("REJECTED")} className="px-3 py-1 bg-red-600 hover:bg-red-500 rounded text-white text-sm">Reject</button>
              <button onClick={() => setIsCorrecting(true)} className="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-white text-sm">Correct</button>
              <button onClick={() => { setIsCorrecting(true); setRationale(""); }} className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-white text-sm">Needs Info</button>
            </>
          ) : (
            <>
              <button onClick={() => handleStatusChange("CORRECTED")} className="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-white text-sm">Submit Correction</button>
              <button onClick={() => setIsCorrecting(false)} className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-white text-sm">Cancel</button>
            </>
          )}
        </div>
      )}
      
      {candidate.verification_status !== "UNREVIEWED" && (
        <div className="mt-2 text-sm font-bold">
          Status: {candidate.verification_status}
        </div>
      )}
    </div>
  );
}
