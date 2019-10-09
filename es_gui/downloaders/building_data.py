"""This module contains functions for obtaining load profiles from the OpenEI database.
"""

from __future__ import absolute_import

import os
import io
import logging

import requests
import pandas as pd
from bs4 import BeautifulSoup


DATASET_ROOT = 'https://openei.org/datasets/files/961/pub/'
"""The URL for the root of the OpenEI load profile database directory.
"""

COMMERCIAL_LOAD_ROOT = DATASET_ROOT + 'COMMERCIAL_LOAD_DATA_E_PLUS_OUTPUT/'
"""The URL for the root of the OpenEI commercial building load profile database directory.
"""

RESIDENTIAL_LOAD_ROOT = DATASET_ROOT + 'RESIDENTIAL_LOAD_DATA_E_PLUS_OUTPUT/'
"""The URL for the root of the OpenEI residential building load profile database directory.
"""


def get_commercial_geographical_locations(ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Returns the available geographical locations for commercial building load profiles.

    This function checks the root of the commercial building database and documents the available geographical locations that can be selected based on the table of URLs.

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
    list
        Records as list of dictionaries with keys ['country', 'name', 'state', 'link'].
    
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit.
    """
    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    locations = []

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('LoadProfileDM: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return

        try:            
            with requests.Session() as req:
                page = req.get(COMMERCIAL_LOAD_ROOT, timeout=10, verify=ssl_verify, proxies=proxy_settings)
                if page.status_code != requests.codes.ok:
                    page.raise_for_status()
                else:
                    attempt_download = False
        except requests.HTTPError as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('LoadProfileDM: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('LoadProfileDM: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('LoadProfileDM: The connection timed out.')
        except requests.RequestException as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('LoadProfileDM: An unexpected error has occurred. ({0})'.format(repr(e)))
        else:
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Get the bulleted list of locations.
            location_tags = soup.body.ul
            
            # Convert bulleted list to DataFrame.
            locations = []

            for link in location_tags.find_all('a')[1:]:
                # [1:] to skip the link to the parent directory.
                loc_root = link['href']
                country, state_abbr, name, _ = loc_root.split('_')

                name = ' '.join(name.split('.')[:-1])

                locations.append({'country': country, 'state': state_abbr, 'name': name, 'link': COMMERCIAL_LOAD_ROOT + loc_root})
    
    return locations, connection_error_occurred


def get_commercial_building_types(location_root, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Returns the available commercial building types for a given geographical location.

    This function checks the specified geographical location root URL and documents the available commercial building types that can be selected based on the table of URLs.

    Parameters
    ----------
    location_root : str
        URL for the directory of a geographical location in the commercial building load profile directorate.
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.

    Returns
    -------
    list
        Records as list of dictionaries with keys ['name', 'link'].
    
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit.
    """
    # Convert root page content to BeautifulSoup
    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    building_types = []

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('LoadProfileDM: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return
        
        try:
            with requests.Session() as req:
                page = req.get(location_root, timeout=10, verify=ssl_verify, proxies=proxy_settings)
                if page.status_code != requests.codes.ok:
                    page.raise_for_status()
                else:
                    attempt_download = False
        except requests.HTTPError as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('LoadProfileDM: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('LoadProfileDM: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('LoadProfileDM: The connection timed out.')
        except requests.RequestException as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('LoadProfileDM: An unexpected error has occurred. ({0})'.format(repr(e)))
        else: 
            soup = BeautifulSoup(page.content, 'html.parser')
    
            # Get the bulleted list of building types
            building_tags = soup.body.ul
            
            # Convert bulleted list to DataFrame
            for link in building_tags.find_all('a')[1:]:
                # [1:] to skip the link to the parent directory
                csv_link = link['href']
                name = csv_link.split('_')[0]

                building_types.append({'name': name, 'link': location_root + csv_link})
            
            building_types = sorted(building_types, key=lambda t: t['name'])
    
    return building_types, connection_error_occurred


def get_building_data(csv_link, save_directory, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Saves the hourly load profile to a .csv file on disk.

    This function saves the load profile at `csv_link` to the directory `save_directory`. The format has two columns: `Date/Time` and `Electricity:Facility [kW](Hourly)`. The filename is based on the specific data obtained. Additional directories will be created in `save_directory` in which the .csv file will be saved.

    Parameters
    ----------
    csv_link : str
        URL for the .csv file containing the load profile.
    save_directory : str
        Relative path for where load profile will be saved.
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.
    """
    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('LoadProfileDM: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return
        
        try:
            with requests.Session() as req:
                page = req.get(csv_link, timeout=10, verify=ssl_verify, proxies=proxy_settings)
                if page.status_code != requests.codes.ok:
                    page.raise_for_status()
                else:
                    attempt_download = False
        except requests.HTTPError as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('LoadProfileDM: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('LoadProfileDM: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('LoadProfileDM: The connection timed out.')
        except requests.RequestException as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('LoadProfileDM: An unexpected error has occurred. ({0})'.format(repr(e)))
        else: 
            data_down = page.content.decode(page.encoding)
            csv_data = pd.read_csv(io.StringIO(data_down))

            electricity_data = csv_data[['Date/Time', 'Electricity:Facility [kW](Hourly)']]

            # Save to persistent object on disk.
            url_split = csv_link.split('/')
            destination_file = os.path.join(save_directory, url_split[-1])

            electricity_data.to_csv(destination_file, sep=',', index=False)
    
    return connection_error_occurred


def get_residential_load_types(ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Returns the available load types for residential building load profiles.

    This function checks the database for which types of load profiles are available for residential buildings. Examples include `base`, `high`, and `low`.

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
    list
        Records as list of dictionaries with keys ['name', 'link'].
    
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit.
    """
    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    load_types = []

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('LoadProfileDM: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return
        
        try:
            with requests.Session() as req:
                page = req.get(RESIDENTIAL_LOAD_ROOT, timeout=10, verify=ssl_verify, proxies=proxy_settings)
                if page.status_code != requests.codes.ok:
                    page.raise_for_status()
                else:
                    attempt_download = False
        except requests.HTTPError as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('LoadProfileDM: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('LoadProfileDM: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('LoadProfileDM: The connection timed out.')
        except requests.RequestException as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('LoadProfileDM: An unexpected error has occurred. ({0})'.format(repr(e)))
        else: 
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Get the bulleted list of locations.
            load_tags = soup.body.ul
            
            # Convert bulleted list to DataFrame.
            for link in load_tags.find_all('a')[1:]:
                # [1:] to skip the link to the parent directory.
                type_root = link['href']

                load_types.append({'name': type_root[:-1], 'link': RESIDENTIAL_LOAD_ROOT + type_root})
    
    return load_types, connection_error_occurred


def get_residential_geographical_locations(load_root_link, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """Returns the available geographical locations for the specified residential building load type.

    This function checks the database for which geographical locations are available for the specific residential load type at `load_root_link` based on the table of URLs.

    Parameters
    ----------
    load_root_link : str
        URL for the directory of a load type in the residential building load profile directorate.
    ssl_verify : bool
        True if the URL request should use SSL verification, defaults to True.
    proxy_settings : dict
        HTTP and HTTPS proxies for URL request; format is {'http_proxy': '...', 'https_proxy': '...'}, defaults to None.
    n_attempts : int
        The maximum number of retries for the URL request before declaring connection errors, defaults to 7.

    Returns
    -------
    list
        Records as list of dictionaries with keys ['country', 'state', 'name', 'link'].
    
    bool
        True if a connection error occurred during the requests and the number of retries hit the specified limit.
    """
    attempt_download = True
    n_tries = 0
    connection_error_occurred = False

    locations = []

    while attempt_download:
        n_tries += 1

        if n_tries >= n_attempts:
            logging.warning('LoadProfileDM: Hit download retry limit.')
            attempt_download = False
            connection_error_occurred = True
            break
        
        # if App.get_running_app().root.stop.is_set():
        #     return
        
        try:
            with requests.Session() as req:
                page = req.get(load_root_link, timeout=10, verify=ssl_verify, proxies=proxy_settings)
                if page.status_code != requests.codes.ok:
                    page.raise_for_status()
                else:
                    attempt_download = False
        except requests.HTTPError as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except requests.exceptions.ProxyError:
            logging.error('LoadProfileDM: Could not connect to proxy.')
        except requests.ConnectionError as e:
            logging.error('LoadProfileDM: Failed to establish a connection to the host server.')
        except requests.Timeout as e:
            logging.error('LoadProfileDM: The connection timed out.')
        except requests.RequestException as e:
            logging.error('LoadProfileDM: {0}'.format(repr(e)))
        except Exception as e:
            # Something else went wrong.
            logging.error('LoadProfileDM: An unexpected error has occurred. ({0})'.format(repr(e)))
        else: 
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Get the bulleted list of locations.
            location_tags = soup.body.ul
            
            # Convert bulleted list to DataFrame.
            locations = []

            for link in location_tags.find_all('a')[1:]:
                # [1:] to skip the link to the parent directory.
                loc_root = link['href']
                country, state_abbr, name, _, _ = loc_root.split('_')

                name = ' '.join(name.split('.')[:-1])

                locations.append({'country': country, 'state': state_abbr, 'name': name, 'link': load_root_link + loc_root})
    
    return locations, connection_error_occurred
