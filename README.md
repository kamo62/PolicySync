# PolicySync

PolicySync is being developed as a specialist liability claims workspace for South African claims handlers, reviewers and team leads, starting with professional indemnity (PI). Its purpose is to help a team reconstruct a matter, understand what is supported or still disputed, track outstanding work and prepare reviewed handovers and insurer reports.

Status: runnable local foundation. Evidence intake, review, instructions, handover and reporting still need implementation. Synthetic data only.

## What the application is intended to do

The planned workspace will let a team:

- Create matters with insurer, handler and external source references.
- Preserve original evidence, replacement versions, SHA-256 hashes and confidentiality classifications without overwriting earlier documents.
- Build a chronology and proposed factual statements linked to precise evidence versions and source passages, with explicit human review before acceptance.
- Track parties, unresolved questions, missing evidence, tasks, deadlines and external instructions, distinguishing drafting, issuing, acknowledgement and response.
- Prepare versioned handover packs and reviewed insurer status reports that preserve uncertainties and exclude privileged or internal-only material from external output.
- Record who changed or approved what and why, and export a traceable local audit pack.

These workflows are the product direction, not a list of completed features. PolicySync supports professional judgement; it must not independently decide cover, liability, reserves, settlement or legal strategy, and it does not replace the insurer's authoritative claims system.

## Future CRM and other integrations

PolicySync is intended to connect to external CRM systems through optional, configurable adapters. Lark Base is the first planned CRM connection; the same boundary is intended to allow other CRM providers later without making the claims workspace depend on one vendor.

The initial CRM link will be limited to explicitly mapped organisation records and non-sensitive onboarding/business metadata. Claim files, claimant or insured identities, policy details, medical information, reserves and privileged commentary must not be sent to the CRM. CRM tasks or approvals will not replace PolicySync's own claims workflow and approval history.

Future insurer-system connections require separate authorisation, starting with controlled read-only imports rather than automatic write-back. No live CRM connector or insurer integration is implemented today. The local workflow must remain usable without a CRM, an AI provider or an external account; `CRM_PROVIDER=none` remains the default.

## Current capabilities and limits

- Local FastAPI application with a read-only synthetic matter list, JSON API, local assets and a demo banner.
- SQLAlchemy organisation/matter models, Alembic migrations and SQLite foreign-key, WAL and transaction configuration.
- Idempotent synthetic seed, locked dependencies, bundled Linux wheels and a CI definition.
- Business audit, optimistic concurrency, matter creation/editing and evidence uploads are not implemented. Existing `version` columns do not yet prevent conflicting updates.
- Source anchors, human review, instructions, handovers, insurer reports and audit exports remain outstanding. The single seed matter is not the PRD's three acceptance scenarios.

The [implementation plan](docs/implementation-plan.md) records delivery status and remaining work. This is a foundation for a synthetic POC, not a completed claims workflow or a system approved for customer information.

## Start offline

Target: Linux x86_64, CPython 3.12, glibc 2.28+. Python and its standard-library `venv` module must already be installed. Transfer the complete handoff archive, not the Mac virtual environment.

```sh
python3.12 -m scripts.install_offline
cp .env.example .env
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m scripts.seed_demo
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m scripts.run_demo
```

Open `http://127.0.0.1:8000`. The seed creates one clearly synthetic matter; the UI/API is read-only. `/healthz` checks the schema, `/docs` links to the local OpenAPI JSON. There are no CDN or external API requirements. Do not expose this local demo through a network or proxy.

The installer refuses to overwrite an existing `.venv`; reuse a matching prepared environment. The bundled wheels do not support macOS, Windows, ARM or Alpine/musl. Do not resolve or upgrade dependencies in an offline environment.

Commands use `.venv/bin/python -m` to select the project's interpreter and dependencies explicitly. Alternatively, run `source .venv/bin/activate` once, then use `pytest`, `ruff` and `alembic` directly. Project helpers still run as modules, for example `python -m scripts.seed_demo`, because they are not installed command-line tools.

## Project documents

- [Technical PRD v2.0](PolicySync_Technical_PRD_v2.0.md): supplied product baseline.
- [Implementation plan](docs/implementation-plan.md): canonical task tracker and acceptance gates.
- [Documentation index](docs/README.md), [offline dependency bundle](vendor/README.md), [contributing](CONTRIBUTING.md).

Agent instruction and handoff files are local-only and excluded from source exports and the offline dependency archive. Use this README and the implementation plan to continue from an exported copy.

## Connected development

For a connected maintainer preparing a separate environment only. Offline continuation uses the bundled installer above, not dependency resolution or downloads.

```sh
uv sync --locked --python 3.12
uv run alembic upgrade head
uv run python -m scripts.seed_demo
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run python -m scripts.run_demo
```

Python/FastAPI, SQLAlchemy 2.x, Alembic, SQLite and Jinja2 are configured. HTMX is vendored for future forms. PDF/multipart dependencies are bundled for the next steps. Lark and AI remain disabled. No database server, Docker, Node or paid service is needed.

## Verification and release status

The [implementation plan](docs/implementation-plan.md#offline-foundation-delivery-evidence-14-november-2026) records nine passing local macOS/Python 3.12 foundation tests and passing Ruff checks. Native Linux installation/runtime, remote CI and visual browser inspection are not yet verified. Passing foundation tests does not establish the PRD's P0 acceptance gates.

Initial development version: `0.1.0.dev0` in `pyproject.toml`; see [changelog](CHANGELOG.md). Public source: [kamo62/PolicySync](https://github.com/kamo62/PolicySync). No application release or deployment has been published. No root application licence has been selected; public visibility alone does not grant redistribution rights.

PolicySync must not independently decide cover, liability, reserves, settlement or legal strategy. Live customer claims require the PRD's P1 approvals and controls.
