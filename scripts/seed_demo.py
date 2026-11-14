"""Idempotent, fixed synthetic foundation fixture, not acceptance scenarios A–C."""

from datetime import date

from sqlalchemy.orm import Session

from app.config import Settings
from app.db import make_engine
from app.models import Matter, Organisation

ORG_ID = "00000000-0000-4000-8000-000000000001"
MATTER_ID = "00000000-0000-4000-8000-000000000002"


def seed(database_url: str):
    engine = make_engine(database_url)
    with Session(engine) as session, session.begin():
        if session.get(Organisation, ORG_ID) is None:
            session.add(
                Organisation(
                    id=ORG_ID,
                    display_name="SYNTHETIC Demo Insurer",
                    type="insurer",
                    created_by="synthetic-seed",
                )
            )
            session.flush()
        if session.get(Matter, MATTER_ID) is None:
            session.add(
                Matter(
                    id=MATTER_ID,
                    insurer_org_id=ORG_ID,
                    source_system="synthetic-fixture",
                    external_claim_ref="SYNTHETIC-PI-001",
                    insured_alias="SYNTHETIC Practice Alpha",
                    handler="demo-handler",
                    notification_date=date(2026, 5, 14),
                    created_by="synthetic-seed",
                )
            )
    engine.dispose()


if __name__ == "__main__":
    seed(Settings().database_url)
    print("Synthetic foundation fixture ready; scenarios A–C are not implemented.")
