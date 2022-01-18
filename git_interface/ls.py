"""
Methods for using the 'ls-tree' command
"""
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Optional, Union

from .constants import LS_TREE_LONG_RE, LS_TREE_RE, NOT_VALID_OBJECT_NAME_RE
from .datatypes import TreeContent
from .exceptions import GitException, UnknownRevisionException

__all__ = ["ls_tree"]


def __ls_tree_process_line(line: str) -> TreeContent:
    match = re.match(LS_TREE_RE, line)
    if match is None:
        raise ValueError("regex must have match")
    groups = match.groups()

    return TreeContent.from_str_values(
        mode=groups[0],
        type_=groups[1],
        object_=groups[2],
        file=groups[3],
    )


def __ls_tree_process_line_long(line: str) -> TreeContent:
    match = re.match(LS_TREE_LONG_RE, line)
    if match is None:
        raise ValueError("regex must have match")
    groups = match.groups()

    return TreeContent.from_str_values(
        mode=groups[0],
        type_=groups[1],
        object_=groups[2],
        object_size=groups[3],
        file=groups[4],
    )


def ls_tree(
        git_repo: Union[Path, str],
        tree_ish: str,
        recursive: bool,
        use_long: bool,
        path: Optional[Path] = None) -> Iterator[TreeContent]:
    """
    Get the tree of objects in repo

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param recursive: Whether tree is recursive
        :param use_long: Whether to get object sizes
        :param path: Filter path, defaults to None
        :raises UnknownRevisionException: Unknown tree_ish
        :raises GitException: Error to do with git
        :return: The git tree
    """
    args = ["git", "-C", str(git_repo), "ls-tree"]

    if use_long:
        args.append("-l")
    if recursive:
        args.append("-r")
    args.append(tree_ish)
    if path is not None:
        args.append(str(path))

    process_status = subprocess.run(args, capture_output=True)
    if not process_status.stdout and process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(NOT_VALID_OBJECT_NAME_RE, stderr):
            raise UnknownRevisionException(f"Unknown tree-ish '{tree_ish}'")
        raise GitException(stderr)

    split_lines = process_status.stdout.decode().strip().split("\n")

    if use_long:
        return map(__ls_tree_process_line_long, split_lines)
    return map(__ls_tree_process_line, split_lines)
