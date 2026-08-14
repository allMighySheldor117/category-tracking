# Phase 7 Streamlit Visual/Product Contract

Status: Proposed — awaiting Streamlit Visual Contract approval.

Authoritative Blueprint:

- `plans/phase-7-streamlit-product-polish.md`

## 1. Purpose and authority

Phase 7 polishes the accepted Streamlit app into a cleaner, more visually professional scientific product.

The accepted primary user-facing frontend is:

- `category_tracking_web.py`

The Phase 6 Next.js workspace remains:

- deferred;
- experimental;
- non-primary;
- not the release UI.

This contract governs visual/product polish only. It does not authorize changes to scientific behavior, engine APIs, FastAPI routes, background jobs, frozen fixtures, diagnostics, or compatibility APIs.

Contract approver:

- the user.

## 2. Design direction

Purpose:

- Help a researcher configure codon mutation probabilities, run the accepted Streamlit workflow, and inspect dense scientific results without fighting the layout.

Audience:

- A repeat user who needs to scan controls, run the analysis, compare user/preset probabilities, inspect codon or population behavior, and read charts/tables confidently.

Tone:

- clean;
- calm;
- scientific;
- precise;
- lightly polished;
- not flashy;
- not generic SaaS;
- not a marketing page.

Memorable detail:

- The interface should feel like a tidy molecular analysis bench: controls are organized like instruments, charts sit in clear result trays, and comparison views keep user and preset probability sets visibly separate.

Constraints:

- Streamlit-native layout first.
- Existing Plotly charts remain.
- Existing light theme and categorical palette remain unless explicit theme approval is granted.
- No dependency additions by default.
- Preserve accessibility, repeatability, and scientific honesty over decoration.

## 3. Existing UI authority

The accepted visual baseline is the current pushed Streamlit app at Phase 6:

- `category_tracking_web.py`
- `tests/test_streamlit_surface.py`
- `tests/fixtures/phase1_streamlit_surface.json`

Phase 7 may improve presentation around the existing UI, but the user accepted the current chart/data experience. The current experience is the baseline to polish, not replace.

## 4. Strict preservation contract

Phase 7 must preserve:

- exact chart types;
- chart meanings;
- chart axes;
- chart units;
- chart legends;
- chart traces;
- chart data;
- chart category ordering;
- Plotly figure semantic content;
- table contents;
- table columns;
- table row ordering;
- table scientific meanings;
- section order;
- accepted control order unless a specific user-approved polish task changes it;
- one-button workflow;
- exact probability behavior;
- sampled RNG behavior;
- aggregated sampled contract;
- FastAPI behavior;
- Phase 5 job behavior;
- engine APIs;
- Streamlit primary frontend decision;
- Tkinter compatibility;
- frozen diagnostics;
- frozen fixtures.

Presentation code may transform already-returned table rows for display only when the current Streamlit app already does so. It must not calculate new scientific results, denominators, mutation behavior, convergence rules, or simulation outputs.

## 5. Allowed visual polish

Phase 7 may improve:

- spacing between control groups;
- sidebar grouping and captions;
- run-status and runtime visibility;
- main title/hero clarity;
- explanatory copy around existing controls and sections;
- section card/container consistency;
- chart panel framing;
- fullscreen button discoverability;
- table captions and headings;
- empty, loading, success, and error messages;
- visual rhythm between Codon focus and Whole population workspaces;
- readability of Compare both side-by-side panels;
- keyboard/focus/accessibility clarity;
- optional local assets after explicit asset approval.

## 6. Sidebar/control contract

The sidebar is the control cockpit.

Preserve:

- `Generations`;
- `Copies per codon`;
- `Sampling seed`;
- `Your probability`;
- `Preset probability`;
- `Your probability` / `Preset` / `Compare both`;
- `Sampled copies` / `Exact probability`;
- `Current computation` / `Exact surviving trait fractions`;
- alpha control;
- selected codon selector;
- compare codon selector;
- codon-outcome generation slider;
- analysis runtime display.

Phase 7 may:

- improve grouping;
- add concise captions;
- add subtle dividers or containers;
- improve runtime/status wording;
- make the one-button/one-flow behavior more visually obvious.

Phase 7 must not:

- split the workflow into many run buttons;
- remove existing controls;
- change defaults;
- change query bindings;
- change probability parsing;
- change validation behavior.

## 7. Main page hierarchy contract

The first viewport should immediately communicate:

- app name;
- scientific purpose;
- current workspace choice;
- where controls live;
- where results begin.

Phase 7 may:

- refine title/caption copy;
- improve hero/header composition;
- add a concise visual motif;
- clarify result-section headings;
- add explanatory microcopy where it reduces confusion.

Phase 7 must not:

- add a marketing page before the tool;
- hide the working analysis UI;
- replace scientific labels with vague product language;
- change the accepted section order without explicit approval.

## 8. Chart container and fullscreen contract

Charts are already accepted.

Phase 7 may:

- improve spacing around charts;
- make chart group headings clearer;
- make fullscreen buttons more consistent;
- add captions that explain what a chart already shows;
- improve chart container/card presentation.

Phase 7 must not change:

- chart type;
- traces;
- axes;
- units;
- legends;
- plotted values;
- category order;
- marker generation logic;
- fullscreen dialog content semantics.

Compare both views must keep `User probability` and `Preset probability` visibly separate. They must not be mixed into one chart/table unless a later explicit user request approves that exact behavior.

## 9. Table and text contract

Tables are scientific evidence, not decoration.

Phase 7 may:

- add table captions;
- improve headings;
- improve table container spacing;
- clarify empty-state or error-state copy;
- improve readability of long sections.

Phase 7 must not:

- remove scientific columns;
- rename columns in a way that changes meaning;
- change row ordering;
- change numeric values;
- hide tables that already exist;
- replace tables with screenshots or images.

## 10. Empty/loading/error/status contract

Phase 7 may polish:

- loading messages;
- success/status messages;
- invalid input guidance;
- runtime display;
- empty-state wording.

Rules:

- Error messages must remain concise and actionable.
- Expected validation failures must not become silent empty results.
- Scientific failures must not be swallowed.
- Status meaning must not rely on color alone.
- Dynamic status text should remain visible to users and testable.

## 11. Asset policy

Assets are optional.

No image, GIF, icon, or asset directory may be added unless the user explicitly approves the asset step.

If approved, assets must:

- live under `assets/**`;
- be local;
- have recorded source/ownership/license notes;
- have recorded file size, dimensions, and SHA-256;
- support the analysis visually or educationally;
- avoid obstructing controls, charts, and tables;
- avoid remote tracking or external requests;
- avoid secrets, personal data, or private paths.

No large asset or new asset dependency may be added without explicit approval.

If assets are not approved, Phase 7 Step 7 is skipped normally and recorded in the execution log.

## 12. Theme policy

Default decision:

- `.streamlit/config.toml` is not approved for edits in Phase 7 unless the user explicitly approves theme-level polish.

If theme edits are approved, they may only adjust Streamlit visual tokens such as:

- primary color;
- background/surface color;
- text color;
- border/radius-like settings supported by Streamlit;
- typography weight where Streamlit supports it safely.

Theme edits must not:

- change chart data;
- change scientific meaning;
- break contrast;
- cause visual overlap;
- introduce external dependencies;
- require engine/API changes.

## 13. Accessibility contract

Phase 7 must preserve or improve:

- keyboard reachability;
- visible focus;
- clear accessible names for controls;
- readable labels;
- understandable status/loading text;
- chart/table headings or captions;
- non-color-only status meaning;
- contrast for key text and controls;
- modal/fullscreen escapability;
- no obvious keyboard traps.

WCAG 2.2 Level AA is the target review lens, with special attention to:

- focus appearance;
- target size;
- labels;
- error suggestions;
- name/role/value;
- live-region/status clarity.

## 14. Documentation policy

`README.md` may be touched only for tiny launch/use wording updates.

Do not edit README content about:

- roadmap;
- architecture;
- API contracts;
- scientific contracts;
- engine behavior;
- deployment.

If assets are approved, README may include local asset attribution or usage notes only if needed.

## 15. Prohibited changes

Phase 7 does not allow:

- engine changes;
- API changes;
- job changes;
- Next.js promotion;
- React/Next.js rewrite;
- new dependencies without explicit approval;
- fixture regeneration;
- diagnostic edits;
- scientific calculation changes;
- chart-data changes;
- table-data changes;
- hidden automatic mode switching;
- deployment/infrastructure work;
- Phase 8 work.

## 16. Verification requirements

Every implementation step must preserve:

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

- frozen fixture hashes unchanged;
- diagnostic file hashes unchanged;
- both diagnostics output all 17 PASS lines;
- no root runtime imports;
- no forbidden engine imports;
- no `__pycache__`;
- no unexpected generated files;
- no Git action until explicit commit/push approval.

## 17. Browser QA contract

Before final visual acceptance, run Streamlit locally if safe:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m streamlit run category_tracking_web.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Browser QA must inspect:

- initial load;
- sidebar/control area;
- one-button workflow;
- Codon focus;
- Whole population;
- Compare both;
- fullscreen sections;
- charts;
- tables;
- invalid input/error state;
- runtime/status display;
- console issues;
- no traceback.

The user must visually accept the result before Phase 7 final handoff.

## 18. Change protocol

If a desired polish requires changing any preserved chart, table, scientific meaning, dependency, theme scope, asset scope, engine/API behavior, fixture, or Next.js status:

1. Stop.
2. Record the evidence in `plans/phase-7-execution-log.md`.
3. Identify the affected section and files.
4. Propose the smallest contract mutation.
5. Explain compatibility and rollback impact.
6. Request explicit human approval.
7. Do not implement until approval is given.

## 19. Approval decisions

| Decision | Recommended option | Status |
| --- | --- | --- |
| Primary Phase 7 frontend | Streamlit app, `category_tracking_web.py` | Proposed — awaiting Streamlit Visual Contract approval |
| Next.js status | Deferred / experimental / non-primary | Proposed — awaiting Streamlit Visual Contract approval |
| Chart/data behavior | Preserve exactly | Proposed — awaiting Streamlit Visual Contract approval |
| Control and section order | Preserve unless explicitly approved | Proposed — awaiting Streamlit Visual Contract approval |
| Assets | Optional, require separate approval | Proposed — awaiting Streamlit Visual Contract approval |
| Theme file edits | Not approved by default | Proposed — awaiting Streamlit Visual Contract approval |
| Dependencies | No new dependencies by default | Proposed — awaiting Streamlit Visual Contract approval |
| Browser visual acceptance | Required before final handoff | Proposed — awaiting Streamlit Visual Contract approval |

## 20. Completion checklist

- [x] Primary frontend owner named.
- [x] Deferred Next.js status named.
- [x] Visual direction defined.
- [x] Chart/data preservation rules defined.
- [x] Sidebar/control rules defined.
- [x] Main hierarchy rules defined.
- [x] Chart/fullscreen rules defined.
- [x] Table/readability rules defined.
- [x] Asset policy defined.
- [x] Theme policy defined.
- [x] Accessibility expectations defined.
- [x] Verification baseline listed.
- [x] Plan-mutation/change protocol listed.
- [ ] User approved this visual contract.
