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
