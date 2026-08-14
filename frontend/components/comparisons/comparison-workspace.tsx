"use client";

import type { ReactNode } from "react";

import { PlotlyChart } from "../charts/plotly-chart";
import type {
  ExactComparisonResult,
  ExactVsSampledComparisonResult,
  JsonValue,
  MetadataResponse,
  SerializedTable,
} from "../../types/api";

interface ComparisonWorkspaceProps {
  exactComparison: ExactComparisonResult | null;
  calibration: ExactVsSampledComparisonResult | null;
  metadata: MetadataResponse | null;
  message: string;
}

const ink = "#1F2937";
const accent = "#FF4B4B";

function formatDisplay(value: JsonValue | unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toPrecision(5);
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .slice(0, 4)
      .map(([key, nested]) => `${key}: ${formatDisplay(nested)}`)
      .join(", ");
  }
  return String(value);
}

function numericValue(record: Record<string, JsonValue>, preferredColumns: string[]): number {
  const column =
    preferredColumns.find((candidate) => typeof record[candidate] === "number") ??
    Object.keys(record).find((candidate) => typeof record[candidate] === "number") ??
    "";
  return Number(record[column] ?? 0);
}

function comparisonBars(table: SerializedTable | null): Record<string, unknown>[] {
  if (!table) {
    return [];
  }
  const labelColumn =
    table.columns.find((column) => ["category", "metric", "start_key", "direction"].includes(column)) ??
    table.columns[0];
  return [
    {
      type: "bar",
      name: "comparison delta",
      x: table.records.map((record) => String(record[labelColumn] ?? "")),
      y: table.records.map((record) => numericValue(record, ["signed_delta", "absolute_delta", "error", "value"])),
      marker: { color: accent },
    },
  ];
}

function comparisonLayout(title: string): Record<string, unknown> {
  return {
    title: { text: title, font: { size: 16, color: ink }, x: 0.02, xanchor: "left" },
    height: 520,
    margin: { l: 58, r: 24, t: 70, b: 130 },
    paper_bgcolor: "#FFFFFF",
    plot_bgcolor: "#FFFFFF",
    font: { color: ink, size: 13 },
    hovermode: "x unified",
    xaxis: { title: "Scientific key", gridcolor: "#F1F5F9", automargin: true },
    yaxis: { title: "Directed delta / error", gridcolor: "#E5E7EB", zerolinecolor: "#CBD5E1", automargin: true },
  };
}

function ResultTable({ caption, table }: { caption: string; table: SerializedTable | null }) {
  if (!table || table.records.length === 0) {
    return null;
  }

  return (
    <table className="result-table">
      <caption>{caption}</caption>
      <thead>
        <tr>
          {table.columns.map((column, columnIndex) => (
            <th key={`${column}-${columnIndex}`} scope="col">
              {column}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {table.records.slice(0, 8).map((row, rowIndex) => (
          <tr key={rowIndex}>
            {table.columns.map((column, columnIndex) => (
              <td key={`${column}-${columnIndex}`}>{formatDisplay(row[column])}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ChartPanel({
  title,
  caption,
  children,
  table,
}: {
  title: string;
  caption: string;
  children: ReactNode;
  table: SerializedTable | null;
}) {
  const descriptionId = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-description`;
  return (
    <article className="chart-panel">
      <div className="chart-panel__heading">
        <h3>{title}</h3>
        <p id={descriptionId}>{caption}</p>
      </div>
      {children}
      <ResultTable caption={`${title} table`} table={table} />
    </article>
  );
}

export function ComparisonWorkspace({
  exactComparison,
  calibration,
  metadata,
  message,
}: ComparisonWorkspaceProps) {
  return (
    <section className="workspace__results streamlit-results" aria-labelledby="comparisons-title">
      <div className="panel-heading">
        <div>
          <h2 id="comparisons-title">Two-codon comparison</h2>
          <p>Comparison outputs are included in the same Run analysis workflow.</p>
        </div>
      </div>

      <p className="status-note" aria-live="polite">
        {message}
      </p>

      <div className="chart-grid">
        <ChartPanel
          title="Summary tables"
          caption="Plotly bar chart for directed exact deltas returned by the comparison endpoint."
          table={exactComparison?.table ?? null}
        >
          <PlotlyChart
            describedBy="summary-tables-description"
            layoutTitle="Two-codon comparison"
            data={comparisonBars(exactComparison?.table ?? null)}
            layout={comparisonLayout("Two-codon comparison")}
          />
        </ChartPanel>
        <ChartPanel
          title="Exact-vs-sampled calibration"
          caption="Plotly bar chart for sampled-estimate calibration against exact probability."
          table={calibration?.table ?? null}
        >
          <PlotlyChart
            describedBy="exact-vs-sampled-calibration-description"
            layoutTitle="Exact-vs-sampled calibration"
            data={comparisonBars(calibration?.table ?? null)}
            layout={comparisonLayout("Exact-vs-sampled calibration")}
          />
        </ChartPanel>
      </div>

      <section className="workspace__results workspace__results--flat" aria-labelledby="trait-drilldown-title">
        <h2 id="trait-drilldown-title">Trait drilldown</h2>
        <p>
          Trait options come from metadata returned by the backend. This panel
          does not calculate category membership in the browser.
        </p>
        <h3>Trait codon survival</h3>
        <ul className="pill-list">
          {(metadata?.category_labels ?? []).map((label) => (
            <li key={label}>{label}</li>
          ))}
        </ul>
      </section>
    </section>
  );
}
