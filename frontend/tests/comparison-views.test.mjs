import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, it } from "node:test";

const root = process.cwd();

function readFrontend(relativePath) {
  return readFileSync(join(root, relativePath), "utf8");
}

describe("comparison and drilldown views", () => {
  it("builds backend-compatible comparison request shapes", () => {
    const stateSource = readFrontend("lib/state/analysis-state.ts");
    const typeSource = readFrontend("types/api.ts");

    assert.match(stateSource, /buildExactComparisonRequest/);
    assert.match(stateSource, /buildExactVsSampledComparisonRequest/);
    assert.match(typeSource, /baseline: ExactComparisonArm/);
    assert.match(typeSource, /candidate: ExactComparisonArm/);
    assert.match(typeSource, /denominator_scope: string/);
    assert.doesNotMatch(typeSource, /scope\?: string \| null/);
  });

  it("renders comparison, trait drilldown, and summary tables without browser science", () => {
    const viewSource = readFrontend("components/comparisons/comparison-workspace.tsx");
    const workspaceSource = readFrontend("components/analysis-workspace.tsx");

    assert.match(viewSource, /"use client"/);
    assert.match(workspaceSource, /compareExact/);
    assert.match(workspaceSource, /compareExactVsSampled/);
    assert.match(workspaceSource, /Run analysis/);
    assert.match(viewSource, /Trait drilldown/);
    assert.match(viewSource, /Summary tables/);
    assert.match(viewSource, /<table/);
    assert.match(viewSource, /aria-live="polite"/);
    assert.match(workspaceSource, /ComparisonWorkspace/);

    assert.doesNotMatch(viewSource, /TAA|TAG|TGA|Phenylalanine|Hydrophobic/);
    assert.doesNotMatch(viewSource, /Math\.pow|random|for\s*\(\s*let generation/);
  });

  it("matches Streamlit comparison and trait drilldown presentation concepts", () => {
    const viewSource = readFrontend("components/comparisons/comparison-workspace.tsx");
    const plotlySource = readFrontend("components/charts/plotly-chart.tsx");

    for (const label of [
      "Two-codon comparison",
      "Trait drilldown",
      "Trait codon survival",
      "Summary tables",
      "Exact-vs-sampled calibration",
    ]) {
      assert.match(viewSource, new RegExp(label));
    }

    assert.match(viewSource, /ChartPanel/);
    assert.match(viewSource, /PlotlyChart/);
    assert.match(viewSource, /type: "bar"/);
    assert.match(plotlySource, /Plotly\.newPlot/);
    assert.match(viewSource, /metadata\?\.category_labels/);
    assert.doesNotMatch(viewSource, /MiniBarChart|mini-bars|\braw\b|\bdebug\b|gibberish|JSON\.stringify|Run the backend comparison|No table rows returned yet/);
  });
});
