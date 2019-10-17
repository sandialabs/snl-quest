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
"""The URL to the OpenEI table of investor-owned utilities.
"""


URL_OPENEI_NONIOU = "https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/672523aa-0d8a-4e6c-8a10-67e311bb1691/download/noniouzipcodes2017.csv"
"""The URL to the OpenEI table of non-investor-owned utilities.
"""

APIROOT_OPENEI = "https://api.openei.org/utility_rates?"
"""The URL to the root of OpenEI utility rate API queries.
"""


VERSION_OPENEI = "version=latest"
"""Segment of OpenEI utility rate API query denoting which version to use.
"""

REQUEST_FMT_OPENEI = "&format=json"
"""Segment of OpenEI utility rate API query denoting which return format to use.
"""


DETAIL_OPENEI = "&detail=full"
"""Segment of OpenEI utility rate API query denoting the level of detail to use.
"""


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
            connection_error_occurred = True
    
    return utility_reference_table, connection_error_occurred


def get_utility_rate_structures(eia_id, api_key, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Obtains a list of records for all rate structures for the utility identified by eia_id. 

    This function forms an API query using the api_key and eia_id which identifies the utility.

    Parameters
    ----------
    eia_id : str
        Numeric EIA ID that identifies the utility.
    api_key : str
        Alphanumeric API key for Data.gov / NREL Developer Network resources.
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.
    
    Returns
    -------
    list
        Records of utility rates in the database for the utility. The keys are the rate structure names augmented with the effective date. The values are from the JSON object returned for each rate structure. The records are sorted alphabetically and then by most recent effective date.

    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit
    """
    api_root = APIROOT_OPENEI + VERSION_OPENEI + REQUEST_FMT_OPENEI + DETAIL_OPENEI
    api_query = api_root + '&api_key=' + api_key + '&eia=' + eia_id

    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    records = []

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
            logging.error('utility_rates: {0}'.format(repr(e)))
            raise requests.ConnectionError
        except requests.exceptions.ProxyError:
            logging.error('utility_rates: Could not connect to proxy.')
            raise requests.ConnectionError
        except requests.ConnectionError as e:
            logging.error('utility_rates: Failed to establish a connection to the host server.')
            raise requests.ConnectionError
        except requests.Timeout as e:
            logging.error('utility_rates: The connection timed out.')
            raise requests.ConnectionError
        except requests.RequestException as e:
            logging.error('utility_rates: {0}'.format(repr(e)))
            raise requests.ConnectionError
        except Exception as e:
            # Something else went wrong.
            logging.error('utility_rates: An unexpected error has occurred. ({0})'.format(repr(e)))
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
    
    return records, connection_error_occurred
