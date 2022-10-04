from __future__ import absolute_import
import logging
import os
import json

import pandas as pd

from es_gui.tools.dms import DataManagementSystem

class EquityDMS(DataManagementSystem):
    """
    A class for managing data for the energy storage equity functions. Class methods for each type of file to be loaded are included, extending from the get_data() method of the superclass. Each of these methods uses get_data() to retrieve the relevant data and loads the file and adds it to the DMS if the data is not loaded. An optional class method for calling each of the individual data methods can be included to, e.g., form the necessary arguments and return the desired variables.

    :param home_path: A string indicating the relative path to where data is saved.
    """
    def __init__(self, home_path, **kwargs):
        DataManagementSystem.__init__(self, **kwargs)

        self.home_path = home_path
        self.delimiter = ' @ '  # delimiter used to split information in id_key
    
    '''def get_peaker_data(self, path, month):
        """Retrieves peaker plant output and polution data."""
        logging.info('DMS: Loading peaker plant data')

        month = str(month)
        peaker_key = self.delimiter.join([path, month])

        try:
            peaker_data = self.get_data(peaker_key)
        except KeyError:
            peaker_data = read_pv_profile(path, month)
            self.add_data(peaker_data, peaker_key)
        finally:
            return peaker_data'''

    def get_pv_profile_data(self, path):
        """Retrieves PV profile data."""
        logging.info('DMS: Loading PV profile data')

        pv_profile_key = path

        try:
            pv_profile = self.get_data(pv_profile_key)
        except KeyError:
            pv_profile = []
            print('There was an error in loading the pv_profile')
        finally:
            return pv_profile