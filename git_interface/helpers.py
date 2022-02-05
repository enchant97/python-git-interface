"""
Methods not related to git commands,
but to help the program function
"""
import asyncio
from collections.abc import Iterable
from pathlib import Path
from subprocess import CompletedProcess
from typing import Union

__all__ = [
    "ensure_path", "subprocess_run"
]


def ensure_path(path_or_str: Union[Path, str]) -> Path:
    """
    Ensures that given value is a pathlib.Path object.

        :param path_or_str: Either a path string or pathlib.Path obj
        :return: The value as a pathlib.Path obj
    """
    return path_or_str if isinstance(path_or_str, Path) else Path(path_or_str)


async def subprocess_run(args: Iterable[str]) -> CompletedProcess:
    """
    Asynchronous alternative to using subprocess.run

        :param args: The  arguments to run (len must be at least 1)
        :return: The completed process
    """
    process = await asyncio.create_subprocess_exec(
        args[0], *args[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return CompletedProcess(args, process.returncode, stdout, stderr)
