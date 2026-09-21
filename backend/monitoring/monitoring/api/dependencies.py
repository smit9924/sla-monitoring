from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from monitoring.database.db import engine


def get_session() -> Generator[Session]:
    """
    Yield a request-scoped SQLModel Session.

    Description:
            Open and yield a Session bound to the application's engine for use
            in FastAPI dependencies. The session is closed automatically when
            the generator exits.

    Parameters:
            None

    Returns:
            Generator[Session, None, None] -- yields a sqlmodel.Session
    """
    with Session(engine) as session:
        yield session


# Database session dependency
# Intented across the application wherever a DB session is needed
SessionDep = Annotated[Session, Depends(get_session)]
