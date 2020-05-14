import os
from pathlib import Path

from dotenv import load_dotenv


env_path = Path("js-examples/.env")
load_dotenv(dotenv_path=env_path)

NODE_URL = "wss://kusama-rpc.polkadot.io/"


escrow_address = os.getenv("ESCROW_ADDRESS")
seller_hexseed = os.getenv("SELLER_HEX_SEED")
buyer_hexseed = os.getenv("BUYER_HEX_SEED")
admin_hexseed = os.getenv("ADMIN_HEX_SEED")
trade_value = 10000000000
