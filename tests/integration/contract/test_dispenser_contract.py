import pytest

TOKEN_AMOUNT_TO_TRANSFER = 2


def test_dispenser(network, accounts):
    dispenser_contract = network.get_contract('Dispenser')
    dex_token_contract = network.get_contract('DexToken')

    test_account = accounts[0]
    balance = dex_token_contract.get_balance(test_account)
    tx_hash = dispenser_contract.request_tokens(test_account, TOKEN_AMOUNT_TO_TRANSFER)
    receipt = dispenser_contract.wait_for_receipt(tx_hash)

    new_balance = dex_token_contract.get_balance(test_account)
    assert(balance + TOKEN_AMOUNT_TO_TRANSFER == new_balance)
