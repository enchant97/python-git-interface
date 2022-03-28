import asyncio
import re
import sys
from os import environ
from pathlib import Path
from typing import Optional, Union

import asyncssh

from ..constants import VALID_SSH_COMMAND_RE
from ..pack import ssh_pack_exchange
from ..shared import logger

__all__ = [
    "NoAuthHandler", "Server"
]


class NoAuthHandler(asyncssh.SSHServer):
    """
    basic ssh server handler that provides no authentication
    """
    def connection_made(self, conn: asyncssh.SSHServerConnection):
        logger.info("SSH connection received from: %s", conn.get_extra_info('peername')[0])

    def connection_lost(self, exc: Optional[Exception]):
        if exc:
            logger.error("SSH connection closed, with error: %s", exc)
        else:
            logger.info("SSH connection closed")

    def begin_auth(self, username: str) -> bool:
        logger.debug("begining fake auth with user: %s", username)
        return False

    def password_auth_supported(self) -> bool:
        return True


class Server:
    """
    Handles creation of a ssh server, with client handler
    that can inherited to adjust functionality
    """
    _no_command_msg = b"Successfully authenticated, but this server does not provide shell access"
    _no_repo_msg = b"request path does not exist, or you do not have access"

    def __init__(
            self,
            root_repo_path: str,
            handler_class: asyncssh.SSHServer = NoAuthHandler):
        self._root_repo_path = root_repo_path
        self._handler_class = handler_class

    def ensure_valid_repo(self, requested_repo: str, username: str) -> Union[Path, None]:
        """
        Used to ensure a given path is a valid repo,
        username currently not used but this method
        could be overridden to implement custom functionality

            :param requested_repo: The requested repo path (relative)
            :param username: The username for the connected client
            :return: The absolute repo path, or None if path was invalid
        """
        repo_path: Path = self._root_repo_path / requested_repo.removeprefix("/")
        if repo_path.exists():
            return repo_path

    def peer_allowed(peername: str) -> bool:
        """
        Blueprint method used to validate
        whether a peername is allowed to use ssh,

            :param peername: The peername
            :return: Whether peername is allowed
        """
        return True

    def username_valid(username: str) -> bool:
        """
        Blueprint method used to validate
        whether a username is valid,

            :param username: The username
            :return: Whether username is valid
        """
        return True

    async def handle_client(self, process: asyncssh.SSHServerProcess):
        """
        Method used when client has been authenticated,
        provides git pack exchange,
        validation provided by:
        ensure_valid_repo, peer_allowed and username_valid

            :param process: The SSHServerProcess
        """
        peer_name = process.get_extra_info('peername')[0]
        username = process.get_extra_info('username')

        if not self.peer_allowed(peer_name):
            logger.error("client with peername: '%s' was denied", peer_name)
            process.exit(0)
            return

        if not self.username_valid(username):
            logger.debug("username: '%s' was invalid, received from '%s'", username, peer_name)
            process.exit(0)
            return

        logger.debug("handling client: %s at %s", username, peer_name)

        if process.command is None:
            process.stdout.write(self._no_command_msg)
            process.exit(0)
            return

        if match := re.match(VALID_SSH_COMMAND_RE, process.command):
            pack_type = match.group(1)
            logger.debug(
                "pack_type: '%s' received from '%s'",
                pack_type, peer_name
            )

            repo_path = match.group(2)
            logger.debug("repo path: '%s' received from '%s'", repo_path, peer_name)
            repo_path = self.ensure_valid_repo(repo_path, username)

            if not repo_path:
                logger.debug("invalid repo path: '%s' received from '%s'", repo_path, peer_name)
                process.stdout.write(self._no_repo_msg)
                process.exit(0)
                return

            async for chunk in ssh_pack_exchange(repo_path, pack_type, process.stdin):
                process.stdout.write(chunk)

        process.exit(0)

    async def create_server(self, host: str, port: int, host_keys: list[str]):
        """
        Create the SSH server to run

            :param host: The host to listen for connections on
            :param port: The port to listen on
            :param host_keys: the private ssh keys file path
            :return: The created SSH server
        """
        return await asyncssh.create_server(
            self._handler_class, host, port,
            server_host_keys=host_keys,
            process_factory=self.handle_client,
            encoding=None
        )


async def main():
    host = environ["SSH_HOST"]
    port = int(environ["SSH_PORT"])
    host_keys = environ["SSH_HOST_KEY"]
    repo_root = Path(environ["SSH_REPO_ROOT"])

    server = Server(repo_root)
    await server.create_server(host, port, [host_keys])


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
        loop.run_forever()
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error starting server: ' + str(exc))
