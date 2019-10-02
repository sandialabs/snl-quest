"""
This module contains functions for obtaining load profiles from the OpenEI database.
"""

from __future__ import absolute_import

import os
import io
import threading
import logging

import requests
import pandas as pd
from bs4 import BeautifulSoup


DATASET_ROOT = 'https://openei.org/datasets/files/961/pub/'
COMMERCIAL_LOAD_ROOT = DATASET_ROOT + 'COMMERCIAL_LOAD_DATA_E_PLUS_OUTPUT/'
RESIDENTIAL_LOAD_ROOT = DATASET_ROOT + 'RESIDENTIAL_LOAD_DATA_E_PLUS_OUTPUT/'


def get_commercial_geographical_locations(ssl_verify=True, proxy_settings=None, n_attempts=7):
    """
    Obtains a list of records of available geographical locations for commercial building load profiles.

    Returns: A list of dictionary records 
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


def get_building_types(location_root, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """

    """
    # Convert root page content to BeautifulSoup
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
            building_types = []

            for link in building_tags.find_all('a')[1:]:
                # [1:] to skip the link to the parent directory
                csv_link = link['href']
                name = csv_link.split('_')[0]

                building_types.append({'name': name, 'link': location_root + csv_link})
            
            building_types = sorted(building_types, key=lambda t: t['name'])
    
    return building_types, connection_error_occurred


def get_building_data(csv_link, save_directory, ssl_verify=True, proxy_settings=None, n_attempts=7):
    """

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


if __name__ == '__main__':
    ssl_verify = False
    proxy_settings = {
        'http_proxy': 'wwwproxy.sandia.gov:80',
        'https_proxy': 'wwwproxy.sandia.gov:80',
    }

    download_all = False

    locations, connection_error_occured = get_commercial_geographical_locations(ssl_verify, proxy_settings)

    if download_all:
        for location in locations:
            location_root = location['link']
            building_types, connection_error_occured = get_building_types(location_root, ssl_verify, proxy_settings)

            for building_type in building_types:    
                csv_link = building_type['link']

                url_split = csv_link.split('/')
                destination_dir = os.path.join('building_data', url_split[-2])
                os.makedirs(destination_dir, exist_ok=True)

                get_building_data(csv_link, save_directory=destination_dir, ssl_verify=False, proxy_settings=proxy_settings)
    else:
        location_root = locations[-1]['link']
        building_types, connection_error_occured = get_building_types(location_root, ssl_verify, proxy_settings)
 
        csv_link = building_types[-1]['link']

        url_split = csv_link.split('/')
        destination_dir = os.path.join('', url_split[-2])
        os.makedirs(destination_dir, exist_ok=True)

        get_building_data(csv_link, save_directory=destination_dir, ssl_verify=False, proxy_settings=proxy_settings)
