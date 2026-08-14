import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, it } from "node:test";

const root = process.cwd();

function readFrontend(relativePath) {
  return readFileSync(join(root, relativePath), "utf8");
}

describe("synchronous simulation views", () => {
  it("builds backend-compatible exact and aggregated requests from UI state", () => {
    const stateSource = readFrontend("lib/state/analysis-state.ts");
    const typeSource = readFrontend("types/api.ts");

    assert.match(stateSource, /buildExactSimulationRequest/);
    assert.match(stateSource, /buildAggregatedSimulationRequest/);
    assert.match(stateSource, /probabilities:/);
    assert.match(stateSource, /a_to_t/);
    assert.match(stateSource, /a_to_g/);
    assert.match(stateSource, /a_to_c/);

    assert.match(typeSource, /probabilities: Record<string, number>/);
    assert.doesNotMatch(typeSource, /mutation_probabilities/);
  });

  it("renders exact and aggregated results only through typed API calls", () => {
    const resultSource = readFrontend("components/results/simulation-results.tsx");
    const workspaceSource = readFrontend("components/analysis-workspace.tsx");

    assert.match(resultSource, /"use client"/);
    assert.match(workspaceSource, /runExactSimulation/);
    assert.match(workspaceSource, /runAggregatedSimulation/);
    assert.match(workspaceSource, /Run analysis/);
    assert.match(resultSource, /Exact probability/);
    assert.match(resultSource, /experimental sampled/);
    assert.match(resultSource, /<table/);
    assert.match(resultSource, /aria-live="polite"/);
    assert.match(workspaceSource, /SimulationResults/);

    assert.doesNotMatch(resultSource, /TAA|TAG|TGA|Phenylalanine|Hydrophobic/);
    assert.doesNotMatch(resultSource, /Math\.pow|random|for\s*\(\s*let generation/);
  });

  it("renders Streamlit-equivalent chart and table panels instead of raw response summaries", () => {
    const resultSource = readFrontend("components/results/simulation-results.tsx");
    const plotlySource = readFrontend("components/charts/plotly-chart.tsx");
    const packageSource = readFrontend("package.json");

    for (const label of [
      "All-codon population overview",
      "Category counts",
      "Surviving category fractions",
      "Stop outcomes",
      "Trait codon survival",
      "Selected codon outcomes at one generation",
      "No more category change for all starting codons",
    ]) {
      assert.match(resultSource, new RegExp(label));
    }

    assert.match(packageSource, /plotly\.js-dist-min/);
    assert.match(plotlySource, /Plotly\.newPlot/);
    assert.match(plotlySource, /Plotly\.react/);
    assert.match(plotlySource, /plotly-chart/);
    assert.match(resultSource, /PlotlyChart/);
    assert.match(resultSource, /type: "scatter"/);
    assert.match(resultSource, /type: "bar"/);
    assert.match(resultSource, /layoutTitle="Category counts"/);
    assert.match(resultSource, /layoutTitle="Surviving category fractions"/);
    assert.match(resultSource, /layoutTitle="Stop outcomes"/);
    assert.doesNotMatch(resultSource, /MiniLineChart|MiniBarChart|mini-chart|mini-bars/);
    assert.match(resultSource, /ChartPanel/);
    assert.match(resultSource, /serialize|records|columns/);
    assert.doesNotMatch(resultSource, /JSON\.stringify\(value\)|Exact simulation response|Aggregated simulation response|Run the backend request|Run a simulation/);
  });
});
