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

from valuation.es_gui.resources.widgets.common import InputError, WarningPopup, ConnectionErrorPopup, MyPopup, APP_NAME, APP_TAGLINE, RecycleViewRow, FADEIN_DUR, LoadingModalView, PALETTE, rgba_to_fraction, fade_in_animation
from valuation.es_gui.apps.data_manager.data_manager import DataManagerException
from valuation.es_gui.proving_grounds.charts import RateScheduleChart
from valuation.es_gui.apps.data_manager.rate_structure import RateStructureDataScreen
from valuation.es_gui.apps.data_manager.utils import check_connection_settings
from valuation.paths import get_path
dirname = get_path()

MAX_THREADS = 4
MAX_WHILE_ATTEMPTS = 7

URL_OPENEI_IOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/500990ae-ada2-4791-9206-01dc68e36f12/download/iouzipcodes2017.csv"
URL_OPENEI_NONIOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/672523aa-0d8a-4e6c-8a10-67e311bb1691/download/noniouzipcodes2017.csv"
APIROOT_OPENEI = "https://api.openei.org/utility_rates?"
VERSION_OPENEI = "version=latest"
REQUEST_FMT_OPENEI = "&format=json"
DETAIL_OPENEI = "&detail=full"


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
            year_range = pd.date_range(datetime_start, datetime_end, freq='YS')

            # Split up the download requests to accomodate the maximum amount of allowable threads.
            job_batches = batch_splitter(year_range, frequency='year')

            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = len(job_batches)*2
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            # Spawn a new thread for each download_ercot_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_ercot_data, 
                kwargs={'year': batch, 'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings})
                thread_downloader.start()
    
    def _download_ercot_data(self, year='all', typedat='both', foldersave=os.path.join('data'), ssl_verify=True, proxy_settings=None):
        """Downloads and extracts specified ERCOT data to the specified local directory.
        
        :param year: An int, str, or list of int/str specifying the year(s) of data to download, defaults to 'all'
        :param year: str, optional
        :param typedat: The type of data to download. 'spp' for settlement point price, 'ccp' for capacity clearing price, or 'both' for both, defaults to 'both'
        :param typedat: {'spp', 'ccp', 'both'}, optional
        :param foldersave: The root directory to save the downloaded and extracted data, defaults to os.path.join('data')
        :param foldersave: str, optional
        """
        # Base URLs for ERCOT website.
        urlERCOTdown_ini = "http://mis.ercot.com/"
        urlERCOT_spp = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13060&reportTitle=Historical%20DAM%20Load%20Zone%20and%20Hub%20Prices&showHTMLView=&mimicKey/"
        urlERCOT_ccp = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13091&reportTitle=Historical%20DAM%20Clearing%20Prices%20for%20Capacity&showHTMLView=&mimicKey/"

        # Determine which categories of data to download and save.
        urlERCOT_list = []
        folderprice = []
        if typedat == "both":
            urlERCOT_list.append(urlERCOT_spp)
            urlERCOT_list.append(urlERCOT_ccp)
            folderprice.append("/ERCOT/SPP/")
            folderprice.append("/ERCOT/CCP/")
        elif typedat == "spp":
            urlERCOT_list.append(urlERCOT_spp)
            folderprice.append("/ERCOT/SPP/")
        elif typedat == "ccp":
            urlERCOT_list.append(urlERCOT_ccp)
            folderprice.append("/ERCOT/CCP/")

        # Iterate through the requested data categories.
        for ixlp, urlERCOT_list_x in enumerate(urlERCOT_list):
            try:
                # Retrieve the webpage and parse for .zip files.
                page = requests.get(urlERCOT_list_x, timeout=10, proxies=proxy_settings, verify=ssl_verify)
                soup_ERCOT_page = BeautifulSoup(page.content, 'html.parser')

                zipfileslinks_ERCOT_page = []
                for link in soup_ERCOT_page.find_all('a'):
                    zipfileslinks_ERCOT_page.append(link.get('href'))
                    #print(link.get('href'))
                #print(zipfileslinks_ERCOT_page)

                zipfilesnames_ERCOT_page = []
                for tdlink in soup_ERCOT_page.find_all('td', attrs={'class': 'labelOptional_ind'}):
                    zipfilesnames_ERCOT_page.append(tdlink.text)
                    #print(tdlink.text)
                #print(zipfilesnames_ERCOT_page)

                # Find the .zip files for the requested years of data.
                if year == "all":
                    ixloop = range(len(zipfilesnames_ERCOT_page))
                else:
                    yearlist = year
                    if type(year) is str:
                        yearlist = []
                        yearlist.append(year)
                    elif type(year) is int:
                        yearlist = []
                        yearlist.append(str(year))
                    ixloop = []
                    for year_x in yearlist:
                        #logging.info('ERCOTdownloader: Downloading data for {0}...'.format(year_x))
                        #Clock.schedule_once(partial(self.update_output_log, 'Downloading data for {0}...'.format(year_x)))
                        
                        yearstr = str(year_x)
                        yearzip = "_" + yearstr + ".zip"
                        ixloop_x = [ix for ix, x in enumerate(zipfilesnames_ERCOT_page) if yearzip in x]
                        ixloop.append(ixloop_x[0])

                # Extract the .zip files to the specified local directory.
                for jx in ixloop:
                    zipfilename = zipfilesnames_ERCOT_page[jx]
                    yearzip = zipfilename[-8:-4]
                    #print(yearzip)
                    urldown = urlERCOTdown_ini + zipfileslinks_ERCOT_page[jx]
                    des_dir = foldersave + folderprice[ixlp] + yearzip + "/"

                    #logging.info('ERCOTdownloader: Extracting to {0}'.format(des_dir))
                    #self.update_output_log('Extracting to {0}'.format(des_dir))

                    if not os.path.exists(des_dir):
                        os.makedirs(des_dir)

                    r = requests.get(urldown, timeout=10, proxies=proxy_settings, verify=ssl_verify)
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    z.extractall(des_dir)
            except IndexError as e:
                logging.error('ERCOTdownloader: An invalid year was provided. (got {0})'.format(year))
                self.thread_failed = True
            except requests.exceptions.ProxyError:
                logging.error('ERCOTdownloader: {0}: Could not connect to proxy.'.format(year))
                Clock.schedule_once(partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(year)), 0)
                self.thread_failed = True
            except socket.timeout:
                logging.error('ERCOTdownloader: The connection timed out.')
                self.update_output_log('The connection for downloading {year} data timed out.'.format(year=year))
                self.thread_failed = True
            except requests.HTTPError as e:
                logging.error('ERCOTdownloader: {0}: {1}'.format(year, repr(e)))
                Clock.schedule_once(partial(self.update_output_log, '{0}: HTTPError: {1}'.format(year, e.response.status_code)), 0)
                self.thread_failed = True
            except requests.ConnectionError as e:
                logging.error('ERCOTdownloader: {0}: Failed to establish a connection to the host server.'.format(year))
                Clock.schedule_once(partial(self.update_output_log, '{0}: Failed to establish a connection to the host server.'.format(year)), 0)
                self.thread_failed = True
            except requests.Timeout as e:
                logging.error('ERCOTdownloader: {0}: The connection timed out.'.format(year))
                Clock.schedule_once(partial(self.update_output_log, '{0}: The connection timed out.'.format(year)), 0)
                self.thread_failed = True
            except requests.RequestException as e:
                logging.error('ERCOTdownloader: {0}: {1}'.format(year, repr(e)))
                self.thread_failed = True
            except Exception as e:
                # Something else went wrong.
                logging.error('ERCOTdownloader: {0}: An unexpected error has occurred. ({1})'.format(year, repr(e)))
                Clock.schedule_once(partial(self.update_output_log, '{0}: An unexpected error has occurred. ({1})'.format(year, repr(e))), 0)
                self.thread_failed = True
            else:
                logging.info('ERCOTdownloader: {0} data successfully downloaded and extracted.'.format(year))
            finally:
                Clock.schedule_once(self.increment_progress_bar, 0)

                # Quit?
                if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                    # Stop running this thread so the main Python process can exit.
                    self.n_active_threads -= 1
                    return
            
        self.n_active_threads -= 1


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

            # Spawn a new thread for each download_ISONE_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_ISONE_data, args=(acc_user, acc_pw, batch[0], batch[-1]),
                                                     kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings, 'nodes':nodes_selected})

                thread_downloader.start()

    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
    def _download_ISONE_data(self, username, password, datetime_start, datetime_end=None, nodes=[], typedat="all", path='data/', ssl_verify=True, proxy_settings={}):
        """Downloads a month's worth of ISO-NE day ahead LMP and RCP data pre Dec 2017. Post Dec 2017 downloads da LMP, five minute LMP, and five minute RCP data.
    
        :param username: ISO-NE ISO Express username
        :type username: str
        :param password: ISO-NE ISO Express password
        :type password: str
        :param nodes: list of pricing nodes
        :type nodes: list
        :param datetime_start: the start of the range of data to download
        :type datetime_start: datetime
        :param datetime_end: the end of the range of data to download, defaults to one month's worth
        :type datetime_end: datetime
        :param path: root directory of data download location, defaults to os.path.join('data')
        :param path: str, optional
        :param ssl_verify: if SSL verification should be done, defaults to True
        :param ssl_verify: bool, optional
        """
        
        mileage_dir = os.path.join(path, 'ISONE')
        if not os.path.exists(mileage_dir):
            os.makedirs(mileage_dir, exist_ok = True)
        mileage_file = os.path.join(mileage_dir, 'MileageFile.xlsx')    
        mileage_url = 'https://www.iso-ne.com/static-assets/documents/2014/10/Energy_Neutral_AGC_Dispatch.xlsx'
        
        if not os.path.exists(mileage_file):
            mileage_request = requests.get(mileage_url, proxies=proxy_settings, timeout=6, verify=ssl_verify, stream=True)
            with open(mileage_file, 'wb') as f:
                f.write(mileage_request.content)
        
        
        print("Max attempts:" + str(MAX_WHILE_ATTEMPTS))
        if not datetime_end:
            datetime_end = datetime_start
    
        pathlistnodes = path
        static_dir = os.path.join(dirname, "es_gui", 'apps', 'data_manager', '_static')
        listnodes_file = os.path.join(pathlistnodes, static_dir, 'nodes_isone.csv')
        
        if not nodes:
            df_listnodes = pd.read_csv(listnodes_file, index_col=False,encoding="cp1252")
            nodelist = df_listnodes['Node ID']
        else:
            nodelist = []
            for node_x in nodes:
                if node_x == 'HUBS':
                    df_listnodes = pd.read_csv(listnodes_file, index_col=False, encoding="cp1252")
                    ixzones = df_listnodes['Node ID'] == df_listnodes['Zone ID']
                    zonelist = df_listnodes.loc[ixzones, 'Node ID'].tolist()
                    nodelist = nodelist + zonelist
                else:
                    nodelist.append(node_x)
    
    
        #	set datetime when five minute data starts
        five_minute_start = datetime.datetime(2017, 12, 1)
    
        
        # Compute the range of months to get da prices
        monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')
    
        url_ISONE = 'https://webservices.iso-ne.com/api/v1.1'
        for date in monthrange:
            _, n_days_month = calendar.monthrange(date.year, date.month)
            
            case_dwn = ['lmp', 'rcp', 'fmlmp', 'fmrcp']
            folderdata = ['LMP', 'RCP', 'LMP', 'RCP']
            lmp_or_rcp_nam = ['_dalmp_', '_rcp', '_fmlmp_', '_fmrcp']
            nodelist_dict = {
                    'lmp'   : nodelist,
                    'rcp'   : [''],
                    'fmlmp' : nodelist,
                    'fmrcp' : ['']
                    }
            
            if date < five_minute_start:
                case_dwn.remove('fmlmp')
                case_dwn.remove('fmrcp')
                folderdata.remove('LMP')
                folderdata.remove('RCP')
                lmp_or_rcp_nam.remove('_fmlmp_')
                lmp_or_rcp_nam.remove('_fmrcp')
                del nodelist_dict['fmlmp']
                del nodelist_dict['fmrcp']

                if typedat == 'lmp':
                    case_dwn.remove('rcp')
                    folderdata.remove('RCP')
                    lmp_or_rcp_nam.remove('_rcp')
                    del nodelist_dict['rcp']
                elif typedat == 'rcp':
                    case_dwn.remove('lmp')
                    folderdata.remove('LMP')
                    lmp_or_rcp_nam.remove('_dalmp_')
                    del nodelist_dict['lmp']
            elif date >= five_minute_start:
                case_dwn.remove('rcp')
                case_dwn.remove('lmp')
                folderdata.remove('RCP')
                folderdata.remove('LMP')
                lmp_or_rcp_nam.remove('_rcp')
                lmp_or_rcp_nam.remove('_dalmp_')
                del nodelist_dict['rcp']
                del nodelist_dict['lmp']
                    
                if typedat == 'lmp':
                    case_dwn.remove('fmrcp')
                    folderdata.remove('RCP')
                    lmp_or_rcp_nam.remove('_fmrcp')
                    del nodelist_dict['fmrcp']
                elif typedat == 'rcp':
                    case_dwn.remove('fmlmp')
                    folderdata.remove('LMP')
                    lmp_or_rcp_nam.remove('_fmlmp_')
                    del nodelist_dict['fmlmp']
    
            for sx, case_dwn_x in enumerate(case_dwn):
                nodelist_loop = nodelist_dict[case_dwn_x]
                for node_x in nodelist_loop:
                    nodex = node_x
                    if isinstance(node_x, int):
                        nodex = str(node_x)
    
                    destination_dir = os.path.join(path,'ISONE', folderdata[sx], nodex, date.strftime('%Y'))
                    destination_file = os.path.join(destination_dir, ''.join([date.strftime('%Y%m'), lmp_or_rcp_nam[sx], nodex, ".csv"]))
    
                    date_Ym_str = date.strftime('%Y%m')
                    if not os.path.exists(destination_file):
    
                        data_down_month = []
                        dwn_ok = True
                        for day in range(1,n_days_month+1):
                            # Quit?
                            if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                                # Stop running this thread so the main Python process can exit.
                                self.n_active_threads -= 1
                                return

                            date_str = date.strftime('%Y%m') + str(day).zfill(2)
                            if case_dwn_x == 'lmp':
                                datadownload_url = ''.join([url_ISONE, '/hourlylmp/da/final/day/', date_str, '/location/', str(nodex),'.json'])
                            elif case_dwn_x == 'rcp':
                                datadownload_url = ''.join([url_ISONE, '/hourlyrcp/final/day/', date_str,'.json'])
                            elif case_dwn_x == 'fmlmp':
                                datadownload_url = ''.join([url_ISONE, '/fiveminutelmp/prelim/day/', date_str, '/location/', str(nodex),'.json'])
                            elif case_dwn_x == 'fmrcp':
                                datadownload_url = ''.join([url_ISONE, '/fiveminutercp/prelim/day/', date_str, '.json'])
                            print(datadownload_url)
    
                            trydownloaddate = True
                            wx = 0
    
                            if not dwn_ok:
                                print("Month download failed")
                                break
                            while trydownloaddate:
                                wx = wx + 1
                                if wx >= MAX_WHILE_ATTEMPTS:
                                    print("Hit wx limit")
                                    dwn_ok = False
                                    trydownloaddate = False
                                    break
    
                                try:
                                    with requests.Session() as req:
                                        http_request = req.get(datadownload_url, auth=(username, password), proxies=proxy_settings, timeout=6, verify=ssl_verify, stream=True)
    
                                        if http_request.status_code == requests.codes.ok:
                                            trydownloaddate = False
                                            self.thread_failed = False
                                        else:
                                            http_request.raise_for_status()
    
                                except requests.HTTPError as e:
                                    logging.error('ISONEdownloader: {0}: {1}'.format(date_str, repr(e)))
                                    Clock.schedule_once(partial(self.update_output_log,
                                                                '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
                                    if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                        self.thread_failed = True
                                except requests.exceptions.ProxyError:
                                    logging.error('ISONEdownloader: {0}: Could not connect to proxy.'.format(date_str))
                                    Clock.schedule_once(
                                        partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
                                    if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                        self.thread_failed = True
                                except requests.ConnectionError as e:
                                    logging.error(
                                        'ISONEdownloader: {0}: Failed to establish a connection to the host server.'.format(
                                            date_str))
                                    Clock.schedule_once(partial(self.update_output_log,
                                                                '{0}: Failed to establish a connection to the host server.'.format(
                                                                    date_str)), 0)
                                    if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                        self.thread_failed = True
                                except requests.Timeout as e:
                                    trydownloaddate = True
                                    logging.error('ISONEdownloader: {0}: The connection timed out.'.format(date_str))
                                    Clock.schedule_once(
                                        partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
                                    if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                        self.thread_failed = True
                                except requests.RequestException as e:
                                    logging.error('ISONEdownloader: {0}: {1}'.format(date_str, repr(e)))
                                    if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                        self.thread_failed = True
                                except Exception as e:
                                    # Something else went wrong.
                                    logging.error(
                                        'ISONEdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                               repr(e)))
                                    Clock.schedule_once(partial(self.update_output_log,
                                                                '{0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                                      repr(e))), 0)
                                    if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                        self.thread_failed = True
                                else:
                                    data_down = []
                                    if case_dwn_x == 'lmp':
                                        try:
                                            data_down = http_request.json()['HourlyLmps']['HourlyLmp']
                                        except TypeError:
                                            logging.error('ISONEdownloader: {0} {1}: No data returned.'.format(date_str, case_dwn_x))
                                            Clock.schedule_once(partial(self.update_output_log, '{0}: No data returned.'.format(date_str)), 0)
                                            
                                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                                self.thread_failed = True
                                            dwn_ok = False
                                            break
                                    elif case_dwn_x == 'rcp':
                                        try:
                                            data_down = http_request.json()['HourlyRcps']['HourlyRcp']
                                        except TypeError:
                                            logging.error('ISONEdownloader: {0} {1}: No data returned.'.format(date_str, case_dwn_x))
                                            Clock.schedule_once(partial(self.update_output_log, '{0}: No data returned.'.format(date_str)), 0)
                                            
                                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                                self.thread_failed = True
                                            dwn_ok = False
                                            break
                                    elif case_dwn_x == 'fmlmp':
                                        try:
                                            data_down = http_request.json()['FiveMinLmps']['FiveMinLmp']
                                        except TypeError:
                                            logging.error('ISONEdownloader: {0} {1}: No data returned.'.format(date_str, case_dwn_x))
                                            Clock.schedule_once(partial(self.update_output_log, '{0}: No data returned.'.format(date_str)), 0)
                                            
                                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                                self.thread_failed = True
                                            dwn_ok = False
                                            break
                                    elif case_dwn_x == 'fmrcp':
                                        try:
                                            data_down = http_request.json()['FiveMinRcps']['FiveMinRcp']
                                        except TypeError:
                                            logging.error('ISONEdownloader: {0} {1}: No data returned.'.format(date_str, case_dwn_x))
                                            Clock.schedule_once(partial(self.update_output_log, '{0}: No data returned.'.format(date_str)), 0)
                                            
                                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                                self.thread_failed = True
                                            dwn_ok = False
                                            break
                                    data_down_month += data_down
    
                        if dwn_ok:
                            print("Successful ISONE data download")
                            df_data = pd.DataFrame.from_records(data_down_month)
                            if case_dwn_x == 'lmp':
                                df_save = df_data.drop(['Location'], axis = 1).set_index('BeginDate')
                            elif case_dwn_x == 'rcp':
                                df_save = df_data.drop(['HourEnd'], axis = 1).set_index('BeginDate')
                            elif case_dwn_x == 'fmlmp':
                                df_data.drop(['Location'], inplace=True, axis=1)
                                df_data.set_index('BeginDate', inplace=True)
                                hours = [i for i in range(len(df_data.index)//12)]
                                df_save = pd.DataFrame(columns = df_data.columns)
                                for hour in hours:
                                    df_temp = df_data[12*hour:12*(hour + 1)].mean()
                                    df_save = df_save.append(df_temp, ignore_index = True)
                            elif case_dwn_x == 'fmrcp':
                                df_data.drop(['HourEnd'], inplace=True, axis=1)
                                df_data.set_index('BeginDate', inplace=True)
                                hours = [i for i in range(len(df_data.index)//12)]
                                df_save = pd.DataFrame(columns = df_data.columns)
                                for hour in hours:
                                    df_temp = df_data[12*hour:12*(hour + 1)].mean()
                                    df_save = df_save.append(df_temp, ignore_index = True)

                            os.makedirs(destination_dir, exist_ok=True)
                            df_save.to_csv(destination_file, index = False)
                            
    
                    else:
                        # Skip downloading the daily file if it already exists where expected.
                        logging.info('ISONEdownloader: {0}: {1} file already exists, skipping...'.format(date_Ym_str, case_dwn[sx]))
                        print('ISONEdownloader: {0}: {1} file already exists, skipping...'.format(date_Ym_str, case_dwn[sx]))
                        
                    Clock.schedule_once(self.increment_progress_bar, 0)
                    # Quit?
                    if App.get_running_app().root.stop.is_set():
                        # Stop running this thread so the main Python process can exit.
                        self.n_active_threads -= 1
                        return
                
        self.n_active_threads -= 1
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#


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

            # Spawn a new thread for each download_MISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_MISO_data, 
                args=(batch[0], batch[-1]),
                kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings})
                thread_downloader.start()
    
    def _download_MISO_data(self, datetime_start, datetime_end=None, path='data', ssl_verify=True, proxy_settings=None):
        """Downloads a range of monthly MISO day ahead LMP and MCP data.
        
        :param datetime_start: the start of the range of data to download
        :type datetime_start: datetime
        :param datetime_end: the end of the range of data to download, defaults to one month's worth
        :type datetime_end: datetime
        :param path: root directory of data download location, defaults to 'data'
        :param path: str, optional
        :param ssl_verify: if SSL verification should be done, defaults to True
        :param ssl_verify: bool, optional
        :param proxy_settings: dictionary of proxy settings, defaults to None
        :param proxy_settings: dict, optional
        """

        if not datetime_end:
            datetime_end = datetime_start

        # Compute the range of months to iterate over.
        monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')

        for date in monthrange:
            year = date.year
            month = date.month

            # Compute the range of days to iterate over.
            _, n_days_month = calendar.monthrange(year, month)

            for day in [x+1 for x in range(n_days_month)]:
                # Quit?
                if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                    # Stop running this thread so the main Python process can exit.
                    self.n_active_threads -= 1
                    return

                date = dt.date(year, month, day)
                date_str = date.strftime('%Y%m%d')

                # LMP call.
                lmp_url = ''.join(['https://docs.misoenergy.org/marketreports/', date_str, '_da_exante_lmp.csv'])
                destination_dir = os.path.join(path, 'MISO', 'LMP', date.strftime('%Y'), date.strftime('%m'))
                destination_file = os.path.join(destination_dir, '_'.join([date_str, 'da_exante_lmp.csv']))

                if os.path.exists(destination_file):
                    # Skip downloading the daily file if it already exists where expected.
                    logging.info('MISOdownloader: {0}: LMP file already exists, skipping...'.format(date_str))
                else:
                    try:
                        with requests.Session() as s:
                            http_request = s.get(lmp_url, stream=True, proxies=proxy_settings, verify=ssl_verify)
                        
                        # Check the HTTP status code.
                        if http_request.status_code == requests.codes.ok:
                            data = http_request.content.decode('utf-8')
                        else:
                            http_request.raise_for_status()
                    except requests.HTTPError as e:
                        logging.error('MISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
                        self.thread_failed = True
                    except requests.ConnectionError as e:
                        logging.error('MISOdownloader: {0}: Failed to establish a connection to the host server.'.format(date_str))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: Failed to establish a connection to the host server.'.format(date_str)), 0)
                        self.thread_failed = True
                    except requests.Timeout as e:
                        logging.error('MISOdownloader: {0}: The connection timed out.'.format(date_str))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
                        self.thread_failed = True
                    except requests.RequestException as e:
                        logging.error('MISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                        self.thread_failed = True
                    except Exception as e:
                        # Something else went wrong.
                        logging.error('MISOdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e)))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))), 0)
                        self.thread_failed = True
                    else:
                        os.makedirs(destination_dir, exist_ok=True)
                        output_file = open(destination_file, 'w')
                        output_file.write(data)
                        output_file.close()

                Clock.schedule_once(self.increment_progress_bar, 0)
                
                # MCP call.
                mcp_url = ''.join(['https://docs.misoenergy.org/marketreports/', date_str, '_asm_exante_damcp.csv'])
                destination_dir = os.path.join(path, 'MISO', 'MCP', date.strftime('%Y'), date.strftime('%m'))
                destination_file = os.path.join(destination_dir, '_'.join([date_str, 'asm_exante_damcp.csv']))

                if os.path.exists(destination_file):
                    # Skip downloading the daily file if it already exists where expected.
                    logging.info('MISOdownloader: {0}: MCP file already exists, skipping...'.format(date_str))
                else:
                    try:
                        with requests.Session() as s:
                            http_request = s.get(mcp_url, stream=True, proxies=proxy_settings, verify=ssl_verify)
                        
                        # Check the HTTP status code.
                        if http_request.status_code == requests.codes.ok:
                            data = http_request.content.decode('utf-8')
                        else:
                            http_request.raise_for_status()
                    except requests.HTTPError as e:
                        logging.error('MISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: HTTPError: {1}'.format(date_str, e.response.status_code), 0))
                        self.thread_failed = True
                    except requests.exceptions.ProxyError:
                        logging.error('MISOdownloader: {0}: Could not connect to proxy.'.format(date_str))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
                        self.thread_failed = True
                    except requests.ConnectionError as e:
                        logging.error('MISOdownloader: {0}: Failed to establish a connection to the host server.'.format(date_str))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: Failed to establish a connection to the host server.'.format(date_str)), 0)
                        self.thread_failed = True
                    except requests.Timeout as e:
                        logging.error('MISOdownloader: {0}: The connection timed out.'.format(date_str))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
                        self.thread_failed = True
                    except requests.RequestException as e:
                        logging.error('MISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                        self.thread_failed = True
                    except Exception as e:
                        # Something else went wrong.
                        logging.error('MISOdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e)))
                        Clock.schedule_once(partial(self.update_output_log, '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))), 0)
                        self.thread_failed = True
                    else:
                        os.makedirs(destination_dir, exist_ok=True)
                        output_file = open(destination_file, 'w')
                        output_file.write(data)
                        output_file.close()
                
                Clock.schedule_once(self.increment_progress_bar, 0)

        self.n_active_threads -= 1


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

            # Spawn a new thread for each download_NYISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_NYISO_data,
                                                     args=(batch[0], batch[-1]),
                                                     kwargs={'ssl_verify': ssl_verify,
                                                             'proxy_settings': proxy_settings, 
                                                             'zone_gen': nodes_selected,
                                                             'RT_DAM': 'DAM'})

                thread_downloader.start()

    def _download_NYISO_data(self, datetime_start, datetime_end=None, typedat="both", RT_DAM="both", zone_gen="both",
                            path='data', ssl_verify=True, proxy_settings=None):
        """Downloads a range of monthly NYISO day ahead LBMP and ASP data.

        :param datetime_start: the start of the range of data to download
        :type datetime_start: datetime
        :param datetime_end: the end of the range of data to download, defaults to one month's worth
        :type datetime_end: datetime
        :param typedat: download ASP data, LBMP data, or both, defaults to 'both'
        :type typedat: str
        :param RT_DAM: download real time or day ahead data, defaults to 'both'
        :type RT_DAM: str
        :param zone_gen: download LBMP data for zones or gens, defaults to 'both'
        :type zone_gen: str
        :param path: root directory of data download location, defaults to 'data'
        :param path: str, optional
        :param ssl_verify: if SSL verification should be done, defaults to True
        :param ssl_verify: bool, optional
        :param proxy_settings: dictionary of proxy settings, defaults to None
        :param proxy_settings: dict, optional
        """
        if not datetime_end:
            datetime_end = datetime_start

        # Compute the range of months to iterate over.
        monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')

        # Note NYISO has .zip files with months

        # ASP
        zone_or_gen_ASP_nam = []
        zone_or_gen_ASP_folder = []
        dam_or_rt_ASP_folder = []
        dam_or_rt_ASP_nam = []
        if RT_DAM == "RT":
            zone_or_gen_ASP_nam.append("")
            zone_or_gen_ASP_folder.append("")
            dam_or_rt_ASP_nam.append("rtasp")
            dam_or_rt_ASP_folder.append("RT")
        elif RT_DAM == "DAM":
            zone_or_gen_ASP_nam.append("")
            zone_or_gen_ASP_folder.append("")
            dam_or_rt_ASP_nam.append("damasp")
            dam_or_rt_ASP_folder.append("DAM")
        elif RT_DAM == "both":
            zone_or_gen_ASP_nam.append("")
            zone_or_gen_ASP_nam.append("")
            zone_or_gen_ASP_folder.append("")
            zone_or_gen_ASP_folder.append("")
            dam_or_rt_ASP_nam.append("rtasp")
            dam_or_rt_ASP_nam.append("damasp")
            dam_or_rt_ASP_folder.append("RT")
            dam_or_rt_ASP_folder.append("DAM")

        # LBMP
        zone_or_gen_LBMP_nam = []
        zone_or_gen_LBMP_folder = []
        dam_or_rt_LBMP_folder = []
        dam_or_rt_LBMP_nam = []
        if zone_gen == 'zone' or zone_gen == 'both':
            if RT_DAM == "RT":
                dam_or_rt_LBMP_nam.append("realtime")
                dam_or_rt_LBMP_folder.append("RT")
                zone_or_gen_LBMP_nam.append("_zone")
                zone_or_gen_LBMP_folder.append("zone")
            elif RT_DAM == "DAM":
                dam_or_rt_LBMP_nam.append("damlbmp")
                dam_or_rt_LBMP_folder.append("DAM")
                zone_or_gen_LBMP_nam.append("_zone")
                zone_or_gen_LBMP_folder.append("zone")
            elif RT_DAM == "both":
                dam_or_rt_LBMP_nam.append("realtime")
                dam_or_rt_LBMP_nam.append("damlbmp")
                dam_or_rt_LBMP_folder.append("RT")
                dam_or_rt_LBMP_folder.append("DAM")
                zone_or_gen_LBMP_nam.append("_zone")
                zone_or_gen_LBMP_nam.append("_zone")
                zone_or_gen_LBMP_folder.append("zone")
                zone_or_gen_LBMP_folder.append("zone")

        if zone_gen == 'gen' or zone_gen == 'both':
            if RT_DAM == "RT":
                dam_or_rt_LBMP_nam.append("realtime")
                dam_or_rt_LBMP_folder.append("RT")
                zone_or_gen_LBMP_nam.append("_gen")
                zone_or_gen_LBMP_folder.append("gen")
            elif RT_DAM == "DAM":
                dam_or_rt_LBMP_nam.append("damlbmp")
                dam_or_rt_LBMP_folder.append("DAM")
                zone_or_gen_LBMP_nam.append("_gen")
                zone_or_gen_LBMP_folder.append("gen")
            elif RT_DAM == "both":
                dam_or_rt_LBMP_nam.append("realtime")
                dam_or_rt_LBMP_nam.append("damlbmp")
                dam_or_rt_LBMP_folder.append("RT")
                dam_or_rt_LBMP_folder.append("DAM")
                zone_or_gen_LBMP_nam.append("_gen")
                zone_or_gen_LBMP_nam.append("_gen")
                zone_or_gen_LBMP_folder.append("gen")
                zone_or_gen_LBMP_folder.append("gen")

        zone_or_gen_nam = []
        zone_or_gen_folder = []
        dam_or_rt_nam = []
        dam_or_rt_folder = []
        lbmp_or_asp_folder = []
        if typedat == "asp":
            zone_or_gen_nam = zone_or_gen_ASP_nam
            zone_or_gen_folder = zone_or_gen_ASP_folder
            dam_or_rt_folder = dam_or_rt_ASP_folder
            dam_or_rt_nam = dam_or_rt_ASP_nam
            lbmp_or_asp_folder = ["ASP"] * len(dam_or_rt_ASP_nam)
        elif typedat == "lbmp":
            zone_or_gen_nam = zone_or_gen_LBMP_nam
            zone_or_gen_folder = zone_or_gen_LBMP_folder
            dam_or_rt_folder = dam_or_rt_LBMP_folder
            dam_or_rt_nam = dam_or_rt_LBMP_nam
            lbmp_or_asp_folder = ["LBMP"] * len(dam_or_rt_LBMP_nam)
        elif typedat == "both":
            zone_or_gen_nam = zone_or_gen_ASP_nam + zone_or_gen_LBMP_nam
            zone_or_gen_folder = zone_or_gen_ASP_folder + zone_or_gen_LBMP_folder
            dam_or_rt_folder = dam_or_rt_ASP_folder + dam_or_rt_LBMP_folder
            dam_or_rt_nam = dam_or_rt_ASP_nam + dam_or_rt_LBMP_nam
            lbmp_or_asp_folder = ["ASP"] * len(dam_or_rt_ASP_nam) + ["LBMP"] * len(dam_or_rt_LBMP_nam)

        for date in monthrange:
            date_str = date.strftime('%Y%m')

            for sx, dam_or_rt_nam_x in enumerate(dam_or_rt_nam):

                # Data download call.
                # datadownload_url = url_NYISO + dam_or_rt_nam_x + "/" + date_str + "01" + dam_or_rt_nam_x + zone_or_gen_nam[sx] + "_csv.zip"
                datadownload_url = ''.join(
                    ['http://mis.nyiso.com/public/csv/', dam_or_rt_nam_x, '/', date_str, '01', dam_or_rt_nam_x,
                     zone_or_gen_nam[sx], "_csv.zip"])
                destination_dir = os.path.join(path, 'NYISO', lbmp_or_asp_folder[sx], dam_or_rt_folder[sx],
                                               zone_or_gen_folder[sx], date.strftime('%Y'), date.strftime('%m'))
                first_name_file = os.path.join(destination_dir,
                                               ''.join([date_str, '01', dam_or_rt_nam_x, zone_or_gen_nam[sx], '.csv']))
                # print(datadownload_url)

                if not os.path.exists(first_name_file):
                    trydownloaddate = True
                    wx = 0
                    while trydownloaddate:
                        # Quit?
                        if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                            # Stop running this thread so the main Python process can exit.
                            self.n_active_threads -= 1
                            return

                        wx = wx + 1
                        if wx >= MAX_WHILE_ATTEMPTS:
                            logging.warning('NYISOdownloader: {0} {1}: Hit download retry limit.'.format(date_str, lbmp_or_asp_folder[sx]))
                            Clock.schedule_once(partial(self.update_output_log, '{0} {1}: Hit download retry limit.'.format(date_str, lbmp_or_asp_folder[sx])), 0)
                            trydownloaddate = False
                            break
                        
                        try:
                            with requests.Session() as req:
                                http_request = req.get(datadownload_url, proxies=proxy_settings, timeout=6,
                                                       verify=ssl_verify, stream=True)

                            if http_request.status_code == requests.codes.ok:
                                trydownloaddate = False
                            else:
                                http_request.raise_for_status()
                        except requests.HTTPError as e:
                            logging.error('NYISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                            Clock.schedule_once(partial(self.update_output_log,
                                                        '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                self.thread_failed = True
                        except requests.exceptions.ProxyError:
                            logging.error('NYISOdownloader: {0}: Could not connect to proxy.'.format(date_str))
                            # Clock.schedule_once(
                            #     partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                self.thread_failed = True
                        except requests.ConnectionError as e:
                            logging.error(
                                'NYISOdownloader: {0}: Failed to establish a connection to the host server.'.format(
                                    date_str))
                            # Clock.schedule_once(partial(self.update_output_log,
                            #                             '{0}: Failed to establish a connection to the host server.'.format(
                            #                                 date_str)), 0)
                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                self.thread_failed = True
                        except requests.Timeout as e:
                            trydownloaddate = True
                            logging.error('NYISOdownloader: {0}: The connection timed out.'.format(date_str))
                            Clock.schedule_once(
                                partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                self.thread_failed = True
                        except requests.RequestException as e:
                            logging.error('NYISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                self.thread_failed = True
                        except Exception as e:
                            # Something else went wrong.
                            logging.error(
                                'NYISOdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                       repr(e)))
                            Clock.schedule_once(partial(self.update_output_log,
                                                        '{0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                              repr(e))), 0)
                            if wx >= (MAX_WHILE_ATTEMPTS - 1):
                                self.thread_failed = True
                        else:
                            os.makedirs(destination_dir, exist_ok=True)
                            z = zipfile.ZipFile(io.BytesIO(http_request.content))
                            z.extractall(destination_dir)
                else:
                    # Skip downloading the daily file if it already exists where expected.
                    logging.info('NYISOdownloader: {0}: {1} file already exists, skipping...'.format(date_str,
                                                                                                     lbmp_or_asp_folder[
                                                                                                         sx]))
                    self.update_output_log('{0}: {1} file already exists, skipping...'.format(date_str, lbmp_or_asp_folder[sx]))

                # Increment progress bar.
                Clock.schedule_once(self.increment_progress_bar, 0)

                # Quit?
                if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                    # Stop running this thread so the main Python process can exit.
                    self.n_active_threads -= 1
                    return

        self.n_active_threads -= 1


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

            # Spawn a new thread for each download_SPP_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_SPP_data, args=(batch[0], batch[-1]),
                                                     kwargs={'ssl_verify': ssl_verify,
                                                             'proxy_settings': proxy_settings,
                                                             'bus_loc': nodes_selected})

                thread_downloader.start()

    def _download_SPP_data(self, datetime_start, datetime_end=None, typedat="all", bus_loc="both", path='data/',
                          ssl_verify=True, proxy_settings=None):
        """Downloads a month's worth of SPP day ahead LMP and MCP data.

        :param datetime_start: the start of the range of data to download
        :type datetime_start: datetime
        :param datetime_end: the end of the range of data to download, defaults to one month's worth
        :type datetime_end: datetime
        :param path: root directory of data download location, defaults to os.path.join('data')
        :param path: str, optional
        :param ssl_verify: if SSL verification should be done, defaults to True
        :param ssl_verify: bool, optional
        """

        # Valid for SPP data starting on Jan 2014. SPP shares data starting May/June 2013 but it is completely disorganized in certain parts

        # print("Max attempts:" + str(MAX_WHILE_ATTEMPTS))
        if not datetime_end:
            datetime_end = datetime_start

        # Compute the range of months to iterate over.
        monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')

        url_spp_daLMP = "https://marketplace.spp.org/file-browser-api/download/da-lmp-by-"
        url_spp_daMCP = "https://marketplace.spp.org/file-browser-api/download/da-mcp"

        foldercompl_da = ['By_Day%2F', '']

        # MCP
        bus_or_loc_MCP_nam = []
        bus_or_loc_MCP_folder = []
        case_MCP_URL = []

        bus_or_loc_MCP_nam.append("")
        bus_or_loc_MCP_folder.append("")
        case_MCP_URL.append(url_spp_daMCP)

        # LMP
        bus_or_loc_LMP_nam = []
        bus_or_loc_LMP_folder = []
        case_LMP_URL = []
        if bus_loc == 'bus' or bus_loc == 'both':
            bus_or_loc_LMP_nam.append('B')
            bus_or_loc_LMP_folder.append("bus")
            case_LMP_URL.append(url_spp_daLMP)

        if bus_loc == 'location' or bus_loc == 'both':
            bus_or_loc_LMP_nam.append('SL')
            bus_or_loc_LMP_folder.append("location")
            case_LMP_URL.append(url_spp_daLMP)

        bus_or_loc_nam = []
        bus_or_loc_folder = []
        lmp_or_mpc_folder = []
        case_URL = []
        if typedat == "mcp":
            bus_or_loc_nam = bus_or_loc_MCP_nam
            bus_or_loc_folder = bus_or_loc_MCP_folder
            lmp_or_mpc_folder = ["MCP"] * len(case_MCP_URL)
            case_URL = case_MCP_URL
        elif typedat == "lmp":
            bus_or_loc_nam = bus_or_loc_LMP_nam
            bus_or_loc_folder = bus_or_loc_LMP_folder
            lmp_or_mpc_folder = ["LMP"] * len(case_LMP_URL)
            case_URL = case_LMP_URL
        elif typedat == "all":
            bus_or_loc_nam = bus_or_loc_MCP_nam + bus_or_loc_LMP_nam + [""]
            bus_or_loc_folder = bus_or_loc_MCP_folder + bus_or_loc_LMP_folder + [""]
            lmp_or_mpc_folder = ["MCP"] * len(case_MCP_URL) + ["LMP"] * len(case_LMP_URL)
            case_URL = case_MCP_URL + case_LMP_URL

        for sx, case_URL_x in enumerate(case_URL):
            for date in monthrange:
                _, n_days_month = calendar.monthrange(date.year, date.month)

                for day in range(1, n_days_month + 1):
                    date_str = date.strftime('%Y%m') + str(day).zfill(2)
                    destination_dir = os.path.join(path, 'SPP', lmp_or_mpc_folder[sx], 'DAM', bus_or_loc_folder[sx],
                                                   date.strftime('%Y'), date.strftime('%m'))

                    if lmp_or_mpc_folder[sx] == "LMP":
                        name_file = "DA-LMP-{0:s}-{1:d}{2:02d}{3:02d}0100.csv".format(bus_or_loc_nam[sx], date.year,
                                                                                      date.month, day)
                        URL_compl = "?path=%2F{0:d}%2F{1:02d}%2F{2:s}".format(date.year, date.month, foldercompl_da[0])

                    elif lmp_or_mpc_folder[sx] == "MCP":
                        name_file = "DA-MCP-{0:d}{1:02d}{2:02d}0100.csv".format(date.year, date.month, day)
                        URL_compl = "?path=%2F{0:d}%2F{1:02d}%2F".format(date.year, date.month)

                    destination_file = os.path.join(destination_dir, name_file)
                    datadownload_url = ''.join([case_URL_x, bus_or_loc_folder[sx], URL_compl, name_file])

                    if not os.path.exists(destination_file):

                        #print(datadownload_url)

                        trydownloaddate = True
                        wx = 0
                        while trydownloaddate:
                            # Quit?
                            if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                                # Stop running this thread so the main Python process can exit.
                                self.n_active_threads -= 1
                                return

                            wx = wx + 1
                            if wx >= MAX_WHILE_ATTEMPTS:
                                logging.warning('SPPdownloader: {0} {1}: Hit download retry limit.'.format(date_str, lmp_or_mpc_folder[sx]))
                                Clock.schedule_once(partial(self.update_output_log,
                                                            '{0} {1}: Hit download retry limit'.format(date_str, lmp_or_mpc_folder[sx])), 0)

                                print("Hit wx limit")
                                trydownloaddate = False
                                break

                            try:
                                with requests.Session() as req:
                                    http_request = req.get(datadownload_url, proxies=proxy_settings, timeout=6,
                                                           verify=ssl_verify, stream=True)

                                http_request_f = http_request
                                if http_request.status_code == requests.codes.ok:
                                    trydownloaddate = False
                                    # self.thread_failed = False
                                elif http_request.status_code == 406:
                                    # Try again!
                                    if lmp_or_mpc_folder[sx] == "LMP":
                                        name_file = "DA-LMP-{0:s}-{1:d}{2:02d}{3:02d}0100.csv".format(bus_or_loc_nam[sx], date.year, date.month, day)
                                        URL_compl = "?path=%2F{0:d}%2F{1:02d}%2F{2:s}".format(date.year, date.month, foldercompl_da[1])
                                    datadownload_url = ''.join(
                                        [case_URL_x, bus_or_loc_folder[sx], URL_compl, name_file])
                                    # print(datadownload_url)
                                    # print('Try LMP again!!!')
                                    with requests.Session() as req:
                                        http_request2 = req.get(datadownload_url, proxies=proxy_settings, timeout=6,
                                                                verify=ssl_verify, stream=True)
                                    if http_request2.status_code == requests.codes.ok:
                                        trydownloaddate = False
                                        foldercompl_aux = foldercompl_da[1]
                                        foldercompl_da[1] = foldercompl_da[0]
                                        foldercompl_da[0] = foldercompl_aux
                                        http_request_f = http_request2
                                    elif http_request.status_code == 406:
                                        trydownloaddate = False
                                        http_request.raise_for_status()
                                        http_request2.raise_for_status()
                                    else:
                                        http_request.raise_for_status()
                                        http_request2.raise_for_status()
                                else:
                                    http_request.raise_for_status()

                            except requests.HTTPError as e:
                                logging.error('SPPdownloader: {0}: {1}'.format(date_str, repr(e)))
                                Clock.schedule_once(partial(self.update_output_log,
                                                            '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
                                if wx >= (MAX_WHILE_ATTEMPTS-1):
                                    self.thread_failed = True
                            except requests.exceptions.ProxyError:
                                logging.error('SPPdownloader: {0}: Could not connect to proxy.'.format(date_str))
                                Clock.schedule_once(
                                    partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
                                if wx >= (MAX_WHILE_ATTEMPTS-1):
                                    self.thread_failed = True
                            except requests.ConnectionError as e:
                                logging.error(
                                    'SPPdownloader: {0}: Failed to establish a connection to the host server.'.format(
                                        date_str))
                                Clock.schedule_once(partial(self.update_output_log,
                                                            '{0}: Failed to establish a connection to the host server.'.format(date_str)), 0)
                                if wx >= (MAX_WHILE_ATTEMPTS-1):
                                    self.thread_failed = True
                            except requests.Timeout as e:
                                trydownloaddate = True
                                logging.error('SPPdownloader: {0}: The connection timed out.'.format(date_str))
                                Clock.schedule_once(
                                    partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
                                if wx >= (MAX_WHILE_ATTEMPTS-1):
                                    self.thread_failed = True
                            except requests.RequestException as e:
                                logging.error('SPPdownloader: {0}: {1}'.format(date_str, repr(e)))
                                if wx >= (MAX_WHILE_ATTEMPTS-1):
                                    self.thread_failed = True
                            except Exception as e:
                                # Something else went wrong.
                                logging.error(
                                    'SPPdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                         repr(e)))
                                Clock.schedule_once(partial(self.update_output_log,
                                                            '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))), 0)
                                if wx >= (MAX_WHILE_ATTEMPTS-1):
                                    self.thread_failed = True
                            
                            try:
                                urldata_str = http_request_f.content.decode('utf-8')
                            except NameError:
                                # http_request_f not yet defined
                                pass
                            except AttributeError:
                                # http_request_f not an object returned by requests.get()
                                pass
                            except requests.exceptions.ConnectionError:
                                # ConnectionError raised when decoding.
                                # See requests.models.response.iter_content()
                                pass
                            else:
                                if len(urldata_str) > 0:
                                    os.makedirs(destination_dir, exist_ok=True)
                                    output_file = open(destination_file, 'w')
                                    output_file.write(urldata_str)
                                    output_file.close()

                    else:
                        # Skip downloading the daily file if it already exists where expected.
                        logging.info('SPPdownloader: {0}: {1} file already exists, skipping...'.format(date_str, lmp_or_mpc_folder[sx]))
                        # print('SPPdownloader: {0}: {1} file already exists, skipping...'.format(date_str, lmp_or_mpc_folder[sx]))

                    Clock.schedule_once(self.increment_progress_bar, 0)

                    # Quit?
                    if App.get_running_app().root.stop.is_set():
                        # Stop running this thread so the main Python process can exit.
                        self.n_active_threads -= 1
                        return

        self.n_active_threads -= 1


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

            # Spawn a new thread for each download_CAISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_CAISO_data,
                                                     args=(batch[0], batch[-1]),
                                                     kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings,
                                                             'nodes': node_type_selected})

                thread_downloader.start()

    def _download_CAISO_data(self, datetime_start, datetime_end=None, typedat="all", nodes=[], path='data/',
                            ssl_verify=True, proxy_settings=None):
        """Downloads a month's worth of CAISO day ahead LMP, ASP and Mileage data.
        :param datetime_start: the start of the range of data to download
        :type datetime_start: datetime
        :param datetime_end: the end of the range of data to download, defaults to one month's worth
        :type datetime_end: datetime
        :param nodes: list of pricing nodes
        :type nodes: list
        :param path: root directory of data download location, defaults to os.path.join('data')
        :param path: str, optional
        :param ssl_verify: if SSL verification should be done, defaults to True
        :param ssl_verify: bool, optional
        """

        # print("Max attempts:" + str(MAX_WHILE_ATTEMPTS))
        if not datetime_end:
            datetime_end = datetime_start

        pathlistnodes = path
        static_dir = os.path.join(dirname, "es_gui", 'apps', 'data_manager', '_static')
        listnodes_file = os.path.join(pathlistnodes, static_dir, 'nodes_caiso.csv')
        if not nodes:
            df_listnodes = pd.read_csv(listnodes_file, index_col=False)
            nodelist = df_listnodes['Node ID']
        else:
            nodelist = []
            for node_x in nodes:
                if node_x == 'TH' or node_x == 'ASP':
                    df_listnodes = pd.read_csv(listnodes_file, index_col=False)
                    ixnodes_sel = df_listnodes['Node Type'] == node_x
                    selnodelist = df_listnodes.loc[ixnodes_sel, 'Node ID'].tolist()
                    nodelist = nodelist + selnodelist
                else:
                    nodelist.append(node_x)
        # print(nodelist)

        monthrange = pd.date_range(datetime_start, datetime_end, freq='1MS')

        url_CAISO = "http://oasis.caiso.com/oasisapi/SingleZip?"

        case_dwn = []
        folderdata = []

        if typedat == "all":
            folderdata.append("LMP")
            folderdata.append("ASP")
            folderdata.append("MILEAGE")
            case_dwn = ["lmp", "asp", "mileage"]
        elif typedat == "lmp":
            folderdata.append("LMP")
            case_dwn = ["lmp"]
        elif typedat == "asp":
            folderdata.append("ASP")
            case_dwn = ["asp"]
        elif typedat == "mileage":
            folderdata.append("MILEAGE")
            case_dwn = ["mileage"]

        for ixlp, case_dwn_x in enumerate(case_dwn):

            for date in monthrange:
                date_str = date.strftime('%Y%m')
                _, n_days_month = calendar.monthrange(date.year, date.month)

                GMT_PST_chunk = dt.timedelta(hours=7)
                day_chunk = dt.timedelta(hours=24)

                datetime_start_x = dt.datetime(date.year, date.month, 1)
                datetime_end_x = dt.datetime(date.year, date.month, n_days_month)
                date_start_x = datetime_start_x + GMT_PST_chunk
                date_end_x = datetime_end_x + GMT_PST_chunk + day_chunk

                pnode_look_list = ["n/a"]
                if case_dwn[ixlp] == "lmp":
                    pnode_look_list = nodelist

                for pnode_look in pnode_look_list:

                    log_identifier = '{date}, {pnode}, {dtype}'.format(date=date_str, dtype=case_dwn[ixlp],
                                                                       pnode=pnode_look)

                    nfilesave = "error.csv"
                    if case_dwn[ixlp] == "lmp":
                        destination_dir = os.path.join(path, 'CAISO', folderdata[ixlp], pnode_look, date.strftime('%Y'))
                        destination_file = os.path.join(destination_dir,
                                                        ''.join([date_str, "_dalmp_", pnode_look, ".csv"]))
                    elif case_dwn[ixlp] == "asp":
                        destination_dir = os.path.join(path, 'CAISO', folderdata[ixlp], date.strftime('%Y'))
                        destination_file = os.path.join(destination_dir, ''.join([date_str, "_asp.csv"]))
                    elif case_dwn[ixlp] == "mileage":
                        destination_dir = os.path.join(path, 'CAISO', folderdata[ixlp], date.strftime('%Y'))
                        destination_file = os.path.join(destination_dir, ''.join([date_str, "_regm.csv"]))

                    if not os.path.exists(destination_file):

                        if case_dwn[ixlp] == "asp":
                            dwn_ok = True
                            for dayx in range(n_days_month):
                                # Quit?
                                if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                                    # Stop running this thread so the main Python process can exit.
                                    self.n_active_threads -= 1
                                    return

                                log_identifier = '{date}, {pnode}, {dtype}'.format(date=date_str+str(dayx+1).zfill(2), dtype=case_dwn[ixlp], pnode=pnode_look)
                                datetime_start_loop = dt.datetime(date.year, date.month, dayx + 1)
                                date_start_loop = datetime_start_loop + GMT_PST_chunk
                                date_end_loop = datetime_start_loop + GMT_PST_chunk + day_chunk
                                """
                                Note that ancillary services prices can only be downloaded on a daily basis and that they
                                can't be controlled via T0XX
                                """
                                datesquery_start = "{0:d}{1:02d}{2:02d}T010:00-0000".format(date_start_loop.year,
                                                                                            date_start_loop.month,
                                                                                            date_start_loop.day)
                                datesquery_end = "{0:d}{1:02d}{2:02d}T010:00-0000".format(date_end_loop.year,
                                                                                          date_end_loop.month,
                                                                                          date_end_loop.day)

                                df_data_x, dwn_ok_x = self.ddownloader_CAISO(url_CAISO, case_dwn[ixlp], datesquery_start,
                                                                        datesquery_end, pnode_look, log_identifier,
                                                                        ssl_verify=ssl_verify,
                                                                        proxy_settings=proxy_settings)
                                dwn_ok = dwn_ok and dwn_ok_x
                                if dwn_ok:
                                    if dayx == 0:
                                        df_data = df_data_x
                                    else:
                                        df_data = pd.concat([df_data, df_data_x], ignore_index=True)
                                else:
                                    break

                        else:
                            # Quit?
                            if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                                # Stop running this thread so the main Python process can exit.
                                self.n_active_threads -= 1
                                return
                            if date_start_x.month == 3:
                                HTstart = 8
                                HTend = 7
                            elif date_start_x.month == 11:
                                HTstart = 7
                                HTend = 8
                            elif date_start_x.month >= 4 and date_start_x.month <= 10:
                                HTstart = 7
                                HTend = 7
                            else:
                                HTstart = 8
                                HTend = 8

                            datesquery_start = "{0:d}{1:02d}{2:02d}T{3:02d}:00-0000".format(date_start_x.year,
                                                                                            date_start_x.month,
                                                                                            date_start_x.day, HTstart)
                            datesquery_end = "{0:d}{1:02d}{2:02d}T{3:02d}:00-0000".format(date_end_x.year,
                                                                                          date_end_x.month,
                                                                                          date_end_x.day, HTend)

                            # datesquery_start = "{0:d}{1:02d}{2:02d}T07:00-0000".format(date_start_x.year,date_start_x.month,date_start_x.day)
                            # datesquery_end = "{0:d}{1:02d}{2:02d}T07:00-0000".format(date_end_x.year, date_end_x.month,date_end_x.day)

                            # If January or December... do things differently
                            if date_start_x.month == 1 or date_start_x.month == 12:
                                date_start_x = datetime_start_x + GMT_PST_chunk
                                date_end_x = datetime_end_x + GMT_PST_chunk
                                datesquery_start = "{0:d}{1:02d}{2:02d}T08:00-0000".format(date_start_x.year,
                                                                                           date_start_x.month,
                                                                                           date_start_x.day)
                                datesquery_end = "{0:d}{1:02d}{2:02d}T08:00-0000".format(date_end_x.year,
                                                                                         date_end_x.month,
                                                                                         date_end_x.day)

                                # ddownloader_CAISO(URL, case_dwn_x, datesquery_start, datesquery_end, pnode_look, log_identifier,
                                #                   proxy_options={}, ssl_verify=True)
                                # 1st download
                                log_identifier = '{date}A, {pnode}, {dtype}'.format(date=date_str, dtype=case_dwn[ixlp],
                                                                                    pnode=pnode_look)
                                df_data1, dwn1_ok = self.ddownloader_CAISO(url_CAISO, case_dwn[ixlp], datesquery_start,
                                                                      datesquery_end,
                                                                      pnode_look, log_identifier, ssl_verify=ssl_verify,
                                                                      proxy_settings=proxy_settings)

                                # df_data = df_data1
                                # dwn_ok = dwn1_ok
                                # 2nd download
                                log_identifier = '{date}B, {pnode}, {dtype}'.format(date=date_str, dtype=case_dwn[ixlp],
                                                                                    pnode=pnode_look)
                                date_start_x = datetime_end_x + GMT_PST_chunk
                                date_end_x = datetime_end_x + GMT_PST_chunk + day_chunk
                                datesquery_start = "{0:d}{1:02d}{2:02d}T08:00-0000".format(date_start_x.year,
                                                                                           date_start_x.month,
                                                                                           date_start_x.day)
                                datesquery_end = "{0:d}{1:02d}{2:02d}T08:00-0000".format(date_end_x.year,
                                                                                         date_end_x.month,
                                                                                         date_end_x.day)
                                df_data2, dwn2_ok = self.ddownloader_CAISO(url_CAISO, case_dwn[ixlp], datesquery_start,
                                                                      datesquery_end,
                                                                      pnode_look, log_identifier, ssl_verify=ssl_verify,
                                                                      proxy_settings=proxy_settings)

                                # Concatenate the two dataframes
                                dwn_ok = dwn1_ok and dwn2_ok

                                if dwn_ok:
                                    df_data = pd.concat([df_data1, df_data2], ignore_index=True)
                            else:
                                df_data, dwn_ok = self.ddownloader_CAISO(url_CAISO, case_dwn[ixlp], datesquery_start,
                                                                    datesquery_end,
                                                                    pnode_look, log_identifier, ssl_verify=ssl_verify,
                                                                    proxy_settings=proxy_settings)

                        if dwn_ok:

                            if case_dwn[ixlp] == "lmp":
                                df_data = df_data.pivot(index='INTERVALSTARTTIME_GMT', columns='LMP_TYPE', values='MW')
                            elif case_dwn[ixlp] == "asp":
                                aregtyp_col = df_data['ANC_REGION'] + "_" + df_data['XML_DATA_ITEM']
                                df_data['REGION_ANC_TYPE'] = aregtyp_col
                                df_data = df_data.pivot(index='INTERVALSTARTTIME_GMT', columns='REGION_ANC_TYPE',
                                                        values='MW')
                            elif case_dwn[ixlp] == "mileage":
                                df_data = df_data.pivot(index='INTERVALSTARTTIME_GMT', columns='XML_DATA_TYPE',
                                                        values='MW')

                            df_data.sort_index(ascending=True, inplace=True)
                            os.makedirs(destination_dir, exist_ok=True)
                            df_data.to_csv(destination_file, sep=',')
                    else:
                        # print('CAISOdownloader: {0}: File already exits, skipping...'.format(log_identifier))
                        logging.info('CAISOdownloader: {0}: File already exists, skipping...'.format(log_identifier))
                    
                    Clock.schedule_once(self.increment_progress_bar, 0)

        self.n_active_threads -= 1

    def ddownloader_CAISO(self, URL, case_dwn_x, datesquery_start, datesquery_end, pnode_look, log_identifier,
                          ssl_verify=True, proxy_settings=None):
        url_CAISO = URL
        if case_dwn_x == "lmp":
            params_dict = {
                # Request parameters
                'queryname': 'PRC_LMP',
                'startdatetime': datesquery_start,
                'enddatetime': datesquery_end,
                'version': '1',
                'market_run_id': 'DAM',
                'node': pnode_look,
                'resultformat': '6'  # SO it's .csv
            }
        elif case_dwn_x == "asp":
            params_dict = {
                # Request parameters
                'queryname': 'PRC_AS',
                'startdatetime': datesquery_start,
                'enddatetime': datesquery_end,
                'version': '1',
                'market_run_id': 'DAM',
                'anc_type': 'ALL',
                'anc_region': 'ALL',
                'resultformat': '6'
            }
        elif case_dwn_x == "mileage":
            params_dict = {
                # Request parameters
                'queryname': 'AS_MILEAGE_CALC',
                'startdatetime': datesquery_start,
                'enddatetime': datesquery_end,
                'version': '1',
                'anc_type': 'ALL',
                'resultformat': '6'
            }

        df_data = np.empty([0])

        trydownloaddate = True
        dwn_ok = False
        wx = 0
        while trydownloaddate:
            # Quit?
            if App.get_running_app().root.stop.is_set():
                # Stop running this thread so the main Python process can exit.
                trydownloaddate = False
                break

            wx = wx + 1
            # print('try no. ' + str(wx) + "--" + log_identifier)
            if wx >= MAX_WHILE_ATTEMPTS:
                print("Hit wx limit")
                trydownloaddate = False
                break

            try:
                # print("go in try")
                with requests.Session() as req:
                    # print("go in with")
                    http_request = req.get(url_CAISO, params=params_dict, proxies=proxy_settings, timeout=7,
                                           verify=ssl_verify)
                    # Check the HTTP status code.

                    # print(http_request.status_code, http_request.reason)
                    if http_request.status_code == requests.codes.ok:
                        trydownloaddate = False
                        # self.thread_failed = False
                    elif http_request.status_code == 429:
                        # time.sleep(5.5)  # delays for 5.5 seconds
                        http_request.raise_for_status()
                    else:
                        # time.sleep(5.1)  # delays for 5.1 seconds
                        http_request.raise_for_status()

            except requests.HTTPError as e:
                logging.error('CAISOdownloader: {0}: {1}'.format(log_identifier, repr(e)))
                Clock.schedule_once(partial(self.update_output_log, '{0}: HTTPError: {1}'.format(log_identifier, e.response.status_code), 0))
                if wx >= (MAX_WHILE_ATTEMPTS - 1):
                    self.thread_failed = True
            except requests.exceptions.ProxyError:
                logging.error('CAISOdownloader: {0}: Could not connect to proxy.'.format(log_identifier))
                Clock.schedule_once(partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(log_identifier)), 0)
                if wx >= (MAX_WHILE_ATTEMPTS - 1):
                    self.thread_failed = True
            except requests.ConnectionError as e:
                logging.error(
                    'CAISOdownloader: {0}: Failed to establish a connection to the host server.'.format(log_identifier))
                Clock.schedule_once(partial(self.update_output_log, '{0}: Failed to establish a connection to the host server.'.format(log_identifier)), 0)
                if wx >= (MAX_WHILE_ATTEMPTS - 1):
                    self.thread_failed = True
            except (socket.timeout, requests.Timeout) as e:
                # print("Go in timeout exception")
                logging.error('CAISOdownloader: {0}: The connection timed out.'.format(log_identifier))
                Clock.schedule_once(partial(self.update_output_log, '{0}: The connection timed out.'.format(log_identifier)), 0)
                if wx >= (MAX_WHILE_ATTEMPTS - 1):
                    self.thread_failed = True
            except requests.RequestException as e:
                logging.error('CAISOdownloader: {0}: {1}'.format(log_identifier, repr(e)))
                if wx >= (MAX_WHILE_ATTEMPTS - 1):
                    self.thread_failed = True
            except Exception as e:
                # print("Go in generic exception")
                # Something else went wrong.
                logging.error(
                    'CAISOdownloader: {0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e)))
                Clock.schedule_once(partial(self.update_output_log, '{0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e))), 0)
                if wx >= (MAX_WHILE_ATTEMPTS - 1):
                    self.thread_failed = True

            else:
                # print("go in 'else' for good download")
                trydownloaddate = False

                z = zipfile.ZipFile(io.BytesIO(http_request.content))
                fnameopen = z.filelist[0].filename

                if fnameopen[-4:] == '.csv':
                    fcsv = z.open(fnameopen)
                    df_data = pd.read_csv(fcsv)

                    logging.info('CAISOdownloader: {0}: Successfully downloaded.'.format(log_identifier))
                    # print('CAISOdownloader: {0}: Successfully downloaded.'.format(log_identifier))
                    # time.sleep(5.2)  # delays for 5.2 seconds
                    dwn_ok = True
                elif fnameopen[-4:] == '.xml':
                    fxml = z.open(fnameopen)
                    xmlsoup = BeautifulSoup(fxml, 'xml')
                    err_xml = xmlsoup.find_all('ERR_CODE')
                    err_xml = err_xml[0].contents[0]
                    if err_xml=='1015':
                        # print('Error 1015')
                        trydownloaddate = True
                    else:
                        dwn_ok = False
                        logging.info('CAISOdownloader: {0}: 1015: GroupZip DownLoad is in Processing, Please Submit request after Sometime.'.format(log_identifier))
                        # print('CAISOdownloader: {0}: Not a valid download request.'.format(log_identifier))

                else:
                    dwn_ok = False
                    logging.info('CAISOdownloader: {0}: Not a valid download request.'.format(log_identifier))
                    # print('CAISOdownloader: {0}: Not a valid download request.'.format(log_identifier))
            time.sleep(5.1)  # delays for 5.1 seconds

        return df_data, dwn_ok


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

            # Split up the download requests to accomodate the maximum amount of allowable threads.
            job_batches = batch_splitter(monthrange)

            self.n_active_threads = len(job_batches)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = 0
            self.output_log.text = ''

            # Check connection settings.
            ssl_verify, proxy_settings = check_connection_settings()

            # Spawn a new thread for each download_PJM_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_PJM_data, 
                args=(sub_key, batch[0], batch[-1]),
                kwargs={'ssl_verify': ssl_verify, 'proxy_options': proxy_settings, 'nodes': node_type_selected})
                thread_downloader.start()

            # thread_downloader = threading.Thread(target=self._download_PJM_data, args=(sub_key, datetime_start, datetime_end), kwargs={'nodes': node_type_selected, 'ssl_verify': False})
            # thread_downloader.start()
    
    def _download_PJM_data(self, subs_key, datetime_start, datetime_end=None, typedat="all", nodes=[], foldersave='data', proxy_options={}, ssl_verify=True):
        
        # Request headers.
        headers = {
            'Ocp-Apim-Subscription-Key': subs_key,
        }

        if not datetime_end:
            datetime_end = datetime_start

        startyear = datetime_start.year
        endyear = datetime_end.year
        startmonth = datetime_start.month
        endmonth = datetime_end.month

        # loop through the months and from them do the start and end
        date_download = []
        for yx in range(startyear,endyear+1):
            # print(yx)
            if yx == startyear:
                startmonth_x = startmonth
            else:
                startmonth_x = 1

            if yx == endyear:
                endmonth_x = endmonth
            else:
                endmonth_x = 12

            for mx in range(startmonth_x,endmonth_x+1):
                date_download.append(str(yx)+str(mx).zfill(2))

        # Request URL roots.
        urlPJM_lmp = "https://api.pjm.com/api/v1/da_hrl_lmps?"
        urlPJM_reg = "https://api.pjm.com//api/v1/reg_zone_prelim_bill?"
        urlPJM_mileage = "https://api.pjm.com/api/v1/reg_market_results?"

        lmp_or_reg = []
        urlPJM_list = []
        folderprice = []
        params_dict_list = []

        if typedat == "all":
            urlPJM_list.append(urlPJM_lmp)
            urlPJM_list.append(urlPJM_reg)
            urlPJM_list.append(urlPJM_mileage)
            folderprice.append("/PJM/LMP/")
            folderprice.append("/PJM/REG/")
            folderprice.append("/PJM/MILEAGE/")
            lmp_or_reg = ["lmp", "reg", "mileage"]
        elif typedat == "lmp":
            urlPJM_list.append(urlPJM_lmp)
            folderprice.append("/PJM/LMP/")
            lmp_or_reg = ["lmp"]
        elif typedat == "reg":
            urlPJM_list.append(urlPJM_reg)
            folderprice.append("/PJM/REG/")
            lmp_or_reg = ["reg"]
        elif typedat == "mileage":
            urlPJM_list.append(urlPJM_mileage)
            folderprice.append("/PJM/MILEAGE/")
            lmp_or_reg = ["mileage"]

        for ixlp, urlPJM_list_x in enumerate(urlPJM_list):
            for dx in date_download:
                yearx = dx[0:4]
                monthx = dx[4:]

                ndaysmonthx = calendar.monthrange(int(yearx), int(monthx))
                ndaysmonthx = int(ndaysmonthx[1])

                nodetypesPJM = ['ZONE', 'LOAD', 'GEN', 'AGGREGATE', 'HUB', 'EHV', 'INTERFACE', 'EXT', 'RESIDUAL_METERED_EDC']

                pnode_look_list = []
                if lmp_or_reg[ixlp] == "lmp":
                    if not nodes:
                        nodelist = getPJMnodes(subs_key, dx, nodetype=[], proxydict=proxy_options, ssl_verify=ssl_verify)
                    else:
                        nodelist = []
                        for node_x in nodes:

                            isnodetype = [True for nodetypePJM_x in nodetypesPJM if node_x == nodetypePJM_x]

                            if isnodetype:
                                nodelist_x = getPJMnodes(subs_key, dx, nodetype=node_x, proxydict=proxy_options, ssl_verify=ssl_verify)
                                nodelist = nodelist + nodelist_x
                            else:
                                nodelist.append(node_x)

                    logging.info('PJMdownloader: Number of nodes in this call: {0}.'.format(str(len(nodelist))))
                    pnode_look_list = nodelist
                elif lmp_or_reg[ixlp] == "reg":
                    pnode_look_list = ["n/a"]
                elif lmp_or_reg[ixlp] == "mileage":
                    pnode_look_list = ["n/a"]
                
                self.progress_bar.max += len(pnode_look_list)

                for pnode_x in pnode_look_list:
                    pnode_look = pnode_x

                    log_identifier = '{date}, {pnode}, {dtype}'.format(date=dx, dtype=lmp_or_reg[ixlp], pnode=pnode_look)

                    nfilesave = "error.csv"
                    if lmp_or_reg[ixlp] == "lmp":
                        des_dir = foldersave + folderprice[ixlp] + pnode_look + "/" + yearx + "/"
                        nfilesave = dx + "_dalmp_" + pnode_look + ".csv"
                    elif lmp_or_reg[ixlp] == "reg":
                        # des_dir = foldersave + folderprice[ixlp] + yearx + "/" + monthx + "/"
                        des_dir = foldersave + folderprice[ixlp] + yearx + "/"
                        nfilesave = dx + "_regp" + ".csv"
                    elif lmp_or_reg[ixlp] == "mileage":
                        des_dir = foldersave + folderprice[ixlp] + yearx + "/"
                        nfilesave = dx + "_regm" + ".csv"

                    if not os.path.exists(des_dir + nfilesave):
                        datesquery = "{0:d}-01-{1:d} 00:00 to {0:d}-{2:02d}-{1:d} 23:59".format(int(monthx), int(yearx), ndaysmonthx)
                        date_str = datetime.date(int(yearx), int(monthx), ndaysmonthx).strftime('%Y%m')

                        if lmp_or_reg[ixlp] == "lmp":
                            params_dict = {
                                # Request parameters
                                'download': 'true',  ### if true it returns some sort of gzip
                                'rowCount': '50000',
                                'sort': 'datetime_beginning_ept',
                                'order': 'asc',
                                'startRow': '1',  ### required if any other parameter is specified
                                'datetime_beginning_ept': datesquery,  #
                                'pnode_id': pnode_look,
                            }
                        elif lmp_or_reg[ixlp] == "reg":
                            params_dict = {
                                # Request parameters
                                'download': 'true',
                                'rowCount': '50000',
                                'sort': 'datetime_beginning_ept',
                                'order': 'asc',
                                'startRow': '1',
                                'datetime_beginning_ept': datesquery,  #
                            }
                        elif lmp_or_reg[ixlp] == "mileage":
                            params_dict = {
                                # Request parameters
                                'download': 'true',
                                'rowCount': '50000',
                                'sort': 'datetime_beginning_ept',
                                'order': 'asc',
                                'startRow': '1',
                                'datetime_beginning_ept': datesquery,  #
                            }

                        try:
                            dodownload = True
                            ix = 0
                            while dodownload:
                                # Quit?
                                if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                                    # Stop running this thread so the main Python process can exit.
                                    self.n_active_threads -= 1
                                    return

                                with requests.Session() as response:
                                    response = requests.get(urlPJM_list_x, params=params_dict,headers=headers, proxies=proxy_options,timeout=10, verify=ssl_verify)
                                    # Check the HTTP status code.

                                #print(response.status_code, response.reason)
                                if response.status_code == requests.codes.ok:
                                    dataheaders = response.headers
                                    data_text = response.json()
                                    df_data = pd.DataFrame.from_dict(data_text)
                                    total_nrows = float(dataheaders['X-TotalRows'])

                                    #print(total_nrows)

                                    if ix == 0:
                                        df_data_all = df_data
                                    else:
                                        df_data_all = pd.concat([df_data_all, df_data], ignore_index=True)
                                    #print(50000 * (ix + 1) + 1)
                                    params_dict['startRow'] = str(50000 * (ix + 1) + 1)

                                    nloops = math.ceil(total_nrows / 50000) - 1

                                    if ix >= nloops:
                                        dodownload = False

                                    ix += 1
                                if total_nrows != 0:
                                    df_data_all.set_index('datetime_beginning_ept', inplace=True)

                                    columns_del = []
                                    if lmp_or_reg[ixlp] == "lmp":
                                        columns_del = ['equipment',
                                                    'pnode_name','row_is_current','system_energy_price_da',
                                                    'version_nbr','voltage','zone',
                                                        'type','pnode_id','congestion_price_da',
                                                    'marginal_loss_price_da']
                                    elif lmp_or_reg[ixlp] == "reg":
                                        columns_del = ['datetime_ending_ept', 'datetime_ending_utc', 'total_pjm_assigned_reg',
                                                    'total_pjm_loc_credit', 'total_pjm_reg_purchases', 'total_pjm_rmccp_cr',
                                                    'total_pjm_rmpcp_cr', 'total_pjm_rt_load_mwh', 'total_pjm_self_sched_reg'
                                                    ]
                                    elif lmp_or_reg[ixlp] == "mileage":
                                        columns_del = ['deficiency', 'is_approved', 'modified_datetime_utc', 'rega_mileage', 
                                        'rega_procure', 'rega_ssmw', 'regd_mileage', 'regd_procure', 'regd_ssmw', 
                                        'requirement', 'rto_perfscore', 'total_mw']
                                    df_data_all.drop(columns_del, inplace=True, axis=1)
                                    os.makedirs(des_dir, exist_ok=True)

                                    df_data_all.to_csv(des_dir + nfilesave, sep=',')
                                    logging.info('PJMdownloader: {0}: Successfully downloaded.'.format(log_identifier))
                                else:
                                    logging.warning('PJMdownloader: {0}: No data retrieved in this API call.'.format(log_identifier))
                        except requests.HTTPError as e:
                            logging.error('PJMdownloader: {0}: {1}'.format(log_identifier, repr(e)))
                            Clock.schedule_once(partial(self.update_output_log, '{0}: HTTPError: {1}'.format(log_identifier, e.response.status_code), 0))
                            self.thread_failed = True
                        except requests.exceptions.ProxyError:
                            logging.error('PJMdownloader: {0}: Could not connect to proxy.'.format(log_identifier))
                            Clock.schedule_once(partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(log_identifier)), 0)
                            self.thread_failed = True
                        except requests.ConnectionError as e:
                            logging.error('PJMdownloader: {0}: Failed to establish a connection to the host server.'.format(log_identifier))
                            Clock.schedule_once(partial(self.update_output_log, '{0}: Failed to establish a connection to the host server.'.format(log_identifier)), 0)
                            self.thread_failed = True
                        except (socket.timeout, requests.Timeout) as e:
                            logging.error('PJMdownloader: {0}: The connection timed out.'.format(log_identifier))
                            Clock.schedule_once(partial(self.update_output_log, '{0}: The connection timed out.'.format(log_identifier)), 0)
                            self.thread_failed = True
                        except requests.RequestException as e:
                            logging.error('PJMdownloader: {0}: {1}'.format(log_identifier, repr(e)))
                            self.thread_failed = True
                        except Exception as e:
                            # Something else went wrong.
                            logging.error('PJMdownloader: {0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e)))
                            Clock.schedule_once(partial(self.update_output_log, '{0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e))), 0)
                            self.thread_failed = True
                    else:
                        logging.info('PJMdownloader: {0}: File already exists, skipping...'.format(log_identifier))
                    
                    Clock.schedule_once(self.increment_progress_bar, 0)

                    # Quit?
                    if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                        # Stop running this thread so the main Python process can exit.
                        self.n_active_threads -= 1
                        return
        
        self.n_active_threads -= 1
        

class DataManagerCheckbox(CheckBox):
    node_type_name = StringProperty('')


class DataManagerPJMSubKeyHelp(ModalView):
    pass


class DataManagerISONEAccHelp(ModalView):
    pass


def getPJMnodes(subs_key, startdate, nodetype=[], proxydict={}, ssl_verify=True):
    """
    """


    startyear = int(startdate[0:4])
    startmonth = int(startdate[4:])


    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': subs_key,
    }

    datesquery = "{0:d}-01-{1:d} 00:00 to {0:d}-01-{1:d} 2:59".format(int(startmonth), int(startyear))
    params_dict = {
        # Request parameters
        'download': 'true',  ### if true it returns some sort of gzip
        'rowCount': '50000',
        'sort': 'datetime_beginning_ept',
        'order': 'asc',
        'startRow': '1',  ### required if any other parameter is specified
        'datetime_beginning_ept': datesquery,  #
    }
    if nodetype:
        params_dict['type'] = nodetype

    try:
        dodownload = True
        ix = 0

        while dodownload:
            response = requests.get("https://api.pjm.com/api/v1/da_hrl_lmps?", params=params_dict, headers=headers, proxies=proxydict, timeout=10, verify=ssl_verify)
            #print(response.status_code, response.reason)

            dataheaders = response.headers
            data_text = response.json()
            df_data = pd.DataFrame.from_dict(data_text)
            total_nrows = float(dataheaders['X-TotalRows'])

            #print(total_nrows)

            if total_nrows > 1000000:
                raise ValueError("Can't get so much data in a particular API search!!!")

            if ix == 0:
                df_data_all = df_data
            else:
                df_data_all = pd.concat([df_data_all, df_data], ignore_index=True)
            #print(50000 * (ix + 1) + 1)
            params_dict['startRow'] = str(50000 * (ix + 1) + 1)

            nloops = math.ceil(total_nrows / 50000) - 1

            if ix >= nloops:
                dodownload = False

            ix += 1

        nodelist = df_data_all.pnode_id.unique()
        nodelist = nodelist.astype(str)
        nodelist = nodelist.tolist()
        #print(type(nodelist))

        return nodelist
    except Exception as e:
        print(repr(e))
        return []

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