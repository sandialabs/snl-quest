# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 14:48:42 2018

@author: tunguy
"""
import urllib.request
import os
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import json
import holidays
from datetime import datetime
import datetime as dt

def download_utdata(**kwargs):
    url_iou="https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/500990ae-ada2-4791-9206-01dc68e36f12/download/iouzipcodes2017.csv"
    url_noniou="https://openei.org/doe-opendata/dataset/53490bd4-671d-416d-aae2-de844d2d2738/resource/672523aa-0d8a-4e6c-8a10-67e311bb1691/download/noniouzipcodes2017.csv"
    
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
        des_dir = kwargs["dirloc"]
    except:
        des_dir="./"    
        
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
        
    des_file_iou = des_dir+"iouzipcodes2017.csv"
    des_file_noniou = des_dir+"noniouzipcodes2017.csv"
    proxy_support = urllib.request.ProxyHandler(proxy_dict)
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    try:
        urllib.request.urlretrieve(url_iou, des_file_iou)  
    except urllib.error.URLError as e1:
        print(e1)
        succeed=False
    try:
        urllib.request.urlretrieve(url_noniou, des_file_noniou)  
    except urllib.error.URLError as e2:
        print(e2)
        suceed=False
        
    if succeed:
        df_iou = pd.read_csv(des_file_iou)
        df_noniou= pd.read_csv(des_file_noniou)
        utdataframe=pd.concat([df_iou,df_noniou],ignore_index=True)
    else:
        utdataframe=pd.DataFrame()
    
    return utdataframe

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

def read_load_profile(path, month):
    """Reads the annual load profile file located at path and returns the array of the load profile for the given month."""
    load_df = pd.read_csv(path)

    if isinstance(month, str):
        month = int(month)

    # Assumptions: column 0 is datetime, column 1 is data
    datetime_column_name = load_df.columns[0]
    data_column_name = load_df.columns[-1]

    # Overwrite DateTime column (esp. for data obtained from OpenEI)
    datetime_start = datetime(2019, 1, 1, 0)
    hour_range = pd.date_range(start=datetime_start, periods=len(load_df), freq="H")
    load_df[datetime_column_name] = hour_range

    # Filter by given month.
    datetime_column = pd.to_datetime(load_df[datetime_column_name])
    load_df_month = load_df.loc[datetime_column.apply(lambda x: x.month == month)]
    load_profile = load_df_month[data_column_name].values

    return load_profile

def read_pv_profile(path, month):
    """Reads the annual PV profile file located at path and returns the array of the PV profile for the given month."""
    if isinstance(month, str):
        month = int(month)
    
    with open(path) as f:
        profile_obj = json.load(f)
        
    pv_output_w = profile_obj['outputs']['ac']

    # Convert to kW.
    df_pv_output = pd.DataFrame(pv_output_w, columns=['kW'])*1e-3

    # Apply datetime index for filtering.
    datetime_start = datetime(2019, 1, 1, 0)
    hour_range = pd.date_range(start=datetime_start, periods=len(pv_output_w), freq='H')
    df_pv_output['dt'] = hour_range

    # Filter by given month.
    df_pv_month = df_pv_output.loc[df_pv_output['dt'].apply(lambda x: x.month == month)]
    pv_output_kw = df_pv_month['kW'].values

    return pv_output_kw

def get_pv_profile_string(path):
    """Reads the PV profile JSON object and returns a list of string descriptors."""
    with open(path) as f:
        profile_obj = json.load(f)
    
    module_type_list = ['Standard', 'Premium', 'Thin Film', 'N/A']
    array_type_list = ['Fixed (open rack)', 'Fixed (roof mounted)', '1-axis', '1-axis (backtracking)', '2-axis', 'N/A']
    
    query_inputs = profile_obj['inputs']

    # Skip if this is a custom/imported profile.
    if query_inputs["array_type"] == -1:
        return ["Custom",]

    coordinates = 'Location: {lat}, {lon}'.format(lat=query_inputs['lat'], lon=query_inputs['lon'])
    system_capacity = 'System Capacity: {0} kW'.format(query_inputs['system_capacity'])
    azimuth = 'Azimuth: {0} deg'.format(query_inputs['azimuth'])
    tilt = 'Tilt: {0} deg'.format(query_inputs['tilt'])
    array_type = 'Array Type: {0}'.format(array_type_list[int(query_inputs['array_type'])])
    module_type = 'Module Type: {0}'.format(module_type_list[int(query_inputs['module_type'])])
    system_losses = 'System Losses: {0}%'.format(query_inputs['losses'])

    descriptors = [
        coordinates,
        system_capacity,
        azimuth,
        tilt,
        array_type,
        module_type,
        system_losses,
    ]

    return descriptors


def input_df(year,wkday_eschld,wkend_eschld,wkday_dschld,wkend_dschld):
    """
    Generate a Pandas dataframe from the downloaded rate schedule data.
    :param year: an integer.
    :param wkday_eschld: a 12x24 NumPy array, wkday_schld[i][j] is the tou energy schedule of hour j+1 in a weekday of month i+1
    :param wkend_eschld: a 12x24 NumPy array, wkend_schld[i][j] is the tou energy schedule of hour j+1 in a weekend day or a holiday of month i+1
    :param wkday_dschld: a 12x24 NumPy array, wkday_schld[i][j] is the tou demand schedule of hour j+1 in a weekday of month i+1
    :param wkend_dschld: a 12x24 NumPy array, wkend_schld[i][j] is the tou demand schedule of hour j+1 in a weekend day or a holiday of month i+1
    
    :return opt_df: a Pandas dataframe with the following template:|year|month|day|hour|tou_energy_schedule|tou_demand_schedule|
    """
    column_list=['year','month','day','hour','tou_energy_schedule','tou_demand_schedule']
    data_list=[]
    nday={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    
    if int(year)%4==0:
        nday[2]=29
        
    us_holidays=holidays.UnitedStates()
    for month in range(1,13):
        for day in range(1,nday[month]+1):
            date=datetime(year, month, day)
            dayofweek = date.weekday()
            for hour in range(1,25):
                if (date in us_holidays) or (dayofweek>4):
                    if len(wkend_dschld)>1:  
                        row=[year,month,day,hour,wkend_eschld[month-1][hour-1],wkend_dschld[month-1][hour-1]]
                    else:
                        row=[year,month,day,hour,wkend_eschld[month-1][hour-1],0]
                else:
                    if len(wkday_dschld)>1:  
                        row=[year,month,day,hour,wkday_eschld[month-1][hour-1],wkday_dschld[month-1][hour-1]]
                    else:
                        row=[year,month,day,hour,wkday_eschld[month-1][hour-1],0]
                    
                data_list.append(row)
    opt_df=pd.DataFrame(data=data_list,columns=column_list)

    return opt_df
                    
# Example             
#utdataframe = download_utdata(https_proxy="wwwproxy.sandia.gov:80")
#utdata=search_utdata_byzip(utdataframe=utdataframe,utzip=87185)
#utid=utdata['eiaid'].values
#utid=[14328]
#print(utid)
#schld_data=find_utschld(https_proxy="wwwproxy.sandia.gov:80",eiaid=str(utid[0]),api_key="QqYsZ7wI57tBiNaqc4IZfffvgWaorWER6J3D69tw")
#
#for i in range(len(schld_data)):
#    print(i,schld_data[i]['name'])
#
#print(schld_data[471].keys())
#print(schld_data[471]['flatdemandstructure'])
#
#wkday_eschld=schld_data[471]['energyweekdayschedule']
#wkend_eschld=schld_data[471]['energyweekendschedule']
#tou_erate=schld_data[471]['energyratestructure']
#
#wkday_dschld=schld_data[471]['demandweekdayschedule']
#wkend_dschld=schld_data[471]['demandweekendschedule']
#tou_drate=schld_data[471]['demandratestructure']
#
#flat_dschld=schld_data[471]['flatdemandmonths']
#flat_drate=schld_data[471]['flatdemandstructure']
#
#year=2016
#opt_df=input_df(year,wkday_eschld,wkend_eschld,wkday_dschld,wkend_dschld)
#opt_df.to_csv('./input.csv')
#print(opt_df)