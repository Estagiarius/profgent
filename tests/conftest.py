import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pytest_mock import MockerFixture
from contextlib import contextmanager
from app.models.base import Base
from app.services.data_service import DataService

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Pytest fixture to create a new in-memory SQLite database session for each test function.
    This ensures that tests are isolated from each other.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def data_service(db_session: Session, mocker: MockerFixture) -> DataService:
    """
    Pytest fixture to create a DataService instance where all database interactions
    are mocked to use the isolated, in-memory test session.
    """
    # Create a context manager that yields the test session
    @contextmanager
    def mock_get_db_session():
        yield db_session

    # Mock the get_db_session context manager in all relevant modules
    mocker.patch("app.services.data_service.get_db_session", new=mock_get_db_session)
    # The tools do not directly call get_db_session, they call the data_service,
    # so we only need to patch it in the service layer.

    service = DataService()
    return service
