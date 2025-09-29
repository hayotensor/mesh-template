import inspect
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

# from mesh import PeerID
from mesh.proto.auth_pb2 import AccessToken

# from mesh.subnet.utils.peer_id import get_ed25519_peer_id, get_rsa_peer_id
# from mesh.substrate.chain_functions import Hypertensor
from mesh.utils.asyncio import (
    anext,
)
from mesh.utils.authorizers.auth import AuthorizedRequestBase, AuthorizedResponseBase, AuthorizerBase
from mesh.utils.crypto import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    RSAPrivateKey,
    RSAPublicKey,
    load_public_key_from_bytes,
)
from mesh.utils.logging import get_logger
from mesh.utils.proof_of_stake import ProofOfStake
from mesh.utils.timed_storage import TimedStorage, get_dht_time

logger = get_logger(__name__)

class ProofOfStakeAuthorizer(AuthorizerBase):
    """
    Implements a proof-of-stake authorization protocol using RSA and Ed25519 keys
    Checks the Hypertensor network for nodes ``peer_id`` is staked.
    The ``peer_id`` is retrieved using the RSA or Ed25519 public key
    """

    def __init__(
        self,
        local_private_key: RSAPublicKey | Ed25519PrivateKey,
        pos: ProofOfStake
    ):
        super().__init__()
        self._local_private_key = local_private_key
        self._local_public_key = local_private_key.get_public_key()
        self.pos = pos

        self._local_access_token = None

        self._recent_nonces = TimedStorage()

    async def get_token(self) -> AccessToken:
        # Uses the built in template ``AccessToken`` format
        token = AccessToken(
            username='',
            public_key=self._local_public_key.to_bytes(),
            expiration_time=str(datetime.now(timezone.utc) + timedelta(minutes=1)),
        )
        token.signature = self._local_private_key.sign(self._token_to_bytes(token))
        return token

    @staticmethod
    def _token_to_bytes(access_token: AccessToken) -> bytes:
        return f"{access_token.username} {access_token.public_key} {access_token.expiration_time}".encode()

    async def sign_request(self, request: AuthorizedRequestBase, service_public_key: Optional[Ed25519PrivateKey | RSAPrivateKey]) -> None:
        auth = request.auth

        local_access_token = await self.get_token()
        auth.client_access_token.CopyFrom(local_access_token)

        if service_public_key is not None:
            auth.service_public_key = service_public_key.to_bytes()
        auth.time = get_dht_time()

        auth.nonce = secrets.token_bytes(8)


        assert auth.signature == b""
        auth.signature = self._local_private_key.sign(request.SerializeToString())

    _MAX_CLIENT_SERVICER_TIME_DIFF = timedelta(minutes=1)

    async def validate_request(self, request: AuthorizedRequestBase) -> bool:
        auth = request.auth

        client_public_key = load_public_key_from_bytes(auth.client_access_token.public_key)

        signature = auth.signature
        auth.signature = b""
        if not client_public_key.verify(request.SerializeToString(), signature):
            logger.debug("Request has invalid signature")
            return False

        if auth.service_public_key and auth.service_public_key != self._local_public_key.to_bytes():
            logger.debug("Request is generated for a peer with another public key")
            return False

        with self._recent_nonces.freeze():
            current_time = get_dht_time()
            if abs(auth.time - current_time) > self._MAX_CLIENT_SERVICER_TIME_DIFF.total_seconds():
                logger.debug("Clocks are not synchronized or a previous request is replayed again")
                return False
            if auth.nonce in self._recent_nonces:
                logger.debug("Previous request is replayed again")
                return False

        if auth.nonce in self._recent_nonces:
            logger.debug("Previous request is replayed again")
            return False

        # Verify proof of stake
        try:
            proof_of_stake = self.pos.proof_of_stake(client_public_key)
            return proof_of_stake
        except Exception as e:
            logger.debug("Proof of stake failed, validate request", e, exc_info=True)

        self._recent_nonces.store(
            auth.nonce, None, current_time + self._MAX_CLIENT_SERVICER_TIME_DIFF.total_seconds() * 3
        )
        return True

    async def sign_response(self, response: AuthorizedResponseBase, request: AuthorizedRequestBase) -> None:
        auth = response.auth

        # auth.service_access_token.CopyFrom(self._local_access_token)
        local_access_token = await self.get_token()
        auth.service_access_token.CopyFrom(local_access_token)
        auth.nonce = request.auth.nonce

        assert auth.signature == b""
        auth.signature = self._local_private_key.sign(response.SerializeToString())

    async def validate_response(self, response: AuthorizedResponseBase, request: AuthorizedRequestBase) -> bool:
        if inspect.isasyncgen(response):
            # asyncgenerator block for inference protocol
            response = await anext(response)
            auth = response.auth
        else:
            auth = response.auth

        service_public_key = load_public_key_from_bytes(auth.service_access_token.public_key)

        signature = auth.signature
        auth.signature = b""
        if not service_public_key.verify(response.SerializeToString(), signature):
            logger.debug("Response has invalid signature")
            return False

        if auth.nonce != request.auth.nonce:
            logger.debug("Response is generated for another request")
            return False

        # Verify proof of stake
        try:
            proof_of_stake = self.pos.proof_of_stake(service_public_key)
            return proof_of_stake
        except Exception as e:
            logger.debug("Proof of stake failed, validate request", e, exc_info=True)

        return True

    @property
    def local_public_key(self) -> RSAPublicKey | Ed25519PublicKey:
        return self._local_public_key
