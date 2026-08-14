export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

export interface ApiSuccess<TData> {
  data: TData;
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details: JsonValue | null;
  status_code?: number;
}

export interface ApiErrorEnvelope {
  error: ApiErrorBody;
}

export interface ApiMultiErrorEnvelope {
  errors: ApiErrorBody[];
}

export type ApiEnvelope<TData> = ApiSuccess<TData> | ApiErrorEnvelope | ApiMultiErrorEnvelope;

export interface SerializedTable {
  columns: string[];
  dtypes: Record<string, string>;
  records: JsonObject[];
  index_kind: string;
  row_count: number;
  value_kind: string;
}

export interface MetadataResponse {
  valid_codons: string[];
  stop_codons: string[];
  category_labels: string[];
  probability_presets: {
    at: number;
    ag: number;
    ac: number;
  };
  supported_modes: string[];
  detailed_sampled_http: boolean;
}

export interface ExactSimulationRequest {
  n_generations: number;
  probabilities: Record<string, number>;
  start_weights?: Record<string, number>;
  scopes?: JsonObject[];
  codon_outcomes?: JsonObject[];
  convergence?: JsonObject[];
}

export interface ExactSimulationResult {
  n_generations: number;
  start_weights: Record<string, number>;
  scopes: JsonObject[];
  codon_outcomes: JsonObject[];
  convergence: JsonObject[];
}

export interface AggregatedSimulationRequest {
  n_generations: number;
  probabilities: Record<string, number>;
  seed: number;
  start_weights?: Record<string, number>;
  scopes?: JsonObject[];
  codon_outcomes?: JsonObject[];
  convergence?: JsonObject[];
}

export interface AggregatedSimulationResult {
  seed: number;
  n_generations: number;
  start_counts: Record<string, number>;
  total_start_count: number;
  generation_counts: JsonObject[];
  final_live_codon: JsonObject;
  final_live_amino_acid: JsonObject;
  final_live_by_start_codon: JsonObject;
  total_stopped: number;
  scopes: JsonObject[];
  codon_outcomes: JsonObject[];
  convergence: JsonObject[];
}

export interface ExactComparisonArm {
  label: string;
  simulation: ExactSimulationRequest;
}

export interface ExactComparisonRequest {
  baseline: ExactComparisonArm;
  candidate: ExactComparisonArm;
  metric: string;
  scope: JsonObject;
}

export interface ExactComparisonResult {
  metric: string;
  baseline_label: string;
  candidate_label: string;
  key_columns: string[];
  table: SerializedTable;
}

export interface ExactVsSampledComparisonRequest {
  exact: ExactSimulationRequest;
  sampled: AggregatedSimulationRequest;
  metric: string;
  denominator_scope: string;
  familywise_alpha?: number;
}

export interface ExactVsSampledComparisonResult {
  metric: string;
  denominator_scope: string;
  familywise_alpha: number;
  family_size: number;
  table: SerializedTable;
}

export type JobStatusValue =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancel_requested"
  | "cancelled"
  | "expired";

export interface JobAccepted {
  job: JobStatus;
  links: JobLinks;
}

export interface JobLinks {
  status: string;
  result: string;
}

export interface JobStatus {
  job_id: string;
  job_type: string;
  status: JobStatusValue;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  updated_at: string;
  progress: number;
  attempt: number;
  max_attempts: number;
  expires_at: string | null;
  cancel_supported: boolean;
  retry_supported: boolean;
}

export interface JobStatusResponse {
  job: JobStatus;
}

export interface JobResult<TData = JsonValue> {
  job: JobStatus;
  result: TData | null;
  error: ApiErrorBody | null;
}
