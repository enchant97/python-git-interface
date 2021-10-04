"""
Methods for using the git branch command
"""
import subprocess
from pathlib import Path
from typing import Tuple

from .exceptions import GitException, NoBranchesException

__all__ = ["get_branches"]


def get_branches(git_repo: Path) -> Tuple[str, Tuple[str]]:
    """
    Get the head branch and all others

        :param git_repo: Path to the repo
        :raises GitException: Error to do with git
        :raises NoBranchesException: Repo has no branches
        :return: the head branch and other branches
    """
    head = ""
    other_branches = []

    args = ["git", "-C", str(git_repo), "branch", "--no-color"]

    process_status = subprocess.run(args, capture_output=True)
    if not process_status.stdout:
        stderr = process_status.stderr.decode()
        if process_status.returncode != 0:
            raise GitException(stderr)
        if not stderr:
            raise NoBranchesException(f"no branches found for '{git_repo.name}'")

    split = process_status.stdout.decode().strip().split("\n")

    for line in split:
        if line[0] == "*":
            head = line[2:]
        else:
            other_branches.append(line[2:])

    return head, tuple(other_branches)
