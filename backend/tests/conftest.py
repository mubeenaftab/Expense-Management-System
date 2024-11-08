import asyncio
import uuid

import asgi_lifespan
import fastapi
import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from src.config.settings.base import config_env
from src.config.settings.logger_config import logger
from src.main import initialize_backend_application
from src.models.db.category import Category
from src.models.db.expense import Expense
from src.models.schemas.user import UserCreate
from src.repository.database import Base, get_db
from src.securities.authorization.jwt import create_access_token

DATABASE_URL = config_env.test_database_url

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        logger.debug(f"Connected to database: {session.bind.engine.url}")
        yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncSession:
    async for session in override_get_db():
        yield session


@pytest.fixture(scope="session")
def backend_test_app() -> fastapi.FastAPI:
    app = initialize_backend_application()
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture(scope="session")
async def initialize_backend_test_application(
    backend_test_app: fastapi.FastAPI,
) -> fastapi.FastAPI:
    async with asgi_lifespan.LifespanManager(backend_test_app):
        yield backend_test_app


@pytest.fixture(scope="session")
async def client(
    initialize_backend_test_application: fastapi.FastAPI,
) -> httpx.AsyncClient:
    async with httpx.AsyncClient(
        app=initialize_backend_test_application,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables successfully created")

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Tables successfully dropped")


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(db: AsyncSession):
    async with db.begin():
        await db.execute(delete(Expense))
        await db.execute(delete(Category))
    await db.commit()


@pytest.fixture(scope="function")
async def create_test_user(client: httpx.AsyncClient):
    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
    user_data = UserCreate(username=unique_username, password="Test@123")
    response = await client.post("/register", json=user_data.model_dump())
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    return response.json()


@pytest.fixture(scope="function")
async def user_token(create_test_user):
    access_token = await create_access_token(data={"sub": create_test_user["username"]})
    return access_token


@pytest.fixture(scope="function")
async def authorized_headers(user_token: str):
    return {"accept": "application/json", "Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="function")
async def create_test_category(client: httpx.AsyncClient, authorized_headers):
    category_data = {"name": f"Test Category_{uuid.uuid4().hex[:6]}", "is_active": True}
    category_response = await client.post("/categories", json=category_data, headers=authorized_headers)
    assert category_response.status_code == 201
    return category_response.json()
