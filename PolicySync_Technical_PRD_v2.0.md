# PolicySync — Technical Product Requirements Document

**Version:** 2.0 (consolidated implementation baseline)  
**Date:** 14 November 2026  
**Status:** Ready for a synthetic-data POC; NOT approved for live customer claims  
**Product:** Specialist liability claims orchestration for South African claims teams  
**Implementation baseline:** Python / FastAPI + SQLite + minimal server-rendered UI + optional Lark Base CRM  
**Owners:** Product/claims-domain lead and technical delivery lead; accountable claims SME to be appointed for design-partner validation

> **Important:** This document specifies the product to build. It does not claim that the POC has been implemented, that a claims professional has approved the rules, or that any specific insurer has authorised processing. Synthetic data is mandatory until the live-pilot gates are completed.

## 1. Executive decision and change record

**Decision.** Build a defensible, human-governed **specialist liability matter workspace**. Start with **professional indemnity (PI)** as the first configurable claim class. Its job is to reconstruct a complex matter, link events and assertions to original evidence, track external instructions and produce a reviewed insurer status/handover pack. It must not independently decide insurance cover, liability, settlement, repudiation, reserves, admissions or legal strategy.

**Technology.** The initial POC and ordinary local development must run on **SQLite**; no PostgreSQL, database server or paid cloud dependency is required. Use Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Jinja2 + HTMX, and a local evidence directory. Keep a PostgreSQL migration path, but do not require it for the POC. A single process plus optional local worker is sufficient.

**CRM.** Use **Lark Base Starter** for the venture's ordinary CRM (organisations, contacts, opportunities, commercial activities and client onboarding). Integrate through a configurable adapter; the claims workspace must work when Lark is not connected. Never place claim files, privileged legal content, medical records or coverage discussions into Lark by default. Lark is not a claims system of record.

**Source lineage.** This v2.0 consolidates *PolicySync PRD v1.4 (14 August 2026)* and *PolicySync Working PRD Addendum 0.1 (17 October 2026)*. It **supersedes only the technical architecture choices** (previously Java/Spring Boot, Flowable/Camel and PostgreSQL as the initial stack) and adds the Lark/SQLite decisions. Business, scope, professional-control, evidence and no-autonomous-decision boundaries continue to apply. Commercial assumptions from earlier drafts remain hypotheses.

| Decision | POC v2.0 | Later, only if justified |
|---|---|---|
| Primary datastore | SQLite file via SQLAlchemy, WAL mode, foreign keys ON | PostgreSQL, per-customer isolated environment |
| Application | Python FastAPI modular monolith | Same services, selectively extracted if necessary |
| UI | Jinja2 + HTMX + accessible CSS | Richer frontend only if users need it |
| Documents | Local private directory + metadata/hash in SQLite | Encrypted managed object storage |
| Workflow | Explicit persisted states, service functions and audit events | Dedicated case engine only if complexity warrants it |
| AI assistance | Disabled by default; deterministic seeded proposals | Provider-gated assistive extraction with reviewed source anchors |
| Internal CRM | Lark Base, optional adapter | Replace or extend by integration, not tight coupling |
| Core insurer integrations | Manual read-only CSV/file import | Authorised read-only APIs; write-back separately approved |
| Authentication | Single demo account / local development only | Federated SSO + MFA, per-role server-side authorization |

## 2. Product problem, buyer and non-goals

**Primary buyer hypothesis:** outsourced specialist claims administrators; secondary: insurer/UMA specialist claims operations teams. A narrow PI claim is the demonstration unit, not a generic insurer core or broker CRM.

**User jobs:** (1) a handler reopens a six-month-old matter and identifies what is known, disputed and missing; (2) a reviewer determines whether every reportable assertion is backed by a usable source; (3) a team lead knows which expert instruction has not been acknowledged and who owns the escalation; (4) an insurer receives a consistent report without exposing privileged internals; (5) a receiving handler acknowledges a versioned handover without pretending uncertainty is resolved.

**Not in POC:** policy administration, payments, claims reserving decisions, settlement approvals, policy binding, advice, direct marketing, full document search, customer portal, automated email/WhatsApp dispatch, production insurer connectors, automated policy interpretation or autonomous legal drafting. A core system remains authoritative for claim and reserve state.

**Value hypothesis to test:** measurably less **total** professional/admin time to reconstruct a matter and prepare a safe report, inclusive of review and corrections. The 30% reconstruction and 40% reporting reductions from v1.4 are pilot hypotheses, **not promises**.

## 3. Users, roles and authority boundaries

| Role | Principal work | May do | Cannot do by default |
|---|---|---|---|
| Handler | Intake, record facts, chase stakeholders | Create proposals, tasks and internal notes | Approve own material report claims where separation is required |
| Reviewer / qualified claims SME | Evidence support, chronology, issues | Accept/reject proposals, sign off factual content | Make insurer decisions without a recorded delegation |
| Claims lead | Workload, oversight and handover | Assign handlers, escalate, approve report release where delegated | Change insurer-core reserve merely via PolicySync |
| Client viewer / insurer contact | Review agreed status | View specifically published, non-privileged pack | View privileged work product or internal drafts |
| Auditor | Investigate lineage | Read authorised audit/export records | Edit claims evidence/history |
| Technical administrator | Deployment, user support | Manage configuration and technical health | Read tenant claim content by default |

**POC caveat:** a local single-user demo can simulate roles for walkthroughs, but role switching in a demo is **not secure authorisation**. Any live pilot needs real identities, server-side role and matter checks, conflict barriers, MFA, customer-approved delegations and tested isolation.

## 4. Release scope and gates

| Stage | Required capabilities | Exit gate |
|---|---|---|
| **P0 — synthetic POC** | PI matter creation; evidence intake/hash; source anchors; chronology proposals/review; issue register; instructions/tasks; handover; reviewed insurer report; audit export; optional Lark CRM link | Three scripted synthetic scenarios pass; no accepted unsupported material assertion; no privileged text leaks externally |
| **P1 — controlled design-partner pilot** | Isolated environment; real authz/MFA; encryption/backup/recovery; virus scanning; permitted processing; document retention/legal hold; customer-specific report template; operational metrics | Signed contract/DPA, security/privacy/privilege assessment, qualified claims SME approval and customer permission |
| **P2 — commercial MVP** | Robust import adapters, notifications, configuration packs, audit operations, admin/monitoring and external client reporting | Repeatable buyer value, supportable run cost and signed commercial terms |
| **Later** | Broker servicing/CRM, insurer core write-back, full case engine, portfolio analytics | Separate product and regulatory approvals |

## 5. End-to-end POC journey

1. **Create a synthetic PI matter**: record a claim reference, insurer, insured pseudonym, claims class, status, notification date, assigned handler and authoritative source-system reference where relevant.
2. **Register evidence**: upload PDF, DOCX, EML or TXT (limited formats in P0); save the original unchanged, compute SHA-256, classify `internal`, `external-shareable` or `privileged`, and record author/sender, received date and immutable version.
3. **Capture cited proposals**: user manually selects evidence passages or imports deterministic demo proposals. Each proposed event/assertion must reference a valid evidence version and precise page/paragraph/span; unsupported or conflicting proposals remain in review.
4. **Review chronology**: reviewer sees provenance, source excerpt, conflicting items and limitations. Accept, amend with reason or reject; approved timeline only contains signed-off entries. Source replacement creates a new version and flags dependent approved content as `needs_revalidation`.
5. **Manage parties, issues and external dependencies**: create questions without coverage conclusions; assign tasks and instructions, due dates, acknowledgements, delivery status, pending replies and escalations.
6. **Produce a handover**: generate a versioned pack containing approved chronology, unresolved issues, cited evidence gaps, next tasks, stakeholder commitments and recorded authority context. Receiver confirms the remaining uncertainties.
7. **Draft and review insurer report**: generate a deterministic template from approved facts and explicitly identified open items. A separate authoriser checks recipients, source support and privilege; publishing produces an immutable version (no actual sending in P0).
8. **Export an audit pack**: JSON/ZIP including matter snapshot, evidence hashes/index, source-anchor references, accepted/rejected decisions, drafts, approvals, task changes and chronological audit log, with visible limitation flags.

## 6. Functional requirements and acceptance criteria

| ID | Requirement | P0 acceptance (synthetic data) | Stage |
|---|---|---|---|
| FR-01 | Matter intake and external references | Create/edit matter metadata; duplicate external key flagged | P0 |
| FR-02 | Evidence originals and versions | Original stored, SHA-256 and metadata persisted; replace creates new version | P0 |
| FR-03 | Provenance and source anchors | Proposed fact links to existing evidence version and page/span | P0 |
| FR-04 | Claims chronology review | Accept/amend/reject with actor/time/reason; only approved events appear on report | P0 |
| FR-05 | Conflicts and missing evidence | Two contradictory dates remain unresolved and surfaced | P0 |
| FR-06 | Policy version and date basis | Store competing policy/version references; require professional review to mark applicability | P0 |
| FR-07 | Parties, issues and questions | Capture insured/claimant/attorney/expert roles and issue owners; no autonomous conclusion | P0 |
| FR-08 | Tasks/deadlines | Owner, due date, acknowledgement, response and escalation visible | P0 |
| FR-09 | External instructions | Draft/sent/acknowledged/responded/completed distinct; sending not inferred from drafting | P0 |
| FR-10 | Handover pack | Version, approved facts, disputes, next actions; receiving handler acknowledges uncertainties | P0 |
| FR-11 | Internal vs external views | Privileged evidence/notes never included in external template/export | P0 |
| FR-12 | Insurer report | Draft → review → approved → published; explicit release actor and version | P0 |
| FR-13 | Audit history | Append-only business events for edits, approvals, rejections and exports | P0 |
| FR-14 | Portability export | ZIP JSON + evidence-index manifest + hashes; P0 export is local-only | P0 |
| FR-15 | CRM linkage | Link customer organisation to optional Lark external ID; sync never carries claims content | P0 |
| FR-16 | Pilot instrumentation | Count corrections, reviewer time, handover/report time and errors | P0 |
| FR-17 | Access control/isolation | Real identities, least privilege, tenant isolation and privilege barriers | P1 |
| FR-18 | Retention, legal hold and secure deletion | Customer-approved policy and tested controls | P1 |
| FR-19 | Controlled source-system imports | Source IDs, idempotency, reconciliation and stale-snapshot labels | P1 |
| FR-20 | Financial and reserve event oversight | Read-only record of external reserve/cost state; change approvals require delegated authority | P1 |
| FR-21 | Communication approvals | Recipient checks, privilege check, send/receipt evidence and exceptions | P1 |
| FR-22 | Optional AI assistance | Bounded source-grounded extraction only, review, provider logging and failure fallback | P1 |

**Critical invariant:** A citation is only a pointer, not proof. A reviewer must explicitly mark material assertions as supported; a wrong-page anchor, ambiguous OCR or contradictory source blocks acceptance until resolved or labelled as disputed.

## 7. Architecture, repositories and developer experience

### 7.1 Logical architecture

```text
Browser (Jinja2 / HTMX, minimal CSS)
       |
FastAPI application (one process, per-request DB sessions)
       |
       +-- identity/demo guard + matter service
       +-- evidence service / local private file store
       +-- anchor & assertion review / conflict service
       +-- chronology and issue service
       +-- task & instruction service
       +-- report, handover and export service
       +-- append-only business audit service
       +-- optional Lark CRM adapter (outbound restricted fields)
       |
SQLAlchemy 2.x + Alembic
       |
SQLite `./var/policysync.db` (local only)
```

### 7.2 Repository layout

```text
policysync/
  pyproject.toml
  .env.example
  README.md
  alembic.ini
  migrations/
  app/
    main.py
    config.py
    db.py
    models/
    schemas/
    routers/          # html and /api/v1
    services/         # business rules; no HTTP imports
    adapters/lark/    # separate interface + stub/mock + client
    templates/        # Jinja2 + HTMX partials
    static/
  tests/
    unit/
    integration/
    acceptance/
    fixtures/synthetic/
  scripts/seed_demo.py
  var/                 # gitignored: sqlite, originals, exports
  docs/adr/
```

### 7.3 Local run contract

- `uv sync` or `pip install -e .[dev]` installs dependencies.
- `cp .env.example .env`; default `DATABASE_URL=sqlite:///./var/policysync.db` and `EVIDENCE_DIR=./var/evidence`.
- `alembic upgrade head` creates tables; `python scripts/seed_demo.py` loads **synthetic** cases.
- `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` launches the app; browser uses `http://127.0.0.1:8000`.
- `/docs` exposes OpenAPI during local development only; `/healthz` verifies DB connectivity and schema version.
- **No dependency on Docker, PostgreSQL, Lark, an LLM key or external API** to complete the seeded workflow.

## 8. SQLite design rules and PostgreSQL migration path

- SQLAlchemy 2.x ORM and Alembic are the **only supported schema access/upgrade path**. Use neutral types: UUIDs stored as strings, UTC timestamp fields, explicit booleans, decimal money stored as integral minor units + ISO currency, JSON as portable text/JSON type via ORM.
- Configure SQLite `PRAGMA foreign_keys=ON` on every connection and `journal_mode=WAL` for the local file. Set busy timeout; keep write transactions short. WAL does not make SQLite a multi-server or network-file-share database.
- Single machine, one local database file, one writer-intense process at a time. Do not claim tenant isolation or high availability from SQLite.
- Use `DATABASE_URL` and storage adapter interfaces rather than application-level raw SQL. Model migrations must include both `upgrade` and `downgrade` where safe, with data-preserving migration tests.
- Store originals outside public static paths. Atomic file-write then checksum/DB transaction reconciliation; orphan-file cleanup command must be safe and logged.
- Exclude DB and evidence folders from Git; development backup = quiesced consistent SQLite backup plus evidence directory and encryption-at-rest where feasible.
- At P1 migration: test all Alembic revisions and CRUD flows on PostgreSQL; replace SQLite-specific pragmas; validate UUID/JSON/date behaviour, isolation, concurrent review, export and rollback; introduce explicit per-customer deployment and secure object storage. Do not migrate real claims data until approved.

**SQLite caveats:** no production-grade concurrent workload guarantees; machine compromise exposes files; deletion is not a defensible retention/legal-hold facility; a shared filesystem is not a compliant multi-user pilot architecture.

## 9. Canonical data model

**Common columns:** `id` (UUID string), `created_at_utc`, `updated_at_utc`, `created_by`, `matter_id` where relevant and a monotonically incremented `version` for optimistic locking. All physical relationships use foreign keys where appropriate.

| Entity | Key fields and relationships | Invariants |
|---|---|---|
| `organisation` | id, display_name, commercial_crm_id, type | No claim content in CRM mapping |
| `matter` | id, external_claim_ref, insurer_org_id, insured_alias, class, state, handler, notification_date | External claim source ID unique per insurer/source |
| `party` / `matter_party` | id, matter_id, role, alias, contact_permission | Internal parties only; export sanitises personal fields |
| `evidence_item` | id, matter_id, kind, title, classification, origin, received_at | Stable identity across versions |
| `evidence_version` | id, evidence_item_id, version_no, sha256, storage_key, mime, source_ref, created_at | Immutable bytes and checksum; no overwrite |
| `source_anchor` | id, evidence_version_id, page, paragraph, start_offset, end_offset, excerpt | Version exists; exact quoted source validated where extractable |
| `assertion` | id, matter_id, text, claim_type, date_basis, state, citation_status | Proposal != approved fact; material approvals require anchors |
| `assertion_anchor` | assertion_id, source_anchor_id, support_type | Many-to-many, supports `supports` / `contradicts` |
| `chronology_event` | assertion_id, event_date, end_date, date_precision, status | Only reviewed events are publishable |
| `issue` | id, matter_id, owner, question, state, criticality | No model-issued coverage determination |
| `task` | id, issue_id, owner, due_at, status, escalation_level | Clear acknowledgement semantics |
| `instruction` | id, matter_id, party_id, task_id, sent_at, acknowledged_at, response_at, delivery_state | Draft/sent/acknowledged distinct; no automatic send in P0 |
| `report_version` | id, matter_id, audience, template_version, rendered_path, status, approved_by, published_at | Immutable published version, exclude privileged data |
| `handover_version` | id, matter_id, generated_at, receiver, acknowledged_at, limitations | Revision creates new version |
| `approval` | id, target_type/id, decision, reviewer, reason, context_hash, decided_at | Record acceptance and rejection, never delete |
| `business_event` | id, matter_id, actor, action, target, before_hash, after_hash, occurred_at, prev_event_hash, event_hash | Append-only audit chain detects simple tampering; not a substitute for WORM |
| `external_reference` | id, provider, external_id, local_type/id, last_synced_at | Unique provider/external ID; reconciliation errors visible |
| `metric_sample` | id, scenario, participant_ref, task_type, elapsed_seconds, corrections, remarks | Do not store claim content in analytics |

**Policy and date questions:** represent claims-made/occurrence basis, alleged event dates, notifications and policy endorsement versions as separate records or typed assertions. Never silently select the applicable version or calculate prescription/critical dates as an authoritative legal outcome.

## 10. State machines and business invariants

### 10.1 Matter lifecycle

`intake → active → awaiting_external → review_pending → reporting → active/closed` with reopening events. State changes require a recorded actor and reason. Closed does not delete evidence or history.

### 10.2 Assertion and chronology

`proposed → under_review → accepted | rejected | disputed`, with `accepted → needs_revalidation` if supporting evidence is superseded. Only an appropriately authorised reviewer can accept a material assertion. A reviewer can amend text only by creating a new revision preserving the earlier version and reason.

### 10.3 Report

`draft → review_pending → approved → published`, with `changes_requested` returning to draft. Publishing pins evidence/assertion versions, reviewer, template version, audience and hash. Any change after approval requires another review.

### 10.4 Instructions

`draft → issued → delivery_confirmed → acknowledged → responded → completed`. `failed_delivery` and `overdue` are independent alert dimensions, **not evidence** of acknowledgment or completion. In P0, issuing is a recorded simulation, never an actual outbound communication.

### 10.5 Handover

`draft → submitted → acknowledged`, with receiver and outstanding uncertainties; acceptance does not resolve an outstanding issue or create a new claims authority.

## 11. Evidence ingestion, classification and provenance

**P0 input:** PDF with extractable text, TXT and EML, plus manual snippet selection. DOCX ingestion may be included if processing is deterministic and safe. OCR is optional and must be labelled as potentially inaccurate. PDFs with scanned pages may have no extractable text, so the reviewer must supply a manually verified passage or keep the item unresolved.

**Process:** validate content-length and file type; reject executable or unexpected formats; stream bytes to private temporary file; compute SHA-256; store new immutable version; enqueue or run restricted text extraction; create anchor candidates; never run instructions embedded in documents. In a live pilot add AV scanning, resource limits, encrypted storage, quarantine, signed access URLs, privilege tagging and customer-approved deletion/retention.

**Anchor granularity:** minimum page number for PDFs, and optional character offsets + snippet/hash. Do not certify source support purely because text matches: the professional reviewer checks semantic meaning, context, OCR confidence and contradictory material. A later version invalidates affected accepted claims and draft packs for re-review.

**Classification:** `internal`, `external_shareable`, `privileged`, `sensitive_personal`; a document may have multiple flags, with deny-by-default external inclusion. P0 exports permit internal audit pack and explicitly approved external report only, never full evidence contents in a public link.

## 12. Issues, instructions and date management

- **Issues** carry question, priority, owner, missing evidence, relevant source anchors, status and an approved professional commentary field. A policy question can be open without a cover opinion.
- **Instruction** records recipient role, objective, linked issue, due date, proposed fee (where needed), acknowledgement and deliverable. UI shows `Unacknowledged`, `Awaiting response`, `Overdue` and `Completed` distinctly.
- **Critical dates** are stored with type (`operational`, `contractual`, `policy`, `potential_legal`), timezone/date basis, source and reviewer; legal/prescription status remains provisional until a qualified human confirms it. Do not generate a legally determinative date automatically.
- **External communication** for P0 uses simulated events; no outbound email integration or automated admission/acknowledgement. In P1 introduce recipient whitelisting, approved templates and send/delivery evidence before enabling dispatch.

## 13. Report and handover artefacts

**Insurer status report, minimum sections:** claim header; reporting period; state of investigation; **approved** key developments with numbered source references; disputed/unverified information; open policy/legal questions (without auto-decision); external instructions and pending deliverables; approaching deadlines; next actions and owner; report limitations; review/approval information.

**Handover pack, minimum sections:** matter overview; approved chronology; evidence inventory/version index; outstanding facts, contradictions and policy-version questions; stakeholders and commitments; task/instruction status and escalation; recorded authority context; next actions; receiver acknowledgement with date and caveats.

**Safety:** final external render uses an explicit `audience=insurer` allow-list, not a general page dump; it excludes privileged and internal-only notes by construction. Drafts are watermarked `NOT APPROVED`. The report cannot be published if any material assertion lacks an accepted anchor, if its evidence is stale, or if the reviewer has not approved the specific version. The renderer exposes unsupported/missing elements as exceptions rather than filling gaps with generated language.

## 14. Lark Base CRM boundary and integration

### 14.1 Purpose

Lark is **the venture's sales/relationship and internal operations workspace**, not the claims database, document vault, medical record store, legally privileged repository or authoritative insurer system. Start with the free/entry tier if permitted under current terms; verify records, API quotas, region, permissions, automation allowances and commercial plan pricing at onboarding. Avoid basing product correctness on free-tier features.

### 14.2 Suggested Base tables

| Base table | Fields | Data boundary |
|---|---|---|
| `Organisations` | CRM ID, trading name, segment, generic company contact, stage, owner | Business metadata only |
| `Contacts` | CRM ID, person, organisation, role, approved contact details, consent/marketing status | Business contact PII with permission controls |
| `Opportunities` | CRM ID, organisation, stage, scope, expected decision date, responsible person | Commercial opportunity, no claim allegations |
| `Activities` | CRM ID, opportunity, task, due date, owner, outcome | Sales and onboarding tasks, no claims specifics |
| `Engagements` | CRM ID, contracted organisation, service tier, onboarding stage, PolicySync organisation ID | Only non-sensitive cross-system reference |

### 14.3 Integration contract

- POC defaults `CRM_PROVIDER=none`. Stub adapter serves locally; optional live adapter uses Lark application credentials and Base APIs.
- **Initial sync direction:** manually initiated Lark organisation → PolicySync `organisation` link and non-sensitive engagement status only. No background bidirectional sync until permissions and idempotency tests pass.
- Canonical key: `external_reference(provider='lark', external_id=record_id)` unique; use a stable organisation UUID in PolicySync. Mapping is explicit, not inferred from customer name.
- Allowed payload: CRM organisation ID, normalised trading name, business segment, non-sensitive onboarding state. Disallowed: matter/claim IDs, claimant or insured identities, policy details, legal documents, privileged commentary, reserves, uploaded evidence and medical data.
- Use configured allow-list fields, redacted logs, narrow service permissions, encrypted credentials, API timeouts and retry/backoff with deduplication. If Lark fails, log a sync error and retain normal claims function.
- Do not invent claims identities in CRM. Any future direct contact/relationship synchronisation needs POPIA purpose, cross-border-transfer, operator-role and consent review.

### 14.4 What is deliberately outside Lark

Lark Tasks/Approvals do **not** become authoritative claim instruction status or approval evidence. Claim approval remains inside PolicySync's auditable state machine. Avoid duplicating sensitive audit or deadlines across platforms.

### 14.5 Technical research supplement (14 November 2026)

See [Lark integration technical notes](docs/lark-integration.md) for verified official SDK request contracts, pagination, authentication/access distinctions, proposed mapping and failure handling, and unresolved endpoint limits and tenant permissions. This supplement does not enable a live integration or alter the data boundary above. No live tenant/API validation has been performed.

## 15. API and minimal UI specification

**API prefix:** `/api/v1`; JSON schema through Pydantic. All POST/PATCH requests validate state and return structured error codes. Expected failures return 4xx; server errors do not expose file paths or sensitive data. P0 local endpoints may be unauthenticated only while bound to `127.0.0.1`; must be disabled for network exposure.

| Endpoint | Purpose | Notes |
|---|---|---|
| `GET /healthz` | Health and DB schema status | No sensitive detail |
| `GET /api/v1/matters` / `POST /api/v1/matters` | List/create | Filter, page, validate external refs |
| `GET /api/v1/matters/{id}` / `PATCH ...` | Matter detail/edit | Optimistic version field |
| `POST /api/v1/matters/{id}/evidence` | Upload evidence | File limit, classification, checksum |
| `GET /api/v1/matters/{id}/evidence` | Inventory | Original download separately gated |
| `POST /api/v1/matters/{id}/assertions` | Propose cited assertion | Requires exact source-anchor reference |
| `POST /api/v1/assertions/{id}/review` | Accept/reject/dispute | Actor, reason and version required |
| `GET /api/v1/matters/{id}/chronology` | Approved/proposed views | Distinct states |
| `POST /api/v1/matters/{id}/issues` | Create issue | No coverage recommendation |
| `POST /api/v1/matters/{id}/tasks` | Create task | Owner and due date |
| `POST /api/v1/matters/{id}/instructions` | Record instruction | P0 simulation, no email |
| `POST /api/v1/matters/{id}/handover` | Create versioned pack | Captures unresolved issues |
| `POST /api/v1/handovers/{id}/acknowledge` | Receiver acknowledgement | Cannot overwrite handover |
| `POST /api/v1/matters/{id}/reports` | Build draft report | Approved facts only |
| `POST /api/v1/reports/{id}/review` | Approve/request edits | Checks citations and audience |
| `POST /api/v1/reports/{id}/publish` | Pin approved version | No outbound send |
| `GET /api/v1/matters/{id}/audit-export` | Local audit ZIP download | Requires audit capability in P1 |
| `POST /api/v1/crm/lark/organisations/import` | Optional safe metadata import | Explicit field mapping, disabled by default |

**UI pages:** `/` list/search matters; `/matters/new` intake; `/matters/{id}` overview; tabbed Evidence, Chronology, Issues, Instructions/Tasks, Handover, Reports and Audit. A small administration panel shows CRM connection status, never credentials. Each proposal clearly displays `PROPOSED`, `DISPUTED`, `ACCEPTED` or `REVALIDATION REQUIRED`. Error pages are actionable, and the reviewer can always perform the basic workflow without AI.

## 16. AI assistance: intentionally optional

For P0, use manual entry and deterministic extraction/seed data; no hidden AI dependency. Later, expose an `ExtractionProvider` interface with `disabled`, `deterministic_demo` and `approved_vendor` implementations. Model output is strictly typed proposals, not saved facts. Record provider/model/version, prompt-template ID, source version IDs, request ID, token/latency/cost where permitted, failure and reviewer action. Never include prompt contents in ordinary analytics/logs.

Hard rules: retrieved documents are untrusted data; prompts cannot invoke email, database writes or external browsing; unsupported facts cannot be approved; a provider outage must leave documents and manual report generation usable; provider processing requires customer approval, data processing terms, privacy review, cost ceilings, timeouts and rate limits. Claim handling or a legal decision must never be presented as model output.

## 17. Audit, privacy, privilege and security

### 17.1 P0 safety controls

- BIND LOCALHOST ONLY; clearly mark `DEMO — SYNTHETIC DATA ONLY` on every page. Do not expose development server on public interfaces.
- Refuse production-looking sample data in seed scripts and keep file contents out of app logs.
- Generate integrity hashes for evidence and published artefacts; track an append-only event log with hash-chain links. Hash chains provide tamper *evidence*, not immutability against a privileged operator who controls the DB.
- Validate uploads by type, size and safe paths; keep originals outside `static/`; set CSRF defenses for HTML form POSTs and restrictive cookie settings where sessions are used.
- Secrets in `.env` excluded from version control; dependencies pinned/locked and scanned before distribution.

### 17.2 Mandatory P1 gates before real customer information

- Written controller/operator responsibility and contract with the buyer; lawful basis/purpose; POPIA risk assessment including cross-border processors and special personal information.
- Privilege ownership and classification policy from the customer's legal team; role/matter information barriers and independent access testing.
- SSO/MFA, session lifecycle, least privilege, non-bypassable server authz and an isolated deployment/data store per design partner.
- TLS, encryption at rest and key management; AV/quarantine, backup and restore test, retention/legal hold, secure export, breach notification procedure and threat model.
- Contractual rights to model processing and subprocessors; approved no-training/data-use controls where applicable.
- Independently reviewed claims handling/approval boundaries and any FSCA-related licencing/outsourcing obligations relevant to the actual operator.

**The POC is not represented as POPIA-compliant production software simply because the requirements are written here.**

## 18. Testing strategy and synthetic demonstration scenarios

### 18.1 Unit and integration tests

- ORM constraints, foreign keys and versioning; migration fresh install/re-upgrade; SQLite DB rollback; invariant that no later evidence version overwrites original bytes.
- Assertion approval rejects missing/wrong-version/missing-page anchors; privilege flag exclusion; reviewers cannot accidentally approve staled source; material revisions produce audit entries.
- Date parsing ambiguity and contradictory policy wording stays unresolved; claims-made/occurrence selection cannot happen automatically.
- Instruction status transitions; draft does not equal sent, sent does not equal acknowledged; overdue behaviour preserves status.
- Lark adapter mock confirms that prohibited fields never leave the boundary; 429/timeout and duplicate record handling do not block claim operations.
- External report excludes internal/privileged classifications and unapproved assertions; published report has immutable version/hash; audit export reconstructs review lineage.
- SQLite-to-Postgres contract tests planned for P1 (same core service operations).

### 18.2 Acceptance scenarios (all invented data)

| Scenario | Fixture | Demonstrated outcome | Failure signal |
|---|---|---|---|
| A. Handler handover | Six-month PI case; 12 documents; 7 verified events; 3 open issues; pending expert instruction | New handler reconstructs current state, acknowledges unresolved questions, gets next steps and references | Needs verbal explanation not in pack; uncited approved facts |
| B. Contradiction | Different event/notification dates in initial notice and later expert report; two policy versions | Both dates visible, one not silently selected, old approved draft invalidated on evidence version change | Unsupported determination published or old report silently reused |
| C. Overdue external instruction | Attorney/expert request with no acknowledgment, overdue report and escalation owner | Dashboard shows issued but unacknowledged, due date and escalation; draft status not misrepresented | System marks complete/acknowledged automatically |

### 18.3 Performance and human evaluation

Use timed, comparable tasks with design partners: baseline work using their existing toolset versus POC, including corrections and reviewer effort. Collect total minutes, unsupported accepted assertions, wrong-page citation rate, privilege leak count, missed dependencies, review/rework time and participant feedback. Report raw values, sample size and confounding factors; do not invent pilot gains from synthetic scenarios. Zero accepted unsupported material assertions and zero privileged external disclosures are **test gates**, not claims about all real-world performance.

## 19. Definition of done, acceptance gates and release checklist

**P0 definition of done:** all three synthetic scenarios are reproducible via one seed command; user can create a matter, upload a text/PDF source, propose+review a dated assertion with source anchor, record instructions, create/acknowledge a handover, create+approve+publish a safe insurer report and export a traceable audit pack; fresh SQLite migration works; unit/integration/acceptance tests pass; no Lark credentials required; documentation has exact local commands.

**No-go conditions:** accepted unsupported assertions, document versions overwritten, privileged content in insurer reports, simulated instruction treated as delivered, missing audit actor, production personal data used without signed safeguards, application required to call Lark or an LLM for ordinary workflow.

**Before external pilot:** authorisation; NDA/DPA and rights to matter records; information security/privacy/privilege design; clinician/claims SME on any medical malpractice variation; insurer-facing review of reporting; delivery and support owner; baseline measurement; secure deployment; backup/recovery exercise; cost/contract approval.

## 20. Backlog and implementation sequence

| Iteration | Engineering stories | Dependencies and done criteria |
|---|---|---|
| Sprint 0 — foundation | Repo, config, SQLite/Alembic, typed ORM, health, synthetic seed, CI, app shell | Local run from empty checkout |
| Sprint 1 — matter/evidence | Matter CRUD; evidence file storage, SHA-256/version/index; source anchor UI | Create matter and cite original document |
| Sprint 2 — chronology/issue | Proposals, reviewer state machine, conflict flags, issue list, audit | Accepted and rejected revisions traceable |
| Sprint 3 — dependencies/handover | Task/instruction tracking, overdue flags, versioned handover, acknowledgement | Scenario A and C pass |
| Sprint 4 — reporting/export | Safe report template, reviewer approval, versioned publication, ZIP audit | Scenario B and privilege test pass |
| Sprint 5 — optional CRM and hardening | Lark adapter stub/live metadata-only connection, forbidden-field tests, demo metrics, documentation | Offline claims still work; all P0 checks pass |

No feature requires a separately deployed workflow engine, queue broker, external OCR, insurer API or paid AI service for P0. Add those only against a measured bottleneck or an agreed pilot need.

## 21. Observability, cost and operational constraints

**POC logs:** correlation ID, route, status, latency, error class and actor pseudonym. Never log document contents, claim bodies, contact details or secrets. **Demo dashboard:** matter counts, open issues, overdue instructions and review backlog; metrics do not expose case-sensitive text. **Cost:** local SQLite and local files incur no database subscription; Lark optional; actual cloud/API costs are not assumed zero for later stages. Performance target is sensible interactive navigation (<2 seconds for common local operations with a small synthetic dataset), excluding large file processing; this must be measured rather than guaranteed.

## 22. Data ownership, portability and integration principles

PolicySync stores matter workflow data on behalf of an authorised customer; agreements determine legal responsibilities and data rights. Exports must include enough source metadata and signed-off artefacts for customer review outside the app. Do not insert writes into TIA, TCS BaNCS, Guidewire, Cardinal, Genasys or customer insurer platforms without separate permission, integration contracts and a transaction control design. If a source record is stale, label its timestamp and block overwriting an approved financial state. Lark business relationships do not substitute for insurer-authoritative reference data.

## 23. Open questions and explicit assumptions

1. **Domain:** PI is the POC claim class; specialist claims SME must confirm that the chosen synthetic fixtures and workflow represent reality.
2. **Buyer/workflow:** no verified design partner or purchasing commitment is assumed. Compare against customers' current tools before asserting differentiation.
3. **CRM:** Lark Base is an optional operations tool; exact tier limits, organisation region, API scopes and data-processing terms must be verified at actual signup.
4. **Identity:** P0 demo login is local only, not acceptable as pilot access control.
5. **Documents:** text-extractable PDF/TXT sufficient for first run; scanned PDFs require manual review and later OCR controls.
6. **Source anchors:** manual verification is mandatory; citation presence does not equal claim support.
7. **Integrations:** none are assumed to exist or be authorised; no insurer credentials in POC.
8. **Governance:** sister-led venture and MashDev technical-supplier model remain planning choices subject to professional, employer outside-interest and IP/funding agreements.
9. **Regulatory:** this is software for authorised operators; any rendering of regulated services requires separate legal/FSCA assessment.
10. **Pilot go/no-go:** security, privacy, privilege and commercial review will determine whether a live P1 is permissible.

## 24. Acceptance matrix: traceability to prior PRD

| Previous focus | Where addressed in v2.0 | Treatment |
|---|---|---|
| PRD v1.4 FR-01 to FR-05 (tenant, intake, model, evidence, chronology) | §§3, 6, 8–11 | Tenant security deferred to P1; evidence and chronology P0 |
| FR-06 to FR-11 (parties, issues, tasks, instructions, finance, communication) | §§6, 9, 12 | Operational core P0; financial authority and outbound communications P1 |
| FR-12 to FR-15 (AI, reporting, authority, audit) | §§10, 13, 16–17 | Human approved reporting/audit P0; AI optional and no autonomous decisions |
| FR-16 to FR-20 (retention, integration, configuration, analytics, export) | §§6, 14–17, 21–22 | Portability P0; secure retention and integration P1 |
| October: source/version correction | §§9–11, 18 | Stale/contradictory evidence invalidates accepted content |
| October: handover and expert continuity | §§5, 10, 13, 18 | Versioned pack and receiver acknowledgement |
| October: instruction state and privilege | §§10–13, 17 | Distinct sent/acknowledged; external allow-list |
| November: CRM and Python architecture | §§1, 7, 14–15 | Lark optional; Python/FastAPI core |
| November: SQLite for local POC | §§1, 7–9, 19–20 | Required; no PostgreSQL server needed |

## 25. References and document status

**Primary project sources:**

1. *PolicySync Product Requirements Document, version 1.4*, 14 August 2026. Existing project baseline and functional scope.
2. *PolicySync Working PRD Addendum 0.1*, 17 October 2026. Controlling clarifications on source support, handover, privilege, read-only imports, measurement and commercial validation.
3. *Business Plan — Women-led PolicySync / LegalOps venture, version 0.1*, October 2026. Commercial and supplier-governance background, not implementation acceptance.

**Implementation references to recheck when coding:** [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/), [Alembic](https://alembic.sqlalchemy.org/), [SQLite](https://sqlite.org/), [HTMX](https://htmx.org/), [Lark Open Platform](https://open.larksuite.com/), [POPIA](https://www.gov.za/documents/acts/protection-personal-information-act-4-2013-26-nov-2013), [FSCA](https://www.fsca.co.za/). API fields, pricing, hosting regions and privacy obligations must be verified against current official sources before live integration.

**Document disposition:** Complete technical implementation baseline for a *synthetic-data POC*. It replaces the previous proposed initial technology stack; it does not authorise production claims processing or override customer/regulatory decision rights.
