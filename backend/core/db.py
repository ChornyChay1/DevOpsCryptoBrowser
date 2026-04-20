from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from core.settings import get_database_url


def get_engine():
    database_url = get_database_url()
    print("DATABASE_URL: ", database_url)
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")
    return create_async_engine(database_url, echo=False)


def get_session_local():
    engine = get_engine()
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


Base = declarative_base()
