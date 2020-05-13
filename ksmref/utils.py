import asyncio
import json

import websockets
from substrateinterface import SubstrateInterface

import settings


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


def rpc_subscription(method, params, request_id, node_url):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id,
    }
    ws_results = {}

    async def ws_request(payload):
        async with websockets.connect(node_url) as websocket:
            await websocket.send(json.dumps(payload))
            event_number = 0
            looping = True
            while looping:
                result = json.loads(await websocket.recv())
                print("Received from node", result)
                ws_results.update({event_number: result})

                # This is nasty but nested ifs are worse
                if (
                    "params" in result
                    and type(result["params"]["result"]) is dict
                    and "finalized" in result["params"]["result"]
                ):
                    looping = False

                event_number += 1

    asyncio.get_event_loop().run_until_complete(ws_request(payload))
    return ws_results
