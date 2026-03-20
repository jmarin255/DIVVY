from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes import groups as groups_routes
from app.api.routes import users as users_routes
from app.api.routes.auth import get_current_user
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import get_db
from app.main import app
from app.models import Base, User

SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL

if settings.TEST_DATABASE_URL == settings.DATABASE_URL:
    raise RuntimeError(
        "Unsafe test configuration: TEST_DATABASE_URL must be different from DATABASE_URL"
    )

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def authorized_user(db_session: Session) -> User:
    user = User(
        first_name="Dev",
        last_name="User",
        email="dev@example.com",
        password_hash=get_password_hash("password"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authorized_client(client: TestClient, authorized_user: User) -> Generator[TestClient, None, None]:

    def override_get_current_user() -> User:
        return authorized_user

    def override_require_dev() -> User:
        return authorized_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[users_routes.require_dev] = override_require_dev
    app.dependency_overrides[groups_routes.require_dev] = override_require_dev
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(users_routes.require_dev, None)
        app.dependency_overrides.pop(groups_routes.require_dev, None)
