import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, it } from "node:test";

const root = process.cwd();

function readFrontend(relativePath) {
  return readFileSync(join(root, relativePath), "utf8");
}

describe("metadata-driven analysis controls", () => {
  it("defines UI-only analysis state without scientific definitions", () => {
    const stateSource = readFrontend("lib/state/analysis-state.ts");

    for (const status of [
      "idle",
      "loading",
      "success",
      "empty",
      "validation-blocked",
      "backend-error",
      "network-error",
    ]) {
      assert.match(stateSource, new RegExp(`"${status}"`));
    }

    assert.match(stateSource, /DEFAULT_ANALYSIS_INPUTS/);
    assert.match(stateSource, /validateAnalysisInputs/);
    assert.doesNotMatch(stateSource, /TAA|TAG|TGA|Phenylalanine|Hydrophobic/);
  });

  it("renders metadata loading controls through the typed API client", () => {
    const componentSource = readFrontend("components/analysis-workspace.tsx");
    const shellSource = readFrontend("components/workspace-shell.tsx");

    assert.match(componentSource, /"use client"/);
    assert.match(componentSource, /getMetadata/);
    assert.match(componentSource, /ApiClientError/);
    assert.match(componentSource, /aria-live="polite"/);

    for (const label of [
      "View",
      "Data type",
      "No more change basis",
      "Selected codon",
      "Your probability",
      "Preset probability",
      "Generations",
      "Sampling seed",
      "Copies per codon",
      "Codon-outcome generation",
      "Run analysis",
    ]) {
      assert.match(componentSource, new RegExp(label));
    }

    assert.match(shellSource, /AnalysisWorkspace/);
  });

  it("preserves the Streamlit-like app framing and control order", () => {
    const componentSource = readFrontend("components/analysis-workspace.tsx");
    const shellSource = readFrontend("components/workspace-shell.tsx");
    const resultSource = readFrontend("components/results/simulation-results.tsx");
    const comparisonSource = readFrontend("components/comparisons/comparison-workspace.tsx");
    const combinedSource = [
      shellSource,
      componentSource,
      resultSource,
      comparisonSource,
    ].join("\n");

    assert.match(shellSource, /Codon Category Tracking Lab/);
    assert.match(shellSource, /Track exact starting codons through amino-acid property categories/);
    assert.doesNotMatch(shellSource, /Phase 6 shell|upcoming Next\.js|Step 5 configures|Results workspace/);

    const orderedLabels = [
      "Simulation",
      "Generations",
      "Copies per codon",
      "Sampling seed",
      "Your probability",
      "Preset probability",
      "Alpha for exact surviving fractions",
      "Selected codon",
      "Compare with codon",
      "Codon-outcome generation",
      "Run analysis",
      "All-codon population overview",
      "Trait codon survival",
      "Two-codon comparison",
    ];
    let cursor = -1;
    for (const label of orderedLabels) {
      const nextIndex = combinedSource.indexOf(label);
      assert.notEqual(nextIndex, -1, `${label} should appear in the Streamlit-like controls`);
      assert.ok(nextIndex > cursor, `${label} should preserve Streamlit-like order`);
      cursor = nextIndex;
    }

    assert.doesNotMatch(componentSource, /developer|debug|placeholder|Step 5|Phase 6 shell/i);
    assert.doesNotMatch(componentSource, />Load metadata<|>Validate controls<|>Run exact<|>Run aggregated<|>Run exact comparison<|>Run exact-vs-sampled comparison</);
    assert.match(componentSource, /Promise\.all/);
  });

  it("allows backend fractional probability presets without native step mismatch", () => {
    const componentSource = readFrontend("components/analysis-workspace.tsx");

    for (const inputId of [
      "position-one-probability",
      "position-two-probability",
      "position-three-probability",
    ]) {
      const controlPattern = new RegExp(
        `id="${inputId}"[\\s\\S]*?type="number"[\\s\\S]*?step="any"`,
      );
      assert.match(componentSource, controlPattern);
    }
  });
});
