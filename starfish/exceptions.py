"""

    Exceptions for starfish-py

"""


class OceanInvalidContractAddress(Exception):
    """  Raised when an invalid address is passed to the contract loader """

class OceanCommandLineError(Exception):
    """ raised on command line errors """

class StarfishPurchaseError(Exception):
    """ Raised when a purchase event has failed to complete """
