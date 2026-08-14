# Category Tracking Frontend

This is the Phase 6 Next.js + TypeScript analysis workspace shell.

Status: deferred / experimental / non-primary.

The accepted Phase 6 user-facing frontend is the Streamlit app at
`../category_tracking_web.py`. Run it from the repository root with:

```powershell
python -m streamlit run category_tracking_web.py
```

This Next.js workspace was implemented as a browser-consumer experiment, but it
was not accepted as the primary UI because its layout, controls, and chart
parity did not match the trusted Streamlit experience closely enough. Do not
treat this directory as the release frontend unless a later approved phase or
contract mutation promotes it again.

## Scope

- Provides the first browser workspace structure under `frontend/`.
- Keeps scientific computation in the FastAPI backend and Python engine.
- Does not duplicate codon tables, mutation matrices, denominators, or simulation algorithms.
- Remains non-primary until explicit visual/control/chart acceptance criteria are approved and satisfied.

## Scripts

```powershell
npm install
npm test
npm run build
npm run lint
```

## API boundary

Step 4 adds typed client functions in `lib/api/client.ts` and a same-origin
proxy under `app/api/`.

Browser code should call the typed client only. The proxy forwards approved
Phase 4 and Phase 5 API routes to `FRONTEND_API_BASE_URL`, defaulting to
`http://127.0.0.1:8000` for local development.

The frontend must not recalculate scientific results, duplicate biological
definitions, or expose detailed sampled per-copy records.

## Generated artifacts

Do not commit:

- `node_modules/`
- `.next/`
- coverage output
- temporary browser/test artifacts
- environment files containing secrets
