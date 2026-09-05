"use client";

import React from "react";

export interface ExtractionStatusProps {
  totalCandidates: number;
  unreviewedCandidates: number;
  acceptedCandidates?: number;
  correctedCandidates?: number;
  rejectedCandidates?: number;
  isComplete: boolean;
  graphSyncStatus?: string;
  /** When true, renders a prominent warning that no authentication is active
   *  and reviews are attributed to a configured development identity. */
  devReviewerMode?: boolean;
  /** The configured dev reviewer identity, displayed in the warning banner. */
  devReviewerId?: string | null;
}

export default function ExtractionStatus({
  totalCandidates,
  unreviewedCandidates,
  acceptedCandidates = 0,
  correctedCandidates = 0,
  rejectedCandidates = 0,
  isComplete,
  graphSyncStatus,
  devReviewerMode = false,
  devReviewerId,
}: ExtractionStatusProps) {
  return (
    <div className="space-y-3">
      {/* ── Development reviewer-mode warning ── */}
      {devReviewerMode && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-amber-300"
        >
          <span className="mt-0.5 shrink-0 text-lg leading-none" aria-hidden="true">
            ⚠
          </span>
          <div className="text-xs leading-relaxed">
            <p className="font-semibold">Development Reviewer Mode — No Authentication Active</p>
            <p className="mt-0.5 text-amber-400/80">
              All review actions in this session are attributed to the configured
              development identity
              {devReviewerId ? (
                <>
                  {" "}
                  <code className="rounded bg-amber-500/20 px-1 py-0.5 font-mono text-amber-300">
                    {devReviewerId}
                  </code>
                </>
              ) : (
                " (not configured — set DEV_REVIEWER_ID)"
              )}
              . This identity is recorded in audit logs. Authentication is not
              enabled in this milestone; do not use this mode in production.
            </p>
          </div>
        </div>
      )}

      {/* ── Extraction verification status card ── */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-semibold text-slate-200">
              Extraction Verification Status
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Human-in-the-loop review tracking for AI-suggested candidate
              entities and relationships.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                isComplete
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
              }`}
            >
              {isComplete ? "Review Complete" : "Review Pending"}
            </span>
            {graphSyncStatus && (
              <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Graph: {graphSyncStatus}
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-4 text-center">
          <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
            <div className="text-lg font-bold text-slate-200">{totalCandidates}</div>
            <div className="text-[11px] text-slate-400 uppercase tracking-wider">Total</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
            <div className="text-lg font-bold text-amber-400">{unreviewedCandidates}</div>
            <div className="text-[11px] text-amber-400 uppercase tracking-wider">Unreviewed</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
            <div className="text-lg font-bold text-emerald-400">{acceptedCandidates}</div>
            <div className="text-[11px] text-emerald-400 uppercase tracking-wider">Accepted</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
            <div className="text-lg font-bold text-blue-400">{correctedCandidates}</div>
            <div className="text-[11px] text-blue-400 uppercase tracking-wider">Corrected</div>
          </div>
          <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
            <div className="text-lg font-bold text-rose-400">{rejectedCandidates}</div>
            <div className="text-[11px] text-rose-400 uppercase tracking-wider">Rejected</div>
          </div>
        </div>
      </div>
    </div>
  );
}
