import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.core.rate_limiter import rate_limiter
from app.core.token_blocklist import token_blocklist
from app.models.user import User, RoleEnum
from app.main import app

# In-memory SQLite database for isolated unit and integration testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_in_memory_state():
    """Resets singleton state between tests to prevent rate limit and token cross-pollution."""
    rate_limiter.reset()
    token_blocklist.clear()
    yield
    rate_limiter.reset()
    token_blocklist.clear()


@pytest.fixture(scope="function")
def db():
    """Provides a fresh database session for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        # Seed test admin
        admin = User(
            username="testadmin",
            email="admin@test.com",
            hashed_password=get_password_hash("AdminPass123!"),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        # Seed test operator
        operator = User(
            username="testoperator",
            email="operator@test.com",
            hashed_password=get_password_hash("OperatorPass123!"),
            role=RoleEnum.OPERATOR,
            is_active=True
        )
        # Seed test recycler
        recycler = User(
            username="testrecycler",
            email="recycler@test.com",
            hashed_password=get_password_hash("RecyclerPass123!"),
            role=RoleEnum.RECYCLER,
            is_active=True
        )
        # Seed test sustainability manager
        sust_mgr = User(
            username="testsustmgr",
            email="sustmgr@test.com",
            hashed_password=get_password_hash("SustMgrPass123!"),
            role=RoleEnum.SUSTAINABILITY_MANAGER,
            is_active=True
        )
        # Seed test manufacturer
        manufacturer = User(
            username="testmanufacturer",
            email="manufacturer@test.com",
            hashed_password=get_password_hash("ManufacturerPass123!"),
            role=RoleEnum.MANUFACTURER,
            is_active=True
        )
        session.add_all([admin, operator, recycler, sust_mgr, manufacturer])
        session.commit()

        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Provides an HTTP test client connected to the test database."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
