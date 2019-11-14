import os
from pathlib import Path
import shutil
import json
import datetime
import unittest

from es_gui.downloaders.market_data import (
    download_caiso_data,
    download_ercot_data,
    download_isone_data,
    download_miso_data,
    download_nyiso_data,
    download_pjm_data,
    download_spp_data,
    get_pjm_nodes
)


class TestMarketDataDownloaders(unittest.TestCase):
    """Test class for the market data downloaders."""
    def setUp(self):
        self.ssl_verify = False
        self.proxy_settings = None
        self.save_directory = 'market_data'
        self.datetime_start = datetime.datetime(2019, 10, 1)

        def _update_function(update):
            if isinstance(update, int):
                if update == -1:
                    print('closing thread')
                else:
                    print('incrementing progress_bar')
            elif isinstance(update, str):
                print('>>', update)
        
        self.update_function = _update_function
    
    def test_ercot_downloader(self):
        """Tests a proper query for ERCOT data downloader."""
        cnx_error = download_ercot_data(
        save_directory=self.save_directory, 
        year='all', 
        typedat='both', 
        ssl_verify=self.ssl_verify, 
        proxy_settings=self.proxy_settings, 
        n_attempts=7,
        update_function=self.update_function
        )

        self.assertFalse(cnx_error)
    
    def test_isone_downloader(self):
        """Tests a proper query for ISO-NE data downloader."""
        node_list = ['HUBS',]
        
        cnx_error = download_isone_data(
            username=username, 
            password=password, 
            save_directory=self.save_directory, 
            datetime_start=self.datetime_start, 
            datetime_end=None, 
            nodes=node_list, 
            typedat='all', 
            ssl_verify=self.ssl_verify, 
            proxy_settings=self.proxy_settings, 
            n_attempts=7, 
            update_function=self.update_function
            )
        
        self.assertFalse(cnx_error)
    
    def tearDown(self):
        shutil.rmtree('market_data')


if __name__ == '__main__':
    unittest.main()
