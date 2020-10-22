"""
    starfish-ddo-registry contract

"""

from starfish.network.convex.contract.contract_base import ContractBase
from starfish.network.convex.convex_account import ConvexAccount
from starfish.network.convex.convex_network import ConvexNetwork
from starfish.types import AccountAddress


class ProvenanceContract(ContractBase):

    def __init__(self, convex: ConvexNetwork):
        ContractBase.__init__(self, convex, 'starfish-provenance')

    def register(self, asset_id: str, account: ConvexAccount):
        command = f'(call {self.address} (register {asset_id}))'
        result = self._convex.send(command, account)
        if result and 'value' in result:
            return result['value']
        return result

    def event_list(self, asset_id: str, account_address: AccountAddress):
        command = f'(call {self.address} (event-list {asset_id}))'
        if isinstance(account_address, str):
            address = account_address
        else:
            address = account_address.address
        result = self._convex.query(command, address)
        if result and 'value' in result:
            return result['value']
        return result

    def event_owner(self, account_address: AccountAddress):
        if isinstance(account_address, str):
            address = account_address
        else:
            address = account_address.address
        command = f'(call {self.address} (event-owner {address}))'
        result = self._convex.query(command, address)
        if result and 'value' in result:
            return result['value']
        return result