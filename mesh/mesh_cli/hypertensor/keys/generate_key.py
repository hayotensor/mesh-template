import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from substrateinterface import Keypair, KeypairType

from mesh.substrate.chain_functions import Hypertensor, KeypairFrom
from mesh.utils.logging import get_logger

load_dotenv(os.path.join(Path.cwd(), '.env'))

PHRASE = os.getenv('PHRASE')

logger = get_logger(__name__)

"""
generate-key --words 12
"""

def main():
    # fmt:off
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--words", type=int, required=False, default=12, help="The amount of words to generate, valid values are 12, 15, 18, 21 and 24. ")

    args = parser.parse_args()
    words = args.words
    assert (
      words == 12 or
      words == 15 or
      words == 18 or
      words == 21 or
      words == 24
    ), "words valid values are 12, 15, 18, 21 and 24."

    try:
      mnemonic = Keypair.generate_mnemonic(words)
      keypair = Keypair.create_from_mnemonic(mnemonic, crypto_type=KeypairType.ECDSA)
      hotkey = keypair.ss58_address

      print("\n")
      print(
        "Store the following mnemonic phrase in a safe place: \n \n"
        f"{mnemonic}"
      )
      print("\n\n")
      print(
        "Your hotkey is: \n \n"
        f"{hotkey}"
      )

      print("\n")
    except Exception as e:
        logger.error("Error: ", e, exc_info=True)

if __name__ == "__main__":
    main()
