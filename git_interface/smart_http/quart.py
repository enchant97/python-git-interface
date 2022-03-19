"""
Smart HTTP Git helpers for quart
"""
from pathlib import Path

from async_timeout import timeout
from quart import Response, current_app, make_response, request

from ..pack import advertise_pack, exchange_pack

__all__ = [
    "post_pack_response", "get_info_refs_response",
]


async def post_pack_response(repo_path: Path, pack_type: str) -> Response:
    """
    Make the response for handling exchange pack responses,
    uses 'BODY_TIMEOUT' for a timeout of a request.

    A matching route should be: '/<repo_name>.git/<pack_type>'.

        :param repo_path: Path to the repo
        :param pack_type: The pack-type
        :return: The created response
    """
    async with timeout(current_app.config["BODY_TIMEOUT"]):
        response = await make_response(exchange_pack(
            repo_path,
            pack_type,
            request.body,
        ))
    response.content_type = f"application/x-{pack_type}-result"
    response.headers.add_header("Cache-Control", "no-store")
    response.headers.add_header("Expires", "0")
    return response


async def get_info_refs_response(repo_path, pack_type) -> Response:
    """
    Make the response for handling advertisements.

    A matching route should be: '/<repo_name>.git/info/refs',
    accessing the 'service' argument for pack_type.

        :param repo_path: Path to the repo
        :param pack_type: The pack-type
        :return: The created response
    """
    response = await make_response(advertise_pack(
        repo_path,
        pack_type,
    ))
    response.content_type = f"application/x-{pack_type}-advertisement"
    response.headers.add_header("Cache-Control", "no-store")
    response.headers.add_header("Expires", "0")
    return response
