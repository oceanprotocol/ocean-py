from unittest.mock import Mock
import pytest
import secrets
import json

from starfish.ddo.starfish_ddo import StarfishDDO

from squid_py.did import (
    id_to_did,
    did_to_id_bytes,
)
from squid_py.agreements.service_types import ServiceTypes
from plecos import is_valid_dict_local


from tests.unit.libs.unit_test_config import unitTestConfig

TEST_SERVICE_NAME = 'service_data'


class MockSquidModel():
    def __init__(self, ocean, options=None):
        """init a standard ocean object"""
        self._ocean = ocean
        self._options = options
        self._metadata = {}
        self._ddo_list = {}
        self._purchase_assets={}

    def get_account(self, address, password=None):
        if address:
            for index in unitTestConfig.accounts:
                test_account = unitTestConfig.accounts[index]
                if address.lower() == test_account.test_address.lower():
                    account = Mock()
                    account.address = address
                    if password:
                        account.password = password
                    return account
        return None

    def register_agent(self, service_name, endpoint_url, account, did=None):
        # if no did then we need to create a new one
        did = id_to_did(secrets.token_hex(32))

        # create a new DDO
        ddo = StarfishDDO(did)
        # add a signature
        private_key_pem = ddo.add_signature()
        # add the service endpoint with the meta data
        ddo.add_service(service_name, endpoint_url)
        # add the static proof
        ddo.add_proof(0, private_key_pem)
        # if self.register_ddo(did, ddo, account._squid_account):
        return [did, ddo, private_key_pem]

    def validate_metadata(self, metadata):
        """

        Validate the metadata with plesto

        :param dict metadata: metadata to validate
        :return: True if the metadata is valid
        :type: boolean

        """
        return is_valid_dict_local(metadata)

    def register_ddo(self, did, ddo, account):
        self._ddo_list[did] = ddo
        return secrets.token_hex(32)
        
    def resolve_did(self, did):
        return self._ddo_list[did]
        
    def register_asset(self, metadata, account ):
        did = id_to_did(secrets.token_hex(32))
        self._metadata[did] = metadata

        # create a new DDO
        ddo = StarfishDDO(did)
        # add a signature
        private_key_pem = ddo.add_signature()
        # add the service endpoint with the meta data
        assert(self._options)
        assert('aquarius_url' in self._options)
        ddo.add_service(TEST_SERVICE_NAME, self._options['aquarius_url'])
        ddo.add_service(ServiceTypes.METADATA, '', {'metadata': metadata})
        # add the static proof
        ddo.add_proof(0, private_key_pem)
        # if self.register_ddo(did, ddo, account._squid_account):
        self._ddo_list[did] = ddo
        return ddo

    def search_assets(self, text, sort=None, offset=100, page=0):
        return self._ddo_list

    def read_asset(self, did):
        return self._ddo_list[did]

    def purchase_asset(self, ddo, account):
        service = ddo.get_service(TEST_SERVICE_NAME)
        assert(service)
        service_dict = service.as_dictionary()
        assert(service_dict['serviceEndpoint'] == self.options['aquarius_url'])
        service_agreement_id = secrets.token_hex(32)
        self._purchase_assets[service_agreement_id] = ddo.did
        return service_agreement_id

    def purchase_wait_for_completion(self, purchase_id, timeoutSeconds):
        if purchase_id:
            return True
        return 'Cannot wait'

    def consume_asset(self, ddo, service_agreement_id, account, download_path):
        service = ddo.get_service(TEST_SERVICE_NAME)
        assert(service)
        service_dict = service.as_dictionary()
        assert(service_dict['serviceEndpoint'] == self.options['aquarius_url'])
        assert(service_agreement_id in self._purchase_assets)
        did = self._purchase_assets[service_agreement_id]
        if not did in self._metadata:
            return False
        return self._metadata[did]


    def is_access_granted_for_asset(self, did, service_agreement_id, account):
        if did in self._metadata and service_agreement_id in self._purchase_assets:
            return True
        return False

    def get_account_balance(self, account):
        for index in unitTestConfig.accounts:
            test_account = unitTestConfig.accounts[index]
            if account.address.lower() == test_account.test_address.lower():
                balance = Mock()
                balance.eth = test_account.test_ether
                balance.ocn = test_account.test_tokens
                return balance
        return 0

    def create_account(self, password = None):
        address = unitTestConfig.create_account(password)
        return self.get_account(address, password)

    def request_tokens(self, account, value):
        found_account = self.get_account(account.address)
        if found_account.address == account.address:
            return value
        return 0

    @property
    def accounts(self):
        result = []
        for index in unitTestConfig.accounts:
            test_account = unitTestConfig.accounts[index]
            account = Mock()
            account.address = test_account.test_address,
            account.password = test_account.test_password
            result.append(account)

        return result

    @property
    def options(self):
        return self._options
