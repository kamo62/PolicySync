from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./var/policysync.db"
    evidence_dir: Path = Path("var/evidence")
    crm_provider: str = "none"
    host: str = "127.0.0.1"
    port: int = 8000

    @model_validator(mode="after")
    def local_demo_only(self):
        url = make_url(self.database_url)
        if url.drivername != "sqlite" or not url.database or url.database == ":memory:":
            raise ValueError("This starter requires a local file-backed SQLite database")
        if self.host != "127.0.0.1":
            raise ValueError("The synthetic demo must bind to 127.0.0.1")
        if self.crm_provider != "none":
            raise ValueError("CRM integration is not implemented; use CRM_PROVIDER=none")
        return self
