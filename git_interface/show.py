"""
Methods for using the 'show' command
"""
import re
import subprocess
from pathlib import Path
from typing import Generator, Union

from .constants import INVALID_OBJECT_NAME, PATH_DOES_NOT_EXIST
from .exceptions import (GitException, PathDoesNotExistInRevException,
                         UnknownRevisionException)

__all__ = [
    "show_file", "show_file_buffered",
]


def show_file(git_repo: Union[Path, str], tree_ish: str, file_path: str) -> bytes:
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

    process_status = subprocess.run(args, capture_output=True)

    if process_status.returncode != 0:
        stderr = process_status.stderr.decode()
        if re.match(INVALID_OBJECT_NAME, stderr):
            raise UnknownRevisionException(f"Unknown tree-ish '{tree_ish}'")
        elif re.match(PATH_DOES_NOT_EXIST, stderr):
            raise PathDoesNotExistInRevException(f"'{file_path}' not found in repo")
        raise GitException(stderr)

    return process_status.stdout


def show_file_buffered(
        git_repo: Union[Path, str],
        tree_ish: str,
        file_path: str,
        bufsize: int = -1) -> Generator[bytes, None, None]:
    """
    Read a file from a repository, but using a buffered read

        :param git_repo: Path to the repo
        :param tree_ish: The tree ish (branch name, HEAD)
        :param file_path: The file in the repo to read
        :param bufsize: The buffer size to pass into subprocess.Popen, defaults to -1
        :raises UnknownRevisionException: Unknown tree_ish
        :raises PathDoesNotExistInRevException: File not found in repo
        :raises GitException: Error to do with git
        :yield: Each read file section
    """
    args = ["git", "-C", str(git_repo), "show", f"{tree_ish}:{file_path}"]

    with subprocess.Popen(
        args,
        bufsize=bufsize,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as process:
        for line in process.stdout:
            yield line

        return_code = process.wait()
        if return_code != 0:
            stderr = process.stderr.read().decode()
            if re.match(INVALID_OBJECT_NAME, stderr):
                raise UnknownRevisionException(f"Unknown tree-ish '{tree_ish}'")
            elif re.match(PATH_DOES_NOT_EXIST, stderr):
                raise PathDoesNotExistInRevException(f"'{file_path}' not found in repo")
            raise GitException(stderr)
