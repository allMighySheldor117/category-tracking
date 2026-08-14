export function BackendStatus() {
  return (
    <aside className="status-card" aria-labelledby="backend-status-title">
      <span className="status-card__label" id="backend-status-title">
        Backend connection
      </span>
      <span className="status-card__value">Ready for Step 4 API wiring</span>
      <p>
        Phase 3 creates the shell only. Backend requests start after the typed
        client and proxy boundary are approved.
      </p>
    </aside>
  );
}

