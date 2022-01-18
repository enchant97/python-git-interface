"""
Methods that don't fit in their own file
"""
import os
import subprocess
from pathlib import Path
from typing import Generator, Optional, Union

from .datatypes import ArchiveTypes
from .exceptions import AlreadyExistsException, GitException
from .helpers import ensure_path

__all__ = [
    "get_version", "init_repo",
    "clone_repo", "get_description",
    "set_description", "run_maintenance",
    "get_archive", "get_archive_buffered",
]


def get_version() -> str:
    """
    Gets the git version

        :raises GitException: Error to do with git
        :return: The version
    """
    args = ("git", "version")
    process_status = subprocess.run(args, capture_output=True)
    if process_status.returncode != 0:
        raise GitException(process_status.stderr.decode())
    return process_status.stdout.decode().strip()


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


def clone_repo(git_repo: Union[Path, str], src: str, bare=False, mirror=False):
    """
    Clone an exiting repo, please note this
    method has no way of passing passwords+usernames

        :param git_repo: Repo path to clone into
        :param src: Where to clone from
        :param bare: Use --bare git argument, defaults to False
        :param mirror: Use --mirror git argument, defaults to False
        :raises ValueError: Both bare and mirror are True
        :raises GitException: Error to do with git
    """
    args = ["git", "clone", src, str(git_repo)]

    # disables interactive password prompt
    env = {
        **os.environ,
        "GCM_INTERACTIVE": "never",
        "GIT_TERMINAL_PROMPT": "0"
    }

    if mirror and bare:
        raise ValueError("both bare and mirror cannot be used at same time")
    elif bare:
        args.append("--bare")
    elif mirror:
        args.append("--mirror")

    process = subprocess.run(args, capture_output=True, env=env)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


def get_description(git_repo: Union[Path, str]) -> str:
    """
    Gets the set description for a repo

        :param git_repo: Path to the repo
        :return: The description
    """
    git_repo = ensure_path(git_repo)
    with open(git_repo / "description", "r") as fo:
        return fo.read()


def set_description(git_repo: Union[Path, str], description: str):
    """
    Sets the set description for a repo

        :param git_repo: Path to the repo
    """
    git_repo = ensure_path(git_repo)
    with open(git_repo / "description", "w") as fo:
        fo.write(description)


def run_maintenance(git_repo: Union[Path, str]):
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
        git_repo: Union[Path, str],
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


def get_archive_buffered(
        git_repo: Union[Path, str],
        archive_type: ArchiveTypes,
        tree_ish: str = "HEAD",
        bufsize: int = -1) -> Generator[bytes, None, None]:
    """
    get a archive of a git repo, but using a buffered read

        :param git_repo: Where the repo is
        :param archive_type: What archive type will be created
        :param tree_ish: What commit/branch to save, defaults to "HEAD"
        :param bufsize: The buffer size to pass into subprocess.Popen, defaults to -1
        :raises GitException: Error to do with git
        :yield: Each read content section
    """
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value

    with subprocess.Popen(
        ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish],
        bufsize=bufsize,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as process:
        for line in process.stdout:
            yield line

        return_code = process.wait()
        if return_code != 0:
            stderr = process.stderr.read().decode()
            raise GitException(stderr)
