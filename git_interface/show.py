"""
Methods for using the 'show' command
"""
import re
from collections.abc import AsyncGenerator, Coroutine
from pathlib import Path
from typing import Any, Union

from .constants import INVALID_OBJECT_NAME, PATH_DOES_NOT_EXIST
from .exceptions import (BufferedProcessError, GitException,
                         PathDoesNotExistInRevException,
                         UnknownRevisionException)
from .helpers import subprocess_run, subprocess_run_buffered

__all__ = [
    "show_file", "show_file_buffered",
]


async def show_file(
        git_repo: Union[Path, str],
        tree_ish: str,
        file_path: str) -> Coroutine[Any, Any, bytes]:
    """
    Read a file from a repository

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Unknown tree_ish
        :raises PathDoesNotExistInRevException: File not found in repo
        :raises GitException: Error to do with git
        :return: The read file
    """
    args = ["git", "-C", str(git_repo), "show", f"{tree_ish}:{file_path}"]

    process_status = await subprocess_run(args)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(INVALID_OBJECT_NAME, stderr):
            raise UnknownRevisionException(f"Unknown tree-ish '{tree_ish}'")
        elif re.match(PATH_DOES_NOT_EXIST, stderr):
            raise PathDoesNotExistInRevException(f"'{file_path}' not found in repo")
        raise GitException(stderr)

    return process_status.stdout


async def show_file_buffered(
        git_repo: Union[Path, str],
        tree_ish: str,
        file_path: str) -> AsyncGenerator[bytes, None, None]:
    """
    Read a file from a repository, but using a buffered read

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Unknown tree_ish
        :raises PathDoesNotExistInRevException: File not found in repo
        :raises GitException: Error to do with git
        :yield: Each read file section
    """
    args = ["git", "-C", str(git_repo), "show", f"{tree_ish}:{file_path}"]

    try:
        async for content in subprocess_run_buffered(args):
            yield content
    except BufferedProcessError as err:
        exception = None
        stderr = err.args[0].decode()

        if re.match(INVALID_OBJECT_NAME, stderr):
            exception = UnknownRevisionException(f"Unknown tree-ish '{tree_ish}'")
        elif re.match(PATH_DOES_NOT_EXIST, stderr):
            exception = PathDoesNotExistInRevException(f"'{file_path}' not found in repo")
        else:
            exception = GitException(stderr)

        raise exception from err
