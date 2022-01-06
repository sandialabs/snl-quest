# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 08:21:28 2021

@author: wolis
"""

from __future__ import absolute_import

import logging
from datetime import datetime
import calendar
import pyutilib
import pandas as pd
from eppy.modeleditor import IDF

from kivy.clock import mainthread, Clock

from es_gui.tools.performance.Battery_v2 import Battery as bt
from es_gui.tools.performance.Grid_simulator import Grid_simulator as gs


class PerformanceSimHandler:
    """A handler for creating and solving ValuationOptimizer instances as requested."""
    dms = None
    solved_sims = []
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    variables = [("Zone Mean Air Temperature", "Zone One"),('Site Outdoor Air Drybulb Temperature','Environment'),("Zone Thermostat Heating Setpoint Temperature", "Zone One"),
             ("Zone Thermostat Cooling Setpoint Temperature", "Zone One"),('Facility Total Building Electricity Demand Rate', 'Whole Building'),
             ('Facility Total HVAC Electricity Demand Rate', 'Whole Building'),('Facility Total Electricity Demand Rate', 'Whole Building'),
             ('Electric Equipment Electricity Rate','BATTERY'),('Site Total Zone Exfiltration Heat Loss','Environment'),
             ('Site Total Zone Exhaust Air Heat Loss','Environment'),('Zone Exfiltration Heat Transfer Rate','Zone One'),
             ('Zone Exhaust Air Heat Transfer Rate','Zone One'),('Zone Air Heat Balance Internal Convective Heat Gain Rate','Zone One'),
             ('Zone Air Heat Balance Surface Convection Rate','Zone One'),('Zone Air Heat Balance Outdoor Air Transfer Rate','Zone One'),
             ('Zone Air Heat Balance System Air Transfer Rate','Zone One'),('Zone Air Heat Balance System Convective Heat Gain Rate','Zone One'),
             ('Zone Packaged Terminal Air Conditioner Total Heating Rate','Zone One PTAC'),('Zone Packaged Terminal Air Conditioner Total Cooling Rate','Zone One PTAC'),
                 ('Zone Packaged Terminal Air Conditioner Electricity Rate','Zone One PTAC')]
    actuators = [('Zone Temperature Control', 'Heating Setpoint', 'Zone One'),
                 ('Zone Temperature Control', 'Cooling Setpoint', 'Zone One'),
                 ('ElectricEquipment','Electricity Rate','BATTERY')]
    idd = 'energyplus/Energy+.idd'
    IDF.setiddname(idd)

    def __init__(self, output_dir):
        self._output_dir = output_dir
        
    @property
    def output_dir(self):
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self,value):
        self._output_dir = value

    def process_requests(self, requests, *args):
        """Generates and solves ValuationOptimizer models based on the given requests."""
        dms = self.dms
        output_dir = self.output_dir
        variables = self.variables
        actuators = self.actuators
        
        hvac_name = requests['hvac']['name']
        hvac_path = requests['hvac']['path']
        location_name = requests['location']['name']
        location_path = requests['location']['path']
        params = requests['params']
        
        idf_obj = IDF(hvac_path)
        runperiods = idf_obj.idfobjects['RunPeriod']
        while len(runperiods) > 1:
            runperiod = runperiods.pop(-1)
        
        if len(requests['profile']) == 1:
            profile_name = requests['profile'][0]['name']
            profile_path = requests['profile'][0]['path']
           
            cdF = pd.read_excel(profile_path)
            cdF[['P_d','P_c']] /= 1000
            
            idf_obj = IDF(hvac_path)
            battery_obj = idf_obj.idfobjects['ElectricEquipment'][0]
            battery_obj.Design_Level = params['pRat']*1e6
            runperiod_obj = runperiods[0]
            runperiod_obj.Begin_Month = cdF['Month'].iloc[0]
            runperiod_obj.End_Month = cdF['Month'].iloc[-1]
            runperiod_obj.Begin_Year = cdF['Year'].iloc[0]
            runperiod_obj.End_Year = cdF['Year'].iloc[-1]
            month_range = calendar.monthrange(cdF['Year'].iloc[0],cdF['Month'].iloc[0])
            runperiod_obj.Begin_Day_of_Month = cdF['Day'].iloc[0]
            runperiod_obj.End_Day_of_Month = cdF['Day'].iloc[-1]
            runperiod_obj.Day_of_Week_for_Start_Day = self.days[month_range[0]]

        else:            
            cdF = pd.DataFrame(columns=['P_c','P_d','Month'])
                
            for i,profile in enumerate(requests['profile']):
                profile_op = profile['op']
                try:
                    resultsF, revenue = profile_op['optimizer'].get_results()
                except ValueError:
                    resultsF = profile_op['optimizer'].get_results()
                
                month_num = list(calendar.month_abbr).index(profile_op['month'])
                try:
                    year = profile_op['year']
                except KeyError:
                    year = 2020
                    
                try:           
                    resultsF['setpoint'] = resultsF['q_r'] + resultsF['q_ru'] + resultsF['q_reg'] - resultsF['q_d'] - resultsF['q_rd']
                except KeyError:
                    print('BTM')
                    resultsF['P_c'] = resultsF['Pcharge']/1000
                    resultsF['P_d'] = resultsF['Pdischarge']/1000
                else:
                    resultsF['P_c'] = [value if value >= 0 else 0 for value in resultsF['setpoint']]
                    resultsF['P_d'] = [-value if value <= 0 else 0 for value in resultsF['setpoint']]
                    
                cd = pd.concat([resultsF.reset_index()]*4).sort_values('index',axis=0).reset_index(drop=True)[['P_c','P_d']]
                cd['Month'] = [month_num]*len(cd.index)
                cdF = cdF.append(cd)
                try:
                    runperiod_obj = runperiods[i]
                    runperiod_obj.Name = 'Run Period {}'.format(i)
                    runperiod_obj.Begin_Month = runperiod_obj.End_Month = int(month_num)
                    runperiod_obj.Begin_Year = runperiod_obj.End_Year = int(year)
                    month_range = calendar.monthrange(int(year),int(month_num))
                    runperiod_obj.Begin_Day_of_Month = month_range[0]
                    runperiod_obj.End_Day_of_Month = month_range[1]
                except IndexError:
                    idf_obj.copyidfobject(runperiods[0])
                    new_runperiod_obj = idf_obj.idfobjects['RunPeriod'][-1]
                    new_runperiod_obj.Name = 'Run Period {}'.format(i)
                    new_runperiod_obj.Begin_Month = new_runperiod_obj.End_Month = int(month_num)
                    new_runperiod_obj.Begin_Year = new_runperiod_obj.End_Year = int(year)
                    new_month_range = calendar.monthrange(int(year),int(month_num))
                    new_runperiod_obj.Begin_Day_of_Month = new_month_range[0]
                    new_runperiod_obj.End_Day_of_Month = new_month_range[1]
                else:
                    print('Successful runperiod change.')
                
            battery_obj = idf_obj.idfobjects['ElectricEquipment'][0]
            battery_obj.Design_Level = params['pRat']*1e6
        
        idf_obj.idfobjects['RunPeriod'] = runperiods
        idf_obj.save()
        battery = bt(params['eCap'],params['pRat'],params['n_s'],params['n_p'],
                     params['q_rate'],params['v_rate'],params['r'],params['k'],params['tau'])
        g_sim = gs(hvac_path, location_path, output_dir, variables=variables, actuators=actuators, 
                   battery=battery)
        g_sim.h_setpoint = params['h_setpoint']
        g_sim.c_setpoint = params['c_setpoint']
        g_sim.power_electronics_flag = False
        g_sim.hvac_flag = False
        g_sim.charge_discharge = cdF        
        g_sim.new_simulation()
        results = g_sim.get_results()
                
        if len(requests['profile']) == 1:
            solved_sim = self._save_to_solved_ops(results,hvac_name,location_name,profile_name)
        else:
            for profile in requests['profile']:
                month_num = list(calendar.month_abbr).index(profile['op']['month'])
                solved_sim = self._save_to_solved_ops(results.loc[results['Month']==month_num],hvac_name,location_name,profile['name'])

        logging.info('Op Handler: Finished processing requested jobs.')
        
        return results

    def _solve_model(self, op):
        op.solver = self.solver_name
        op.run()

        return op

#    @staticmethod
    def _save_to_solved_ops(self,results,hvac,location,profile):
        
        name = ' | '.join([hvac,location,profile])

        results_dict = {}

        results_dict['name'] = name
        results_dict['results'] = results
        results_dict['hvac'] = hvac
        results_dict['location'] = location
        results_dict['profile'] = profile

        self.solved_sims.append(results_dict)

        return (name, results)
    
    def get_solved_sims(self):
        """Returns the list of solved Optimizer objects in reverse chronological order."""
        return self.solved_sims
    
    def set_function(self,g_sim,func):
        """"""
        
        g_sim.set_callback_function('end_zone_timestep_before_zone_reporting',func)
    
class BadRunException(Exception):
    pass