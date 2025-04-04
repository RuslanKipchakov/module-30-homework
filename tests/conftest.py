import os

import pytest_asyncio
from app import models
from app.database import Base
from app.fastapi_app import app, get_session
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.orm import sessionmaker

from tests.sample_recipes import recipes_to_dump

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_recipes_app.db"
engine = create_async_engine(TEST_DATABASE_URL, future=True)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope="function")
async def client():
    """Создает объект клиента для работы с приложением"""
    yield TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Создает сессию для работы с базой данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield async_session
    finally:
        os.remove(TEST_DATABASE_URL.split("///")[-1])
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
def new_db(db_session):
    """Создает тестовую базу данных и
    применяет для неё зависимости FastAPI"""

    def _get_test_session():
        return db_session()

    app.dependency_overrides[get_session] = _get_test_session
    return _get_test_session


@pytest_asyncio.fixture(scope="function")
async def sample_data(db_session):
    """Добавляет примеры рецептов в тестовую базу данных"""
    async with db_session() as session:
        for recipe in recipes_to_dump:
            new_recipe = models.Recipe(**recipe)
            session.add(new_recipe)
        await session.commit()
