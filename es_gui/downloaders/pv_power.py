"""This module contains functions for obtaining photovoltaic power profiles from the PVWatts API.
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


URL_PVWATTS = "https://developer.nrel.gov/api/pvwatts/v6.json?"
"""The URL for the root of the PVWatts API.
"""


def get_pv_profile_data(query_parameters, save_path, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Saves the hourly photovoltaic (PV) power profile and metadata to a .json file on disk.

    This function saves the PV profile from the PVWatts query described by `query_parameters` to the path `save_path`. The format is a .json file with the format described by the PVWatts API.

    Parameters
    ----------
    query_parameters : dict
        Dictionary of parameters for PVWatts API query. The keys must match the request parameters described by the API. Parameters marked as required must be provided. See notes for more details.
    save_path : str
        Relative path, including file name and extension, for where the profile data is to be saved. The extension should be .json.
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.
    
    Returns
    -------
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit

    Notes
    -----
    Details about the API including request parameter names and requirements can be found here:

    https://developer.nrel.gov/docs/solar/pvwatts/v6/

    """
    # Form the API query based on the supplied parameters
    query_segments = []

    for k, v in query_parameters.items():
        query_segments.append('{key}={value}'.format(key=k, value=v))
    
    api_query = URL_PVWATTS + '&'.join(query_segments)

    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    while attempt_download:
        n_tries = 0

        if n_tries >= n_attempts:
            logging.warning('pv_power: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break

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
            logging.error('pv_power: {0}'.format(repr(e)))
            raise requests.ConnectionError(e)
        except requests.exceptions.ProxyError:
            logging.error('pv_power: Could not connect to proxy.')
            raise requests.ConnectionError
        except requests.ConnectionError as e:
            logging.error('pv_power: Failed to establish a connection to the host server.')
            raise requests.ConnectionError
        except requests.Timeout as e:
            logging.error('pv_power: The connection timed out.')
            raise requests.ConnectionError
        except requests.RequestException as e:
            logging.error('pv_power: {0}'.format(repr(e)))
            raise requests.ConnectionError
        except Exception as e:
            # Something else went wrong.
            logging.error('pv_power: An unexpected error has occurred. ({0})'.format(repr(e)))
            raise requests.ConnectionError
        else:
            request_content = http_request.json()

            # Save.
            if not os.path.exists(save_path):
                with open(save_path, 'w') as outfile:
                    json.dump(request_content, outfile)
    
    return connection_error_occurred
