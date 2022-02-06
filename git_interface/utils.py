"""
Methods that don't fit in their own file
"""
import os
from collections.abc import Coroutine
from pathlib import Path
from typing import Any, AsyncGenerator, Optional, Union

import aiofiles

from .datatypes import ArchiveTypes
from .exceptions import (AlreadyExistsException, BufferedProcessError,
                         GitException)
from .helpers import ensure_path, subprocess_run, subprocess_run_buffered

__all__ = [
    "get_version", "init_repo",
    "clone_repo", "get_description",
    "set_description", "run_maintenance",
    "get_archive", "get_archive_buffered",
]


async def get_version() -> Coroutine[Any, Any, str]:
    """
    Gets the git version

        :raises GitException: Error to do with git
        :return: The version
    """
    args = ("git", "version")
    process_status = await subprocess_run(args)
    if process_status.returncode != 0:
        raise GitException(process_status.stderr.decode())
    return process_status.stdout.decode().strip()


async def init_repo(
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
    process = await subprocess_run(args)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


async def clone_repo(git_repo: Union[Path, str], src: str, bare=False, mirror=False):
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

    process = await subprocess_run(args, env=env)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


async def get_description(git_repo: Union[Path, str]) -> Coroutine[Any, Any, str]:
    """
    Gets the set description for a repo

        :param git_repo: Path to the repo
        :return: The description
    """
    git_repo = ensure_path(git_repo)
    async with aiofiles.open(git_repo / "description", "r") as fo:
        return await fo.read()


async def set_description(git_repo: Union[Path, str], description: str):
    """
    Sets the set description for a repo

        :param git_repo: Path to the repo
    """
    git_repo = ensure_path(git_repo)
    async with aiofiles.open(git_repo / "description", "w") as fo:
        await fo.write(description)


async def run_maintenance(git_repo: Union[Path, str]):
    """
    Run a maintenance git command to specified repo

        :param git_repo: Where the repo is
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "maintenance", "run"]
    process = await subprocess_run(args)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


async def get_archive(
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
    process = await subprocess_run(
        ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish],
    )
    if process.returncode != 0:
        raise GitException(process.stderr.decode())
    return process.stdout


async def get_archive_buffered(
        git_repo: Union[Path, str],
        archive_type: ArchiveTypes,
        tree_ish: str = "HEAD") -> AsyncGenerator[bytes, None]:
    """
    get a archive of a git repo, but using a buffered read

        :param git_repo: Where the repo is
        :param archive_type: What archive type will be created
        :param tree_ish: What commit/branch to save, defaults to "HEAD"
        :raises GitException: Error to do with git
        :yield: Each read content section
    """
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value

    args = ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish]

    try:
        async for content in subprocess_run_buffered(args):
            yield content
    except BufferedProcessError as err:
        raise GitException(err.args[0].decode()) from err


async def add_to_staged(git_repo: Union[Path, str], path: str, *extra_paths: tuple[str]):
    """
    Add files to the repository staging area

        :param git_repo: Where the repo is
        :param path: The path to add
        :param *extra_paths: Add more paths
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "add", path]
    if len(extra_paths) != 0:
        args.extend(extra_paths)

    process = await subprocess_run(args)
    if process.returncode != 0:
        # TODO handle more specific exceptions
        raise GitException(process.stderr.decode())


async def commit_staged(git_repo: Union[Path, str], messages: Union[str, tuple[str]]):
    """
    Commit staged files with a message(s)

        :param git_repo: Where the repo is
        :param messages: A single message or multiple
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "commit"]

    if (isinstance(messages, str)):
        messages = (messages,)

    for content in messages:
        args.extend(("-m", f"\"{content}\""))

    process = await subprocess_run(args)
    if process.returncode != 0:
        # TODO handle more specific exceptions
        raise GitException(process.stderr.decode())
