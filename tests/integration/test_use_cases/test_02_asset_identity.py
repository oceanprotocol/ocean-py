"""
    test_02_asset_identity


    As a developer working with Ocean,
    I need a stable identifier (Asset ID) for an arbitrary asset in the Ocean ecosystem

"""

import secrets
from starfish.asset import DataAsset
from starfish.agent import RemoteAgent

# TEST_TEXT = "Django raspberrypi diversity goat python. Cython raspberrypi community dict import object coroutine arduino. Python raspberrypi beautiful pypy gevent pycon raspberrypi rocksdahouse method. Return integration mercurial pypi dunder. Reduce integration itertools test import. Future raspberrypi exception list."

def test_02_asset_register(ocean, resources, remote_agent):
    testData = secrets.token_hex(1024)
    asset1 = DataAsset.create('TestAsset1', testData)
    asset2 = DataAsset.create('TestAsset2', testData)
    asset = remote_agent.register_asset(asset2)
    assert(asset.data == asset2.data)
    assert(asset.asset_id == asset2.asset_id)


def test_02_asset_upload(ocean, resources, remote_agent):
    testData = secrets.token_hex(1024)
    asset_data = DataAsset.create('TestAsset', testData)
    asset = remote_agent.register_asset(asset_data)
    remote_agent.upload_asset(asset)
