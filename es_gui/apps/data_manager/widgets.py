from __future__ import absolute_import

from functools import partial
import os
import zipfile
import io
import calendar
import datetime
import logging
import threading
import socket
import math
import datetime as dt
import collections
import time

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, SwapTransition, SlideTransition
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.modalview import ModalView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.actionbar import ActionBar, ActionButton, ActionGroup
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty, DictProperty
from kivy.core.text import LabelBase

import urllib3
urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

from es_gui.resources.widgets.common import InputError, WarningPopup, ConnectionErrorPopup, MyPopup, APP_NAME, APP_TAGLINE, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction, fade_in_animation
from es_gui.apps.data_manager.data_manager import DataManagerException
from es_gui.proving_grounds.charts import RateScheduleChart
from es_gui.apps.data_manager.rate_structure import RateStructureDataScreen
from es_gui.apps.data_manager.utils import check_connection_settings
from es_gui.downloaders.market_data import download_ercot_data, download_isone_data, download_spp_data, download_nyiso_data, download_miso_data, download_pjm_data, download_caiso_data


MAX_THREADS = 4
MAX_WHILE_ATTEMPTS = 7


class DataManagerRTOMOdataScreen(Screen):
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.set_title('Data Manager: ISO/RTO Market and Operations Data')


class DataManagerMarketTabbedPanel(TabbedPanel):
    pass


class DataManagerPanelERCOT(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('ERCOTdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning('ERCOTdownloader: At least one download thread failed. See the log for details.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the years that returned errors.'), 0)
            else:
                logging.info('ERCOTdownloader: All requested data successfully finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data successfully finished downloading.'), 0)
            
            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.
        
        :param text: The text to be added to the log.
        :type text: str
        """
        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        """Checks if all options selected in the GUI are valid and returns them.
        
        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """
        # Check if all the spinners have been selected.
        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))
        
        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        # Check if a valid month range has been specified.
        datetime_start = datetime.date(year_start, 1, 1)
        datetime_end = datetime.date(year_end, 1, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid range where the starting year precedes the ending year.'))
        
        return datetime_start, datetime_end

    def get_inputs(self):
        """Gets the options selected in the GUI.
        
        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """
        datetime_start, datetime_end = self._validate_inputs()

        return datetime_start, datetime_end

    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        """Executes the data downloader for ERCOT data based on options selected in GUI.
        
        """
        try:
            datetime_start, datetime_end = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of years to iterate over.
            year_range = pd.date_range(
                datetime_start, datetime_end, 
                freq='YS'
                )
            year_range.union([year_range[-1] + 1])

            # Split up the download requests to accomodate the maximum amount of allowable threads.
            job_batches = batch_splitter(year_range, frequency='year')

            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = len(job_batches)*2
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_ercot_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_ercot_data, 
                    args=[os.path.join('data')],
                    kwargs={'year': batch, 'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'update_function': update_function}
                )
                thread_downloader.start()


class DataManagerPanelISONE(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def open_isone_acc_help(self):
        isone_acc_help_view = DataManagerISONEAccHelp()
        isone_acc_help_view.open()

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('ISO-NEdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning('ISO-NEdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                self.update_output_log('At least one download thread failed. Please retry downloading data for the months that returned errors.')
            else:
                logging.info('ISO-NEdownloader: All requested data downloaded and extracted.')
                self.update_output_log('All requested data downloaded and extracted.')
            
            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        # Check if all the spinners have been selected.
        month_start = self.month_start.text
        month_end = self.month_end.text

        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))
        
        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        if not month_start or month_start not in calendar.month_name:
            raise (InputError('Please select a valid starting month (got "' + month_start + '").'))
        elif not month_end or month_end not in calendar.month_name:
            raise (InputError('Please select a valid ending month (got "' + month_end + '").'))
        
        month_start_int = list(calendar.month_name).index(month_start)
        month_end_int = list(calendar.month_name).index(month_end)

        # Check if a valid month range has been specified.
        datetime_start = datetime.date(year_start, month_start_int, 1)
        datetime_end = datetime.date(year_end, month_end_int, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid month range where the starting month precedes the ending month.'))
        
        # Check if a username and password have been specified.
        acc_user = self.acc_user.text
        acc_pw = self.acc_pw.text

        if not acc_user:
            raise (InputError('Please enter an ISO-NE ISO Express username.'))
        if not acc_pw:
            raise (InputError('Please enter an ISO-NE ISO Express password.'))

        # Check if a node ID and/or node types have been specified.
        node_id = self.node_id.text
        nodes_selected = []
        total_nodes = 0
        if self.chkbx_hub.active:
            nodes_selected.append('4000')
            total_nodes += 1
        if self.chkbx_zones.active:
            nodes_selected.append('HUBS')
            total_nodes += 9
        if not node_id and not any(nodes_selected):
            raise (InputError('Please enter a node ID and/or select categories of pricing nodes.'))
        elif node_id:
            nodes_selected.append(node_id)
            total_nodes += 1
        
        return acc_user, acc_pw, datetime_start, datetime_end, nodes_selected, total_nodes

    def get_inputs(self):
        acc_user, acc_pw, datetime_start, datetime_end, nodes_selected, total_nodes = self._validate_inputs()

        return acc_user, acc_pw, datetime_start, datetime_end, nodes_selected, total_nodes
    
    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        try:
            acc_user, acc_pw, datetime_start, datetime_end, nodes_selected, total_nodes = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of months to iterate over.
            monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            monthrange.union([monthrange[-1] + 1])

            # Compute number of days in the given range.
            total_days = 0
            for date in monthrange:
                total_days += calendar.monthrange(date.year, date.month)[1]
            
            total_months = len(monthrange)
            
            # Distribute the requests for multiple threads.
            job_batches = batch_splitter(monthrange)

            self.n_active_threads = len(job_batches)
            
            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = total_months*total_nodes + total_months
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_ISONE_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_isone_data, 
                    args=(acc_user, acc_pw, os.path.join('data'), batch[0], batch[-1]),
                    kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'nodes': nodes_selected, 'n_attempts': MAX_WHILE_ATTEMPTS, 'update_function': update_function}
                    )

                thread_downloader.start()


class DataManagerPanelMISO(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('MISOdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning('MISOdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'), 0)
            else:
                logging.info('MISOdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)
            
            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.
        
        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        """Checks if all options selected in the GUI are valid and returns them.
        
        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        # Check if all the spinners have been selected.
        month_start = self.month_start.text
        month_end = self.month_end.text

        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))
        
        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        if not month_start or month_start not in calendar.month_name:
            raise (InputError('Please select a valid starting month (got "' + month_start + '").'))
        elif not month_end or month_end not in calendar.month_name:
            raise (InputError('Please select a valid ending month (got "' + month_end + '").'))
        
        month_start_int = list(calendar.month_name).index(month_start)
        month_end_int = list(calendar.month_name).index(month_end)

        # Check if a valid month range has been specified.
        datetime_start = datetime.date(year_start, month_start_int, 1)
        datetime_end = datetime.date(year_end, month_end_int, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid month range where the starting month precedes the ending month.'))
        
        return datetime_start, datetime_end

    def get_inputs(self):
        """Gets the options selected in the GUI.
        
        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        datetime_start, datetime_end = self._validate_inputs()

        return datetime_start, datetime_end
    
    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        """Executes the data downloader for MISO data based on options selected in GUI.
        
        """

        try:
            datetime_start, datetime_end = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of months to iterate over.
            monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            monthrange.union([monthrange[-1] + 1])

            # Compute number of days in the given range.
            total_days = 0
            for date in monthrange:
                total_days += calendar.monthrange(date.year, date.month)[1]

            self.n_active_threads = len(monthrange)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = 2*total_days
            self.output_log.text = ''

            # Split up the download requests to accomodate the maximum amount of allowable threads.
            job_batches = batch_splitter(monthrange)

            self.n_active_threads = len(job_batches)

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_MISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_miso_data, 
                    args=(os.path.join('data'), batch[0], batch[-1]),
                    kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'n_attempts': MAX_WHILE_ATTEMPTS, 'update_function': update_function}
                )

                thread_downloader.start()


class DataManagerPanelNYISO(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('NYISOdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning \
                    ('NYISOdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'), 0)
            else:
                logging.info('NYISOdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)

            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.

        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        """Checks if all options selected in the GUI are valid and returns them.

        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        # Check if all the spinners have been selected.
        month_start = self.month_start.text
        month_end = self.month_end.text

        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))

        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        if not month_start or month_start not in calendar.month_name:
            raise (InputError('Please select a valid starting month (got "' + month_start + '").'))
        elif not month_end or month_end not in calendar.month_name:
            raise (InputError('Please select a valid ending month (got "' + month_end + '").'))

        month_start_int = list(calendar.month_name).index(month_start)
        month_end_int = list(calendar.month_name).index(month_end)

        # Check if a valid month range has been specified.
        datetime_start = datetime.date(year_start, month_start_int, 1)
        datetime_end = datetime.date(year_end, month_end_int, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid month range where the starting month precedes the ending month.'))
        
        # Check if at least one node type has been specified.
        if self.chkbx_zonal.active and self.chkbx_gens.active:
            nodes_selected = 'both'
        elif self.chkbx_zonal.active:
            nodes_selected = 'zone'
        elif self.chkbx_gens.active:
            nodes_selected = 'gen'
        else:
            nodes_selected = None
            raise (InputError('Please select at least one category of pricing nodes.'))

        return datetime_start, datetime_end, nodes_selected

    def get_inputs(self):
        """Gets the options selected in the GUI.

        :return: datetime of start of range, datetime of end of range, str describing which nodes to download
        :rtype: 2-tuple of datetime, str
        """

        datetime_start, datetime_end, nodes_selected = self._validate_inputs()

        return datetime_start, datetime_end, nodes_selected
    
    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        """Executes the data downloader for NYISO data based on options selected in GUI.
        """
        try:
            datetime_start, datetime_end, nodes_selected = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of months to iterate over.
            monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            monthrange.union([monthrange[-1] + 1])

            # Distribute the requests for multiple threads.
            job_batches = batch_splitter(monthrange)

            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            if nodes_selected == 'both':
                self.progress_bar.max = len(monthrange)*3
            else:
                self.progress_bar.max = len(monthrange)*2
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_NYISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_nyiso_data,
                    args=(os.path.join('data'), batch[0], batch[-1]),
                    kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'zone_gen': nodes_selected, 'RT_DAM': 'DAM', 'n_attempts': MAX_WHILE_ATTEMPTS, 'update_function': update_function}
                    )

                thread_downloader.start()


class DataManagerPanelSPP(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('SPPdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning \
                    ('SPPdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'),0)
            else:
                logging.info('SPPdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)

            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.

        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        """Checks if all options selected in the GUI are valid and returns them.

        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        # Check if all the spinners have been selected.
        month_start = self.month_start.text
        month_end = self.month_end.text

        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))

        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        if not month_start or month_start not in calendar.month_name:
            raise (InputError('Please select a valid starting month (got "' + month_start + '").'))
        elif not month_end or month_end not in calendar.month_name:
            raise (InputError('Please select a valid ending month (got "' + month_end + '").'))

        month_start_int = list(calendar.month_name).index(month_start)
        month_end_int = list(calendar.month_name).index(month_end)

        # Check if a valid month range has been specified.
        datetime_start = datetime.date(year_start, month_start_int, 1)
        datetime_end = datetime.date(year_end, month_end_int, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid month range where the starting month precedes the ending month.'))

        # Check if at least one node type has been specified.
        if self.chkbx_location.active and self.chkbx_bus.active:
            nodes_selected = 'both'
        elif self.chkbx_location.active:
            nodes_selected = 'location'
        elif self.chkbx_bus.active:
            nodes_selected = 'bus'
        else:
            nodes_selected = None
            raise (InputError('Please select at least one category of pricing nodes.'))

        return datetime_start, datetime_end, nodes_selected

    def get_inputs(self):
        """Gets the options selected in the GUI.

        :return: datetime of start of range, datetime of end of range, str describing which nodes to download
        :rtype: 2-tuple of datetime, str
        """

        datetime_start, datetime_end, nodes_selected = self._validate_inputs()

        return datetime_start, datetime_end, nodes_selected
    
    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        """Executes the data downloader for SPP data based on options selected in GUI.
        """
        try:
            datetime_start, datetime_end, nodes_selected = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of months to iterate over.
            monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            monthrange.union([monthrange[-1] + 1])

            # Compute number of days in the given range.
            total_days = 0
            for date in monthrange:
                total_days += calendar.monthrange(date.year, date.month)[1]

            # Distribute the requests for multiple threads.
            job_batches = batch_splitter(monthrange)

            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            if nodes_selected == 'both':
                self.progress_bar.max = total_days * 3
            else:
                self.progress_bar.max = total_days * 2
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_SPP_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_spp_data, 
                    args=(os.path.join('data'), batch[0], batch[-1]),
                    kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'bus_loc': nodes_selected, 'n_attempts': MAX_WHILE_ATTEMPTS, 'update_function': update_function}
                )

                thread_downloader.start()


class DataManagerPanelCAISO(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('CAISOdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning(
                    'CAISOdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'),0)
            else:
                logging.info('CAISOdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)

            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.

        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        """Checks if all options selected in the GUI are valid and returns them.

        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        # Check if all the spinners have been selected.
        month_start = self.month_start.text
        month_end = self.month_end.text

        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))

        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        if not month_start or month_start not in calendar.month_name:
            raise (InputError('Please select a valid starting month (got "' + month_start + '").'))
        elif not month_end or month_end not in calendar.month_name:
            raise (InputError('Please select a valid ending month (got "' + month_end + '").'))

        month_start_int = list(calendar.month_name).index(month_start)
        month_end_int = list(calendar.month_name).index(month_end)

        # Check if a valid month range has been specified.
        datetime_start = dt.date(year_start, month_start_int, 1)
        datetime_end = dt.date(year_end, month_end_int, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid month range where the starting month precedes the ending month.'))

        # Check if a node ID and/or node types have been specified.
        total_nodes = 0
        node_id_txtinput = self.node_id_txtinput.text
        node_type_chkbx = [self.chkbx_th, self.chkbx_asp]
        node_type_nonodes = [3, 29]
        nodes_selected = [node_type.attr_name for node_type in node_type_chkbx if node_type.active]
        total_nodes_sel = [node_type_nonodes[nx] for nx, node_type in enumerate(node_type_chkbx) if node_type.active]
        for node_no_x in total_nodes_sel:
            total_nodes += node_no_x

        if not node_id_txtinput and not any(nodes_selected):
            raise (InputError('Please enter a node ID and/or select categories of pricing nodes.'))
        elif node_id_txtinput:
            nodes_selected.append(node_id_txtinput)
            total_nodes += 1

        return datetime_start, datetime_end, nodes_selected, total_nodes

    def get_inputs(self):
        """Gets the options selected in the GUI.

        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        datetime_start, datetime_end, node_type_selected, total_nodes = self._validate_inputs()

        return datetime_start, datetime_end, node_type_selected, total_nodes
    
    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        """Executes the data downloader for CAISO data based on options selected in GUI.

        """
        try:
            datetime_start, datetime_end, node_type_selected, total_nodes = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of months to iterate over.
            monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            monthrange.union([monthrange[-1] + 1])
            total_months = len(monthrange)

            # Split up the download requests to accomodate the maximum amount of allowable threads.
            # job_batches = batch_splitter(monthrange)
            # job_batches = monthrange # for CAISO only one thread is allowed due to error 429 of only one request per 5 seconds
            job_batches = collections.deque([date for date in monthrange])
            job_batches = [job_batches]
            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = total_months*total_nodes + 2*total_months
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_CAISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_caiso_data,
                    args=(os.path.join('data'), batch[0], batch[-1]),
                    kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings,
                            'nodes': node_type_selected, 'n_attempts': MAX_WHILE_ATTEMPTS, 'update_function': update_function}
                    )

                thread_downloader.start()


class DataManagerPanelPJM(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)
    request_cancel = threading.Event()

    def open_pjm_subkey_help(self):
        pjm_subkey_help_view = DataManagerPJMSubKeyHelp()
        pjm_subkey_help_view.open()    

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.request_cancel.is_set():
                logging.warning \
                    ('PJMdownloader: User manually canceled download requests.')
                Clock.schedule_once(partial(self.update_output_log, 'Download requests canceled.'), 0)
            elif self.thread_failed:
                logging.warning('PJMdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'), 0)
            else:
                logging.info('PJMdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)
            
            self.execute_download_button.disabled = False
            self.cancel_download_button.disabled = True
            self.thread_failed = False
            self.request_cancel.clear()

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.
        
        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])
    
    @mainthread
    def increment_progress_bar(self, *args):
        """Increases the value of the progress bar by 1."""
        self.progress_bar.value += 1

    def _validate_inputs(self):
        """Checks if all options selected in the GUI are valid and returns them.
        
        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        # Check if all the spinners have been selected.
        month_start = self.month_start.text
        month_end = self.month_end.text

        try:
            year_start = int(self.year_start.text)
        except ValueError:
            raise (InputError('Please select a starting year.'))
        
        try:
            year_end = int(self.year_end.text)
        except ValueError:
            raise (InputError('Please select an ending year.'))

        if not month_start or month_start not in calendar.month_name:
            raise (InputError('Please select a valid starting month (got "' + month_start + '").'))
        elif not month_end or month_end not in calendar.month_name:
            raise (InputError('Please select a valid ending month (got "' + month_end + '").'))
        
        month_start_int = list(calendar.month_name).index(month_start)
        month_end_int = list(calendar.month_name).index(month_end)

        # Check if a valid month range has been specified.
        datetime_start = dt.date(year_start, month_start_int, 1)
        datetime_end = dt.date(year_end, month_end_int, 1)

        if datetime_start > datetime_end:
            raise (InputError('Please specify a valid month range where the starting month precedes the ending month.'))
        
        # Check if a subscription key has been specified.
        sub_key = self.subscription_key.text

        if not sub_key:
            raise (InputError('Please enter a subscription key.'))

        # Check if a node ID and/or node types have been specified.
        node_id_txtinput = self.node_id_txtinput.text
        node_type_chkbx = [self.chkbx_pjm_avg, self.chkbx_aggregate, self.chkbx_zone, self.chkbx_hub]
        nodes_selected = [node_type.attr_name for node_type in node_type_chkbx if node_type.active]

        if not node_id_txtinput and not any(nodes_selected):
            raise (InputError('Please enter a node ID and/or select categories of pricing nodes.'))
        elif node_id_txtinput:
            nodes_selected.append(node_id_txtinput)
        
        return sub_key, datetime_start, datetime_end, nodes_selected

    def get_inputs(self):
        """Gets the options selected in the GUI.
        
        :return: datetime of start of range, datetime of end of range
        :rtype: 2-tuple of datetime
        """

        sub_key, datetime_start, datetime_end, node_type_selected = self._validate_inputs()

        return sub_key, datetime_start, datetime_end, node_type_selected
    
    def cancel_download(self):
        self.request_cancel.set()
        Clock.schedule_once(partial(self.update_output_log, 'Canceling download requests...'), 0)
        self.cancel_download_button.disabled = True

    def execute_download(self):
        """Executes the data downloader for PJM data based on options selected in GUI.
        """
        try:
            sub_key, datetime_start, datetime_end, node_type_selected = self.get_inputs()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.execute_download_button.disabled = True
            self.cancel_download_button.disabled = False

            # Compute the range of months to iterate over.
            monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            monthrange.union([monthrange[-1] + 1])

            # Split up the download requests to accomodate the maximum amount of allowable threads.
            job_batches = batch_splitter(monthrange)

            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = 0
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            update_function = _build_update_progress_function(self)

            # Spawn a new thread for each download_PJM_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(
                    target=download_pjm_data, 
                    args=(os.path.join('data'), sub_key, batch[0], batch[-1]),
                    kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'nodes': node_type_selected, 'n_attempts': MAX_WHILE_ATTEMPTS, 'update_function': update_function}
                    )

                thread_downloader.start()
        

class DataManagerCheckbox(CheckBox):
    node_type_name = StringProperty('')


class DataManagerPJMSubKeyHelp(ModalView):
    pass


class DataManagerISONEAccHelp(ModalView):
    pass


def batch_splitter(date_range, frequency='month'):
    """Splits a Pandas date_range evenly to allocate data download workload among different threads.

    :param date_range: Range of dates to download data for.
    :type text: Pandas date_range
    :return: list of batch jobs to pass to data downloader function
    :rtype: list of batches (list of datetime)
    """
    # Split up the download requests to accomodate the maximum amount of allowable threads.
    if frequency == 'year':
        date_queue = collections.deque([date.year for date in date_range])
    else:
        date_queue = collections.deque([date for date in date_range])
    batch_size = math.ceil(len(date_queue) / MAX_THREADS)

    job_batches = []
    while len(date_queue) > 0:
        batch = []

        for ix in range(batch_size):
            try:
                batch.append(date_queue.popleft())
            except IndexError:
                # Pop from empty queue.
                continue

        job_batches.append(batch)
    
    return job_batches


def _build_update_progress_function(panel_instance):
    """Builds the data download update progress function specific to the panel_instance object.
    """
    def update_progress_function(update):
        """Updates the GUI (output log and/or progress bar) based on feedback from the data downloader function.

        This function is passed to the data downloader function and is called when GUI updates are instructed.

        Parameters
        ----------
        update : int or str
            The update passed back from the data downloader function.
        """
        if isinstance(update, int):
            if update == -1:
                # Decrement the number of active threads.
                panel_instance.n_active_threads -= 1
            else:
                # Increment the progress bar.
                # Increase progress bar maximum if necessary (PJM data downloader computes progress bar max during node lookup).
                if panel_instance.progress_bar.value + update > panel_instance.progress_bar.max:
                    panel_instance.progress_bar.max += update
                else:
                    for ix in range(update):
                        Clock.schedule_once(panel_instance.increment_progress_bar, 0)
        elif isinstance(update, str):
            # Print a message to the output log.
            Clock.schedule_once(partial(panel_instance.update_output_log, update), 0)
    
    return update_progress_function
