from __future__ import absolute_import

import os
import io
import threading
import logging

import requests
import pandas as pd
from bs4 import BeautifulSoup

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, DictProperty

from es_gui.apps.data_manager.data_manager import DATA_HOME
from es_gui.apps.data_manager.utils import check_connection_settings
from es_gui.resources.widgets.common import InputError, WarningPopup, MyPopup, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction, fade_in_animation


DATASET_ROOT = 'https://openei.org/datasets/files/961/pub/'
COMMERCIAL_LOAD_ROOT = DATASET_ROOT + 'COMMERCIAL_LOAD_DATA_E_PLUS_OUTPUT/'
RESIDENTIAL_LOAD_ROOT = DATASET_ROOT + 'RESIDENTIAL_LOAD_DATA_E_PLUS_OUTPUT/'


class DataManagerLoadHomeScreen(Screen):
    """"""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager: Hourly Commercial/Residential Load Profiles')


class DataManagerCommercialLoadScreen(Screen):
    """"""
    df_locations = pd.DataFrame()
    state_selected = StringProperty('')
    location_selected = DictProperty()
    building_selected = DictProperty()

    def __init__(self, **kwargs):
        super(DataManagerCommercialLoadScreen, self).__init__(**kwargs)

        StateRVEntry.host_screen = self
        LocationRVEntry.host_screen = self
        BuildingRVEntry.host_screen = self

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager: Hourly Commercial Load Profiles')

        StateRVEntry.host_screen = self
        LocationRVEntry.host_screen = self
        BuildingRVEntry.host_screen = self

        if self.df_locations.empty:
            logging.info('CommercialLoadDM: Retrieving locations from database...')
            ssl_verify, proxy_settings = check_connection_settings()

            thread_locations = threading.Thread(target=self._get_locations, args=[ssl_verify, proxy_settings])
            thread_locations.start()
    
    def _get_locations(self, ssl_verify=True, proxy_settings=None):
        # Convert root page content to BeautifulSoup.
        page = requests.get(COMMERCIAL_LOAD_ROOT, timeout=10, verify=ssl_verify, proxies=proxy_settings)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Get the bulleted list of locations.
        location_tags = soup.body.ul
        
        # Convert bulleted list to DataFrame.
        locations = []

        for link in location_tags.find_all('a')[1:]:
            # [1:] to skip the link to the parent directory.
            loc_root = link['href']
            country, state_abbr, name, _ = loc_root.split('_')

            name = ' '.join(name.split('.')[:-1])

            locations.append({'country': country, 'state': state_abbr, 'name': name, 'link': COMMERCIAL_LOAD_ROOT + loc_root})

        self.df_locations = pd.DataFrame.from_records(locations)

        # Populate state RV.
        records = [{'name': state} for state in self.df_locations['state'].unique()]
        records = sorted(records, key=lambda t: t['name'])

        self.state_rv.data = records
        self.state_rv.unfiltered_data = records
    
    def _get_building_types(self, location_root, ssl_verify=True, proxy_settings=None):
        # Convert root page content to BeautifulSoup
        page = requests.get(location_root, timeout=10, verify=ssl_verify, proxies=proxy_settings)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Get the bulleted list of building types
        building_tags = soup.body.ul
        
        # Convert bulleted list to DataFrame
        building_types = []

        for link in building_tags.find_all('a')[1:]:
            # [1:] to skip the link to the parent directory
            csv_link = link['href']
            name = csv_link.split('_')[0]

            building_types.append({'name': name, 'link': location_root + csv_link})
        
        building_types = sorted(building_types, key=lambda t: t['name'])

        self.building_rv.data = building_types
        self.building_rv.unfiltered_data = building_types

    def on_state_selected(self, instance, value):
        try:
            logging.info('CommercialLoadDM: State selection changed to {0}.'.format(value))
        except KeyError:
            logging.info('CommercialLoadDM: State selection reset.')
        else:
            locations = self.df_locations.loc[self.df_locations['state'] == value]

            records = locations.to_dict(orient='records')
            records = [{'name': record['name'], 'link': record['link']} for record in records]
            records = sorted(records, key=lambda t: t['name'])

            self.location_rv.data = records
            self.location_rv.unfiltered_data = records
        finally:
            self.location_rv.deselect_all_nodes()
            self.location_rv_filter.text = ''
            self.location_selected = ''

    def on_location_selected(self, instance, value):
        try:
            logging.info('CommercialLoadDM: Location selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('CommercialLoadDM: Location selection reset.')
        else:
            location_root_link = value['link']

            ssl_verify, proxy_settings = check_connection_settings()

            thread_building_types = threading.Thread(target=self._get_building_types, args=[location_root_link, ssl_verify, proxy_settings])
            thread_building_types.start()
        finally:
            self.building_rv.deselect_all_nodes()
            self.building_rv_filter.text = ''
            self.building_selected = {}
            self.building_rv.data = []
            self.building_rv.unfiltered_data = []
    
    def on_building_selected(self, instance, value):
        try:
            logging.info('CommercialLoadDM: Building type selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('CommercialLoadDM: Building type selection reset.')
    
    def _validate_selections(self):
        csv_link = self.building_selected['link']

        return csv_link
    
    def save_load_data(self):
        """Saves the data for the building type selected."""
        try:
            csv_link = self._validate_selections()
        except Exception as e:
            print(e)
        else:
            ssl_verify, proxy_settings = check_connection_settings()

            with requests.Session() as req:
                http_request = req.get(csv_link,
                                        proxies=None, 
                                        timeout=6, 
                                        verify=ssl_verify,
                                        stream=proxy_settings)

                if http_request.status_code != requests.codes.ok:
                    http_request.raise_for_status()
            
            data_down = http_request.content.decode(http_request.encoding)
            csv_data = pd.read_csv(io.StringIO(data_down))

            electricity_data = csv_data[['Date/Time', 'Electricity:Facility [kW](Hourly)']]

            # Save to persistent object on disk.
            url_split = csv_link.split('/')

            destination_dir = os.path.join(DATA_HOME, 'load', 'commercial', url_split[-2])
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, url_split[-1])

            electricity_data.to_csv(destination_file, sep=',', index=False)

            popup = WarningPopup()
            popup.title = 'Success!'
            popup.popup_text.text = 'Load data successfully saved.'
            popup.open()

            logging.info('CommercialLoadDM: Load data successfully saved.')
            

class StateRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(StateRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.state_selected = rv.data[self.index]['name']


class LocationRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(LocationRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.location_selected = rv.data[self.index]


class BuildingRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(BuildingRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.building_selected = rv.data[self.index]


class DataManagerResidentialLoadScreen(Screen):
    """"""
    df_locations = pd.DataFrame()
    load_type_selected = DictProperty()
    state_selected = StringProperty('')
    location_selected = DictProperty()

    def __init__(self, **kwargs):
        super(DataManagerResidentialLoadScreen, self).__init__(**kwargs)

        LoadTypeRVEntry.host_screen = self
        LocationRVEntry.host_screen = self
        StateRVEntry.host_screen = self

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager: Hourly Residential Load Profiles')

        LoadTypeRVEntry.host_screen = self
        LocationRVEntry.host_screen = self
        StateRVEntry.host_screen = self

        ssl_verify, proxy_settings = check_connection_settings()

        thread_locations = threading.Thread(target=self._get_load_types, args=[ssl_verify, proxy_settings])
        thread_locations.start()
    
    def _get_load_types(self, ssl_verify=True, proxy_settings=None):
        # Convert root page content to BeautifulSoup.
        page = requests.get(RESIDENTIAL_LOAD_ROOT, timeout=10, verify=ssl_verify, proxies=proxy_settings)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Get the bulleted list of locations.
        load_tags = soup.body.ul
        
        # Convert bulleted list to DataFrame.
        load_types = []

        for link in load_tags.find_all('a')[1:]:
            # [1:] to skip the link to the parent directory.
            type_root = link['href']

            load_types.append({'name': type_root[:-1], 'link': RESIDENTIAL_LOAD_ROOT + type_root})

        # Populate load types RV.
        records = [{'name': load_type['name'], 'link': load_type['link']} for load_type in load_types]
        records = sorted(records, key=lambda t: t['name'])

        self.load_type_rv.data = records
        self.load_type_rv.unfiltered_data = records
    
    def _get_locations(self, load_root_link, ssl_verify=True, proxy_settings=None):
        # Convert root page content to BeautifulSoup.
        page = requests.get(load_root_link, timeout=10, verify=ssl_verify, proxies=proxy_settings)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Get the bulleted list of locations.
        location_tags = soup.body.ul
        
        # Convert bulleted list to DataFrame.
        locations = []

        for link in location_tags.find_all('a')[1:]:
            # [1:] to skip the link to the parent directory.
            loc_root = link['href']
            country, state_abbr, name, _, _ = loc_root.split('_')

            name = ' '.join(name.split('.')[:-1])

            locations.append({'country': country, 'state': state_abbr, 'name': name, 'link': load_root_link + loc_root})

        self.df_locations = pd.DataFrame.from_records(locations)

        # Populate state RV.
        records = [{'name': state} for state in self.df_locations['state'].unique()]
        records = sorted(records, key=lambda t: t['name'])

        self.state_rv.data = records
        self.state_rv.unfiltered_data = records
    
    def on_load_type_selected(self, instance, value):
        try:
            logging.info('ResidentialLoadDM: Load type selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('ResidentialLoadDM: Load type selection reset.')
        else:
            load_type_root_link = value['link']

            ssl_verify, proxy_settings = check_connection_settings()

            thread_building_types = threading.Thread(target=self._get_locations, args=[load_type_root_link, ssl_verify, proxy_settings])
            thread_building_types.start()
        finally:
            self.state_rv.deselect_all_nodes()
            self.state_rv_filter.text = ''
            self.state_selected = ''

    def on_state_selected(self, instance, value):
        try:
            logging.info('ResidentialLoadDM: State selection changed to {0}.'.format(value))
        except KeyError:
            logging.info('ResidentialLoadDM: State selection reset.')
        else:
            locations = self.df_locations.loc[self.df_locations['state'] == value]

            records = locations.to_dict(orient='records')
            records = [{'name': record['name'], 'link': record['link']} for record in records]
            records = sorted(records, key=lambda t: t['name'])

            self.location_rv.data = records
            self.location_rv.unfiltered_data = records
        finally:
            self.location_rv.deselect_all_nodes()
            self.location_rv_filter.text = ''
            self.location_selected = ''

    def on_location_selected(self, instance, value):
        try:
            logging.info('ResidentialLoadDM: Location selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('ResidentialLoadDM: Location selection reset.')
    
    def _validate_selections(self):
        csv_link = self.location_selected['link']

        return csv_link
    
    def save_load_data(self):
        """Saves the data for the building type selected."""
        try:
            csv_link = self._validate_selections()
        except Exception as e:
            print(e)
        else:
            ssl_verify, proxy_settings = check_connection_settings()

            with requests.Session() as req:
                http_request = req.get(csv_link,
                                        proxies=None, 
                                        timeout=6, 
                                        verify=ssl_verify,
                                        stream=proxy_settings)

                if http_request.status_code != requests.codes.ok:
                    http_request.raise_for_status()
            
            data_down = http_request.content.decode(http_request.encoding)
            csv_data = pd.read_csv(io.StringIO(data_down))

            electricity_data = csv_data[['Date/Time', 'Electricity:Facility [kW](Hourly)']]

            # Save to persistent object on disk.
            url_split = csv_link.split('/')

            destination_dir = os.path.join(DATA_HOME, 'load', 'residential', url_split[-2])
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, url_split[-1])

            electricity_data.to_csv(destination_file, sep=',', index=False)

            popup = WarningPopup()
            popup.title = 'Success!'
            popup.popup_text.text = 'Load data successfully saved.'
            popup.open()

            logging.info('ResidentialLoadDM: Load data successfully saved.')
    

class LoadTypeRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(LoadTypeRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.load_type_selected = rv.data[self.index]