export interface GraphNode {
  id: string;
  label: string;
  entity_type: string;
  properties: Record<string, any>;
  case_id: string | null;
  source_document_ids: string[];
}

export interface GraphEdge {
  id: string;
  source_id: string;
  target_id: string;
  relationship_type: string;
  properties: Record<string, any>;
  source_document_id: string | null;
  source_type: string | null;
  event_date: string | null; // ISO datetime string
  confidence: number | null;
  verified: boolean;
}

export interface AnalyticsRunResponse {
  analysis_run_id: string;
  case_id: string;
  status: string;
  analytics_engine: string;
  gds_available: boolean;
  node_count: number;
  edge_count: number;
  feature_count: number;
  alert_count: number;
  warnings: string[];
  started_at: string;
  completed_at: string;
}

export interface PatternAlert {
  alert_id: string;
  case_id: string;
  pattern_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  title: string;
  explanation: string;
  entities_involved?: string[];
  evidence_ids?: string[];
  feature_values?: Record<string, any>;
  requires_human_verification?: boolean;
  status: 'OPEN' | 'ACCEPTED' | 'REJECTED' | 'CORRECTED' | 'NEEDS_MORE_INFORMATION';
  created_at: string;
}

export interface EntityGraphFeature {
  entity_id: string;
  degree: number;
  pagerank_score: number;
  betweenness_score: number;
  bridge_score: number;
  transaction_chain_count: number;
}

export interface SimilarityMatch {
  current_case_id: string;
  similar_case_id: string;
  similarity_score: number;
  matched_features: Record<string, any>;
  differing_features: Record<string, any>;
  explanation: string;
  feature_version: string;
  analysis_run_id: string;
  computed_at: string;
}

export interface SimilarityResponse {
  results: SimilarityMatch[];
  provider: string;
  warning: string;
}

export interface ModelPrediction {
  id?: string;
  prediction_type: string;
  prediction: string;
  score: number | null;
  explanation: string;
  top_features: Record<string, any>;
  model_version: string;
  dataset_version: string;
  feature_version: string;
  requires_human_verification: boolean;
  created_at?: string;
}

export interface MLRunResponse {
  case_id: string;
  dataset_metadata: Record<string, any>;
  anomaly_baseline: ModelPrediction | null;
  supervised_baseline: ModelPrediction | null;
  comparison: {
    status: string;
    explanation: string;
  };
  warnings: string[];
}

export interface GraphResponse {
  case_id: string | null;
  nodes: GraphNode[];
  edges: GraphEdge[];
  generated_at: string;
  truncated: boolean;
}

export interface EntityNeighbourResponse {
  entity: GraphNode;
  neighbours: GraphNode[];
  relationships: GraphEdge[];
}

export interface RelationshipEvidenceResponse {
  relationship_id: string;
  relationship_type: string;
  source_id: string;
  target_id: string;
  source_document_id: string | null;
  source_type: string | null;
  event_date: string | null;
  confidence: number | null;
  verified: boolean;
  evidence_text: string | null;
}

export interface GraphHealthResponse {
  status: string;
  neo4j_available: boolean;
  database: string;
  checked_at: string;
  message: string | null;
}

export interface CaseResponse {
  id: string;
  case_number: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface CaseListResponse {
  total: number;
  cases: CaseResponse[];
}

export interface DocumentResponse {
  id: string;
  case_id: string;
  file_name: string;
  file_type: string;
  file_hash: string | null;
  status: string;
  uploaded_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface IngestionSummary {
  status: string;
  details: Record<string, any>;
}

export interface ApiError {
  status: number;
  code?: string;
  message: string;
  details?: any;
  graphUnavailable?: boolean;
}
