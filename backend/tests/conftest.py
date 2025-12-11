import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db, engine
from app.main import app

# Test database URL - use a test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/byro_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    # Create test database
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Create test database session"""
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create test client with test database"""
    # Override the get_db dependency
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()