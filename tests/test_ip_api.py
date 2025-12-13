from subnet.utils.p2p_utils import extract_multiple_peer_ips_info, get_multiple_locations

# pytest tests/test_ip_api.py::test_ip_api -rP


def test_ip_api():
    subnets_data = get_multiple_locations(["208.80.152.201", "91.198.174.192"])
    print(subnets_data)


# pytest tests/test_ip_api.py::test_extract_multiple_peer_ips_info -rP


def test_extract_multiple_peer_ips_info():
    multiaddrs = ["/ip4/208.80.152.201/tcp/4001", "/ip4/91.198.174.192/tcp/4001"]
    peer_ips_info = extract_multiple_peer_ips_info(multiaddrs)
    print(peer_ips_info)


def serialize_object(obj):
    """Recursively serialize objects to JSON-compatible formats"""
    # Handle None
    if obj is None:
        return None

    # Handle primitive types
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Handle peer_id specifically (libp2p ID objects)
    if hasattr(obj, "_b58_str"):
        return obj._b58_str  # Return the base58 string representation

    # Handle enums
    if hasattr(obj, "value") and hasattr(obj, "name"):
        return obj.name

    # Handle lists/tuples
    if isinstance(obj, (list, tuple)):
        return [serialize_object(item) for item in obj]

    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: serialize_object(value) for key, value in obj.items()}

    # Handle objects with __dict__ (most custom classes)
    if hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            # Skip private/internal attributes
            if key.startswith("_"):
                continue
            result[key] = serialize_object(value)
        return result

    # Fallback to string representation
    return str(obj)


class PeerInfo:
    def __init__(self, peer_id: str, addrs: list[str]):
        self.peer_id = peer_id
        self.addrs = addrs


# pytest tests/test_ip_api.py::test_dht_api_get_peers_info -rP


def test_dht_api_get_peers_info():
    peers_list = [
        PeerInfo(
            "QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwiG",
            ["/ip4/208.80.152.201/tcp/4001"],
        ),
        PeerInfo(
            "QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwi1",
            ["/ip4/91.198.174.192/tcp/4001"],
        ),
    ]
    ip_to_peer_id = {}
    for peer_info in peers_list:
        for addr in peer_info.addrs:
            addr_str = str(addr)
            # Extract IP from multiaddr
            import re

            if ip_match := re.search(r"/ip4/(\d+\.\d+\.\d+\.\d+)", addr_str):
                ip = ip_match[1]
                ip_to_peer_id[ip] = str(peer_info.peer_id)

    # 2. Get all multiaddrs and fetch locations in batch
    multiaddrs = [str(addr) for peer_info in peers_list for addr in peer_info.addrs]
    ip_locations = extract_multiple_peer_ips_info(multiaddrs)  # {ip: location_data}

    # 3. Build the result keyed by peer_id
    result = {}
    for ip, location_data in ip_locations.items():
        peer_id = ip_to_peer_id.get(ip)
        if peer_id:
            if peer_id not in result:
                result[peer_id] = {}
            result[peer_id][ip] = location_data

    serialized_results = serialize_object(result)
    print(serialized_results)


MAX_IP_ADDRESSES_PER_REQUEST = 1

# pytest tests/test_ip_api.py::test_dht_api_get_peers_info_batch -rP


def test_dht_api_get_peers_info_batch():
    peers_list = [
        PeerInfo(
            "QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwiG",
            ["/ip4/208.80.152.201/tcp/4001"],
        ),
        PeerInfo(
            "QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwi1",
            ["/ip4/91.198.174.192/tcp/4001"],
        ),
    ]

    ip_to_peer_id = {}
    all_ips = []
    for peer_info in peers_list:
        for addr in peer_info.addrs:
            addr_str = str(addr)
            import re

            if ip_match := re.search(r"/ip4/(\d+\.\d+\.\d+\.\d+)", addr_str):
                ip = ip_match[1]
                if ip not in ip_to_peer_id:  # Avoid duplicates
                    ip_to_peer_id[ip] = str(peer_info.peer_id)
                    all_ips.append(ip)

    # 2. Batch IP lookups in chunks of MAX_IP_ADDRESSES_PER_REQUEST
    from subnet.utils.p2p_utils import get_multiple_locations

    ip_locations = {}
    for i in range(0, len(all_ips), MAX_IP_ADDRESSES_PER_REQUEST):
        batch = all_ips[i : i + MAX_IP_ADDRESSES_PER_REQUEST]
        batch_results = get_multiple_locations(batch)
        # Merge results into ip_locations dict
        for loc in batch_results:
            if loc.get("query"):
                ip_locations[loc["query"]] = loc

    # 3. Build the result keyed by peer_id
    result = {}
    for ip, location_data in ip_locations.items():
        peer_id = ip_to_peer_id.get(ip)
        if peer_id:
            if peer_id not in result:
                result[peer_id] = {}
            result[peer_id][ip] = location_data

    serialized_results = serialize_object(result)
    print(serialized_results)
