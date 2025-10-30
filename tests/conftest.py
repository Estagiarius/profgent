import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.base import Base
from app.services.data_service import DataService

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Pytest fixture to create a new in-memory SQLite database session for each test function.
    This ensures that tests are isolated from each other.
    """
    # Use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def data_service(db_session: Session) -> DataService:
    """
    Pytest fixture to create a DataService instance that uses the test database session.
    We need to monkeypatch the service's session with our test session.
    """
    # Create a real DataService instance
    service = DataService()

    # Replace its database session with our isolated, in-memory test session
    service.db_session = db_session
    service.student_repo.session = db_session
    service.course_repo.session = db_session
    service.grade_repo.session = db_session

    return service
