# Offline dependencies

Target: CPython 3.12, Linux x86_64, glibc 2.28 or newer (for example Ubuntu 20.04+).
Python itself and the standard-library `venv` module must already be available.
Alpine/musl, Windows and ARM targets are not supported by this bundle.

`wheels/linux-x86_64/` contains all 33 pinned runtime/development dependencies plus
the pip bootstrap wheel. `requirements-linux.txt` is a target-specific, hash-locked
export of `uv.lock`, with markers evaluated for Linux x86_64/Python 3.12. This
avoids the common error of omitting Linux-only dependencies while preparing on Mac.
The installer needs neither uv, system pip, ensurepip, a compiler nor an index.

`manifest.json` records SHA-256 for wheels, requirements, lock and HTMX assets.
The offline installer verifies it before creating `.venv`. These hashes detect
transfer corruption; they are not a signature from an independent trust source.

The dependency wheels retain upstream metadata/licences. Vendored
`app/static/vendor/htmx.min.js` is HTMX 2.0.11, downloaded with its licence from
the package URLs recorded in `scripts/prepare_offline.py`. It is reserved for
future forms; the current read-only page does not load JavaScript.

Refresh only on a connected maintainer machine after reviewing dependency changes:

```sh
uv lock
# Review/move the old wheel directory aside; the preparation command refuses a nonempty one.
uv run --with pip python -m scripts.prepare_offline
```

Never resolve or upgrade packages in the offline environment. New packages beyond
this bundle require a separate connected preparation and revalidation step.

Current official implementation references: [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/),
[SQLAlchemy SQLite transaction/foreign-key guidance](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html),
[Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html),
[local HTMX installation](https://htmx.org/docs/). These links are for connected
maintainers; the offline handoff includes working source examples and technical notes.
