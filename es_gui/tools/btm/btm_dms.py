from __future__ import absolute_import
import logging
import os
import json

import pandas as pd

from es_gui.tools.dms import DataManagementSystem
from es_gui.tools.btm.readutdata import *


class BtmDMS(DataManagementSystem):
    """
    A class for managing data for the behind-the-meter energy storage functions. Class methods for each type of file to be loaded are included, extending from the get_data() method of the superclass. Each of these methods uses get_data() to retrieve the relevant data and loads the file and adds it to the DMS if the data is not loaded. An optional class method for calling each of the individual data methods can be included to, e.g., form the necessary arguments and return the desired variables.

    :param home_path: A string indicating the relative path to where data is saved.
    """
    def __init__(self, home_path, **kwargs):
        DataManagementSystem.__init__(self, **kwargs)

        self.home_path = home_path
        self.delimiter = ' @ '  # delimiter used to split information in id_key
    
    def get_load_profile_data(self, path, month):
        """Retrieves commercial or residential load profile data."""
        logging.info('DMS: Loading load profile data')

        month = str(month)
        load_profile_key = self.delimiter.join([path, month])

        try:
            load_profile = self.get_data(load_profile_key)
        except KeyError:
            load_profile = read_load_profile(path, month)
            self.add_data(load_profile, load_profile_key)
        finally:
            return load_profile
    
    def get_pv_profile_data(self, path, month):
        """Retrieves PV profile data."""
        logging.info('DMS: Loading PV profile data')

        month = str(month)
        pv_profile_key = self.delimiter.join([path, month])

        try:
            pv_profile = self.get_data(pv_profile_key)
        except KeyError:
            pv_profile = read_pv_profile(path, month)
            self.add_data(pv_profile, pv_profile_key)
        finally:
            return pv_profile