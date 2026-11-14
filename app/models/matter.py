from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Record:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    updated_at_utc: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    created_by: Mapped[str] = mapped_column(String(80))
    version: Mapped[int] = mapped_column(default=1)


class Organisation(Record, Base):
    __tablename__ = "organisation"

    display_name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(40))
    commercial_crm_id: Mapped[str | None] = mapped_column(String(200))


class Matter(Record, Base):
    __tablename__ = "matter"
    __table_args__ = (
        UniqueConstraint("insurer_org_id", "source_system", "external_claim_ref"),
        CheckConstraint("version >= 1"),
        CheckConstraint("class_code = 'PI'"),
        CheckConstraint(
            "state IN ('intake','active','awaiting_external','review_pending','reporting','closed')"
        ),
    )

    insurer_org_id: Mapped[str] = mapped_column(ForeignKey("organisation.id"))
    source_system: Mapped[str] = mapped_column(String(80))
    external_claim_ref: Mapped[str] = mapped_column(String(120))
    insured_alias: Mapped[str] = mapped_column(String(200))
    class_code: Mapped[str] = mapped_column(String(20), default="PI")
    state: Mapped[str] = mapped_column(String(40), default="intake")
    handler: Mapped[str] = mapped_column(String(80))
    notification_date: Mapped[date] = mapped_column(Date)
