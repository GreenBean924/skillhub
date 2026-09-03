from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.database import Base, get_db
from app.main import app
from app.models.skill import Skill

TEST_DATABASE_URL = "postgresql+asyncpg://skillhub:skillhub_dev@localhost:5432/skillhub_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_skill(db_session: AsyncSession) -> Skill:
    skill = Skill(
        name="Test Skill",
        slug="test-skill",
        description="A test skill for unit testing",
        author="Test Author",
        tags=["python", "testing"],
        capabilities=["file_read", "code_exec"],
        security_level="safe",
        security_score=95,
        security_report={
            "findings": [
                {
                    "id": "F001",
                    "severity": "info",
                    "title": "Reads files",
                    "description": "Can read local files",
                    "evidence": "fs.read",
                    "recommendation": "Verify file paths",
                }
            ],
            "scannedAt": "2026-09-01T00:00:00+00:00",
        },
        install_command="skillhub install test-skill",
        downloads=1200,
        stars=42,
        content="# Test Skill\nprint('hello')",
    )
    db_session.add(skill)
    await db_session.flush()
    return skill


@pytest_asyncio.fixture
async def seed_skills(db_session: AsyncSession) -> list[Skill]:
    skills_data = [
        {
            "name": "Alpha Skill",
            "slug": "alpha-skill",
            "description": "First alpha skill",
            "author": "Author A",
            "tags": ["python", "ai"],
            "capabilities": ["llm_call"],
            "security_level": "safe",
            "security_score": 90,
            "security_report": {},
            "install_command": "skillhub install alpha-skill",
            "downloads": 500,
            "stars": 30,
        },
        {
            "name": "Beta Skill",
            "slug": "beta-skill",
            "description": "Second beta skill with medium risk",
            "author": "Author B",
            "tags": ["security", "audit"],
            "capabilities": ["network_access"],
            "security_level": "medium",
            "security_score": 60,
            "security_report": {},
            "install_command": "skillhub install beta-skill",
            "downloads": 200,
            "stars": 15,
        },
        {
            "name": "Gamma Skill",
            "slug": "gamma-skill",
            "description": "Third gamma skill for testing",
            "author": "Author A",
            "tags": ["python", "testing"],
            "capabilities": ["file_read"],
            "security_level": "safe",
            "security_score": 88,
            "security_report": {},
            "install_command": "skillhub install gamma-skill",
            "downloads": 800,
            "stars": 25,
        },
    ]
    skills = [Skill(**data) for data in skills_data]
    db_session.add_all(skills)
    await db_session.flush()
    return skills
