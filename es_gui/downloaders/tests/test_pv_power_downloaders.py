import os
from pathlib import Path
import shutil
import json
import unittest

import requests

from es_gui.downloaders.pv_power import get_pv_profile_data


class TestPVPowerProfileDownloaders(unittest.TestCase):
    """Test class for the PV power profile downloaders."""
    def setUp(self):
        pass
    
    def test_query_without_api_key(self):
        """Tests that a ConnectionError is raised with HTTP response status code 403 for an API query without an API key."""
        pv_params = {}

        pv_params['dataset'] = 'tmy3'
        pv_params['radius'] = '0'
        pv_params['timeframe'] = 'hourly'
        pv_params['lat'] = 35.08
        pv_params['lon'] = -106.65
        pv_params['system_capacity'] = 1000
        pv_params['losses'] = 14
        pv_params['azimuth'] = 180
        pv_params['tilt'] = 35.08
        pv_params['array_type'] =  0
        pv_params['module_type'] = 0

        os.makedirs('test_pv', exist_ok=True)

        with self.assertRaises(requests.exceptions.ConnectionError, msg='A connection error occurred.') as cm:
            get_pv_profile_data(pv_params, save_path=os.path.join('test_pv', 'test_pv.json'), ssl_verify=False)
        
        status_code = cm.exception.args[0].response.status_code

        self.assertEqual(status_code, 403, msg='A query that is missing an API key should result in HTTP response status code 403.')
    
    def test_query_missing_required_parameter(self):
        """Tests that a ConnectionError is raised with HTTP response status code 422 for an API query with a missing required parameter."""
        pv_params = {}

        pv_params['dataset'] = 'tmy3'
        pv_params['radius'] = '0'
        pv_params['timeframe'] = 'hourly'
        pv_params['api_key'] = 'AHKRnsqzqRbhOZ9XU2C63gwFEsPASXtQJl3b1Pd0'
        pv_params['lat'] = 35.08
        pv_params['lon'] = -106.65
        pv_params['losses'] = 14
        pv_params['azimuth'] = 180
        pv_params['tilt'] = 35.08
        pv_params['array_type'] =  0
        pv_params['module_type'] = 0

        os.makedirs('test_pv', exist_ok=True)

        with self.assertRaises(requests.exceptions.ConnectionError, msg='A connection error occurred.')  as cm:
            get_pv_profile_data(pv_params, save_path=os.path.join('test_pv', 'test_pv.json'), ssl_verify=False)
        
        status_code = cm.exception.args[0].response.status_code

        self.assertEqual(status_code, 422, msg='A query that is missing a required parameter should result in HTTP response status code 422.')
    
    def test_proper_query(self):
        """Tests a proper query."""
        pv_params = {}

        pv_params['dataset'] = 'tmy3'
        pv_params['radius'] = '0'
        pv_params['timeframe'] = 'hourly'
        pv_params['api_key'] = 'AHKRnsqzqRbhOZ9XU2C63gwFEsPASXtQJl3b1Pd0'
        pv_params['lat'] = 35.08
        pv_params['lon'] = -106.65
        pv_params['system_capacity'] = 1000
        pv_params['losses'] = 14
        pv_params['azimuth'] = 180
        pv_params['tilt'] = 35.08
        pv_params['array_type'] =  0
        pv_params['module_type'] = 0

        os.makedirs('test_pv', exist_ok=True)
        get_pv_profile_data(pv_params, save_path=os.path.join('test_pv', 'test_pv.json'), ssl_verify=False)

        self.assertTrue(Path(os.path.join('test_pv', 'test_pv.json')).exists(), msg='The PV power profile file failed to be saved where expected.')
    
    def tearDown(self):
        shutil.rmtree('test_pv')


if __name__ == '__main__':
    unittest.main()
