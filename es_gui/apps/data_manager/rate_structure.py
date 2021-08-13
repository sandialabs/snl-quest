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
from kivy.core.window import Window
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

from es_gui.resources.widgets.common import BodyTextBase, InputError, WarningPopup, ConnectionErrorPopup, MyPopup, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction, fade_in_animation, DataGovAPIhelp
from es_gui.apps.data_manager.data_manager import DataManagerException, DATA_HOME, STATE_ABBR_TO_NAME
from es_gui.proving_grounds.charts import RateScheduleChart
from es_gui.apps.data_manager.utils import check_connection_settings


MAX_WHILE_ATTEMPTS = 7

URL_OPENEI_IOU = "https://data.openei.org/files/4042/iou_zipcodes_2019.csv"
URL_OPENEI_NONIOU = "https://data.openei.org/files/4042/non_iou_zipcodes_2019.csv"
APIROOT_OPENEI = "https://api.openei.org/utility_rates?"
VERSION_OPENEI = "version=latest"
REQUEST_FMT_OPENEI = "&format=json"
DETAIL_OPENEI = "&detail=full"


class RateStructureDataScreen(Screen):
    """"""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.set_title('Data Manager: Utility Rate Structure Data')


class RateStructureScreenManager(ScreenManager):
    """The screen manager for the Data Manager Rate Structure Data screens."""
    def __init__(self, **kwargs):
        super(RateStructureScreenManager, self).__init__(**kwargs)

        self.transition = SlideTransition()
        self.add_widget(RateStructureUtilitySearchScreen(name='start'))
        self.add_widget(RateStructureEnergyRateStructureScreen(name='energy_rate_structure'))
        self.add_widget(RateStructureDemandRateStructureScreen(name='demand_rate_structure'))
        self.add_widget(RateStructureFinishScreen(name='finish'))
    
    def go_to_data_manager_home(self):
        """Sets the current screen to Data Manager Home."""
        ab = self.parent.parent.parent.manager.nav_bar
        ab.go_to_screen('data_manager_home')


class RateStructureUtilitySearchTextInput(TextInput):
    host_screen = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode

        if key_str in ('enter', 'numpadenter'):
            self.host_screen.execute_search()
        else:
            super(RateStructureUtilitySearchTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        
        return True


class RateStructureUtilitySearchScreen(Screen):
    """DataManager Rate Structure screen for searching for a utility rate structure."""
    utility_ref_table = pd.DataFrame()
    utility_selected = DictProperty()
    rate_structure_selected = DictProperty()
    api_key = StringProperty('')

    def __init__(self, **kwargs):
        super(RateStructureUtilitySearchScreen, self).__init__(**kwargs)

        UtilitySearchRVEntry.host_screen = self
        RateStructureRVEntry.host_screen = self
        RateStructureUtilitySearchTextInput.host_screen = self

    def open_api_key_help(self):
        """Opens the API key help ModalView."""
        open_ei_help_view = DataGovAPIhelp()
        open_ei_help_view.open()
    
    def reset_screen(self):
        """Resets the screen to its initial state."""
        self.utility_select_bx.opacity = 0.05
        self.rate_structure_select_bx.opacity = 0.05

        # Deselects all RV selections.
        self.utility_rv.deselect_all_nodes()
        self.rate_structure_rv.deselect_all_nodes()

        # Clear all RV data.
        self.utility_rv.data = []
        self.rate_structure_rv.data = []

        # Clears all RV text filters.
        self.rate_structure_rv_text_filter.text = ''
        self.utility_rv_text_filter.text = ''

        # Resets properties.
        self.rate_structure_desc.text = ''
        self.utility_selected = {}
        self.rate_structure_selected = {}

        # Focus text input.
        self.search_text_input.focus = True
    
    def _download_utility_ref_table(self):
        """Downloads and builds the utility reference table from OpenEI."""
        ssl_verify, proxy_settings = check_connection_settings()

        # Invester-owned utilities.
        attempt_download = True
        n_tries = 0

        while attempt_download:
            n_tries += 1

            if n_tries >= MAX_WHILE_ATTEMPTS:
                logging.warning('RateStructureDM: Hit download retry limit.')
                attempt_download = False
                break
            
            if App.get_running_app().root.stop.is_set():
                return

            try:
                with requests.Session() as req:
                    http_request = req.get(URL_OPENEI_IOU,
                                            proxies=proxy_settings, 
                                            timeout=6, 
                                            verify=ssl_verify,
                                            stream=True)
                    if http_request.status_code != requests.codes.ok:
                        http_request.raise_for_status()
                    else:
                        attempt_download = False
            except requests.HTTPError as e:
                logging.error('RateStructureDM: {0}'.format(repr(e)))
            except requests.exceptions.ProxyError:
                logging.error('RateStructureDM: Could not connect to proxy.')
            except requests.ConnectionError as e:
                logging.error('RateStructureDM: Failed to establish a connection to the host server.')
            except requests.Timeout as e:
                logging.error('RateStructureDM: The connection timed out.')
            except requests.RequestException as e:
                logging.error('RateStructureDM: {0}'.format(repr(e)))
            except Exception as e:
                # Something else went wrong.
                logging.error('RateStructureDM: An unexpected error has occurred. ({0})'.format(repr(e)))
            else:
                data_down = http_request.content.decode(http_request.apparent_encoding)
                data_iou = pd.read_csv(io.StringIO(data_down))
        
        # Non-investor-owned utilities.
        attempt_download = True
        n_tries = 0

        while attempt_download:
            n_tries += 1

            if n_tries >= MAX_WHILE_ATTEMPTS:
                logging.warning('RateStructureDM: Hit download retry limit.')
                attempt_download = False
                break
            
            if App.get_running_app().root.stop.is_set():
                return
        
            try:
                with requests.Session() as req:
                    http_request = req.get(URL_OPENEI_NONIOU,
                                            proxies=proxy_settings, 
                                            timeout=6, 
                                            verify=ssl_verify,
                                            stream=True)
                    if http_request.status_code != requests.codes.ok:
                        http_request.raise_for_status()
                    else:
                        attempt_download = False
            except requests.HTTPError as e:
                logging.error('RateStructureDM: {0}'.format(repr(e)))
            except requests.exceptions.ProxyError:
                logging.error('RateStructureDM: Could not connect to proxy.')
            except requests.ConnectionError as e:
                logging.error('RateStructureDM: Failed to establish a connection to the host server.')
            except requests.Timeout as e:
                logging.error('RateStructureDM: The connection timed out.')
            except requests.RequestException as e:
                logging.error('RateStructureDM: {0}'.format(repr(e)))
            except Exception as e:
                # Something else went wrong.
                logging.error('RateStructureDM: An unexpected error has occurred. ({0})'.format(repr(e)))
            else:
                data_down = http_request.content.decode(http_request.apparent_encoding)
                data_noniou = pd.read_csv(io.StringIO(data_down))
            
            try:
                df_combined = pd.concat([data_iou, data_noniou], ignore_index=True)
            except NameError:
                # Connection error prevented downloads.
                raise requests.ConnectionError
            else:
                # Add column for state/district name.
                df_combined['state name'] = df_combined['state'].apply(lambda state_abbr: STATE_ABBR_TO_NAME.get(state_abbr, ''))

                self.utility_ref_table = df_combined
                logging.info('RateStructureDM: Retrieved list of all utilities.')

    def _validate_inputs(self):      
        """Validates the search parameters."""  
        # Check if an API key has been provided.
        api_key = self.api_key_input.text

        if not api_key:
            raise (InputError('Please enter an OpenEI API key.'))
        
        # Check if a search string has been provided.
        search_query = self.search_text_input.text

        if not search_query:
            raise (InputError('Please enter a search query.'))

        # Check if a search type has been specified.
        if self.by_name_toggle.state == 'down':
            search_type = 'utility_name'
        elif self.by_zip_toggle.state == 'down':
            search_type = 'zip'
        elif self.by_state_toggle.state == 'down':
            search_type = 'state'
        else:
            raise(InputError('Please select a search type. (by name, by zip, or by state)'))
        
        return api_key, search_query, search_type

    def get_inputs(self):
        """Retrieves the search inputs and validates them."""
        api_key, search_query, search_type = self._validate_inputs()

        if search_type == 'zip':
            try:
                search_query = int(search_query)
            except ValueError:
                raise(InputError('When searching by zip, please provide a five digit numeric search query. (got "{0}")'.format(search_query)))
        else:
            search_query = search_query.lower()

        return api_key, search_query, search_type
    
    def execute_search(self):
        """Executes the utility search using the given parameters."""
        try:
            api_key, search_query, search_type = self.get_inputs()
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
            self.search_button.disabled = True

            def _execute_search():
                # Open loading screen.
                # self.loading_screen = LoadingModalView()
                # self.loading_screen.loading_text.text = 'Retrieving rate structures...'
                # self.loading_screen.open()

                if self.utility_ref_table.empty:
                    try:
                        self._download_utility_ref_table()
                    except requests.ConnectionError:
                        popup = ConnectionErrorPopup()
                        popup.popup_text.text = 'There was an issue connecting to and downloading the lists of utilities. Check your connection settings and try again.'
                        popup.open()
                        return
                    finally:
                        self.search_button.disabled = False
                
                # Filter DataFrame by search type/query and drop duplicate entries.
                if search_type == 'state':
                    utility_data_filtered = self.utility_ref_table.loc[self.utility_ref_table['state'].str.lower().str.contains(search_query)
                    | self.utility_ref_table['state name'].str.lower().str.contains(search_query)]
                elif search_type == 'zip':
                    utility_data_filtered = self.utility_ref_table.loc[self.utility_ref_table[search_type] == search_query]
                else:
                    utility_data_filtered = self.utility_ref_table.loc[self.utility_ref_table[search_type].str.lower().str.contains(search_query)]                    
                
                utility_data_filtered = utility_data_filtered[['eiaid', 'utility_name', 'state', 'ownership']]
                utility_data_filtered.drop_duplicates(inplace=True)

                logging.info('RateStructureDM: Utility table filter completed.')
                self.search_button.disabled = False

                if utility_data_filtered.empty:
                    logging.warning('RateStructureDM: No results matched the query.')

                    popup = WarningPopup()
                    popup.popup_text.text = 'No results matched your query.'
                    popup.open()

                # Enable search results selector.
                fade_in_animation(self.utility_select_bx)
                self._populate_utility_selector(utility_data_filtered)

                # Animation.stop_all(self.loading_screen.logo, 'opacity')
                # self.loading_screen.dismiss()

            thread_query = threading.Thread(target=_execute_search)
            thread_query.start()
    
    def _populate_utility_selector(self, df):
        """Generates utility RecycleView based on search results."""
        records = df.to_dict(orient='records')
        records = [{'name': record['utility_name'], 'record': record} for record in records]

        records = sorted(records, key=lambda t: t['name'])

        self.utility_rv.data = records
        self.utility_rv.unfiltered_data = records
    
    def on_utility_selected(self, instance, value):
        try:
            logging.info('RateStructureDM: Utility selection changed to {0}.'.format(value['utility_name']))
        except KeyError:
            logging.info('RateStructureDM: Utility selection reset.')
        else:
            eiaid = str(value['eiaid'])

            self.rate_structure_desc.text = ''
            self.rate_structure_rv.deselect_all_nodes()
            self.rate_structure_rv_text_filter.text = ''
            self.rate_structure_selected = {}

            # Get utility schedules.
            self._populate_utility_rate_structures(eiaid)
            
    def _populate_utility_rate_structures(self, eia_id):
        """Executes OpenEI API query for given EIA ID."""
        api_root = APIROOT_OPENEI + VERSION_OPENEI + REQUEST_FMT_OPENEI + DETAIL_OPENEI
        api_query = api_root + '&api_key=' + self.api_key + '&eia=' + eia_id

        try:
            thread_query = threading.Thread(target=self._query_api_for_rate_structures, args=[api_query])
            thread_query.start()
        except requests.ConnectionError:
            popup = ConnectionErrorPopup()
            popup.popup_text.text = 'There was an issue querying the OpenEI database. Check your connection settings and try again.'
            popup.open()
        finally:
            self.search_button.disabled = False

        # thread_query = threading.Thread(target=self._query_api_for_rate_structures, args=[api_query])
        # thread_query.start()

        # Open loading screen.
        self.loading_screen = LoadingModalView()
        self.loading_screen.loading_text.text = 'Retrieving rate structures...'
        self.loading_screen.open()
    
    def _query_api_for_rate_structures(self, api_query):
        """Uses OpenEI API to query the rate structures for given EIA ID and populates rate structure RecycleView."""
        ssl_verify, proxy_settings = check_connection_settings()

        attempt_download = True
        n_tries = 0

        while attempt_download:
            n_tries += 1
            
            if n_tries >= MAX_WHILE_ATTEMPTS:
                logging.warning('RateStructureDM: Hit download retry limit.')
                attempt_download = False
                break
            
            if App.get_running_app().root.stop.is_set():
                return

            try:
                with requests.Session() as req:
                    http_request = req.get(api_query,
                                            proxies=proxy_settings, 
                                            timeout=10, 
                                            verify=ssl_verify,
                                            stream=True)
                    if http_request.status_code != requests.codes.ok:
                        http_request.raise_for_status()
                    else:
                        attempt_download = False
            except requests.HTTPError as e:
                logging.error('RateStructureDM: {0}'.format(repr(e)))
                raise requests.ConnectionError
            except requests.exceptions.ProxyError:
                logging.error('RateStructureDM: Could not connect to proxy.')
                raise requests.ConnectionError
            except requests.ConnectionError as e:
                logging.error('RateStructureDM: Failed to establish a connection to the host server.')
                raise requests.ConnectionError
            except requests.Timeout as e:
                logging.error('RateStructureDM: The connection timed out.')
                raise requests.ConnectionError
            except requests.RequestException as e:
                logging.error('RateStructureDM: {0}'.format(repr(e)))
                raise requests.ConnectionError
            except Exception as e:
                # Something else went wrong.
                logging.error('RateStructureDM: An unexpected error has occurred. ({0})'.format(repr(e)))
                raise requests.ConnectionError
            else:
                structure_list = http_request.json()['items']

                structure_df = pd.DataFrame.from_records(structure_list)
                structure_df.dropna(subset=['energyratestructure'], inplace=True)

                # Filter out entries whose energyratestructure array does not contain "rate" terms.
                mask = structure_df['energyratestructure'].apply(lambda x: all(['rate' in hr.keys() for row in x for hr in row]))
                structure_df = structure_df[mask]

                structure_list = structure_df.to_dict(orient='records')

                # First, sort by effective date.
                # structure_list = sorted(structure_list, key=lambda x: (x['name'], x.get('startdate', np.nan)))
                structure_list = sorted(structure_list, key=lambda x: x.get('startdate', np.nan), reverse=True)

                # Then, sort by name.
                structure_list = sorted(structure_list, key=lambda x: x['name'])                

                # Display name: Name (record['startdate']).
                effective_dates = ['(Effective Date : {0})'.format(dt.datetime.fromtimestamp(record['startdate']).strftime('%m/%d/%Y')) if not np.isnan(record['startdate']) else '' for record in structure_list]

                records = [{'name': record['name'] + ' ' + effective_dates[ix] , 'record': record} 
                for ix, record in enumerate(structure_list, start=0)]
                # records = sorted(records, key=lambda t: t['name'])

                self.rate_structure_rv.data = records
                self.rate_structure_rv.unfiltered_data = records

                logging.info('RateStructureDM: Retrieved utility rate structures.')
                fade_in_animation(self.rate_structure_select_bx)
            finally:
                self.loading_screen.dismiss()
    
    def on_rate_structure_selected(self, instance, value):
        try:
            logging.info('RateStructureDM: Rate structure selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('RateStructureDM: Rate structure selection reset.')
            self.rate_structure_desc.text = ''
        else:
            self.manager.get_screen('energy_rate_structure').populate_rate_schedules(value)
            self.manager.get_screen('demand_rate_structure').populate_rate_schedules(value)
            self.manager.get_screen('finish').populate_peak_demand_limits(value)
        
        try:
            # print(value)
            self.rate_structure_desc.text = value.get('description', 'No description provided.')
        except ValueError:
            pass
    
    def get_selections(self):
        """Retrieves UI selections."""
        if not self.utility_selected:
            raise(InputError('Please select a utility before proceeding.'))
        
        if not self.rate_structure_selected:
            raise(InputError('Please select a rate structure before proceeding.'))

        return self.utility_selected, self.rate_structure_selected
    
    def next_screen(self):
        try:
            self.get_selections()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.manager.current = self.manager.next()


class UtilitySearchRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(UtilitySearchRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.utility_selected = rv.data[self.index]['record']


class RateStructureRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(RateStructureRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.rate_structure_selected = rv.data[self.index]['record']


class RateStructureEnergyRateStructureScreen(Screen):
    """DataManager Rate Structure screen for viewing and modifying a utility rate structure."""
    rate_structure = DictProperty()

    def populate_rate_schedules(self, rate_structure):
        """Fills in the rate/tier table and energy rate schedule based on selected rate structure."""
        self.rate_structure_period_table.reset_table()

        self.rate_structure = rate_structure

        # Get the energy rate structure.
        energy_rate_structure = rate_structure.get('energyratestructure', [])

        # Populates the period/rate table.
        for ix, energy_rate in enumerate(energy_rate_structure, start=0):
            try:
                rate = str(energy_rate[0]['rate'])
            except KeyError:
                logging.warning('RateStructureDM: No rate value found in energy rate structure.')

            period = str(ix)
            rate = str(energy_rate[0].get('rate', 0))

            row = RateStructureTableRow(desc={'period': period, 'rate': rate})
            self.rate_structure_period_table.period_rows.append(row)
            self.rate_structure_period_table.add_widget(row)

        # self.generate_schedule_charts()
        self.generate_schedule_tables()
    
    def generate_schedule_tables(self, *args):
        """Populates the weekday and weekend rate schedule tables."""
        weekday_schedule_data = self.rate_structure['energyweekdayschedule']
        weekend_schedule_data = self.rate_structure['energyweekendschedule']

        # Weekday chart.
        for ix, month_row in enumerate(self.weekday_chart.schedule_rows, start=0):
            for iy, text_input in enumerate(month_row.text_inputs, start=0):
                text_input.text = str(weekday_schedule_data[ix][iy])
        
        # Weekend chart.
        for ix, month_row in enumerate(self.weekend_chart.schedule_rows, start=0):
            for iy, text_input in enumerate(month_row.text_inputs, start=0):
                text_input.text = str(weekend_schedule_data[ix][iy])
        
    def generate_schedule_charts(self, *args):
        """Draws the weekday and weekend rate schedule charts."""
        weekday_schedule_data = self.rate_structure.get('energyweekdayschedule', [])
        weekend_schedule_data = self.rate_structure.get('energyweekendschedule', [])

        if weekday_schedule_data and weekend_schedule_data:
            n_tiers = len(np.unique(weekday_schedule_data))

            # Select chart colors.
            palette = [rgba_to_fraction(color) for color in PALETTE][:n_tiers]
            labels = calendar.month_abbr[1:]

            # Draw charts.
            self.weekday_chart.draw_chart(np.array(weekday_schedule_data), palette, labels)
            self.weekend_chart.draw_chart(np.array(weekend_schedule_data), palette, labels)
    
    def _validate_inputs(self):
        weekday_schedule = self.weekday_chart.get_schedule()
        weekend_schedule = self.weekend_chart.get_schedule()

        # Get period/rates from table.
        rates_dict = self.rate_structure_period_table.get_rates()
        periods = set([int(period) for period in rates_dict.keys()])

        # Determine if any values in schedule are not in period list.
        weekday_periods = set(np.unique(weekday_schedule))
        weekend_periods = set(np.unique(weekend_schedule))

        if not weekday_periods.issubset(periods):
            set_diff = ', '.join(['{:d}'.format(int(x)) for x in sorted(weekday_periods.difference(periods))])

            raise(InputError('Impermissible entries ({0}) in the Weekday Rate Schedule found.'.format(set_diff)))

        if not weekend_periods.issubset(periods):
            set_diff = ', '.join(['{:d}'.format(int(x)) for x in sorted(weekend_periods.difference(periods))])

            raise(InputError('Impermissible entries ({0}) in the Weekend Rate Schedule found.'.format(set_diff)))
        
        return weekday_schedule, weekend_schedule, rates_dict
    
    def get_selections(self):
        """Retrieves UI selections."""
        try:
            weekday_schedule, weekend_schedule, rates_dict = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return weekday_schedule.tolist(), weekend_schedule.tolist(), rates_dict

    def next_screen(self):
        """Check if all input data is valid before proceeding to the next demand rate structure screen."""
        try:
            self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.manager.current = self.manager.next()
    
    def on_enter(self):
        pass
        # self.generate_schedule_charts()

    def on_leave(self):
        pass
        # self.weekday_chart.clear_widgets()
        # self.weekend_chart.clear_widgets()


class RateStructureDemandRateStructureScreen(Screen):
    """DataManager Rate Structure screen for viewing and modifying a utility rate structure."""
    rate_structure = DictProperty()

    def populate_rate_schedules(self, rate_structure):
        """Fills in the rate/tier table and energy rate schedule based on selected rate structure."""
        self.flat_period_table.reset_table()
        self.tou_period_table.reset_table()

        self.rate_structure = rate_structure

        # Get the demand rate structures.
        flat_demand_months = rate_structure.get('flatdemandmonths', [0 for x in range(12)])
        flat_demand_rates = rate_structure.get('flatdemandstructure', [[{'rate': 0}]])
        tou_demand_rates = rate_structure.get('demandratestructure', [[{'rate': 0}]])

        # Sometimes rather than being empty, a nan is in the field.
        if type(flat_demand_rates) == float:
            flat_demand_rates = [[{'rate': 0}]]
        
        if type(flat_demand_months) == float:
            flat_demand_months = [0 for x in range(12)]
        
        if type(tou_demand_rates) == float:
            tou_demand_rates = [[{'rate': 0}]]

        # Populate the period/rate tables.
        # Flat demand rate by month.
        for ix, period in enumerate(flat_demand_months, start=0):
            try:
                rate = str(flat_demand_rates[period][0].get('rate', 0))
            except AttributeError:
                rate = str(0)

            row = RateStructureTableRow(desc={'period': calendar.month_abbr[ix+1], 'rate': rate})
            self.flat_period_table.period_rows.append(row)
            self.flat_period_table.add_widget(row)
        
        # Time-of-use demand rate per period.
        for ix, demand_rate in enumerate(tou_demand_rates, start=0):
            try:
                rate = str(demand_rate[0]['rate'])
            except KeyError:
                logging.warning('RateStructureDM: No rate value found in TOU demand rate structure.')

            period = str(ix)
            rate = str(demand_rate[0].get('rate', 0))

            row = RateStructureTableRow(desc={'period': period, 'rate': rate})
            self.tou_period_table.period_rows.append(row)
            self.tou_period_table.add_widget(row)

        # self.generate_schedule_charts()
        self.generate_schedule_tables()
    
    def generate_schedule_tables(self, *args):
        """Populates the weekday and weekend rate schedule tables."""
        try:
            weekday_schedule_data = self.rate_structure['demandweekdayschedule']
            weekend_schedule_data = self.rate_structure['demandweekendschedule']
        except KeyError:
            # No demand rate schedules provided.
            logging.warning('RateStructureDM: No demand rate schedules provided, setting to flat schedule...')

            weekday_schedule_data = np.zeros(shape=(12, 24), dtype=int)
            weekend_schedule_data = np.zeros(shape=(12, 24), dtype=int)
        else:
            # Sometimes rather than being empty, a nan is in the field.
            if type(weekday_schedule_data) == float:
                logging.warning('RateStructureDM: No demand rate schedules provided, setting to flat schedule...')
                weekday_schedule_data = np.zeros(shape=(12, 24), dtype=int)
            if type(weekend_schedule_data) == float:
                logging.warning('RateStructureDM: No demand rate schedules provided, setting to flat schedule...')
                weekend_schedule_data = np.zeros(shape=(12, 24), dtype=int)

        # print(self.rate_structure)

        # Weekday chart.
        for ix, month_row in enumerate(self.weekday_chart.schedule_rows, start=0):
            for iy, text_input in enumerate(month_row.text_inputs, start=0):
                text_input.text = str(weekday_schedule_data[ix][iy])
        
        # Weekend chart.
        for ix, month_row in enumerate(self.weekend_chart.schedule_rows, start=0):
            for iy, text_input in enumerate(month_row.text_inputs, start=0):
                text_input.text = str(weekend_schedule_data[ix][iy])
    
    def _validate_inputs(self):
        weekday_schedule = self.weekday_chart.get_schedule()
        weekend_schedule = self.weekend_chart.get_schedule()

        # Get period/rates from table.
        tou_rates_dict = self.tou_period_table.get_rates()
        periods = set([int(period) for period in tou_rates_dict.keys()])

        # Determine if any values in schedule are not in period list.
        weekday_periods = set(np.unique(weekday_schedule))
        weekend_periods = set(np.unique(weekend_schedule))

        if not weekday_periods.issubset(periods):
            set_diff = ', '.join(['{:d}'.format(int(x)) for x in sorted(weekday_periods.difference(periods))])

            raise(InputError('Impermissible entries ({0}) in the Weekday Rate Schedule found.'.format(set_diff)))

        if not weekend_periods.issubset(periods):
            set_diff = ', '.join(['{:d}'.format(int(x)) for x in sorted(weekend_periods.difference(periods))])

            raise(InputError('Impermissible entries ({0}) in the Weekend Rate Schedule found.'.format(set_diff)))
        
        flat_rates_dict = self.flat_period_table.get_rates()
        
        return weekday_schedule, weekend_schedule, tou_rates_dict, flat_rates_dict
    
    def get_selections(self):
        """Retrieves UI selections."""
        try:
            weekday_schedule, weekend_schedule, tou_rates_dict, flat_rates_dict = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return weekday_schedule.tolist(), weekend_schedule.tolist(), tou_rates_dict, flat_rates_dict

    def next_screen(self):
        """Check if all input data is valid before proceeding to the net metering screen."""
        try:
            self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.manager.current = self.manager.next()


class RateStructureFinishScreen(Screen):
    """DataManager Rate Structure screen for finalizing inputs and saving the rate structure."""
    def __init__(self, **kwargs):
        super(RateStructureFinishScreen, self).__init__(**kwargs)

        RateStructureSaveNameTextInput.host_screen = self

    def populate_peak_demand_limits(self, rate_structure):
        """Fills in the values for peak demand minimum and maximum, if available."""
        peak_minimum = rate_structure.get('peakkwcapacitymin', 0)
        peak_maximum = rate_structure.get('peakkwcapacitymax', np.nan)

        if np.isnan(peak_minimum):
            self.peak_kw_min_field.text = '0'
        else:
            self.peak_kw_min_field.text = str(int(peak_minimum))

        
        if np.isnan(peak_maximum):
            self.peak_kw_max_field.text = ''
        else:
            self.peak_kw_max_field.text = str(int(peak_maximum))

    def _validate_inputs(self):
        if not self.peak_kw_min_field.text:
            raise(InputError('The peak demand minimum must be specified. If there is no minimum, please set it to 0.'))
        else:
            peak_kw_min = int(self.peak_kw_min_field.text)
        
        if self.peak_kw_max_field.text:
            if peak_kw_min > int(self.peak_kw_max_field.text):
                raise(InputError('The peak demand minimum must be less than the maximum.'))
            else:
                peak_kw_max = int(self.peak_kw_max_field.text)
        else:
            peak_kw_max = np.inf
        
        if not any([self.net_metering_1_toggle.state == 'down', self.net_metering_2_toggle.state == 'down']):
            raise(InputError('Please specify a net energy metering type.'))
        else:
            net_metering_type = self.net_metering_2_toggle.state == 'down'
        
        if self.net_metering_1_toggle.state == 'down' and not self.net_metering_sell_price_field.text:
            raise(InputError('Please specify an energy sell price when selecting "Net metering 1.0."'))
        else:
            sell_price = float(self.net_metering_sell_price_field.text) if self.net_metering_1_toggle.state == 'down' else None        

        return peak_kw_min, peak_kw_max, net_metering_type, sell_price
    
    def get_selections(self):
        """Retrieves UI selections."""
        try:
            peak_kw_min, peak_kw_max, net_metering_type, sell_price = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return peak_kw_min, peak_kw_max, net_metering_type, sell_price

    def save_rate_structure(self):
        """Saves the rate structure details to an object on disk."""
        # Retrieve selections from other screens.
        utility_search_screen = self.manager.get_screen('start')
        utility_selected, rate_structure_selected = utility_search_screen.get_selections()

        energy_rate_screen = self.manager.get_screen('energy_rate_structure')
        energy_weekday_schedule, energy_weekend_schedule, energy_rates_dict = energy_rate_screen.get_selections()

        demand_rate_screen = self.manager.get_screen('demand_rate_structure')
        demand_weekday_schedule, demand_weekend_schedule, demand_tou_rates_dict, demand_flat_rates_dict = demand_rate_screen.get_selections()

        try:
            peak_kw_min, peak_kw_max, net_metering_type, sell_price = self.get_selections()
        except TypeError:
            return

        # Form dictionary object for saving.
        rate_structure_object = {}
        
        if not self.save_name_field.text:
            popup = WarningPopup()
            popup.popup_text.text = 'Please specify a name to save the rate structure as.'
            popup.open()
            return
        else:
            rate_structure_object['name'] = self.save_name_field.text

        rate_structure_object['utility'] = {
            'utility name': utility_selected['utility_name'],
            'rate structure name': rate_structure_selected['name']
        }

        rate_structure_object['energy rate structure'] = {
            'weekday schedule': energy_weekday_schedule,
            'weekend schedule': energy_weekend_schedule,
            'energy rates': energy_rates_dict
        }

        rate_structure_object['demand rate structure'] = {
            'weekday schedule': demand_weekday_schedule,
            'weekend schedule': demand_weekend_schedule,
            'time of use rates': demand_tou_rates_dict,
            'flat rates': demand_flat_rates_dict,
            'minimum peak demand': peak_kw_min,
            'maximum peak demand': peak_kw_max
        }

        rate_structure_object['net metering'] = {
            'type': net_metering_type,
            'energy sell price': sell_price
        }

        # Save to JSON.
        # Strip non-alphanumeric chars from given name for filename.
        delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
        fname = rate_structure_object['name'].translate({ord(i): None for i in delchars})

        destination_dir = os.path.join(DATA_HOME, 'rate_structures')
        os.makedirs(destination_dir, exist_ok=True)
        destination_file = os.path.join(destination_dir, fname + '.json')

        if not os.path.exists(destination_file):
            with open(destination_file, 'w') as outfile:
                json.dump(rate_structure_object, outfile)
            
            popup = WarningPopup()
            popup.title = 'Success!'
            popup.popup_text.text = 'Rate structure data successfully saved.'
            popup.open()
        else:
            # File already exists with same name.
            popup = WarningPopup()
            popup.popup_text.text = 'A rate structure with the provided name already exists. Please specify a new name.'
            popup.open()

    def next_screen(self):
        self.manager.get_screen(self.manager.next()).reset_screen()
        self.manager.current = self.manager.next()


class RateStructureSaveNameTextInput(TextInput):
    """TextInput field for entering the save name in the Rate Structure Data Manager."""
    host_screen = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode

        if key_str in ('enter', 'numpadenter'):
            self.host_screen.save_rate_structure()
        else:
            super(RateStructureSaveNameTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        
        return True


class RateStructurePeriodTable(GridLayout):
    """A layout of RateStructureTableRow widgets that form a rate period table."""
    def __init__(self, **kwargs):
        super(RateStructurePeriodTable, self).__init__(**kwargs)

        self.period_rows = []

    def reset_table(self):
        self.period_rows = []

        while len(self.children) > 1:
            for widget in self.children:
                if isinstance(widget, RateStructureTableRow):
                    self.remove_widget(widget)
    
    def _validate_inputs(self):
        try:
            rate_dict = {rate.desc['period']: float(rate.text_input.text) for rate in self.period_rows}
        except ValueError:
            # An empty input.
            raise(InputError('All rates in the rate table must be specified.'))
        
        return rate_dict
    
    def get_rates(self):
        """Retrieves table data into a dictionary format."""
        rate_dict = self._validate_inputs()

        return rate_dict
    
    def copy_text_down(self, instance):
        """Copies the text from the text input to the next row."""
        # Find calling instance's position.
        ix = self.period_rows.index(instance)
        txt = instance.text_input.text

        try:
            ix_update = ix + 1
            self.period_rows[ix_update].text_input.text = txt
        except IndexError:
            pass
        

class RateStructureTableRow(GridLayout):
    """A labeled row with a TextInput for the tier rate."""
    desc = DictProperty()

    def __init__(self, **kwargs):
        super(RateStructureTableRow, self).__init__(**kwargs)

        self.name.text = self.desc['period']
        self.text_input.text = self.desc['rate']
    
    def copy_text_down(self):
        # Pass to parent table.
        self.parent.copy_text_down(self)

    def _validate_input(self):
        """Validate entry when unfocusing text input."""
        pass


class RateStructureRateTextInput(TextInput):
    """A TextInput field for entering rates in a RateStructurePeriodTable."""
    def insert_text(self, substring, from_undo=False):
        # limit # chars
        substring = substring[:8 - len(self.text)]
        return super(RateStructureRateTextInput, self).insert_text(substring, from_undo=from_undo)


class RateStructureScheduleGrid(GridLayout):
    """A layout of RateScheduleRow widgets that form a rate schedule table."""
    def __init__(self, **kwargs):
        super(RateStructureScheduleGrid, self).__init__(**kwargs)

        self.schedule_rows = []

        for ix in range(0, 13):
            if ix > 0:
                schedule_row = RateScheduleRow(row_name=calendar.month_abbr[ix])
                self.add_widget(schedule_row)
                self.schedule_rows.append(schedule_row)
            else:
                schedule_row = RateScheduleRow(row_name='', is_header=True)
                self.add_widget(schedule_row)
    
    def _validate_inputs(self):
        schedule_array = np.empty((12, 24), dtype=int)

        try:
            for ix, month_row in enumerate(self.schedule_rows, start=0):
                for iy, text_input in enumerate(month_row.text_inputs, start=0):
                    schedule_array[ix, iy] = int(text_input.text)
        except ValueError:
            # A TextInput is empty.
            raise(InputError('All schedule hours must be populated.'))

        return schedule_array
    
    def get_schedule(self):
        """Retrieves the rate schedule inputs into NumPy arrays."""
        schedule_array = self._validate_inputs()

        return schedule_array
    

class RateScheduleRow(GridLayout):
    """A labeled row of TextInput fields for the rate schedule table."""
    row_name = StringProperty('')

    def __init__(self, is_header=False, **kwargs):
        super(RateScheduleRow, self).__init__(**kwargs)

        self.name.text = self.row_name
        self.text_inputs = []

        for ix in range(24):
            if not is_header:
                text_input = RateScheduleTextInput()
                self.add_widget(text_input)
                self.text_inputs.append(text_input)
            else:
                col_header = RateScheduleColumnHeader(text=str(ix).zfill(2))
                self.add_widget(col_header)


class RateScheduleColumnHeader(BodyTextBase):
    pass


class RateScheduleTextInput(TextInput):
    """A TextInput field for entering rate schedule period numbers. Changes color based on input."""

    def insert_text(self, substring, from_undo=False):
        # Limit # chars to 2.
        substring = substring[:2 - len(self.text)]
        return super(RateScheduleTextInput, self).insert_text(substring, from_undo=from_undo)
    
    def get_background_color(self, input_text):
        """Change the background color depending on the text input."""
        try:
            ix = divmod(int(input_text), len(PALETTE))[1]
            return_color = rgba_to_fraction(PALETTE[ix])
        except ValueError:
            return_color = (1, 1, 1, 1)
        return return_color
    
    def get_foreground_color(self, input_text):
        """Change the font color depending on the background color."""
        try:
            ix = divmod(int(input_text), len(PALETTE))[1]
        except ValueError:
            return (0, 0, 0, 1)

        if not divmod(int(input_text), 6)[1] or not divmod(int(input_text), 5)[1]:
            return_color = (1, 1, 1, 1)
        else:
            return_color = (0, 0, 0, 1)

        return return_color

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key, key_str = keycode

        if key_str in ('up', 'left', 'down', 'right'):
            rate_schedule_row = self.parent
            rate_schedule_grid = self.parent.parent

            # Get the current column (hour) and row (month) indices.
            n_cols = len(rate_schedule_row.text_inputs)
            n_rows = len(rate_schedule_grid.schedule_rows)

            col_ix = rate_schedule_row.text_inputs.index(self)
            row_ix = rate_schedule_grid.schedule_rows.index(rate_schedule_row)

            if key_str == 'up':
                next_row_ix = row_ix - 1
                next_col_ix = col_ix
            elif key_str == 'down':
                next_row_ix = 0 if row_ix == n_rows-1 else row_ix + 1
                next_col_ix = col_ix
            elif key_str == 'left':
                next_row_ix = row_ix 
                next_col_ix = col_ix - 1
            elif key_str == 'right':
                next_row_ix = row_ix
                next_col_ix = 0 if col_ix == n_cols-1 else col_ix + 1
            
            # Focus the next specified text input.
            next_text_input = rate_schedule_grid.schedule_rows[next_row_ix].text_inputs[next_col_ix]
            next_text_input.focus = True
        elif key_str in ('enter', 'numpadenter'):
            tab_keycode = [9, 'tab']
            super(RateScheduleTextInput, self).keyboard_on_key_down(window, tab_keycode, text, modifiers)
        else:
            super(RateScheduleTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        
        return True
