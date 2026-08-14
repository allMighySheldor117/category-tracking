import { BackendStatus } from "./backend-status";
import { AnalysisWorkspace } from "./analysis-workspace";

export function WorkspaceShell() {
  return (
    <main className="workspace">
      <header className="workspace__header">
        <div>
          <p className="workspace__eyebrow">Exact codon category analysis</p>
          <h1 className="workspace__title">Codon Category Tracking Lab</h1>
          <p className="workspace__subtitle">
            Track exact starting codons through amino-acid property categories,
            compare mutation probabilities, and inspect sampled estimates with
            the same chart-first flow as the trusted Streamlit app.
          </p>
        </div>
        <BackendStatus />
      </header>

      <div className="workspace__grid">
        <AnalysisWorkspace />
      </div>
    </main>
  );
}
