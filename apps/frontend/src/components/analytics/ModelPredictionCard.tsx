import React from 'react';
import { ModelPrediction } from '@/types/api';
import { BrainCircuit, ShieldAlert, CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-react';
import { AnomalyExplanation } from './AnomalyExplanation';

interface ModelPredictionCardProps {
  anomalyPrediction: ModelPrediction | null;
  supervisedPrediction: ModelPrediction | null;
  datasetMetadata: any;
  loading: boolean;
  onRunModel: () => void;
}

export function ModelPredictionCard({ 
  anomalyPrediction, 
  supervisedPrediction, 
  datasetMetadata, 
  loading, 
  onRunModel 
}: ModelPredictionCardProps) {

  const isInsufficientData = datasetMetadata?.supervised_valid === false;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-emerald-400" />
          AI Baseline Analysis
        </h3>
        <button
          onClick={onRunModel}
          disabled={loading}
          className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
            loading 
            ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
            : 'bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30'
          }`}
        >
          {loading ? 'Analyzing...' : 'Run Baseline Models'}
        </button>
      </div>

      {!anomalyPrediction && !supervisedPrediction ? (
        <div className="flex-1 flex items-center justify-center text-center text-slate-500 text-sm">
          Run baseline models to evaluate structural anomalies and prioritize investigation.
        </div>
      ) : (
        <div className="flex-1 space-y-4 overflow-y-auto pr-1">
          {/* Anomaly Detection (Isolation Forest) */}
          {anomalyPrediction && (
            <div className={`p-4 rounded-lg border ${anomalyPrediction.prediction === 'ANOMALOUS' ? 'bg-orange-500/10 border-orange-500/30' : 'bg-slate-800 border-slate-700'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">Anomaly Detection</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  anomalyPrediction.prediction === 'ANOMALOUS' 
                  ? 'bg-orange-500/20 text-orange-400' 
                  : 'bg-slate-700 text-slate-300'
                }`}>
                  {anomalyPrediction.prediction === 'ANOMALOUS' ? 'ANOMALOUS' : 'NORMAL'}
                </span>
              </div>
              <p className="text-sm text-slate-300 mb-3">{anomalyPrediction.explanation}</p>
              
              {anomalyPrediction.top_features && Object.keys(anomalyPrediction.top_features).length > 0 && (
                <div className="mt-3 border-t border-slate-700/50 pt-3">
                  <AnomalyExplanation features={anomalyPrediction.top_features} />
                </div>
              )}
            </div>
          )}

          {/* Supervised Prediction (Random Forest) */}
          {isInsufficientData ? (
             <div className="p-4 rounded-lg border bg-slate-800/50 border-slate-700/50 text-slate-400 text-sm">
                <div className="flex items-center gap-2 mb-1 text-slate-300">
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                  <span className="font-semibold">Insufficient Data</span>
                </div>
                <p className="text-xs">{datasetMetadata.supervised_reason}</p>
                <p className="text-xs mt-1">Supervised baseline is disabled. Rely on anomalies and rules.</p>
             </div>
          ) : supervisedPrediction && (
            <div className={`p-4 rounded-lg border ${
              supervisedPrediction.prediction === 'HIGH' ? 'bg-red-500/10 border-red-500/30' : 
              supervisedPrediction.prediction === 'MEDIUM' ? 'bg-amber-500/10 border-amber-500/30' : 
              'bg-blue-500/10 border-blue-500/30'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-400">Model Suggestion</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  supervisedPrediction.prediction === 'HIGH' ? 'bg-red-500/20 text-red-400' : 
                  supervisedPrediction.prediction === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' : 
                  'bg-blue-500/20 text-blue-400'
                }`}>
                  {supervisedPrediction.prediction} PRIORITY
                </span>
              </div>
              <p className="text-sm text-slate-300 mb-3">{supervisedPrediction.explanation}</p>
              
              {supervisedPrediction.top_features && Object.keys(supervisedPrediction.top_features).length > 0 && (
                <div className="mt-3 border-t border-slate-700/50 pt-3">
                  <AnomalyExplanation features={supervisedPrediction.top_features} />
                </div>
              )}
            </div>
          )}
          
          <div className="flex items-start gap-2 text-[10px] text-amber-500/80 bg-amber-500/10 p-2 rounded mt-4">
             <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
             <div>
               <strong>Synthetic Data & Verification Warning:</strong> Models trained on synthetic data do not represent real-world accuracy. Predictions are for investigative prioritization only and require human verification. Do not interpret as claims of wrongdoing.
             </div>
          </div>
        </div>
      )}
    </div>
  );
}
