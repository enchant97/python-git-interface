"""
Methods used for 'archive' command
"""
from pathlib import Path
from typing import AsyncGenerator, Union

from .datatypes import ArchiveTypes
from .exceptions import BufferedProcessError, GitException
from .helpers import subprocess_run, subprocess_run_buffered

__all__ = [
    "get_archive", "get_archive_buffered",
]


async def get_archive(
        git_repo: Union[Path, str],
        archive_type: ArchiveTypes,
        tree_ish: str = "HEAD") -> bytes:
    """
    get a archive of a git repo

        :param git_repo: Where the repo is
        :param archive_type: What archive type will be created
        :param tree_ish: What commit/branch to save, defaults to "HEAD"
        :raises GitException: Error to do with git
        :return: The content of the archive ready to write to a file
    """
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value
    process = await subprocess_run(
        ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish],
    )
    if process.returncode != 0:
        raise GitException(process.stderr.decode())
    return process.stdout


async def get_archive_buffered(
        git_repo: Union[Path, str],
        archive_type: ArchiveTypes,
        tree_ish: str = "HEAD") -> AsyncGenerator[bytes, None]:
    """
    get a archive of a git repo, but using a buffered read

        :param git_repo: Where the repo is
        :param archive_type: What archive type will be created
        :param tree_ish: What commit/branch to save, defaults to "HEAD"
        :raises GitException: Error to do with git
        :yield: Each read content section
    """
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value

    args = ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish]

    try:
        async for content in subprocess_run_buffered(args):
            yield content
    except BufferedProcessError as err:
        raise GitException(err.args[0].decode()) from err
