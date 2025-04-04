from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./recipes_app.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def init_db() -> None:
    """Создаёт базу данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
