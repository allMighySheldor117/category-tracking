"use client";

import type { ReactNode } from "react";

import { PlotlyChart } from "../charts/plotly-chart";
import type {
  AggregatedSimulationResult,
  ExactSimulationResult,
  JsonObject,
  JsonValue,
  SerializedTable,
} from "../../types/api";

interface SimulationResultsProps {
  exactResult: ExactSimulationResult | null;
  aggregatedResult: AggregatedSimulationResult | null;
  status: string;
  message: string;
}

const panelBackground = "#FFFFFF";
const ink = "#1F2937";
const accent = "#FF4B4B";
const stopColor = "#64748B";
const presetColor = "#7C3AED";
const discretePalette = ["#2563EB", "#14B8A6", "#F97316", "#DC2626", "#7C3AED", "#64748B"];

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

function asSerializedTable(value: unknown): SerializedTable | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const table = value as Partial<SerializedTable>;
  if (!Array.isArray(table.columns) || !Array.isArray(table.records)) {
    return null;
  }
  return table as SerializedTable;
}

function scopeTable(
  result: ExactSimulationResult | AggregatedSimulationResult | null,
  tableName: string,
): SerializedTable | null {
  const scope = result?.scopes[0] as JsonObject | undefined;
  return asSerializedTable(scope?.[tableName]);
}

function firstTable(items: JsonObject[] | undefined): SerializedTable | null {
  const item = items?.[0] as JsonObject | undefined;
  return asSerializedTable(item?.table);
}

function numericValue(record: JsonObject, preferredColumns: string[]): number {
  const column =
    preferredColumns.find((candidate) => typeof record[candidate] === "number") ??
    Object.keys(record).find((candidate) => typeof record[candidate] === "number") ??
    "";
  return Number(record[column] ?? 0);
}

function baseLayout(
  title: string,
  height: number,
  yAxisTitle: string,
): Record<string, unknown> {
  return {
    title: { text: title, font: { size: 16, color: ink }, x: 0.02, xanchor: "left" },
    height,
    margin: { l: 58, r: 24, t: 70, b: 115 },
    paper_bgcolor: panelBackground,
    plot_bgcolor: panelBackground,
    font: { color: ink, size: 13 },
    legend: {
      orientation: "h",
      y: -0.26,
      x: 0,
      xanchor: "left",
      font: { size: 12, color: ink },
    },
    hovermode: "x unified",
    xaxis: { title: "Generation", gridcolor: "#F1F5F9", automargin: true },
    yaxis: { title: yAxisTitle, gridcolor: "#E5E7EB", zerolinecolor: "#CBD5E1", automargin: true, rangemode: "tozero" },
  };
}

function groupedLineTraces(
  table: SerializedTable | null,
  groupColumn: string,
  valueColumns: string[],
): Record<string, unknown>[] {
  if (!table) {
    return [];
  }
  const groups = new Map<string, JsonObject[]>();
  for (const record of table.records) {
    const group = String(record[groupColumn] ?? "value");
    groups.set(group, [...(groups.get(group) ?? []), record]);
  }
  return Array.from(groups.entries()).map(([group, records], index) => ({
    type: "scatter",
    mode: "lines+markers",
    name: group,
    x: records.map((record) => record.generation ?? record.start_key ?? record[groupColumn]),
    y: records.map((record) => numericValue(record, valueColumns)),
    line: { width: groupColumn === "codon" ? 2.5 : 3, color: discretePalette[index % discretePalette.length] },
    marker: { size: groupColumn === "codon" ? 6 : 7 },
  }));
}

function barTrace(
  table: SerializedTable | null,
  labelColumns: string[],
  valueColumns: string[],
  name: string,
): Record<string, unknown>[] {
  if (!table) {
    return [];
  }
  const labelColumn =
    labelColumns.find((candidate) => table.columns.includes(candidate)) ?? table.columns[0];
  return [
    {
      type: "bar",
      name,
      x: table.records.map((record) => String(record[labelColumn] ?? "")),
      y: table.records.map((record) => numericValue(record, valueColumns)),
      marker: { color: accent },
    },
  ];
}

function stopTraces(table: SerializedTable | null): Record<string, unknown>[] {
  if (!table) {
    return [];
  }
  return [
    {
      type: "bar",
      name: "new stops",
      x: table.records.map((record) => record.generation ?? record.stop_codon ?? ""),
      y: table.records.map((record) => numericValue(record, ["new_stops", "new_stop_weight", "new_stop_count", "value"])),
      marker: { color: stopColor },
    },
    {
      type: "scatter",
      mode: "lines+markers",
      name: "cumulative stops",
      x: table.records.map((record) => record.generation ?? record.stop_codon ?? ""),
      y: table.records.map((record) => numericValue(record, ["cumulative_stops", "cumulative_stop_weight", "cumulative_stop_count", "value"])),
      line: { color: presetColor, width: 3 },
      marker: { size: 7 },
    },
  ];
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
        {table.records.slice(0, 8).map((record, rowIndex) => (
          <tr key={rowIndex}>
            {table.columns.map((column, columnIndex) => (
              <td key={`${column}-${columnIndex}`}>{formatDisplay(record[column])}</td>
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
  chart,
  table,
}: {
  title: string;
  caption: string;
  chart: ReactNode;
  table: SerializedTable | null;
}) {
  const descriptionId = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-description`;
  return (
    <article className="chart-panel">
      <div className="chart-panel__heading">
        <h3>{title}</h3>
        <p id={descriptionId}>{caption}</p>
      </div>
      {chart}
      <ResultTable caption={`${title} table`} table={table} />
    </article>
  );
}

export function SimulationResults({
  exactResult,
  aggregatedResult,
  status,
  message,
}: SimulationResultsProps) {
  const exactCategoryMetrics = scopeTable(exactResult, "category_metrics");
  const exactFractions = scopeTable(exactResult, "survivor_fractions");
  const exactStops = scopeTable(exactResult, "stop_outcomes");
  const exactTraitSurvival = scopeTable(exactResult, "survival_by_start");
  const exactCodonOutcomes = firstTable(exactResult?.codon_outcomes as JsonObject[]);
  const exactConvergence = firstTable(exactResult?.convergence as JsonObject[]);

  const aggregatedCategoryMetrics = scopeTable(aggregatedResult, "category_metrics");
  const aggregatedFractions = scopeTable(aggregatedResult, "survivor_fractions");

  return (
    <section className="workspace__results streamlit-results" aria-labelledby="sync-results-title">
      <div className="panel-heading">
        <div>
          <h2 id="sync-results-title">All-codon population overview</h2>
          <p>Pooled view across every valid starting codon.</p>
        </div>
      </div>

      <p className={`status-note status-note--${status}`} aria-live="polite">
        {message}
      </p>

      <div className="metric-row" aria-label="Run summary">
        <article className="summary-card">
          <span>Exact probability</span>
          <strong>authoritative</strong>
        </article>
        <article className="summary-card">
          <span>Sampled copies</span>
          <strong>experimental sampled</strong>
        </article>
        <article className="summary-card">
          <span>Total sampled starts</span>
          <strong>{aggregatedResult?.total_start_count ?? "—"}</strong>
        </article>
      </div>

      <div className="chart-grid">
        <ChartPanel
          title="Category counts"
          caption="Faithful Plotly line chart port of category_chart: generation by live category value, colored by category."
          chart={
            <PlotlyChart
              describedBy="category-counts-description"
              layoutTitle="Category counts"
              data={groupedLineTraces(exactCategoryMetrics, "category", ["value", "live_weight", "live_count"])}
              layout={baseLayout("Category counts", 500, "Live category count / exact live weight")}
            />
          }
          table={exactCategoryMetrics}
        />
        <ChartPanel
          title="Surviving category fractions"
          caption="Faithful Plotly line chart port of surviving_fraction_chart: generation by category survivor fraction."
          chart={
            <PlotlyChart
              describedBy="surviving-category-fractions-description"
              layoutTitle="Surviving category fractions"
              data={groupedLineTraces(exactFractions, "category", ["value", "fraction", "survivor_fraction"])}
              layout={{
                ...baseLayout("Surviving category fractions", 460, "Fraction in trait / surviving"),
                yaxis: { title: "Fraction in trait / surviving", tickformat: ".0%", range: [0, 1], gridcolor: "#E5E7EB", zerolinecolor: "#CBD5E1", automargin: true },
              }}
            />
          }
          table={exactFractions}
        />
        <ChartPanel
          title="Stop outcomes"
          caption="Faithful Plotly bar-plus-line port of stop_chart: new stops and cumulative stops over generation."
          chart={
            <PlotlyChart
              describedBy="stop-outcomes-description"
              layoutTitle="Stop outcomes"
              data={stopTraces(exactStops)}
              layout={baseLayout("Stop outcomes", 340, "Copies / weight")}
            />
          }
          table={exactStops}
        />
        <ChartPanel
          title="Aggregated sampled overview"
          caption="Plotly line chart using the sampled category table returned by the aggregated API."
          chart={
            <PlotlyChart
              describedBy="aggregated-sampled-overview-description"
              layoutTitle="Aggregated sampled overview"
              data={groupedLineTraces(aggregatedCategoryMetrics, "category", ["value", "live_count", "live_weight"])}
              layout={baseLayout("Aggregated sampled overview", 500, "Live category count")}
            />
          }
          table={aggregatedCategoryMetrics ?? aggregatedFractions}
        />
      </div>

      <section className="workspace__results workspace__results--flat" aria-labelledby="trait-survival-title">
        <h2 id="trait-survival-title">Trait codon survival</h2>
        <p>Plotly line chart following trait_codon_survival_chart where the backend scope table is available.</p>
        <PlotlyChart
          describedBy="trait-survival-title"
          layoutTitle="Trait codon survival"
          data={groupedLineTraces(exactTraitSurvival, "start_key", ["value", "survivor_fraction", "survival"])}
          layout={baseLayout("Trait codon survival", 460, "Surviving copies / weight")}
        />
        <ResultTable caption="Trait codon survival" table={exactTraitSurvival} />
      </section>

      <section className="workspace__results workspace__results--flat" aria-labelledby="outcomes-title">
        <h2 id="outcomes-title">Selected codon outcomes at one generation</h2>
        <PlotlyChart
          describedBy="outcomes-title"
          layoutTitle="Selected codon outcomes at one generation"
          data={barTrace(exactCodonOutcomes, ["codon", "current_codon", "start_key"], ["value", "weight", "count"], "outcome value")}
          layout={{
            ...baseLayout("Selected codon outcomes at one generation", 520, "Probability / count"),
            xaxis: { title: "Codon", gridcolor: "#F1F5F9", automargin: true },
          }}
        />
        <ResultTable caption="Selected codon outcomes" table={exactCodonOutcomes} />
      </section>

      <section className="workspace__results workspace__results--flat" aria-labelledby="no-more-change-title">
        <h2 id="no-more-change-title">No more category change for all starting codons</h2>
        <PlotlyChart
          describedBy="no-more-change-title"
          layoutTitle="No more category change for all starting codons"
          data={barTrace(exactConvergence, ["start_key", "codon", "generation"], ["first_stable_generation", "generation", "value"], "first stable generation")}
          layout={{
            ...baseLayout("No more category change for all starting codons", 520, "Generation"),
            xaxis: { title: "Codon", gridcolor: "#F1F5F9", automargin: true },
          }}
        />
        <ResultTable caption="No more category change summary" table={exactConvergence} />
      </section>
    </section>
  );
}
