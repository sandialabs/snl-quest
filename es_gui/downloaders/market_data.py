"""This module contains functions for obtaining ISO/RTO market data through their various portals.

Notes
-----
update_function optional keyword arguments are available for each download function. They are primarily intended for connecting QuESt GUI updates with progress increments within each function, e.g., progress bar updates or progress log messages. If a function is provided at the function call, the following calls to update_function will be made:

update_function(str) : When an update message is returned, such as a completion notice or handled exception.

update_function(n) (n > 0) : When progress has incremented by n units.

update_function(-1) : When the function is completed; signals that this work thread is terminated.

As an example, the QuESt Data Manager GUI will pass an update function to these data download function calls such that the relevant progress bar will be incremented or the relayed message is printed to a message log.

If update_function is None or is not provided, no such functionality will exist.
"""

import os
import io
import socket
import math
import calendar
import datetime
import logging
import datetime as dt
import json
import zipfile
import time

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

    Notes
    -----
    Validated for 2010 and later.
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


def download_isone_data(username, password, save_directory, datetime_start, datetime_end=None, nodes=[], typedat='all', ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified ISO-NE data to the specified local directory.

    Downloads day-ahead LMP and RCP data into monthly packages using API calls accessed with user credentials. See notes for details. This function also obtains a sample energy neutral AGC dispatch signal to estimate mileage parameters.

    Parameters
    ----------
    username : str
        Username for ISO-NE ISO Express API
    password : str
        Password for ISO-NE ISO Express API
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | ISONE.
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
    Validated for 2016 and later.

    User credentials may be obtained by signing up for ISO Express access on the ISO-NE website.

    Before December 2017, day ahead (hourly) data for both LMP and RCP were posted. After December 2017, for RCP data only real time (five minute) data is posted. This function downloads five minute data for LMP and RCP and takes the hourly average for those dates.
    """
    connection_error_occurred = False

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

    # pathlistnodes = save_directory
    listnodes_file = os.path.join(current_dir, '..', 'apps', 'data_manager', '_static', 'nodes_isone.csv')
    
    if not nodes:
        df_listnodes = pd.read_csv(listnodes_file, index_col=False, encoding="cp1252")
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

    # set datetime when five minute data starts
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

                destination_dir = os.path.join(save_directory, 'ISONE', folderdata[sx], nodex, date.strftime('%Y'))
                destination_file = os.path.join(destination_dir, ''.join([date.strftime('%Y%m'), lmp_or_rcp_nam[sx], nodex, ".csv"]))

                date_Ym_str = date.strftime('%Y%m')
                if not os.path.exists(destination_file):

                    data_down_month = []
                    dwn_ok = True
                    for day in range(1,n_days_month+1):
                        # # Quit?
                        # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                        #     # Stop running this thread so the main Python process can exit.
                        #     self.n_active_threads -= 1
                        #     return

                        date_str = date.strftime('%Y%m') + str(day).zfill(2)
                        if case_dwn_x == 'lmp':
                            datadownload_url = ''.join([url_ISONE, '/hourlylmp/da/final/day/', date_str, '/location/', str(nodex), '.json'])
                        elif case_dwn_x == 'rcp':
                            datadownload_url = ''.join([url_ISONE, '/hourlyrcp/final/day/', date_str,'.json'])
                        elif case_dwn_x == 'fmlmp':
                            datadownload_url = ''.join([url_ISONE, '/fiveminutelmp/prelim/day/', date_str, '/location/', str(nodex), '.json'])
                        elif case_dwn_x == 'fmrcp':
                            datadownload_url = ''.join([url_ISONE, '/fiveminutercp/prelim/day/', date_str, '.json'])

                        trydownloaddate = True
                        wx = 0

                        if not dwn_ok:
                            print("Month download failed")
                            break
                        while trydownloaddate:
                            wx = wx + 1
                            if wx >= n_attempts:
                                print("Hit wx limit")
                                dwn_ok = False
                                trydownloaddate = False
                                break

                            try:
                                with requests.Session() as req:
                                    http_request = req.get(datadownload_url, auth=(username, password), proxies=proxy_settings, timeout=6, verify=ssl_verify, stream=True)

                                    if http_request.status_code == requests.codes.ok:
                                        trydownloaddate = False
                                        connection_error_occurred = False
                                    else:
                                        http_request.raise_for_status()

                            except requests.HTTPError as e:
                                logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                                if update_function is not None:
                                    update_message = '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)
                                    update_function(update_message)

                                if wx >= (n_attempts - 1):
                                    connection_error_occurred = True
                            except requests.exceptions.ProxyError:
                                logging.error('market_data: {0}: Could not connect to proxy.'.format(date_str))

                                if update_function is not None:
                                    update_message = '{0}: Could not connect to proxy.'.format(date_str)
                                    update_function(update_message)

                                if wx >= (n_attempts - 1):
                                    connection_error_occurred = True
                            except requests.ConnectionError as e:
                                logging.error(
                                    'market_data: {0}: Failed to establish a connection to the host server.'.format(
                                        date_str))
                                
                                if update_function is not None:
                                    update_message = '{0}: Failed to establish a connection to the host server.'.format(date_str)
                                    update_function(update_message)
                                
                                if wx >= (n_attempts - 1):
                                    connection_error_occurred = True
                            except requests.Timeout as e:
                                trydownloaddate = True
                                logging.error('market_data: {0}: The connection timed out.'.format(date_str))

                                if update_function is not None:
                                    update_message = '{0}: The connection timed out.'.format(date_str)
                                    update_function(update_message)

                                if wx >= (n_attempts - 1):
                                    connection_error_occurred = True
                            except requests.RequestException as e:
                                logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                                if wx >= (n_attempts - 1):
                                    connection_error_occurred = True
                            except Exception as e:
                                # Something else went wrong.
                                logging.error(
                                    'market_data: {0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                            repr(e)))
                                
                                if update_function is not None:
                                    update_message = '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))
                                    update_function(update_message)
                                
                                if wx >= (n_attempts - 1):
                                    connection_error_occurred = True
                            else:
                                data_down = []
                                if case_dwn_x == 'lmp':
                                    try:
                                        data_down = http_request.json()['HourlyLmps']['HourlyLmp']
                                    except TypeError:
                                        logging.error('market_data: {0} {1}: No data returned.'.format(date_str, case_dwn_x))

                                        if update_function is not None:
                                            update_message = '{0}: No data returned.'.format(date_str)
                                            update_function(update_message)
                                        
                                        if wx >= (n_attempts - 1):
                                            connection_error_occurred = True
                                        dwn_ok = False
                                        break
                                elif case_dwn_x == 'rcp':
                                    try:
                                        data_down = http_request.json()['HourlyRcps']['HourlyRcp']
                                    except TypeError:
                                        logging.error('market_data: {0} {1}: No data returned.'.format(date_str, case_dwn_x))

                                        if update_function is not None:
                                            update_message = '{0}: No data returned.'.format(date_str)
                                            update_function(update_message)
                                        
                                        if wx >= (n_attempts - 1):
                                            connection_error_occurred = True
                                        dwn_ok = False
                                        break
                                elif case_dwn_x == 'fmlmp':
                                    try:
                                        data_down = http_request.json()['FiveMinLmps']['FiveMinLmp']
                                    except TypeError:
                                        logging.error('market_data: {0} {1}: No data returned.'.format(date_str, case_dwn_x))

                                        if update_function is not None:
                                            update_message = '{0}: No data returned.'.format(date_str)
                                            update_function(update_message)
                                        
                                        if wx >= (n_attempts - 1):
                                            connection_error_occurred = True
                                        dwn_ok = False
                                        break
                                elif case_dwn_x == 'fmrcp':
                                    try:
                                        data_down = http_request.json()['FiveMinRcps']['FiveMinRcp']
                                    except TypeError:
                                        logging.error('market_data: {0} {1}: No data returned.'.format(date_str, case_dwn_x))

                                        if update_function is not None:
                                            update_message = '{0}: No data returned.'.format(date_str)
                                            update_function(update_message)
                                        
                                        if wx >= (n_attempts - 1):
                                            connection_error_occurred = True
                                        dwn_ok = False
                                        break
                                data_down_month += data_down

                    if dwn_ok:
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
                    logging.info('market_data: {0}: {1} file already exists, skipping...'.format(date_Ym_str, case_dwn[sx]))
                    
                if update_function is not None:
                    update_function(1)
                # # Quit?
                # if App.get_running_app().root.stop.is_set():
                #     # Stop running this thread so the main Python process can exit.
                #     self.n_active_threads -= 1
                #     return
            
    if update_function is not None:
        update_function(-1)
    
    return connection_error_occurred


def download_spp_data(save_directory, datetime_start, datetime_end=None, typedat='all', bus_loc='both', ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified SPP data to the specified local directory.

    Downloads day-ahead LMP and MCP (for operating reserve products) data into monthly packages using the SPP integrated marketplace portal. 

    Parameters
    ----------
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | SPP.
    datetime_start : datetime.datetime
        The beginning month and year for which to obtain data 
    datetime_end : datetime.datetime
        The ending month and year, inclusive, for which to obtain data, defaults to None. If None, then only the month specified by datetime_start is used.
    typedat : str
        The type of data to download: 'lmp' for locational marginal price, 'mcp' for market clearing price (Operating Reserve product), or 'all' for both, defaults to 'all'
    bus_loc : str
        The pricing nodes for which to obtain LMP data. Valid values are 'bus', 'location', and 'both', defaults to 'both'
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
    Validated for 2014 and later. SPP shares data starting in May/June 2013 but it is completely disorganized in certain parts.

    Per summary descriptions on https://marketplace.spp.org/groups/day-ahead-market

    bus_loc = 'bus' : 'Provides LMP information by Pnode location for each Day-Ahead Market solution for each Operating Day.'

    bus_loc = 'location' : 'Provides LMP information by Pnode location and corresponding Settlement Location for each Day-Ahead Market solution for each Operating Day.'

    Updated 01/17/2020: API prefix changed from "file-api" to "file-browser-api"
    """
    connection_error_occurred = False

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
                destination_dir = os.path.join(save_directory, 'SPP', lmp_or_mpc_folder[sx], 'DAM', bus_or_loc_folder[sx],
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
                    trydownloaddate = True
                    wx = 0

                    while trydownloaddate:
                        # # Quit?
                        # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                        #     # Stop running this thread so the main Python process can exit.
                        #     self.n_active_threads -= 1
                        #     return

                        wx = wx + 1
                        if wx >= n_attempts:
                            logging.warning('market_data: {0} {1}: Hit download retry limit.'.format(date_str, lmp_or_mpc_folder[sx]))

                            if update_function is not None:
                                update_message = '{0} {1}: Hit download retry limit.'.format(date_str, lmp_or_mpc_folder[sx])
                                update_function(update_message)

                            trydownloaddate = False
                            break

                        try:
                            with requests.Session() as req:
                                http_request = req.get(datadownload_url, proxies=proxy_settings, timeout=6,
                                                        verify=ssl_verify, stream=True)

                            http_request_f = http_request
                            if http_request.status_code == requests.codes.ok:
                                trydownloaddate = False
                            elif http_request.status_code == 406:
                                # Try again!
                                if lmp_or_mpc_folder[sx] == "LMP":
                                    name_file = "DA-LMP-{0:s}-{1:d}{2:02d}{3:02d}0100.csv".format(bus_or_loc_nam[sx], date.year, date.month, day)
                                    URL_compl = "?path=%2F{0:d}%2F{1:02d}%2F{2:s}".format(date.year, date.month, foldercompl_da[1])
                                
                                datadownload_url = ''.join(
                                    [case_URL_x, bus_or_loc_folder[sx], URL_compl, name_file]
                                    )

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
                            logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                            if update_function is not None:
                                update_message = '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)
                                update_function(update_message)

                            if wx >= (n_attempts - 1):
                                connection_error_occurred = True
                        except requests.exceptions.ProxyError:
                            logging.error('market_data: {0}: Could not connect to proxy.'.format(date_str))

                            if update_function is not None:
                                update_message = '{0}: Could not connect to proxy.'.format(date_str)
                                update_function(update_message
                                )

                            if wx >= (n_attempts - 1):
                                connection_error_occurred = True
                        except requests.ConnectionError as e:
                            logging.error(
                                'market_data: {0}: Failed to establish a connection to the host server.'.format(
                                    date_str))

                            if update_function is not None:
                                update_message = '{0}: Failed to establish a connection to the host server.'.format(date_str)
                                update_function(update_message)

                            if wx >= (n_attempts - 1):
                                connection_error_occurred = True
                        except requests.Timeout as e:
                            trydownloaddate = True
                            logging.error('market_data: {0}: The connection timed out.'.format(date_str))

                            if update_function is not None:
                                update_message = '{0}: The connection timed out.'.format(date_str)
                                update_function(update_message)

                            if wx >= (n_attempts - 1):
                                connection_error_occurred = True
                        except requests.RequestException as e:
                            logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                            if wx >= (n_attempts - 1):
                                connection_error_occurred = True
                        except Exception as e:
                            # Something else went wrong.
                            logging.error(
                                'market_data: {0}: An unexpected error has occurred. ({1})'.format(date_str,
                                                                                                        repr(e)))

                            if update_function is not None:
                                update_message = '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))
                                update_function(update_message)

                            if wx >= (n_attempts - 1):
                                connection_error_occurred = True
                        
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
                    logging.info('market_data: {0}: {1} file already exists, skipping...'.format(date_str, lmp_or_mpc_folder[sx]))

                if update_function is not None:
                    update_function(1)

                # # Quit?
                # if App.get_running_app().root.stop.is_set():
                #     # Stop running this thread so the main Python process can exit.
                #     self.n_active_threads -= 1
                #     return

    if update_function is not None:
        update_function(-1)

    return connection_error_occurred


def download_nyiso_data(save_directory, datetime_start, datetime_end=None, typedat='both', RT_DAM='both', zone_gen='both', ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified NYISO data to the specified local directory.

    Downloads day-ahead and/or real-time LBMP and/or ASP data using the NYISO OASIS portal. The files are downloaded as compressed .zip archives and extracted into monthly folders.

    Parameters
    ----------
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | NYISO.
    datetime_start : datetime.datetime
        The beginning month and year for which to obtain data 
    datetime_end : datetime.datetime
        The ending month and year, inclusive, for which to obtain data, defaults to None. If None, then only the month specified by datetime_start is used.
    typedat : str
        The type of data to download: 'lbmp' for location-based marginal price, 'asp' for ancillary service price, or 'both' for both, defaults to 'both'
    RT_DAM : str
        The type of data to download: 'RT' for real-time, 'DAM' for day-ahead, or 'both' for both, defaults to 'both' 
    zone_gen : str
        The class of nodes to download data for: 'zone' for zonal, 'gen' for generator, or 'both' for both, defaults to 'both'
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
    Validated for 2013 and later.
    """
    connection_error_occurred = False

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
            datadownload_url = ''.join(
                ['http://mis.nyiso.com/public/csv/', 
                dam_or_rt_nam_x, '/', 
                date_str, '01', 
                dam_or_rt_nam_x,
                zone_or_gen_nam[sx], "_csv.zip"]
            )

            destination_dir = os.path.join(save_directory, 'NYISO', lbmp_or_asp_folder[sx], dam_or_rt_folder[sx],
                                            zone_or_gen_folder[sx], date.strftime('%Y'), date.strftime('%m'))
            first_name_file = os.path.join(destination_dir,
                                            ''.join([date_str, '01', dam_or_rt_nam_x, zone_or_gen_nam[sx], '.csv']))

            if not os.path.exists(first_name_file):
                trydownloaddate = True
                wx = 0
                while trydownloaddate:
                    # # Quit?
                    # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                    #     # Stop running this thread so the main Python process can exit.
                    #     self.n_active_threads -= 1
                    #     return

                    wx = wx + 1
                    if wx >= n_attempts:
                        logging.warning('market_data: {0} {1}: Hit download retry limit.'.format(date_str, lbmp_or_asp_folder[sx]))

                        if update_function is not None:
                            update_message = '{0} {1}: Hit download retry limit.'.format(date_str, lbmp_or_asp_folder[sx])
                            update_function(update_message)

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
                        logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                        if update_function is not None:
                            update_message = '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)
                            update_function(update_function)

                        if wx >= (n_attempts  - 1):
                            connection_error_occurred = True
                    except requests.exceptions.ProxyError:
                        logging.error('market_data: {0}: Could not connect to proxy.'.format(date_str))

                        if update_function is not None:
                            update_message = '{0}: Could not connect to proxy.'.format(date_str)
                            update_function(update_message)

                        if wx >= (n_attempts - 1):
                            connection_error_occurred = True
                    except requests.ConnectionError as e:
                        logging.error(
                            'market_data: {0}: Failed to establish a connection to the host server.'.format(
                                date_str))

                        if update_function is not None:
                            update_message = '{0}: Failed to establish a connection to the host server.'.format(date_str)
                            update_function(update_message)

                        if wx >= (n_attempts - 1):
                            connection_error_occurred = True
                    except requests.Timeout as e:
                        trydownloaddate = True
                        logging.error('market_data: {0}: The connection timed out.'.format(date_str))

                        if update_function is not None:
                            update_message = '{0}: The connection timed out.'.format(date_str)
                            update_function(update_message)

                        if wx >= (n_attempts - 1):
                            connection_error_occurred = True
                    except requests.RequestException as e:
                        logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                        if wx >= (n_attempts - 1):
                            connection_error_occurred = True
                    except Exception as e:
                        # Something else went wrong.
                        logging.error(
                            'market_data: {0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))
                        )

                        if update_function is not None:
                            update_message = '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))
                            update_function(update_message)

                        if wx >= (n_attempts - 1):
                            connection_error_occurred = True
                    else:
                        os.makedirs(destination_dir, exist_ok=True)
                        z = zipfile.ZipFile(io.BytesIO(http_request.content))
                        z.extractall(destination_dir)
            else:
                # Skip downloading the daily file if it already exists where expected.
                logging.info('market_data: {0}: {1} file already exists, skipping...'.format(
                    date_str, lbmp_or_asp_folder[sx])
                    )
                
                # if update_function is not None:
                #     update_message = '{0}: {1} file already exists, skipping...'.format(date_str, lbmp_or_asp_folder[sx])
                #     update_function(update_message)

            if update_function is not None:
                update_function(1)

            # # Quit?
            # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
            #     # Stop running this thread so the main Python process can exit.
            #     self.n_active_threads -= 1
            #     return

    if update_function is not None:
        update_function(-1)
    
    return connection_error_occurred


def download_miso_data(save_directory, datetime_start, datetime_end=None, ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified MISO data to the specified local directory.

    Downloads day-ahead LMP and MCP data into monthly packages using the MISO market reports portal.

    Parameters
    ----------
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | MISO.
    datetime_start : datetime.datetime
        The beginning month and year for which to obtain data 
    datetime_end : datetime.datetime
        The ending month and year, inclusive, for which to obtain data, defaults to None. If None, then only the month specified by datetime_start is used.
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
    Validated for 2015 and later.
    """
    connection_error_occurred = False

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
            # # Quit?
            # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
            #     # Stop running this thread so the main Python process can exit.
            #     self.n_active_threads -= 1
            #     return

            date = dt.date(year, month, day)
            date_str = date.strftime('%Y%m%d')

            # LMP call.
            lmp_url = ''.join(['https://docs.misoenergy.org/marketreports/', date_str, '_da_exante_lmp.csv'])
            destination_dir = os.path.join(save_directory, 'MISO', 'LMP', date.strftime('%Y'), date.strftime('%m'))
            destination_file = os.path.join(destination_dir, '_'.join([date_str, 'da_exante_lmp.csv']))

            if os.path.exists(destination_file):
                # Skip downloading the daily file if it already exists where expected.
                logging.info('market_data: {0}: LMP file already exists, skipping...'.format(date_str))
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
                    logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                    if update_function is not None:
                        update_message = '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.ConnectionError as e:
                    logging.error('market_data: {0}: Failed to establish a connection to the host server.'.format(date_str))

                    if update_function is not None:
                        update_message = '{0}: Failed to establish a connection to the host server.'.format(date_str)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.Timeout as e:
                    logging.error('market_data: {0}: The connection timed out.'.format(date_str))

                    if update_function is not None:
                        update_message = '{0}: The connection timed out.'.format(date_str)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.RequestException as e:
                    logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                    connection_error_occurred = True
                except Exception as e:
                    # Something else went wrong.
                    logging.error('market_data: {0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e)))

                    if update_function is not None:
                        update_message = '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))
                        update_function(update_message)

                    connection_error_occurred = True
                else:
                    os.makedirs(destination_dir, exist_ok=True)
                    output_file = open(destination_file, 'w')
                    output_file.write(data)
                    output_file.close()

            if update_function is not None:
                update_function(1)
            
            # MCP call.
            mcp_url = ''.join(['https://docs.misoenergy.org/marketreports/', date_str, '_asm_exante_damcp.csv'])
            destination_dir = os.path.join(save_directory, 'MISO', 'MCP', date.strftime('%Y'), date.strftime('%m'))
            destination_file = os.path.join(destination_dir, '_'.join([date_str, 'asm_exante_damcp.csv']))

            if os.path.exists(destination_file):
                # Skip downloading the daily file if it already exists where expected.
                logging.info('market_data: {0}: MCP file already exists, skipping...'.format(date_str))
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
                    logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))

                    if update_function is not None:
                        update_message = '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.exceptions.ProxyError:
                    logging.error('market_data: {0}: Could not connect to proxy.'.format(date_str))

                    if update_function is not None:
                        update_message = '{0}: Could not connect to proxy.'.format(date_str)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.ConnectionError as e:
                    logging.error('market_data: {0}: Failed to establish a connection to the host server.'.format(date_str))

                    if update_function is not None:
                        update_message = '{0}: Failed to establish a connection to the host server.'.format(date_str)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.Timeout as e:
                    logging.error('market_data: {0}: The connection timed out.'.format(date_str))

                    if update_function is not None:
                        update_message = '{0}: The connection timed out.'.format(date_str)
                        update_function(update_message)

                    connection_error_occurred = True
                except requests.RequestException as e:
                    logging.error('market_data: {0}: {1}'.format(date_str, repr(e)))
                    connection_error_occurred = True
                except Exception as e:
                    # Something else went wrong.
                    logging.error('market_data: {0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e)))

                    if update_function is not None:
                        update_message = '{0}: An unexpected error has occurred. ({1})'.format(date_str, repr(e))
                        update_function(update_message)

                    connection_error_occurred = True
                else:
                    os.makedirs(destination_dir, exist_ok=True)
                    output_file = open(destination_file, 'w')
                    output_file.write(data)
                    output_file.close()
            
            if update_function is not None:
                update_function(1)

    if update_function is not None:
        update_function(-1)
    
    return connection_error_occurred


def get_pjm_nodes(subs_key, startdate, nodetype=None, proxy_settings=None, ssl_verify=True):
    """Returns the list of node IDs in PJM for which day-ahead hourly LMP data is available.

    This function queries the day-ahead hourly LMP API for PJM, filtering for nodes of type `nodetype`. 

    Parameters
    ----------
    subs_key : str
        PJM Data Miner 2 API subscription key
    startdate : str
        The beginning month and year for which to collect the nodes list from, format is 'YYYYMM' 
    nodetype : str
        'ZONE', 'LOAD', 'GEN', 'AGGREGATE', 'HUB', 'EHV', 'INTERFACE', 'EXT', 'RESIDUAL_METERED_EDC'
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    
    Returns
    -------
    list[str]
        List of node IDs of type `nodetype` from `startdate` to the present
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

    if nodetype is not None:
        params_dict['type'] = nodetype
    else:
        return []

    try:
        dodownload = True
        ix = 0

        while dodownload:
            response = requests.get("https://api.pjm.com/api/v1/da_hrl_lmps?", params=params_dict, headers=headers, proxies=proxy_settings, timeout=10, verify=ssl_verify)

            dataheaders = response.headers
            data_text = response.json()
            df_data = pd.DataFrame.from_dict(data_text)
            total_nrows = float(dataheaders['X-TotalRows'])

            if total_nrows > 1000000:
                raise ValueError("Can't get so much data in a particular API search!!!")

            if ix == 0:
                df_data_all = df_data
            else:
                df_data_all = pd.concat([df_data_all, df_data], ignore_index=True)

            params_dict['startRow'] = str(50000 * (ix + 1) + 1)

            nloops = math.ceil(total_nrows / 50000) - 1

            if ix >= nloops:
                dodownload = False

            ix += 1

        nodelist = df_data_all.pnode_id.unique()
        nodelist = nodelist.astype(str)
        nodelist = nodelist.tolist()

        return nodelist
    except Exception as e:
        print(repr(e))
        return []


def download_pjm_data(save_directory, subs_key, datetime_start, datetime_end=None, typedat='all', nodes=[], ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified PJM data to the specified local directory.

    Downloads data into monthly packages using the PJM Data Miner 2 API.

    Parameters
    ----------
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | MISO.
    subs_key : str
        PJM Data Miner 2 API subscription key
    datetime_start : datetime.datetime
        The beginning month and year for which to obtain data 
    datetime_end : datetime.datetime
        The ending month and year, inclusive, for which to obtain data, defaults to None. If None, then only the month specified by datetime_start is used.
    typedat : str
        The type of data to download: 'lmp' for locational marginal price, 'reg' for regulation price, or 'mileage' for regulation mileage, 'all' for all, defaults to 'all'
    nodes : list[str]
        Node IDs and/or node types to obtain LMPs for. Node types include: 'ZONE', 'LOAD', 'GEN', 'AGGREGATE', 'HUB', 'EHV', 'INTERFACE', 'EXT', 'RESIDUAL_METERED_EDC'
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
    Validated for 2009 and later.
    """
    connection_error_occurred = False

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
                    nodelist = get_pjm_nodes(subs_key, dx, nodetype=[], proxy_settings=proxy_settings, ssl_verify=ssl_verify)
                else:
                    nodelist = []
                    for node_x in nodes:

                        isnodetype = [True for nodetypePJM_x in nodetypesPJM if node_x == nodetypePJM_x]

                        if isnodetype:
                            nodelist_x = get_pjm_nodes(subs_key, dx, nodetype=node_x, proxy_settings=proxy_settings, ssl_verify=ssl_verify)
                            nodelist = nodelist + nodelist_x
                        else:
                            nodelist.append(node_x)

                logging.info('PJMdownloader: Number of nodes in this call: {0}.'.format(str(len(nodelist))))
                pnode_look_list = nodelist
            elif lmp_or_reg[ixlp] == "reg":
                pnode_look_list = ["n/a"]
            elif lmp_or_reg[ixlp] == "mileage":
                pnode_look_list = ["n/a"]
            
            if update_function is not None:
                # Increase progress bar maximum by number of nodes.
                update_function(len(pnode_look_list))

            for pnode_x in pnode_look_list:
                pnode_look = pnode_x

                log_identifier = '{date}, {pnode}, {dtype}'.format(date=dx, dtype=lmp_or_reg[ixlp], pnode=pnode_look)

                nfilesave = "error.csv"
                if lmp_or_reg[ixlp] == "lmp":
                    des_dir = save_directory + folderprice[ixlp] + pnode_look + "/" + yearx + "/"
                    nfilesave = dx + "_dalmp_" + pnode_look + ".csv"
                elif lmp_or_reg[ixlp] == "reg":
                    # des_dir = foldersave + folderprice[ixlp] + yearx + "/" + monthx + "/"
                    des_dir = save_directory + folderprice[ixlp] + yearx + "/"
                    nfilesave = dx + "_regp" + ".csv"
                elif lmp_or_reg[ixlp] == "mileage":
                    des_dir = save_directory + folderprice[ixlp] + yearx + "/"
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
                            # # Quit?
                            # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                            #     # Stop running this thread so the main Python process can exit.
                            #     self.n_active_threads -= 1
                            #     return

                            with requests.Session() as response:
                                response = requests.get(urlPJM_list_x, params=params_dict,headers=headers, proxies=proxy_settings, timeout=10, verify=ssl_verify)
                            
                            # Check the HTTP status code.
                            if response.status_code == requests.codes.ok:
                                dataheaders = response.headers
                                data_text = response.json()
                                df_data = pd.DataFrame.from_dict(data_text)
                                total_nrows = float(dataheaders['X-TotalRows'])

                                if ix == 0:
                                    df_data_all = df_data
                                else:
                                    df_data_all = pd.concat([df_data_all, df_data], ignore_index=True)

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

                        if update_function is not None:
                            update_message = '{0}: HTTPError: {1}'.format(log_identifier, e.response.status_code)
                            update_function(update_message)

                        connection_error_occurred = True
                    except requests.exceptions.ProxyError:
                        logging.error('PJMdownloader: {0}: Could not connect to proxy.'.format(log_identifier))

                        if update_function is not None:
                            update_message = '{0}: Could not connect to proxy.'.format(log_identifier)
                            update_function(update_message)

                        connection_error_occurred = True
                    except requests.ConnectionError as e:
                        logging.error('PJMdownloader: {0}: Failed to establish a connection to the host server.'.format(log_identifier))

                        if update_function is not None:
                            update_message = '{0}: Failed to establish a connection to the host server.'.format(log_identifier)
                            update_function(update_message)

                        connection_error_occurred = True
                    except (socket.timeout, requests.Timeout) as e:
                        logging.error('PJMdownloader: {0}: The connection timed out.'.format(log_identifier))

                        if update_function is not None:
                            update_message = '{0}: The connection timed out.'.format(log_identifier)
                            update_function(update_message)

                        connection_error_occurred = True
                    except requests.RequestException as e:
                        logging.error('PJMdownloader: {0}: {1}'.format(log_identifier, repr(e)))

                        connection_error_occurred = True
                    except Exception as e:
                        # Something else went wrong.
                        logging.error('PJMdownloader: {0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e)))

                        if update_function is not None:
                            update_message = '{0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e))
                            update_function(update_message)

                        connection_error_occurred = True
                else:
                    logging.info('PJMdownloader: {0}: File already exists, skipping...'.format(log_identifier))
                
                if update_function is not None:
                    update_function(1)

                # # Quit?
                # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                #     # Stop running this thread so the main Python process can exit.
                #     self.n_active_threads -= 1
                #     return
    
    if update_function is not None:
        update_function(-1)
    
    return connection_error_occurred


def download_caiso_data(save_directory, datetime_start, datetime_end=None, typedat='all', nodes=[], ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Downloads specified CAISO data to the specified local directory.

    Downloads data into monthly packages using the CAISO API.

    Parameters
    ----------
    save_directory : str
        The base directory where the requested data is to be saved. Subdirectories will be created under the structure of save_directory | CAISO.
    datetime_start : datetime.datetime
        The beginning month and year for which to obtain data 
    datetime_end : datetime.datetime
        The ending month and year, inclusive, for which to obtain data, defaults to None. If None, then only the month specified by datetime_start is used.
    typedat : str
        The type of data to download: 'lmp' for locational marginal price, 'asp' for ancillary service price, 'mileage' for regulation mileage, or 'all' for all, defaults to 'all'
    nodes : list[str]
        Node IDs and/or node types to obtain LMPs for. Node types include: 'TH', 'ASP'
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
    Validated for 2015 and later.

    The CAISO API limits requests to approximately one every five seconds. Sleep/wait functions are used to accomodate this restriction. Since ASP data is acquired in daily calls, it may take especially long to download ASP data.
    """
    connection_error_occurred = False

    if not datetime_end:
        datetime_end = datetime_start
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    listnodes_file = os.path.join(current_dir, '..', 'apps', 'data_manager', '_static', 'nodes_caiso.csv')

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
                    destination_dir = os.path.join(save_directory, 'CAISO', folderdata[ixlp], pnode_look, date.strftime('%Y'))
                    destination_file = os.path.join(destination_dir,
                                                    ''.join([date_str, "_dalmp_", pnode_look, ".csv"]))
                elif case_dwn[ixlp] == "asp":
                    destination_dir = os.path.join(save_directory, 'CAISO', folderdata[ixlp], date.strftime('%Y'))
                    destination_file = os.path.join(destination_dir, ''.join([date_str, "_asp.csv"]))
                elif case_dwn[ixlp] == "mileage":
                    destination_dir = os.path.join(save_directory, 'CAISO', folderdata[ixlp], date.strftime('%Y'))
                    destination_file = os.path.join(destination_dir, ''.join([date_str, "_regm.csv"]))

                if not os.path.exists(destination_file):
                    if case_dwn[ixlp] == "asp":
                        dwn_ok = True
                        for dayx in range(n_days_month):
                            # # Quit?
                            # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                            #     # Stop running this thread so the main Python process can exit.
                            #     self.n_active_threads -= 1
                            #     return

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

                            df_data_x, dwn_ok_x, connection_error_occurred = _ddownloader_caiso(
                                url_CAISO, 
                                case_dwn[ixlp], 
                                datesquery_start,
                                datesquery_end, 
                                pnode_look, 
                                log_identifier,
                                ssl_verify=ssl_verify,
                                proxy_settings=proxy_settings,
                                n_attempts=n_attempts,
                                update_function=update_function
                                )
                            dwn_ok = dwn_ok and dwn_ok_x
                            if dwn_ok:
                                if dayx == 0:
                                    df_data = df_data_x
                                else:
                                    df_data = pd.concat([df_data, df_data_x], ignore_index=True)
                            else:
                                break

                    else:
                        # # Quit?
                        # if App.get_running_app().root.stop.is_set() or self.request_cancel.is_set():
                        #     # Stop running this thread so the main Python process can exit.
                        #     self.n_active_threads -= 1
                        #     return
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

                            # 1st download
                            log_identifier = '{date}A, {pnode}, {dtype}'.format(date=date_str, dtype=case_dwn[ixlp],
                                                                                pnode=pnode_look)
                            df_data1, dwn1_ok, connection_error_occured = _ddownloader_caiso(
                                url_CAISO, 
                                case_dwn[ixlp], 
                                datesquery_start,
                                datesquery_end,
                                pnode_look, 
                                log_identifier, 
                                ssl_verify=ssl_verify,
                                proxy_settings=proxy_settings,
                                n_attempts=n_attempts,
                                update_function=update_function
                                )

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
                            df_data2, dwn2_ok, connection_error_occured = _ddownloader_caiso(
                                url_CAISO, 
                                case_dwn[ixlp], 
                                datesquery_start,
                                datesquery_end,
                                pnode_look, 
                                log_identifier, 
                                ssl_verify=ssl_verify,
                                proxy_settings=proxy_settings,
                                n_attempts=n_attempts,
                                update_function=update_function
                                )

                            # Concatenate the two dataframes
                            dwn_ok = dwn1_ok and dwn2_ok

                            if dwn_ok:
                                df_data = pd.concat([df_data1, df_data2], ignore_index=True)
                        else:
                            df_data, dwn_ok, connection_error_occured = _ddownloader_caiso(
                                url_CAISO, 
                                case_dwn[ixlp], 
                                datesquery_start,
                                datesquery_end,
                                pnode_look, 
                                log_identifier, 
                                ssl_verify=ssl_verify,
                                proxy_settings=proxy_settings,
                                n_attempts=n_attempts,
                                update_function=update_function
                                )

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
                    logging.info('market_data: {0}: File already exists, skipping...'.format(log_identifier))
                
                if update_function is not None:
                    update_function(1)

    if update_function is not None:
        update_function(-1)
    
    return connection_error_occurred


def _ddownloader_caiso(URL, case_dwn_x, datesquery_start, datesquery_end, pnode_look, log_identifier, ssl_verify=True, proxy_settings=None, n_attempts=7, update_function=None):
    """Helper function for download_caiso_data() that executes the API query.
    """
    url_CAISO = URL

    connection_error_occurred = False

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
        # # Quit?
        # if App.get_running_app().root.stop.is_set():
        #     # Stop running this thread so the main Python process can exit.
        #     trydownloaddate = False
        #     break

        wx = wx + 1

        if wx >= n_attempts:
            print("Hit wx limit")
            trydownloaddate = False
            break

        try:
            with requests.Session() as req:
                http_request = req.get(url_CAISO, params=params_dict, proxies=proxy_settings, timeout=7,
                                        verify=ssl_verify)

                # Check the HTTP status code.
                if http_request.status_code == requests.codes.ok:
                    trydownloaddate = False
                elif http_request.status_code == 429:
                    # time.sleep(5.5)  # delays for 5.5 seconds
                    http_request.raise_for_status()
                else:
                    # time.sleep(5.1)  # delays for 5.1 seconds
                    http_request.raise_for_status()
        except requests.HTTPError as e:
            logging.error('market_data: {0}: {1}'.format(log_identifier, repr(e)))

            if update_function is not None:
                update_message = '{0}: HTTPError: {1}'.format(log_identifier, e.response.status_code)
                update_function(update_message)

            if wx >= (n_attempts - 1):
                connection_error_occurred = True
        except requests.exceptions.ProxyError:
            logging.error('market_data: {0}: Could not connect to proxy.'.format(log_identifier))

            if update_function is not None:
                update_message = '{0}: Could not connect to proxy.'.format(log_identifier)
                update_function(update_message)

            if wx >= (n_attempts - 1):
                connection_error_occurred = True
        except requests.ConnectionError as e:
            logging.error(
                'market_data: {0}: Failed to establish a connection to the host server.'.format(log_identifier))
            
            if update_function is not None:
                update_message = '{0}: Failed to establish a connection to the host server.'.format(log_identifier)
                update_function(update_message)

            if wx >= (n_attempts - 1):
                connection_error_occurred = True
        except (socket.timeout, requests.Timeout) as e:
            logging.error('market_data: {0}: The connection timed out.'.format(log_identifier))

            if update_function is not None:
                update_message = '{0}: The connection timed out.'.format(log_identifier)
                update_function(update_message)

            if wx >= (n_attempts - 1):
                connection_error_occurred = True
        except requests.RequestException as e:
            logging.error('market_data: {0}: {1}'.format(log_identifier, repr(e)))

            if wx >= (n_attempts - 1):
                connection_error_occurred = True
        except Exception as e:
            # Something else went wrong.
            logging.error(
                'market_data: {0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e)))

            if update_function is not None:
                update_message = '{0}: An unexpected error has occurred. ({1})'.format(log_identifier, repr(e))
                update_function(update_message)

            if wx >= (n_attempts - 1):
                connection_error_occurred = True
        else:
            trydownloaddate = False

            z = zipfile.ZipFile(io.BytesIO(http_request.content))
            fnameopen = z.filelist[0].filename

            if fnameopen[-4:] == '.csv':
                fcsv = z.open(fnameopen)
                df_data = pd.read_csv(fcsv)

                logging.info('market_data: {0}: Successfully downloaded.'.format(log_identifier))

                # time.sleep(5.2)  # delays for 5.2 seconds
                dwn_ok = True
            elif fnameopen[-4:] == '.xml':
                fxml = z.open(fnameopen)
                # xmlsoup = BeautifulSoup(fxml, 'xml')
                xmlsoup = BeautifulSoup(fxml, 'html.parser')
                err_xml = xmlsoup.find_all('ERR_CODE')

                try:
                    err_xml = err_xml[0].contents[0]
                    if err_xml=='1015':
                        trydownloaddate = True
                    else:
                        dwn_ok = False
                        logging.info('market_data: {0}: 1015: GroupZip DownLoad is in Processing, Please Submit request after Sometime.'.format(log_identifier))
                except IndexError:
                    dwn_ok = False
                    logging.info('market_data: {0}: No data returned for this request.'.format(log_identifier))
            else:
                dwn_ok = False
                logging.info('market_data: {0}: Not a valid download request.'.format(log_identifier))

        time.sleep(5.1)  # delays for 5.1 seconds

    return df_data, dwn_ok, connection_error_occurred


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    import getpass

    log_name = 'market_data.log'

    with open(log_name, 'w'):
        pass

    logging.basicConfig(filename=log_name, format='[%(levelname)s] %(asctime)s: %(message)s',
                        level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    ssl_verify = False
    proxy_settings = {'http_proxy': 'wwwproxy.sandia.gov:80', 'https_proxy': 'wwwproxy.sandia.gov:80'}

    save_directory = 'test'

    datetime_start = datetime.datetime(2019, 7, 1)

    def _update_function(update):
        if isinstance(update, int):
            if update == -1:
                print('closing thread')
            else:
                print('incrementing progress_bar')
        elif isinstance(update, str):
            print('>>', update)

    # cnx_error = download_ercot_data(
    #     save_directory, 
    #     year='all', 
    #     typedat='both', 
    #     ssl_verify=ssl_verify, 
    #     proxy_settings=proxy_settings, 
    #     n_attempts=7,
    #     update_function=_update_function
    #     )

    # node_list = ['HUBS',]
    # username = 'rconcep@sandia.gov'
    # password = getpass.getpass(prompt='ISO-NE ISO Express password: ')
    
    # cnx_error = download_isone_data(
    #     username=username, 
    #     password=password, 
    #     save_directory=save_directory, 
    #     datetime_start=datetime_start, 
    #     datetime_end=None, 
    #     nodes=node_list, 
    #     typedat='all', 
    #     ssl_verify=ssl_verify, 
    #     proxy_settings=proxy_settings, 
    #     n_attempts=7, 
    #     update_function=_update_function
    #     )

    # cnx_error = download_spp_data(
    #     save_directory=save_directory, 
    #     datetime_start=datetime_start, 
    #     datetime_end=None, 
    #     bus_loc='both', 
    #     typedat='all', 
    #     ssl_verify=ssl_verify, 
    #     proxy_settings=proxy_settings, 
    #     n_attempts=7, 
    #     update_function=_update_function
    # )

    cnx_error = download_nyiso_data(
        save_directory=save_directory, 
        datetime_start=datetime_start, 
        datetime_end=None, 
        typedat='both', 
        RT_DAM='both', 
        zone_gen='both', 
        ssl_verify=ssl_verify, 
        proxy_settings=proxy_settings, 
        n_attempts=7, 
        update_function=_update_function
        )

    # cnx_error = download_miso_data(
    #     save_directory=save_directory, 
    #     datetime_start=datetime_start, 
    #     datetime_end=None, 
    #     ssl_verify=ssl_verify, 
    #     proxy_settings=proxy_settings, 
    #     n_attempts=7, 
    #     update_function=_update_function
    # )

    # subs_key = '7eed848380df4fe5b2401d125aaecc8f'

    # node_list = get_pjm_nodes(
    #     subs_key=subs_key,
    #     startdate='201909',
    #     nodetype='HUB',
    #     proxy_settings=proxy_settings,
    #     ssl_verify=ssl_verify
    # )
    # print(node_list)

    # cnx_error = download_pjm_data(
    #     save_directory=save_directory, 
    #     subs_key=subs_key,
    #     datetime_start=datetime_start, 
    #     datetime_end=None, 
    #     typedat='all', 
    #     nodes=['HUB',], 
    #     ssl_verify=ssl_verify, 
    #     proxy_settings=proxy_settings, 
    #     n_attempts=7, 
    #     update_function=_update_function
    #     )

    # cnx_error = download_caiso_data(
    #     save_directory=save_directory, 
    #     datetime_start=datetime_start, 
    #     datetime_end=None, 
    #     typedat='all', 
    #     nodes=['ASP',], 
    #     ssl_verify=ssl_verify, 
    #     proxy_settings=proxy_settings, 
    #     n_attempts=7, 
    #     update_function=_update_function
    #     )
    