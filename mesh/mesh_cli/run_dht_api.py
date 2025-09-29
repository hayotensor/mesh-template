from argparse import ArgumentParser
from secrets import token_hex
from signal import SIGINT, SIGTERM, signal, strsignal
from threading import Event, Thread

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.status import HTTP_403_FORBIDDEN

from mesh.dht import DHT, DHTNode
from mesh.mesh_cli.api.api_utils import get_active_keys, load_api_keys
from mesh.utils.dht import get_node_infos_sig
from mesh.utils.logging import get_logger, use_mesh_log_handler
from mesh.utils.networking import log_visible_maddrs

use_mesh_log_handler("in_root_logger")
logger = get_logger(__name__)

dht: DHT = None

"""
Bootnode API

Example:
    curl -H "X-API-Key: key-party1-abc123" http://localhost:8000/get_bootnodes

Create endpoint with NGINX for HTTPS encryption

Docs: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04#step-5-configuring-nginx-to-proxy-requests

server {
    listen 443 ssl;
    server_name bootnode.example.com;

    ssl_certificate /etc/letsencrypt/live/bootnode.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bootnode.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    api_keys: set[str] = load_api_keys()
    active_keys = get_active_keys(api_keys)
    if api_key_header in active_keys:
        return api_key_header
    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing API Key")

app = FastAPI()
# Limiter for API key
key_limiter = Limiter(key_func=lambda request: request.state.api_key)
# Limiter for IP
ip_limiter = Limiter(key_func=lambda request: request.client.host)
app.state.limiter = key_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware to attach api_key to request.state
@app.middleware("http")
async def attach_api_key(request: Request, call_next):
    api_key = request.query_params.get("api_key") or request.headers.get("x-api-key")
    request.state.api_key = api_key
    return await call_next(request)

@app.get("/get_heartbeat")
@ip_limiter.limit("5/minute")
@key_limiter.limit("5/minute")
async def get_heartbeat(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    """
    Query the DHT for the subnets heartbeats.
    """
    if dht is None:
        return {"error": "DHT not initialized"}
    result = get_node_infos_sig(
        dht,
        uid="node",
        latest=True
    )
    print("result", result)
    if result:
        try:
            return {"value": result.value, "expiration": result.expiration_time}
        except Exception as e:
            logger.warning(f"Error returning heartbeat {e}", exc_info=True)

    return {"value": None}

@app.get("/get_bootnodes")
@ip_limiter.limit("5/minute")
@key_limiter.limit("5/minute")
async def get_bootnodes(
    request: Request,
    api_key: str = Depends(get_api_key)
):
    """
    Query the DHT bootnodes.
    """
    if dht is None:
        return {"error": "DHT not initialized"}
    visible_maddrs = dht.get_visible_maddrs()
    print("visible_maddrs", visible_maddrs)
    if visible_maddrs:
        try:
            addrs = []
            for addr in visible_maddrs:
                addrs.append(str(addr))
            return {"value": addrs}
        except Exception as e:
            logger.warning(f"Error returning heartbeat {e}", exc_info=True)

    return {"value": None}

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Bootnode
"""
async def report_status(dht: DHT, node: DHTNode):
    logger.info(
        f"{len(node.protocol.routing_table.uid_to_peer_id) + 1} DHT nodes (including this one) "
        f"are in the local routing table "
    )
    logger.debug(f"Routing table contents: {node.protocol.routing_table}")
    logger.info(f"Local storage contains {len(node.protocol.storage)} keys")
    logger.debug(f"Local storage contents: {node.protocol.storage}")

    # Contact peers and keep the routing table healthy (remove stale PeerIDs)
    await node.get(f"heartbeat_{token_hex(16)}", latest=True)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--initial_peers",
        nargs="*",
        help="Multiaddrs of the peers that will welcome you into the existing DHT. "
        "Example: /ip4/203.0.113.1/tcp/31337/p2p/XXXX /ip4/203.0.113.2/tcp/7777/p2p/YYYY",
    )
    parser.add_argument(
        "--host_maddrs",
        nargs="*",
        default=["/ip4/0.0.0.0/tcp/0"],
        help="Multiaddrs to listen for external connections from other DHT instances. "
        "Defaults to all IPv4 interfaces and the TCP protocol: /ip4/0.0.0.0/tcp/0",
    )
    parser.add_argument(
        "--announce_maddrs",
        nargs="*",
        help="Visible multiaddrs the host announces for external connections from other DHT instances",
    )
    parser.add_argument(
        "--use_ipfs",
        action="store_true",
        help='Use IPFS to find initial_peers. If enabled, you only need to provide the "/p2p/XXXX" '
        "part of the multiaddrs for the initial_peers "
        "(no need to specify a particular IPv4/IPv6 host and port)",
    )
    parser.add_argument(
        "--identity_path",
        help="Path to a private key file. If defined, makes the peer ID deterministic. "
        "If the file does not exist, writes a new private key to this file.",
    )
    parser.add_argument(
        "--use_relay",
        action="store_true",
        dest="use_relay",
        help="Disable circuit relay functionality in libp2p (see https://docs.libp2p.io/concepts/nat/circuit-relay/)",
    )
    parser.add_argument(
        "--use_auto_relay",
        action="store_true",
        help="Look for libp2p relays to become reachable if we are behind NAT/firewall",
    )
    parser.add_argument(
        "--refresh_period", type=int, default=30, help="Period (in seconds) for fetching the keys from DHT"
    )

    args = parser.parse_args()

    global dht
    dht = DHT(
        start=True,
        initial_peers=args.initial_peers,
        host_maddrs=args.host_maddrs,
        announce_maddrs=args.announce_maddrs,
        use_ipfs=args.use_ipfs,
        identity_path=args.identity_path,
        use_relay=args.use_relay,
        use_auto_relay=args.use_auto_relay,
    )
    log_visible_maddrs(dht.get_visible_maddrs(), only_p2p=args.use_ipfs)

    # Run the FastAPI server in a thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()

    exit_event = Event()

    def signal_handler(signal_number: int, _) -> None:
        logger.info(f"Caught signal {signal_number} ({strsignal(signal_number)}), shutting down")
        exit_event.set()

    signal(SIGTERM, signal_handler)
    signal(SIGINT, signal_handler)

    try:
        while not exit_event.is_set():
            dht.run_coroutine(report_status, return_future=False)
            exit_event.wait(args.refresh_period)
    finally:
        dht.shutdown()


if __name__ == "__main__":
    main()
