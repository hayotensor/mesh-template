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
activate-node \
--subnet_id 1 \
--subnet_node_id 23 \

# Local

activate-node \
--subnet_id 1 \
--subnet_node_id 23 \
--private_key "0x5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133" \
--local
"""

def main():
    # fmt:off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--subnet_id", type=str, required=True, help="Subnet ID stored on blockchain. ")
    parser.add_argument("--subnet_node_id", type=str, required=False, help="Hotkey responsible for subnet features. ")
    parser.add_argument("--local", action="store_true", help="[Testing] Run in local mode, uses LOCAL_RPC")
    parser.add_argument("--phrase", type=str, required=False, help="[Testing] Coldkey phrase that controls actions which include funds, such as registering, and staking")
    parser.add_argument("--private_key", type=str, required=False, help="[Testing] Hypertensor blockchain private key")

    args = parser.parse_args()
    local = args.local
    phrase = args.phrase
    private_key = args.private_key

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

    subnet_id = args.subnet_id
    subnet_node_id = args.subnet_node_id

    try:
        receipt = hypertensor.activate_subnet_node(
            subnet_id,
            subnet_node_id,
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
