# Contributing

Read the README, PRD and current implementation plan before changing the project. Keep that plan as the single delivery tracker.

## Scope and data

- Use synthetic fixtures only. Never commit real claim data, credentials, evidence, SQLite files or generated report/export artefacts.
- Keep original evidence unchanged, business decisions explicit and audit history traceable.
- Keep the local demo on `127.0.0.1`. Demo role simulation does not establish secure authorisation.
- Keep Lark and AI optional and disabled by default. No outbound communications in P0.

## Changes and verification

Use focused branches for implementation. Preserve unrelated work and stage only task-owned paths. When publishing is authorised, use a normal ready-for-review PR.

Follow the PRD's Python/SQLite stack and repository layout. Dependencies are locked in `uv.lock` and exported with hashes. Offline work must use the bundled Linux wheels; do not add or upgrade dependencies without preparing a replacement bundle on a connected machine.

Run the smallest relevant checks and record actual results in the plan or PR. Documentation changes require link and source checks, not an application build. Run `.venv/bin/python -m pytest -q`, `.venv/bin/python -m ruff check .` and `.venv/bin/python -m ruff format --check .`. CI is defined in `.github/workflows/check.yml`; [the initial Linux run](https://github.com/kamo62/PolicySync/actions/runs/43577808396) passed offline installation, tests and Ruff.

Use `pyproject.toml` as the application version source and `CHANGELOG.md` for changes. The initial development version is `0.1.0.dev0`; no release is published. PRD version 2.0 is a document version, not an application release number.
