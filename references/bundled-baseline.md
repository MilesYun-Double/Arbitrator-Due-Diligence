# V1 Bundled Capability Baseline — Issue #13

## Scope and task-owned run

Current baseline composes existing local synthetic HTML/text and digital-PDF collectors, their actual saved Evidence, Validator, Canonical Model, Markdown/HTML/PDF and PDF readback. It does not perform research or classify business claims. The smoke supplies fixed synthetic task assignments and copies only three explicitly named synthetic fixtures; it never substitutes the old prebuilt report Evidence/model.

`static_source.task_run_root(path, create=True)` creates a **new direct project child** named `.tmp-add-run-*` and its `synthetic-run.json` scope marker; it refuses existing roots. The marker is a scope declaration, not a security credential or proof that user content is non-sensitive. Caller authorization to use only task-owned synthetic inputs remains necessary. No root search or directory discovery occurs.

The four existing command-line entries accept optional `--run-root`. They recheck the root marker/path and constrain input/output to that root; the PDF renderer also constrains its runtime there. With no run root, the previous test fixture boundaries remain unchanged. Static source in this mode accepts local input only, not URLs. File extensions and size limits remain. `report.validate_inputs(..., run_root=...)` bounds actual snapshot paths before the existing Validator performs file/hash checks. It does not read Evidence source URL/local_path or expand snapshot notes; the PDF renderer checks the model without reopening source/snapshot paths.

Outside-project roots, nested roots, reports/.preview/credentials and other denied components, symlinks/junctions/reparse points and hard-linked files remain rejected by `scoped_path`. New output directories cannot overwrite existing data. These are application checks, not an OS sandbox; no concurrency/TOCTOU security guarantee or arbitrary-disk access is claimed. Failed runs retain task-owned partial results and explicit failure status.

## Actual smoke commands

```text
python -B -E -S tests/synthetic_chain.py --run-root .tmp-add-run-new
python -B -E -S tests/package_synthetic_smoke.py --output .tmp-package-new
```

The first smoke copies synthetic page.html, source.txt and digital.pdf into the new run, collects three Evidence Objects with saved snapshots, validates/merges their exact returned JSON, writes explicit task metadata, and invokes existing report and PDF entries on actual preceding outputs. MD/HTML from both entries must match. Evidence and limitations must remain unchanged; complete PDF text/page labels/fonts are read back. All collected Evidence IDs reach the same canonical model.

The package script uses an explicit file allowlist: current chain scripts and synthetic inputs, Schema/Snapshot Policy, this reference, pypdf, the ADD ReportLab runtime archive, required Pillow/charset-normalizer, unchanged Chinese font, licenses and provenance records. It excludes reports, .preview, task logs, original ReportLab wheel and DarkGarden. Nested ZIP/wheel inventory is checked with the existing closure checker. It relocates and invokes a fresh `-B -E -S` Python; product dependencies are loaded from authenticated package-local archives, never site-packages. All file-backed product module origins are recorded; neutral in-memory ReportLab configuration hooks have no file origin.

## Pillow finding: REQUIRED / PLATFORM_DEPENDENCY_CONFIRMED

An independent no-Pillow package excludes the Pillow archive and license. Its subprocess actively rejects every PIL import through a MetaPathFinder; it records attempted imports and confirms no PIL module loaded. Its test-only loader extracts/authenticates only non-Pillow archives and disables the same home hooks. It does not patch ReportLab code or supply fake PIL objects, and is not a product fallback.

The real chain reaches the current PDF renderer and fails at:

`render_pdf -> reportlab.pdfbase.pdfmetrics -> _fontdata -> rl_config -> reportlab.lib.utils:15 -> from PIL import Image`.

Some earlier pypdf optional PIL imports are also attempted/blocked; the retained trace shows the unhandled import on the required renderer path. The first package assertion incorrectly assumed exactly one attempted import; it was corrected to accept multiple blocked attempts, while still requiring that exact unhandled renderer failure and zero loaded PIL modules. The experiment is an expected failure, not a passing no-Pillow chain.

Therefore keep the existing Windows x64 / CPython 3.12 candidate, licenses and hashes unchanged. No Linux/macOS Pillow wheels, alternate renderer, upstream modification or new dependency. Ubuntu/macOS and Python3.11 remain UNKNOWN/not executed; the conditional authorization for cross-OS CI was not met. Future choices (requiring separate authorization) are retaining the platform closure or investigating an upstream-compatible no-image dependency change; neither is implemented here.

## Timing / limits

Each successful run records static HTML and text collection, PDF collection, merge/validation, report validation, Canonical Model, Markdown, HTML, PDF dependency load/render/write/readback and internal total. The package parent records fresh-process wall time. Input bytes/pages, Evidence count, output PDF bytes/pages, font and dependency sizes, ZIP and uncompressed package sizes are recorded. The original PDF entry regenerates MD/HTML from the saved canonical model; duplicate-format work and model checks remain included in total, not hidden. Stage subtotals are not a non-overlapping sum of total.

Fresh task runs unpack dependencies; the existing loader can reuse an explicitly selected runtime only after full archive/file integrity verification. No checks were removed for performance, and no cache service or daemon was added. This tiny local synthetic sample is not a prediction of real arbitrator research time, nor a product SLA. Input digital PDF is 3 pages including a blank page; blank-page limitations remain in Evidence and all reports.

This is a capability smoke package, not a final Skill release or a product support list. No real people, case materials, OCR, web/browser expansion, sampling, UI/database/backend or next phase are included. Wait for controller acceptance and independent review as directed.
