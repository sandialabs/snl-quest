import os
from pathlib import Path
import shutil
import json
import unittest

import requests

from es_gui.downloaders.utility_rates import get_utility_reference_table, get_utility_rate_structures


class TestUtilityRateDownloaders(unittest.TestCase):
    """Test class for the utility rate downloaders."""
    def setUp(self):
        pass

    def test_utility_reference_table_download(self):
        """Tests that the utility reference tables can be downloaded successfully.
        """
        ssl_verify = False
        proxy_settings = None

        utility_reference_table, connection_error_occurred = get_utility_reference_table(
            ssl_verify=ssl_verify,
            proxy_settings=proxy_settings
        )

        self.assertFalse(connection_error_occurred)
    
    def test_query_without_api_key(self):
        """Tests that a ConnectionError is raised with HTTP response status code 403 for an API query without an API key."""
        ssl_verify = False
        proxy_settings = None

        utility_reference_table, connection_error_occurred = get_utility_reference_table(
            ssl_verify=ssl_verify,
            proxy_settings=proxy_settings
        )

        self.assertFalse(connection_error_occurred)

        eia_id = str(utility_reference_table.iloc[0]['eiaid'])

        with self.assertRaises(requests.exceptions.ConnectionError, msg='A connection error occurred.') as cm:
            records, connection_error_occurred = get_utility_rate_structures(
                eia_id,
                '',
                ssl_verify=ssl_verify,
                proxy_settings=proxy_settings
            )
    
    def test_proper_query(self):
        """Tests a proper query."""
        ssl_verify = False
        proxy_settings = None

        utility_reference_table, connection_error_occurred = get_utility_reference_table(
            ssl_verify=ssl_verify,
            proxy_settings=proxy_settings
        )

        self.assertFalse(connection_error_occurred)

        eia_id = str(utility_reference_table.iloc[0]['eiaid'])

        records, connection_error_occurred = get_utility_rate_structures(
            eia_id,
            'AHKRnsqzqRbhOZ9XU2C63gwFEsPASXtQJl3b1Pd0',
            ssl_verify=ssl_verify,
            proxy_settings=proxy_settings
        )

        self.assertFalse(connection_error_occurred)


if __name__ == '__main__':
    unittest.main()
