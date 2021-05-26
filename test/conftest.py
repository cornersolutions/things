import pytest
import os
import tempfile

from things.src.server import app as flaskapp
from things.src.dbs import setup_session


@pytest.fixture
def app():
    print('app')
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    setup_session(f'sqlite:///{db_path}')
    # create the app with common test config
    yield flaskapp

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    print('client')
    return app.test_client()