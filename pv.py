# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 17:31:16 2019

@author: tunguy
"""
import urllib.request
import os
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import seaborn as sb
import json
import holidays
from datetime import datetime
    

def download_pvdata(**kwargs):
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
    
    api_key = "api_key="+kwargs["api_key"]
    PV_CONFIG = kwargs["pv_config"]
    root_url="https://developer.nrel.gov/api/pvwatts/v6.json?"
    url_pvwatt=root_url+api_key
    
    for key,value in PV_CONFIG.items():
        url_pvwatt+='&'+key+'='+value
    try:
        des_dir = kwargs["dirloc"]
    except:
        des_dir="./"    
    
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    
    des_file=des_dir+"pv_data.json"
    proxy_support = urllib.request.ProxyHandler(proxy_dict)
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    try:
        urllib.request.urlretrieve(url_pvwatt, des_file)  
    except urllib.error.URLError as e:
        print(e)
        succeed=False
    
    pv_data=json.loads(open(des_file).read()) 

    return pv_data['outputs']['ac'] # 

# Example
PV_CONFIG={}
PV_CONFIG['lat']='35' #degree
PV_CONFIG['lon']='-106' #degree
PV_CONFIG['radius']='0' #closest station regardless of distance
PV_CONFIG['system_capacity']='1000' #kW
PV_CONFIG['module_type']= '0' #standard type
PV_CONFIG['losses']= '10' # percent
PV_CONFIG['array_type']= '0' # Open rack
PV_CONFIG['tilt']= '40' #degree
PV_CONFIG['azimuth']= '180' #degree
PV_CONFIG['timeframe']='hourly'

api_call = ''

for key,value in PV_CONFIG.items():
    api_call=api_call+'&'+key+'='+value

print(api_call)

key="QqYsZ7wI57tBiNaqc4IZfffvgWaorWER6J3D69tw"
pvdata=download_pvdata(https_proxy="wwwproxy.sandia.gov:80",api_key=key,pv_config=PV_CONFIG)
print(pvdata,len(pvdata))
