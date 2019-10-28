"""This module contains functions for obtaining ISO/RTO market data through their various portals.

Notes
-----
update_function optional keyword arguments are available for each download function. They are primarily intended for connecting QuESt GUI updates with progress increments within each function, e.g., progress bar updates or progress log messages. If a function is provided at the function call, the following calls to update_function will be made:

update_function(str) : When an update message is returned, such as a completion notice or handled exception.

update_function(1) : When progress has incremented by one unit.

update_function(-1) : When the function is completed; signals that this work thread is terminated.

As an example, the QuESt Data Manager GUI will pass an update function to these data download function calls such that the relevant progress bar will be incremented or the relayed message is printed to a message log.

If update_function is None or is not provided, no such functionality will exist.
"""

import os
import io
import socket
import calendar
import datetime
import logging
import datetime as dt
import json
import zipfile

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def download_ercot_data(save_directory, year='all', typedat='both', ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads and extracts specified ERCOT data to the specified local directory.

    This function explores the root of the settlement point price and/or capacity clearing price data portals from ERCOT using BeautifulSoup, downloads, and extracts the .zip files in which the data quanta are delivered.

    Parameters
    ----------
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | ERCOT.
    year : int, str, or list thereof
        The year(s) for which data should be downloaded, defaults to 'all' to indicate all available years.
    typedat : str
        The type of data to download: 'spp' for settlement point price, 'ccp' for capacity clearing price, or 'both' for both, defaults to 'both'
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.
    update_function : function
        An optional function handle for hooking into download progress updates, defaults to None. See module notes for specifications.
    
    Returns
    -------
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit
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
    
    connection_error_occurred = False

    # Iterate through the requested data categories.
    for ixlp, urlERCOT_list_x in enumerate(urlERCOT_list):
        try:
            # Retrieve the webpage and parse for .zip files.
            page = requests.get(urlERCOT_list_x, timeout=10, proxies=proxy_settings, verify=ssl_verify)
            soup_ERCOT_page = BeautifulSoup(page.content, 'html.parser')

            zipfileslinks_ERCOT_page = []
            for link in soup_ERCOT_page.find_all('a'):
                zipfileslinks_ERCOT_page.append(link.get('href'))

            zipfilesnames_ERCOT_page = []
            for tdlink in soup_ERCOT_page.find_all('td', attrs={'class': 'labelOptional_ind'}):
                zipfilesnames_ERCOT_page.append(tdlink.text)

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
                    logging.info('ERCOTdownloader: Downloading data for {0}...'.format(year_x))

                    if update_function is not None:
                        update_message = 'Downloading data for {0}...'.format(year_x)
                        update_function(update_message)
                    
                    yearstr = str(year_x)
                    yearzip = "_" + yearstr + ".zip"
                    ixloop_x = [ix for ix, x in enumerate(zipfilesnames_ERCOT_page) if yearzip in x]
                    ixloop.append(ixloop_x[0])

            # Extract the .zip files to the specified local directory.
            for jx in ixloop:
                zipfilename = zipfilesnames_ERCOT_page[jx]
                yearzip = zipfilename[-8:-4]
                urldown = urlERCOTdown_ini + zipfileslinks_ERCOT_page[jx]
                des_dir = save_directory + folderprice[ixlp] + yearzip + "/"

                if not os.path.exists(des_dir):
                    os.makedirs(des_dir)

                r = requests.get(urldown, timeout=10, proxies=proxy_settings, verify=ssl_verify)
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(des_dir)
        except IndexError as e:
            logging.error('ERCOTdownloader: An invalid year was provided. (got {0})'.format(year))
            connection_error_occurred = True
        except requests.exceptions.ProxyError:
            logging.error('ERCOTdownloader: {0}: Could not connect to proxy.'.format(year))

            if update_function is not None:
                update_message = '{0}: Could not connect to proxy.'.format(year)
                update_function(update_message)

            connection_error_occurred = True
        except socket.timeout:
            logging.error('ERCOTdownloader: The connection timed out.')
            self.update_output_log('The connection for downloading {year} data timed out.'.format(year=year))
            connection_error_occurred = True
        except requests.HTTPError as e:
            logging.error('ERCOTdownloader: {0}: {1}'.format(year, repr(e)))

            if update_function is not None:
                update_message = '{0}: HTTPError: {1}'.format(year, e.response.status_code)
                update_function(update_message)

            connection_error_occurred = True
        except requests.ConnectionError as e:
            logging.error('ERCOTdownloader: {0}: Failed to establish a connection to the host server.'.format(year))

            if update_function is not None:
                update_message = '{0}: Failed to establish a connection to the host server.'.format(year)
                update_function(update_message)

            connection_error_occurred = True
        except requests.Timeout as e:
            logging.error('ERCOTdownloader: {0}: The connection timed out.'.format(year))

            if update_function is not None:
                update_message = '{0}: The connection timed out.'.format(year)
                update_function(update_message)

            connection_error_occurred = True
        except requests.RequestException as e:
            logging.error('ERCOTdownloader: {0}: {1}'.format(year, repr(e)))
            connection_error_occurred = True
        except Exception as e:
            # Something else went wrong.
            logging.error('ERCOTdownloader: {0}: An unexpected error has occurred. ({1})'.format(year, repr(e)))

            if update_function is not None:
                update_message = '{0}: An unexpected error has occurred. ({1})'.format(year, repr(e))
                update_function(update_message)

            connection_error_occurred = True
        else:
            logging.info('ERCOTdownloader: {0} data successfully downloaded and extracted.'.format(year))

            if update_function is not None:
                update_message = 'Data for {0} successfully downloaded and extracted.'.format(year)
                update_function(update_message)
        finally:
            if update_function is not None:
                update_function(1)

            # # Quit?
            # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
            #     # Stop running this thread so the main Python process can exit.
            #     self.n_active_threads -= 1
            #     return
        
    if update_function is not None:
        update_function(-1)


def download_isone_data(self, username, password, save_directory, datetime_start, datetime_end=None, nodes=[], typedat='all', ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified ISO-NE data to the specified local directory.

    Downloads day-ahead LMP and RCP data into monthly packages using API calls accessed with user credentials. See notes for details. This function also obtains a sample energy neutral AGC dispatch signal to estimate mileage parameters.

    Parameters
    ----------
    username : str
        Username for ISO-NE ISO Express API
    password : str
        Password for ISO-NE ISO Express API
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | ERCOT.
    datetime_start : datetime.datetime
        The beginning month and year for which to obtain data 
    datetime_end : datetime.datetime
        The ending month and year, inclusive, for which to obtain data, defaults to None. If None, then only the month specified by datetime_start is used.
    nodes :  list[str]
        The pricing nodes for which to obtain LMP data. If None, all nodes will be used. If 'HUBS' is in nodes, all hubs will be used.
        TODO: check if [] evaluates to None and we can replace default values
    typedat : str
        The type of data to download: 'lmp' for locational marginal price, 'rcp' for regulation capacity price, or 'all' for both, defaults to 'all'
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.
    update_function : function
        An optional function handle for hooking into download progress updates, defaults to None. See module notes for specifications.
    
    Returns
    -------
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit

    Notes
    -----
    User credentials may be obtained by signing up for ISO Express access on the ISO-NE website.

    Before December 2017, day ahead (hourly) data for both LMP and RCP were posted. After December 2017, for RCP data only real time (five minute) data is posted. This function downloads five minute data for LMP and RCP and takes the hourly average for those dates.
    """
    # Mileage data.
    mileage_dir = os.path.join(save_directory, 'ISONE')

    if not os.path.exists(mileage_dir):
        os.makedirs(mileage_dir, exist_ok=True)
    mileage_file = os.path.join(mileage_dir, 'MileageFile.xlsx')    
    mileage_url = 'https://www.iso-ne.com/static-assets/documents/2014/10/Energy_Neutral_AGC_Dispatch.xlsx'
    
    if not os.path.exists(mileage_file):
        mileage_request = requests.get(mileage_url, proxies=proxy_settings, timeout=6, verify=ssl_verify, stream=True)

        with open(mileage_file, 'wb') as f:
            f.write(mileage_request.content)
    
    if not datetime_end:
        datetime_end = datetime_start

    # Get the static list of pricing nodes.
    current_dir = os.path.dirname(os.path.abspath(__file__))

    pathlistnodes = path
    listnodes_file = os.path.join(current_dir, '..', 'apps', 'data_manager', '_static', 'nodes_isone.csv')
    
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
    monthrange.union([monthrange[-1] + 1])

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



if __name__ == '__main__':
    ssl_verify = False
    proxy_settings = {'http_proxy': 'wwwproxy.sandia.gov:80', 'https_proxy': 'wwwproxy.sandia.gov:80'}

    save_directory = 'test'

    def _update_function(update):
        if isinstance(update, int):
            print('incrementing progress_bar')
        elif isinstance(update, str):
            print(update)

    cnx_error = download_ercot_data(
        save_directory, 
        year='all', 
        typedat='both', 
        ssl_verify=ssl_verify, 
        proxy_settings=proxy_settings, 
        n_attempts=7,
        update_function=_update_function
        )
    