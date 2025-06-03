from __future__ import absolute_import, print_function

import os
import collections
import json
import calendar
import threading
import logging
import copy
import csv

import pandas as pd
from kivy.app import App
from kivy.animation import Animation
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

from valuation.es_gui.resources.widgets.common import LoadingModalView,WarningPopup
from valuation.paths import get_path
dirname = get_path()

DATA_HOME = 'data'

STATE_ABBR_TO_NAME = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'DC': 'District of Columbia',
}


class DataManager(EventDispatcher):
    data_bank = {}
    n_threads_scanning = NumericProperty(0)

    def __init__(self, data_bank_root='data', **kwargs):
        super(DataManager, self).__init__(**kwargs)
        self.data_bank_root = data_bank_root
    
    def on_n_threads_scanning(self, instance, value):
        if value == 0:
            logging.info('DataManager: Data bank scan complete.')
            # Animation.stop_all(self.loading_screen.logo, 'opacity')
            self.loading_screen.dismiss()

    @property
    def data_bank_root(self):
        """The path to the root of the data download directory."""
        return self._data_bank_root
    
    @data_bank_root.setter
    def data_bank_root(self, value):
        self._data_bank_root = value
    
    def scan_btm_data_bank(self):
        """Scans the behind-the-meter data bank to determine what data has been downloaded."""
        # Check if data bank exists.
        try:
            os.listdir(self.data_bank_root)
        except FileNotFoundError:
            return

        # Open loading screen.
        self.loading_screen = LoadingModalView()
        self.loading_screen.loading_text.text = 'Scanning data files...'
        self.loading_screen.open()

        self.n_threads_scanning = 1

        def _scan_btm_data_bank():
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            self._scan_rate_structure_data_bank()
            self._scan_btm_load_profile_data_bank()
            self._scan_btm_pv_profile_data_bank()

            self.n_threads_scanning -= 1
        
        thread = threading.Thread(target=_scan_btm_data_bank)
        thread.start()       
    
    def _scan_rate_structure_data_bank(self):
        """Scans the saved rate structure data bank."""
        rate_structure_root = os.path.join(self.data_bank_root, 'rate_structures')
        rate_structure_data_bank = {}

        try:
            os.listdir(rate_structure_root)
        except FileNotFoundError:
            return

        for rate_structure_file in os.scandir(rate_structure_root):
            if not rate_structure_file.name.startswith('.'):
                with open(rate_structure_file.path) as f:
                    rate_structure = json.load(f)
                
                rate_structure_data_bank[rate_structure['name']] = rate_structure
        
        self.data_bank['rate structures'] = rate_structure_data_bank
    
    def _scan_btm_load_profile_data_bank(self):
        """Scans the saved load profile data bank."""
        load_profile_root = os.path.join(self.data_bank_root, 'load')
        load_profile_data_bank = {}

        try:
            os.listdir(load_profile_root)
        except FileNotFoundError:
            return

        # TODO: Create more readable names?

        # Commercial load profiles.
        if 'commercial' in os.listdir(load_profile_root):
            commercial_root = os.path.join(load_profile_root, 'commercial')

            for location_dir in os.scandir(commercial_root):
                if not location_dir.name.startswith('.'):
                    location_root = location_dir.path

                    for load_profile in os.scandir(location_root):
                        if not load_profile.name.startswith('.'):
                            profile_key = '/'.join(['commercial', load_profile.name])
                            profile_path = load_profile.path

                            load_profile_data_bank[profile_key] = profile_path
        
        # Residential load profiles.
        if 'residential' in os.listdir(load_profile_root):
            residential_root = os.path.join(load_profile_root, 'residential')

            for load_level_dir in os.scandir(residential_root):
                if not load_level_dir.name.startswith('.'):
                    level_root = load_level_dir.path

                    for load_profile in os.scandir(level_root):
                        if not load_profile.name.startswith('.'):
                            profile_key = '/'.join(['residential', load_profile.name])
                            profile_path = load_profile.path

                            load_profile_data_bank[profile_key] = profile_path
        
        # Imported.
        if 'imported' in os.listdir(load_profile_root):
            imported_root = os.path.join(load_profile_root, 'imported')

            for load_profile in os.scandir(imported_root):
                if not load_profile.name.startswith('.'):
                    profile_key = '/'.join(['imported', load_profile.name])
                    profile_path = load_profile.path

                    load_profile_data_bank[profile_key] = profile_path
            
        self.data_bank['load profiles'] = load_profile_data_bank
    
    def _scan_btm_pv_profile_data_bank(self):
        """Scans the saved PV profile data bank."""
        pv_profile_root = os.path.join(self.data_bank_root, 'pv')
        pv_profile_data_bank = {}

        try:
            os.listdir(pv_profile_root)
        except FileNotFoundError:
            return

        for pv_profile in os.scandir(pv_profile_root):
            if not pv_profile.name.startswith('.'):
                profile_key = pv_profile.name.split('.')[0]

                # with open(pv_profile.path) as f:
                #     profile_val = json.load(f)
                profile_val = pv_profile.path

                pv_profile_data_bank[profile_key] = profile_val
            
        self.data_bank['PV profiles'] = pv_profile_data_bank
    
    def get_rate_structures(self):
        """Returns a dictionary of all of the rate structures saved to the data bank."""
        # Sort by name alphabetically before returning.
        try:
            return_dict = collections.OrderedDict(sorted(self.data_bank['rate structures'].items(), key=lambda t: t[0]))
        except KeyError:
            raise KeyError('It looks like no rate structures have been saved.')
        
        return return_dict
    
    def get_load_profiles(self):
        """Returns a dictionary of all of the load profiles saved to the data bank."""
        # Sort by name alphabetically before returning.
        try:
            return_dict = collections.OrderedDict(sorted(self.data_bank['load profiles'].items(), key=lambda t: t[0]))
        except KeyError:
            raise KeyError('It looks like no load profiles have been saved.')
        
        return return_dict
    
    def get_pv_profiles(self):
        """Returns a dictionary of all of the PV profiles saved to the data bank."""
        # Sort by name alphabetically before returning.
        try:
            return_dict = collections.OrderedDict(sorted(self.data_bank['PV profiles'].items(), key=lambda t: t[0]))
        except KeyError:
            raise(KeyError('It looks like no PV profiles have been saved.'))

        return return_dict
    
    def get_markets(self):
        """Returns a keys view of all of the markets for valuation available."""
        # self.scan_valuation_data_bank()

        try:
            valuation_data_bank = self.data_bank['valuation']
        except KeyError:
            return []
        else:
            return self.data_bank['valuation'].keys()

    def scan_valuation_data_bank(self):
        """Scans the valuation data bank to determine what data has been downloaded."""
        # Check if data bank exists.
        try:
            os.listdir(self.data_bank_root)
        except FileNotFoundError:
            return

        # Open loading screen.
        self.loading_screen = LoadingModalView()
        self.loading_screen.loading_text.text = 'Scanning data files...'
        self.loading_screen.open()

        self.data_bank['valuation'] = {}
        market_names = []

        # Determine the market areas that have downloaded data.
        for dir_entry in os.scandir(self.data_bank_root):
            if not dir_entry.name.startswith('.'):
                market_names.append(dir_entry.name)

        self.n_threads_scanning = 1

        def _scan_valuation_data_bank():
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            if 'ERCOT' in market_names:
                self._scan_ercot_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return
                
            if 'PJM' in market_names:
                self._scan_pjm_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return
                
            if 'MISO' in market_names:
                self._scan_miso_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            if 'NYISO' in market_names:
                self._scan_nyiso_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            if 'ISONE' in market_names:
                self._scan_isone_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            if 'SPP' in market_names:
                self._scan_spp_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            if 'CAISO' in market_names:
                self._scan_caiso_data_bank()
            
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            self.n_threads_scanning -= 1
        
        thread = threading.Thread(target=_scan_valuation_data_bank)
        thread.start()            
    
    def _scan_pjm_data_bank(self):
        """Scans the PJM data bank."""
        pjm_root = os.path.join(self.data_bank_root, 'PJM')
        pjm_data_bank = {}

        # Scan LMP files.
        if 'LMP' in os.listdir(pjm_root):
            pjm_data_bank['LMP'] = {}
            lmp_dir = os.path.join(pjm_root, 'LMP')

            # Identify pricing node ID dirs.
            for node_dir_entry in os.scandir(lmp_dir):
                if not node_dir_entry.name.startswith('.'):
                    node_id = node_dir_entry.name
                    pjm_data_bank['LMP'][node_id] = {}
                    node_id_dir = node_dir_entry.path

                    # Identify year dirs.
                    for year_dir_entry in os.scandir(node_id_dir):
                        if not year_dir_entry.name.startswith('.'):
                            year = year_dir_entry.name
                            pjm_data_bank['LMP'][node_id][year] = []
                            year_dir = year_dir_entry.path

                            # Identify month files.
                            for lmp_dir_entry in os.scandir(year_dir):
                                if not lmp_dir_entry.name.startswith('.'):
                                    lmp_file = lmp_dir_entry.name
                                    yyyymm, _ = lmp_file.split('_', maxsplit=1)
                                    month = yyyymm[-2:]
                                    pjm_data_bank['LMP'][node_id][year].append(month)
        
        # Scan Reg files.
        if 'REG' in os.listdir(pjm_root):
            pjm_data_bank['REG'] = {}
            reg_dir = os.path.join(pjm_root, 'REG')

            # Identify year dirs.
            for year_dir_entry in os.scandir(reg_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    pjm_data_bank['REG'][year] = []
                    year_dir = year_dir_entry.path

                    # Identify month files.
                    for reg_dir_entry in os.scandir(year_dir):
                        if not reg_dir_entry.name.startswith('.'):
                            reg_file = reg_dir_entry.name
                            yyyymm, _ = reg_file.split('_', maxsplit=1)
                            month = yyyymm[-2:]
                            pjm_data_bank['REG'][year].append(month)
        
        # Scan Mileage files.
        if 'MILEAGE' in os.listdir(pjm_root):
            pjm_data_bank['MILEAGE'] = {}
            mileage_dir = os.path.join(pjm_root, 'MILEAGE')

            # Identify year dirs.
            for year_dir_entry in os.scandir(mileage_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    pjm_data_bank['MILEAGE'][year] = []
                    year_dir = year_dir_entry.path

                    # Identify month files.
                    for mileage_dir_entry in os.scandir(year_dir):
                        if not mileage_dir_entry.name.startswith('.'):
                            mileage_file = mileage_dir_entry.name
                            yyyymm, _ = mileage_file.split('_', maxsplit=1)
                            month = yyyymm[-2:]
                            pjm_data_bank['MILEAGE'][year].append(month)
        
        self.data_bank['valuation']['PJM'] = pjm_data_bank
    
    def _scan_miso_data_bank(self):
        """Scans the MISO data bank."""
        miso_root = os.path.join(self.data_bank_root, 'MISO')
        miso_data_bank = {}
        miso_nodes = self.get_nodes('MISO')

        # LMP scan.
        if 'LMP' in os.listdir(miso_root):
            miso_data_bank['LMP'] = {}
            lmp_dir = os.path.join(miso_root, 'LMP')

            # Scan LMP directory structure once.
            miso_lmp_dir_struct = {}

            for year_dir_entry in os.scandir(lmp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    year_dir = year_dir_entry.path
                    miso_lmp_dir_struct[year] = []

                    for month_dir_entry in os.scandir(year_dir):
                        if not month_dir_entry.name.startswith('.'):
                            month = month_dir_entry.name
                            month_dir = month_dir_entry.path
                            
                            # Get the number of days in the month and compare it to number of files in dir.
                            _, n_days_month = calendar.monthrange(int(year), int(month))
                            n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if not dir_entry.name.startswith('.')])

                            # Only add the month if it has a full set of data.
                            if n_files == n_days_month:
                                miso_lmp_dir_struct[year].append(month)

            for node in miso_nodes.keys():
                tmp_dir = copy.deepcopy(miso_lmp_dir_struct)
                miso_data_bank['LMP'][node] = tmp_dir                
        
        # MCP scan.
        if 'MCP' in os.listdir(miso_root):
            miso_data_bank['MCP'] = {}
            mcp_dir = os.path.join(miso_root, 'MCP')

            for year_dir_entry in os.scandir(mcp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    year_dir = year_dir_entry.path
                    miso_data_bank['MCP'][year] = []

                    for month_dir_entry in os.scandir(year_dir):
                        if not month_dir_entry.name.startswith('.'):
                            month = month_dir_entry.name
                            month_dir = month_dir_entry.path
                            
                            # Get the number of days in the month and matches it to number of files in dir.
                            _, n_days_month = calendar.monthrange(int(year), int(month))
                            n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if not dir_entry.name.startswith('.')])

                            # Only add the month if it has a full set of data.
                            if n_files == n_days_month:
                                miso_data_bank['MCP'][year].append(month)
        
        self.data_bank['valuation']['MISO'] = miso_data_bank
    
    def _scan_ercot_data_bank(self):
        """Scans the ERCOT data bank."""
        ercot_root = os.path.join(self.data_bank_root, 'ERCOT')
        ercot_data_bank = {}
        ercot_nodes = self.get_nodes('ERCOT')

        # SPP scan.
        if 'SPP' in os.listdir(ercot_root):
            ercot_data_bank['SPP'] = {}
            spp_dir = os.path.join(ercot_root, 'SPP')

            # Scan SPP directory structure once.
            ercot_spp_dir_struct = {}

            for year_dir_entry in os.scandir(spp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    year_dir = year_dir_entry.path
                    ercot_spp_dir_struct[year] = []

                    # TODO: Not all yearly files have every month of data... but opening them to look is costly.
                    ercot_spp_dir_struct[year].extend([str(x+1).zfill(2) for x in range(0, 12)])

            for node in ercot_nodes.keys():
                tmp_dir = copy.deepcopy(ercot_spp_dir_struct)
                ercot_data_bank['SPP'][node] = tmp_dir
        
        # CCP scan.
        if 'CCP' in os.listdir(ercot_root):
            ercot_data_bank['CCP'] = {}
            ccp_dir = os.path.join(ercot_root, 'CCP')

            # Determine the years of data downloaded.
            for year_dir_entry in os.scandir(ccp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    year_dir = year_dir_entry.path
                    ercot_data_bank['CCP'][year] = []

                    # Verify a file exists in the directory.
                    if os.listdir(year_dir):
                        ercot_data_bank['CCP'][year].extend([str(x+1).zfill(2) for x in range(0, 12)])
        
        self.data_bank['valuation']['ERCOT'] = ercot_data_bank
    
    def _scan_nyiso_data_bank(self):
        """Scans the NYISO data bank."""
        nyiso_root = os.path.join(self.data_bank_root, 'NYISO')
        nyiso_data_bank = {}

        # LBMP scan.
        if 'LBMP' in os.listdir(nyiso_root):
            nyiso_data_bank['LBMP'] = {}

            pathf_nodeszones = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_nyiso.csv')
            df_nodeszones = pd.read_csv(pathf_nodeszones, index_col=False)

            # Get zone and gen nodes.
            df_zone_nodes = df_nodeszones.loc[df_nodeszones['Node ID'] == df_nodeszones['Zone ID'], :]
            df_gen_nodes = df_nodeszones.loc[df_nodeszones['Node ID'] != df_nodeszones['Zone ID'], :]

            # Gen nodes scan.
            lbmp_dir = os.path.join(nyiso_root, 'LBMP', 'DAM', 'gen')

            if os.path.exists(lbmp_dir):
                nyiso_lbmp_gen_dir_struct = {}

                for year_dir_entry in os.scandir(lbmp_dir):
                    if not year_dir_entry.name.startswith('.'):
                        year = year_dir_entry.name
                        year_dir = year_dir_entry.path
                        nyiso_lbmp_gen_dir_struct[year] = []

                        for month_dir_entry in os.scandir(year_dir):
                            if not month_dir_entry.name.startswith('.'):
                                month = month_dir_entry.name
                                month_dir = month_dir_entry.path

                                # Get the number of days in the month and compare it to number of files in dir.
                                _, n_days_month = calendar.monthrange(int(year), int(month))
                                n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if not dir_entry.name.startswith('.')])

                                # Only add the month if it has a full set of data.
                                if n_files == n_days_month:
                                    nyiso_lbmp_gen_dir_struct[year].append(month)

                for node_id in df_gen_nodes['Node ID']:
                    tmp_dir = copy.deepcopy(nyiso_lbmp_gen_dir_struct)
                    nyiso_data_bank['LBMP'][node_id] = tmp_dir
            
            # Zone nodes scan.
            lbmp_dir = os.path.join(nyiso_root, 'LBMP', 'DAM', 'zone')

            if os.path.exists(lbmp_dir):
                nyiso_lbmp_zone_dir_struct = {}

                for year_dir_entry in os.scandir(lbmp_dir):
                    if not year_dir_entry.name.startswith('.'):
                        year = year_dir_entry.name
                        year_dir = year_dir_entry.path
                        nyiso_lbmp_zone_dir_struct[year] = []

                        for month_dir_entry in os.scandir(year_dir):
                            if not month_dir_entry.name.startswith('.'):
                                month = month_dir_entry.name
                                month_dir = month_dir_entry.path

                                # Get the number of days in the month and compare it to number of files in dir.
                                _, n_days_month = calendar.monthrange(int(year), int(month))
                                n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if not dir_entry.name.startswith('.')])

                                # Only add the month if it has a full set of data.
                                if n_files == n_days_month:
                                    nyiso_lbmp_zone_dir_struct[year].append(month)

                for node_id in df_zone_nodes['Node ID']:
                    tmp_dir = copy.deepcopy(nyiso_lbmp_zone_dir_struct)
                    nyiso_data_bank['LBMP'][node_id] = tmp_dir

        # ASP scan.
        if 'ASP' in os.listdir(nyiso_root):
            nyiso_data_bank['ASP'] = {}
            asp_dir = os.path.join(nyiso_root, 'ASP', 'DAM')

            for year_dir_entry in os.scandir(asp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    year_dir = year_dir_entry.path
                    nyiso_data_bank['ASP'][year] = []

                    for month_dir_entry in os.scandir(year_dir):
                        if not month_dir_entry.name.startswith('.'):
                            month = month_dir_entry.name
                            month_dir = month_dir_entry.path

                            # Get the number of days in the month and matches it to number of files in dir.
                            _, n_days_month = calendar.monthrange(int(year), int(month))
                            n_files = len \
                                ([dir_entry for dir_entry in os.scandir(month_dir) if
                                  not dir_entry.name.startswith('.')])

                            # Only add the month if it has a full set of data.
                            if n_files == n_days_month:
                                nyiso_data_bank['ASP'][year].append(month)

        self.data_bank['valuation']['NYISO'] = nyiso_data_bank

    def _scan_isone_data_bank(self):
        """Scans the ISONE data bank."""
        isone_root = os.path.join(self.data_bank_root, 'ISONE')
        isone_data_bank = {}

        # Scan LMP files.
        if 'LMP' in os.listdir(isone_root):
            isone_data_bank['LMP'] = {}
            lmp_dir = os.path.join(isone_root, 'LMP')

            # Identify pricing node ID dirs.
            for node_dir_entry in os.scandir(lmp_dir):
                if not node_dir_entry.name.startswith('.'):
                    node_id = node_dir_entry.name
                    isone_data_bank['LMP'][node_id] = {}
                    node_id_dir = node_dir_entry.path

                    # Identify year dirs.
                    for year_dir_entry in os.scandir(node_id_dir):
                        if not year_dir_entry.name.startswith('.'):
                            year = year_dir_entry.name
                            isone_data_bank['LMP'][node_id][year] = []
                            year_dir = year_dir_entry.path

                            # Identify month files.
                            for lmp_dir_entry in os.scandir(year_dir):
                                if not lmp_dir_entry.name.startswith('.'):
                                    lmp_file = lmp_dir_entry.name
                                    yyyymm, _ = lmp_file.split('_', maxsplit=1)
                                    month = yyyymm[-2:]
                                    isone_data_bank['LMP'][node_id][year].append(month)

        # Scan ASP files.
        if 'RCP' in os.listdir(isone_root):
            isone_data_bank['RCP'] = {}
            rcp_dir = os.path.join(isone_root, 'RCP')

            # Identify year dirs.
            for year_dir_entry in os.scandir(rcp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    isone_data_bank['RCP'][year] = []
                    year_dir = year_dir_entry.path

                    # Identify month files.
                    for rcp_dir_entry in os.scandir(year_dir):
                        if not rcp_dir_entry.name.startswith('.'):
                            rcp_file = rcp_dir_entry.name
                            yyyymm, _ = rcp_file.split('_', maxsplit=1)
                            month = yyyymm[-2:]
                            isone_data_bank['RCP'][year].append(month)

        self.data_bank['valuation']['ISONE'] = isone_data_bank

    def _scan_spp_data_bank(self):
        """Scans the SPP data bank."""
        spp_root = os.path.join(self.data_bank_root, 'SPP')
        spp_data_bank = {}
        # spp_nodes = self.get_nodes('SPP')

        # LMP scan.
        if 'LMP' in os.listdir(spp_root):
            spp_data_bank['LMP'] = {}

            pathf_nodes = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_spp.csv')
            df_nodes = pd.read_csv(pathf_nodes, index_col=False)

            # Get location and bus nodes.
            df_loc_nodes = df_nodes.loc[df_nodes['Node Type'] == 'Location', :]
            df_bus_nodes = df_nodes.loc[df_nodes['Node Type'] == 'Bus', :]

            # Location nodes scan.
            lmp_dir = os.path.join(spp_root, 'LMP', 'DAM', 'location')

            if os.path.exists(lmp_dir):
                spp_lmp_loc_dir_struct = {}

                for year_dir_entry in os.scandir(lmp_dir):
                    if not year_dir_entry.name.startswith('.'):
                        year = year_dir_entry.name
                        year_dir = year_dir_entry.path
                        spp_lmp_loc_dir_struct[year] = []

                        for month_dir_entry in os.scandir(year_dir):
                            if not month_dir_entry.name.startswith('.'):
                                month = month_dir_entry.name
                                month_dir = month_dir_entry.path

                                # Get the number of days in the month and compare it to number of files in dir.
                                _, n_days_month = calendar.monthrange(int(year), int(month))
                                n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if
                                               not dir_entry.name.startswith('.')])

                                # Only add the month if it has a full set of data.
                                if n_files == n_days_month:
                                    spp_lmp_loc_dir_struct[year].append(month)

                for node in df_loc_nodes['Node ID']:
                    tmp_dir = copy.deepcopy(spp_lmp_loc_dir_struct)
                    spp_data_bank['LMP'][node] = tmp_dir

            # Bus nodes scan.
            lmp_dir = os.path.join(spp_root, 'LMP', 'DAM', 'bus')

            if os.path.exists(lmp_dir):
                spp_lmp_bus_dir_struct = {}

                for year_dir_entry in os.scandir(lmp_dir):
                    if not year_dir_entry.name.startswith('.'):
                        year = year_dir_entry.name
                        year_dir = year_dir_entry.path
                        spp_lmp_bus_dir_struct[year] = []

                        for month_dir_entry in os.scandir(year_dir):
                            if not month_dir_entry.name.startswith('.'):
                                month = month_dir_entry.name
                                month_dir = month_dir_entry.path

                                # Get the number of days in the month and compare it to number of files in dir.
                                _, n_days_month = calendar.monthrange(int(year), int(month))
                                n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if
                                               not dir_entry.name.startswith('.')])

                                # Only add the month if it has a full set of data.
                                if n_files == n_days_month:
                                    spp_lmp_bus_dir_struct[year].append(month)

                for node in df_bus_nodes['Node ID']:
                    tmp_dir = copy.deepcopy(spp_lmp_bus_dir_struct)
                    spp_data_bank['LMP'][node] = tmp_dir


        # MCP scan.
        if 'MCP' in os.listdir(spp_root):
            spp_data_bank['MCP'] = {}
            mcp_dir = os.path.join(spp_root, 'MCP', 'DAM')

            for year_dir_entry in os.scandir(mcp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    year_dir = year_dir_entry.path
                    spp_data_bank['MCP'][year] = []

                    for month_dir_entry in os.scandir(year_dir):
                        if not month_dir_entry.name.startswith('.'):
                            month = month_dir_entry.name
                            month_dir = month_dir_entry.path

                            # Get the number of days in the month and matches it to number of files in dir.
                            _, n_days_month = calendar.monthrange(int(year), int(month))
                            n_files = len([dir_entry for dir_entry in os.scandir(month_dir) if
                                           not dir_entry.name.startswith('.')])

                            # Only add the month if it has a full set of data.
                            if n_files == n_days_month:
                                spp_data_bank['MCP'][year].append(month)

        self.data_bank['valuation']['SPP'] = spp_data_bank
    
    def _scan_caiso_data_bank(self):
        """Scans the CAISO data bank."""
        caiso_root = os.path.join(self.data_bank_root, 'CAISO')
        caiso_data_bank = {}

        # Scan LMP files.
        if 'LMP' in os.listdir(caiso_root):
            caiso_data_bank['LMP'] = {}
            lmp_dir = os.path.join(caiso_root, 'LMP')

            # Identify pricing node ID dirs.
            for node_dir_entry in os.scandir(lmp_dir):
                if not node_dir_entry.name.startswith('.'):
                    node_id = node_dir_entry.name
                    caiso_data_bank['LMP'][node_id] = {}
                    node_id_dir = node_dir_entry.path

                    # Identify year dirs.
                    for year_dir_entry in os.scandir(node_id_dir):
                        if not year_dir_entry.name.startswith('.'):
                            year = year_dir_entry.name
                            caiso_data_bank['LMP'][node_id][year] = []
                            year_dir = year_dir_entry.path

                            # Identify month files.
                            for lmp_dir_entry in os.scandir(year_dir):
                                if not lmp_dir_entry.name.startswith('.'):
                                    lmp_file = lmp_dir_entry.name
                                    yyyymm, _ = lmp_file.split('_', maxsplit=1)
                                    month = yyyymm[-2:]
                                    caiso_data_bank['LMP'][node_id][year].append(month)

        # Scan Reg files.
        if 'ASP' in os.listdir(caiso_root):
            caiso_data_bank['ASP'] = {}
            asp_dir = os.path.join(caiso_root, 'ASP')

            # Identify year dirs.
            for year_dir_entry in os.scandir(asp_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    caiso_data_bank['ASP'][year] = []
                    year_dir = year_dir_entry.path

                    # Identify month files.
                    for asp_dir_entry in os.scandir(year_dir):
                        if not asp_dir_entry.name.startswith('.'):
                            asp_file = asp_dir_entry.name
                            yyyymm, _ = asp_file.split('_', maxsplit=1)
                            month = yyyymm[-2:]
                            caiso_data_bank['ASP'][year].append(month)

        # Scan Mileage files.
        if 'MILEAGE' in os.listdir(caiso_root):
            caiso_data_bank['MILEAGE'] = {}
            mileage_dir = os.path.join(caiso_root, 'MILEAGE')

            # Identify year dirs.
            for year_dir_entry in os.scandir(mileage_dir):
                if not year_dir_entry.name.startswith('.'):
                    year = year_dir_entry.name
                    caiso_data_bank['MILEAGE'][year] = []
                    year_dir = year_dir_entry.path

                    # Identify month files.
                    for mileage_dir_entry in os.scandir(year_dir):
                        if not mileage_dir_entry.name.startswith('.'):
                            mileage_file = mileage_dir_entry.name
                            yyyymm, _ = mileage_file.split('_', maxsplit=1)
                            month = yyyymm[-2:]
                            caiso_data_bank['MILEAGE'][year].append(month)

        self.data_bank['valuation']['CAISO'] = caiso_data_bank
    
    def get_nodes(self, market_area):
        """Retrieves all available pricing nodes for the given market_area."""
        if market_area == 'ERCOT':
            # Reads static node ID list.
            static_ercot_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_ercot.csv')

            node_df = pd.read_csv(static_ercot_node_list)
            node_dict = {row[0]: row[1] for row in zip(node_df['Node ID'], node_df['Node Name'])}
        elif market_area == 'PJM':
            # Reads static node ID list.
            static_pjm_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_pjm.csv')
            node_df = pd.read_csv(static_pjm_node_list)
            node_mapping = {str(row[0]): '{nodename} ({nodeid})'.format(nodename=row[1], nodeid=row[0]) for row in zip(node_df['Node ID'], node_df['Node Name'])}

            # Reads keys of PJM LMP data bank.
            node_id_list = self.data_bank['valuation']['PJM']['LMP'].keys()
            node_dict = {node_id: node_mapping.get(node_id, node_id) for node_id in node_id_list}
        elif market_area == 'MISO':
            # Reads static node ID list.
            static_miso_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_miso.csv')

            node_df = pd.read_csv(static_miso_node_list)
            node_dict = {row[0]: row[1] for row in zip(node_df['Node ID'], node_df['Node Name'])}
        elif market_area == 'NYISO':
            # Reads static node ID list.
            static_nyiso_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_nyiso.csv')
            node_df = pd.read_csv(static_nyiso_node_list)
            node_mapping = {row[0]: row[1] for row in zip(node_df['Node ID'], node_df['Node Name'])}

            # Reads keys of NYISO LBMP data bank.
            node_id_list = self.data_bank['valuation']['NYISO']['LBMP'].keys()
            node_dict = {node_id: node_mapping.get(node_id, node_id) for node_id in node_id_list}
        elif market_area == 'ISONE':
            # Reads static node ID list.
            static_isone_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_isone.csv')
            node_df = pd.read_csv(static_isone_node_list, encoding="cp1252")

            node_dict = {str(row[0]): '{nodename} ({nodeid})'.format(nodename=row[1], nodeid=row[0]) for row in zip(node_df['Node ID'], node_df['Node Name'])}

            # Reads keys of PJM LMP data bank.
            node_id_list = self.data_bank['valuation']['ISONE']['LMP'].keys()
            node_dict = {node_id: node_dict.get(node_id, node_id) for node_id in node_id_list}
        elif market_area == 'SPP':
            # Reads static node ID list.
            static_spp_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_spp.csv')

            node_df = pd.read_csv(static_spp_node_list)
            node_dict = {row[0]: row[1] for row in zip(node_df['Node ID'], node_df['Node Name'])}
        elif market_area == 'CAISO':
            # Reads static node ID list.
            static_caiso_node_list = os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nodes_caiso.csv')
            node_df = pd.read_csv(static_caiso_node_list)

            node_id_list = self.data_bank['valuation']['CAISO']['LMP'].keys()
            node_dict = {node_x: node_x for node_x in node_id_list}
        # Use the PJM pattern of reading data_bank node keys to generate the node_dict (key = value) if no CSV LUT exists.
        else:
            raise(DataManagerException('Invalid market_area given (got {0})'.format(market_area)))
        
        # Sort by name alphabetically before returning.
        return_dict = collections.OrderedDict(sorted(node_dict.items(), key=lambda t: t[1]))
        
        return return_dict
    
    def get_valuation_revstreams(self, market_area, node):
        """Retrieves the available revenue streams for a given node in a given market_area based on downloaded data."""
        rev_stream_dict = {}

        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'valuation_rev_streams.json'), 'r') as fp:
            rev_stream_defs = json.load(fp).get(market_area, {})

        if market_area == 'ERCOT':
            ercot_data_bank = self.data_bank['valuation']['ERCOT']

            spp_data = ercot_data_bank['SPP'].get(node, [])
            ccp_data = ercot_data_bank.get('CCP', [])

            if spp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if spp_data and ccp_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
        elif market_area == 'PJM':
            pjm_data_bank = self.data_bank['valuation']['PJM']

            lmp_data = pjm_data_bank['LMP'].get(node, [])
            reg_data = pjm_data_bank.get('REG', [])
            mileage_data = pjm_data_bank.get('MILEAGE', [])

            if lmp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if lmp_data and reg_data and mileage_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
        elif market_area == 'MISO':
            miso_data_bank = self.data_bank['valuation']['MISO']

            lmp_data = miso_data_bank['LMP'].get(node, [])
            reg_data = miso_data_bank.get('MCP', [])

            if lmp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if lmp_data and reg_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
        elif market_area == 'NYISO':
            # print("NYISO case data manager")
            nyiso_data_bank = self.data_bank['valuation']['NYISO']

            lbmp_data = nyiso_data_bank['LBMP'].get(node, [])
            asp_data = nyiso_data_bank.get('ASP', [])

            if lbmp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if lbmp_data and asp_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
                # print("NYISO case data manager")
                # print(rev_stream_dict)

        elif market_area == 'ISONE':
            # print("ISONE case data manager 1")
            isone_data_bank = self.data_bank['valuation']['ISONE']

            lmp_data = isone_data_bank['LMP'].get(node, [])
            rcp_data = isone_data_bank.get('RCP', [])

            if lmp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if lmp_data and rcp_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
                # print("ISONE case data manager")
                # print(rev_stream_dict)
        elif market_area == 'SPP':
            spp_data_bank = self.data_bank['valuation']['SPP']

            lmp_data = spp_data_bank['LMP'].get(node, [])
            mcp_data = spp_data_bank.get('MCP', [])

            if lmp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if lmp_data and mcp_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
        elif market_area == 'CAISO':
            caiso_data_bank = self.data_bank['valuation']['CAISO']

            lmp_data = caiso_data_bank['LMP'].get(node, [])
            asp_data = caiso_data_bank.get('ASP', [])
            mileage_data = caiso_data_bank.get('MILEAGE', [])

            if lmp_data:
                # Arbitrage is available.
                rev_stream_dict['Arbitrage'] = rev_stream_defs['Arbitrage']
            if lmp_data and asp_data and mileage_data:
                # Arbitrage and regulation is available.
                rev_stream_dict['Arbitrage and regulation'] = rev_stream_defs['Arbitrage and regulation']
        else:
            raise(DataManagerException('Invalid market_area given (got {0})'.format(market_area)))
            
        return rev_stream_dict
    
    def get_historical_datasets(self, market_area, node, rev_streams):
        """Retrieves the available historical datasets for a given node in a given market area using the given rev_streams."""
        hist_datasets_dict = {}

        hist_data_options = self.get_historical_data_options(market_area, node, rev_streams)

        for year, month_list in hist_data_options.items():
            hist_dataset = [{'month': month, 'year': year} for month in month_list]
            hist_datasets_dict['{year}'.format(year=year)] = hist_dataset

        # Sort before returning.
        return_dict = collections.OrderedDict(sorted(hist_datasets_dict.items(), key=lambda t: int(t[0])))
        
        return return_dict
    
    def get_historical_data_options(self, market_area, node, rev_streams):
        """Retrieves the years of available historical data for a given node in a given market area using the given rev_streams."""
        hist_data_options = {}

        if market_area == 'ERCOT':
            ercot_data_bank = self.data_bank['valuation']['ERCOT']

            spp_data = ercot_data_bank['SPP'].get(node, {})

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation data is downloaded for each month.
                reg_data = ercot_data_bank['CCP']

                for year, month_list in spp_data.items():
                    reg_month_list = reg_data.get(year, [])

                    # Compute intersection of all data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = spp_data
        elif market_area == 'PJM':
            pjm_data_bank = self.data_bank['valuation']['PJM']

            lmp_data = pjm_data_bank['LMP'].get(node, {})

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation and mileage data is downloaded for each month.
                reg_data = pjm_data_bank['REG']
                mileage_data = pjm_data_bank['MILEAGE']

                for year, month_list in lmp_data.items():
                    reg_month_list = reg_data.get(year, [])
                    mileage_month_list = mileage_data.get(year, [])

                    # Compute intersection of all three data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)).intersection(set(mileage_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = lmp_data
        elif market_area == 'MISO':
            miso_data_bank = self.data_bank['valuation']['MISO']

            lmp_data = miso_data_bank['LMP'].get(node, {})

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation data is downloaded for each month.
                reg_data = miso_data_bank['MCP']

                for year, month_list in lmp_data.items():
                    reg_month_list = reg_data.get(year, [])

                    # Compute intersection of all data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = lmp_data
        elif market_area == 'NYISO':
            nyiso_data_bank = self.data_bank['valuation']['NYISO']

            lbmp_data = nyiso_data_bank['LBMP'].get(node, {})

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation data is downloaded for each month.
                reg_data = nyiso_data_bank['ASP']

                for year, month_list in lbmp_data.items():
                    reg_month_list = reg_data.get(year, [])

                    # Compute intersection of all data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = lbmp_data
        elif market_area == 'ISONE':
            isone_data_bank = self.data_bank['valuation']['ISONE']

            lmp_data = isone_data_bank['LMP'].get(node, {})

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation data is downloaded for each month.
                reg_data = isone_data_bank['RCP']

                for year, month_list in lmp_data.items():
                    reg_month_list = reg_data.get(year, [])

                    # Compute intersection of all data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = lmp_data
        elif market_area == 'SPP':
            spp_data_bank = self.data_bank['valuation']['SPP']

            lmp_data = spp_data_bank['LMP'].get(node, {})

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation data is downloaded for each month.
                reg_data = spp_data_bank['MCP']

                for year, month_list in lmp_data.items():
                    reg_month_list = reg_data.get(year, [])

                    # Compute intersection of all data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = lmp_data

        elif market_area == 'CAISO':
            caiso_data_bank = self.data_bank['valuation']['CAISO']

            lmp_data = caiso_data_bank['LMP'].get(node, {})
            # print(lmp_data)

            if rev_streams == 'Arbitrage and regulation':
                # Ensure regulation and mileage data is downloaded for each month.
                reg_data = caiso_data_bank['ASP']
                mileage_data = caiso_data_bank['MILEAGE']

                for year, month_list in lmp_data.items():
                    reg_month_list = reg_data.get(year, [])
                    mileage_month_list = mileage_data.get(year, [])

                    # Compute intersection of all three data types.
                    months_common = list(set(month_list).intersection(set(reg_month_list)).intersection(set(mileage_month_list)))

                    if months_common:
                        hist_data_options[year] = sorted(months_common)
            else:
                hist_data_options = lmp_data
        else:
            raise(DataManagerException('Invalid market_area given (got {0})'.format(market_area)))
        
        # Sort before returning.
        return_dict = collections.OrderedDict(sorted(hist_data_options.items(), key=lambda t: int(t[0])))

        return return_dict

    def get_valuation_device_templates(self):
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'valuation_device_templates.json'), 'r') as fp:
            device_list = json.load(fp)
        
        return device_list
    
    def get_valuation_wizard_device_params(self):
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'valuation_device_params.json'), 'r') as fp:
            device_params = json.load(fp)
        
        return device_params
    
    def get_valuation_model_params(self, market_area):
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'valuation_model_params.json'), 'r') as fp:
            model_params_all = json.load(fp)
        
        model_params = model_params_all.get(market_area, {})

        return model_params
    
    def get_btm_cost_savings_model_params(self):
        """Returns the list of dictionaries of parameters for the energy storage system model in the BTM cost savings application."""
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'btm_cost_savings_model_params.json'), 'r') as fp:
            model_params_all = json.load(fp)

        return model_params_all
    
    def get_pvwatts_search_params(self):
        """Returns the list of dictionaries of parameters for the PVWatts PV profile search."""
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'pvwatts_search_parameters.json'), 'r') as fp:
            model_params_all = json.load(fp)

        return model_params_all
    
    def get_nsrdb_search_params(self):
        """Returns the list of dictionaries of parameters for the NSRDB search."""
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'nsrdb_data_parameters.json'), 'r') as fp:
            model_params_all = json.load(fp)

        return model_params_all
    
    def scan_performance_data_bank(self):
        """Scans the performance data bank to determine what data has been downloaded."""
        # Check if data bank exists.
        try:
            os.listdir(self.data_bank_root)
        except FileNotFoundError:
            return

        # Open loading screen.
        self.loading_screen = LoadingModalView()
        self.loading_screen.loading_text.text = 'Scanning data files...'
        self.loading_screen.open()

        self.n_threads_scanning = 1

        def _scan_performance_data_bank():
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                return

            self._scan_idf_data_bank()
            self._scan_weather_data_bank()
            self._scan_ess_profile_data_bank()

            self.n_threads_scanning -= 1
        
        thread = threading.Thread(target=_scan_performance_data_bank)
        thread.start() 
        
    def _scan_idf_data_bank(self):
        """"""
        idf_root = os.path.join(self.data_bank_root, 'idf')
        idf_data_bank = {}

        try:
            os.listdir(idf_root)
        except FileNotFoundError:
            return
        
        try:
            for idf_folder in os.scandir(idf_root):
                if not idf_folder.name.startswith('.'):
                    hvac_root = idf_folder.path
                    
                    hvac_name = idf_folder.name
                    idf_data_bank[hvac_name] = []
                    for hvac_file in os.scandir(hvac_root):
                        if not hvac_file.name.startswith('.'):
                            hvac_fname = hvac_file.name
                            hvac_dir = hvac_file.path
                            idf_data_bank[hvac_name].append([hvac_fname,hvac_dir])
        except NotADirectoryError:
            return
        else:
            self.data_bank['idf files'] = idf_data_bank
        
    def _scan_weather_data_bank(self):
        """"""
        weather_root = os.path.join(self.data_bank_root,'weather')
        weather_data_bank = {}
        
        try: 
            os.listdir(weather_root)
        except FileNotFoundError:
            return
        
        try:
            for weather_folder in os.scandir(weather_root):
                if not weather_folder.name.startswith('.'):
                    location_root = weather_folder.path
                    
                    weather_key = weather_folder.name
                    weather_data_bank[weather_key] = []
                    for weather_file in os.scandir(location_root):
                        if not weather_file.name.startswith('.'):
                            weather_name = weather_file.name
                            weather_dir = weather_file.path
                            
                            weather_data_bank[weather_key].append([weather_name,weather_dir])
        except NotADirectoryError:
            return
        else:
            self.data_bank['weather files'] = weather_data_bank
        
    def _scan_ess_profile_data_bank(self):
        """"""
        profile_root = os.path.join(self.data_bank_root, 'profile')
        profile_data_bank = {}

        try:
            os.listdir(profile_root)
        except FileNotFoundError:
            return
        
        try:
            for profile_folder in os.scandir(profile_root):
                if not profile_folder.name.startswith('.'):
                    p_root = profile_folder.path
                    
                    profile_key = profile_folder.name
                    profile_data_bank[profile_key] = []
                    for profile_file in os.scandir(p_root):
                        if not profile_file.name.startswith('.'):
                            profile_key = profile_folder.name
                            profile_fname = profile_file.name
                            profile_dir = profile_file.path
                            
                            profile_data_bank[profile_key].append([profile_fname,profile_dir])
        except NotADirectoryError:
            return
        else:
            self.data_bank['profiles'] = profile_data_bank   
        
    def get_tech_selection_params(self):
        """Returns the dictionary of parameters (user selections) for the technology selection application."""
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'tech_selection_params.json'), 'r') as fp:
            model_params_all = json.load(fp)
            
        return model_params_all
        
    def get_techs_db(self):
        """"""
        return pd.read_excel(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'techs_Database.xlsx'), index_col='Storage technology')
        
    def get_applications_db(self):
        """"""
        apps_db = pd.read_csv(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'applications_database.csv'), index_col=0)
        return apps_db.sort_index()
        
    def get_tech_selection_all_options(self):
        """"""
        with open(os.path.join(dirname, 'es_gui', 'apps', 'data_manager', '_static', 'tech_selection_all_options_names.csv')) as csvfile:
            reader = csv.reader(csvfile)
            all_options_names = {}
            for row in reader:
                all_options_names[row[0]] = row[1:]   
        
        return all_options_names
        
#    def get_idfs(self):
#        
#        try:
#            idf_files = self.data_bank[]
        

class DataManagerException(Exception):
    pass


if __name__ == '__main__':
    dm = DataManager()
    dm.scan_btm_data_bank()
    # print('cwd: ', os.getcwd())
    # dm.scan_valuation_data_bank()

    # market_area = 'PJM'
    # node = '113745'
    # rev_streams = 'Arbitrage and regulation'

    #print(dm.get_historical_datasets(market_area, node, rev_streams))


