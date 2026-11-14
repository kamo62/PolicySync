import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.db import make_engine
from app.main import create_app
from scripts.install_offline import verify
from scripts.seed_demo import seed


@pytest.fixture
def database(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    command.upgrade(Config("alembic.ini"), "head")
    return url


def test_seed_and_readonly_workflow(database):
    seed(database)
    seed(database)
    app = create_app(Settings(database_url=database))
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        assert client.get("/healthz").json()["status"] == "ok"
        page = client.get("/")
        assert page.status_code == 200
        assert "SYNTHETIC DATA ONLY" in page.text
        assert "SYNTHETIC-PI-001" in page.text
        rows = client.get("/api/v1/matters").json()
        assert len(rows) == 1
        assert client.get("/api/v1/matters?limit=101").status_code == 422
        assert client.post("/api/v1/matters", json={}).status_code == 405
        assert client.get("/static/app.css").status_code == 200
        assert "https://" not in client.get("/docs").text
        assert client.get("/openapi.json").json()["info"]["title"]
    app.state.engine.dispose()


def test_network_guards(database):
    app = create_app(Settings(database_url=database))
    with TestClient(app, base_url="http://127.0.0.1", client=("192.0.2.1", 50000)) as client:
        assert client.get("/healthz").status_code == 403
    with TestClient(app, base_url="http://attacker.example", client=("127.0.0.1", 50000)) as client:
        assert client.get("/healthz").status_code == 400
    app.state.engine.dispose()


def test_database_constraints_and_rollback(database):
    seed(database)
    engine = make_engine(database)
    with engine.connect() as connection:
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1
        assert connection.scalar(text("PRAGMA journal_mode")) == "wal"
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(text("UPDATE matter SET insurer_org_id='missing'"))
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM matter")) == 1
        assert connection.scalar(text("SELECT insurer_org_id FROM matter")) != "missing"
    engine.dispose()


def test_migration_reapply_and_empty_downgrade(database):
    seed(database)
    command.upgrade(Config("alembic.ini"), "head")
    engine = make_engine(database)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM matter")) == 1
    # Initial downgrade is intentionally destructive, tested on a disposable fixture only.
    command.downgrade(Config("alembic.ini"), "base")
    assert "matter" not in inspect(engine).get_table_names()
    command.upgrade(Config("alembic.ini"), "head")
    command.check(Config("alembic.ini"))
    engine.dispose()


def test_health_requires_migrations(tmp_path):
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'empty.db'}"))
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        response = client.get("/healthz")
        assert response.status_code == 503
        assert "empty.db" not in response.text
    app.state.engine.dispose()


@pytest.mark.parametrize(
    "override",
    [{"host": "0.0.0.0"}, {"crm_provider": "lark"}, {"database_url": "postgresql://example/db"}],
)
def test_configuration_rejects_unimplemented_modes(override):
    with pytest.raises(ValidationError):
        Settings(**override)


def test_offline_dependencies_have_valid_hashes():
    manifest = verify()
    assert "Linux x86_64" in manifest["target"]
