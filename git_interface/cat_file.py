"""
Methods for using the 'cat-file' command
"""
import re
from collections.abc import Coroutine
from pathlib import Path
from typing import Any, Union

from .constants import NOT_VALID_OBJECT_NAME_RE
from .datatypes import TreeContentTypes
from .exceptions import GitException, UnknownRevisionException
from .helpers import subprocess_run

__all__ = ["get_object_size", "get_object_type", "get_pretty_print"]


async def __cat_file_command(
        git_repo: Union[Path, str],
        tree_ish: str,
        file_path: str, *flags) -> Coroutine[Any, Any, bytes]:
    args = ["git", "-C", str(git_repo), "cat-file", f"{tree_ish}:{file_path}"]
    args.extend(flags)

    process_status = await subprocess_run(args)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(NOT_VALID_OBJECT_NAME_RE, stderr):
            raise UnknownRevisionException(f"Invalid object name '{tree_ish}:{file_path}'")
        raise GitException(stderr)

    return process_status.stdout


async def get_object_size(git_repo: Union[Path, str], tree_ish: str, file_path: str) -> int:
    """
    Gets the objects size from repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Invalid tree_ish or file_path
        :raises GitException: Error to do with git
        :return: The object size
    """
    return int(await __cat_file_command(git_repo, tree_ish, file_path, "-s"))


async def get_object_type(
        git_repo: Union[Path, str],
        tree_ish: str,
        file_path: str) -> Coroutine[Any, Any, TreeContentTypes]:
    """
    Gets the object type from repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Invalid tree_ish or file_path
        :raises GitException: Error to do with git
        :return: The object type
    """
    output = await __cat_file_command(git_repo, tree_ish, file_path, "-t").decode()
    return TreeContentTypes(output)


async def get_pretty_print(git_repo: Union[Path, str], tree_ish: str, file_path: str) -> Coroutine[Any, Any, bytes]:
    """
    Gets a object from repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Invalid tree_ish or file_path
        :raises GitException: Error to do with git
        :return: The object type
    """
    return await __cat_file_command(git_repo, tree_ish, file_path, "-p")
