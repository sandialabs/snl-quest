"""This module contains functions for obtaining utility rates from OpenEI.
"""

import os
import io
import calendar
import datetime
import logging
import datetime as dt
import json

import requests
import pandas as pd
import numpy as np

URL_OPENEI_IOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/500990ae-ada2-4791-9206-01dc68e36f12/download/iouzipcodes2017.csv"
URL_OPENEI_NONIOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/672523aa-0d8a-4e6c-8a10-67e311bb1691/download/noniouzipcodes2017.csv"
APIROOT_OPENEI = "https://api.openei.org/utility_rates?"
VERSION_OPENEI = "version=latest"
REQUEST_FMT_OPENEI = "&format=json"
DETAIL_OPENEI = "&detail=full"


def get_utility_reference_table(ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Obtains a table of records for all utilities in the U.S. utility rate database.

    This function downloads the invester-owned and non-investor-owned utility reference tables from OpenEI and combines them into a single Pandas DataFrame.

    Parameters
    ----------
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.
    
    Returns
    -------
    DataFrame
        Records of U.S. utilities in the database with keys: ['zip', 'eiaid', 'utility_name', 'state', 'service_type', 'ownership', 'comm_rate', 'ind_rate', 'res_rate']

    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit

    Notes
    -----
    See the U.S. Utility Rate Database here:

    https://openei.org/apps/USURDB/

    """
    utility_reference_table = pd.DataFrame()

    # Invester-owned utilities.
    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('utility_rates: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return

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
            logging.error('utility_rates: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('utility_rates: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('utility_rates: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('utility_rates: The connection timed out.')
        except requests.RequestException as e:
            logging.error('utility_rates: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('utility_rates: An unexpected error has occurred. ({0})'.format(repr(e)))
        else:
            data_down = http_request.content.decode(http_request.encoding)
            data_iou = pd.read_csv(io.StringIO(data_down))
    
    # Non-investor-owned utilities.
    attempt_download = True
    n_tries = 0

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('utility_rates: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return
    
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
            logging.error('utility_rates: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('utility_rates: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('utility_rates: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('utility_rates: The connection timed out.')
        except requests.RequestException as e:
            logging.error('utility_rates: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('utility_rates: An unexpected error has occurred. ({0})'.format(repr(e)))
        else:
            data_down = http_request.content.decode(http_request.encoding)
            data_noniou = pd.read_csv(io.StringIO(data_down))
        
        try:
            utility_reference_table = pd.concat([data_iou, data_noniou], ignore_index=True)
        except (UnboundLocalError, NameError):
            # Connection error prevented downloads.
            raise requests.ConnectionError
    
    return utility_reference_table, connection_error_occurred


if __name__ == '__main__':
    ssl_verify = False
    proxy_settings = None
    # proxy_settings = {'http_proxy': 'wwwproxy.sandia.gov:80', 'https_proxy': 'wwwproxy.sandia.gov:80'}

    utility_reference_table, connection_error_occurred = get_utility_reference_table(ssl_verify=ssl_verify, proxy_settings=proxy_settings)

    print(utility_reference_table.columns)
