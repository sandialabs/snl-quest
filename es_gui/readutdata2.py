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
import seaborn as sb
import json
import holidays
from datetime import datetime

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

def input_df(year,wkday_er,wkend_er,wkday_dr,wkend_dr,flat_dr,nem):
    """
    Generate a Pandas dataframe from the downloaded rate schedule data.
    :param year: an integer.
    :param wkday_er: a 12x24 NumPy array, wkday_er[i][j] is the energy price in $/kWh during hour j+1 in a weekday of month i+1
    :param wkend_er: a 12x24 NumPy array, wkend_er[i][j] is the energy price in $/kWh during hour j+1 in a weekend day or a holiday of month i+1
    :param wkday_dr: a 12x24 NumPy array, wkday_dr[i][j] is the demand price in $/kW during hour j+1 in a weekday of month i+1
    :param wkend_dr: a 12x24 NumPy array, wkend_dr[i][j] is the demand price in $/kW during hour j+1 in a weekend day or a holiday of month i+1
    :param flat_dr: a float represents the flat demand price in $/kW for all hours of a month.
    :param nem: a float represents the netmetering sell price in $/kWh
    :return opt_df: a Pandas dataframe with the following template:|year|month|day|hour|toue|toud|flatd|neme|
    """
    column_list=['year','month','day','hour','toue','toud','flatd','neme']
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
                    if wkend_dr.size>1:  
                        row=[year,month,day,hour,wkend_er[month-1][hour-1],wkend_dr[month-1][hour-1],flat_dr,nem]
                    else:
                        row=[year,month,day,hour,wkend_er[month-1][hour-1],0,flat_dr,nem]
                else:
                    if wkday_dr.size>1:  
                        row=[year,month,day,hour,wkday_er[month-1][hour-1],wkday_dr[month-1][hour-1],flat_dr,nem]
                    else:
                        row=[year,month,day,hour,wkday_er[month-1][hour-1],0,flat_dr,nem]
                    
                data_list.append(row)
    opt_df=pd.DataFrame(data=data_list,columns=column_list)
    pd.DataFrame()
    return opt_df
                    
                
                
                
# Example             
utdataframe = download_utdata(https_proxy="wwwproxy.sandia.gov:80")
utdata=search_utdata_byzip(utdataframe=utdataframe,utzip=87185)
utid=utdata['eiaid'].values
print(utid)
schld_data=find_utschld(https_proxy="wwwproxy.sandia.gov:80",eiaid=str(utid[0]),api_key="QqYsZ7wI57tBiNaqc4IZfffvgWaorWER6J3D69tw")
print(len(schld_data))
print(schld_data[1].keys())

wkday_schld=schld_data[1]['energyweekdayschedule']
wkend_schld=schld_data[1]['energyweekendschedule']
energy_rate=schld_data[1]['energyratestructure']
#print(energy_rate)
wkday_er_list=[]
wkend_er_list=[]
for i in range(12):
    wkday_row=[energy_rate[wkday_schld[i][j]][0]['rate'] for j in range(24)]
    wkend_row=[energy_rate[wkend_schld[i][j]][0]['rate'] for j in range(24)]
    wkday_er_list.append(wkday_row)
    wkend_er_list.append(wkend_row)
wkday_er=np.array(wkday_er_list)
wkend_er=np.array(wkend_er_list)
wkday_dr=np.empty([])
wkend_dr=np.empty([])
flat_dr=20
nem=0.03
year=2017
opt_df=input_df(year,wkday_er,wkend_er,wkday_dr,wkend_dr,flat_dr,nem)
print(opt_df)