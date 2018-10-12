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

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import pandas as pd
from bs4 import BeautifulSoup
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, SwapTransition
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar, ActionButton, ActionGroup
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.core.text import LabelBase

from es_gui.resources.widgets.common import InputError, WarningPopup, MyPopup, APP_NAME, APP_TAGLINE

MAX_THREADS = 4
MAX_WHILE_ATTEMPTS = 7

class DataManagerHomeScreen(Screen):
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager')


class DataManagerRTOMOdataScreen(Screen):
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager: ISO/RTO Market and Operations Data')


class DataManagerMarketTabbedPanel(TabbedPanel):
    pass


class DataManagerPanelERCOT(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.thread_failed:
                logging.warning('ERCOTdownloader: At least one download thread failed. See the log for details.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the years that returned errors.'), 0)
            else:
                logging.info('ERCOTdownloader: All requested data successfully finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data successfully finished downloading.'), 0)
            
            self.execute_download_button.disabled = False
            self.thread_failed = False

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.
        
        :param text: The text to be added to the log.
        :type text: str
        """
        self.output_log.text = '\n'.join([self.output_log.text, text])

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

            # Compute the range of years to iterate over.
            year_range = pd.date_range(datetime_start, datetime_end, freq='YS')
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
                self.progress_bar.value += 1
            
        self.n_active_threads -= 1


class DataManagerPanelISONE(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)

    def open_isone_acc_help(self):
        isone_acc_help_view = DataManagerISONEAccHelp()
        isone_acc_help_view.open()

    def on_n_active_threads(self, instance, value):
        # Update progress bar.
        self.progress_bar.value = self.progress_bar.max - value

        # Check if all threads have finished executing.
        if value == 0:
            if self.thread_failed:
                logging.warning('ISO-NEdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                self.update_output_log('At least one download thread failed. Please retry downloading data for the months that returned errors.')
            else:
                logging.info('ISO-NEdownloader: All requested data downloaded and extracted.')
                self.update_output_log('All requested data downloaded and extracted.')
            
            self.execute_download_button.disabled = False
            self.thread_failed = False

    @mainthread
    def update_output_log(self, text, *args):
        self.output_log.text = '\n'.join([self.output_log.text, text])

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

        # Check if a node ID has been specified
        node_id = self.node_id.text

        if not node_id:
            raise (InputError('Please enter a node ID.'))
        
        return acc_user, acc_pw, datetime_start, datetime_end, node_id

    def get_inputs(self):
        acc_user, acc_pw, datetime_start, datetime_end, node_id = self._validate_inputs()

        return acc_user, acc_pw, datetime_start, datetime_end, node_id

    def execute_download(self):
        try:
            acc_user, acc_pw, datetime_start, datetime_end, node_id = self.get_inputs()
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

            # Compute the range of months to iterate over.
            daterange = pd.date_range(datetime_start, datetime_end, freq='1MS')
            daterange.union([daterange[-1] + 1])

            self.n_active_threads = len(daterange)

            # (Re)set the progress bar and output log.
            self.progress_bar.value = 0
            self.progress_bar.max = len(daterange)
            self.output_log.text = ''

            # Spawn a new thread for each download call.
            for date in daterange:
                thread_downloader = threading.Thread(target=self._download_ISONE_data, args=(acc_user, acc_pw, node_id, date.year, date.month,), kwargs={'ssl_verify': False})
                thread_downloader.start()

                # thread_downloader = threading.Thread(target=self._download_ISONE_RCP, args=(acc_user, acc_pw, date.year, date.month,), kwargs={'ssl_verify': False})
                # thread_downloader.start()
    
    def _download_ISONE_data(self, username, password, node, year, month, path=os.path.join('data'), ssl_verify=True):
        """Downloads a month's worth of ISO-NE day ahead LMP and RCP data.
        
        :param username: ISO-NE ISO Express username
        :type username: str
        :param password: ISO-NE ISO Express password
        :type password: str
        :param node: pricing node ID
        :type node: str
        :param year: year of month to download
        :type year: int
        :param month: month to download
        :type month: int
        :param path: root directory of data download location, defaults to os.path.join('data')
        :param path: str, optional
        :param ssl_verify: if SSL verification should be done, defaults to True
        :param ssl_verify: bool, optional
        """
        api = 'https://webservices.iso-ne.com/api/v1.1'

        lmp_record_list = []
        rcp_record_list = []

        _, n_days_month = calendar.monthrange(year, month)
        logging.info('ISO-NEdownloader: Retrieving data for {0} {1}...'.format(month, year))

        for day in [x+1 for x in range(n_days_month)]:
            # Format API request.
            date = dt.datetime(year, month, day, 0, 0, 0).strftime("%Y%m%d")
            
            # LMP API call.
            request_string = '/hourlylmp/da/final/day/{0}/location/{1}.json'.format(date, node)
            lmp_api_call = api + request_string

            # RCP API call.
            request_string = '/hourlyrcp/final/day/{0}.json'.format(date)
            rcp_api_call = api + request_string

            # Make request to the API.
            try:
                lmp_data = requests.get(lmp_api_call, auth=(username, password), timeout=10, verify=ssl_verify)
                rcp_data = requests.get(rcp_api_call, auth=(username, password), timeout=10, verify=ssl_verify)
            except requests.HTTPError as e:
                logging.error('ISO-NEdownloader: {0}: {1}'.format(date, repr(e)))
                self.update_output_log('{0}: {1}'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.ConnectionError as e:
                logging.error('ISO-NEdownloader: {0}: Failed to establish a connection to the host server.'.format(date))
                self.update_output_log('{0}: Failed to establish a connection to the host server.'.format(date))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.Timeout as e:
                logging.error('ISO-NEdownloader: {0}: The connection timed out.'.format(date))
                self.update_output_log('{0}: The connection timed out.'.format(date))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.RequestException as e:
                logging.error('ISO-NEdownloader: {0}: {1}'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except Exception as e:
                # Something else went wrong.
                logging.error('ISO-NEdownloader: {0}: An unexpected error has occurred. ({1})'.format(date, repr(e)))
                self.update_output_log('{0}: An unexpected error has occurred. ({1})'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            else:
                # Decode the returned .json, interpret it as dictionary, and append to the record for the month.
                try:
                    lmp_data_list = lmp_data.json()['HourlyLmps']['HourlyLmp']
                    rcp_data_list = rcp_data.json()['HourlyRcps']['HourlyRcp']
                except TypeError as e:
                    # Unauthorized access/invalid credentials?
                    logging.error('ISO-NEdownloader: {0}: Data returned in an unexpected format. An invalid query (data not available) or credentials are likely the reason. ({1})'.format(date, repr(rcp_data.json())))
                    self.update_output_log('{0}: Data returned in unexpected format. An invalid query (data not available) or credentials are likely the reason.'.format(date))
                    self.n_active_threads -= 1
                    self.thread_failed = True

                    return
                else:
                    lmp_record_list += lmp_data_list
                    rcp_record_list += rcp_data_list

        # Convert to DataFrame and save to directory.
        df = pd.DataFrame.from_records(lmp_record_list)

        destination_path = os.path.join(path, 'ISO-NE', 'LMP', str(year), str(month).zfill(2))
        os.makedirs(destination_path, exist_ok=True)

        fname = os.path.join(destination_path, '_'.join([str(year), str(month).zfill(2), 'dalmp', node]))
        df.to_csv(fname+'.csv')

        # Convert to DataFrame and save to directory.
        df = pd.DataFrame.from_records(rcp_record_list)

        destination_path = os.path.join(path, 'ISO-NE', 'RCP', str(year), str(month).zfill(2))
        os.makedirs(destination_path, exist_ok=True)

        fname = os.path.join(destination_path, '_'.join([str(year), str(month).zfill(2), 'darcp']))
        df.to_csv(fname+'.csv')

        self.n_active_threads -= 1
    
    def _download_ISONE_LMP(self, username, password, node, year, month, path=os.path.join('data'), ssl_verify=True):
        """Deprecated."""
        api = 'https://webservices.iso-ne.com/api/v1.1'

        record_list = []

        _, n_days_month = calendar.monthrange(year, month)

        for day in [x+1 for x in range(n_days_month)]:
            #print('Processing day {0}, year {1}, month {2}, node {3}'.format(int(day), int(year), int(month), node))
            
            # Format API request.
            date = dt.datetime(year, month, day, 0, 0, 0).strftime("%Y%m%d")
            request_string = '/hourlylmp/da/final/day/{0}/location/{1}.json'.format(date, node)
            urllink = api + request_string

            # Make request to the API.
            try:
                data = requests.get(urllink, auth=(username, password), timeout=20, verify=ssl_verify)
            except requests.HTTPError as e:
                self.update_output_log('{0}: {1}'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.ConnectionError as e:
                self.update_output_log('{0}: Failed to establish a connection to the host server.'.format(date))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.Timeout as e:
                self.update_output_log('{0}: The connection timed out.'.format(date))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.RequestException as e:
                print(repr(e))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except Exception as e:
                # Something else went wrong.
                self.update_output_log('{0}: An unexpected error has occurred. ({1})'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            else:
                # Decode the returned .json, interpret it as dictionary, and append to the record for the month.
                data_dict = data.json()
                record_list += data_dict['HourlyLmps']['HourlyLmp']

        # Convert to DataFrame and save to directory.
        df = pd.DataFrame.from_records(record_list)

        destination_path = os.path.join(path, 'ISO-NE', 'LMP', str(year), str(month).zfill(2))
        os.makedirs(destination_path, exist_ok=True)

        fname = os.path.join(destination_path, '_'.join([str(year), str(month).zfill(2), 'dalmp', node]))
        df.to_csv(fname+'.csv')

        self.n_active_threads -= 1
    
    def _download_ISONE_RCP(self, username, password, year, month, path=os.path.join('data'), ssl_verify=True):
        """Deprecated."""
        api = 'https://webservices.iso-ne.com/api/v1.1'

        record_list = []

        _, n_days_month = calendar.monthrange(year, month)

        for day in [x+1 for x in range(n_days_month)]:
            #print('Processing day {0}, year {1}, month {2}'.format(int(day), int(year), int(month)))

            # Format API request.
            date = dt.datetime(year, month, day, 0, 0, 0).strftime("%Y%m%d")
            request_string = '/hourlyrcp/final/day/{0}.json'.format(date)
            urllink = api + request_string

            # Make request to the API.
            try:
                data = requests.get(urllink, auth=(username, password), timeout=20, verify=ssl_verify)
            except requests.HTTPError as e:
                self.update_output_log('{0}: {1}'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.ConnectionError as e:
                self.update_output_log('{0}: Failed to establish a connection to the host server.'.format(date))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.Timeout as e:
                self.update_output_log(('{0}: The connection timed out.'.format(date)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except requests.RequestException as e:
                print(repr(e))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            except Exception as e:
                # Something else went wrong.
                self.update_output_log('{0}: An unexpected error has occurred. ({1})'.format(date, repr(e)))
                self.n_active_threads -= 1
                self.thread_failed = True
                return
            else:
                # Decode the returned .json, interpret it as dictionary, and append to the record for the month.
                data_dict = data.json()
                record_list += data_dict['HourlyRcps']['HourlyRcp']

        # Convert to DataFrame and save to directory.
        df = pd.DataFrame.from_records(record_list)

        destination_path = os.path.join(path, 'ISO-NE', 'RCP', str(year), str(month).zfill(2))
        os.makedirs(destination_path, exist_ok=True)

        fname = os.path.join(destination_path, '_'.join([str(year), str(month).zfill(2), 'darcp']))
        df.to_csv(fname+'.csv')

        self.n_active_threads -= 1


class DataManagerPanelMISO(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.thread_failed:
                logging.warning('MISOdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'), 0)
            else:
                logging.info('MISOdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)
            
            self.execute_download_button.disabled = False
            self.thread_failed = False

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.
        
        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])

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

            # Spawn a new thread for each download_MISO_data call.
            for batch in job_batches:
                thread_downloader = threading.Thread(target=self._download_MISO_data, 
                args=(batch[0], batch[-1]),
                kwargs={'ssl_verify': ssl_verify, 'proxy_settings': proxy_settings})
                thread_downloader.start()

            # # Spawn a new thread for each download call.
            # for date in monthrange:
            #     thread_downloader = threading.Thread(target=self._download_MISO_data, args=(date.year, date.month), kwargs={'ssl_verify': False})
            #     thread_downloader.start()
    
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
        monthrange.union([monthrange[-1] + 1])

        for date in monthrange:
            year = date.year
            month = date.month

            # Compute the range of days to iterate over.
            _, n_days_month = calendar.monthrange(year, month)

            for day in [x+1 for x in range(n_days_month)]:
                date = dt.date(year, month, day)
                date_str = date.strftime('%Y%m%d')

                # LMP call.
                lmp_url = ''.join(['https://docs.misoenergy.org/marketreports/', date_str, '_da_exante_lmp.csv'])
                destination_dir = os.path.join(path, 'MISO', 'LMP', date.strftime('%Y'), date.strftime('%m'))
                destination_file = os.path.join(destination_dir, '_'.join([date_str, 'da_exante_lmp.csv']))

                if os.path.exists(destination_file):
                    # Skip downloading the daily file if it already exists where expected.
                    logging.info('MISOdownloader: {0}: LMP file already exists, skipping...'.format(date_str))
                    #self.update_output_log('{0}: LMP file already exists, skipping...'.format(date_str))
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

                self.progress_bar.value += 1
                
                # MCP call.
                mcp_url = ''.join(['https://docs.misoenergy.org/marketreports/', date_str, '_asm_exante_damcp.csv'])
                destination_dir = os.path.join(path, 'MISO', 'MCP', date.strftime('%Y'), date.strftime('%m'))
                destination_file = os.path.join(destination_dir, '_'.join([date_str, 'asm_exante_damcp.csv']))

                if os.path.exists(destination_file):
                    # Skip downloading the daily file if it already exists where expected.
                    logging.info('MISOdownloader: {0}: MCP file already exists, skipping...'.format(date_str))
                    #self.update_output_log('{0}: MCP file already exists, skipping...'.format(date_str))
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
                
                self.progress_bar.value += 1

        self.n_active_threads -= 1


########################################################################################################################

class DataManagerPanelNYISO(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.thread_failed:
                logging.warning \
                    ('NYISOdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'), 0)
            else:
                logging.info('NYISOdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)

            self.execute_download_button.disabled = False
            self.thread_failed = False

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.

        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])

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
        monthrange.union([monthrange[-1] + 1])

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
                        wx = wx + 1
                        if wx >= MAX_WHILE_ATTEMPTS:
                            logging.warning('NYISOdownloader: {0} {1}: Hit download retry limit.'.format(date_str, lbmp_or_asp_folder[sx]))
                            Clock.schedule_once(partial(self.update_output_log, '{0} {1}: Hit download retry limit'.format(date_str, lbmp_or_asp_folder[sx])), 0)
                            trydownloaddate = False

                        try:
                            with requests.Session() as req:
                                http_request = req.get(datadownload_url, proxies=proxy_settings, timeout=6,
                                                       verify=ssl_verify, stream=True)

                            if http_request.status_code == requests.codes.ok:
                                trydownloaddate = False
                                self.thread_failed = False
                            else:
                                http_request.raise_for_status()
                        except requests.HTTPError as e:
                            logging.error('NYISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                            Clock.schedule_once(partial(self.update_output_log,
                                                        '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
                            self.thread_failed = True
                        except requests.exceptions.ProxyError:
                            logging.error('NYISOdownloader: {0}: Could not connect to proxy.'.format(date_str))
                            Clock.schedule_once(
                                partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
                            self.thread_failed = True
                        except requests.ConnectionError as e:
                            logging.error(
                                'NYISOdownloader: {0}: Failed to establish a connection to the host server.'.format(
                                    date_str))
                            Clock.schedule_once(partial(self.update_output_log,
                                                        '{0}: Failed to establish a connection to the host server.'.format(
                                                            date_str)), 0)
                            self.thread_failed = True
                        except requests.Timeout as e:
                            trydownloaddate = True
                            logging.error('NYISOdownloader: {0}: The connection timed out.'.format(date_str))
                            Clock.schedule_once(
                                partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
                            self.thread_failed = True
                        except requests.RequestException as e:
                            logging.error('NYISOdownloader: {0}: {1}'.format(date_str, repr(e)))
                            # self.thread_failed = True
                        except Exception as e:
                            # Something else went wrong.
                            logging.error(
                                'NYISOdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                       repr(e)))
                            Clock.schedule_once(partial(self.update_output_log,
                                                        '{0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                              repr(e))), 0)
                            self.thread_failed = True
                        else:
                            os.makedirs(destination_dir, exist_ok=True)
                            z = zipfile.ZipFile(io.BytesIO(http_request.content))
                            z.extractall(destination_dir)
                            # print("Successful NYISO data download")
                else:
                    # Skip downloading the daily file if it already exists where expected.
                    logging.info('NYISOdownloader: {0}: {1} file already exists, skipping...'.format(date_str,
                                                                                                     lbmp_or_asp_folder[
                                                                                                         sx]))
                    self.update_output_log('{0}: {1} file already exists, skipping...'.format(date_str, lbmp_or_asp_folder[sx]))

                self.progress_bar.value +=1

        self.n_active_threads -= 1

########################################################################################################################

class DataManagerPanelPJM(BoxLayout):
    n_active_threads = NumericProperty(0)
    thread_failed = BooleanProperty(False)

    def open_pjm_subkey_help(self):
        pjm_subkey_help_view = DataManagerPJMSubKeyHelp()
        pjm_subkey_help_view.open()    

    def on_n_active_threads(self, instance, value):
        # Check if all threads have finished executing.
        if value == 0:
            if self.thread_failed:
                logging.warning('PJMdownloader: At least one download thread failed. See the log for details. Please retry downloading data for the months that returned errors.')
                Clock.schedule_once(partial(self.update_output_log, 'At least one download thread failed. Please retry downloading data for the months that returned errors.'), 0)
            else:
                logging.info('PJMdownloader: All requested data finished downloading.')
                Clock.schedule_once(partial(self.update_output_log, 'All requested data finished downloading.'), 0)
            
            self.execute_download_button.disabled = False
            self.thread_failed = False

    @mainthread
    def update_output_log(self, text, *args):
        """Updates the text input object representing the output log.
        
        :param text: The text to be added to the log.
        :type text: str
        """

        self.output_log.text = '\n'.join([self.output_log.text, text])

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
                        logging.info('PJMdownloader: {0}: File already exits, skipping...'.format(log_identifier))
                    
                    self.progress_bar.value += 1
        
        self.n_active_threads -= 1
        


class DataManagerTabCheckbox(CheckBox):
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


def check_connection_settings():
    """Checks QuESt settings and returns configuration for connection settings """
    app_config = App.get_running_app().config
    proxy_settings = {}

    # Proxy settings.
    if int(app_config.get('connectivity', 'use_proxy')):
        http_proxy = app_config.get('connectivity', 'http_proxy')
        https_proxy = app_config.get('connectivity', 'https_proxy')
        
        if http_proxy:
            proxy_settings['http'] = http_proxy
        if https_proxy:
            proxy_settings['https'] = https_proxy
    
    # SSL verification.
    ssl_verify = True if int(app_config.get('connectivity', 'use_ssl_verify')) else False

    return ssl_verify, proxy_settings

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