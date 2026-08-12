# Phase 2 Execution Log

## Step 1 — Revalidate Phase 1 and open the Phase 2 execution log

- **Status:** Complete; stop before Step 2
- **Started (UTC):** 2026-08-11T17:31:32.831Z
- **Automated gates completed (UTC):** 2026-08-11T17:34:50.358Z
- **Plan:** `plans/phase-2-strengthen-computation.md`
- **Execution mode:** Direct mode. `git rev-parse --is-inside-work-tree` and `git status --short` both report that this is not a Git repository. No Git state was initialized, repaired, or modified.
- **Scope:** Read-only Phase 1 revalidation plus creation of this execution log. No application code, test, fixture, configuration, diagnostic, or research file was edited.
- **Approval:** ECC Gate 1 was explicitly approved by the user with the instruction to execute Blueprint Step 1 only and stop before Step 2.
- **Style preflight:** No application-code edit occurred, so the application-code compliance declaration was not required for this step.

### Environment observation

| Component | Observed version |
|---|---|
| Python | `3.13.0` |
| pandas | `2.2.3` |
| Plotly | `6.8.0` |
| Streamlit | `1.60.0` |

These are observations of the approved Phase 1 environment, not newly introduced constraints or dependencies.

### Pre-change touched-file manifest

| Path | Planned action | Existed before step | Pre-change SHA-256 | Backup |
|---|---|---|---|---|
| `plans/phase-2-execution-log.md` | Create Step 1 execution evidence | No | N/A | N/A — newly created file |

Rollback may remove only the exact resolved execution-log path after confirming that it was absent before this step. No application or research file is a rollback target.

### Governing-context and baseline manifest

All 34 files explicitly required by the Phase 2 orchestration prompt existed. The wider manifest below records every governing document, root research artifact, final application file, engine module, baseline test, diagnostic, fixture, and configuration file in scope before Phase 2 application work.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `CLAUDE.md` | 7465 | `fb87fe4e8d34f55fbad15ec533ea823ccce41aab4e36fbbfae54d599246de6bc` |
| `future_enhancement_explained.plan.md` | 11992 | `b709d5609c0fe0519271fd61b5b517096b2d7a430770d73730f7459d3fd34317` |
| `plans/phase-1-extract-ui-independent-engine.md` | 39004 | `9a65102eec81ca704a80706f1d0d9062359e182eba8535fc05d09ae28f455de7` |
| `plans/phase-1-execution-log.md` | 37010 | `7d83b4f1643e2083f49cc6e6ce478f6fbccc8eb9abf87f1956d752269fd0f66f` |
| `plans/phase-2-strengthen-computation.md` | 61196 | `eccff38c71aae379222243dc82ad13c047f8a1b174bc942ce6f722e0254254dc` |
| `category_tracking.py` | 346862 | `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de` |
| `category_tracking_web.py` | 63021 | `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8` |
| `diagnose_category_tracking_web.py` | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| `.streamlit/config.toml` | 1338 | `24a12ab95395af1a655b70a00bbf940347cc062a4a83b658f53dd7f0193fb0d9` |
| `final code/.ai-style-rules.md` | 12069 | `7e24d0df23ea6a50b197ace375c38e8518f83684052a17dc8f9ab12c73a1a490` |
| `final code/.streamlit/config.toml` | 1338 | `24a12ab95395af1a655b70a00bbf940347cc062a4a83b658f53dd7f0193fb0d9` |
| `final code/category_tracking_web.py` | 53781 | `c6301105b218da042fa56f57a3d4a96db5dbc86aa5b23abc05a43f86ce269797` |
| `final code/category_tracking.py` | 334892 | `3b0f2510d47a32e44b5d549d2e875c5a0e1ea4d890d9fb60c5f9828ac0856394` |
| `final code/CLAUDE.md` | 3893 | `7f629c34c3c56077fddf0568daedd83115f989f4a5a233d9da7220fe208ad8c6` |
| `final code/diagnose_category_tracking_web.py` | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| `final code/engine/__init__.py` | 187 | `708a4a68b62fe1c28706e9ca1746c3581624f7de2b9c7dd6702a7c34ad37edb8` |
| `final code/engine/category_analysis.py` | 12228 | `90d0f9dbb0381aa5e08d25db5eb8e57c70f0cc04472456521733ee9c0a7a8a8d` |
| `final code/engine/exact_tracking.py` | 7742 | `de9526c79f855a2dc2e8adae26682b816904b68d63433b50b4d768193b197716` |
| `final code/engine/genetic_code.py` | 4136 | `7306478d03aaafd7e5e3fad23f30bb761cdcae3628e4554f01c110fc0142496d` |
| `final code/engine/models.py` | 4337 | `f959c4202a681f59ba77c7210b4096255b6cf1c81a6cde803f2ccce7b432da3e` |
| `final code/engine/mutation_matrix.py` | 704 | `be819f9af26611fb788dcb9bdc1e8a93a96417003b204e72a98a3b08b5939a96` |
| `final code/engine/README.md` | 4090 | `fd7700ff1ee980d9b678277017e929d254f0643fec00b7d3bf8112354fe68cb2` |
| `final code/engine/sampled_tracking.py` | 2614 | `b959ffad244d0ebba4f34a8d61e187b2020ab845edf835547d15c4cf16d0bbc6` |
| `final code/engine/summaries.py` | 11143 | `b036af3781e216af22423c3c60ce95d1c5be3741989d9d8aabd9131e3e4b5bed` |
| `final code/README.md` | 3073 | `b561e8e9198d678a03ddf3b3f55ee6f7be9dcb075bd45282ab85fcfeb00183f6` |
| `final code/tests/__init__.py` | 48 | `b0dbb33fd5480cd72ab82cae5f38aa1727a85ce6108ab1097384ddfaa091a281` |
| `final code/tests/compat/__init__.py` | 48 | `0929ccadf646eda8ec1873de254f9f95b42995c538dcc832aee5dfacd3e23df5` |
| `final code/tests/compat/diagnose_category_tracking_web_phase1_baseline.py` | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| `final code/tests/fixtures/phase1_scientific_baseline.json` | 13552 | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` |
| `final code/tests/fixtures/phase1_streamlit_surface.json` | 7606 | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` |
| `final code/tests/test_baseline_behavior.py` | 12687 | `1c310f60e0a5f972e154eb98befc1d52d884dbf2c6d6642a403fa4a4855cdcf8` |
| `final code/tests/test_category_analysis.py` | 7535 | `e4c88689f26f1273fa0298c0162943730d520150687658c93461142901616a4d` |
| `final code/tests/test_engine_boundaries.py` | 5812 | `2dc932044797c2ae32f29a53b17e84c435febf7a2c83a459d532e103f0edb61d` |
| `final code/tests/test_exact_tracking.py` | 3579 | `f307d0222efde71a084fa66a049a4a9345d9cd71c951e811b219de8258da3ab0` |
| `final code/tests/test_genetic_code.py` | 5044 | `55928d9fbd420fb0d987397948d31ecbb11a7334d8573df014a203a367e04477` |
| `final code/tests/test_legacy_adapter.py` | 3351 | `8e0ce0423ff7d683a49d5427e5fb94d17d5a0530e07c4371d0ff3b8046a04b2e` |
| `final code/tests/test_phase1_boundaries.py` | 4527 | `aa6ed47a9db9102358fd37a4768ae27b7f421aa7853422e80afcf951e321a1ae` |
| `final code/tests/test_sampled_tracking.py` | 4324 | `801735226f6aacdc7ccd436222d1339f0e091c3f05c9fa640b46ab640ee3eef2` |
| `final code/tests/test_streamlit_engine_boundary.py` | 5045 | `90600b16fd9f238341d7c4ee2daaa5873abe84f0291bad9d44cd4401ead318d3` |
| `final code/tests/test_streamlit_surface.py` | 7741 | `30d60050e14c364eea4ab35badf3841bcc9730bb2eba14a6df7f377ad70d2cdc` |
| `final code/tests/test_summaries.py` | 8008 | `d8a169d09ef257943eb9d98b8f11619e434c6ff5f5b3c6f9ae2ab1814154077e` |

The execution log itself is excluded from its own content hash because embedding that hash would be recursive. Later steps record its pre-change hash before appending.

### Verification commands and evidence

Every Python command ran from `final code/` with `PYTHONDONTWRITEBYTECODE=1`. No `__pycache__` directory existed after verification.

#### Complete unittest discovery

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

- **Result:** PASS, exit code `0`
- **Observed:** 63 tests in 31.821 seconds

```text
...............................................................
----------------------------------------------------------------------
Ran 63 tests in 31.821s

OK
```

The previously documented non-failing Streamlit bare-mode warnings appeared: `MemoryCacheStorageManager` was used without a runtime and `ScriptRunContext` was absent during bare-mode checks. No exception or test failure occurred.

#### Final-code frozen diagnostic

```powershell
python diagnose_category_tracking_web.py
```

- **Result:** PASS, exit code `0`
- **Observed:** all 17 checks passed

```text
PASS no-more-change exact tolerance
PASS constant-state start generation
PASS alpha stable-state tolerance
PASS surviving-category fractions
PASS aggregate all-codon population series
PASS no-more-change shared exact source
PASS surviving-fraction no-more-change basis
PASS default render
PASS whole population workspace
PASS whole population trait selector
PASS preset mode
PASS compare both mode
PASS exact probability mode
PASS surviving-fraction no-more-change mode
PASS surviving-fraction alpha input
PASS selected codon TGG
PASS invalid probability handled
```

The same documented bare-mode Streamlit warnings appeared and were non-failing.

#### Frozen compatibility diagnostic

```powershell
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

- **Result:** PASS, exit code `0`
- **Observed:** all 17 checks passed

```text
PASS no-more-change exact tolerance
PASS constant-state start generation
PASS alpha stable-state tolerance
PASS surviving-category fractions
PASS aggregate all-codon population series
PASS no-more-change shared exact source
PASS surviving-fraction no-more-change basis
PASS default render
PASS whole population workspace
PASS whole population trait selector
PASS preset mode
PASS compare both mode
PASS exact probability mode
PASS surviving-fraction no-more-change mode
PASS surviving-fraction alpha input
PASS selected codon TGG
PASS invalid probability handled
```

The same documented bare-mode Streamlit warnings appeared and were non-failing.

#### Engine UI-import boundary

```powershell
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

- **Result:** PASS, exit code `0`
- No forbidden UI framework was loaded by importing `engine`.

#### Final-code runtime locality

```powershell
python -c "from pathlib import Path; import category_tracking, category_tracking_web, engine; root=Path.cwd().resolve(); assert all(root in Path(module.__file__).resolve().parents for module in (category_tracking, category_tracking_web, engine))"
```

- **Result:** PASS, exit code `0`
- `category_tracking` resolved to `final code/category_tracking.py`.
- `category_tracking_web` resolved to `final code/category_tracking_web.py`.
- `engine` resolved to `final code/engine/__init__.py`.

#### Immutable diagnostic and fixture gate

- **Result:** PASS
- Root diagnostic, final-code diagnostic, and frozen compatibility diagnostic are byte-identical at SHA-256 `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4`.
- Phase 1 scientific fixture remains `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b`.
- Phase 1 Streamlit fixture remains `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035`.
- Root research application hashes match the Phase 1 fixed point.

### Baseline interpretation notes

- `plans/phase-1-execution-log.md` retains an early Step 10 header saying automated validation was in progress, but the same section later records the user's explicit Step 10 approval, and Step 11 is marked complete. The later approval/completion evidence is authoritative.
- `plans/phase-2-strengthen-computation.md` still labels itself “Reviewed draft awaiting human approval.” The user's explicit ECC Gate 1 implementation approval establishes the current authority to execute Step 1; the Blueprint status is not changed in this step and will be registered according to Step 11.
- No Phase 2 contract, production module, test, or fixture exists yet.
- No dependency was added and no external research was required.

### Step 1 exit criteria

| Criterion | Result |
|---|---|
| Complete Phase 1 unittest baseline remains green | PASS — 63 tests |
| Both frozen diagnostic commands retain 17 passes | PASS |
| All three diagnostic hashes remain identical | PASS |
| Frozen Phase 1 fixture hashes remain unchanged | PASS |
| Root research hashes remain unchanged | PASS |
| Engine import remains UI-independent | PASS |
| Application imports resolve entirely under `final code/` | PASS |
| No application/frozen artifact changed | PASS |
| Phase 2 execution log created with manifest and evidence | PASS |
| No Git state created or repaired | PASS |
| No derived `__pycache__` directories remain | PASS — count `0` |

### Plan mutations

None.

### Rollback

Because this execution log was the only new file and did not exist before Step 1, rollback removes only the exact resolved path `plans/phase-2-execution-log.md` after validating that it is inside the workspace `plans/` directory. No application, test, fixture, configuration, diagnostic, or research file is restored or removed.

### Handoff and mandatory stop

Step 1 is complete. Stop before Blueprint Step 2. The next action is the separately scheduled scientific-contract specialist step, which must create and obtain approval for `final code/docs/phase_2_scientific_contract.md` before any Phase 2 production implementation begins.

---

## Step 2 — Freeze the scientific contract and obtain approval

- **Status:** Contract drafted and verified — human Scientific Contract approval pending
- **Started (UTC):** 2026-08-11T17:42:46.583Z
- **Scope:** Create the authoritative proposed Phase 2 scientific contract and record evidence. No production code, test, fixture, schema generator, dependency, adapter, diagnostic, or Blueprint change is authorized.
- **Contract-first boundary:** The provider is the Python engine under `final code/engine/`; consumers are the Streamlit and Tkinter adapters, engine/compatibility tests, and Python/notebook callers. The user is the contract approver. HTTP/service contracts remain deferred.

### Pre-change touched-file manifest

| Path | Planned action | Existed before step | Bytes | Pre-change SHA-256 | Backup |
|---|---|---|---:|---|---|
| `plans/phase-2-execution-log.md` | Append Step 2 manifest, verification, and approval state | Yes | 12996 | `cc9a155727bdb98b024cd2c1acbd51fa528cb9e93f61076a56b2423ccd3a98bf` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-02-20260811T174246565Z\phase-2-execution-log.md` |
| `final code/docs/phase_2_scientific_contract.md` | Create proposed authoritative contract | No | N/A | N/A | N/A — newly created file |

The execution-log backup hash is `cc9a155727bdb98b024cd2c1acbd51fa528cb9e93f61076a56b2423ccd3a98bf`, exactly matching the pre-change source. Rollback restores only this recorded log backup and removes only the exact new contract file after validating its resolved path under `final code/docs/`.

### Contract artifact

- **Path:** `final code/docs/phase_2_scientific_contract.md`
- **Status inside artifact:** `Proposed — awaiting Scientific Contract approval`
- **Contract version:** `2.0-proposed`; Phase 1 compatibility remains `v1`
- **Size:** 52326 bytes, 886 lines
- **SHA-256:** `acc427005e13651f728492ddee3ace6bde8c9b2dbcac5c0f0be7659ad0a8d75f`
- **Authoritative owner:** Python scientific engine under `final code/engine/`
- **Approver:** Project owner/user

The contract contains all 27 required numbered sections. It freezes the exact and aggregate public signatures, ordered dataclass fields, all canonical DataFrame columns/dtypes/index/order/empty behavior, scope and denominator rules, formulas and worked examples, convergence/status semantics, directed comparisons, exact-result provenance, aggregated copy-major/local-RNG behavior, detailed-reduction equivalence, unavailable per-copy information, invariants, errors, structural memory limits, UI compatibility, fixture policy, consumer/provider verification, change protocol, and deferred work.

The proposed calibration panel is concrete and preregistered in the contract: seeds `(1729, 271828, 314159)`, total sample sizes `(610, 6100, 61000)`, equal valid-codon starts, the existing preset mutation matrix, and ten generations. No implementation or calibration run occurred in this documentation step.

### Contract review and resolutions

A line-by-line review against the Blueprint and the requested contract inventory found no unresolved CRITICAL or HIGH ambiguity after these contract-only corrections:

1. Added numerical worked examples for category fractions, codon/amino-acid/trait survival, cumulative stops, convergence, comparisons, and exact-versus-sampled normalization.
2. Replaced an unspecified future seed/size panel with the explicit proposed preregistration above.
3. Made canonical convergence status values exact and distinct from frozen compatibility strings.
4. Named the aggregated scoped-query and comparison entry points, approved metric identifiers, source columns, and key-alignment behavior.
5. Made aggregate counter ownership, nullability, derivation hierarchy, grouped cumulative-stop derivation, and non-duplication rules explicit.

The contract completeness audit passed 30 required-token checks, confirmed exactly 27 numbered sections, confirmed nine proposed decision rows, and found no `TBD`, `TODO`, “as applicable,” generic numeric-column, or implementation-defined placeholders.

### Verification commands and evidence

All Python commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1`.

#### Contract existence

```powershell
python -c "from pathlib import Path; p=Path('docs/phase_2_scientific_contract.md'); assert p.is_file() and p.stat().st_size > 0"
```

- **Result:** PASS, exit code `0`
- **Observed:** `docs\\phase_2_scientific_contract.md` exists and is 52326 bytes.

#### Complete unittest discovery

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

- **Result:** PASS, exit code `0`
- **Observed:** 63 tests in 39.269 seconds.

```text
...............................................................
----------------------------------------------------------------------
Ran 63 tests in 39.269s

OK
```

Only the previously documented non-failing Streamlit bare-mode cache/`ScriptRunContext` warnings appeared.

#### Final-code frozen diagnostic

```powershell
python diagnose_category_tracking_web.py
```

- **Result:** PASS, exit code `0`
- **Observed:** all original 17 checks passed.

#### Frozen compatibility diagnostic

```powershell
python -m tests.compat.diagnose_category_tracking_web_phase1_baseline
```

- **Result:** PASS, exit code `0`
- **Observed:** all original 17 checks passed.

Both commands produced the same ordered PASS list: no-more-change exact tolerance; constant-state start generation; alpha stable-state tolerance; surviving-category fractions; aggregate all-codon population series; no-more-change shared exact source; surviving-fraction no-more-change basis; default render; whole population workspace; whole population trait selector; preset mode; compare both mode; exact probability mode; surviving-fraction no-more-change mode; surviving-fraction alpha input; selected codon TGG; invalid probability handled.

#### Engine UI-import boundary

```powershell
python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"
```

- **Result:** PASS, exit code `0`.

#### Runtime import locality

```powershell
python -c "from pathlib import Path; import category_tracking, category_tracking_web, engine; root=Path.cwd().resolve(); assert all(root in Path(module.__file__).resolve().parents for module in (category_tracking, category_tracking_web, engine))"
```

- **Result:** PASS, exit code `0`.
- `category_tracking` resolved to `final code/category_tracking.py`.
- `category_tracking_web` resolved to `final code/category_tracking_web.py`.
- `engine` resolved to `final code/engine/__init__.py`.

#### Immutable hashes

| Artifact | SHA-256 | Result |
|---|---|---|
| Root `category_tracking.py` | `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de` | Unchanged |
| Root `category_tracking_web.py` | `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8` | Unchanged |
| All three diagnostic copies | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` | Equal and unchanged |
| `phase1_scientific_baseline.json` | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` | Unchanged |
| `phase1_streamlit_surface.json` | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` | Unchanged |

The full corrected immutable manifest passed for 41 recorded governing/application/test artifacts. The Step 1 table contains one transcription error for `final code/tests/test_category_analysis.py`: it records `...934611...`, while both the authoritative Phase 1 execution log and the repeatedly observed current file hash are `e4c88689f26f1273fa0298c0162943730d520150687658c93441142901616a4d`. The file is still 7535 bytes, its tests pass, and no edit occurred in Step 2. This note corrects the evidence without rewriting historical Step 1 text.

#### File-boundary and repository audit

- Final-code manifest: PASS — 33 files; the contract is the only additive file relative to the corrected Step 1 manifest.
- No Phase 2 production module, test, fixture, schema, generator, or algorithm exists: PASS.
- No unexpected file exists outside the two-file touched manifest: PASS.
- Derived `__pycache__` directory count after verification: `0`.
- `git rev-parse --is-inside-work-tree`: expected exit `128`, “not a git repository.”
- `git status --short`: expected exit `128`, “not a git repository.”
- Git was not initialized, repaired, removed, or modified.

### Post-change touched-file manifest

| Path | Result | Post-change bytes | Post-change SHA-256 |
|---|---|---:|---|
| `final code/docs/phase_2_scientific_contract.md` | Created proposed contract | 52326 | `acc427005e13651f728492ddee3ace6bde8c9b2dbcac5c0f0be7659ad0a8d75f` |
| `plans/phase-2-execution-log.md` | Appended Step 2 evidence; human approval remains pending | Self-referential log | Excluded from embedded post-hash; pre-completion append hash was `2248a4aee8ec6644d9146dbe8cbdba68fa248839650a3f3fef0af5cdb1043580` |

### Proposed decisions awaiting approval

1. Required local integer seed for aggregated sampling.
2. Copy-major streaming and detailed-reduction draw-order equivalence.
3. Engine-only aggregated mode with frozen Streamlit UI.
4. Eager exact population core plus named scoped queries.
5. Nullable `pd.NA` relative delta at zero baseline.
6. Both new and cumulative stop-codon outcomes.
7. Constructed Wilson/Bonferroni tests plus fixed reviewed calibration.
8. One compact static Phase 2 fixture in Step 3.
9. Exact conservation tolerance `rel_tol=1e-12`, `abs_tol=1e-12`, with Phase 1 hex equality retained.

All nine remain **Proposed — awaiting human approval**. This log does not approve them on the user's behalf.

### Plan mutations and implementation state

- **Plan mutations:** None. Contract details resolve Blueprint-scheduled scientific decisions at the approval gate.
- **Production implementation:** None.
- **Tests/fixtures/dataclasses/algorithms created or changed:** None.
- **Dependencies added:** None.
- **Blueprint or Phase 1 documentation changed:** None.

### Rollback

1. Validate that `final code/docs/phase_2_scientific_contract.md` resolves inside the workspace's `final code/docs/` directory, then remove only that exact newly created file.
2. Restore only `plans/phase-2-execution-log.md` from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-02-20260811T174246565Z\phase-2-execution-log.md`.
3. Verify the restored log is 12996 bytes with SHA-256 `cc9a155727bdb98b024cd2c1acbd51fa528cb9e93f61076a56b2423ccd3a98bf`.

No application, test, fixture, diagnostic, configuration, Blueprint, Phase 1 document, root research file, or Git path is a rollback target.

### Step 2 completion and mandatory stop

- **Automated drafting/verification completed (UTC):** 2026-08-11T18:01:48.637Z
- **Automated Step 2 checks:** Complete and green.
- **Scientific Contract approval:** Pending explicit user approval.
- **Step 3 authorization:** Not granted.

The `ecc:contract-first` workflow stops here. Do not create typed models, fixtures, tests, providers, comparisons, or aggregated algorithms until the user explicitly approves this proposed contract.

### Scientific Contract approval record

- **Approval received (UTC):** 2026-08-11T18:06:11.050Z
- **User approval:** “Approve the Phase 2 Scientific Contract. Resume the Phase 2 orchestrator at Blueprint Step 3 without redoing Steps 1–2.”
- **Decision effect:** All nine decisions in contract section 25 are accepted exactly as proposed.
- **Gate result:** PASS — Blueprint Step 2 is complete and Step 3 is authorized.
- **No redo:** Step 1 and the Step 2 drafting/verification suite are not rerun as implementation work.
- **Approved contract pre-status hash:** `acc427005e13651f728492ddee3ace6bde8c9b2dbcac5c0f0be7659ad0a8d75f`.
- **Approval-transition backup:** `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-03-20260811T180610892Z\phase_2_scientific_contract.md`.

---

## Step 3 — Add typed Phase 2 models and static schema contracts

- **Status:** Complete
- **Started (UTC):** 2026-08-11T18:06:11.050Z
- **Depends on:** Scientific Contract approval — satisfied above
- **Execution mode:** Direct mode; writes and verification serialized; no Git action
- **TDD order:** Create the focused test and reviewed static fixture, confirm the intended missing-model failure, then edit `engine/models.py` minimally to green.

### Pre-change touched-file manifest and backups

| Path | Planned action | Existed | Bytes | Pre-change SHA-256 | Backup |
|---|---|---|---:|---|---|
| `final code/engine/models.py` | Add only approved Phase 2 aliases, errors, and named result dataclasses | Yes | 4337 | `f959c4202a681f59ba77c7210b4096255b6cf1c81a6cde803f2ccce7b432da3e` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-03-20260811T180610892Z\models.py` |
| `final code/tests/test_phase2_models.py` | Create focused contract tests | No | N/A | N/A | N/A — remove exact new path on rollback |
| `final code/tests/fixtures/phase2_scientific_contract.json` | Create one reviewed static contract fixture | No | N/A | N/A | N/A — remove exact new path on rollback |
| `plans/phase-2-execution-log.md` | Record Step 3 evidence | Yes | 24206 | `9bdc96840669c7658d1e2b393b0c95fe79c1d5f653749eb589c44f747e23b750` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-03-20260811T180610892Z\phase-2-execution-log.md` |

The contract status transition is backed up at the path recorded in the approval section. Every backup hash matched its source before editing. Root research, adapters, diagnostics, Phase 1 fixtures/tests, and all engine modules other than `models.py` are outside the Step 3 touched-file boundary.

### TDD evidence

The ECC implementation delegate edited only the three application/test files in the Step 3 manifest. No concurrent writer or verifier ran.

#### RED

```powershell
python -m unittest discover -s tests -p "test_phase2_models.py" -v
```

- **Result:** Expected failure, exit code `1`.
- **Observed:** unittest loader failed to import the new contract test because `AggregatedGenerationCounts` did not yet exist in `engine.models`.
- **Production state:** `engine/models.py` was still byte-identical to its pre-step hash when RED was captured.

#### GREEN and focused compatibility

| Command | Result | Evidence |
|---|---|---|
| `python -m unittest discover -s tests -p "test_phase2_models.py" -v` | PASS | 9 tests |
| `python -m unittest discover -s tests -p "test_engine_boundaries.py" -v` | PASS | 6 tests |
| Fresh `engine.models` UI-import subprocess | PASS | No Streamlit, Tkinter, Plotly, or PyQt5 module loaded |

The tests prove the reviewed fixture hash, all approved alias literals, five distinct `ValueError` subclasses, ordered/frozen/required Phase 2 dataclass fields, complete annotations, absence of legacy tuple conversion, frozen rebinding, unchanged Phase 1 model contracts, and fresh-process UI independence. The fixture is static data with `generated_by_tests=false`; no generator exists.

`ScientificInvariantReport.expected` and `observed` use `Any` because the approved report fields can describe heterogeneous numeric, ordering, and schema observations. Field order and all other types are exact; no contract mutation was required.

### Universal verification

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1`.

| Command | Result | Evidence |
|---|---|---|
| `python -m unittest discover -s tests -p "test_*.py"` | PASS | 72 tests in 37.196 seconds |
| `python diagnose_category_tracking_web.py` | PASS | Original 17/17 checks |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | PASS | Original 17/17 checks |
| Engine forbidden-import assertion | PASS | No UI framework imported by `engine` |
| Frozen diagnostic/fixture/root hash audit | PASS | All Step 1 immutable values unchanged |
| Derived-bytecode audit | PASS | Zero `__pycache__` directories |

One UI-independence command was initially invoked from the workspace root and correctly failed with `ModuleNotFoundError: engine` because runtime imports are intentionally local to `final code/`. It was immediately rerun from the required working directory and passed. This was a verification-directory error, not an application failure or runtime root dependency.

### Post-change manifest

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/docs/phase_2_scientific_contract.md` | 52368 | `23f02c5f6a66ec9ff3386cdf13833e0b19324d036ede4ace2b6703fc5a4c71aa` |
| `final code/engine/models.py` | 7821 | `0766d663c383a36c55fd9ce245c9632d426a52b3c91a54104eaa858998fbdaaf` |
| `final code/tests/test_phase2_models.py` | 12727 | `6e786be208dde307c79c91221930596d7ac82dda590b32f127b92000b1380cea` |
| `final code/tests/fixtures/phase2_scientific_contract.json` | 6532 | `92a30801ef14f911ade2fcba75bb77a3bf2345540de1775e40cc49afb3b89f32` |

The execution log is excluded from its own embedded post-hash; its pre-completion-append hash was `017755546394aeed3620e986dd61e8a3199f3fb0d2c8120b3478cfccdd813d5b`.

### Exit criteria, rollback, and handoff

- All approved new multi-field results are named frozen dataclasses with no tuple boundary: PASS.
- Existing Phase 1 dataclass order, signatures, mutability, and conversions: unchanged.
- Static reviewed schema fixture and hardcoded hash: PASS.
- UI-independent imports and full compatibility baseline: PASS.
- **Plan mutations:** None.
- **Completed (UTC):** 2026-08-11T18:18:01.452Z.

Rollback restores only `engine/models.py` and this log from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-03-20260811T180610892Z\`, restores the approved contract only if rolling back the approval transition, and removes only the exact two new test/fixture paths after validating them under `final code/tests/`. No other file is a rollback target.

Step 4 receives the approved dataclasses, fixture hash, numeric kinds, canonical ordering, and complete schema contracts. Step 3 does not implement exact analysis, invariants, comparisons, or aggregated sampling.

---

## Step 4 — Build the authoritative exact-analysis surface

- **Status:** Complete
- **Started (UTC):** 2026-08-11T18:19:25.367Z
- **Preconditions:** Approved contract and Step 3 model/schema suite are green.
- **Execution:** Serial direct mode; one implementation writer; no Git.

### Pre-change touched-file manifest

| Path | Planned action | Existed | Bytes | SHA-256 | Backup/rollback |
|---|---|---|---:|---|---|
| `final code/engine/exact_analysis.py` | Create authoritative exact-analysis composition/query module | No | N/A | N/A | Remove exact new path |
| `final code/engine/category_analysis.py` | Extend only if a canonical derivation owner is required | Yes | 12228 | `90d0f9dbb0381aa5e08d25db5eb8e57c70f0cc04472456521733ee9c0a7a8a8d` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-04-20260811T181925101Z\category_analysis.py` |
| `final code/engine/summaries.py` | Extend only if a canonical summary owner is required | Yes | 11143 | `b036af3781e216af22423c3c60ce95d1c5be3741989d9d8aabd9131e3e4b5bed` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-04-20260811T181925101Z\summaries.py` |
| `final code/tests/test_exact_analysis.py` | Create focused RED/GREEN tests | No | N/A | N/A | Remove exact new path |
| `plans/phase-2-execution-log.md` | Append Step 4 evidence | Yes | 31159 | `a2d0b45b02c90f39c6c69c07d271b3afcdf9b97ad621179ad37e46f20b636474` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-04-20260811T181925101Z\phase-2-execution-log.md` |

Every backup hash matched its source. `exact_tracking.py` is a read-only oracle and is not a touched or rollback file. Root research, UI adapters, diagnostics, Phase 1 fixtures, Step 3 fixture, and other engine modules are outside this step.

### TDD and focused evidence

- **RED:** `python -m unittest discover -s tests -p "test_exact_analysis.py" -v` exited `1` with the intended `ModuleNotFoundError: No module named 'engine.exact_analysis'`; no production file existed.
- **GREEN:** the same command passed 13 tests.
- `test_exact_tracking.py`: 4/4 PASS.
- `test_category_analysis.py`: 6/6 PASS.
- `test_summaries.py`: 6/6 PASS.
- Fresh `engine.exact_analysis` import loaded no Streamlit, Tkinter, Plotly, or PyQt5 module.

The implementation adds all eight approved public functions, complete type hints, exact schemas/dtypes/RangeIndexes, eager population tables, named codon/AA/trait/population queries, requested-zero and typed-empty behavior, canonical category/codon/AA/stop ordering, exact provenance checks, and canonical convergence results. `run_exact_analysis` calls the unchanged `run_simulation` once; `build_exact_analysis` never calls it. No propagation algorithm or biological definition was copied.

### Universal verification

All Python commands ran serially from `final code/` with bytecode writing disabled.

| Command | Result | Evidence |
|---|---|---|
| Full unittest discovery | PASS | 85 tests in 38.779 seconds |
| `python diagnose_category_tracking_web.py` | PASS | 17/17 original checks |
| Frozen compatibility diagnostic | PASS | 17/17 original checks |
| Engine forbidden-import assertion | PASS | No UI framework imported |
| Immutable Phase 1 hashes | PASS | Diagnostics and fixtures unchanged |
| Bytecode audit | PASS | Zero `__pycache__` directories |

Independent source review found no UI import, tuple compatibility API, duplicated propagation loop, pandas sort/reorder of exact state, or root runtime import. The new table assembly consumes `ExactSimulationResult` in canonical start and existing insertion order. Existing `category_analysis.py` and `summaries.py` stayed byte-identical.

### Post-change manifest

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/exact_analysis.py` | 22381 | `425ce12385d6d582b03f5533abe7f8b6082cb50bd31be272ef63d84b9fe5dc05` |
| `final code/tests/test_exact_analysis.py` | 22016 | `c06803c2a904936a594b9569aa65d91526ab41637b56d8c676853f2794a18019` |
| `final code/engine/category_analysis.py` | 12228 | `90d0f9dbb0381aa5e08d25db5eb8e57c70f0cc04472456521733ee9c0a7a8a8d` — unchanged |
| `final code/engine/summaries.py` | 11143 | `b036af3781e216af22423c3c60ce95d1c5be3741989d9d8aabd9131e3e4b5bed` — unchanged |

The execution log pre-completion-append hash was `e92c4fbdd0482202abf0987f2fe48d89ebd7ac28fa799fc1aa5a2bd29847635d`.

### Exit, rollback, and handoff

- Exact authoritative surface complete and deterministic: PASS.
- Explicit sparse/unequal denominators and provenance rejection: PASS.
- Same-process Phase 1 exact/category/summary compatibility: PASS.
- **Plan mutations:** None.
- **Completed (UTC):** 2026-08-11T18:33:32.445Z.

Rollback removes only the exact new module/test after validating their paths and restores only the manifest-listed existing files/log from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-04-20260811T181925101Z\`. Step 5 receives the exact result object, formulas, schemas, provenance rules, and start-scope denominator mappings.

---

## Step 5 — Enforce exact scientific invariants

- **Status:** Complete
- **Started (UTC):** 2026-08-11T18:34:31.294Z
- **Execution:** Serial direct mode; no Git.

### Pre-change manifest

| Path | Action | Existed | Pre-change state | Rollback |
|---|---|---|---|---|
| `final code/engine/invariants.py` | Create non-mutating invariant validators | No | N/A | Remove exact new path |
| `final code/tests/test_scientific_invariants.py` | Create focused passing/corruption tests | No | N/A | Remove exact new path |
| `plans/phase-2-execution-log.md` | Append Step 5 evidence | Yes | 36198 bytes; `23674511ccfc8d3212681f181682299ac7c78cba505548812737be26cf6234a6` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-05-20260811T183431095Z\phase-2-execution-log.md` |

The log backup hash matched its source. Exact-analysis, biological, mutation, propagation, adapter, diagnostic, fixture, and root research files are read-only for Step 5.

### TDD, review, and verification evidence

- Initial RED: focused discovery exited `1` with missing `engine.invariants`.
- Adversarial follow-up RED: two added corruption cases exposed absent category-order and cumulative-stop-prefix checks; minimal enforcement was added.
- Final focused GREEN: 20/20 invariant tests in 21.600 seconds.
- Exact-analysis regression: 13/13 PASS.
- Fresh invariant-module UI boundary: PASS.

The validators return tuples of frozen `ScientificInvariantReport` values and raise `ScientificInvariantError` on the first failure with metric, scope, generation, expected, observed, and tolerance. Tests separately corrupt biology/order, mutation rows, schema/index/dtypes, generation rows, category/stop order, conservation, rollups, denominators, fractions, cumulative prefixes, convergence, and deterministic tables. Validation never repairs, clips, fills, renormalizes, reorders, or mutates inputs. Mutation rows retain caller-supplied probability semantics; no range, finiteness, or sum-to-one validation was added.

Universal verification from `final code/` with bytecode disabled:

| Check | Result |
|---|---|
| Full unittest discovery | PASS — 105 tests in 55.744 seconds |
| Final diagnostic | PASS — 17/17 |
| Frozen compatibility diagnostic | PASS — 17/17 |
| Engine UI-import boundary | PASS |
| Frozen hashes | PASS |
| `__pycache__` count | 0 |

Post-change artifacts:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/invariants.py` | 24924 | `6b3f4637b893fbd13511266039bd8ca445f4db1cce7de492cbd8b8c9bdb4df63` |
| `final code/tests/test_scientific_invariants.py` | 12800 | `04c8f4e2a242f82ce0eb820539becebb16beac33cb7ac832ded88d4e2ec8506d` |

The execution-log pre-completion hash was `ae45b366eabe334b2ffc090d7025375b5bf7ae0a856c32664e3fc9d8f75048e2`. **Plan mutations:** none. **Completed (UTC):** 2026-08-11T18:50:57.291Z.

Rollback removes only the two exact new paths and restores the log from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-05-20260811T183431095Z\phase-2-execution-log.md`. Step 6 receives the validated schemas, alignment keys, tolerance enforcement, and exact reference tables.

---

## Step 6 — Add typed directed exact comparisons

- **Status:** Complete
- **Started (UTC):** 2026-08-11T18:51:38.463Z
- **Execution:** Serial direct mode; no Git.

| Path | Action | Pre-state | Rollback |
|---|---|---|---|
| `final code/engine/comparisons.py` | Create approved numeric, convergence, and exact-sampled comparison functions | Absent | Remove exact new path |
| `final code/tests/test_comparisons.py` | Create focused contract tests | Absent | Remove exact new path |
| `plans/phase-2-execution-log.md` | Append evidence | 39351 bytes; `c23f990e1f57e7eabc6b77c44b54cd3902abb0daebeb920c88364ff2808a4b42` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-06-20260811T185138356Z\phase-2-execution-log.md` |

All providers, schemas, fixtures, UI/compatibility files, root research, and Git metadata are read-only for this step.

### Evidence and handoff

- RED: focused discovery exited `1` because `engine.comparisons` did not exist.
- GREEN: 10/10 comparison tests in 0.504 seconds.
- Invariant regression: 20/20 PASS in 26.012 seconds.
- Fresh UI-import boundary: PASS; `compare_exact_to_sampled` correctly remains absent until Step 8.
- Universal suite: PASS — 115 tests in 73.702 seconds.
- Both frozen diagnostics: PASS — 17/17 each.
- Immutable hashes, engine boundary, and zero-bytecode audit: PASS.

Numeric comparisons validate one canonical scenario per input, align by approved scientific keys, fill only approved sparse keys with `0.0`, preserve canonical row order, return nullable `pd.NA` relative deltas at zero baseline, and satisfy self/swap laws. Starting scope/key metadata is intentionally not an alignment key so different codons, amino acids, traits, or mutation settings can be compared. Convergence comparisons remain separate and require identical scope/key/basis/tolerance; nullable generations yield nullable deltas. Inputs are not mutated.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/comparisons.py` | 12658 | `560d948d0b5691cffff6f1114bc36d3219d556ed1ba3f45f7aa5008a4d3e300a` |
| `final code/tests/test_comparisons.py` | 19223 | `ff7f4ac6c3601c724cb4456e9f385bd7c8e463d5e6ee050398322bb0d0f8d605` |

Execution-log pre-completion hash: `86208ff5410aa265a5b60d5af401ce677b5b778b152ab33c8b0cb219e9f4a5d7`. **Plan mutations:** none. **Completed (UTC):** 2026-08-11T19:03:35.934Z.

Rollback removes only the two exact new paths and restores this log from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-06-20260811T185138356Z\phase-2-execution-log.md`. Step 7 receives the approved aggregate models independently; Step 8 receives these exact comparison contracts.

---

## Step 7 — Add the memory-safe aggregated sampled engine

- **Status:** In progress — TDD RED pending
- **Started (UTC):** 2026-08-11T19:17:16.921Z
- **Execution:** Serial direct mode; no Git.
- **Prior gates:** ECC Gate 1 and the Phase 2 Scientific Contract gate are approved. Blueprint Steps 1–6 are complete; Step 8 has not started.

### Pre-change revalidation

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1` before any Step 7 implementation or test file existed.

| Command/check | Result |
|---|---|
| Full unittest discovery | PASS — 115 tests in 56.116 seconds |
| `python diagnose_category_tracking_web.py` | PASS — 17/17 original checks |
| Frozen compatibility diagnostic | PASS — 17/17 original checks |
| Fresh engine forbidden-import assertion | PASS |

### Pre-change manifest and backup

| Path | Step 7 role | Existed | Bytes | SHA-256 | Rollback |
|---|---|---:|---:|---|---|
| `final code/engine/aggregated_tracking.py` | Create the aggregated sampled provider | No | N/A | N/A | Remove this exact new path after validating it |
| `final code/tests/test_aggregated_tracking.py` | Create focused RED/GREEN tests | No | N/A | N/A | Remove this exact new path after validating it |
| `plans/phase-2-execution-log.md` | Append Step 7 evidence | Yes | 42026 | `fcad197e7c5d495a6ceb40b04c8d5b459d0985da6f3410cd03a38d48d54992dd` | Restore the literal backup below |

The interrupted Step 7 preparation had already created the unique OS-temporary backup below. It was inspected before reuse and is byte/hash-identical to the current pre-Step 7 execution log:

- **Source:** `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\plans\phase-2-execution-log.md`
- **Backup:** `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-07-20260811T190418808Z\phase-2-execution-log.md`
- **Destination on rollback:** `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\plans\phase-2-execution-log.md`
- **Backup bytes/hash:** 42026 / `fcad197e7c5d495a6ceb40b04c8d5b459d0985da6f3410cd03a38d48d54992dd`

The detailed sampled oracle and reviewed inputs are read-only for Step 7:

| Read-only artifact | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/sampled_tracking.py` | 2614 | `b959ffad244d0ebba4f34a8d61e187b2020ab845edf835547d15c4cf16d0bbc6` |
| `final code/tests/test_sampled_tracking.py` | 4324 | `801735226f6aacdc7ccd436222d1339f0e091c3f05c9fa640b46ab640ee3eef2` |
| `final code/tests/fixtures/phase1_scientific_baseline.json` | 13552 | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` |
| `final code/tests/fixtures/phase1_streamlit_surface.json` | 7606 | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` |
| `final code/tests/fixtures/phase2_scientific_contract.json` | 6532 | `92a30801ef14f911ade2fcba75bb77a3bf2345540de1775e40cc49afb3b89f32` |

All three diagnostic copies are 11180 bytes with SHA-256 `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4`. Root research hashes remain `category_tracking.py` `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de` and `category_tracking_web.py` `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8`.

`sampled_tracking.py`, models, biological definitions, mutation mapping, compatibility/UI files, fixtures, diagnostics, root research files, and Git metadata are not Step 7 edit or rollback targets.

### TDD implementation evidence

- **RED:** `python -m unittest tests.test_aggregated_tracking` exited nonzero solely with the intended `ModuleNotFoundError: No module named 'engine.aggregated_tracking'`; the production module did not yet exist.
- **Initial GREEN:** the new focused suite passed 9/9 in 0.117 seconds.
- **Detailed sampled regression:** `python -m unittest discover -s tests -p "test_sampled_tracking.py" -v` passed 5/5 without changing the frozen provider or module-global RNG contract.
- **Fresh aggregated-provider UI boundary:** PASS with no Streamlit, Tkinter, Plotly, or PyQt5 import.

The provider implements the approved `run_aggregated_experiment(...) -> AggregatedSampledResult` surface with a required integer seed and local `random.Random(seed)`. It normalizes all 61 starts with `max(0, int(weight))`, iterates `VALID_CODONS` and copies in copy-major order, performs `randint(0, 2)` followed by `choices(keys, probabilities)` in substitution-row insertion order, stops immediately at the first stop codon, and retains only generation-bounded counters. Zero generations return an empty snapshot tuple, normalized initial final counters, and zero stopped copies. No detailed record, path, copy ID, final per-copy object, automatic mode switch, vectorized draw, or global RNG side effect exists.

### Detailed reduction, conservation, RNG, and memory evidence

The test-only canonical reducer seeds the frozen detailed provider, restores its prior global RNG state, and compares recursively against the aggregated result. Equality covers concrete types, values, and insertion/key order for every generation and final mapping: live codon, amino-acid, category, starting-codon and starting-trait counters; all nested current-codon-by-start counters; new stops by stop, start codon, and start trait; scalar totals; final counters; and all 61 canonical outer start keys.

Reviewed compact cases cover sparse, zero, negative, and fractional starts, multiple starts/traits, nonuniform mutation, zero generations, early stops, all three stop codons, no survivors, no starts, and consecutive calls. Every generation satisfies `total_live + cumulative_stops == total_start_count`; rollups agree; cumulative stops are monotonic; and a known generation-1 stop contributes zero live/new stops but one cumulative stop through generations 2–4. Same-seed calls are identical, permitted different seeds diverge, and module-global `random.getstate()` is unchanged.

The deterministic structural gate compares positive-generation runs with 1 and 10000 copies across four generations. Snapshot count depends only on generations; the canonical outer mapping remains exactly 61 keys; counters stay within 61 codons, 20 amino acids, five categories/traits, three stops, and at most `61 x 61` nested nonzero cells. Dataclass fields contain no per-copy collection. AST enforcement rejects loaded copy IDs, retained container literals/comprehensions, direct accumulator attribute/subscript assignment, per-copy mutator calls, and every augmented assignment except the nine approved bounded `state.<counter>[...] += 1` updates. Wall-clock and `tracemalloc` values are not acceptance assertions.

### Review findings and resolution

The first read-only review found three HIGH test-evidence gaps and two MEDIUM gaps: incomplete recursive insertion-order assertions, a zero-generation-only structural check, a weak per-copy-retention source guard, a single-generation early-stop assertion, and incomplete frozen dataclass-surface assertions. TDD remediation strengthened the test without changing production code. A second review found one remaining HIGH AST gap for attribute/non-subscript augmented assignment; a second focused patch restricted copy-loop mutation to the exact bounded Counter-update whitelist. Final read-only re-review returned **PASS** with no CRITICAL or HIGH findings.

One non-blocking MEDIUM hardening note remains: a future arbitrary helper call or unlisted container constructor could require extending the source guard. It exposes no current provider defect; the present copy loop conforms to the approved whitelist and runtime structural bounds.

### Final focused and universal verification

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1`.

| Command/check | Result |
|---|---|
| `python -m unittest discover -s tests -p "test_aggregated_tracking.py" -v` | PASS — 9/9 in 0.166 seconds |
| `python -m unittest discover -s tests -p "test_sampled_tracking.py" -v` | PASS — 5/5 in 0.005 seconds |
| `python -m unittest discover -s tests -p "test_*.py"` | PASS — 124 tests in 65.485 seconds |
| `python diagnose_category_tracking_web.py` | PASS — 17/17 original checks |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | PASS — 17/17 original checks |
| Fresh `engine`/aggregated forbidden-import assertion | PASS |
| Final-code import locality for `category_tracking`, `category_tracking_web`, and `engine` | PASS |
| Duplicate biology/simulation-owner search | PASS — biological tables only in `genetic_code.py`; one detailed and one aggregate provider |
| New-file UI/root/presentation/positional-API audit | PASS |
| Bytecode audit | PASS — zero `__pycache__` directories |
| Git validity check | Expected invalid state preserved — exit 128, not a Git repository |

The Streamlit warnings during bare diagnostic/test execution are the established non-failing baseline warnings.

### Immutable and post-change hashes

| Path | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `final code/engine/aggregated_tracking.py` | 8252 | `3413a7ea20ec0139492e12ae314d7e4679751ded0b3ce596ab465dbfa4d7b32e` | New Step 7 provider |
| `final code/tests/test_aggregated_tracking.py` | 22658 | `cc08ee183931ef88247e9870bce37b4ae7a1aee8b297d75705fa7746e0947ca4` | New Step 7 tests after review remediation |
| `final code/engine/sampled_tracking.py` | 2614 | `b959ffad244d0ebba4f34a8d61e187b2020ab845edf835547d15c4cf16d0bbc6` | Unchanged |
| `final code/tests/test_sampled_tracking.py` | 4324 | `801735226f6aacdc7ccd436222d1339f0e091c3f05c9fa640b46ab640ee3eef2` | Unchanged |
| `final code/tests/fixtures/phase1_scientific_baseline.json` | 13552 | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` | Unchanged |
| `final code/tests/fixtures/phase1_streamlit_surface.json` | 7606 | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` | Unchanged |
| `final code/tests/fixtures/phase2_scientific_contract.json` | 6532 | `92a30801ef14f911ade2fcba75bb77a3bf2345540de1775e40cc49afb3b89f32` | Unchanged |

All three diagnostic copies remain 11180 bytes and SHA-256 `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4`. Root research remains unchanged: `category_tracking.py` SHA-256 `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de`; `category_tracking_web.py` SHA-256 `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8`.

The execution log immediately before this completion append was 45455 bytes with SHA-256 `51403a13c76b1c26b1aaed307972156cc2bb608b39bff887ded38d268b86661e`.

### Exit, rollback, and Step 8 handoff

- Aggregated integer conservation at every generation: PASS.
- Detailed-record reduction equivalence, including nested order: PASS.
- Explicit-seed repeatability and global-RNG isolation: PASS.
- Structural memory independence from copy count: PASS.
- Frozen detailed sampled behavior and final RNG semantics: PASS.
- **Plan mutations:** None.
- **Completed (UTC):** 2026-08-11T19:40:46.921Z.

Rollback validates and removes only these exact new paths:

- `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\final code\engine\aggregated_tracking.py`
- `C:\Users\hatem\OneDrive\Desktop\Project for uri\visualize code\final code\tests\test_aggregated_tracking.py`

It then restores only `plans/phase-2-execution-log.md` from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-07-20260811T190418808Z\phase-2-execution-log.md` and reruns the Step 6 universal baseline. No recursive deletion or unrelated restore is authorized.

Step 8 receives the ordered `AggregatedGenerationCounts` snapshots, normalized 61-key start counts, exact detailed-reducer evidence, required local-seed semantics, conservation/rollup guarantees, and structural-memory bounds. The optional read-only ECC benchmark may run before Step 8, but it is not part of Step 7 and was not run here.

---

## Step 8 — Add aggregated metrics and exact-versus-sampled validation

- **Status:** In progress — Slice A TDD RED pending
- **Started (UTC):** 2026-08-11T20:06:47.782Z
- **Execution:** Serial direct mode; no Git.
- **Prior gates:** ECC Gate 1 and the Scientific Contract gate are approved. Blueprint Steps 1–7 are complete; the optional read-only Step 7 benchmark passed without changing files; Step 9 has not started.

### Pre-change revalidation

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1` before any Step 8 application or test edit.

| Command/check | Result |
|---|---|
| Full unittest discovery | PASS — 124 tests in 89.591 seconds |
| `python diagnose_category_tracking_web.py` | PASS — 17/17 original checks |
| Frozen compatibility diagnostic | PASS — 17/17 original checks |
| Fresh engine forbidden-import assertion | PASS |

### Pre-change manifest and unique backups

| Path | Step 8 role | Existed | Bytes | SHA-256 | Backup/rollback |
|---|---|---:|---:|---|---|
| `final code/engine/category_analysis.py` | Add aggregated category/fraction derivations | Yes | 12228 | `90d0f9dbb0381aa5e08d25db5eb8e57c70f0cc04472456521733ee9c0a7a8a8d` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-20260811T200647768Z\category_analysis.py` |
| `final code/engine/summaries.py` | Add aggregated survival/stop/codon/convergence derivations | Yes | 11143 | `b036af3781e216af22423c3c60ce95d1c5be3741989d9d8aabd9131e3e4b5bed` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-20260811T200647768Z\summaries.py` |
| `final code/engine/comparisons.py` | Add exact-versus-sampled Wilson/Bonferroni comparison | Yes | 12658 | `560d948d0b5691cffff6f1114bc36d3219d556ed1ba3f45f7aa5008a4d3e300a` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-20260811T200647768Z\comparisons.py` |
| `final code/tests/test_aggregated_analysis.py` | Create Slice A RED/GREEN tests | No | N/A | N/A | Remove only this exact validated new path |
| `final code/tests/test_statistical_convergence.py` | Create Slices B/C RED/GREEN and preregistered calibration tests | No | N/A | N/A | Remove only this exact validated new path |
| `plans/phase-2-execution-log.md` | Append Step 8 evidence | Yes | 53924 | `27f6beed9a9c334ea2dc4b85cf85adcac452037ca60accfed523f86d18d00d63` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-20260811T200647768Z\phase-2-execution-log.md` |

Every backup hash matched its source. Models, exact providers, both sampled providers, invariants, biological/mutation definitions, public exports, fixtures, diagnostics, compatibility/UI files, root research, and Git metadata are read-only and are not Step 8 rollback targets.

### Scientific-contract conflict — paused before Slice A RED

- **Detected (UTC):** 2026-08-11T20:10:21.092Z
- **Status:** PAUSED at the formal plan/contract mutation gate; explicit human approval required.
- **Implementation state:** No Step 8 production or test file was created or edited. The three Step 8 engine owners remain byte-identical to their pre-change hashes, and both planned new test paths remain absent.

The approved `AggregatedGenerationCounts` contract retains these separate marginals:

- `new_stops_by_stop_codon: Counter[str]`;
- `new_stops_by_start_codon: Counter[str]`;
- `new_stops_by_start_trait: Counter[str]`.

It does not retain the joint stop-codon-by-starting-codon distribution. Separate marginals cannot determine which starting codon produced `TAA`, `TAG`, or `TGA`. Therefore the approved Step 8 provider cannot scientifically produce either of these required outputs from `AggregatedSampledResult`:

1. `get_aggregated_stop_outcomes(...)` for `start_scope="codon"`, `"amino_acid"`, or `"trait"`, because each scope requires three per-stop new and cumulative rows;
2. `get_aggregated_codon_outcomes(...)` stop rows for a requested starting codon, because each `TAA`/`TAG`/`TGA` row requires the same joint counts.

The result does not retain the mutation matrix, paths, records, or per-copy stop histories. Reconstructing paths or rerunning sampling is explicitly prohibited and would not be a valid derivation. No deterministic transformation of the existing marginals can recover the missing joint distribution.

#### Recommended contract mutation

Add one bounded per-generation field to `AggregatedGenerationCounts`:

```python
new_stop_codon_by_start_codon: dict[str, Counter[str]]
```

The outer mapping has all 61 `VALID_CODONS` keys in canonical order; each inner Counter has at most the canonical stops `TAA`, `TAG`, and `TGA`. The maximum is `61 x 3` nonzero cells per generation, so the structural memory contract remains independent of copy count. This joint counter becomes the authoritative stop grouping; existing stop/start/trait marginals remain contract fields but are derived and cross-checked from it rather than serving as competing measurements. Starting-amino-acid and starting-trait stop outcomes derive by canonical rollup of the outer starting codons.

#### Compatibility and touched-file impact

- Phase 1 compatibility version `v1`, detailed sampled behavior, exact results, Streamlit, and Tkinter remain unchanged.
- The approved Phase 2 contract/result shape changes additively before public registration; record the contract as a reviewed `2.1` amendment.
- Reopen only the owning Phase 2 work before resuming Step 8:
  - Step 2 contract: `final code/docs/phase_2_scientific_contract.md`;
  - Step 3 model/schema: `final code/engine/models.py`, `final code/tests/test_phase2_models.py`, `final code/tests/fixtures/phase2_scientific_contract.json`;
  - Step 7 provider/tests: `final code/engine/aggregated_tracking.py`, `final code/tests/test_aggregated_tracking.py`;
  - Blueprint registration: `plans/phase-2-strengthen-computation.md`;
  - evidence: `plans/phase-2-execution-log.md`.
- All newly affected existing files require a fresh exact manifest and unique OS-temporary backups before edits. The current Step 8 backup does not authorize restoring or changing those additional files.
- The immutable Phase 1 fixtures and diagnostics remain untouched. The Phase 2 fixture may change only after the contract amendment is explicitly approved and must remain manually reviewed/static.

#### Alternative not recommended

Narrow Step 8 to population-only stop outcomes and omit per-start stop codon rows. This avoids a new retained joint counter but breaks the approved codon/amino-acid/trait and codon-outcome contracts and weakens the Phase 2 scientific surface.

No RED test was written because it would knowingly demand information that the approved provider cannot represent. Work remains stopped before Step 8 Slice A pending explicit selection and approval of the contract mutation or the narrower contract.

### Joint-stop contract mutation approved

- **Approval:** The user explicitly approved the recommended bounded `new_stop_codon_by_start_codon` amendment and authorized reopening its Step 2/3/7 owners through TDD, then resuming Step 8.
- **Mutation started (UTC):** 2026-08-11T20:16:26.969Z
- **Contract target:** Phase 2 `2.1-approved`; Phase 1 compatibility remains `v1`.
- **Execution:** Serial direct mode; no Git.

Fresh exact backups were created specifically for this expanded mutation boundary under:

`C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\mutation-joint-stop-20260811T201626954Z`

| Path | Bytes | SHA-256 | Backup |
|---|---:|---|---|
| `final code/docs/phase_2_scientific_contract.md` | 52368 | `23f02c5f6a66ec9ff3386cdf13833e0b19324d036ede4ace2b6703fc5a4c71aa` | `phase_2_scientific_contract.md` |
| `plans/phase-2-strengthen-computation.md` | 61196 | `eccff38c71aae379222243dc82ad13c047f8a1b174bc942ce6f722e0254254dc` | `phase-2-strengthen-computation.md` |
| `final code/engine/models.py` | 7821 | `0766d663c383a36c55fd9ce245c9632d426a52b3c91a54104eaa858998fbdaaf` | `models.py` |
| `final code/tests/test_phase2_models.py` | 12727 | `6e786be208dde307c79c91221930596d7ac82dda590b32f127b92000b1380cea` | `test_phase2_models.py` |
| `final code/tests/fixtures/phase2_scientific_contract.json` | 6532 | `92a30801ef14f911ade2fcba75bb77a3bf2345540de1775e40cc49afb3b89f32` | `phase2_scientific_contract.json` |
| `final code/engine/aggregated_tracking.py` | 8252 | `3413a7ea20ec0139492e12ae314d7e4679751ded0b3ce596ab465dbfa4d7b32e` | `aggregated_tracking.py` |
| `final code/tests/test_aggregated_tracking.py` | 22658 | `cc08ee183931ef88247e9870bce37b4ae7a1aee8b297d75705fa7746e0947ca4` | `test_aggregated_tracking.py` |
| `plans/phase-2-execution-log.md` | 60783 | `8a03fd1cc0ed7a61cbce66bda33e2d7788d11c67b7ef4098cb8a79ef58480f98` | `phase-2-execution-log.md` |

Every backup hash matched its source. The mutation will amend the contract/Blueprint first, then update the model/static fixture through RED/GREEN, then update the aggregate provider/reducer through RED/GREEN. No other file is authorized until the original Step 8 slices resume.

#### Approved mutation TDD and verification evidence

The Scientific Contract was amended first to `2.1-approved`, and the Blueprint now registers the bounded joint counter, its authoritative derivation hierarchy, detailed-reducer equality, and `61 x 3` structural bound.

- **Reopened Step 3 RED:** 9 model tests ran; exactly three intended assertions failed because the fixture still named `2.0-approved`, the field was absent at position 8, and its annotation was missing.
- **Reopened Step 3 GREEN:** model tests 9/9 PASS; engine boundaries 6/6 PASS.
- **Reopened Step 7 RED:** the 9-test aggregate suite produced nine intended missing-constructor-field failures plus one AST failure rejecting the old independent marginal increment.
- **Reopened Step 7 GREEN:** aggregate tests 9/9 PASS; detailed sampled tests 5/5 PASS; model tests 9/9 PASS; fresh aggregate-provider UI boundary PASS.

The aggregate provider now updates only `new_stop_codon_by_start_codon` on an early stop. Snapshot freezing canonicalizes all 61 outer keys and the `TAA`, `TAG`, `TGA` inner order, then derives the stop-codon, starting-codon, and starting-trait marginals and `new_stops` from that joint source. The test-only detailed reducer requires recursive value/type/insertion-order equality for every joint cell and marginal. Multiple starts, all three stops, conservation, RNG order, global-RNG isolation, and the `61 x 3` bound pass. No path/history is retained.

Universal mutation checkpoint from `final code/` with bytecode disabled:

| Check | Result |
|---|---|
| Full unittest discovery | PASS — 124 tests in 60.625 seconds |
| Final diagnostic | PASS — 17/17 |
| Frozen compatibility diagnostic | PASS — 17/17 |
| Detailed sampled compatibility | PASS — 5/5 focused |
| Fresh aggregate UI independence | PASS |

Post-mutation artifacts:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/docs/phase_2_scientific_contract.md` | 53213 | `d4f4de22fa50e512e11491dfb4f7a2f346d156f811bfca49f96ebd135201757b` |
| `plans/phase-2-strengthen-computation.md` | 61688 | `922b7dc417ea40d36f0f7995f9f3736f7644ef999722e3f0a42e4ee71702acaf` |
| `final code/engine/models.py` | 7880 | `2c60b1e205f215f73a5a3c33292fa99f4a378251541e7573147d749856f3e852` |
| `final code/tests/test_phase2_models.py` | 12842 | `01608f73e95fe2af217e56b1c47a288a326bedf7bad9e7f257e5e0d404d85995` |
| `final code/tests/fixtures/phase2_scientific_contract.json` | 6571 | `39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887` |
| `final code/engine/aggregated_tracking.py` | 8914 | `5effaa9431b69ccd240c88574f0e70d1b130cc8ec5174f3a830ded36a4899cec` |
| `final code/tests/test_aggregated_tracking.py` | 25862 | `2f527dca20479feb80fd630351fa80607cbd7879f2ffbecb9b3cb8c946c697dc` |

The execution log immediately before this evidence append was 62963 bytes with SHA-256 `120d5833a1c319b0c4a992a04d13f2a93fa1837eca94b29e43e90c753ed736f3`. **Plan/contract mutation:** approved and complete. **Completed (UTC):** 2026-08-11T20:27:25.016Z. Step 8 Slice A may now resume using the joint stop distribution without inference or resimulation.

### Step 8 Slice B touched-file boundary conflict

- **Recorded (UTC):** 2026-08-11T20:38:16.062Z
- **Status:** Blocked before Slice B RED; awaiting a narrow touched-file manifest amendment.
- **Completed work retained:** the approved joint-stop mutation and Step 8 Slice A remain complete. No Slice B production or test edit occurred.

The approved Step 8 API must add `compare_exact_to_sampled` to `final code/engine/comparisons.py`. However, the existing regression module `final code/tests/test_comparisons.py` contains a stale pre-Step-8 assertion:

- test name: `test_public_functions_are_typed_and_step8_api_is_absent`;
- assertion at line 125: `assertFalse(hasattr(comparisons, "compare_exact_to_sampled"))`.

That file is outside the currently approved Step 8 touched-file manifest, so implementing the required public API without amending the manifest would knowingly leave the universal suite failing. A repository-wide test search found no other stale Step 8 absence assertion. Legitimate unrelated assertions that result dataclasses do not expose legacy tuple conversion remain unchanged.

Current evidence:

| Path | State | Bytes | SHA-256 |
|---|---|---:|---|
| `final code/engine/comparisons.py` | unchanged/existing | 12658 | `560d948d0b5691cffff6f1114bc36d3219d556ed1ba3f45f7aa5008a4d3e300a` |
| `final code/tests/test_comparisons.py` | existing, outside current manifest | 19223 | `ff7f4ac6c3601c724cb4456e9f385bd7c8e463d5e6ee050398322bb0d0f8d605` |
| `final code/tests/test_statistical_convergence.py` | absent | — | — |

#### Recommended narrow manifest amendment

Add only `final code/tests/test_comparisons.py` to the Step 8 touched-file manifest. Before editing, record a fresh exact manifest entry and create a unique OS-temporary backup. Replace only the stale API-absence test name/assertion with positive typed-signature and approved-default coverage for `compare_exact_to_sampled`; preserve every existing numeric and convergence comparison assertion. Then resume Step 8 Slices B and C using strict RED → GREEN → REFACTOR.

This amendment does not change the Scientific Contract, Blueprint semantics, production scope, compatibility behavior, or frozen artifacts. It only updates an earlier phase-boundary assertion that conflicts with the already approved additive Step 8 API. No file will be edited under this amendment until explicit human approval is received.

### Step 8 narrow manifest amendment approved

- **Approval:** The user explicitly approved adding only `final code/tests/test_comparisons.py` to the Step 8 touched-file manifest and replacing only its stale Step 8 absence assertion with typed-signature and approved-default coverage for `compare_exact_to_sampled`.
- **Started (UTC):** 2026-08-11T20:41:36.478Z
- **Execution:** Serialized direct mode; no Git.
- **Scope:** The existing comparison assertions remain protected. This amendment does not alter the approved Scientific Contract or Blueprint semantics.

Fresh exact backups for the amended boundary were created under:

`C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-manifest-amendment-20260811T204136431Z`

| Path | Bytes | SHA-256 | Backup |
|---|---:|---|---|
| `final code/tests/test_comparisons.py` | 19223 | `ff7f4ac6c3601c724cb4456e9f385bd7c8e463d5e6ee050398322bb0d0f8d605` | `test_comparisons.py` (hash matched source) |
| `plans/phase-2-execution-log.md` | 68476 | `11e8d0e935fb47e552f5879e5354ae6a5b245dd4d2a66d9389f31207a140c9a8` | `phase-2-execution-log.md` (hash matched source) |

Rollback for this amendment restores only these exact existing paths from that directory. Step 8 Slices B and C may now resume under strict RED → GREEN → REFACTOR.

### Step 8 Slices B–C — Exact-versus-sampled statistics and preregistered calibration

- **Status:** Complete; stop before Step 9.
- **Completed (UTC):** 2026-08-11T20:48:56.8796599Z
- **Execution:** Serialized direct mode from `final code/` with `PYTHONDONTWRITEBYTECODE=1`; no Git and no full universal suite.
- **Authority:** Phase 2 Scientific Contract `2.1-approved`, including the fixed Wilson/Bonferroni formulas and preregistered seed/sample-size panel.
- **Scope:** Add the approved exact-versus-aggregated fraction comparison, deterministic statistical correctness tests, and scientific calibration evidence. Slice A files, frozen fixtures/diagnostics, sampled providers, exact providers, UI adapters, and root research were not edited.

#### Touched files

| Path | Action | Bytes | SHA-256 |
|---|---|---:|---|
| `final code/engine/comparisons.py` | Add `compare_exact_to_sampled` and its single Wilson/Bonferroni implementation | 21517 | `ecb1b1fb3589ad370c73d263c741115a2452288df314bfb0a972cb768a0d33ef` |
| `final code/tests/test_comparisons.py` | Replace only the stale Step-8 absence assertion with typed/default public-API coverage | 20067 | `504ff4cb13822cbf63b89649756f8ea91eaeb797ec6ccaeda3d58c9200fa14b3` |
| `final code/tests/test_statistical_convergence.py` | New deterministic correctness and preregistered calibration tests | 19452 | `46c7a5fbaaa2b1fcf167f5423f2ff011c74083c66e5c60acfeefcb3649371d91` |
| `plans/phase-2-execution-log.md` | Append this evidence | pre-append 69777 | pre-append `1730a2559f96a330bd8744b3237c2a41b8cbd932e625cbdda6ccef29a8d12f32` |

The pre-existing Step 8 backup for `comparisons.py` remains at `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-20260811T200647768Z\comparisons.py`. The manifest-amendment backup for `test_comparisons.py` and the log remains at `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-08-manifest-amendment-20260811T204136431Z`. The new statistical test did not exist before Step 8; rollback may remove only that exact validated path. No recursive restore or removal is authorized.

#### RED evidence

```powershell
python -m unittest tests.test_statistical_convergence
```

- **Result:** Intended RED, exit code `1`.
- **Observed:** one loader error because `engine.comparisons.compare_exact_to_sampled` did not yet exist. No unrelated failure occurred.

#### GREEN and regression evidence

All commands below ran with bytecode writing disabled.

| Command | Result |
|---|---|
| `python -m unittest tests.test_statistical_convergence` | PASS — 5/5 in 12.583 seconds |
| `python -m unittest tests.test_comparisons` | PASS — 10/10 in 0.221 seconds |
| `python -m unittest tests.test_aggregated_analysis` | PASS — 9/9 in 1.062 seconds |
| `python -m unittest tests.test_scientific_invariants` | PASS — 20/20 in 17.397 seconds |
| `python -m unittest tests.test_aggregated_tracking` | PASS — 9/9 in 0.174 seconds |
| Fresh `engine.comparisons` forbidden-UI import assertion | PASS — exit code `0` |

#### Deterministic statistical evidence

- Only the approved fraction metrics are accepted: `category_fraction`, `survivor_fraction`, `stop_fraction`, and `cumulative_stop_fraction`. Other pairings raise `UnsupportedComparisonError`.
- Exact and sampled schemas, value kinds, scenarios, canonical key order, duplicate keys, and exact key alignment are validated before calculation.
- Sampled estimates use the canonical integer success and denominator columns: category numerator/live denominator; live or stopped/initial survival denominator; cumulative stop/initial denominator. Deliberately inconsistent displayed sampled fractions do not drive the calculation.
- The tests independently recompute `adjusted_alpha = familywise_alpha / family_size`, the two-sided `NormalDist` quantile, Wilson center/half-width, standard error, signed error, and absolute error and require exact floating-point equality for constructed `p=0`, `p=0.25`, and `p=1` rows.
- Single-row and multirow Bonferroni families pass. At sample size zero, exact/family metadata remains populated while sampled fraction, errors, standard error, bounds, and verdict use their approved nullable dtypes and `pd.NA` values.
- The output uses the exact 15-column contract, explicit dtypes, and zero-based `RangeIndex`; inputs remain unmodified.

#### Preregistered scientific calibration evidence

The focused suite executes the approved fixed panel without seed searching or parameter changes:

- seeds `(1729, 271828, 314159)`;
- equal copies per valid codon `(10, 100, 1000)`, totaling `(610, 6100, 61000)`;
- preset `(1/6, 2/3, 1/6)` mutation matrix;
- ten generations;
- population category fractions, survivor fractions, stop fractions, and cumulative `TAA`/`TAG`/`TGA` stop fractions.

All nine parameter cells repeat exactly for the same seed, conserve live plus cumulative stopped counts at every generation, and use the reviewed live or initial integer denominators. Family sizes are exactly 50 category rows, 10 survivor rows, 10 stop-fraction rows, and 30 cumulative-stop rows per run. Interval coverage is recorded over 300 aligned rows per sample size. The pooled RMSE for 1000 copies per codon is lower than the pooled RMSE for 10 copies per codon, satisfying the preregistered directional expectation. No statistical rejection occurred.

#### Slice B–C exit

- **Contract ambiguity/blocker:** None.
- **Dependencies added:** None; standard-library `math` and `statistics.NormalDist` only.
- **Phase 3 work:** None.
- **Step 9:** Not started.

### Reconstructed Step 8 Slice A evidence

This subsection was appended after Slices B–C to close a documentation omission. It is reconstructed only from the contemporaneous specialist handoff already retained by the parent orchestrator; Slice A commands were **not rerun** for this append, and no raw command output is invented here.

- Focused final Slice A suite: 9/9 PASS in 1.502 seconds.
- Recorded related regressions: category analysis 6/6 in 0.231 seconds; summaries 6/6 in 0.652 seconds; exact analysis 13/13 in 0.647 seconds; scientific invariants 20/20 in 25.689 seconds; aggregated tracking 9/9 in 0.285 seconds.
- Fresh `engine.category_analysis`/`engine.summaries` forbidden-UI import assertion: PASS.
- The Slice A RED was the intended missing aggregated category API import; the initial GREEN was 8/8 before the final fresh-import/no-rerun test hardening produced 9/9.

Contemporaneously recorded Slice A artifacts:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/tests/test_aggregated_analysis.py` | 19557 | `f4855cfb5573f25d275e2451db1f29524942f74a3fc3669c144d954ca3baaffe` |
| `final code/engine/category_analysis.py` | 15381 | `f2505d5bc0e1aae4c0c0bfade0df0e42d76faa4a8546f49f7f42698fa5a9719e` |
| `final code/engine/summaries.py` | 19897 | `d21d6fccde2b68aca6cdcf5e6831c49b784b4e99069345eb05122933570467e2` |

Slice A established the six typed aggregate query functions, four canonical start scopes, normalized integer denominators, typed empty/zero/no-survivor behavior, exact joint stop/codon outcomes, convergence statuses, detailed-record integer/order overlap, input nonmutation, no sampling rerun/path reconstruction, and UI-independent imports.

### Step 8 read-only review remediation

- **Status:** Complete; HIGH and MEDIUM findings resolved without changing the frozen panel, seeds, alpha, contract, Blueprint, Slice A, or frozen artifacts.
- **Completed (UTC):** 2026-08-11T21:01:25.2039523Z
- **Execution:** Serialized, bytecode disabled, no Git, no universal suite.

#### Review RED

```powershell
python -m unittest tests.test_statistical_convergence
```

- **Result:** Intended RED — 5 tests ran with four failures.
- **Cause:** The provider still accepted the wrong denominator scope for each approved fraction metric.
- **Unchanged-panel numeric output observed during RED:** pooled RMSE per codon-copy size was `10: 0.013886208648238856`, `100: 0.0042036797355381565`, `1000: 0.0014663744937501101`; every reported family/size coverage ratio was `1.0`.

#### Review GREEN and regressions

| Command | Result |
|---|---|
| `python -m unittest tests.test_statistical_convergence` | PASS — 5/5 in 12.592 seconds |
| `python -m unittest tests.test_comparisons` | PASS — 10/10 in 0.225 seconds |
| `python -m unittest tests.test_aggregated_analysis` | PASS — 9/9 in 1.170 seconds |
| `python -m unittest tests.test_scientific_invariants` | PASS — 20/20 in 19.084 seconds |
| `python -m unittest tests.test_aggregated_tracking` | PASS — 9/9 in 0.209 seconds |
| Fresh `engine.comparisons` forbidden-UI import assertion | PASS |

#### Numeric calibration report

The GREEN run emitted this deterministic reviewed report:

| Copies per codon | Total copies | Category coverage | Survivor coverage | Stop-fraction coverage | Cumulative-stop coverage | Pooled RMSE |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 610 | 1.0 | 1.0 | 1.0 | 1.0 | 0.013886208648238856 |
| 100 | 6100 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0042036797355381565 |
| 1000 | 61000 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0014663744937501101 |

Coverage is reported numerically per family/sample size with no acceptance threshold. The only preregistered statistical rejection gate is explicit and executable: pooled RMSE at 61000 total copies must be less than pooled RMSE at 610. The observed `0.0014663744937501101 < 0.013886208648238856`, so the gate passes. An unmet inequality raises the test message `Preregistered rejection: pooled RMSE at 61000 must improve over 610` and pauses scientific review; it does not alter seeds, alpha, sample sizes, or intervals.

#### Canonical denominator-scope resolution

`compare_exact_to_sampled` now requires the approved scientific meaning rather than arbitrary metadata:

- `category_fraction` → `live_population` because its raw sampled denominator is the live count for that generation;
- `survivor_fraction`, `stop_fraction`, and `cumulative_stop_fraction` → `population_initial` because their raw denominator is the fixed eligible initial population.

All four wrong pairings have focused negative tests and raise `MetricSchemaError` naming `denominator_scope`. Raw integer success and denominator columns remain authoritative; displayed fractions remain non-authoritative.

#### Review-remediation artifacts

| Path | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `final code/engine/comparisons.py` | 21742 | `f086d65b081cdf5141c4f0d803a1dc997538b89d2c94987e495ef0f3f8628f99` | Canonical scope validation added |
| `final code/tests/test_statistical_convergence.py` | 21809 | `1eb00c70c58f76f0cc332d488297ff0b7d9b22822fe8f336365d7765967fd6a0` | Numeric report and rejection test added |
| `final code/tests/test_comparisons.py` | 20067 | `504ff4cb13822cbf63b89649756f8ea91eaeb797ec6ccaeda3d58c9200fa14b3` | Unchanged during remediation |
| `plans/phase-2-execution-log.md` | pre-append 75344 | pre-append `dcce5bbf7abce680b0de1cec56e4d26f9981bd71b0fd9552ea51da454a77d36d` | This evidence append |

- **Remaining review findings:** None in the reopened Slices B–C scope.
- **Step 9:** Not started.

### Step 8 review-remediation continuation

- **Started/recorded (UTC):** 2026-08-11T21:11:08.5611087Z
- **Reason:** After resuming from interruption, the prior read-only review still had to be closed with an executable Wilson-interval rejection gate and updated post-change evidence.
- **Allowed manifest:** `final code/engine/comparisons.py`, `final code/tests/test_comparisons.py`, `final code/tests/test_statistical_convergence.py`, `plans/phase-2-execution-log.md`.
- **Actual code/test edit:** `final code/tests/test_statistical_convergence.py` only.
- **Production code edit:** None during this continuation.
- **Git:** Not used.

#### Continuation changes

- Strengthened the preregistered calibration test so every non-null Wilson `within_interval` verdict in the approved fixed panel must pass. A failing verdict now raises a preregistered rejection message and pauses scientific review.
- Added per-family coverage row counts to the emitted deterministic calibration report.
- Added a focused negative assertion that the ambiguous label `population_initial_or_live` is rejected for `category_fraction` with `MetricSchemaError`.
- Preserved the existing pooled-RMSE gate: the 61000-copy pooled sample must improve over the 610-copy pooled sample.

#### Continuation focused verification

| Command | Result |
|---|---|
| `python -m unittest discover -s tests -p "test_statistical_convergence.py" -v` | PASS — 5/5 in 12.670 seconds |
| `python -m unittest discover -s tests -p "test_comparisons.py" -v` | PASS — 10/10 in 0.243 seconds |
| `python -m unittest discover -s tests -p "test_aggregated_analysis.py" -v` | PASS — 9/9 in 1.956 seconds |
| `python -m unittest discover -s tests -p "test_scientific_invariants.py" -v` | PASS — 20/20 in 20.303 seconds |
| `python -m unittest discover -s tests -p "test_aggregated_tracking.py" -v` | PASS — 9/9 in 0.328 seconds |

#### Continuation calibration report

The focused statistical suite emitted:

```json
{"coverage_by_copies_per_codon": {"10": {"category_fraction": 1.0, "cumulative_stop_fraction": 1.0, "stop_fraction": 1.0, "survivor_fraction": 1.0}, "100": {"category_fraction": 1.0, "cumulative_stop_fraction": 1.0, "stop_fraction": 1.0, "survivor_fraction": 1.0}, "1000": {"category_fraction": 1.0, "cumulative_stop_fraction": 1.0, "stop_fraction": 1.0, "survivor_fraction": 1.0}}, "coverage_row_counts_by_copies_per_codon": {"10": {"category_fraction": 150, "cumulative_stop_fraction": 90, "stop_fraction": 30, "survivor_fraction": 30}, "100": {"category_fraction": 150, "cumulative_stop_fraction": 90, "stop_fraction": 30, "survivor_fraction": 30}, "1000": {"category_fraction": 150, "cumulative_stop_fraction": 90, "stop_fraction": 30, "survivor_fraction": 30}}, "pooled_rmse_by_copies_per_codon": {"10": 0.013886208648238856, "100": 0.0042036797355381565, "1000": 0.0014663744937501101}}
```

The executable rejection checks pass because every Wilson verdict is true and `0.0014663744937501101 < 0.013886208648238856`.

#### Continuation artifact hashes before full gate

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/comparisons.py` | 21742 | `f086d65b081cdf5141c4f0d803a1dc997538b89d2c94987e495ef0f3f8628f99` |
| `final code/tests/test_comparisons.py` | 20067 | `504ff4cb13822cbf63b89649756f8ea91eaeb797ec6ccaeda3d58c9200fa14b3` |
| `final code/tests/test_statistical_convergence.py` | 22853 | `8af3052b14548847bac18d61fa8976c7ad7e52bf5790006bd3df0cfb4ec057e4` |
| `plans/phase-2-execution-log.md` | pre-append 80902 | `c99cd14ef05d8ca6042081e9584fc523ae5c0cd535e2f6a268a9460789dd4f76` |

- **Remaining CRITICAL/HIGH review findings:** None known after continuation.
- **Step 9:** Not started.

### Step 8 final compatibility and boundary gate

- **Completed (UTC):** 2026-08-11T21:20:56.1451808Z
- **Execution mode:** Serialized direct mode with `PYTHONDONTWRITEBYTECODE=1`.
- **Git:** No Git commands, commits, branch changes, repairs, or repository metadata changes were performed.
- **Step 9:** Not started.

#### Final focused verification after positional-index cleanup

| Command | Result |
|---|---|
| `python -m unittest discover -s tests -p "test_comparisons.py" -v` | PASS — 10/10 in 0.319 seconds |
| `python -m unittest discover -s tests -p "test_statistical_convergence.py" -v` | PASS — 5/5 in 13.341 seconds |
| Step 8 positional-index audit for `engine/comparisons.py`, `engine/category_analysis.py`, and `engine/summaries.py` | PASS — no matches |

The final comparison cleanup replaced internal key/scenario tuple indexing with named unpacking/helpers and changed no scientific formulas, denominators, row order, RNG behavior, or public API.

#### Final universal verification

| Command | Result |
|---|---|
| `python -m unittest discover -s tests -p "test_*.py"` | PASS — 138 tests in 73.872 seconds |
| `python diagnose_category_tracking_web.py` | PASS — all 17 checks |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | PASS — all 17 checks |
| `python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"` | PASS |

The full suite emitted the deterministic preregistered calibration report:

```json
{"coverage_by_copies_per_codon": {"10": {"category_fraction": 1.0, "cumulative_stop_fraction": 1.0, "stop_fraction": 1.0, "survivor_fraction": 1.0}, "100": {"category_fraction": 1.0, "cumulative_stop_fraction": 1.0, "stop_fraction": 1.0, "survivor_fraction": 1.0}, "1000": {"category_fraction": 1.0, "cumulative_stop_fraction": 1.0, "stop_fraction": 1.0, "survivor_fraction": 1.0}}, "coverage_row_counts_by_copies_per_codon": {"10": {"category_fraction": 150, "cumulative_stop_fraction": 90, "stop_fraction": 30, "survivor_fraction": 30}, "100": {"category_fraction": 150, "cumulative_stop_fraction": 90, "stop_fraction": 30, "survivor_fraction": 30}, "1000": {"category_fraction": 150, "cumulative_stop_fraction": 90, "stop_fraction": 30, "survivor_fraction": 30}}, "pooled_rmse_by_copies_per_codon": {"10": 0.013886208648238856, "100": 0.0042036797355381565, "1000": 0.0014663744937501101}}
```

#### Final immutable hashes and locality evidence

| Path | SHA-256 |
|---|---|
| `diagnose_category_tracking_web.py` | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| `final code/diagnose_category_tracking_web.py` | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| `final code/tests/compat/diagnose_category_tracking_web_phase1_baseline.py` | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| `final code/tests/fixtures/phase1_scientific_baseline.json` | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` |
| `final code/tests/fixtures/phase1_streamlit_surface.json` | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` |
| `final code/tests/fixtures/phase2_scientific_contract.json` | `39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887` |
| `category_tracking.py` | `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de` |
| `category_tracking_web.py` | `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8` |

`category_tracking`, `category_tracking_web`, and `engine` resolved to:

- `final code/category_tracking.py`
- `final code/category_tracking_web.py`
- `final code/engine/__init__.py`

#### Final Step 8 changed artifacts

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/comparisons.py` | 22058 | `8bec3b065238ef25a320e4e68c676ba987c0e3e17aa06c16cea32bc7208895c2` |
| `final code/tests/test_comparisons.py` | 20067 | `504ff4cb13822cbf63b89649756f8ea91eaeb797ec6ccaeda3d58c9200fa14b3` |
| `final code/tests/test_statistical_convergence.py` | 22853 | `8af3052b14548847bac18d61fa8976c7ad7e52bf5790006bd3df0cfb4ec057e4` |
| `plans/phase-2-execution-log.md` | pre-final-append 84596 | `b866aea2a5ee60566d7dc3b37038fcac0e0d4bb5856bb7fa0b10a6d3adf2821c` |

#### Final boundary audits

- Engine UI/presentation audit: PASS — no `streamlit`, `tkinter`, `plotly`, `PyQt`, `HTML`, `CSS`, `ui_color`, or `color` matches in `final code/engine/*.py`.
- `__pycache__` audit under `final code/`: PASS — no directories found.
- Step 8 tuple-index audit for comparison consumers: PASS — no `\[[0-9]+\]` matches in `engine/comparisons.py`, `engine/category_analysis.py`, or `engine/summaries.py`.
- Duplicate biological table audit: PASS for codon tables and property labels; canonical stop-order constants remain local ordering declarations and do not duplicate the biological table.
- Root runtime import audit: PASS — runtime modules resolved under `final code/`.

#### Final Step 8 status

- Aggregate analysis surfaces, exact/scenario comparisons, exact-versus-sampled calibration, Wilson/Bonferroni statistics, coverage reporting, pooled RMSE reporting, canonical denominator-scope validation, UI-independent imports, and compatibility boundaries are complete.
- Read-only review CRITICAL/HIGH findings are resolved.
- No frozen fixtures, frozen diagnostics, root research files, Streamlit UI, Tkinter compatibility adapter, detailed sampled RNG behavior, or approved contract/Blueprint content changed during final remediation.
- **Handoff:** Step 8 is complete. Stop before Blueprint Step 9.

## Step 9 - Register public surface and adversarial review

### Step 9 start and pre-change manifest

- **Started (UTC):** 2026-08-12T08:31:01.327Z
- **Prior status:** Phase 2 Blueprint Steps 1-8 are complete and verified; Step 8 stopped before Step 9. The approved Phase 2 Scientific Contract is version 2.1-approved and includes the bounded `new_stop_codon_by_start_codon` field. ECC Gate 1 and the Scientific Contract gate are approved. Step 10 has not started.
- **Pre-edit baseline:** The Step 8 universal suite was rerun before Step 9 edits: 138 tests passed; `diagnose_category_tracking_web.py` passed all 17 checks; `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` passed all 17 checks; fresh `import engine` UI-independence check passed.
- **Execution mode:** Direct mode with invalid Git metadata; no Git action. Writes and verification remain serialized. Application artifacts remain under `final code/`.

| Path | Step 9 role | Existed | Bytes | SHA-256 | Backup/rollback |
|---|---|---:|---:|---|---|
| `final code/engine/__init__.py` | Register approved public Phase 2 engine surface | Yes | 187 | `708a4a68b62fe1c28706e9ca1746c3581624f7de2b9c7dd6702a7c34ad37edb8` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-09-20260812T083101327Z\__init__.py` |
| `final code/tests/test_phase2_boundaries.py` | New Step 9 public-surface and boundary tests | No | 0 | `ABSENT` | `N/A` |
| `plans/phase-2-execution-log.md` | Append Step 9 evidence | Yes | 90186 | `1476665decc39756bc73bada4f965a05032ce6ac24565522518960433f0e502c` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-09-20260812T083101327Z\phase-2-execution-log.md` |

Every existing backup hash matched its source. No Step 3-8 owner is authorized for modification during the initial Step 9 implementation; any CRITICAL/HIGH finding there is passed to Council rather than repaired in this invocation.

### Step 9 RED -> GREEN -> REFACTOR evidence

- **Style compliance:** Edits used `final code/engine/models.py`, `final code/engine/exact_analysis.py`, `final code/engine/aggregated_tracking.py`, `final code/tests/test_phase1_boundaries.py`, and `final code/tests/test_engine_boundaries.py` as golden exemplars. The edits avoided duplicated biological tables or algorithms, scientific formula/denominator changes, exact floating-point changes, detailed-sampled RNG changes, positional tuple APIs, wildcard exports, implementation-helper leakage, UI imports, root runtime imports, frozen fixture/diagnostic changes, Phase 3 work, and application files outside `final code/`.
- **RED command:** `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v`
- **RED result:** Exit code 1. After correcting the new test's overbroad non-contract assertions, the intended RED failure was missing Phase 2 public registration from `engine`: `run_exact_analysis`, `build_exact_analysis`, exact query functions, `run_aggregated_experiment`, aggregated query functions, comparison APIs, invariant validators, Phase 2 dataclasses, and approved engine errors were absent from `engine.__all__`/attributes.
- **GREEN implementation:** `final code/engine/__init__.py` now imports and exposes only approved high-level Phase 2 result models, engine errors, authoritative exact APIs, explicit aggregated sampled API, approved aggregated query functions, comparison APIs, and invariant validators. It does not export `run_simulation`, `run_experiment`, implementation helpers, schema internals, biological tables, UI adapters, or wildcard imports.
- **Focused GREEN command:** `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v`
- **Focused GREEN result:** Exit code 0; 10 tests passed in 16.034s.

### Step 9 focused and universal verification

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1`.

| Command | Exit code | Evidence |
|---|---:|---|
| `python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v` | 0 | 10 tests passed |
| `python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"` | 0 | Fresh `engine` import did not load forbidden UI modules |
| `python -m unittest discover -s tests -p "test_*.py"` | 0 | 148 tests passed in 92.574s; preregistered calibration coverage remained 1.0 for 10/100/1000 copies per codon and RMSE improved from 0.013886208648238856 to 0.0042036797355381565 to 0.0014663744937501101 |
| `python diagnose_category_tracking_web.py` | 0 | 17 PASS lines |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | 0 | 17 PASS lines |

### Step 9 boundary and immutable-artifact audits

- **Diagnostic hashes:** `final code/diagnose_category_tracking_web.py`, `final code/tests/compat/diagnose_category_tracking_web_phase1_baseline.py`, and root `diagnose_category_tracking_web.py` all remain `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4`.
- **Frozen fixture hashes:** `phase1_scientific_baseline.json` remains `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b`; `phase1_streamlit_surface.json` remains `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035`; `phase2_scientific_contract.json` remains `39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887`.
- **Root research hashes:** root `category_tracking.py` remains `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de`; root `category_tracking_web.py` remains `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8`.
- **Import locality:** `category_tracking`, `category_tracking_web`, and `engine` resolved under `final code/`.
- **Engine UI-token audit:** `streamlit`, `tkinter`, `plotly`, `PyQt5`, UI color literals, `background`, `color:`, `HTML`, and `CSS` each had 0 matches under `final code/engine`.
- **Single-source ownership:** `run_simulation` appears only in `engine/exact_tracking.py`; `run_experiment` appears only in `engine/sampled_tracking.py`; `run_aggregated_experiment` appears only in `engine/aggregated_tracking.py`; `CODON_TABLE`, `VALID_CODONS`, `STOP_CODONS`, and `PROPERTY_LABELS` appear only in `engine/genetic_code.py`.
- **Tuple-index audit:** no `\[[0-9]+\]` matches in the new comparison/analysis consumers `engine/comparisons.py`, `engine/category_analysis.py`, or `engine/summaries.py`.
- **Pycache audit:** no `__pycache__` directories were found under `final code/`.
- **Git:** no Git command was run and no Git metadata was modified.

### Step 9 post-change hashes before technical review

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/__init__.py` | 2584 | `46c4ca7f33daca707e666d98d6e6faafb262255ad8ef75def008b2f8678a` |
| `final code/tests/test_phase2_boundaries.py` | 12340 | `67ef2e6a46aa92d149f0cfc0a25875c1650efd0be347954bd2275284e8e6a4` |
| `plans/phase-2-execution-log.md` | 92122 | `a0925d5fa7672d13d18d7f37a1c23d9f156260ab238855c6328bdcf2f0051e3` |

Technical adversarial review starts after all implementation writes and verification commands have stopped.

### Step 9 strongest-model technical review

- **Review status:** Complete; read-only reviewer edited no files.
- **Council prerequisite recommendation:** READY.
- **CRITICAL/HIGH findings:** None confirmed.

| ID | Severity | Evidence | Affected file/symbol or contract | Owning Blueprint step | Consequence | Recommended disposition |
|---|---|---|---|---|---|---|
| P2-TR-01 | MEDIUM | `run_exact_analysis` validates `n_generations` with `isinstance(n_generations, int)`, so `True` is accepted and runs one generation; `get_exact_codon_outcomes` similarly accepts `generation=True`. Aggregated equivalents use exact-type integer validation. | `engine/exact_analysis.py::_validate_generation_count`, `engine/exact_analysis.py::get_exact_codon_outcomes`; Scientific Contract section 5.3 | Step 4 | A Boolean control value can silently produce generation-1 output instead of the contracted error. | Reopen Step 4 later to explicitly reject `bool` and add focused tests. Not a Step 9 Council prerequisite blocker. |
| P2-TR-02 | LOW | Canonical stop order is independently hard-coded as `("TAA", "TAG", "TGA")` in `exact_analysis.py`, `comparisons.py`, and `invariants.py`, while `genetic_code.py` is the declared biological source of truth. The Step 9 ownership test detects duplicate `STOP_CODONS =` assignments but not parallel order constants. | `engine/exact_analysis.py::CANONICAL_STOP_CODONS`, `engine/comparisons.py::CANONICAL_STOP_CODONS`, `engine/invariants.py::CANONICAL_STOP_CODONS`; single-source ownership contract | Step 9 boundary audit, with repairs belonging to Steps 4-6 | Current results are correct, but future stop-order changes could drift across formulas, schemas, and validators. | Centralize ordered stop constants in `genetic_code.py` or explicitly designate one shared owner later; strengthen the ownership test. |

The reviewer reported no confirmed deviations in formulas, denominators and zero cases, exact floating-point preservation, conservation, detailed and aggregated RNG behavior, detailed-reducer equivalence, schemas/order/empty results, Wilson/Bonferroni calculations, preregistered calibration, structural memory bounds, UI compatibility, import locality, public exports, or Phase 3 exclusion.

### Step 9 Council prerequisite gate

- Approved exports are registered in `engine/__init__.py`: PASS.
- `final code/tests/test_phase2_boundaries.py` exists and passes: PASS, 10 tests.
- Focused Step 9 verification passes: PASS.
- Universal verification passes: PASS, 148 tests.
- Both diagnostics pass all 17 checks: PASS.
- Immutable hashes pass: PASS.
- Strongest-model technical review covers the required scientific and compatibility areas: PASS.
- Technical findings have severity, evidence, owner, consequence, and disposition: PASS.

Council may be convened. Step 10 has not started.

### Step 9 Council outcome

## Council: Phase 2 Step 9 go/no-go

**Prerequisite status:** READY.

Evidence summary: approved exports are registered, `test_phase2_boundaries.py` exists and passes, focused Step 9 verification passed, universal verification passed with 148 tests, both diagnostics passed all 17 checks, immutable hashes passed, the strongest-model technical review covered the required scientific and compatibility areas, and every finding has severity/evidence/owner/consequence/disposition.

**Architect position:** PROCEED. The public Phase 2 surface is discoverable and owned by the correct modules, exact analysis remains the authoritative deterministic path, aggregated sampling remains explicit and experimental, full verification is green, and no CRITICAL/HIGH finding remains. Largest risk: P2-TR-01 could be forgotten unless carried forward as an explicit Step 4 follow-up.

**Skeptic position:** PROCEED, with explicit non-blocking follow-ups logged. Strongest concern: P2-TR-01 is a real contract-conformance gap and should not be blurred by Step 10 approval. Overlooked issue: Step 10 should check that documentation/UI wording keeps aggregated sampled mode clearly experimental.

**Pragmatist position:** PROCEED. The Medium bool issue is narrow and does not undermine Step 9 boundary readiness; user-facing compatibility evidence is strong. Largest risk: Step 10 may decide the bool contract gap deserves a stricter compatibility interpretation. Overlooked issue: repeated stop-order tuples could create future ambiguity, but current results are correct.

**Critic position:** PROCEED. The supplied evidence shows no unresolved CRITICAL/HIGH scientific, RNG, conservation, statistics, memory, import, compatibility, or scope violation. Largest risk: accepting `generation=True` silently interprets a boolean as generation 1. Overlooked issue: Step 10 should explicitly verify exact-versus-sampled wording, including around the joint stop counter.

#### Council findings

| ID | Severity | Evidence | Affected file or contract | Owning Blueprint step | Required action |
|---|---|---|---|---|---|
| P2-TR-01 | MEDIUM | `run_exact_analysis` and `get_exact_codon_outcomes` accept `True` because `bool` subclasses `int`; Scientific Contract section 5.3 says generation inputs are `int >= 0`. | `engine/exact_analysis.py`; Scientific Contract section 5.3 | Step 4 | Defer as a known Medium follow-up unless Step 10 elevates it; reopen Step 4 later to reject `bool` and add focused tests. |
| P2-TR-02 | LOW | Canonical stop order appears as repeated tuples in `exact_analysis.py`, `comparisons.py`, and `invariants.py`; current behavior is correct. | Stop-order ownership boundary | Step 9 audit, with repairs belonging to Steps 4-6 | Defer; centralize ordered stop ownership or explicitly document the shared owner and strengthen the boundary test. |

#### Council verdict

- **Decision:** PROCEED.
- **Consensus:** Unanimous.
- **Strongest dissent:** Skeptic and Critic emphasized that P2-TR-01 is a genuine contract conformance bug, even though not a Step 9 blocker.
- **Premise check:** No CRITICAL/HIGH finding remains; no contract conflict requires plan mutation; no Step 10 approval is implied.
- **Required repairs before Step 10:** None.
- **Deferred MEDIUM/LOW findings:** P2-TR-01 owned by Step 4; P2-TR-02 owned by Step 9 boundary audit / Steps 4-6.
- **Recommended next ECC action:** Resume `ecc:orch-add-feature` for Step 10 only after explicit human approval at the Compatibility/UI Approval Gate.

### Step 9 completion

- **Completed (UTC):** 2026-08-12T08:46:44.000Z
- **Status:** Blueprint Step 9 complete. Stop at the Step 10 Compatibility/UI Approval Gate.
- **Step 10:** Not started.
- **Gate 2:** Not reached.
- **Git:** No Git command was run and Git metadata was not modified.
- **Rollback:** Restore `final code/engine/__init__.py` from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-09-20260812T083101327Z\__init__.py`, remove only the exact new path `final code/tests/test_phase2_boundaries.py` after validating its absolute path if rolling back to the pre-Step-9 state, and restore the execution log from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-09-20260812T083101327Z\phase-2-execution-log.md`; then rerun the complete Step 8 baseline.

#### Final Step 9 touched-file manifest

| Path | Bytes | SHA-256 |
|---|---:|---|
| `final code/engine/__init__.py` | 2584 | `46c4ca7f33daca707e666d98d6e6faafb26226ba922e7f6b1d6f45c2860f9006` |
| `final code/tests/test_phase2_boundaries.py` | 12340 | `67ef2e6a46aa92d149f0cfc0a25875c1650efa16bf2d077182a6baa54b58f095` |
| `plans/phase-2-execution-log.md` before this final manifest append | 104492 | `0220b40fc4be0165ca66b151a19c68a2b1cdbe8be8ae258a7b99b906b117c3a4` |

---

## Step 10 - Compatibility/UI Approval Gate

### Step 10 start and pre-gate manifest

- **Started (UTC):** 2026-08-12T09:26:26.9915375Z
- **Prior status:** Phase 2 Blueprint Steps 1-9 are complete and verified. The Step 9 Council verdict is PROCEED. Step 10 had not previously been completed. Step 11 has not started and Gate 2 has not been reached.
- **Scope:** Validation gate only. No production code, tests, fixtures, documentation, configuration, or application files are authorized for modification. Browser and accessibility checks are read-only against the local Streamlit app.
- **Execution mode:** Direct mode with invalid Git metadata. No Git action is authorized. Commands run from `final code/` with `PYTHONDONTWRITEBYTECODE=1` where applicable.

| Path | Step 10 role | Existed | Bytes | SHA-256 | Backup/rollback |
|---|---|---:|---:|---|---|
| `plans/phase-2-execution-log.md` | Append Step 10 compatibility/UI gate evidence | Yes | 104963 | `8f7026bc0a8de9561ea0d51ca8a4ee451dc8e9e55eccfdb2f78adefd8de1cba3` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-10-20260812T092626946Z\phase-2-execution-log.md` |

The execution-log backup hash is `8f7026bc0a8de9561ea0d51ca8a4ee451dc8e9e55eccfdb2f78adefd8de1cba3`, matching the pre-change source. Rollback restores only this recorded log backup. No application file is a rollback target for Step 10 unless a later approved reopen step creates a separate manifest.

### Step 10 automated compatibility baseline

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1`.

| Command | Exit code | Evidence |
|---|---:|---|
| `python -m unittest discover -s tests -p "test_*.py"` | 0 | 148 tests passed in 88.802s before browser QA |
| `python diagnose_category_tracking_web.py` | 0 | 17 PASS lines |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | 0 | 17 PASS lines |
| `python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"` | 0 | Fresh `engine` import did not load forbidden UI modules |

The unittest run emitted the preregistered calibration report with coverage `1.0` for 10, 100, and 1000 copies per codon and pooled RMSE improving from `0.013886208648238856` to `0.0042036797355381565` to `0.0014663744937501101`. The documented bare-mode Streamlit cache and `ScriptRunContext` warnings appeared during tests/diagnostics and remained non-failing.

### Step 10 Streamlit startup

- **Command:** `python -m streamlit run category_tracking_web.py --server.headless true --server.port 8517 --browser.gatherUsageStats false`
- **Working directory:** `final code/`
- **Process:** Started successfully as PID `17800`
- **URL:** `http://localhost:8517`
- **Startup result:** Browser loaded `Codon Category Tracking Lab`; no visible traceback; application entry point resolved under `final code/`; visual theme loaded.
- **Termination:** `Stop-Process -Id 17800`; process stopped cleanly.

### Browser QA report

- **Skill:** `ecc:browser-qa`
- **Mode:** Read-only local browser QA against `http://localhost:8517`.
- **Viewport observed:** 1036 x 502.
- **Temporary screenshot:** `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-10-browser-qa.png`.
- **Smoke:** PASS. Page title was `Codon Category Tracking Lab`; sidebar controls and main content appeared; no visible traceback; no local network failures were observed in the listed requests.
- **Console:** PASS WITH NON-BLOCKING FINDINGS. Browser console reported Streamlit/theme warnings for `h2FontWeight: 650`, plus browser issues for unlabeled form fields and autocomplete attributes. These did not block app use and were observed in the existing Streamlit-rendered surface; no JavaScript exception blocked the page.
- **Interactions:** PASS. Verified Sampled copies, Exact probability, Compare both, Codon focus, Whole population, preset/user sections, selected-codon output, charts, Plotly controls, and data tables.
- **Invalid input:** PASS. Setting the user probability sum to `1.6667` produced the concise live error `Set A->T, A->G, and A->C so they add to 1.0. Current sum is 1.6667.` without a crash.
- **UI exposure:** PASS. No aggregated-mode widget or automatic threshold appeared. Exact and sampled labels remained visible as `Exact probability` and `Sampled copies`.
- **Verdict:** PASS WITH NON-BLOCKING FINDINGS.

### Accessibility report

- **Skill:** `ecc:accessibility`
- **Mode:** Read-only WCAG-oriented audit using the browser accessibility snapshot and keyboard probes. No automated axe run was available in the current tool surface, so this is not a claim of full WCAG conformance.
- **Labels and names:** PASS WITH NON-BLOCKING FINDINGS. Primary Streamlit controls exposed accessible names such as `Generations`, `Copies per codon`, `Sampling seed`, probability labels, radio labels, codon selectors, and chart toolbar button names. Browser-reported issues noted unlabeled form fields and autocomplete usage in generated Streamlit internals.
- **Keyboard:** PASS. Tab and Shift+Tab moved focus through the probability inputs; focus state was visible in the accessibility tree. No keyboard trap was observed in the tested path.
- **Error accessibility:** PASS. Invalid probability produced an `alert` with `aria-live="assertive"` and concise text.
- **Skip/focus support:** PASS. The `Skip to main content` link remained present.
- **Charts/tables:** PASS WITH NON-BLOCKING FINDINGS. Plotly toolbar controls and Streamlit data tables were present in the accessibility tree; chart data remains primarily visual, as in the frozen Streamlit surface.
- **Verdict:** PASS WITH NON-BLOCKING FINDINGS.

### Final Step 10 verification

After browser and accessibility checks, the Streamlit process was stopped and all final verification ran serially from `final code/`.

| Command | Exit code | Evidence |
|---|---:|---|
| `python -m unittest discover -s tests -p "test_*.py"` | 0 | 148 tests passed in 103.771s |
| `python diagnose_category_tracking_web.py` | 0 | 17 PASS lines |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | 0 | 17 PASS lines |
| `python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"` | 0 | Fresh `engine` import did not load forbidden UI modules |
| `python -c "import tkinter as tk; root=tk.Tk(); root.withdraw(); root.update_idletasks(); root.destroy(); print('TKINTER_SMOKE_PASS')"` | 0 | `TKINTER_SMOKE_PASS` |

### Final Step 10 immutable hashes and boundary evidence

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Root diagnostic | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| Final-code diagnostic | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| Frozen compatibility diagnostic | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| Phase 1 scientific fixture | 13552 | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` |
| Phase 1 Streamlit fixture | 7606 | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` |
| Phase 2 scientific contract fixture | 6571 | `39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887` |
| Root `category_tracking.py` | 346862 | `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de` |
| Root `category_tracking_web.py` | 63021 | `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8` |
| Phase 2 Blueprint | 61688 | `922b7dc417ea40d36f0f7995f9f3736f7644ef999722e3f0a42e4ee71702acaf` |
| Approved scientific contract | 53213 | `d4f4de22fa50e512e11491dfb4f7a2f346d156f811bfca49f96ebd135201757b` |

Additional boundary evidence:

- `category_tracking`, `category_tracking_web`, and `engine` resolved under `final code/`.
- Engine UI/presentation token audit found no matches for `streamlit`, `tkinter`, `plotly`, `PyQt5`, `HTML`, `CSS`, `color:`, or `background` in `final code/engine/*.py`.
- No `__pycache__` directories were found under `final code/`.
- `.git` still has no `HEAD` or `config`; no Git command was run and no Git metadata was modified.
- No production code, tests, fixtures, root research files, Blueprint, scientific contract, or configuration files were modified during Step 10.
- Step 11 did not start and Gate 2 was not reached.

### Step 10 findings

| ID | Severity | Evidence | Owner | Disposition |
|---|---|---|---|---|
| P2-UI-01 | LOW | Browser console reported Streamlit/theme warnings for `h2FontWeight: 650`; the app remained usable and tests/diagnostics passed. | Future UI/design cleanup | Defer; not a Step 10 blocker because frozen visual behavior is preserved. |
| P2-A11Y-01 | LOW | Browser issues reported unlabeled generated form fields and autocomplete attributes; primary controls still exposed accessible names in the a11y tree and the invalid-input error used an assertive live alert. | Future accessibility cleanup | Defer; not a Step 10 blocker because no Phase 2-introduced accessibility regression was confirmed. |

Previously deferred Step 9 findings remain non-blocking: P2-TR-01 (MEDIUM bool-as-int generation validation, Step 4 owner) and P2-TR-02 (LOW repeated canonical stop-order tuples, boundary/Steps 4-6 owner).

### Step 10 status and approval gate

- **Completed (UTC):** 2026-08-12T09:38:30Z
- **Status:** Step 10 compatibility/UI approval evidence is complete and ready for human approval.
- **Blockers:** None confirmed.
- **Rollback:** Restore only `plans/phase-2-execution-log.md` from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-10-20260812T092626946Z\phase-2-execution-log.md` if rolling back this gate record.
- **Step 11:** Not started.
- **Gate 2:** Not reached.
- **Git:** No Git action occurred.

Awaiting explicit human approval: `Do you approve Phase 2 Step 10 and authorize Step 11?`

---

## Step 11 - Final boundary audit, documentation, and registration

### Step 11 start and pre-change manifest

- **Started (UTC):** 2026-08-12T09:49:32.762Z
- **Approval:** Phase 2 Step 10 Compatibility/UI Approval Gate is explicitly approved by the user in the Step 11 prompt. Step 11 is authorized.
- **Prior status:** Phase 2 Steps 1-10 are complete. Step 11 had not previously started. Gate 2 has not been reached.
- **Pre-edit baseline:** From `final code/`, the full suite passed 148 tests; both frozen diagnostics passed all 17 checks; fresh `engine` UI-independence check passed.
- **Execution mode:** Direct mode. Git metadata is invalid and no Git action is authorized.

| Path | Step 11 role | Existed | Bytes | SHA-256 | Backup/rollback |
|---|---|---:|---:|---|---|
| `CLAUDE.md` | Root soft-hook and Phase 2 completion instructions | Yes | 7465 | `fb87fe4e8d34f55fbad15ec533ea823ccce41aab4e36fbbfae54d599246de6bc` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\CLAUDE.md` |
| `final code/CLAUDE.md` | Final-app soft-hook and Phase 2 completion instructions | Yes | 3893 | `7f629c34c3c56077fddf0568daedd83115f989f4a5a233d9da7220fe208ad8c6` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\final_code_CLAUDE.md` |
| `final code/README.md` | Final application Phase 2 runtime documentation | Yes | 3073 | `b561e8e9198d678a03ddf3b3f55ee6f7be9dcb075bd45282ab85fcfeb00183f6` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\final_code_README.md` |
| `final code/engine/README.md` | Engine Phase 2 scientific API documentation | Yes | 4090 | `fd7700ff1ee980d9b678277017e929d254f0643fec00b7d3bf8112354fe68cb2` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\final_code_engine_README.md` |
| `final code/tests/test_phase2_boundaries.py` | Non-weakening Step 11 documentation/boundary coverage | Yes | 12340 | `67ef2e6a46aa92d149f0cfc0a25875c1650efa16bf2d077182a6baa54b58f095` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\final_code_tests_test_phase2_boundaries.py` |
| `plans/phase-2-strengthen-computation.md` | Blueprint completion registration | Yes | 61688 | `922b7dc417ea40d36f0f7995f9f3736f7644ef999722e3f0a42e4ee71702acaf` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\plans_phase-2-strengthen-computation.md` |
| `plans/phase-2-execution-log.md` | Append Step 11 evidence and Gate 2 handoff | Yes | 114879 | `af1153bf58799d2b10d761169e56cdfac68848f0ad2b33a448721237892613f6` | `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\plans_phase-2-execution-log.md` |

Every existing backup hash matched its source. Rollback restores only the files listed in this manifest from the recorded backup directory.

### Step 11 TDD documentation registration

- **Style compliance:** Documentation and boundary-test edits used `final code/README.md`, `final code/engine/README.md`, `final code/tests/test_phase2_boundaries.py`, `final code/CLAUDE.md`, and root `CLAUDE.md` as golden exemplars. The edits avoided duplicated biological tables or algorithms, scientific/formula changes, RNG or float-order changes, UI imports in engine code, positional tuple APIs, frozen fixture/diagnostic changes, Phase 3 work, root runtime imports, and application files outside `final code/`.
- **RED command:** `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v`
- **RED result:** Exit code 1. The new Step 11 documentation-registration test failed for the intended reason: final app docs, engine docs, soft-hook instructions, and Blueprint status had not yet registered the completed Phase 2 exact/aggregated/comparison contracts and Gate 2 handoff state.
- **GREEN edits:** Updated final app README, engine README, root/final CLAUDE instructions, and Blueprint metadata. No production engine module, adapter, fixture, diagnostic, or root research file was modified.
- **Focused GREEN command:** `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v`
- **Focused GREEN result:** Exit code 0; 11 tests passed in 12.211s.

### Step 11 documentation and registration summary

- `final code/README.md` now identifies Phase 2 as the current self-contained application state, documents `run_exact_analysis`, `build_exact_analysis`, `run_aggregated_experiment`, exact-vs-sampled comparisons, denominator/zero behavior, and the frozen Streamlit labels `Sampled copies` and `Exact probability`.
- `final code/engine/README.md` now documents the authoritative exact surface, detailed sampled compatibility path, explicit aggregated sampled API, comparison models, Wilson/Bonferroni calibration, canonical table meanings, RNG separation, `new_stop_codon_by_start_codon`, and unavailable per-copy aggregate information.
- `final code/CLAUDE.md` and root `CLAUDE.md` now register Phase 2 completion rules: read `final code/.ai-style-rules.md` before application-code edits, keep `final code/` canonical, treat exact analysis as authoritative for new scientific callers, keep aggregated sampled mode engine-only unless a new approved Blueprint mutates that UI decision, and preserve Phase 2 contracts in later phases.
- `plans/phase-2-strengthen-computation.md` status is registered as `Complete` and records that Gate 2 handoff is ready after Step 10 approval and Step 11 evidence.

### Step 11 focused and universal verification

All commands ran serially from `final code/` with `PYTHONDONTWRITEBYTECODE=1`.

| Command | Exit code | Evidence |
|---|---:|---|
| `python -m unittest discover -s tests -p "test_phase2_boundaries.py" -v` | 0 | 11 tests passed |
| `python -m unittest discover -s tests -p "test_phase2_*.py" -v` | 0 | 20 tests passed |
| `python -m unittest discover -s tests -p "test_*.py"` | 0 | 149 tests passed in 84.972s |
| `python diagnose_category_tracking_web.py` | 0 | 17 PASS lines |
| `python -m tests.compat.diagnose_category_tracking_web_phase1_baseline` | 0 | 17 PASS lines |
| `python -c "import sys, engine; forbidden={'streamlit','tkinter','plotly','PyQt5'}; assert not forbidden.intersection(sys.modules)"` | 0 | Fresh `engine` import did not load forbidden UI modules |

The full suite emitted the preregistered calibration report with coverage `1.0` for 10, 100, and 1000 copies per codon and pooled RMSE improving from `0.013886208648238856` to `0.0042036797355381565` to `0.0014663744937501101`.

### Step 11 final boundary audits

| Audit | Result |
|---|---|
| Runtime import locality | PASS — `category_tracking`, `category_tracking_web`, and `engine` resolved under `final code/` |
| Engine UI/presentation tokens | PASS — no matches for `streamlit`, `tkinter`, `plotly`, `PyQt5`, `HTML`, `CSS`, `color:`, or `background` in `final code/engine/*.py` |
| Single biological owners | PASS — `CODON_TABLE`, `VALID_CODONS`, `STOP_CODONS`, and `PROPERTY_LABELS` are owned by `genetic_code.py` |
| Single algorithm owners | PASS — `run_simulation` is owned by `exact_tracking.py`; `run_experiment` by `sampled_tracking.py`; `run_aggregated_experiment` by `aggregated_tracking.py` |
| Positional tuple-index audit in new consumers | PASS — no `\[[0-9]+\]` matches in `engine/comparisons.py`, `engine/category_analysis.py`, or `engine/summaries.py` |
| Streamlit Phase 2 leakage audit | PASS — no `run_exact_analysis`, `run_aggregated_experiment`, `compare_exact_to_sampled`, or `new_stop_codon_by_start_codon` matches in `category_tracking_web.py` |
| Pycache audit | PASS — no `__pycache__` directories under `final code/` |
| Git metadata | PASS — `.git` exists but still has no `HEAD` or `config`; no Git command was run |

### Step 11 immutable hashes and changed-file manifest

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Root diagnostic | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| Final-code diagnostic | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| Frozen compatibility diagnostic | 11180 | `03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4` |
| Phase 1 scientific fixture | 13552 | `96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b` |
| Phase 1 Streamlit fixture | 7606 | `4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035` |
| Phase 2 scientific contract fixture | 6571 | `39e8387bd76c49ad426d6c336736c63540df4de0595eae921029e84bf8441887` |
| Root `category_tracking.py` | 346862 | `7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de` |
| Root `category_tracking_web.py` | 63021 | `eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8` |
| `final code/README.md` | 5292 | `24a66e43e70501af58e315b4efdea0c2dc39837db00590805e03077ab0e8bf19` |
| `final code/engine/README.md` | 7790 | `120127a30a9ad86471a3dbf2aa0406c9d0c493d03bf0f4f404fc471815d695d9` |
| `final code/CLAUDE.md` | 4721 | `e9865c193a5910bc12003f723c47821a585f9a7fd00850465ff063305d6f5c3a` |
| `CLAUDE.md` | 8047 | `74a28e4f1823aec6f4a7602bcc8fa8d0ae933e1c24ebab45415ae59af2a62bd0` |
| `final code/tests/test_phase2_boundaries.py` | 14342 | `00d6c73c691c84973034e00cb54859f43d4250a9f71f78bf33f83d4e31421723` |
| `plans/phase-2-strengthen-computation.md` | 61856 | `c7c209cdc15d598742be5f27ffcadcce5a533c241fc45c0c612947480c2dd02b` |

### Delivery gate

- **Skill:** `ecc:delivery-gate`
- **Disk:** WARNING, not blocking — free space was `38.34 GB`, below the 50 GB warning threshold but above the 15 GB critical block threshold.
- **Learning/session hygiene:** WARNING — the default `memory/` learning-library paths (`growth-log`, `decisions/log.md`, `output-index.md`, `ratings-tracker.md`, and `tooling_capabilities.md`) were absent. Step 11 did not create out-of-manifest memory files.
- **Rationalized skipped verification:** PASS — required focused, universal, diagnostic, import, hash, and boundary checks ran and passed.
- **Delivery-gate disposition:** PASS WITH WARNINGS for Gate 2 handoff. No critical delivery-gate blocker was present.

### Deferred findings and Gate 2 handoff

Deferred non-blocking findings remain:

- P2-TR-01 (MEDIUM): bool-as-int generation validation in exact analysis; owner Step 4 follow-up.
- P2-TR-02 (LOW): repeated canonical stop-order tuple declarations; owner Step 9 boundary / Steps 4-6 cleanup.
- P2-UI-01 (LOW): Streamlit/theme `h2FontWeight: 650` console warning; future UI/design cleanup.
- P2-A11Y-01 (LOW): browser-reported generated form label/autocomplete issues; future accessibility cleanup.

Proposed conventional commit messages if Git is later repaired and explicitly authorized:

- `feat(engine): add phase 2 authoritative exact and sampled aggregate contracts`
- `test(engine): cover phase 2 scientific invariants and public boundaries`
- `docs(engine): register phase 2 completion and gate 2 handoff`

Rollback restores the Step 11 manifest from `C:\Users\hatem\AppData\Local\Temp\phase2-strengthen-computation\step-11-20260812T094932762Z\` and reruns the Step 10 baseline. No production scientific code, frozen diagnostic, frozen fixture, root research application file, dependency, or Git metadata was modified.

- **Completed (UTC):** 2026-08-12T09:58:30Z
- **Status:** Phase 2 Blueprint Step 11 complete. Gate 2 handoff ready.
- **Phase 3:** Not started.
- **Gate 2:** Prepared as a handoff only; no commit performed.
- **Git:** No Git action occurred.
