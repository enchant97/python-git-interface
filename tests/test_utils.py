from pathlib import Path
from secrets import token_hex

import pytest
from git_interface import utils


@pytest.mark.asyncio
async def test_get_version():
    assert isinstance(await utils.get_version(), str)


@pytest.mark.asyncio
async def test_init_repo(testdata_path: Path):
    repo_name = "init_repo-" + token_hex(4)
    repo_path = testdata_path / (repo_name + ".git")

    await utils.init_repo(testdata_path, repo_name, bare=True, default_branch="main")

    assert repo_path.exists()
    assert repo_path.joinpath("config").exists()
