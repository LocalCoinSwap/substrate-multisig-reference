import websockets
from scalecodec.base import RuntimeConfiguration
from scalecodec.type_registry import load_type_registry_preset
from substrateinterface import SubstrateInterface

import settings
import asyncio
import json

def get_balance_for_address(address):
    """
    Params:
    -------
    address - str

    Returns:
    --------
    dict

    Example:
    {
        "free": 22000000000,
        "reserved": 0,
        "miscFrozen": 0,
        "feeFrozen": 0,
    }
    """

    substrate = SubstrateInterface(
        url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
    )
    block = substrate.get_chain_finalised_head()

    account_data = substrate.get_runtime_state(
        module="System", storage_function="Account", params=[address], block_hash=block,
    )

    return account_data.get("result", {}).get("data")


def broadcast(signed_exctrinsic):
    """
    Params:
    -------
    signed exctrinsic - hex str

    Returns:
    --------
    Tuple:
        data

        success - Bool

    Example:
    ('0x5d66ccff882e61ce8845cc462d553c87b9007c91dfd817b3a63f578f510368ed', True)

    """
    substrate = SubstrateInterface(
        url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
    )
    # Need to refactor py-substrate to have rpc_request use something other then run_until_complete
    # (Maybe "run_forever" with a stop condition on failure or complete) to subscribe to all events (not just one)
    # result = substrate.rpc_request(method="author_submitAndWatchExtrinsic", params=[extrinsic])
    result = substrate.rpc_request(
        method="author_submitExtrinsic", params=[signed_exctrinsic]
    )
    if result["result"]:
        return result["result"], True
    elif result["error"]:
        return result["error"], False


class rpcInterface:
    def __init__(
        self,
        url,
        address_type=None,
        type_registry=None,
        type_registry_preset=None,
        cache_region=None,
    ):
        """
            A specialized class in interfacing with a Substrate node.

            Parameters
            ----------
            url: the URL to the substrate node, either in format https://127.0.0.1:9933 or wss://127.0.0.1:9944
            address_type: The address type which account IDs will be SS58-encoded to Substrate addresses. Defaults to 42, for Kusama the address type is 2
            type_registry: A dict containing the custom type registry in format: {'types': {'customType': 'u32'},..}
            type_registry_preset: The name of the predefined type registry shipped with the SCALE-codec, e.g. kusama
            cache_region: a Dogpile cache region as a central store for the metadata cache
            """
        self.cache_region = cache_region
        if type_registry or type_registry_preset:

            RuntimeConfiguration().update_type_registry(
                load_type_registry_preset("default")
            )

            if type_registry:
                # Load type registries in runtime configuration
                RuntimeConfiguration().update_type_registry(type_registry)
            if type_registry_preset:
                # Load type registries in runtime configuration
                RuntimeConfiguration().update_type_registry(
                    load_type_registry_preset(type_registry_preset)
                )
        self.request_id = 1
        self.url = url
        self._ws_result = None
        self.address_type = address_type
        self.mock_extrinsics = None
        self._version = None
        self.default_headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
        }
        self.metadata_decoder = None
        self.runtime_version = None
        self.block_hash = None
        self.metadata_cache = {}
        self.type_registry_cache = {}
        self.debug = False

    async def ws_request(self, payload):
        extrinsicUpdates = []
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(payload))
            _ws_result = None
            # while 'finalized' or 'error' not in str(_ws_result): #this never stops for some reason but the below does
            # Todo, end loop safely
            while "finalized" not in str(_ws_result):
                _ws_result = json.loads(await websocket.recv())
                if "method" in _ws_result.keys():
                    if _ws_result["method"] == "author_extrinsicUpdate":
                        ws_result = _ws_result["params"]["result"]
                        extrinsicUpdates.append(ws_result)
        return extrinsicUpdates

    def rpc_request(self, method, params):
        """
            Method that handles the actual RPC request to the Substrate node. The other implemented functions eventually
            use this method to perform the request.

            Parameters
            ----------
            method: method of the JSONRPC request
            params: a list containing the parameters of the JSONRPC request

            Returns
            -------
            a dict with the parsed result of the request.
            """
        # Assumes wss conection
        """
            substrate = SubstrateInterface(
                url=NODE_URL, address_type=2, type_registry_preset="kusama",
            )
            """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id,
        }
        extrinsic_update_data = asyncio.get_event_loop().run_until_complete(
            self.ws_request(payload)
        )
        json_body = self._ws_result

        return json_body, extrinsic_update_data
