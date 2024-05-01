from pathlib import Path
import shutil
import pytest


@pytest.fixture(scope="session")
def testdata_path():
    path = Path("test-data")
    path.mkdir(parents=True, exist_ok=True)
    yield path
    shutil.rmtree(path)
