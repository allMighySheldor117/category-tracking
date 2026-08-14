import type {
  AggregatedSimulationRequest,
  ExactComparisonRequest,
  ExactSimulationRequest,
  ExactVsSampledComparisonRequest,
  MetadataResponse,
} from "../../types/api";

export type WorkspaceStatus =
  | "idle"
  | "loading"
  | "success"
  | "empty"
  | "validation-blocked"
  | "backend-error"
  | "network-error";

export type AnalysisMode =
  | "exact"
  | "aggregated"
  | "job"
  | "comparison"
  | "trait-drilldown";

export interface AnalysisInputs {
  mode: AnalysisMode;
  wholePopulation: boolean;
  selectedCodon: string;
  generationCount: number;
  positionOneProbability: number;
  positionTwoProbability: number;
  positionThreeProbability: number;
  sampledSeed: number;
  copiesPerCodon: number;
  baselineLabel: string;
  candidateLabel: string;
}

export const DEFAULT_ANALYSIS_INPUTS: AnalysisInputs = {
  mode: "exact",
  wholePopulation: true,
  selectedCodon: "",
  generationCount: 20,
  positionOneProbability: 1 / 3,
  positionTwoProbability: 1 / 3,
  positionThreeProbability: 1 / 3,
  sampledSeed: 7,
  copiesPerCodon: 100,
  baselineLabel: "Baseline",
  candidateLabel: "Candidate",
};

function isNonNegativeFinite(value: number): boolean {
  return Number.isFinite(value) && value >= 0;
}

function isIntegerAtLeast(value: number, minimum: number): boolean {
  return Number.isInteger(value) && value >= minimum;
}

export function isMetadataEmpty(metadata: MetadataResponse): boolean {
  return (
    metadata.valid_codons.length === 0 ||
    metadata.category_labels.length === 0 ||
    metadata.supported_modes.length === 0
  );
}

export function firstAvailableCodon(metadata: MetadataResponse | null): string {
  return metadata?.valid_codons[0] ?? "";
}

export function validateAnalysisInputs(
  inputs: AnalysisInputs,
  metadata: MetadataResponse | null,
): string[] {
  const messages: string[] = [];

  if (!metadata) {
    messages.push("Load metadata before validating controls.");
  }

  if (!inputs.wholePopulation && inputs.selectedCodon.trim() === "") {
    messages.push("Choose a codon focus or enable whole-population analysis.");
  }

  if (!isIntegerAtLeast(inputs.generationCount, 0)) {
    messages.push("Generations must be a whole number of zero or more.");
  }

  if (!isIntegerAtLeast(inputs.sampledSeed, 0)) {
    messages.push("Sampled seed must be a non-negative integer.");
  }

  if (!isIntegerAtLeast(inputs.copiesPerCodon, 0)) {
    messages.push("Copies per codon must be a whole number of zero or more.");
  }

  for (const [label, value] of [
    ["Position 1 probability", inputs.positionOneProbability],
    ["Position 2 probability", inputs.positionTwoProbability],
    ["Position 3 probability", inputs.positionThreeProbability],
  ] as const) {
    if (!isNonNegativeFinite(value)) {
      messages.push(`${label} must be a non-negative number.`);
    }
  }

  if (inputs.mode === "comparison") {
    if (inputs.baselineLabel.trim() === "") {
      messages.push("Baseline label is required for comparison mode.");
    }
    if (inputs.candidateLabel.trim() === "") {
      messages.push("Candidate label is required for comparison mode.");
    }
  }

  return messages;
}

function probabilityPayload(inputs: AnalysisInputs): Record<string, number> {
  return {
    a_to_t: inputs.positionOneProbability,
    a_to_g: inputs.positionTwoProbability,
    a_to_c: inputs.positionThreeProbability,
  };
}

function focusedStartWeights(
  inputs: AnalysisInputs,
  metadata: MetadataResponse | null,
  weight: number,
): Record<string, number> | undefined {
  if (!metadata) {
    return undefined;
  }

  if (inputs.wholePopulation) {
    return Object.fromEntries(metadata.valid_codons.map((codon) => [codon, weight]));
  }

  if (inputs.selectedCodon.trim() === "") {
    return undefined;
  }

  return {
    [inputs.selectedCodon]: weight,
  };
}

function selectedCodonStartWeights(
  inputs: AnalysisInputs,
  metadata: MetadataResponse | null,
  weight: number,
): Record<string, number> | undefined {
  const contractExampleCodon = metadata?.valid_codons.includes("TGG") ? "TGG" : "";
  const selectedCodon = inputs.wholePopulation
    ? contractExampleCodon || firstAvailableCodon(metadata)
    : inputs.selectedCodon.trim() || firstAvailableCodon(metadata);
  if (selectedCodon === "") {
    return undefined;
  }

  return {
    [selectedCodon]: weight,
  };
}

export function buildExactSimulationRequest(
  inputs: AnalysisInputs,
  metadata?: MetadataResponse | null,
): ExactSimulationRequest {
  const request: ExactSimulationRequest = {
    n_generations: inputs.generationCount,
    probabilities: probabilityPayload(inputs),
    scopes: [{ start_scope: "population", start_key: "all" }],
  };

  const startWeights = selectedCodonStartWeights(inputs, metadata ?? null, 1);
  if (startWeights) {
    request.start_weights = startWeights;
  }

  return request;
}

export function buildAggregatedSimulationRequest(
  inputs: AnalysisInputs,
  metadata: MetadataResponse | null,
): AggregatedSimulationRequest {
  const request: AggregatedSimulationRequest = {
    n_generations: inputs.generationCount,
    probabilities: probabilityPayload(inputs),
    seed: inputs.sampledSeed,
    scopes: [{ start_scope: "population", start_key: "all" }],
  };

  const startWeights = focusedStartWeights(inputs, metadata, inputs.copiesPerCodon);
  if (startWeights) {
    request.start_weights = startWeights;
  }

  return request;
}

export function buildExactComparisonRequest(
  inputs: AnalysisInputs,
  metadata?: MetadataResponse | null,
): ExactComparisonRequest {
  const simulation = buildExactSimulationRequest(inputs, metadata);
  return {
    baseline: {
      label: inputs.baselineLabel,
      simulation,
    },
    candidate: {
      label: inputs.candidateLabel,
      simulation,
    },
    metric: "survivor_fraction",
    scope: { start_scope: "population", start_key: "all" },
  };
}

export function buildExactVsSampledComparisonRequest(
  inputs: AnalysisInputs,
  metadata: MetadataResponse | null,
): ExactVsSampledComparisonRequest {
  const contractExampleCodon = metadata?.valid_codons.includes("TGG") ? "TGG" : "";
  const selectedCodon = inputs.wholePopulation
    ? contractExampleCodon || firstAvailableCodon(metadata)
    : inputs.selectedCodon.trim() || firstAvailableCodon(metadata);
  const focusedInputs: AnalysisInputs = {
    ...inputs,
    wholePopulation: false,
    selectedCodon,
  };

  return {
    exact: buildExactSimulationRequest(focusedInputs, metadata),
    sampled: buildAggregatedSimulationRequest(focusedInputs, metadata),
    metric: "survivor_fraction",
    denominator_scope: "population_initial",
    familywise_alpha: 0.01,
  };
}
