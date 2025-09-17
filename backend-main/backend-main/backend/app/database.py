from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Allow overriding DB via env; default to local sqlite for dev
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

# Configure engine; avoid pooling options for SQLite
is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite+")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    **({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
    } if not is_sqlite else {})
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
