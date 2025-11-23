import pytest
from unittest.mock import patch
from main import initialize_database
from app.data.database import Base

def test_startup_logic_fixed(mocker):
    """
    Verifies that initialize_database always calls create_all to ensure schema integrity.
    """
    # Mock os.path.exists to return True (simulate DB file exists)
    mocker.patch('os.path.exists', return_value=True)

    # Mock Base.metadata.create_all
    mock_create_all = mocker.patch.object(Base.metadata, 'create_all')

    # Action
    initialize_database()

    # Assert
    # Fix: It should be called even if file exists.
    mock_create_all.assert_called_once()
