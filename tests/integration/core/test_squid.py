"""
    Test ocean class

"""

import pathlib
import json
import logging
import time
from web3 import Web3

from starfish import Ocean
from starfish.models.squid_model import SquidModel
from starfish.agent import SquidAgent
from starfish.asset import SquidAsset

from starfish.logging import setup_logging

from squid_py.agreements.service_factory import ServiceDescriptor
from squid_py.utils.utilities import generate_new_id

from squid_py.keeper import Keeper
from squid_py.brizo.brizo_provider import BrizoProvider
from squid_py.brizo.brizo import Brizo

from tests.integration.mocks.brizo_mock import BrizoMock


def _register_asset_for_sale(agent, metadata, account):
    asset = SquidAsset(metadata)
    listing = agent.register_asset(asset, account=account)
    assert listing
    assert listing.asset.did
    return listing

def _log_event(event_name):
    def _process_event(event):
        logging.debug(f'Received event {event_name}: {event}')
    return _process_event

def test_asset(ocean, metadata, config):

    agent = SquidAgent(ocean, config.squid_config)
    assert agent


    # test node has the account #0 unlocked
    publisher_account = ocean.get_account(config.publisher_account)
    publisher_account.unlock()
    publisher_account.request_tokens(20)

    # check to see if the sla template has been registered, this is only run on
    # new networks, especially during a travis test run..
    agent.init_network(publisher_account)

    listing = _register_asset_for_sale(agent, metadata, publisher_account)
    assert listing
    assert publisher_account

    listing_did = listing.asset.did
    # start to test getting the asset from storage
    listing = agent.get_listing(listing_did)
    assert listing
    assert listing.asset.did == listing_did


    purchase_account = ocean.get_account(config.purchaser_account)
    logging.info(f'purchase_account {purchase_account.ocean_balance}')

    purchase_account.unlock()

    purchase_account.request_tokens(10)

    time.sleep(2)
    logging.info(f'purchase_account after token request {purchase_account.ocean_balance}')

    # since Brizo does not work outside in the barge , we need to start
    # brizo as a dumy client to do the brizo work...
    model = agent.squid_model
    BrizoMock.ocean_instance = model.get_squid_ocean()
    BrizoMock.publisher_account = publisher_account._squid_account
    BrizoProvider.set_brizo_class(BrizoMock)

    keeper = Keeper.get_instance()
    # test purchase an asset
    purchase_asset = listing.purchase(purchase_account)
    assert purchase_asset
    agreement_id = purchase_asset.purchase_id

    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        20,
        _log_event(keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for EscrowAccessSecretStoreTemplate.AgreementCreated'

    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        20,
        _log_event(keeper.lock_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for LockRewardCondition.Fulfilled'

    event = keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        _log_event(keeper.escrow_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for EscrowReward.Fulfilled'

    assert Web3.toHex(event.args['_agreementId']) == agreement_id
    # assert len(os.listdir(consumer_ocean_instance.config.downloads_path)) == downloads_path_elements + 1

    # This test does not work with the current barge

    assert purchase_asset.is_purchased
    assert purchase_asset.is_purchase_valid(purchase_account)

    purchase_asset.consume(purchase_account, config.squid_config['download_path'])



def test_search_listing(ocean, metadata, config):


    agent = SquidAgent(ocean, config.squid_config)

    # test node has the account #0 unlocked
    publisher_account = ocean.get_account(config.publisher_account)
    publisher_account.unlock()

    listing = _register_asset_for_sale(agent, metadata, publisher_account)
    assert listing
    assert publisher_account

    # choose a word from the description field
    text = metadata['base']['description']
    words = text.split(' ')
    word = words[0]

    # should return at least 1 or more assets
    logging.info(f'search word is {word}')
    searchResult = agent.search_listings(word)
    assert searchResult

    assert(len(searchResult) > 1)