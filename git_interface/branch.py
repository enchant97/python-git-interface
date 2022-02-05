"""
Methods for using the 'branch' command
"""
import re
from pathlib import Path
from typing import Union, Any

from .constants import (BRANCH_ALREADY_EXISTS_RE, BRANCH_NOT_FOUND_RE,
                        BRANCH_REFNAME_NOT_FOUND_RE)
from .exceptions import (AlreadyExistsException, GitException,
                         NoBranchesException)
from .helpers import ensure_path, subprocess_run
from collections.abc import Coroutine

__all__ = [
    "get_branches", "new_branch",
    "copy_branch", "rename_branch",
    "delete_branch",
]


async def get_branches(git_repo: Union[Path, str]) -> Coroutine[Any, Any, tuple[str, tuple[str]]]:
    """
    Get the head branch and all others

        :param git_repo: Path to the repo
        :raises GitException: Error to do with git
        :raises NoBranchesException: Repo has no branches
        :return: the head branch and other branches
    """
    git_repo = ensure_path(git_repo)
    head = ""
    other_branches = []

    args = ["git", "-C", str(git_repo), "branch", "--no-color"]

    process_status = await subprocess_run(args)
    if not process_status.stdout:
        stderr = process_status.stderr.decode()
        if process_status.returncode != 0:
            raise GitException(stderr)
        if not stderr:
            raise NoBranchesException(
                f"no branches found for '{git_repo.name}'")

    split = process_status.stdout.decode().strip().split("\n")

    for line in split:
        if line[0] == "*":
            head = line[2:].strip()
        else:
            other_branches.append(line.strip())

    return head, tuple(other_branches)


async def new_branch(git_repo: Union[Path, str], branch_name: str):
    """
    Create a new branch in repo

        :param git_repo: Path to the repo
        :param branch_name: Branch name
        :raises AlreadyExistsException: Branch already exists
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "branch", branch_name]
    process_status = await subprocess_run(args)
    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(BRANCH_ALREADY_EXISTS_RE, stderr):
            raise AlreadyExistsException(
                f"branch name '{branch_name}' already exists")
        raise GitException(stderr)


async def copy_branch(git_repo: Union[Path, str], branch_name: str, new_branch: str):
    """
    Copy an existing branch to a new branch in repo (uses --force)

        :param git_repo: Path to the repo
        :param branch_name: Branch name
        :param new_branch: The new branch name
        :raises NoBranchesException: Branch does not exist
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "branch", "-C",
            branch_name, new_branch]
    process_status = await subprocess_run(args)
    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(BRANCH_REFNAME_NOT_FOUND_RE, stderr):
            raise NoBranchesException(
                f"no branch found with name '{branch_name}'")
        raise GitException(stderr)


async def rename_branch(git_repo: Union[Path, str], branch_name: str, new_branch: str):
    """
    Rename an existing branch (uses --force)

        :param git_repo: Path to the repo
        :param branch_name: Branch name
        :param new_branch: The new branch name
        :raises NoBranchesException: Branch does not exist
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "branch", "-M",
            branch_name, new_branch]
    process_status = await subprocess_run(args)
    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(BRANCH_REFNAME_NOT_FOUND_RE, stderr):
            raise NoBranchesException(
                f"no branch found with name '{branch_name}'")
        raise GitException(stderr)


async def delete_branch(git_repo: Union[Path, str], branch_name: str):
    """
    Delete an existing branch (uses --force)

        :param git_repo: Path to the repo
        :param branch_name: Branch name
        :raises NoBranchesException: Branch does not exist
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "branch", "-D", branch_name]
    process_status = await subprocess_run(args)
    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(BRANCH_NOT_FOUND_RE, stderr):
            raise NoBranchesException(
                f"no branch found with name '{branch_name}'")
        raise GitException(stderr)
