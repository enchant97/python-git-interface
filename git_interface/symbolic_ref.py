"""
Methods for using git symbolic-ref command
"""
from collections.abc import Coroutine
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Union

from .exceptions import GitException, UnknownRefException
from .helpers import subprocess_run

__all__ = [
    "change_symbolic_ref", "get_symbolic_ref",
    "delete_symbolic_ref", "get_active_branch",
    "change_active_branch",
]


def _raise_known_errors(process_status: CompletedProcess, ref: str):
    """
    Used to raise any known git
    exceptions for the 'symbolic-ref' command

        :param process_status: The current procress status
        :param ref: The given reference/name
        :raises UnknownRefException: Unknown reference given
        :raises GitException: Error to do with git
    """
    if process_status.returncode == 1:
        raise UnknownRefException(f"Unknown ref {ref}")
    elif process_status.returncode > 0:
        raise GitException(process_status.stderr.decode())


async def change_symbolic_ref(git_repo: Union[Path, str], name: str, ref: str):
    """
    Change a symbolic ref in repo

        :param git_repo: Path to the repo
        :param name: The name (for example HEAD)
        :param ref: The reference
        :raises UnknownRefException: Unknown reference given
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "symbolic-ref", name, ref]
    process_status = await subprocess_run(args)
    _raise_known_errors(process_status, ref)


async def get_symbolic_ref(git_repo: Union[Path, str], name: str) -> Coroutine[Any, Any, str]:
    """
    Get a symbolic ref in repo

        :param git_repo: Path to the repo
        :param name: The name (for example HEAD)
        :raises UnknownRefException: Unknown reference given
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "symbolic-ref", name]
    process_status = await subprocess_run(args)
    _raise_known_errors(process_status, name)
    return process_status.stdout.decode().strip()


async def delete_symbolic_ref(git_repo: Union[Path, str], name: str):
    """
    Delete a symbolic ref in repo

        :param git_repo: Path to the repo
        :param name: The name (for example HEAD)
        :raises UnknownRefException: Unknown reference given
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "symbolic-ref", "-d", name]
    process_status = await subprocess_run(args)
    _raise_known_errors(process_status, name)


async def get_active_branch(git_repo: Union[Path, str]) -> Coroutine[Any, Any, str]:
    """
    Get the active (HEAD) reference

        :param git_repo: Path to the repo
        :raises UnknownRefException: Unknown reference given
        :raises GitException: Error to do with git
    """
    return await get_symbolic_ref(git_repo, "HEAD")


async def change_active_branch(git_repo: Union[Path, str], branch: str):
    """
    Change the active (HEAD) reference

        :param git_repo: Path to the repo
        :param branch: The branch name to use
        :raises UnknownRefException: Unknown reference given
        :raises GitException: Error to do with git
    """
    await change_symbolic_ref(git_repo, "HEAD", f"refs/heads/{branch}")
