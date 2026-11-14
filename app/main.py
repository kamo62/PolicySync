from contextlib import asynccontextmanager
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import Settings
from app.db import make_engine
from app.services.matters import list_matters

ROOT = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=ROOT / "app/templates")


def create_app(settings: Settings | None = None):
    settings = settings or Settings()
    engine = make_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    # Swagger's default HTML uses a CDN; serve a local schema page instead.
    app = FastAPI(
        title="PolicySync synthetic demo", docs_url=None, redoc_url=None, lifespan=lifespan
    )
    app.state.engine = engine
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    app.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        # Host validation alone does not prevent a remote client spoofing Host.
        if request.client is None or request.client.host not in {"127.0.0.1", "::1"}:
            return JSONResponse({"error": "local_demo_only"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError):
        return JSONResponse({"error": "database_unavailable_run_migrations"}, status_code=503)

    @app.get("/healthz")
    def health():
        config = Config(str(ROOT / "alembic.ini"))
        expected = ScriptDirectory.from_config(config).get_current_head()
        with engine.connect() as connection:
            actual = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        if actual != expected:
            return JSONResponse({"status": "schema_not_current"}, status_code=503)
        return {"status": "ok", "mode": "synthetic_demo"}

    @app.get("/")
    def index(request: Request):
        with Session(engine) as session:
            matters = list_matters(session)
            return templates.TemplateResponse(
                request=request, name="index.html", context={"matters": matters}
            )

    @app.get("/docs", include_in_schema=False)
    def docs(request: Request):
        return templates.TemplateResponse(request=request, name="api-docs.html")

    @app.get("/api/v1/matters")
    def matters(limit: int = 50, offset: int = 0):
        if not 1 <= limit <= 100 or offset < 0:
            return JSONResponse({"error": "invalid_pagination"}, status_code=422)
        with Session(engine) as session:
            return [
                {
                    "id": m.id,
                    "reference": m.external_claim_ref,
                    "insured_alias": m.insured_alias,
                    "state": m.state,
                    "version": m.version,
                }
                for m in list_matters(session, limit, offset)
            ]

    return app


app = create_app()
