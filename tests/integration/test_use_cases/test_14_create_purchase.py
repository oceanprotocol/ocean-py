"""
    test_14_create_purchase

    As a developer working with an Ocean marketplace,
    I want to record a purchase.

"""

import secrets
import logging
import json

from starfish.asset import MemoryAsset


def test_14_create_purchase(ocean, config, surfer_agent, metadata):
    test_data = secrets.token_hex(1024)
    asset = MemoryAsset(metadata=metadata, data=test_data)
    listing = surfer_agent.register_asset(asset)
    listing.set_published(True)
    logging.debug("create_purchase for listingid: " + listing.listing_id)
    purchaser_account = ocean.get_account(config.purchaser_account)
    purchaser_account.unlock()
    purchase = surfer_agent.purchase_asset(listing, purchaser_account)
    assert(purchase['listingid'] == listing.listing_id)
    assert(purchase['status'] == 'wishlist')
    logging.debug("purchase: " + json.dumps(purchase))
