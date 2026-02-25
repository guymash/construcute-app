from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.infrastructure.db import create_session_factory, session_scope
from app.infrastructure.db.models import Base


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return url


def get_session_factory(
    database_url: Annotated[str, Depends(get_database_url)],
):
    return create_session_factory(database_url)


def get_db_session(
    session_factory=Depends(get_session_factory),
):
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
        )
    return token


def get_admin_token(
    admin_header: Annotated[str | None, Header(alias="X-Admin-Token")] = None,
) -> str:
    expected = os.getenv("ADMIN_TOKEN", "admin-secret")
    if not admin_header or admin_header != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )
    return admin_header

