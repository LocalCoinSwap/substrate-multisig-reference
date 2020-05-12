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
