"""
Methods that don't fit in their own file
"""
import os
from pathlib import Path

import aiofiles

from .exceptions import AlreadyExistsException, GitException
from .helpers import ensure_path, subprocess_run

__all__ = [
    "get_version",
    "init_repo",
    "clone_repo",
    "get_description",
    "set_description",
    "run_maintenance",
    "add_to_staged",
    "commit_staged",
]


async def get_version() -> str:
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
    repo_dir: Path, repo_name: str, bare: bool = True, default_branch: str | None = None
):
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

    if repo_path.exists():
        msg = f"path already exists for '{repo_name}'"
        raise AlreadyExistsException(msg)

    args = ["git", "init", str(repo_path), "--quiet"]
    if bare:
        args.append("--bare")
    if default_branch:
        args.append(f"--initial-branch={default_branch}")
    process = await subprocess_run(args)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


async def clone_repo(
    git_repo: Path | str, src: str, bare=False, mirror=False, depth: None | int = None
):
    """
    Clone an exiting repo, please note this
    method has no way of passing passwords+usernames

        :param git_repo: Repo path to clone into
        :param src: Where to clone from
        :param bare: Use --bare git argument, defaults to False
        :param mirror: Use --mirror git argument, defaults to False
        :param depth: Use --depth git argument, defaults to None
        :raises ValueError: Both bare and mirror are True
        :raises GitException: Error to do with git
    """
    args = ["git", "clone", src, str(git_repo)]

    # disables interactive password prompt
    env = {**os.environ, "GCM_INTERACTIVE": "never", "GIT_TERMINAL_PROMPT": "0"}

    if mirror and bare:
        raise ValueError("both bare and mirror cannot be used at same time")
    if bare:
        args.append("--bare")
    if mirror:
        args.append("--mirror")
    if depth:
        args.append("--depth")
        args.append(f"{depth}")

    process = await subprocess_run(args, env=env)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


async def get_description(git_repo: Path | str) -> str:
    """
    Gets the set description for a repo

        :param git_repo: Path to the repo
        :return: The description
    """
    git_repo = ensure_path(git_repo)
    async with aiofiles.open(git_repo / "description", "r") as fo:
        return await fo.read()


async def set_description(git_repo: Path | str, description: str):
    """
    Sets the set description for a repo

        :param git_repo: Path to the repo
    """
    git_repo = ensure_path(git_repo)
    async with aiofiles.open(git_repo / "description", "w") as fo:
        await fo.write(description)


async def run_maintenance(git_repo: Path | str):
    """
    Run a maintenance git command to specified repo

        :param git_repo: Where the repo is
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "maintenance", "run"]
    process = await subprocess_run(args)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


async def add_to_staged(git_repo: Path | str, path: str, *extra_paths: str):
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
        # TODO: handle more specific exceptions
        raise GitException(process.stderr.decode())


async def commit_staged(git_repo: Path | str, messages: str | tuple[str]):
    """
    Commit staged files with a message(s)

        :param git_repo: Where the repo is
        :param messages: A single message or multiple
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "commit"]

    if isinstance(messages, str):
        messages = (messages,)

    for content in messages:
        args.extend(("-m", f'"{content}"'))

    process = await subprocess_run(args)
    if process.returncode != 0:
        # TODO: handle more specific exceptions
        raise GitException(process.stderr.decode())
