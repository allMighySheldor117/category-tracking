"use client";

import { useEffect, useRef } from "react";

interface PlotlyChartProps {
  data: Record<string, unknown>[];
  layout: Record<string, unknown>;
  layoutTitle: string;
  describedBy: string;
}

const plotlyConfig = {
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d"],
};

export function PlotlyChart({ data, layout, layoutTitle, describedBy }: PlotlyChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let mounted = true;
    let plotElement: HTMLElement | null = null;

    async function drawChart() {
      if (!containerRef.current) {
        return;
      }
      plotElement = containerRef.current;
      const Plotly = (await import("plotly.js-dist-min")).default;
      if (!mounted || !plotElement) {
        return;
      }
      await Plotly.newPlot(plotElement, data, layout, plotlyConfig);
      if (mounted && plotElement) {
        await Plotly.react(plotElement, data, layout, plotlyConfig);
      }
    }

    void drawChart();

    return () => {
      mounted = false;
      if (plotElement) {
        const elementToPurge = plotElement;
        void import("plotly.js-dist-min").then((module) => module.default.purge(elementToPurge));
      }
    };
  }, [data, layout]);

  return (
    <div
      ref={containerRef}
      className="plotly-chart"
      role="img"
      aria-label={layoutTitle}
      aria-describedby={describedBy}
    />
  );
}
