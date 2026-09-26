# Authorized real research run (Issue #18)

This is a caller-authorized, task-owned scope contract, **not an OS permission or identity system**. Creating a marker does not establish source authenticity, identify a person, or grant research permission. The caller must already have authority for the exact task and files. Synthetic contracts and defaults remain separate and unchanged.

## Contract and path boundary

`scripts/research_run.py` creates only a **new direct child** of `PROJECT/reports/`, with `research-run.json`:

```json
{
  "scope": "ADD authorized research run",
  "version": 1,
  "authorized_inputs": [
    {"path": "ABSOLUTE_EXPLICIT_FILE", "sha256": "64_lowercase_hex_digits", "url": null}
  ]
}
```

An empty input list permits URL collection without authorizing any local import. The ordinary `scoped_path` still denies `reports`; only the real resolver and staging boundary can apply the narrow exception. Every collector/report input, output, metadata and runtime path is checked against the selected run. Parent traversal, hidden/denied components, symlinks, Windows junctions/reparse points and hard-linked files remain refused. Sibling runs cannot be sources or outputs. Existing runs, staged folders and report outputs are not overwritten.

Checks are local scope enforcement, not a sandbox against an adversarial process concurrently changing files or the authorization marker. Callers must protect the workspace with host permissions. Marker creation does not authenticate a human authorization decision.

## Local input staging

1. Explicitly declare each authorized absolute filename, expected SHA-256 and original URL (or null) in an authorization JSON under the ordinary allowed project path, e.g. `.tmp-research-control/authorization.json`. No directory scan or wildcard is supported.
2. `python -B scripts/research_run.py create reports/NEW_RUN --authorization .tmp-research-control/authorization.json`
3. `python -B scripts/research_run.py stage reports/NEW_RUN ABSOLUTE_FILE --sha256 EXPECTED_SHA256`

The exact path/hash pair must match the contract. Supported import locations are project `tests/fixtures/` (synthetic testing), explicitly declared legacy files under project `reports/` **outside any research run**, or explicitly declared files in the current run's `incoming/` folder. A caller may save an already authorized download to that declared incoming path before staging. Arbitrary external disk imports and imports from sibling research runs are refused; this version has no authorization-update API.

Staging reads at most 10 MiB + 1 byte, verifies the expected hash, and creates a new `inputs/<hash>-<filename>/<filename>` copy. `staging.json` records original path/URL, expected/actual hash, copy time and staged path. Collectors require that record, its contract binding and unchanged bytes. Copying proves byte identity only. Staged text/HTML/PDF must remain local and ignored by Git; do not publish real source content in issue comments.

## Caller Evidence metadata

Real collectors require `--metadata CURRENT_RUN/metadata.json`. This JSON has exactly these top-level fields:

`subject`, `evidence_type`, `claim`, `source`, `identity_resolution`, `quality`, `supports`, `context`, `limitations`, `uncertainty`, `human_review`.

Values follow the **unchanged** Evidence Schema. The caller supplies subject identity (including optional ID/institution/notes), source title/publisher/type/URL/dates, identity status, quality/provenance, support relevance/statement, context, limits, uncertainty and review state. `source.local_path` is forbidden in metadata and assigned by the collector. For a URL capture, metadata's source URL must equal the requested URL. Use null for unknown dates; never invent them. `tests/test_research_run.py:metadata()` is a complete fabricated example, not a real-person conclusion.

Collectors own `evidence_id` (CLI parameter), retrieval time/details, acquired local path, verified excerpt and locator, snapshot and hashes. Metadata is checked by the existing Validator before acquisition. No synthetic subject/default identity leaks into real Evidence. Successful capture preserves caller semantics; a failed real acquisition or excerpt check raises an error and creates no Evidence output. The caller must record the failure/coverage gap explicitly; the collector does not rewrite a claim or invent a new support relationship.

```text
python -B scripts/static_source.py STAGED_TEXT_OR_PUBLIC_URL --output CURRENT_RUN/static --run-root CURRENT_RUN --metadata CURRENT_RUN/metadata.json --evidence-id E-001 --excerpt EXACT_TEXT
python -B scripts/pdf_source.py STAGED_PDF --output CURRENT_RUN/pdf --run-root CURRENT_RUN --metadata CURRENT_RUN/metadata.json --evidence-id E-002 --excerpt EXACT_TEXT --page 107
```

Static real mode uses the existing public HTTP(S), robots, redirects, timeout, 1 MiB and encoding policy; it does not inherit cookies or proxy credentials. Local `.txt/.html/.htm` requires staging. Synthetic runs still refuse URLs. Real URL plumbing is covered with deterministic mocks, not a new search/browser system or live website acceptance.

## Bounded PDF handling

Synthetic mode retains the 100-page, all-page extraction behavior. Real mode retains fixed bundled pypdf 6.19.0/hash, 10 MiB maximum, strict parsing, encryption refusal and no OCR/global fallback. It accepts **at most 300 physical pages**, giving bounded headroom over the 151-page acceptance case, and extracts **only the one explicitly requested page**. Parsing still traverses the PDF page structure; selective extraction is not a CPU/memory sandbox for hostile PDFs.

Real `pages.json` is an object with `extraction_scope: requested_page_only`, total `page_count`, `extracted_pages`, and a one-element `pages` array. Snapshot L3 retains the full original PDF. Snapshot notes and timing also distinguish total pages from extracted pages; no full-document text coverage is implied. Page 107 of a 151-page **generated synthetic** PDF passes; 301-page, corrupt, encrypted and byte-limit cases fail. The real CIETAC file is only a local staging/hash acceptance case, not a committed fixture or hardcoded product allowlist.

## Same-run report chain and validation

```text
python -B scripts/report.py CURRENT_RUN/evidence.json CURRENT_RUN/task.json --output CURRENT_RUN/canonical --run-root CURRENT_RUN
python -B -E -S scripts/pdf_report.py CURRENT_RUN/canonical/report.json --output CURRENT_RUN/rendered --runtime CURRENT_RUN/.tmp-runtime --run-root CURRENT_RUN
```

Merged Evidence remains a caller-prepared array; task/module assignment rules are unchanged. Snapshot paths are bounded before Validator file reads. The renderer consumes the canonical model, never reopens `source.local_path` or source URLs. PDF runtime archives remain authenticated and within the same run. Canonical JSON/MD/HTML equality, full ordered PDF text readback, embedded fonts and page labels are checked in `tests/real_chain.py`. It uses fabricated identities and HTML plus a generated 151-page PDF, through actual subprocess CLIs with site packages disabled.

Regression entry points: `tests/test_research_run.py`, existing full unittest discovery, `tests/synthetic_chain.py`, `tests/package_synthetic_smoke.py`, `tests/package_pdf_smoke.py`. Synthetic compatibility and relocated packaging remain required; this repair is not evidence of a completed real due-diligence report or an independent reviewer PASS.
