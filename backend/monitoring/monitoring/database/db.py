from sqlmodel import create_engine

from monitoring.core.config import settings
from monitoring.database.models import *  # noqa: F403

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
