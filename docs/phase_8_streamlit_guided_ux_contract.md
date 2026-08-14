# Phase 8 Streamlit Guided UX, Branding, and Asset Contract

Status: Proposed — awaiting Phase 8 Guided UX Contract approval.

Authoritative Blueprint:

- `plans/phase-8-streamlit-assets-guided-ux.md`

Related approved contracts:

- `docs/phase_2_scientific_contract.md`
- `docs/phase_4_api_contract.md`
- `docs/phase_5_job_contract.md`
- `docs/phase_6_frontend_contract.md`
- `docs/phase_7_streamlit_visual_contract.md`

## 1. Purpose and authority

Phase 8 improves the accepted Streamlit app with clearer branding, guided copy, onboarding context, and optional local assets while preserving the exact accepted Phase 7 chart/data behavior.

The accepted primary user-facing frontend remains:

- `category_tracking_web.py`

The deferred frontend remains:

- `frontend/`

Next.js remains experimental / deferred / non-primary. Phase 8 does not promote it.

This contract governs product-experience polish only. It does not authorize scientific behavior changes, engine changes, FastAPI changes, background-job changes, fixture changes, diagnostic changes, dependency changes, deployment work, or Phase 9 work.

Contract approver:

- the user.

## 2. Product direction

Purpose:

- Help a researcher configure codon mutation probabilities, run the accepted Streamlit workflow, and understand dense scientific output with less friction.

Audience:

- A curious researcher, student, or reviewer who needs to scan settings, run a simulation, compare probability sets, and inspect charts/tables without losing scientific precision.

Tone:

- calm;
- scientific;
- clear;
- polished;
- practical;
- lightly guided;
- not sales-like.

Memorable product detail:

- The interface should feel like a “guided scientific cockpit”: configure once, run once, inspect carefully.

Constraints:

- Streamlit-native layout first.
- Existing Phase 7 visual system first.
- Existing charts/tables remain central.
- No remote assets.
- No new dependencies.
- No scientific reinterpretation.

## 3. Primary frontend authority

The primary accepted frontend is:

- `category_tracking_web.py`

Phase 8 may edit this file only within approved Steps 3-5 and optional Step 6 if assets are approved.

Phase 8 must preserve:

- Streamlit entry point;
- one-button/one-flow user experience;
- accepted section order unless a specific user-approved change says otherwise;
- accepted control order unless a specific user-approved change says otherwise;
- accepted chart/table display;
- accepted fullscreen behavior;
- accepted compare-both separation.

## 4. Deferred Next.js status

The Next.js workspace under `frontend/` remains:

- deferred;
- experimental;
- non-primary.

Phase 8 must not:

- edit `frontend/**`;
- make Next.js the release UI;
- rebuild the app in React/Next.js;
- use Next.js as an asset or branding source;
- change `frontend/README.md` unless a later plan mutation explicitly approves it.

## 5. Guided UX rules

Guided UX means helping the user understand the existing workflow without changing it.

Phase 8 may add or refine:

- high-level intro copy;
- title/subtitle support text;
- Configure → Run → Inspect guidance;
- sidebar helper captions;
- mode explanations;
- status/loading guidance;
- empty-state guidance;
- error guidance;
- result interpretation hints;
- short scientific context near complex sections.

Guided UX must not:

- create a marketing landing page before the tool;
- hide controls behind onboarding;
- add multiple run buttons;
- change the meaning of any mode;
- imply sampled output is authoritative;
- imply exact output is sampled;
- change scientific terminology incorrectly;
- replace charts/tables with prose summaries;
- add speculative scientific claims.

## 6. Branding rules

Branding may make the app feel more intentional, but must remain restrained.

Approved direction:

- scientific lab;
- clear dashboard;
- light, calm, readable surfaces;
- subtle codon/genetics motif if assets are later approved;
- no loud marketing hero;
- no generic gradient/blob design;
- no stock-like filler imagery.

Phase 8 may refine:

- app subtitle;
- short product descriptor;
- small local logo/icon placement if Step 6 assets are approved;
- section microcopy;
- educational captions;
- lightweight visual identity around the existing Streamlit theme.

Phase 8 must not:

- dominate the first viewport with branding;
- push the analysis UI far below the fold;
- obscure charts/tables;
- use brand copy that overpromises scientific certainty;
- introduce remote fonts, remote scripts, or external media.

## 7. Copywriting and scientific wording rules

Copy may clarify the workflow and reduce confusion. It must not redefine the science.

Preserve established labels and terms unless a later explicit approval says otherwise:

- `Codon focus`;
- `Whole population`;
- `Your probability`;
- `Preset`;
- `Compare both`;
- `Sampled copies`;
- `Exact probability`;
- `No more category change`;
- `Surviving category fractions`;
- `Trait codon survival`;
- category labels from the engine.

Copy may explain:

- where to configure settings;
- what each mode is for;
- that exact probability is deterministic;
- that sampled copies are stochastic/experimental;
- that compare-both displays user and preset probability results side by side;
- that charts/tables preserve the accepted scientific output.

Copy must not:

- invent biological claims;
- state causal or evolutionary conclusions not supported by the app;
- hide uncertainty;
- imply sampled results are exact;
- alter numerator/denominator meanings;
- rename scientific outputs in a way that changes meaning;
- simplify terms so far that precision is lost.

If uncertain, preserve existing wording.

## 8. Asset policy

Assets are deferred by default before Step 3.

No image, GIF, icon, SVG, logo, or `assets/**` file may be added during Steps 1-5.

Step 6 requires separate explicit user approval before any asset is added.

If approved later, assets must:

- live under `assets/**`;
- be local only;
- be committed intentionally;
- have source/ownership/license notes;
- have recorded byte size;
- have recorded SHA-256;
- have dimensions recorded when practical;
- be small enough not to bloat the repository;
- support the analysis visually or educationally;
- not obscure controls, charts, or tables;
- not replace scientific charts or tables;
- not require network requests;
- not require new dependencies;
- not contain secrets, personal information, private paths, or external tracking.

Recommended maximum asset sizes unless the user explicitly approves otherwise:

- logo/icon SVG: under 100 KB;
- PNG/JPG illustration: under 500 KB each;
- GIF: under 2 MB each and used sparingly.

Remote hotlinked assets are prohibited.

## 9. Image/GIF/icon accessibility rules

If Step 6 assets are later approved:

- informative images need nearby text, caption, or appropriate alt-like context;
- decorative images should not be presented as scientific evidence;
- icons used for controls must have text labels or accessible names;
- GIFs must not flash;
- GIFs must not distract from analysis;
- motion must not be necessary to understand scientific output;
- assets must not reduce keyboard usability or reading order clarity.

## 10. Theme policy

Default Phase 8 decision:

- `.streamlit/config.toml` is not approved for edits.

Theme edits require separate explicit user approval before implementation.

If theme edits are later approved, they may only adjust safe visual tokens:

- primary color;
- background/surface color;
- text color;
- supported border/radius-like settings;
- supported typography settings.

Theme edits must not:

- change chart data;
- change chart semantics;
- break contrast;
- cause overlapping sections;
- introduce external dependencies;
- require engine/API changes.

## 11. Chart and table preservation rules

Phase 8 may style or explain around accepted charts and tables.

Phase 8 must not change:

- chart type;
- chart traces;
- plotted data;
- axes;
- axis labels;
- units;
- legends;
- category order;
- line/bar meanings;
- marker generation logic;
- fullscreen content semantics;
- table columns;
- table row order;
- table numeric values;
- table scientific meanings.

Phase 8 may add:

- captions;
- short “how to read this” hints;
- section context;
- empty/loading/status copy;
- accessibility context.

Those additions must not calculate new scientific values.

## 12. Control and workflow preservation rules

Preserve:

- sidebar control order unless explicitly approved;
- widget labels unless explicitly approved;
- widget keys;
- widget defaults;
- query bindings;
- validation behavior;
- one-button/one-flow workflow;
- runtime display;
- fullscreen buttons;
- compare-both side-by-side separation.

Do not:

- split the run into many experiment buttons;
- add hidden automatic switching;
- change probability parsing;
- change generation/copy/seed semantics;
- add browser storage;
- add session persistence outside existing Streamlit behavior.

## 13. Error/loading/status guidance rules

Phase 8 may improve wording around:

- loading;
- running;
- invalid input;
- no result yet;
- how to interpret a result section.

Rules:

- Expected validation failures must remain visible.
- Expected validation failures must not become silent empty results.
- Scientific failures must not be swallowed.
- Error copy should be concise and actionable.
- Status meaning must not rely on color alone.
- Runtime display must remain.

## 14. Verification requirements

Every implementation step after this contract must preserve:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest discover -s tests -p "test_streamlit_surface.py" -v
python diagnose_category_tracking_web.py
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
python -m unittest discover -s tests -p "test_*.py"
python -m unittest discover -s tests -p "test_api_job*.py" -v
python -m unittest discover -s tests -p "test_api_*.py" -v
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules); print('engine-ui-independence-ok')"
```

Also verify:

- frozen fixture hashes match the Step 1 immutable baseline manifest;
- diagnostic hashes match the Step 1 immutable baseline manifest;
- dependency files match the Step 1 immutable baseline manifest unless a later approved mutation says otherwise;
- no root runtime imports in engine/API;
- no forbidden engine imports;
- no `__pycache__`;
- no unexpected generated files;
- Git untouched until explicit commit approval.

## 15. Test protection rules

`tests/test_streamlit_surface.py` may be edited during Steps 3-5 only to add focused coverage for approved guided-UX behavior.

Default rule:

- test edits are additive.

Existing Phase 7 assertions must not be:

- deleted;
- weakened;
- relaxed;
- renamed to hide behavior drift;
- changed to accept different chart/table/control behavior.

Any deletion or relaxation of an existing Phase 7 assertion requires:

1. formal plan mutation;
2. explicit user approval;
3. execution-log explanation;
4. proof that scientific/chart/data compatibility is preserved.

Every implementation step that touches `tests/test_streamlit_surface.py` must record a diff review certifying that no existing Phase 7 assertion was removed, weakened, or relaxed unless separately approved.

## 16. Browser QA requirements

Before final Phase 8 acceptance, browser QA must inspect the live Streamlit app if it can be started safely.

Browser QA evidence must include:

- initial load;
- branding/header;
- intro guidance;
- sidebar controls;
- mode explanations;
- one-button workflow;
- Codon focus;
- Whole population;
- Compare both;
- fullscreen sections;
- chart headings;
- table headings;
- assets if later approved;
- invalid input/error state;
- runtime/status display;
- console issues;
- no traceback.

Browser QA is a supplement to deterministic tests, not the source of truth for chart-data equality.

## 17. Prohibited changes

Phase 8 does not allow:

- scientific calculation changes;
- engine changes;
- API changes;
- background-job changes;
- Next.js promotion;
- React/Next.js rewrite;
- dependency changes;
- fixture regeneration;
- diagnostic edits;
- remote assets;
- unlicensed assets;
- asset addition before Step 6 approval;
- theme edits before explicit approval;
- chart-data changes;
- table-data changes;
- hidden automatic mode switching;
- deployment/infrastructure work;
- Phase 9 work.

## 18. Plan-mutation protocol

If a requested improvement requires any prohibited or uncertain change:

1. Stop.
2. Record the conflict in `plans/phase-8-execution-log.md`.
3. Identify affected files and user-visible behavior.
4. Propose the smallest contract/Blueprint mutation.
5. Explain compatibility, verification, and rollback impact.
6. Request explicit user approval.
7. Do not implement until approval is given.

Mutation triggers include:

- chart type/data/axis/legend changes;
- scientific wording changes that alter meaning;
- asset addition before Step 6 approval;
- new dependency;
- theme-file edit;
- engine/API behavior change;
- fixture/diagnostic modification;
- making Next.js primary;
- deployment/auth/database/external service work.

## 19. Approval decisions

| Decision | Recommended option | Status |
| --- | --- | --- |
| Primary Phase 8 frontend | Streamlit app, `category_tracking_web.py` | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Next.js status | Deferred / experimental / non-primary | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Chart/data behavior | Preserve exactly | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Control and section order | Preserve unless explicitly approved | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Assets before Step 3 | Defer by default | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Assets in Step 6 | Require separate explicit approval | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Theme file edits | Not approved by default | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Dependencies | No new dependencies | Proposed — awaiting Phase 8 Guided UX Contract approval |
| Browser visual acceptance | Required before final handoff | Proposed — awaiting Phase 8 Guided UX Contract approval |

## 20. Completion checklist

- [x] Primary frontend owner named.
- [x] Deferred Next.js status named.
- [x] Product direction defined.
- [x] Guided UX rules defined.
- [x] Branding rules defined.
- [x] Copy/scientific wording rules defined.
- [x] Asset policy defined.
- [x] Image/GIF/icon accessibility rules defined.
- [x] Theme policy defined.
- [x] Chart/table preservation rules defined.
- [x] Control/workflow preservation rules defined.
- [x] Verification baseline listed.
- [x] Test-protection rules listed.
- [x] Browser QA expectations listed.
- [x] Plan-mutation protocol listed.
- [ ] User approved this guided-UX contract.

