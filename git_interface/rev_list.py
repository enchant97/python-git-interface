"""
Methods for using the 'rev-list' command
"""
import re
from collections.abc import Coroutine
from pathlib import Path
from typing import Any, Optional, Union

from .constants import UNKNOWN_REV_RE
from .exceptions import GitException, UnknownRevisionException
from .helpers import subprocess_run

__all__ = [
    "get_commit_count", "get_disk_usage",
    "get_rev_list",
]


async def _rev_list(
        git_repo: Union[Path, str],
        branch: Optional[str] = None,
        operator: Optional[str] = None) -> Coroutine[Any, Any, str]:
    if branch is None:
        branch = "--all"
    args = ["git", "-C", str(git_repo), "rev-list", branch]
    if operator:
        args.append(operator)
    process_status = await subprocess_run(args)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(UNKNOWN_REV_RE, stderr):
            raise UnknownRevisionException(stderr)
        raise GitException(stderr)
    return process_status.stdout.decode()


async def get_commit_count(
        git_repo: Union[Path, str],
        branch: Optional[str] = None) -> Coroutine[Any, Any, int]:
    """
    Get a repos commit count

        :param git_repo: Path to the repo
        :param branch: Branch to filter, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The commit count
    """
    return int(await _rev_list(git_repo, branch, "--count"))


async def get_disk_usage(
        git_repo: Union[Path, str],
        branch: Optional[str] = None) -> Coroutine[Any, Any, int]:
    """
    Get a size of the repo

        :param git_repo: Path to the repo
        :param branch: Branch to filter, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The size of the repo
    """
    return int(await _rev_list(git_repo, branch, "--disk-usage"))


async def get_rev_list(
        git_repo: Union[Path, str],
        branch: Optional[str] = None) -> Coroutine[Any, Any, list[str]]:
    """
    Get a repos revisions

        :param git_repo: Path to the repo
        :param branch: Branch to filter, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The repos revisions
    """
    return (await _rev_list(git_repo, branch)).strip().split("\n")
