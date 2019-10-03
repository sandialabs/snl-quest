import os
from pathlib import Path
import shutil
import json
import unittest


from es_gui.downloaders.building_data import get_commercial_geographical_locations, get_commercial_building_types, get_residential_load_types, get_residential_geographical_locations, get_building_data


class TestBuildingLoadProfileDownloaders(unittest.TestCase):
    """Test class for the OpenEI building load profile downloaders."""
    def setUp(self):
        pass
    
    def test_commercial_building_load_profile_downloader(self):
        """Tests process for saving a commercial building load profile."""
        ssl_verify = False

        locations, connection_error_occurred = get_commercial_geographical_locations(ssl_verify=ssl_verify)

        self.assertFalse(connection_error_occurred, msg='A connection error occurred when obtaining commercial building geographical locations.')

        location_root = locations[-1]['link']

        building_types, connection_error_occurred = get_commercial_building_types(location_root, ssl_verify=ssl_verify)

        self.assertFalse(connection_error_occurred, msg='A connection error occurred when obtaining commercial building types.')
 
        csv_link = building_types[-1]['link']

        url_split = csv_link.split('/')
        destination_dir = os.path.join('building_profile_tests', url_split[-2])
        os.makedirs(destination_dir, exist_ok=True)

        destination_file = os.path.join(destination_dir, url_split[-1])

        connection_error_occurred = get_building_data(csv_link, save_directory=destination_dir, ssl_verify=ssl_verify)

        self.assertFalse(connection_error_occurred, msg='A connection error occurred when downloading the load profile.')

        self.assertTrue(Path(destination_file).exists(), msg='The commercial building load profile file failed to be saved where expected.')
    
    def test_residential_building_load_profile_downloader(self):
        """Tests process for saving a residential building load profile."""
        ssl_verify = False

        load_types, connection_error_occurred = get_residential_load_types(ssl_verify=ssl_verify)

        self.assertFalse(connection_error_occurred, msg='A connection error occurred when obtaining residential building load types.')

        load_type_root = load_types[-1]['link']

        locations, connection_error_occurred = get_residential_geographical_locations(load_type_root, ssl_verify=ssl_verify)

        self.assertFalse(connection_error_occurred, msg='A connection error occurred when obtaining residential building geographical locations.')
 
        csv_link = locations[-1]['link']

        url_split = csv_link.split('/')
        destination_dir = os.path.join('building_profile_tests', url_split[-2])
        os.makedirs(destination_dir, exist_ok=True)

        destination_file = os.path.join(destination_dir, url_split[-1])

        connection_error_occurred = get_building_data(csv_link, save_directory=destination_dir, ssl_verify=ssl_verify)

        self.assertFalse(connection_error_occurred, msg='A connection error occurred when downloading the load profile.')

        self.assertTrue(Path(destination_file).exists(), msg='The residential building load profile file failed to be saved where expected.')
    
    def tearDown(self):
        shutil.rmtree('building_profile_tests')


if __name__ == '__main__':
    unittest.main()
