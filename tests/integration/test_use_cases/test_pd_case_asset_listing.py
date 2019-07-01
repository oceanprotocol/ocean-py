"""
    test_pd_case_search_listings

    As a developer
    I want register an asset in squid, and then find it in the search listings,

"""

import secrets
import logging
import json
from web3 import Web3

from starfish.asset import (
    FileAsset,
    RemoteAsset,
)
from tests.integration.libs.helpers import setup_squid_purchase

def test_pd_case_file_transfer(ocean, config, resources, surfer_agent, squid_agent):

    publisher_account = ocean.get_account(config.publisher_account)

    # for the use case , we need to assign a unique id to the asset
    # so we know that it's from the publisher
    pd_test_case_tag = 'pd_test_case'
    unique_pd_case_id = secrets.token_hex(32)
    dummy_did = secrets.token_hex(32)
    dummy_asset_id = secrets.token_hex(32)
    # create a pretend dummy url based on the dummy surfer DID & dummy asset_id saved in surfer
    dummy_url = 'op:did:{dummy_did}/{dummy_asset_id}'

    # now create a checksum so that we know this actually comes from the correct publisher
    valid_check = Web3.toHex(Web3.sha3(text=f'{unique_pd_case_id}{dummy_url}{publisher_account.address}'))

    listing_data = {
        'name': 'Test file asset',
        'description': 'Test asset for sale - not for public purchase',
        'author': 'pd_test_case asset listing',
        'license': 'Closed',
        'price': 100,
        'extra_data': json.dumps({
        'id': unique_pd_case_id,
        'valid_check': valid_check,
        }),
        'tags': [pd_test_case_tag],
        'categories': [pd_test_case_tag],
    }
    print(listing_data)
    asset_sale = RemoteAsset(url=dummy_url)
    # print('metadata ',squid_agent._convert_listing_asset_to_metadata(asset_sale, resources.listing_data))
    # listing = squid_agent.register_asset(asset_sale, resources.listing_data, account=publisher_account)
    # assert(listing)

    listing_items = squid_agent.search_listings({
#         'query': {'tags': [pd_test_case_tag]}
        'query': {'type': 'dataset'}
    })

    # listing_items = squid_agent.search_listings(pd_test_case_tag)


    for listing in listing_items:
        if 'tags' in listing.data and pd_test_case_tag in listing.data['tags'] :
            print(listing.data.tags)
        else:
            print('listing failed')
