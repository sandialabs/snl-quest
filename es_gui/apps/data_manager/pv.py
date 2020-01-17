from __future__ import absolute_import

import os
import io
import calendar
import datetime
import logging
import threading
import datetime as dt
import json

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

from es_gui.resources.widgets.common import InputError, WarningPopup, ConnectionErrorPopup, MyPopup, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction, fade_in_animation, DataGovAPIhelp, ParameterRow
from es_gui.apps.data_manager.data_manager import DataManagerException, DATA_HOME
from es_gui.proving_grounds.charts import RateScheduleChart
from es_gui.apps.data_manager.utils import check_connection_settings

MAX_WHILE_ATTEMPTS = 7

URL_PVWATTS = "https://developer.nrel.gov/api/pvwatts/v6.json?"


class PVwattsSearchScreen(Screen):
    """DataManager screen for searching for a PV profile through PVWatts."""
    api_key = StringProperty('')

    def __init__(self, **kwargs):
        super(PVwattsSearchScreen, self).__init__(**kwargs)

        PVWattsSaveNameTextInput.host_screen = self
    
    def on_pre_enter(self):
        if not self.param_widget.children:
            self.param_widget.build()
    
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.set_title('Data Manager: Photovoltaic Power Profiles')

    def open_api_key_help(self):
        """Opens the API key help ModalView."""
        open_ei_help_view = DataGovAPIhelp()
        open_ei_help_view.open()
    
    def reset_screen(self):
        """Resets the screen to its initial state."""
        pass
    
    def _validate_inputs(self):      
        """Validates the search parameters."""  
        # Check if an API key has been provided.
        api_key = self.api_key_input.text

        if not api_key:
            raise (InputError('Please enter an OpenEI API key.'))
        
        pv_params = self.param_widget.get_inputs()

        # Check module and array type spinners.
        module_types = self.module_type_select.values
        array_types = self.array_type_select.values

        try:
            module_ix = module_types.index(self.module_type_select.text)
            pv_params['module_type'] = str(module_ix)
        except ValueError:
            raise(InputError('Please specify a valid module type.'))
        
        try:
            array_ix = array_types.index(self.array_type_select.text)
            pv_params['array_type'] = str(array_ix)
        except ValueError:
            raise(InputError('Please specify a valid array type.'))
       
        return api_key, pv_params

    def get_inputs(self):
        """Retrieves the search inputs and validates them."""
        api_key, pv_params = self._validate_inputs()

        # Fixed values.
        pv_params['dataset'] = 'tmy3'
        pv_params['radius'] = '0'
        pv_params['timeframe'] = 'hourly'
        pv_params['api_key'] = api_key

        if not pv_params.get('tilt', None):
            pv_params['tilt'] = pv_params['lat']

        return api_key, pv_params
    
    def execute_query(self):
        """Executes the PVWatts query using the given parameters."""
        try:
            api_key, pv_params = self.get_inputs()
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

            # Form query.
            api_query = URL_PVWATTS
            query_segs = []
            for k, v in pv_params.items():
                query_segs.append('{key}={value}'.format(key=k, value=v))
            
            api_query += '&'.join(query_segs)
            # print(api_query)
            
            try:
                self._query_api(api_query)
            except requests.ConnectionError:
                popup = ConnectionErrorPopup()
                popup.popup_text.text = 'There was an issue connecting to the API. Check your connection settings and try again.'
                popup.open()

            # thread_query = threading.Thread(target=self._query_api, args=[api_query])
            # thread_query.start()
    
    def _query_api(self, api_query):
        """Uses PVWatts API to query for a PV profile."""
        ssl_verify, proxy_settings = check_connection_settings()

        try:
            with requests.Session() as req:
                http_request = req.get(api_query,
                                        proxies=proxy_settings, 
                                        timeout=10, 
                                        verify=ssl_verify,
                                        stream=True)
                if http_request.status_code != requests.codes.ok:
                    http_request.raise_for_status()
        except requests.HTTPError as e:
            logging.error('PVProfileDM: {0}'.format(repr(e)))
            raise requests.ConnectionError
        except requests.exceptions.ProxyError:
            logging.error('PVProfileDM: Could not connect to proxy.')
            raise requests.ConnectionError
        except requests.ConnectionError as e:
            logging.error('PVProfileDM: Failed to establish a connection to the host server.')
            raise requests.ConnectionError
        except requests.Timeout as e:
            logging.error('PVProfileDM: The connection timed out.')
            raise requests.ConnectionError
        except requests.RequestException as e:
            logging.error('PVProfileDM: {0}'.format(repr(e)))
            raise requests.ConnectionError
        except Exception as e:
            # Something else went wrong.
            logging.error('PVProfileDM: An unexpected error has occurred. ({0})'.format(repr(e)))
            raise requests.ConnectionError
        else:
            request_content = http_request.json()

            if not self.save_name_field.text:
                popup = WarningPopup()
                popup.popup_text.text = 'Please specify a name to save the PV profile as.'
                popup.open()
                return
            else:
                outname = self.save_name_field.text

            # Strip non-alphanumeric chars from given name for filename.
            delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
            outname = outname.translate({ord(i): None for i in delchars})

            # Save.
            destination_dir = os.path.join(DATA_HOME, 'pv')
            os.makedirs(destination_dir, exist_ok=True)
            destination_file = os.path.join(destination_dir, outname + '.json')

            if not os.path.exists(destination_file):
                with open(destination_file, 'w') as outfile:
                    json.dump(request_content, outfile)
                
                logging.info('PVProfileDM: Profile successfully saved.')
                
                popup = WarningPopup()
                popup.title = 'Success!'
                popup.popup_text.text = 'PV profile successfully saved.'
                popup.open()
            else:
                # File already exists with same name.
                popup = WarningPopup()
                popup.popup_text.text = 'A PV profile with the provided name already exists. Please specify a new name.'
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


class PVWattsSaveNameTextInput(TextInput):
    """TextInput field for entering the save name in the PV Profile Data Manager."""
    host_screen = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode

        if key_str in ('enter', 'numpadenter'):
            self.host_screen.execute_query()
        else:
            super(PVWattsSaveNameTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        
        return True


class PVWattsSearchParameterWidget(GridLayout):
    """Grid layout containing rows of parameter adjustment widgets."""
    def build(self):
        # Build the widget by creating a row for each parameter.
        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_pvwatts_search_params()

        for param in MODEL_PARAMS:
            row = ParameterRow(desc=param)

            # if param['attr name'] == 'tilt':
            #     def _match_latitude_to_tilt(instance, value):
            #         row.text_input.hint_text = self.lat.text_input.text
                
            #     self.lat.bind(text_input_text=_match_latitude_to_tilt)

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
