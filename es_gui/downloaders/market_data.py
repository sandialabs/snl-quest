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
        The type of data to download: 'spp' for settlement point price, 'ccp' for capacity clearing prince, or 'both' for both, defaults to 'both'
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
    