from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def testdata_path() -> Path:
    path = Path("test-data")
    path.mkdir(parents=True, exist_ok=True)
    return path
