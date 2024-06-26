"""
Methods not related to git commands,
but to help the program function
"""
import asyncio
from collections.abc import AsyncGenerator, Sequence
from pathlib import Path
from subprocess import CompletedProcess

from .constants import DEFAULT_BUFFER_SIZE
from .exceptions import BufferedProcessError

__all__ = [
    "ensure_path",
    "chunk_yielder",
    "subprocess_run",
    "subprocess_run_buffered",
]


def ensure_path(path_or_str: Path | str) -> Path:
    """
    Ensures that given value is a pathlib.Path object.

        :param path_or_str: Either a path string or pathlib.Path obj
        :return: The value as a pathlib.Path obj
    """
    return path_or_str if isinstance(path_or_str, Path) else Path(path_or_str)


async def chunk_yielder(input_stream: asyncio.StreamReader) -> AsyncGenerator[bytes, None]:
    """
    reads from a stream chunk by chunk until EOF.
    Uses DEFAULT_BUFFER_SIZE to determine max chunk size

        :param input_stream: The stream to read
        :yield: Each chunk
    """
    while (chunk := await input_stream.read(DEFAULT_BUFFER_SIZE)) != b"":
        yield chunk


async def subprocess_run(args: Sequence[str], **kwargs) -> CompletedProcess[bytes]:
    """
    Asynchronous alternative to using subprocess.run

        :param args: The arguments to run (len must be at least 1)
        :return: The completed process
    """
    process = await asyncio.create_subprocess_exec(
        args[0], *args[1:], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs
    )
    stdout, stderr = await process.communicate()
    return CompletedProcess(list(args), process.returncode or 0, stdout, stderr)


async def subprocess_run_buffered(args: Sequence[str]) -> AsyncGenerator[bytes, None]:
    """
    Asynchronous alternative to using subprocess.Popen using buffered reading

        :param args: The arguments to run (len must be at least 1)
        :raises BufferedProcessError: Raised a non-zero return code is provided
        :yield: Each read content section
    """
    process = await asyncio.create_subprocess_exec(
        args[0],
        *args[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    async for chunk in chunk_yielder(process.stdout):
        yield chunk

    return_code = await process.wait()
    if return_code != 0:
        raise BufferedProcessError(await process.stderr.read(), return_code)
