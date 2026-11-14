from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Matter


def list_matters(session: Session, limit: int = 50, offset: int = 0):
    return session.scalars(
        select(Matter).order_by(Matter.created_at_utc, Matter.id).limit(limit).offset(offset)
    ).all()
