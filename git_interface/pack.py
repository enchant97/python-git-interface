"""
Methods for using commands relating to git packs
"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Union

from .constants import ALLOWED_PACK_TYPES, RECEIVE_PACK_TYPE, UPLOAD_PACK_TYPE
from .exceptions import BufferedProcessError
from .helpers import chunk_yielder
from .shared import logger

__all__ = [
    "UPLOAD_PACK_TYPE", "RECEIVE_PACK_TYPE",
    "ALLOWED_PACK_TYPES", "exchange_pack",
    "advertise_pack",
]


def _create_advertisement(pack_type) -> bytes:
    """
    Service type prefixed with the total line length
    """
    advertisement = f"# service={pack_type}\n".encode()
    hex_len = hex(len(advertisement) + 4)[2:]
    hex_len = hex_len.zfill(4)
    advertisement = hex_len.encode() + advertisement + b"0000"
    return advertisement


async def _pack_handler(
        git_repo: Path,
        pack_type: str,
        input_stream: Union[AsyncGenerator[bytes, None], None] = None
    ) -> AsyncGenerator[bytes, None]:
    """
    Used to upload or receive a pack.

    When input_stream is None, sends advertisement instead

        :param git_repo: Path to the repo
        :param pack_type: The pack type
        :param input_stream: The input stream, defaults to None
        :return: The output stream
    """
    if pack_type not in ALLOWED_PACK_TYPES:
        raise ValueError("Invalid pack_type argument")

    args = ["git", pack_type.removeprefix("git-"), "--stateless-rpc"]
    if input_stream is None:
        args.append("--http-backend-info-refs")
    args.append(str(git_repo))

    process = await asyncio.create_subprocess_exec(
        args[0], *args[1:],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    if input_stream is not None:
        async for chunk in input_stream:
            process.stdin.write(chunk)
            if chunk.endswith(b"done\n"):
                # allows for ssh style pack exchange
                break
        process.stdin.write_eof()
    else:
        yield _create_advertisement(pack_type)

    async for chunk in chunk_yielder(process.stdout):
        yield chunk

    return_code = await process.wait()
    if return_code != 0:
        raise BufferedProcessError(await process.stderr.read(), return_code)


def exchange_pack(
        git_repo: Union[Path, str],
        pack_type: str,
        input_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
    """
    Used to exchange packs between client and remote.

    :param git_repo: Path to the repo
    :param pack_type: The pack-type ('git-upload-pack' or 'git-receive-pack')
    :param input_stream: The buffered input stream
    :return: The buffered output stream as a AsyncGenerator
    """
    return _pack_handler(git_repo, pack_type, input_stream)


def advertise_pack(
        git_repo: Union[Path, str],
        pack_type: str) -> AsyncGenerator[bytes, None]:
    """
    Used to advertise packs between remote and client.

    :param git_repo: Path to the repo
    :param pack_type: The pack-type ('git-upload-pack' or 'git-receive-pack')
    :return: The buffered output stream as a AsyncGenerator
    """
    return _pack_handler(git_repo, pack_type)


async def ssh_pack_exchange(
        git_repo: Union[str, Path],
        pack_type: str,
        stdin: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
    """
    Used to handle git pack exchange for a ssh connection.

        :param git_repo: Path to the repo
        :param pack_type: The pack-type ('git-upload-pack' or 'git-receive-pack')
        :param stdin: Input to feed from client
        :yield: Output to send to client
    """
    advert_stdout = advertise_pack(git_repo, pack_type)
    # skips http 'advertisement' provided by _pack_handler
    await advert_stdout.__anext__()

    async for chunk in advert_stdout:
        yield chunk

    logger.debug("git advert done for: %s", git_repo)

    async for chunk in exchange_pack(git_repo, pack_type, stdin):
        yield chunk

    logger.debug("git pack exchange done for: %s", git_repo)
