from __future__ import absolute_import

import os
import io
import calendar
import datetime
import logging
import threading
import datetime as dt

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

from es_gui.resources.widgets.common import InputError, WarningPopup, MyPopup, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction
from es_gui.apps.data_manager.data_manager import DataManagerException
from es_gui.tools.charts import RateScheduleChart
from es_gui.apps.data_manager.utils import check_connection_settings

MAX_WHILE_ATTEMPTS = 7

URL_OPENEI_IOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/500990ae-ada2-4791-9206-01dc68e36f12/download/iouzipcodes2017.csv"
URL_OPENEI_NONIOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/672523aa-0d8a-4e6c-8a10-67e311bb1691/download/noniouzipcodes2017.csv"
APIROOT_OPENEI = "https://api.openei.org/utility_rates?"
VERSION_OPENEI = "version=latest"
REQUEST_FMT_OPENEI = "&format=json"
DETAIL_OPENEI = "&detail=full"

bx_anim = Animation(transition='out_expo', duration=FADEIN_DUR, opacity=1)

class RateStructureDataScreen(Screen):
    """"""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager: Utility Rate Structure Data')


class RateStructureScreenManager(ScreenManager):
    """The screen manager for the Data Manager Rate Structure Data screens."""
    def __init__(self, **kwargs):
        super(RateStructureScreenManager, self).__init__(**kwargs)

        self.transition = SlideTransition()
        self.add_widget(RateStructureUtilitySearchScreen(name='start'))
        self.add_widget(RateStructureEnergyRateStructureScreen(name='energy_rate_structure'))
        self.add_widget(RateStructureDemandRateStructureScreen(name='demand_rate_structure'))

class RateStructureOpenEIapiHelp(ModalView):
    """ModalView to display instructions on how to get an OpenEI API key."""


class RateStructureUtilitySearchScreen(Screen):
    """DataManager Rate Structure screen for searching for a utility rate structure."""
    utility_ref_table = pd.DataFrame()
    utility_selected = DictProperty()
    rate_structure_selected = DictProperty()
    api_key = StringProperty('')

    def __init__(self, **kwargs):
        super(RateStructureUtilitySearchScreen, self).__init__(**kwargs)

        DataManagerUtilitySearchRVNodeEntry.host_screen = self
        DataManagerRateStructureRVNodeEntry.host_screen = self

    def open_openei_key_help(self):
        """Opens the OpenEI API key ModalView."""
        open_ei_help_view = RateStructureOpenEIapiHelp()
        open_ei_help_view.open()
    
    def _reset_screen(self):
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
    
    def _download_utility_ref_table(self):
        """Downloads and builds the utility reference table from OpenEI."""

        ssl_verify, proxy_settings = check_connection_settings()

        try:
            with requests.Session() as req:
                http_request = req.get(URL_OPENEI_IOU,
                                        proxies=proxy_settings, 
                                        timeout=6, 
                                        verify=ssl_verify,
                                        stream=True)
                if http_request.status_code != requests.codes.ok:
                    http_request.raise_for_status()
        except requests.HTTPError as e:
            logging.error('DMUtilitySearch: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('DMUtilitySearch: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('DMUtilitySearch: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('DMUtilitySearch: The connection timed out.')
        except requests.RequestException as e:
            logging.error('DMUtilitySearch: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('DMUtilitySearch: An unexpected error has occurred. ({0})'.format(repr(e)))
        else:
            data_down = http_request.content.decode(http_request.encoding)
            data_iou = pd.read_csv(io.StringIO(data_down))
        
        try:
            with requests.Session() as req:
                http_request = req.get(URL_OPENEI_NONIOU,
                                        proxies=proxy_settings, 
                                        timeout=6, 
                                        verify=ssl_verify,
                                        stream=True)
                if http_request.status_code != requests.codes.ok:
                    http_request.raise_for_status()
        except requests.HTTPError as e:
            logging.error('DMUtilitySearch: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('DMUtilitySearch: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('DMUtilitySearch: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('DMUtilitySearch: The connection timed out.')
        except requests.RequestException as e:
            logging.error('DMUtilitySearch: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('DMUtilitySearch: An unexpected error has occurred. ({0})'.format(repr(e)))
        else:
            data_down = http_request.content.decode(http_request.encoding)
            data_noniou = pd.read_csv(io.StringIO(data_down))
        
        try:
            df_combined = pd.concat([data_iou, data_noniou], ignore_index=True)
        except NameError:
            # Connection error prevented downloads.
            raise requests.ConnectionError
        else:
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
        if self.chkbx_by_name.active:
            search_type = 'utility_name'
        elif self.chkbx_by_zip.active:
            search_type = 'zip'
        elif self.chkbx_by_state.active:
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
            self._reset_screen()
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
                        popup = WarningPopup()
                        popup.popup_text.text = 'There was an issue connecting and downloading list of utilities.'
                        popup.open()
                        return
                
                # Filter DataFrame by search type/query and drop duplicate entries.
                if not search_type == 'zip': 
                    utility_data_filtered = self.utility_ref_table.loc[self.utility_ref_table[search_type].str.lower().str.contains(search_query)]
                else:
                    utility_data_filtered = self.utility_ref_table.loc[self.utility_ref_table[search_type] == search_query]
                
                utility_data_filtered = utility_data_filtered[['eiaid', 'utility_name', 'state', 'ownership']]
                utility_data_filtered.drop_duplicates(inplace=True)

                logging.info('RateStructureDM: Utility table filter completed.')

                if utility_data_filtered.empty:
                    logging.warning('RateStructureDM: No results matched the query.')

                    popup = WarningPopup()
                    popup.popup_text.text = 'No results matched your query.'
                    popup.open()

                # Enable search results selector.
                bx_anim.start(self.utility_select_bx)
                self._populate_utility_selector(utility_data_filtered)

                # Animation.stop_all(self.loading_screen.logo, 'opacity')
                # self.loading_screen.dismiss()
                self.search_button.disabled = False

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

        thread_query = threading.Thread(target=self._query_api_for_rate_structures, args=[api_query])
        thread_query.start()

        # Open loading screen.
        self.loading_screen = LoadingModalView()
        self.loading_screen.loading_text.text = 'Retrieving rate structures...'
        self.loading_screen.open()
    
    def _query_api_for_rate_structures(self, api_query):
        """Uses OpenEI API to query the rate structures for given EIA ID and populates rate structure RecycleView."""
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
            logging.error('DMUtilitySearch: {0}'.format(repr(e)))

            popup = WarningPopup()
            popup.popup_text.text = repr(e)
            popup.open()
        except requests.exceptions.ProxyError:
            logging.error('DMUtilitySearch: Could not connect to proxy.')

            popup = WarningPopup()
            popup.popup_text.text = 'Could not connect to proxy.'
            popup.open()
        except requests.ConnectionError as e:
            logging.error('DMUtilitySearch: Failed to establish a connection to the host server.')

            popup = WarningPopup()
            popup.popup_text.text = 'Failed to establish a connection to the host server.'
            popup.open()
        except requests.Timeout as e:
            logging.error('DMUtilitySearch: The connection timed out.')

            popup = WarningPopup()
            popup.popup_text.text = 'The connection timed out.'
            popup.open()
        except requests.RequestException as e:
            logging.error('DMUtilitySearch: {0}'.format(repr(e)))

            popup = WarningPopup()
            popup.popup_text.text = repr(e)
            popup.open()
        except Exception as e:
            # Something else went wrong.
            logging.error('DMUtilitySearch: An unexpected error has occurred. ({0})'.format(repr(e)))

            popup = WarningPopup()
            popup.popup_text.text = 'An unexpected error has occurred. ({0})'.format(repr(e))
            popup.open()
        else:
            structure_list = http_request.json()['items']

            structure_df = pd.DataFrame.from_records(structure_list)
            structure_df.dropna(subset=['energyratestructure'], inplace=True)

            # Filter out entries whose energyratestructure array does not contain "rate" terms
            mask = structure_df['energyratestructure'].apply(lambda x: all(['rate' in hr.keys() for row in x for hr in row]))
            structure_df = structure_df[mask]

            structure_list = structure_df.to_dict(orient='records')

            # Display name: Name (record['startdate'])
            effective_dates = ['(Effective Date : {0})'.format(dt.datetime.fromtimestamp(record['startdate']).strftime('%m/%d/%Y'))  if not np.isnan(record['startdate']) else '' for record in structure_list]

            records = [{'name': record['name'] + ' ' + effective_dates[ix] , 'record': record} 
            for ix, record in enumerate(structure_list, start=0)]
            records = sorted(records, key=lambda t: t['name'])

            self.rate_structure_rv.data = records
            self.rate_structure_rv.unfiltered_data = records

            logging.info('RateStructureDM: Retrieved utility rate structures.')
            self.loading_screen.dismiss()

            bx_anim.start(self.rate_structure_select_bx)
    
    def on_rate_structure_selected(self, instance, value):
        try:
            logging.info('RateStructureDM: Rate structure selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('RateStructureDM: Rate structure selection reset.')
            self.rate_structure_desc.text = ''
        else:
            self.manager.get_screen('energy_rate_structure').populate_rate_schedules(value)
            self.manager.get_screen('demand_rate_structure').populate_rate_schedules(value)
        
        try:
            self.rate_structure_desc.text = value.get('description', 'No description provided.')
        except ValueError:
            pass


class DataManagerUtilitySearchRVNodeEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(DataManagerUtilitySearchRVNodeEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.utility_selected = rv.data[self.index]['record']


class DataManagerRateStructureRVNodeEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(DataManagerRateStructureRVNodeEntry, self).apply_selection(rv, index, is_selected)

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
        periods = set(rates_dict.keys())

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

    def go_to_demand_rate_schedule(self):
        """Check if all input data is valid before proceeding to the next demand rate structure screen."""
        try:
            weekday_schedule, weekend_schedule, rates_dict = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            logging.info('EnergyRateSchedule: All seems well.')
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
        flat_demand_months = rate_structure.get('flatdemandmonths', np.zeros(shape=(12,1)))
        flat_demand_rates = rate_structure.get('flatdemandstructure', [[{'rate': 0}]])
        tou_demand_rates = rate_structure.get('demandratestructure', [[{'rate': 0}]])

        # Sometimes rather than being empty, a nan is in the field.
        if type(flat_demand_rates) == float:
            flat_demand_rates = np.zeros(shape=(12, 1), dtype=int)
        
        if type(flat_demand_months) == float:
            flat_demand_months = np.zeros(shape=(12, 1), dtype=int)

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
            logging.warning('DemandRateSchedule: No demand rate schedules provided, setting to flat schedule...')

            weekday_schedule_data = np.zeros(shape=(12, 24), dtype=int)
            weekend_schedule_data = np.zeros(shape=(12, 24), dtype=int)
        else:
            # Sometimes rather than being empty, a nan is in the field.
            if type(weekday_schedule_data) == float:
                logging.warning('DemandRateSchedule: No demand rate schedules provided, setting to flat schedule...')
                weekday_schedule_data = np.zeros(shape=(12, 24), dtype=int)
            if type(weekend_schedule_data) == float:
                logging.warning('DemandRateSchedule: No demand rate schedules provided, setting to flat schedule...')
                weekend_schedule_data = np.zeros(shape=(12, 24), dtype=int)

        print(self.rate_structure)

        # Weekday chart.
        for ix, month_row in enumerate(self.weekday_chart.schedule_rows, start=0):
            for iy, text_input in enumerate(month_row.text_inputs, start=0):
                text_input.text = str(weekday_schedule_data[ix][iy])
        
        # Weekend chart.
        for ix, month_row in enumerate(self.weekend_chart.schedule_rows, start=0):
            for iy, text_input in enumerate(month_row.text_inputs, start=0):
                text_input.text = str(weekend_schedule_data[ix][iy])


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
            rate_dict = {int(rate.desc['period']): float(rate.text_input.text) for rate in self.period_rows}
        except ValueError:
            # An empty input.
            raise(InputError('All rates in the rate table must be specified.'))
        
        return rate_dict
    
    def get_rates(self):
        rate_dict = self._validate_inputs()

        return rate_dict
        

class RateStructureTableRow(GridLayout):
    """A labeled row with a TextInput for the tier rate."""
    desc = DictProperty()

    def __init__(self, **kwargs):
        super(RateStructureTableRow, self).__init__(**kwargs)

        self.name.text = self.desc['period']
        self.text_input.text = self.desc['rate']

    def _validate_input(self):
        """Validate entry when unfocusing text input."""
        pass
        # if not self.text_input.focus:
        #     try:
        #         input_value = float(self.text_input.text)
        #     except ValueError:
        #         # No text entered.
        #         input_value = self.param_slider.value
        #         self.text_input.text = str(input_value)

        #         return

        #     if input_value > self.param_max or input_value < self.param_min:
        #         # If input value is out of range.
        #         popup = WarningPopup()
        #         popup.popup_text.text = '{param_name} must be between {param_min} and {param_max} (got {input_val}).'.format(param_name=self.name.text[:1].upper() + self.name.text[1:], param_min=self.param_min, param_max=self.param_max, input_val=input_value)
        #         popup.open()

        #         input_value = self.param_slider.value
        #         self.text_input.text = str(input_value)
        #     else:
        #         # Set slider value to input value.
        #         anim = Animation(transition='out_expo', duration=SLIDER_DUR, value=input_value)
        #         anim.start(self.param_slider)


class RateStructureRateTextInput(TextInput):
    """A TextInput field for entering parameter values."""

    def insert_text(self, substring, from_undo=False):
        # limit # chars
        substring = substring[:8 - len(self.text)]
        return super(RateStructureRateTextInput, self).insert_text(substring, from_undo=from_undo)


class RateStructureScheduleGrid(GridLayout):
    """A layout of RateScheduleRow widgets that form a rate schedule table."""
    def __init__(self, **kwargs):
        super(RateStructureScheduleGrid, self).__init__(**kwargs)

        self.schedule_rows = []

        for ix in range(1, 13):
            schedule_row = RateScheduleRow(row_name=calendar.month_abbr[ix])
            self.add_widget(schedule_row)
            self.schedule_rows.append(schedule_row)
    
    def _validate_inputs(self):
        schedule_array = np.empty((12, 24))

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

    def __init__(self, **kwargs):
        super(RateScheduleRow, self).__init__(**kwargs)

        self.name.text = self.row_name
        self.text_inputs = []

        for ix in range(1, 25):
            text_input = RateScheduleTextInput()
            self.add_widget(text_input)
            self.text_inputs.append(text_input)


class RateScheduleTextInput(TextInput):
    """A TextInput field for entering rate schedule tiers. Changes color based on input."""

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
