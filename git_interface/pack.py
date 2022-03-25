"""
Methods for using commands relating to git packs
"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Union

from .exceptions import BufferedProcessError

__all__ = [
    "UPLOAD_PACK_TYPE", "RECEIVE_PACK_TYPE",
    "ALLOWED_PACK_TYPES", "exchange_pack",
    "advertise_pack",
]

UPLOAD_PACK_TYPE = "git-upload-pack"
RECEIVE_PACK_TYPE = "git-receive-pack"
ALLOWED_PACK_TYPES = (UPLOAD_PACK_TYPE, RECEIVE_PACK_TYPE)


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
            if chunk.endswith(b"done\n"):
                # allows for ssh style pack exchange
                break
        process.stdin.write_eof()
    else:
        yield _create_advertisement(pack_type)

    async for chunk in process.stdout:
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
