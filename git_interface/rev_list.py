"""
Methods for using the 'rev-list' command
"""
import re
import subprocess
from pathlib import Path
from typing import Optional, Union

from .constants import UNKNOWN_REV_RE
from .exceptions import GitException, UnknownRevisionException

__all__ = [
    "get_commit_count", "get_disk_usage",
    "get_rev_list",
]


def _rev_list(
        git_repo: Union[Path, str],
        branch: Optional[str] = None,
        operator: Optional[str] = None) -> str:
    if branch is None:
        branch = "--all"
    args = ["git", "-C", str(git_repo), "rev-list", branch]
    if operator:
        args.append(operator)
    process_status = subprocess.run(args, capture_output=True)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(UNKNOWN_REV_RE, stderr):
            raise UnknownRevisionException(stderr)
        raise GitException(stderr)
    return process_status.stdout.decode()


def get_commit_count(git_repo: Union[Path, str], branch: Optional[str] = None) -> int:
    """
    Get a repos commit count

        :param git_repo: Path to the repo
        :param branch: Branch to filter, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The commit count
    """
    return int(_rev_list(git_repo, branch, "--count"))


def get_disk_usage(git_repo: Union[Path, str], branch: Optional[str] = None) -> int:
    """
    Get a size of the repo

        :param git_repo: Path to the repo
        :param branch: Branch to filter, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The size of the repo
    """
    return int(_rev_list(git_repo, branch, "--disk-usage"))


def get_rev_list(git_repo: Union[Path, str], branch: Optional[str] = None) -> list[str]:
    """
    Get a repos revisions

        :param git_repo: Path to the repo
        :param branch: Branch to filter, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The repos revisions
    """
    return _rev_list(git_repo, branch).strip().split("\n")
