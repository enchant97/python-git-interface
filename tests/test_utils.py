from pathlib import Path
from secrets import token_hex

from git_interface import utils


def test_get_version():
    assert isinstance(utils.get_version(), str)


def test_init_repo(testdata_path: Path):
    repo_name = "init_repo-" + token_hex(4)
    repo_path = testdata_path / (repo_name + ".git")

    utils.init_repo(testdata_path, repo_name, bare=True, default_branch="main")

    assert repo_path.exists()
    assert repo_path.joinpath("config").exists()
