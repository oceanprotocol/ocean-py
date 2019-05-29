"""
    Inovke Asset
"""

from starfish.asset.asset_base import AssetBase

class OperationAsset(AssetBase):

    """

    Operation asset can be used to perform a invokable service

    :param metadata: Optional dictionary metadata to provide for the asset
        if non used then the class will generate a default metadata based on the data provided
    :type metadata: None or dict
    :param did: Optional did of the asset if it's registered
    :type did: None or str

    """
    def __init__(self, metadata=None, did=None):
        if metadata is None:
            metadata = {
                'name': 'OperationAsset',
                'type': 'operation',
                'author': 'operation asset'
            }
        AssetBase.__init__(self, metadata, did)
        
        if not self.is_asset_type('operation'):
            raise ValueError('The metadata type is not a valid type for this asset')
            

    def is_mode(self, mode_type):
        """
        
        Check to see if this operation supports the mode provided.
        
        :param str mode_type: Mode type to check to see if this operation supports
        :return: Return True if this mode is supported
        :type: boolean
        
        """
        try:
            return mode_type in self._metadata['operation']['modes']
        except:
            pass
        return False
