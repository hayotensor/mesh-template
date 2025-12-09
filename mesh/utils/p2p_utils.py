import asyncio
import functools
import re

import requests
from async_timeout import timeout

import mesh
from mesh.subnet.protocols.mock_protocol import MockProtocol

info_cache = mesh.TimedStorage()


async def check_reachability(peer_id, _, node, *, fetch_info=False, connect_timeout=5, expiration=300, use_cache=True):
    if use_cache:
        entry = info_cache.get(peer_id)
        if entry is not None:
            return entry.value

    try:
        async with timeout(connect_timeout):
            if fetch_info:
                # For Peer
                stub = MockProtocol.get_server_stub(node.p2p, peer_id)
                response = await stub.rpc_info(mesh.proto.runtime_pb2.Empty())
                rpc_info = mesh.MSGPackSerializer.loads(response.serialized_info)
                rpc_info["ok"] = True
            else:
                # For Bootstrap
                await node.p2p._client.connect(peer_id, [])
                await node.p2p._client.disconnect(peer_id)
                rpc_info = {"ok": True}
    except Exception as e:
        if not isinstance(e, asyncio.TimeoutError):
            message = str(e) if str(e) else repr(e)
            if message == "protocol not supported":
                return {"ok": True}
        else:
            message = f"Failed to connect in {connect_timeout:.0f} sec. Firewall may be blocking connections"
        rpc_info = {"ok": False, "error": message}

    info_cache.store(peer_id, rpc_info, mesh.get_dht_time() + expiration)
    return rpc_info


async def check_reachability_parallel(peer_ids, dht, node, *, fetch_info=False):
    rpc_infos = await asyncio.gather(
        *[check_reachability(peer_id, dht, node, fetch_info=fetch_info) for peer_id in peer_ids]
    )
    return dict(zip(peer_ids, rpc_infos))


async def get_peers_ips(dht, dht_node):
    return await dht_node.p2p.list_peers()


@functools.cache
def get_location(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}


def extract_peer_ip_info(multiaddr_str):
    if ip_match := re.search(r"/ip4/(\d+\.\d+\.\d+\.\d+)", multiaddr_str):
        return get_location(ip_match[1])
    return {}


def get_multiple_locations(ip_addresses: list):
    """
    Get location info for multiple IP addresses in a single batch request.

    :param ip_addresses: List of IP address strings, e.g. ["208.80.152.201", "91.198.174.192"]
    :returns: List of location dicts from ip-api.com
    """
    try:
        response = requests.post("http://ip-api.com/batch", json=ip_addresses)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


def extract_multiple_peer_ips_info(multiaddrs: list) -> dict:
    """
    Extract IP addresses from a list of multiaddrs and get location info for all in a single batch request.

    :param multiaddrs: List of multiaddr strings, e.g. ["/ip4/208.80.152.201/tcp/4001", "/ip4/91.198.174.192/tcp/4001"]
    :returns: Dict mapping IP addresses to their location info
    """
    # Extract all IPs from multiaddrs
    ip_addresses = []
    for multiaddr in multiaddrs:
        if ip_match := re.search(r"/ip4/(\d+\.\d+\.\d+\.\d+)", multiaddr):
            ip_addresses.append(ip_match[1])

    if not ip_addresses:
        return {}

    # Get locations for all IPs in one batch request
    locations = get_multiple_locations(ip_addresses)

    # Map results by the query IP
    return {loc["query"]: loc for loc in locations if loc.get("query")}
