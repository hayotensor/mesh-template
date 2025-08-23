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
activate-subnet --subnet_id 1

# Local

activate-subnet \
--subnet_id 1 \
--private_key "0x5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133" \
--local
"""

def main():
    # fmt:off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--subnet_id", type=int, required=True, help="Subnet name (unique)")

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

    subnet_id = hypertensor.subnet_id

    try:
        receipt = hypertensor.activate_subnet(subnet_id)
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
