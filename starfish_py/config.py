"""

Config Class to handle config data and config files

"""

import configparser
import logging
import os
import os.path
import re
import tempfile

from starfish_py import logger

CONFIG_SECTION_NAME = 'starfish-py'

CONFIG_DEFAULT = """
[starfish-py]
keeper_url = http://localhost:8545
contract_path = artifacts

secret_store_url = http://localhost:8010
parity_url = http://localhost:9545
parity_address = 0x00bd138abd70e2f00903268f3db08f2d25677c9e
parity_password = node0

aquarius_url = http://localhost:5000
brizo_url = http://localhost:8030

storage_path = squid_py.db
download_path = consume_downloads

agent_store_did =
agent_store_auth =

gas_limit = 300000

"""


class Config(configparser.ConfigParser):
    """
    Create a new config instance, using a config file, dictionary of values or argument list (kwargs)

    :param filename: Filename of the config file to load.
    :param contracts_path: path to the contract files ( artifacts ).
    :param keeper_url: url to the keeper node ( http://localhost:8545 ).
    :param secret_store_url: url to the secret store node ( http://localhost:12001 ).
    :param parity_url: url to the parity node ( http://localhost:8545 ).
    :param aquarius_url: url of the Aquarius metadata service ( http://localhost:5000 ).
    :param brizo_url: url of the Brizo consumer service (http://localhost:8030 ).

    :param storage_path: Path to save temporary storage of assets purchased and consumed ( squid_py.db ).
    :param download_path: Path to save the consumed assets too. ( consume_downloads ).
    :param agent_store_did: DID of the agent metadata service.
    :param agent_store_auth: Authorziation text to access the metadat service.
    :param gas_limit: The amount of gas you are willing to spend on each block chain transaction ( 30000 ).



    For example::

        # only set the contarcts path and keeper url values
        ocean = Ocean(contracts_path='artifacts', keeper_url='http://localhost:8080')

    The default config values as defined as an `ini` file are defined as follows:
    
    .. literalinclude:: ../../../starfish_py/config.py
        :start-after: CONFIG_DEFAULT
        :end-before: "
    """

    def __init__(self, filename=None, **kwargs):
        """
        The config class

        """
        configparser.ConfigParser.__init__(self)

        self.read_string(CONFIG_DEFAULT)
        self._section_name = CONFIG_SECTION_NAME
        values = {}

        if filename:
            if isinstance(filename, str):
                if not os.path.exists(filename):
                    logging.error(f'Config file not found: "{filename}"')
                logging.debug(f'loading config file {filename}')
                with open(filename) as file_handle:
                    text = file_handle.read()
                    self.read_string(text)
                    values[self._section_name] = kwargs
            elif isinstance(filename, dict):
                logger.debug('loading config from a dict')
                values[self._section_name] = filename
            elif isinstance(filename, Config):
                logger.debug('loading config from another config object')
                for section_name in filename.items():
                    values[section_name[0]] = {}
                    for name, value in filename.items(section_name[0]):
                        values[section_name[0]][name] = value
            else:
                raise TypeError('Invalid type of data passed, can only be a filename or a dict of values')
        else:
            if kwargs:
                logger.debug('loading config from a kwargs')
                values[self._section_name] = kwargs

        if values:
            logger.debug(f'loading values {kwargs}')
            self.read_dict(values)

        self._read_environ()

    def _read_environ(self):
        """

        Read the environment variables and replace them with the config values

        """
        defaults = configparser.ConfigParser()
        defaults.read_string(CONFIG_DEFAULT)
        for name, value in defaults.items(CONFIG_SECTION_NAME):
            value = os.environ.get(re.sub(r'[^\w]+', '_', name).upper())
            if value is not None:
                logger.debug(f'setting environ {name} = {value}')
                self.set(self._section_name, name, value)

    @property
    def as_squid_file(self):
        """

        For compatibility generate a temporary config file, and pass back the filename.
        The config values must conform to the current version of squid-py

        :return: A temporary filename that can be used by squid.

        """
        squid = configparser.ConfigParser()
        values = self.as_squid_dict
        squid.read_dict(values)
        logger.debug(f'squid config values {values}')
        temp_handle = tempfile.mkstemp('_squid.conf', text=True)
        os.close(temp_handle[0])
        filename = temp_handle[1]
        with open(filename, 'w') as file_handle:
            squid.write(file_handle)
        return filename

    @property
    def as_squid_dict(self):
        """

        Return a set of config values, so that squid can read.

        :return: a dict that is compatiable with the current supported version of squid-py.
        """
        return {
            'keeper-contracts': {
                'keeper.url': self.keeper_url,
                'keeper.path': self.contract_path,
                'secret_store.url': self.secret_store_url,
                'parity.url': self.parity_url,
                'parity.address': self.parity_address,
                'parity.password':  self.parity_password,
            },
            'resources': {
                'aquarius.url': self.aquarius_url,
                'brizo.url': self.brizo_url,
                'storage.path': self.storage_path,
                'downloads.path': self.download_path,
            }
        }

    @property
    def contract_path(self):
        """
        :return: the contract path value.
        """
        return self.get(self._section_name, 'contract_path')

    @property
    def storage_path(self):
        """
        :return: the storage path.
        """
        return self.get(self._section_name, 'storage_path')

    @property
    def download_path(self):
        """
        :return: the download path.
        """
        return self.get(self._section_name, 'download_path')

    @property
    def keeper_url(self):
        """
        :return: the ocean url or ethereum node url.
        """
        return self.get(self._section_name, 'keeper_url')

    @property
    def gas_limit(self):
        """
        :return: the default gas limit
        """
        return int(self.get(self._section_name, 'gas_limit'))

    @property
    def aquarius_url(self):
        """
        :return: the aquarius server URL.
        """
        return self.get(self._section_name, 'aquarius_url')

    @property
    def brizo_url(self):
        """
        :return: the URL of the brizo server.
        """
        return self.get(self._section_name, 'brizo_url')

    @property
    def secret_store_url(self):
        """
        :return: the secret store URL.
        """
        return self.get(self._section_name, 'secret_store_url')

    @property
    def parity_url(self):
        """
        :return: the parity URL.
        """
        return self.get(self._section_name, 'parity_url')

    @property
    def parity_address(self):
        """
        :return: the parity address.
        """
        return self.get(self._section_name, 'parity_address')

    @property
    def parity_password(self):
        """
        :return: the parity password.
        """
        return self.get(self._section_name, 'parity_password')

    @property
    def agent_store_did(self):
        """
        :return: the storage agent's DID.
        """
        return self.get(self._section_name, 'agent_store_did')

    @property
    def agent_store_auth(self):
        """
        :return: the storage agent's authorization.
        """
        return self.get(self._section_name, 'agent_store_auth')
