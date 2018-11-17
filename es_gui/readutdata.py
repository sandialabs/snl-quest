# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 14:48:42 2018

@author: tunguy
"""
import urllib.request
import os
import io
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import seaborn as sb
import json
import requests

def download_utdata(**kwargs):
    url_iou="https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/500990ae-ada2-4791-9206-01dc68e36f12/download/iouzipcodes2017.csv"
    url_noniou="https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/672523aa-0d8a-4e6c-8a10-67e311bb1691/download/noniouzipcodes2017.csv"
    
    try:
        with requests.Session() as req:
            http_request = req.get(url_iou,
                                    # proxies=proxy_settings, 
                                    timeout=6, 
                                    verify=False,
                                    stream=True)
            if http_request.status_code != requests.codes.ok:
                http_request.raise_for_status()
    # except requests.HTTPError as e:
    #     logging.error('ISONEdownloader: {0}: {1}'.format(date_str, repr(e)))
    #     Clock.schedule_once(partial(self.update_output_log,
    #                                 '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    # except requests.exceptions.ProxyError:
    #     logging.error('ISONEdownloader: {0}: Could not connect to proxy.'.format(date_str))
    #     # Clock.schedule_once(
    #     #     partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    # except requests.ConnectionError as e:
    #     logging.error(
    #         'ISONEdownloader: {0}: Failed to establish a connection to the host server.'.format(date_str))
    #     Clock.schedule_once(partial(self.update_output_log,
    #                                 '{0}: Failed to establish a connection to the host server.'.format(date_str)), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    # except requests.Timeout as e:
    #     trydownloaddate = True
    #     logging.error('ISONEdownloader: {0}: The connection timed out.'.format(date_str))
    #     # Clock.schedule_once(
    #     #     partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
    #     self.thread_failed = True
    # except requests.RequestException as e:
    #     logging.error('ISONEdownloader: {0}: {1}'.format(date_str, repr(e)))
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    except Exception as e:
        # Something else went wrong.
        print(e)
        # logging.error(
        #     'ISONEdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str,repr(e)))
        # Clock.schedule_once(partial(self.update_output_log,
        #                             '{0}: An unexpected error has occurred. ({1})'.format(date_str,repr(e))), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    else:
        data_down = http_request.content.decode(http_request.encoding)
        data_iou = pd.read_csv(io.StringIO(data_down))
    
    try:
        with requests.Session() as req:
            http_request = req.get(url_noniou,
                                    # proxies=proxy_settings, 
                                    timeout=6, 
                                    verify=False,
                                    stream=True)
            if http_request.status_code != requests.codes.ok:
                http_request.raise_for_status()
    # except requests.HTTPError as e:
    #     logging.error('ISONEdownloader: {0}: {1}'.format(date_str, repr(e)))
    #     Clock.schedule_once(partial(self.update_output_log,
    #                                 '{0}: HTTPError: {1}'.format(date_str, e.response.status_code)), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    # except requests.exceptions.ProxyError:
    #     logging.error('ISONEdownloader: {0}: Could not connect to proxy.'.format(date_str))
    #     # Clock.schedule_once(
    #     #     partial(self.update_output_log, '{0}: Could not connect to proxy.'.format(date_str)), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    # except requests.ConnectionError as e:
    #     logging.error(
    #         'ISONEdownloader: {0}: Failed to establish a connection to the host server.'.format(date_str))
    #     Clock.schedule_once(partial(self.update_output_log,
    #                                 '{0}: Failed to establish a connection to the host server.'.format(date_str)), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    # except requests.Timeout as e:
    #     trydownloaddate = True
    #     logging.error('ISONEdownloader: {0}: The connection timed out.'.format(date_str))
    #     # Clock.schedule_once(
    #     #     partial(self.update_output_log, '{0}: The connection timed out.'.format(date_str)), 0)
    #     self.thread_failed = True
    # except requests.RequestException as e:
    #     logging.error('ISONEdownloader: {0}: {1}'.format(date_str, repr(e)))
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    except Exception as e:
        # Something else went wrong.
        print(e)
        # logging.error(
        #     'ISONEdownloader: {0}: An unexpected error has occurred. ({1})'.format(date_str,repr(e)))
        # Clock.schedule_once(partial(self.update_output_log,
        #                             '{0}: An unexpected error has occurred. ({1})'.format(date_str,repr(e))), 0)
    #     if wx >= (MAX_WHILE_ATTEMPTS - 1):
    #         self.thread_failed = True
    else:
        data_down = http_request.content.decode(http_request.encoding)
        data_noniou = pd.read_csv(io.StringIO(data_down))
    
    df_combined = pd.concat([data_iou, data_noniou], ignore_index=True)
    
    return df_combined

def search_utdata_byname(**kwargs):
    
    try:
        utdataframe=kwargs["utdataframe"]
    except:
        utdataframe=pd.DataFrame()
            
    try:
        utname=kwargs["utname"]
    except:
        utname="na"
           
    if len(utdataframe)>0:
        utdatabyname=utdataframe.loc[utdataframe['utility_name']==utname]
        utdatabyname=utdatabyname[['eiaid','utility_name','state','ownership']]
        utdatabyname=utdatabyname.drop_duplicates()
    else:
        utdatabyname=pd.Dataframe()
    
    return utdatabyname

def search_utdata_byzip(**kwargs):
    
    try:
        utdataframe=kwargs["utdataframe"]
    except:
        utdataframe=pd.DataFrame()
            
    try:
        utzip=kwargs["utzip"]
    except:
        utzip="na"
           
    if len(utdataframe)>0:
        utdatabyzip=utdataframe.loc[utdataframe['zip']==utzip]
        utdatabyzip=utdatabyzip[['eiaid','utility_name','state','ownership']]
        utdatabyzip=utdatabyzip.drop_duplicates()
    else:
        utdatabyzip=pd.Dataframe()
    
    return utdatabyzip

def search_utdata_bystate(**kwargs):
    
    try:
        utdataframe=kwargs["utdataframe"]
    except:
        utdataframe=pd.DataFrame()
            
    try:
        utstate=kwargs["utstate"]
    except:
        utstate="na"
           
    if len(utdataframe)>0:
        utdatabystate=utdataframe.loc[utdataframe['state']==utstate]
        utdatabystate=utdatabystate[['eiaid','utility_name','state','ownership']]
        utdatabystate=utdatabystate.drop_duplicates()
    else:
        utdatabystate=pd.Dataframe()
    
    return utdatabystate

def find_utschld(**kwargs):
    proxy_dict={}
    http_proxy_on=True
    https_proxy_on=True
    succeed=True
    
    try:
        proxy_dict["http"]=kwargs["http_proxy"]
    except:
        http_proxy_on=False

    try:
        proxy_dict["https"]=kwargs["https_proxy"]
    except:
        https_proxy_on=False
    
    try:
        eia_id="&eia="+kwargs["eiaid"]
    except:
        eia_id="no_id"
    
    try:
        api_key="&api_key="+kwargs["api_key"]
    except:
        api_key="no_key"
       
    root_url="https://api.openei.org/utility_rates?"
    version="version=5"
    request_format="&format=json"
    detail="&detail=full"
    url_openei=root_url+version+request_format+api_key+eia_id+detail
    print(url_openei)
    
    try:
        des_dir = kwargs["dirloc"]
    except:
        des_dir="./"    
    
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    
    des_file=des_dir+"schedule.json"
    
    proxy_support = urllib.request.ProxyHandler(proxy_dict)
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    try:
        urllib.request.urlretrieve(url_openei, des_file)  
    except urllib.error.URLError as e:
        print(e)
        succeed=False
    
    schld=json.loads(open(des_file).read()) 
#    schld_data=json_normalize(schld['items'])
    return schld['items'] # this is a list of schedules in which each element contains the full details of a schedule.

# Example             
utdataframe = download_utdata(https_proxy="wwwproxy.sandia.gov:80")
utdata=search_utdata_byzip(utdataframe=utdataframe,utzip=87185)
utid=utdata['eiaid'].values
print(utid)
schld_data=find_utschld(https_proxy="wwwproxy.sandia.gov:80",eiaid=str(utid[0]),api_key="QqYsZ7wI57tBiNaqc4IZfffvgWaorWER6J3D69tw")
print(len(schld_data))
print(schld_data[1].keys())