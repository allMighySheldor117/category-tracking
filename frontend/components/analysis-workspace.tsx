"use client";

import { useEffect, useMemo, useState } from "react";

import {
  ApiClientError,
  compareExact,
  compareExactVsSampled,
  getMetadata,
  runAggregatedSimulation,
  runExactSimulation,
} from "../lib/api/client";
import {
  DEFAULT_ANALYSIS_INPUTS,
  firstAvailableCodon,
  isMetadataEmpty,
  validateAnalysisInputs,
  buildAggregatedSimulationRequest,
  buildExactComparisonRequest,
  buildExactSimulationRequest,
  buildExactVsSampledComparisonRequest,
  type AnalysisInputs,
  type WorkspaceStatus,
} from "../lib/state/analysis-state";
import type {
  AggregatedSimulationResult,
  ExactComparisonResult,
  ExactSimulationResult,
  ExactVsSampledComparisonResult,
  MetadataResponse,
} from "../types/api";
import { ComparisonWorkspace } from "./comparisons/comparison-workspace";
import { SimulationResults } from "./results/simulation-results";

function parseNumber(value: string): number {
  return value.trim() === "" ? Number.NaN : Number(value);
}

function statusText(status: WorkspaceStatus): string {
  switch (status) {
    case "idle":
      return "Set the simulation controls, then run the analysis.";
    case "loading":
      return "Mutating codon populations through the backend.";
    case "success":
      return "Analysis complete.";
    case "empty":
      return "The backend returned no available options.";
    case "validation-blocked":
      return "Controls need attention before running analysis.";
    case "backend-error":
      return "The backend returned an expected error.";
    case "network-error":
      return "The frontend proxy could not reach the backend.";
  }
}

function presetLabel(metadata: MetadataResponse | null): string {
  if (!metadata) {
    return "Backend preset loads automatically before the first run.";
  }
  const preset = metadata.probability_presets;
  return `A→T ${preset.at}, A→G ${preset.ag}, A→C ${preset.ac}`;
}

export function AnalysisWorkspace() {
  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [status, setStatus] = useState<WorkspaceStatus>("idle");
  const [message, setMessage] = useState(statusText("idle"));
  const [inputs, setInputs] = useState<AnalysisInputs>(DEFAULT_ANALYSIS_INPUTS);
  const [validationMessages, setValidationMessages] = useState<string[]>([]);
  const [hasRun, setHasRun] = useState(false);
  const [exactResult, setExactResult] = useState<ExactSimulationResult | null>(null);
  const [aggregatedResult, setAggregatedResult] =
    useState<AggregatedSimulationResult | null>(null);
  const [exactComparison, setExactComparison] =
    useState<ExactComparisonResult | null>(null);
  const [calibration, setCalibration] =
    useState<ExactVsSampledComparisonResult | null>(null);

  async function loadMetadata(): Promise<MetadataResponse> {
    const nextMetadata = await getMetadata();
    setMetadata(nextMetadata);
    setInputs((current) => ({
      ...current,
      selectedCodon: current.selectedCodon || firstAvailableCodon(nextMetadata),
    }));
    return nextMetadata;
  }

  useEffect(() => {
    let cancelled = false;

    async function loadInitialMetadata() {
      try {
        const nextMetadata = await getMetadata();
        if (cancelled) {
          return;
        }
        setMetadata(nextMetadata);
        setInputs((current) => ({
          ...current,
          selectedCodon: current.selectedCodon || firstAvailableCodon(nextMetadata),
        }));
        setStatus(isMetadataEmpty(nextMetadata) ? "empty" : "idle");
        setMessage(
          isMetadataEmpty(nextMetadata)
            ? statusText("empty")
            : "Metadata loaded. Set controls, then run the analysis.",
        );
      } catch {
        if (!cancelled) {
          setStatus("network-error");
          setMessage("Metadata will retry when you run the analysis.");
        }
      }
    }

    void loadInitialMetadata();
    return () => {
      cancelled = true;
    };
  }, []);

  const validationSummary = useMemo(
    () => validateAnalysisInputs(inputs, metadata),
    [inputs, metadata],
  );

  async function runAnalysis() {
    setStatus("loading");
    setMessage(statusText("loading"));
    setValidationMessages([]);

    try {
      const activeMetadata = metadata ?? (await loadMetadata());
      const validation = validateAnalysisInputs(inputs, activeMetadata);
      if (validation.length > 0) {
        setValidationMessages(validation);
        setStatus("validation-blocked");
        setMessage(statusText("validation-blocked"));
        return;
      }

      const [exact, aggregated, comparison, exactVsSampled] = await Promise.all([
        runExactSimulation(buildExactSimulationRequest(inputs, activeMetadata)),
        runAggregatedSimulation(buildAggregatedSimulationRequest(inputs, activeMetadata)),
        compareExact(buildExactComparisonRequest(inputs, activeMetadata)),
        compareExactVsSampled(buildExactVsSampledComparisonRequest(inputs, activeMetadata)),
      ]);

      setExactResult(exact);
      setAggregatedResult(aggregated);
      setExactComparison(comparison);
      setCalibration(exactVsSampled);
      setHasRun(true);
      setStatus("success");
      setMessage("Analysis complete. Results are shown in the Streamlit app order.");
    } catch (error) {
      setStatus(error instanceof ApiClientError ? "backend-error" : "network-error");
      setMessage(
        error instanceof ApiClientError
          ? error.message
          : "The analysis request could not reach the backend.",
      );
    }
  }

  return (
    <div className="analysis-workspace">
      <section className="workspace__panel streamlit-sidebar" aria-labelledby="controls-title">
        <div className="panel-heading">
          <div>
            <h2 id="controls-title">Simulation</h2>
            <p>Use the same sidebar flow as the original Streamlit app.</p>
          </div>
        </div>

        <p className={`status-note status-note--${status}`} aria-live="polite">
          {message}
        </p>

        <div className="control-grid">
          <label className="field">
            <span>Generations</span>
            <input
              id="generation-count"
              name="generation-count"
              type="number"
              min="1"
              max="2000"
              step="1"
              value={inputs.generationCount}
              onChange={(event) =>
                setInputs((current) => ({
                  ...current,
                  generationCount: parseNumber(event.target.value),
                }))
              }
            />
          </label>

          <label className="field">
            <span>Copies per codon</span>
            <input
              id="copies-per-codon"
              name="copies-per-codon"
              type="number"
              min="1"
              max="1000000"
              step="1"
              value={inputs.copiesPerCodon}
              onChange={(event) =>
                setInputs((current) => ({
                  ...current,
                  copiesPerCodon: parseNumber(event.target.value),
                }))
              }
            />
          </label>

          <label className="field">
            <span>Sampling seed</span>
            <input
              id="sampled-seed"
              name="sampled-seed"
              type="number"
              min="0"
              max="999999"
              step="1"
              value={inputs.sampledSeed}
              onChange={(event) =>
                setInputs((current) => ({
                  ...current,
                  sampledSeed: parseNumber(event.target.value),
                }))
              }
            />
          </label>

          <fieldset className="fieldset">
            <legend>Your probability</legend>
            <label className="field">
              <span>A → T</span>
              <input
                id="position-one-probability"
                name="position-one-probability"
                type="number"
                min="0"
                step="any"
                value={inputs.positionOneProbability}
                onChange={(event) =>
                  setInputs((current) => ({
                    ...current,
                    positionOneProbability: parseNumber(event.target.value),
                  }))
                }
              />
            </label>
            <label className="field">
              <span>A → G</span>
              <input
                id="position-two-probability"
                name="position-two-probability"
                type="number"
                min="0"
                step="any"
                value={inputs.positionTwoProbability}
                onChange={(event) =>
                  setInputs((current) => ({
                    ...current,
                    positionTwoProbability: parseNumber(event.target.value),
                  }))
                }
              />
            </label>
            <label className="field">
              <span>A → C</span>
              <input
                id="position-three-probability"
                name="position-three-probability"
                type="number"
                min="0"
                step="any"
                value={inputs.positionThreeProbability}
                onChange={(event) =>
                  setInputs((current) => ({
                    ...current,
                    positionThreeProbability: parseNumber(event.target.value),
                  }))
                }
              />
            </label>
          </fieldset>

          <fieldset className="fieldset">
            <legend>Preset probability</legend>
            <p className="helper-text">{presetLabel(metadata)}</p>
          </fieldset>

          <label className="field">
            <span>View</span>
            <select id="view-mode" name="view-mode" defaultValue="Your probability">
              <option>Your probability</option>
              <option>Preset</option>
              <option>Compare both</option>
            </select>
          </label>

          <label className="field">
            <span>Data type</span>
            <select id="data-type" name="data-type" defaultValue="Sampled copies">
              <option>Sampled copies</option>
              <option>Exact probability</option>
            </select>
          </label>

          <label className="field">
            <span>No more change basis</span>
            <select id="no-more-basis" name="no-more-basis" defaultValue="Current computation">
              <option>Current computation</option>
              <option>Exact surviving trait fractions</option>
            </select>
          </label>

          <label className="field">
            <span>Alpha for exact surviving fractions</span>
            <input
              id="surviving-alpha"
              name="surviving-alpha"
              type="number"
              min="0"
              max="1"
              step="any"
              defaultValue="0.01"
            />
          </label>

          <label className="field">
            <span>Selected codon</span>
            <select
              id="codon-focus"
              name="codon-focus"
              value={inputs.selectedCodon}
              disabled={!metadata}
              onChange={(event) =>
                setInputs((current) => ({
                  ...current,
                  selectedCodon: event.target.value,
                }))
              }
            >
              {(metadata?.valid_codons ?? []).map((codon) => (
                <option key={codon} value={codon}>
                  {codon}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Compare with codon</span>
            <select id="compare-codon" name="compare-codon" defaultValue="TTC" disabled={!metadata}>
              {(metadata?.valid_codons ?? []).map((codon) => (
                <option key={codon} value={codon}>
                  {codon}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Codon-outcome generation</span>
            <input
              id="codon-outcome-generation"
              name="codon-outcome-generation"
              type="range"
              min="1"
              max={Math.max(1, inputs.generationCount)}
              value={Math.min(5, Math.max(1, inputs.generationCount))}
              readOnly
            />
          </label>
        </div>

        <button className="run-analysis-button" type="button" onClick={runAnalysis}>
          Run analysis
        </button>

        {validationMessages.length > 0 ? (
          <ul className="message-list" aria-label="Validation messages">
            {validationMessages.map((validationMessage) => (
              <li key={validationMessage}>{validationMessage}</li>
            ))}
          </ul>
        ) : null}
      </section>

      <section className="workspace__results streamlit-intro" aria-labelledby="workspace-title">
        <h2 id="workspace-title">Workspace</h2>
        <div className="segmented-control" aria-label="Workspace">
          <span className="segmented-control__item segmented-control__item--active">
            Codon focus
          </span>
          <span className="segmented-control__item">Whole population</span>
        </div>
        <div className="codon-chip-row" aria-label="Codon bases">
          <span className="codon-chip codon-chip--t">T</span>
          <span className="codon-chip codon-chip--a">A</span>
          <span className="codon-chip codon-chip--c">C</span>
          <span className="codon-chip codon-chip--g">G</span>
          <span className="small-note">exact codon copies → category counts → stop behavior</span>
        </div>
        {!hasRun ? (
          <p className="empty-state">
            Choose the sidebar settings and press <strong>Run analysis</strong>. The charts
            and tables will appear below in the same order as the original web app.
          </p>
        ) : null}
      </section>

      {hasRun ? (
        <>
          <SimulationResults
            exactResult={exactResult}
            aggregatedResult={aggregatedResult}
            status={status}
            message={message}
          />
          <ComparisonWorkspace
            exactComparison={exactComparison}
            calibration={calibration}
            metadata={metadata}
            message={message}
          />
        </>
      ) : null}

      <section className="workspace__results workspace__results--flat" aria-labelledby="metadata-title">
        <h2 id="metadata-title">Backend property labels</h2>
        <ul className="pill-list">
          {(metadata?.category_labels ?? []).map((label) => (
            <li key={label}>{label}</li>
          ))}
        </ul>
        {validationSummary.length > 0 && !hasRun ? (
          <p className="helper-text">The run button will validate the controls before requests start.</p>
        ) : null}
      </section>
    </div>
  );
}
