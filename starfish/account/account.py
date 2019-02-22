"""

Account class to provide basic functionality for all Ocean Accounts

"""

from starfish.account.account_object import AccountObject
from starfish.models.squid_model import SquidModel

class Account(AccountObject):
    """

    Account class, adds functionality for an account to be used by the Ocean network.

    At the moment the Account object is created by the :class:`Ocean` class.

    :param ocean: Ocean object
    :type ocean: :class:`.Ocean`
    :param address: address or dict of the account details
    :type address: string or dict
    :param password: password for the account
    :type password: str or None

    If the address parameter is a string then it's the account address.
    If dict then the dict can be the following format: ::

        {
            'address': 'xxxx',
            'password': 'yyyy',
        }

    """

    def __init__(self, ocean, address, password=None):
        """init a standard ocean agent"""
        AccountObject.__init__(self, ocean)
        self._address = None
        self._password = None
        self._unlock_squid_account = None

        if isinstance(address, dict):
            self._address = address.get('address')
            self._password = address.get('password')
        elif isinstance(address, str):
            self._address = address
            self._password = password

    def unlock(self, password=None):
        """

        Unlock the account so that it can be used to spend tokens/gas

        :param password: optional password to use to unlock this account, if none provided then the original password will be used.

        :type password: str or None

        >>> account.unlock('secret')
        True

        """
        if password is None:
            password = self._password

        if password is None:
            raise ValueError('You must provide an account password to unlock')

        # clear out the onlocked account for squid
        self._unlock_squid_account = None
        self._unlock_squid_account = self._squid_account
        if self._unlock_squid_account:
            self._unlock_squid_account.password = password
            return True
        return False

    def lock(self):
        """

        Lock the account, to stop access to this account for ethereum token transfer

        :return: True if this account was unlocked, else False if the account was not locked.
        :type: boolean

        >>> account.lock()
        True
        """
        if self._unlock_squid_account:
            self._unlock_squid_account = None
            return True
        return False

    def request_tokens(self, amount):
        """

        For **Testing Only**

        Request some ocean tokens to be transfere to this account address

        :param number amount: The amount of ocean tokens to transfer ( *Money for nothing* )

        :return: number of tokens transfered
        :type: int

        >>> account.request_tokens(100)
        100
        """
        model = SquidModel(self._ocean)
        if not self._unlock_squid_account:
            raise ValueError('You must unlock the account before requesting tokens')

        return model.request_tokens(self._unlock_squid_account, amount)

    def is_address_equal(self, address):
        """

        Compares two addresses if are equal. Both addresses are converted to checksum
        address and then compared.

        :param str address: address to compare with this object's address
        :return: True if the param address is the same is the one held in this account
        :type: boolean

        >>> account = ocean.get_account('0x00bd138abd70e2f00903268f3db08f2d25677c9e')
        >>> account.is_address_equal('0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e')
        True
        """
        return self.as_checksum_address == self._ocean._web3.toChecksumAddress(address)

    @property
    def is_valid(self):
        """

        Return True if this account is registered in the Ocean network
        :return: True if this account address is valid
        :type: boolean

        >>> account.is_valid
        True
        """
        squid_account = self._squid_account
        return not squid_account is None

    @property
    def _squid_account(self):
        """

        Return the squid account object used for squid services
        :return: The squid account object
        :type: object

        """

        if self._unlock_squid_account:
            return self._unlock_squid_account

        model = SquidModel(self._ocean)
        return model.get_account(self.as_checksum_address)

    @property
    def address(self):
        """

        Return the account address for this account

        :return: address
        :type: str

        >>> account = ocean.get_account('0x00bd138abd70e2f00903268f3db08f2d25677c9e')
        >>> account.address
        0x00bd138abd70e2f00903268f3db08f2d25677c9e
        """
        return self._address

    @property
    def as_checksum_address(self):
        """

        Return the address as a checksum address

        :return: checksum address
        :type: str

        >>> account = ocean.get_account('0x00bd138abd70e2f00903268f3db08f2d25677c9e')
        >>> account.as_checksum_address
        0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e

        """
        if self._address:
            return self._ocean._web3.toChecksumAddress(self._address.lower())
        return None

    @property
    def password(self):
        """

        Return the account password for this account

        :return: password
        :type: str

        >>> account.password
        secret

        """
        return self._password

    def set_password(self, password):
        """

        Set the password for this account

        :param str password: Password to set for this account

        >>> account.set_password('new secret')
        >>> account.password
        new secret
        """
        self.lock()
        self._password = password

    @property
    def ocean_balance(self):
        """

        Get the number of ocean tokens

        :return: number of ocean tokens
        :type: number

        >>> account.ocean_balance
        101

        """
        model = SquidModel(self._ocean)
        squid_account = self._squid_account
        if squid_account:
            balance = model.get_account_balance(squid_account)
            if balance:
                return balance.eth
        return 0

    @property
    def ether_balance(self):
        """

        Get the number of ocean tokens

        :return: number of ocean tokens
        :type: number

        >>> account.ether_balance
        1000000001867769600000000000

        """
        model = SquidModel(self._ocean)
        squid_account = self._squid_account
        if squid_account:
            balance = model.get_account_balance(self._squid_account)
            if balance:
                return balance.ocn
        return 0