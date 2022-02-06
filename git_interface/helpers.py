"""
Methods not related to git commands,
but to help the program function
"""
import asyncio
from collections.abc import AsyncGenerator, Coroutine, Iterable
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Union

from .exceptions import BufferedProcessError

__all__ = [
    "ensure_path", "subprocess_run",
    "subprocess_run_buffered",
]


def ensure_path(path_or_str: Union[Path, str]) -> Path:
    """
    Ensures that given value is a pathlib.Path object.

        :param path_or_str: Either a path string or pathlib.Path obj
        :return: The value as a pathlib.Path obj
    """
    return path_or_str if isinstance(path_or_str, Path) else Path(path_or_str)


async def subprocess_run(args: Iterable[str], **kwargs) -> Coroutine[Any, Any, CompletedProcess]:
    """
    Asynchronous alternative to using subprocess.run

        :param args: The arguments to run (len must be at least 1)
        :return: The completed process
    """
    process = await asyncio.create_subprocess_exec(
        args[0], *args[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        **kwargs
    )
    stdout, stderr = await process.communicate()
    return CompletedProcess(args, process.returncode, stdout, stderr)


async def subprocess_run_buffered(args: Iterable[str]) -> AsyncGenerator[bytes, None]:
    """
    Asynchronous alternative to using subprocess.Popen using buffered reading

        :param args: The arguments to run (len must be at least 1)
        :raises BufferedProcessError: Raised a non-zero return code is provided
        :yield: Each read content section
    """
    process = await asyncio.create_subprocess_exec(
        args[0], *args[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    async for line in process.stdout:
        yield line

    return_code = await process.wait()
    if return_code != 0:
        raise BufferedProcessError(await process.stderr.read(), return_code)
