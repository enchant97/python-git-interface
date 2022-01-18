"""
Methods for using the 'cat-file' command
"""
import re
import subprocess
from pathlib import Path
from typing import Union

from .constants import NOT_VALID_OBJECT_NAME_RE
from .datatypes import TreeContentTypes
from .exceptions import GitException, UnknownRevisionException

__all__ = ["get_object_size", "get_object_type", "get_pretty_print"]


def __cat_file_command(git_repo: Union[Path, str], tree_ish: str, file_path: str, *flags) -> bytes:
    args = ["git", "-C", str(git_repo), "cat-file", f"{tree_ish}:{file_path}"]
    args.extend(flags)

    process_status = subprocess.run(args, capture_output=True)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(NOT_VALID_OBJECT_NAME_RE, stderr):
            raise UnknownRevisionException(f"Invalid object name '{tree_ish}:{file_path}'")
        raise GitException(stderr)

    return process_status.stdout


def get_object_size(git_repo: Union[Path, str], tree_ish: str, file_path: str) -> int:
    """
    Gets the objects size from repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Invalid tree_ish or file_path
        :raises GitException: Error to do with git
        :return: The object size
    """
    return int(__cat_file_command(git_repo, tree_ish, file_path, "-s"))


def get_object_type(git_repo: Union[Path, str], tree_ish: str, file_path: str) -> TreeContentTypes:
    """
    Gets the object type from repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Invalid tree_ish or file_path
        :raises GitException: Error to do with git
        :return: The object type
    """
    output = __cat_file_command(git_repo, tree_ish, file_path, "-t").decode()
    return TreeContentTypes(output)


def get_pretty_print(git_repo: Union[Path, str], tree_ish: str, file_path: str) -> bytes:
    """
    Gets a object from repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :raises UnknownRevisionException: Invalid tree_ish or file_path
        :raises GitException: Error to do with git
        :return: The object type
    """
    return __cat_file_command(git_repo, tree_ish, file_path, "-p")
