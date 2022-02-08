"""
Methods for using the 'tag' command
"""
import re
from collections.abc import Coroutine
from pathlib import Path
from typing import Any, Optional, Union

from .constants import TAG_ALREADY_EXISTS_RE, TAG_NOT_FOUND_RE
from .exceptions import (AlreadyExistsException, DoesNotExistException,
                         GitException)
from .helpers import subprocess_run

__all__ = [
    "list_tags", "create_tag",
    "delete_tag",
]


async def list_tags(
        git_repo: Union[Path, str],
        tag_pattern: Optional[str] = None) -> Coroutine[Any, Any, list[str]]:
    """
    List all git tags or filter with a wildcard pattern

        :param git_repo: Path to the repo
        :param tag_pattern: Filter the tag list with a wildcard pattern, defaults to None
        :raises GitException: Error to do with git
        :return: List of found git tags
    """
    args = ["git", "-C", str(git_repo), "tag", "-l"]
    if tag_pattern:
        args.append(tag_pattern)

    process_status = await subprocess_run(args)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        raise GitException(stderr)

    if not process_status.stdout.decode().strip():
        return list()

    return process_status.stdout.decode().strip().split("\n")


async def create_tag(
        git_repo: Union[Path, str],
        tag_name: str,
        commit_hash: Optional[str] = None):
    """
    Create a new lightweight tag

        :param git_repo: Path to the repo
        :param tag_name: The tag name to use
        :param commit_hash: Create tag on a different
                            commit other than HEAD, defaults to None
        :raises AlreadyExistsException: When the tag name already exists
        :raises GitException: Error to do with git
    """
    args = ["git", "-C", str(git_repo), "tag", tag_name]
    if commit_hash:
        args.append(commit_hash)

    process_status = await subprocess_run(args)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(TAG_ALREADY_EXISTS_RE, stderr):
            raise AlreadyExistsException(f"tag '{tag_name}' already exists")
        raise GitException(stderr)


async def delete_tag(
        git_repo: Union[Path, str],
        tag_name: str) -> Coroutine[Any, Any, str]:
    """
    Delete a tag

        :param git_repo: Path to the repo
        :param tag_name: The tag name to use
        :raises DoesNotExistException: The tag was not found
        :raises GitException: Error to do with git
        :return: Output provided by the git when a tag is removed
    """
    args = ["git", "-C", str(git_repo), "tag", "-d", tag_name]

    process_status = await subprocess_run(args)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(TAG_NOT_FOUND_RE, stderr):
            raise DoesNotExistException(f"tag '{tag_name}' not found")
        raise GitException(stderr)

    return process_status.stdout.decode().strip().removesuffix("\n")
