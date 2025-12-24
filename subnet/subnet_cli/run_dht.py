# import os
# from argparse import ArgumentParser
# from pathlib import Path
# from secrets import token_hex
# from signal import SIGINT, SIGTERM, signal, strsignal
# from threading import Event

# from dotenv import load_dotenv
# from substrateinterface import Keypair, KeypairType

# from subnet.dht import DHT, DHTNode
# from subnet.dht.crypto import SignatureValidator
# from subnet.substrate.chain_functions import Hypertensor, KeypairFrom
# from subnet.substrate.mock.local_chain_functions import LocalMockHypertensor
# from subnet.utils.authorizers.auth import SignatureAuthorizer
# from subnet.utils.authorizers.pos_auth import ProofOfStakeAuthorizer
# from subnet.utils.key import get_peer_id_from_identity_path, get_private_key
# from subnet.utils.logging import get_logger, setup_mp_logging, use_subnet_log_handler
# from subnet.utils.networking import log_visible_maddrs
# from subnet.utils.proof_of_stake import ProofOfStake

# use_subnet_log_handler("in_root_logger")
# logger = get_logger(__name__)

# setup_mp_logging()

# load_dotenv(os.path.join(Path.cwd(), ".env"))

# PHRASE = os.getenv("PHRASE")

# """
# Bootstrap node
# """


# async def report_status(dht: DHT, node: DHTNode):
#     logger.info(
#         f"{len(node.protocol.routing_table.uid_to_peer_id) + 1} DHT nodes (including this one) "
#         f"are in the local routing table "
#     )
#     logger.debug(f"Routing table contents: {node.protocol.routing_table}")
#     logger.info(f"Local storage contains {len(node.protocol.storage)} keys")
#     logger.debug(f"Local storage contents: {node.protocol.storage}")

#     # Contact peers and keep the routing table healthy (remove stale PeerIDs)
#     await node.get(f"heartbeat_{token_hex(16)}", latest=True)


# def main():
#     parser = ArgumentParser()
#     parser.add_argument(
#         "--initial_peers",
#         nargs="*",
#         help="Multiaddrs of the peers that will welcome you into the existing DHT. "
#         "Example: /ip4/203.0.113.1/tcp/31337/p2p/XXXX /ip4/203.0.113.2/tcp/7777/p2p/YYYY",
#     )
#     parser.add_argument(
#         "--host_maddrs",
#         nargs="*",
#         default=["/ip4/0.0.0.0/tcp/0"],
#         help="Multiaddrs to listen for external connections from other DHT instances. "
#         "Defaults to all IPv4 interfaces and the TCP protocol: /ip4/0.0.0.0/tcp/0",
#     )
#     parser.add_argument(
#         "--announce_maddrs",
#         nargs="*",
#         help="Visible multiaddrs the host announces for external connections from other DHT instances",
#     )
#     parser.add_argument(
#         "--use_ipfs",
#         action="store_true",
#         help='Use IPFS to find initial_peers. If enabled, you only need to provide the "/p2p/XXXX" '
#         "part of the multiaddrs for the initial_peers "
#         "(no need to specify a particular IPv4/IPv6 host and port)",
#     )
#     parser.add_argument(
#         "--identity_path",
#         help="Path to a private key file. If defined, makes the peer ID deterministic. "
#         "If the file does not exist, writes a new private key to this file.",
#     )
#     parser.add_argument(
#         "--use_relay",
#         action="store_true",
#         dest="use_relay",
#         help="Disable circuit relay functionality in libp2p (see https://docs.libp2p.io/concepts/nat/circuit-relay/)",
#     )
#     parser.add_argument(
#         "--use_auto_relay",
#         action="store_true",
#         help="Look for libp2p relays to become reachable if we are behind NAT/firewall",
#     )
#     parser.add_argument(
#         "--refresh_period", type=int, default=30, help="Period (in seconds) for fetching the keys from DHT"
#     )
#     parser.add_argument("--subnet_id", type=int, required=False, default=None, help="Subnet ID running a node for ")
#     parser.add_argument("--no_blockchain_rpc", action="store_true", help="[Testing] Run with no RPC")
#     parser.add_argument("--local_rpc", action="store_true", help="[Testing] Run in local RPC mode, uses LOCAL_RPC")
#     parser.add_argument(
#         "--phrase",
#         type=str,
#         required=False,
#         help="[Testing] Coldkey phrase that controls actions which include funds, such as registering, and staking",
#     )
#     parser.add_argument("--private_key", type=str, required=False, help="[Testing] Hypertensor blockchain private key")

#     args = parser.parse_args()
#     subnet_id = args.subnet_id
#     no_blockchain_rpc = args.no_blockchain_rpc
#     local_rpc = args.local_rpc
#     phrase = args.phrase
#     private_key = args.private_key

#     if not no_blockchain_rpc:
#         if local_rpc:
#             rpc = os.getenv("LOCAL_RPC")
#         else:
#             rpc = os.getenv("DEV_RPC")

#         if phrase is not None:
#             hypertensor = Hypertensor(rpc, phrase)
#         elif private_key is not None:
#             hypertensor = Hypertensor(rpc, private_key, KeypairFrom.PRIVATE_KEY)
#             keypair = Keypair.create_from_private_key(private_key, crypto_type=KeypairType.ECDSA)
#             hotkey = keypair.ss58_address
#             logger.info(f"hotkey: {hotkey}")
#         else:
#             hypertensor = Hypertensor(rpc, PHRASE)
#     else:
#         peer_id = get_peer_id_from_identity_path(args.identity_path)
#         reset_db = False
#         if not args.initial_peers:
#             # Reset when deploying a new swarm
#             reset_db = True
#         hypertensor = LocalMockHypertensor(
#             subnet_id=subnet_id,
#             peer_id=peer_id,
#             subnet_node_id=0,
#             coldkey="",
#             hotkey="",
#             bootnode_peer_id="",
#             client_peer_id="",
#             reset_db=reset_db,
#         )

#     pk = get_private_key(args.identity_path)
#     signature_validator = SignatureValidator(pk)
#     record_validators = [signature_validator]
#     signature_authorizer = SignatureAuthorizer(pk)

#     if hypertensor is not None:
#         print("Initializing PoS - proof-of-stake")
#         logger.info("Initializing PoS - proof-of-stake")
#         pos = ProofOfStake(
#             subnet_id,
#             hypertensor,
#             min_class=0,
#         )
#         pos_authorizer = ProofOfStakeAuthorizer(signature_authorizer, pos)
#     else:
#         print("Initializing sig authorizer")
#         # For testing purposes, at minimum require signatures
#         pos_authorizer = signature_authorizer

#     # dht = DHT(
#     #     start=True,
#     #     initial_peers=args.initial_peers,
#     #     host_maddrs=args.host_maddrs,
#     #     announce_maddrs=args.announce_maddrs,
#     #     use_ipfs=args.use_ipfs,
#     #     identity_path=args.identity_path,
#     #     use_relay=args.use_relay,
#     #     use_auto_relay=args.use_auto_relay,
#     # )
#     dht = DHT(
#         start=True,
#         initial_peers=args.initial_peers,
#         host_maddrs=args.host_maddrs,
#         announce_maddrs=args.announce_maddrs,
#         use_ipfs=args.use_ipfs,
#         identity_path=args.identity_path,
#         use_relay=args.use_relay,
#         use_auto_relay=args.use_auto_relay,
#         record_validators=record_validators,
#         **dict(authorizer=pos_authorizer),
#     )

#     log_visible_maddrs(dht.get_visible_maddrs(), only_p2p=args.use_ipfs)

#     exit_event = Event()

#     def signal_handler(signal_number: int, _) -> None:
#         logger.info(f"Caught signal {signal_number} ({strsignal(signal_number)}), shutting down")
#         exit_event.set()

#     signal(SIGTERM, signal_handler)
#     signal(SIGINT, signal_handler)

#     try:
#         while not exit_event.is_set():
#             dht.run_coroutine(report_status, return_future=False)
#             exit_event.wait(args.refresh_period)
#     finally:
#         dht.shutdown()


# if __name__ == "__main__":
#     main()
