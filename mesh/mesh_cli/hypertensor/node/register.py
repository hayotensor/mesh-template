import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from mesh.substrate.chain_functions import Hypertensor, KeypairFrom
from mesh.utils.logging import get_logger

load_dotenv(os.path.join(Path.cwd(), '.env'))

PHRASE = os.getenv('PHRASE')

logger = get_logger(__name__)

"""
register-node \
--subnet_id 1 \
--hotkey 0x773539d4Ac0e786233D90A233654ccEE26a613D9 \
--peer_id QmTJ8uyLJBwVprejUQfYFAywdXWfdnUQbC1Xif6QiTNta9 \
--bootnode_peer_id QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj7v \
--bootnode /ip4/127.00.1/tcp/31330/p2p/QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj7v \
--client_peer_id QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwiG \
--delegate_reward_rate 0.125 \
--stake_to_be_added 100.00

# Local

register-node \
--subnet_id 1 \
--hotkey 0x773539d4Ac0e786233D90A233654ccEE26a613D9 \
--peer_id QmTJ8uyLJBwVprejUQfYFAywdXWfdnUQbC1Xif6QiTNta9 \
--bootnode_peer_id QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj7v \
--bootnode /ip4/127.00.1/tcp/31330/p2p/QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj7v \
--client_peer_id QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwiG \
--delegate_reward_rate 0.125 \
--stake_to_be_added 100.00 \
--private_key "0x5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133" \
--local
"""

def main():
    # fmt:off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--subnet_id", type=str, required=True, help="Subnet ID stored on blockchain. ")
    parser.add_argument("--hotkey", type=str, required=True, help="Hotkey responsible for subnet features. ")
    parser.add_argument("--peer_id", type=str, required=True, help="Peer ID generated using `keygen`")
    parser.add_argument("--bootnode_peer_id", type=str, required=True, help="Bootnode Peer ID generated using `keygen`")
    parser.add_argument("--bootnode", type=str, required=False, default=None, help="Bootnode URL/MultiAddr")
    parser.add_argument("--client_peer_id", type=str, required=True, help="Bootstrap Peer ID generated using `keygen`")
    parser.add_argument("--delegate_reward_rate", type=float, required=False, default=0.0, help="Reward weight for your delegate stakers")
    parser.add_argument("--stake_to_be_added", type=float, required=True, help="Amount of stake to be added as float")
    parser.add_argument("--unique", type=str, required=False, default=None, help="Non-unique value for subnet node")
    parser.add_argument("--non_unique", type=str, required=False, default=None, help="Non-unique value for subnet node")
    parser.add_argument("--local", action="store_true", help="[Testing] Run in local mode, uses LOCAL_RPC")
    parser.add_argument("--phrase", type=str, required=False, help="[Testing] Coldkey phrase that controls actions which include funds, such as registering, and staking")
    parser.add_argument("--private_key", type=str, required=False, help="[Testing] Hypertensor blockchain private key")

    args = parser.parse_args()
    local = args.local
    phrase = args.phrase
    private_key = args.private_key

    hotkey = args.hotkey
    bootnode = args.bootnode

    if local:
        rpc = os.getenv('LOCAL_RPC')
    else:
        rpc = os.getenv('DEV_RPC')

    if phrase is not None:
        hypertensor = Hypertensor(rpc, phrase)
    elif private_key is not None:
        hypertensor = Hypertensor(rpc, private_key, KeypairFrom.PRIVATE_KEY)
    else:
        hypertensor = Hypertensor(rpc, PHRASE)
    if hotkey is None:
        hotkey = hypertensor.keypair.ss58_address

    subnet_id = args.subnet_id
    peer_id = args.peer_id
    bootnode_peer_id = args.bootnode_peer_id
    delegate_reward_rate = int(args.delegate_reward_rate * 1e18)
    stake_to_be_added = int(args.stake_to_be_added * 1e18)
    unique = args.unique
    non_unique = args.non_unique

    try:
        receipt = hypertensor.register_subnet_node(
            subnet_id,
            hotkey,
            peer_id,
            bootnode_peer_id,
            delegate_reward_rate,
            stake_to_be_added,
            bootnode=bootnode,
            unique=unique,
            non_unique=non_unique
        )
        if receipt.is_success:
            print('✅ Success, triggered events:')
            for event in receipt.triggered_events:
                print(f'* {event.value}')
        else:
            print('⚠️ Extrinsic Failed: ', receipt.error_message)
    except Exception as e:
        logger.error("Error: ", e, exc_info=True)

if __name__ == "__main__":
    main()
