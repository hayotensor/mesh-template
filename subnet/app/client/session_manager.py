from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from subnet import get_logger
from subnet.app.client.routing.routing_manager import RemoteManager
from subnet.app.client.session import Session
from subnet.utils.authorizers.auth import AuthorizerBase

logger = get_logger(__name__)


class SessionManager:
    """
    Stateless manager: just creates SessionManager instances on demand.
    Does not keep track of sessions or history.
    """

    def __init__(
        self,
        remote_manager: RemoteManager,
        authorizer: Optional[AuthorizerBase] = None,
    ):
        self._remote_manager = remote_manager
        self._authorizer = authorizer

    @asynccontextmanager
    async def session(self) -> AsyncIterator[Session]:
        session = Session(self._remote_manager, self._authorizer)
        try:
            yield session
        finally:
            await session.close()
