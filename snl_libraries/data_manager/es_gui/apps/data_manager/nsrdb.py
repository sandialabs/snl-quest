from __future__ import absolute_import

import os
import io
import calendar
import datetime
import logging
import threading
import datetime as dt
import json
import subprocess

import requests
import pandas as pd
import numpy as np
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty, DictProperty

import urllib3
urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

from es_gui.resources.widgets.common import InputError, WarningPopup, ConnectionErrorPopup, MyPopup, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction, fade_in_animation, DataGovAPIhelp
from es_gui.apps.data_manager.data_manager import DataManagerException, DATA_HOME
from es_gui.proving_grounds.charts import RateScheduleChart
from es_gui.apps.data_manager.utils import check_connection_settings
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView


MAX_WHILE_ATTEMPTS = 7

URL_NSRDB = 'https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt='

class NSRDBDataScreen(Screen):
    """DataManager screen for searching for a weather file through the national solar radiation database (NSRDB)."""
    api_key = StringProperty('')

    def __init__(self, **kwargs):
        super(NSRDBDataScreen, self).__init__(**kwargs)

        NSRDBSaveNameTextInput.host_screen = self
    
    def on_pre_enter(self):
        """Build parameter widget before entering"""
        if not self.param_widget.children:
            self.param_widget.build()
    
    def on_enter(self):
        """Set title and make sure EnergyPlus is installed"""
        ab = self.manager.nav_bar
        ab.set_title('Data Manager: NSRDB')
        
        self.check_eplus()

    def open_api_key_help(self):
        """Opens the API key help ModalView."""
        open_ei_help_view = DataGovAPIhelp()
        open_ei_help_view.open()
    
    def reset_screen(self):
        """Resets the screen to its initial state."""
        pass
    
    def check_eplus(self):
        """Checks for the energyplus directory"""
        
        if not os.path.isdir(os.path.join("energyplus")):
            help_carousel_view = HelpCarouselModalView()
            help_carousel_view.title.text = "Download EnergyPlus to use this tool"
    
            slide_03_text = "EnergyPlus is a building simulation software used to model energy consumption developed by the Department of Energy Building Technologies Office. To download EnergyPlus, simply navigate to www.energyplus.net/downloads and select the appropriate package." 
            
            slide_04_text = "Once downloaded, move the software to the Quest directory and rename to 'energyplus'. Following these two steps you will be able to download NSRDB data and use the Quest Performance tool."

            slides = [
                (os.path.join("es_gui", "resources", "help_views", "performance", "eplus_download.png"), slide_03_text),
                (os.path.join("es_gui", "resources", "help_views", "performance", "Inkedquest_directory_LI.jpg"), slide_04_text),
            ]
    
            help_carousel_view.add_slides(slides)
            help_carousel_view.open()
    
    def _validate_inputs(self):      
        """Validates the search parameters."""  
        # Check if an API key has been provided.
        api_key = self.api_key_input.text

        if not api_key:
            raise (InputError('Please enter an NSRDB API key.'))
        
        params = self.param_widget.get_inputs()
       
        return api_key, params

    def get_inputs(self):
        """Retrieves the search inputs and validates them."""
        api_key, params = self._validate_inputs()

        params['api_key'] = api_key

        return api_key, params
    
    def execute_query(self):
        """Executes the NSRDB query using the given parameters."""
        try:
            api_key, params = self.get_inputs()
            self.api_key = api_key
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            # Reset screen.
            self.reset_screen()
            self.save_button.disabled = True


            api_query = URL_NSRDB
            query_segs=[]
            for k,v in params.items():
                if not k in ['lat','lon','loc']:
                    query_segs.append('{key}={value}'.format(key=k,value=v))
            
            api_query += 'POINT({lon}%20{lat})&interval=60&'.format(lat=params['lat'],lon=params['lon'])
            api_query += '&'.join(query_segs)
            
            destination_dir = os.path.join(DATA_HOME, 'weather',params['loc'])

            try:
                self._query_api(api_query,destination_dir)
            except requests.ConnectionError:
                popup = ConnectionErrorPopup()
                popup.popup_text.text = 'There was an issue connecting to the API. Check your connection settings and try again.'
                popup.open()
            
    
    def _query_api(self, api_query, destination_dir):
        """Uses NSRDB API to query for a weather file."""
        ssl_verify, proxy_settings = check_connection_settings()

        try:
            with requests.Session() as req:
                http_request = req.get(api_query,
                                        proxies=proxy_settings, 
                                        timeout=100, 
                                        verify=ssl_verify,
                                        stream=True)
                if http_request.status_code != requests.codes.ok:
                    http_request.raise_for_status()
        except requests.HTTPError as e:
            logging.error('NSRDBDM: {0}'.format(repr(e)))
            
            raise requests.ConnectionError
        except requests.exceptions.ProxyError:
            logging.error('NSRDBDM: Could not connect to proxy.')
            raise requests.ConnectionError
        except requests.ConnectionError as e:
            logging.error('NSRDBDM: Failed to establish a connection to the host server. {}'.format(repr(e)))
            raise requests.ConnectionError
        except requests.Timeout as e:
            logging.error('NSRDBDM: The connection timed out.')
            raise requests.ConnectionError
        except requests.RequestException as e:
            logging.error('NSRDBDM: {0}'.format(repr(e)))
            raise requests.ConnectionError
        except Exception as e:
            # Something else went wrong.
            logging.error('NSRDBDM: An unexpected error has occurred. ({0})'.format(repr(e)))
            raise requests.ConnectionError
        else:
            info = pd.read_csv(api_query, nrows = 1)
            dataF = pd.read_csv(api_query, skiprows = 2)
            
            if not self.save_name_field.text:
                popup = WarningPopup()
                popup.popup_text.text = 'Please specify a name to save the weather file as.'
                popup.open()
                return
            else:
                outname = self.save_name_field.text

            # Strip non-alphanumeric chars from given name for filename.
            delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
            outname = outname.translate({ord(i): None for i in delchars})

            # Save
            cwd=os.getcwd()
            try:
                weather_converter=os.path.join(cwd,'energyplus','PreProcess','WeatherConverter','Weather.exe')
            except FileNotFoundError:
                popup = WarningPopup()
                popup.popup_text.text = "EnergyPlus weather converter not found. Please visit the help tab for more information on installing and downloading EnergyPlus on your machine."
                popup.open()
                return
            else:
                os.makedirs(destination_dir, exist_ok=True)
                file_info = os.path.join(destination_dir,outname + '_info')
                file_data = os.path.join(destination_dir,outname + '_data')
                destination_file_info = file_info + '.csv'
                destination_file_data = file_data + '.csv'
                self.create_location_files(file_data,info)

            if not os.path.exists(destination_file_data):
                info.to_csv(destination_file_info,index=False)
                dataF.to_csv(destination_file_data,index=False)
                
                subprocess.run(weather_converter)
#                print(os.getcwd())
                
                logging.info('NSRDBDM: Profile successfully saved.')
                
                popup = WarningPopup()
                popup.title = 'Success!'
                popup.popup_text.text = 'Weather file successfully saved.'
                popup.open()
            else:
                # File already exists with same name.
                popup = WarningPopup()
                popup.popup_text.text = 'A weather file with the provided name already exists. Please specify a new name.'
                popup.open()
        finally:
            self.save_button.disabled = False
    
    def get_selections(self):
        """Retrieves UI selections."""
        if not self.utility_selected:
            raise(InputError('Please select a utility before proceeding.'))
        
        if not self.rate_structure_selected:
            raise(InputError('Please select a rate structure before proceeding.'))

        return self.utility_selected, self.rate_structure_selected
    
    def create_location_files(self, path, info,city='',state='',country='',wmo = ''):
        """Creates the .def file needed for the Energyplus converter"""
        
        loc_id = info['Location ID']
        file_def = path + '.def'
        
        f = open(file_def, 'w')
        
        f.write('&location\n')
        f.write('City = \'{}\'\n'.format(city))
        f.write('StateProv = \'{}\'\n'.format(state))
        f.write('Country = \'{}\'\n'.format(country))
        f.write('InWMO = {}\n'.format(wmo))
        f.write('InLat = {}\n'.format(info['Latitude'][0]))
        f.write('InLong = {}\n'.format(info['Longitude'][0]))
        f.write('InElev = {}\n'.format(info['Elevation'][0]))
        f.write('InTime = {}\n'.format(info['Time Zone'][0]))
        f.write('/\n')
        f.write('&miscdata\n')
        f.write('Comments1 = \'No comment\'\n')
        f.write('Comments2 = \'No comment\'\n')
        f.write('SourceData = \'NSRDB\'\n')
        f.write('/\n')
        f.write('&wthdata\n')
        f.write('InputFileType = \'Custom\'\n')
        f.write('InFormat = \'DELIMITED\'\n')
        f.write('NumInHour = 1\n')
        f.write('''DataElements = Year,Month,Day,Hour,Minute,Drybulb,Ignore,Ignore,Ignore,Ignore,dewpoint
                ,difhorrad,dirnorrad,Ignore,glohorrad,relhum,Ignore,Albedo,atmos_pressure,
                precipitable_water,winddir,windspd\n''')
        f.write('''DataUnits = x,x,x,x,x,C,x,x,x,x,C,Wh/m2,Wh/m2,x,Wh/m2,%,x,x,mbar,mm,degrees,m/s\n''')
        f.write('''DataConversionFactors = 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,100,1,1,1\n''')
        f.write('DelimiterChar=\',\'\n')
        f.write('/\n')
        f.write('&datacontrol\n')
        f.write('NumRecordsToSkip = 1\n')
        f.write('MaxNumRecordsToRead = 8760\n')
        f.write('/\n')
        
        f.close()
        
        return


class NSRDBSaveNameTextInput(TextInput):
    """TextInput field for entering the save name in the PV Profile Data Manager."""
    host_screen = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode

        if key_str in ('enter', 'numpadenter'):
            self.host_screen.execute_query()
        else:
            super(NSRDBSaveNameTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        
        return True


class NSRDBParameterWidget(GridLayout):
    """Grid layout containing rows of parameter adjustment widgets."""
    def build(self):
        # Build the widget by creating a row for each parameter.
        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_nsrdb_search_params()

        for param in MODEL_PARAMS:
            if param['attr name'] in ['lat','long','interval']:
                row = ParameterRowNSRDB(desc=param)
            else:
                row = ParameterRowTextNSRDB(desc=param)

            self.add_widget(row)
            setattr(self, param['attr name'], row)
    
    def _validate_inputs(self):
        param_set = {}

        for row in self.children:
            attr_name = row.desc['attr name']

            if not row.text_input.text:
                attr_val = row.text_input.hint_text
            else:
                attr_val = row.text_input.text
            
            if attr_val:
                param_set[attr_name] = attr_val
            else:
                # Skip if values is None.
                continue

        return param_set
    
    def get_inputs(self):
        try:
            params = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return params
        
class ParameterRowNSRDB(GridLayout):
    """Grid layout containing parameter name, description, text input, and units."""
    def __init__(self, desc, **kwargs):
        super(ParameterRowNSRDB, self).__init__(**kwargs)

        self._desc = desc

        self.name.text = self.desc.get('name', '')
        self.notes.text = self.desc.get('notes', '')
        self.text_input.hint_text = str(self.desc.get('default', ''))
#        self.units.text = self.desc.get('units', '')

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value


class ParamTextInputNSRDB(TextInput):
    """A TextInput field for entering parameter values. Limited to float values."""
    def insert_text(self, substring, from_undo=False):
        # limit to 8 chars
        substring = substring[:8 - len(self.text)]
        return super(ParamTextInputNSRDB, self).insert_text(substring, from_undo=from_undo)
    
class ParameterRowTextNSRDB(GridLayout):
    """Grid layout containing parameter name, description, text input, and units."""
    def __init__(self, desc, **kwargs):
        super(ParameterRowTextNSRDB, self).__init__(**kwargs)

        self._desc = desc

        self.name.text = self.desc.get('name', '')
        self.notes.text = self.desc.get('notes', '')
        self.text_input.hint_text = str(self.desc.get('default', ''))
#        self.units.text = self.desc.get('units', '')

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value


class ParamTextInputTextNSRDB(TextInput):
    """A TextInput field for entering parameter values. Limited to float values."""
    def insert_text(self, substring, from_undo=False):
        # limit to 25 chars
        substring = substring[:25 - len(self.text)]
        return super(ParamTextInputTextNSRDB, self).insert_text(substring, from_undo=from_undo)
