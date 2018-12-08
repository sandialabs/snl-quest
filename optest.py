# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:03:21 2018

@author: tunguy
"""

from __future__ import absolute_import

import logging
from datetime import datetime
import calendar
import pyutilib
import pandas as pd


from es_gui.tools.btm.btm_optimizer import BtmOptimizer, BadParameterException, IncompatibleDataException
import es_gui.tools.btm.readutdata as readut

# if __name__ == '__main__':
with open('btm_optimizer.log', 'w'):
    pass

logging.basicConfig(filename='btm_optimizer.log', format='[%(levelname)s] %(asctime)s: %(message)s',
                    level=logging.INFO)


utid=[14328] #PG&E
print(utid)
schld_data=readut.find_utschld(https_proxy="wwwproxy.sandia.gov:80",eiaid=str(utid[0]),api_key="QqYsZ7wI57tBiNaqc4IZfffvgWaorWER6J3D69tw")

#    for i in range(len(schld_data)):
#        print(i,schld_data[i]['name'])

#    print(schld_data[471].keys())
#    print(schld_data[471]['flatdemandstructure'])

wkday_eschld=schld_data[471]['energyweekdayschedule']
wkend_eschld=schld_data[471]['energyweekendschedule']
tou_erate=[schld_data[471]['energyratestructure'][i][0]['rate'] for i in range(len(schld_data[471]['energyratestructure']))]

wkday_dschld=schld_data[471]['demandweekdayschedule']
wkend_dschld=schld_data[471]['demandweekendschedule']
tou_drate=[schld_data[471]['demandratestructure'][i][0]['rate'] for i in range(len(schld_data[471]['demandratestructure']))]

flat_dschld=schld_data[471]['flatdemandmonths']
flat_drate=schld_data[471]['flatdemandstructure']

year=2016
rate_df=readut.input_df(year,wkday_eschld,wkend_eschld,wkday_dschld,wkend_dschld)
rate_df.to_csv('./rate.csv')

loadpv_df = pd.read_csv('./loadpv.csv')

month=1
rate_df_month=rate_df.loc[rate_df['month']==month]
loadpv_df_month = loadpv_df.loc[loadpv_df['month']==month] 

op = BtmOptimizer()

op.tou_energy_schedule=rate_df_month['tou_energy_schedule'].values
op.tou_energy_rate=tou_erate

op.tou_demand_schedule=rate_df_month['tou_demand_schedule'].values
op.tou_demand_rate=tou_drate

op.flat_demand_rate=flat_drate[flat_dschld[month-1]][0]['rate']
op.nem_type=1
op.nem_rate=0.03

op.load_profile=loadpv_df_month['load'].values
op.pv_profile=loadpv_df_month['pv0'].values

op.model.Transformer_rating=1000
op.model.Power_rating=200
op.model.Energy_capacity=800

results_df=op.run()
results_df.to_csv('./results.csv')