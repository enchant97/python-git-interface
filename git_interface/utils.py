"""
Methods that don't fit in their own file
"""
import subprocess
from pathlib import Path
from typing import Optional

from .datatypes import ArchiveTypes
from .exceptions import AlreadyExistsException, GitException

__all__ = [
    "init_repo", "get_description",
    "set_description", "run_maintenance",
    "get_archive",
]


def init_repo(
        repo_dir: Path,
        repo_name: str,
        bare: bool = True,
        default_branch: Optional[str] = None):
    """
    Creates a new git repo in the directory with the given name,
    if bare the repo name will have .git added at the end.

        :param repo_dir: Where the repo will be
        :param repo_name: The name of the repo
        :param bare: Whether the repo is bare, defaults to True
        :param default_branch: The branch name to use, defaults to None
        :raises AlreadyExistsException: A repo already exists
        :raises GitException: Error to do with git
    """
    if bare:
        repo_name = repo_name + ".git"
    repo_path = repo_dir / repo_name

    if (repo_path.exists()):
        raise AlreadyExistsException(f"path already exists for '{repo_name}'")

    args = ["git", "init", str(repo_path), "--quiet"]
    if bare:
        args.append("--bare")
    if default_branch:
        args.append(f"--initial-branch={default_branch}")
    process = subprocess.run(args)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


def get_description(git_repo: Path) -> str:
    """
    Gets the set description for a repo

        :param git_repo: Path to the repo
        :return: The description
    """
    with open(git_repo / "description", "r") as fo:
        return fo.read()


def set_description(git_repo: Path, description: str):
    """
    Sets the set description for a repo

        :param git_repo: Path to the repo
    """
    with open(git_repo / "description", "w") as fo:
        fo.write(description)


def run_maintenance(git_repo: Path):
    """
    Run a maintenance git command to specified repo

        :param git_repo: Where the repo is
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "maintenance", "run"]
    process = subprocess.run(args, capture_output=True)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


def get_archive(
        git_repo: Path,
        archive_type: ArchiveTypes,
        tree_ish: str = "HEAD") -> bytes:
    """
    get a archive of a git repo

        :param git_repo: Where the repo is
        :param archive_type: What archive type will be created
        :param tree_ish: What commit/branch to save, defaults to "HEAD"
        :raises GitException: Error to do with git
        :return: The content of the archive ready to write to a file
    """
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value
    process = subprocess.run(
        ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish],
        capture_output=True)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())
    return process.stdout
