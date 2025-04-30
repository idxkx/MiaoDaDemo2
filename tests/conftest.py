import pytest

# Import the synchronous setup and teardown functions
from tests.utils.db_utils import init_test_db_sync, cleanup_test_db_sync

@pytest.fixture(scope="function", autouse=True)
def db(): # Make the fixture synchronous
    """数据库 fixture (function scope, auto-applied) - 同步初始化/清理

    Defined in conftest.py to be available across all tests.
    Uses synchronous functions for DB setup/teardown to avoid async issues.
    """
    print("[conftest.py db fixture] Calling synchronous init...")
    init_test_db_sync() # Call the synchronous setup function
    print("[conftest.py db fixture] Synchronous init finished. Yielding to test...")
    yield # Yield control to the test function
    print("[conftest.py db fixture] Test finished. Calling synchronous cleanup...")
    cleanup_test_db_sync() # Call the synchronous cleanup function
    print("[conftest.py db fixture] Teardown (sync cleanup performed)") 