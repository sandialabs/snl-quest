# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 08:21:28 2021.

@author: wolis
"""

from __future__ import absolute_import

import logging
import calendar
import pandas as pd
from eppy.modeleditor import IDF

from kivy.clock import Clock

from es_gui.tools.performance.Battery_v2 import Battery as bt
from es_gui.tools.performance.Grid_simulator import Grid_simulator as gs
from es_gui.resources.widgets.common import WarningPopup


class PerformanceSimHandler:
    """A handler for creating and solving Performance instances as requested."""

    dms = None
    solved_sims = []

    # day names, variables, actuators, and idd for EnergyPlus
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    variables = [("Zone Mean Air Temperature", "Zone One"), ('Site Outdoor Air Drybulb Temperature', 'Environment'),
                 ("Zone Thermostat Heating Setpoint Temperature", "Zone One"),
                 ("Zone Thermostat Cooling Setpoint Temperature", "Zone One"), ('Facility Total Building Electricity Demand Rate', 'Whole Building'),
                 ('Facility Total HVAC Electricity Demand Rate', 'Whole Building'), ('Facility Total Electricity Demand Rate', 'Whole Building'),
                 ('Electric Equipment Electricity Rate', 'BATTERY'), ('Site Total Zone Exfiltration Heat Loss', 'Environment'),
                 ('Site Total Zone Exhaust Air Heat Loss', 'Environment'), ('Zone Exfiltration Heat Transfer Rate', 'Zone One'),
                 ('Zone Exhaust Air Heat Transfer Rate', 'Zone One'), ('Zone Air Heat Balance Internal Convective Heat Gain Rate', 'Zone One'),
                 ('Zone Air Heat Balance Surface Convection Rate', 'Zone One'), ('Zone Air Heat Balance Outdoor Air Transfer Rate', 'Zone One'),
                 ('Zone Air Heat Balance System Air Transfer Rate', 'Zone One'), ('Zone Air Heat Balance System Convective Heat Gain Rate', 'Zone One'),
                 ('Zone Packaged Terminal Air Conditioner Total Heating Rate',
                  'Zone One PTAC'), ('Zone Packaged Terminal Air Conditioner Total Cooling Rate', 'Zone One PTAC'),
                 ('Zone Packaged Terminal Air Conditioner Electricity Rate', 'Zone One PTAC')]
    actuators = [('Zone Temperature Control', 'Heating Setpoint', 'Zone One'),
                 ('Zone Temperature Control', 'Cooling Setpoint', 'Zone One'),
                 ('ElectricEquipment', 'Electricity Rate', 'BATTERY')]
    idd = 'energyplus/Energy+.idd'
    IDF.setiddname(idd)

    def __init__(self, output_dir):
        self._output_dir = output_dir

        self.bad_run_popup = BadRunPopup()

    @property
    def output_dir(self):
        """Directory for EnergyPlus output files."""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value

    def process_requests(self, requests, *args):
        """Generate and solve EnergyPlus models based on the given requests."""
        output_dir = self.output_dir
        variables = self.variables
        actuators = self.actuators

        # get rv data
        hvac_name = requests['hvac']['name']
        hvac_path = requests['hvac']['path']
        location_name = requests['location']['name']
        location_path = requests['location']['path']
        params = requests['params']

        # reset EnergyPlus input file with selected information
        idf_obj = IDF(hvac_path)
        runperiods = idf_obj.idfobjects['RunPeriod']
        while len(runperiods) > 1:
            runperiods.pop(-1)

        if len(requests['profile']) == 1 and not requests['profile'][0]['path'] == 1:
            profile_name = requests['profile'][0]['name']
            profile_path = requests['profile'][0]['path']

            cdF = pd.read_excel(profile_path)
            cdF[['P_d', 'P_c']] /= 1000

            idf_obj = IDF(hvac_path)
            battery_obj = idf_obj.idfobjects['ElectricEquipment'][0]
            battery_obj.Design_Level = params['pRat']*1e6
            runperiod_obj = runperiods[0]
            runperiod_obj.Begin_Month = cdF['Month'].iloc[0]
            runperiod_obj.End_Month = cdF['Month'].iloc[-1]
            runperiod_obj.Begin_Year = cdF['Year'].iloc[0]
            runperiod_obj.End_Year = cdF['Year'].iloc[-1]
            month_range = calendar.monthrange(cdF['Year'].iloc[0], cdF['Month'].iloc[0])
            runperiod_obj.Begin_Day_of_Month = 1
            runperiod_obj.End_Day_of_Month = month_range[1]
            runperiod_obj.Day_of_Week_for_Start_Day = calendar.day_name[month_range[0]]

        else:
            cdF = pd.DataFrame(columns=['P_c', 'P_d', 'Month'])

            for i, profile in enumerate(requests['profile']):
                profile_op = profile['op']
                try:
                    resultsF, revenue = profile_op['optimizer'].get_results()
                except ValueError:
                    resultsF = profile_op['optimizer'].get_results()

                try:
                    month_num = list(calendar.month_abbr).index(profile_op['month'])
                except ValueError:
                    month_num = list(calendar.month_name).index(profile_op['month'])

                try:
                    year = profile_op['year']
                except KeyError:
                    year = 2020

                try:
                    resultsF['setpoint'] = resultsF['q_r'] + resultsF['q_rd'] - resultsF['q_reg'] - resultsF['q_d'] - resultsF['q_ru']
                except KeyError:
                    resultsF['P_c'] = resultsF['Pcharge']/1000  # convert to MW for E+
                    resultsF['P_d'] = resultsF['Pdischarge']/1000  # convert to MW for E+
                else:
                    resultsF['P_c'] = [value if value >= 0 else 0 for value in resultsF['setpoint']]
                    resultsF['P_d'] = [-value if value <= 0 else 0 for value in resultsF['setpoint']]

                cd = pd.concat([resultsF.reset_index()]*4).sort_values('index', axis=0).reset_index(drop=True)[['P_c', 'P_d']]
                cd['Month'] = [month_num]*len(cd.index)
                cdF = cdF.append(cd)

                try:
                    runperiod_obj = runperiods[i]
                    runperiod_obj.Name = 'Run Period {}'.format(i)
                    runperiod_obj.Begin_Month = runperiod_obj.End_Month = int(month_num)
                    runperiod_obj.Begin_Year = runperiod_obj.End_Year = int(year)
                    month_range = calendar.monthrange(int(year), int(month_num))
                    runperiod_obj.Begin_Day_of_Month = 1
                    runperiod_obj.End_Day_of_Month = month_range[1]
                    runperiod_obj.Day_of_Week_for_Start_Day = calendar.day_name[month_range[0]]
                except IndexError:
                    idf_obj.copyidfobject(runperiods[0])
                    runperiod_obj = idf_obj.idfobjects['RunPeriod'][-1]
                    runperiod_obj.Name = 'Run Period {}'.format(i)
                    runperiod_obj.Begin_Month = runperiod_obj.End_Month = int(month_num)
                    runperiod_obj.Begin_Year = runperiod_obj.End_Year = int(year)
                    month_range = calendar.monthrange(int(year), int(month_num))
                    runperiod_obj.Begin_Day_of_Month = 1
                    runperiod_obj.End_Day_of_Month = month_range[1]
                    runperiod_obj.Day_of_Week_for_Start_Day = calendar.day_name[month_range[0]]
                else:
                    print('Successful runperiod change.')

                if month_num == 5:
                    runperiod_obj.Begin_Month = 4
                    runperiod_obj.Begin_Day_of_Month = 30

            try:
                battery_obj = idf_obj.idfobjects['ElectricEquipment'][0]
                assert battery_obj.Name == 'BATTERY', 'Battery not first ElectricEquipment object...creating new'
                battery_obj.Design_Level = params['pRat']*1e6
                idf_obj.idfobjects['ElectricEquipment'][0] = battery_obj
            except IndexError or AssertionError:
                idf_obj.newidfobject("Schedule:Constant")
                new_schedule = idf_obj.idfobjects['Schedule:Constant'][-1]
                new_schedule.Name = "Battery Heat Loss Schedule"
                new_schedule.Schedule_Type_Limits_Name = "Fraction"
                new_schedule.Hourly_Value = 0

                idf_obj.newidfobject("ElectricEquipment")
                battery_obj = idf_obj.idfobjects['ElectricEquipment'][-1]
                battery_obj.Name = "BATTERY"
                battery_obj.Zone_or_ZoneList_Name = idf_obj.idfobjects['Zone'][-1].Name
                battery_obj.Schedule_Name = "Battery Heat Loss Schedule"
                battery_obj.Design_Level_Calculation_Method = "EquipmentLevel"
                battery_obj.Design_Level = params['pRat']*1e6
                battery_obj.Watts_per_Zone_Floor_Area = ''
                battery_obj.Watts_per_Person = ''
                battery_obj.Fraction_Latent = 0
                battery_obj.Fraction_Radiant = 0
                battery_obj.Fraction_Lost = 0

                idf_obj.idfobjects["Schedule:Constant"][-1] = new_schedule
                idf_obj.idfobjects["ElectricEquipment"][-1] = battery_obj
                print("New battery and schedule object added to idf...")
            else:
                print("Successful battery update")

        index = None
        for i, obj in enumerate(idf_obj.idfobjects['Construction']):
            if obj['Name'] == 'Outer Shell':
                index = i

        idf_obj.popidfobject('Construction', index)
        if params['insulation'] == 0:
            idf_obj.newidfobject('Construction', Name='Outer Shell', Outside_Layer='Corten Steel')
        else:
            ins_mat = idf_obj.idfobjects['Material:NoMass'][-1]
            ins_mat.Thermal_Resistance = params['insulation']
            idf_obj.newidfobject('Construction', Name='Outer Shell', Outside_Layer='Corten Steel', Layer_2='Insulation')

        idf_obj.idfobjects['RunPeriod'] = runperiods
        idf_obj.save()

        # run EnergyPlus simulation
        battery = bt(params['eCap'], params['pRat'], params['n_s'], params['n_p'],
                     params['q_rate'], params['v_rate'], params['r'], params['k'])
        g_sim = gs(hvac_path, location_path, output_dir, variables=variables, actuators=actuators,
                   battery=battery)
        g_sim.h_setpoint = params['h_setpoint']
        g_sim.c_setpoint = params['c_setpoint']
        g_sim.power_electronics_flag = False
        g_sim.hvac_flag = False
        g_sim.charge_discharge = cdF
        return_code = g_sim.new_simulation()

        # Energyplus has crashed...restart QuESt
        if not return_code == 0:
            self.bad_run_popup.bad_open()

        results = g_sim.get_results()

        # save results
        if len(requests['profile']) == 1:
            self._save_to_solved_ops(results, hvac_name, location_name, profile_name)
        else:
            for profile in requests['profile']:
                profile_op = profile['op']
                try:
                    month_num = list(calendar.month_abbr).index(profile_op['month'])
                except ValueError:
                    month_num = list(calendar.month_name).index(profile_op['month'])

                self._save_to_solved_ops(results.loc[results['Month'] == month_num], hvac_name, location_name, profile['name'])

        logging.info('Op Handler: Finished processing requested jobs.')

        return results

    def _solve_model(self, op):
        op.solver = self.solver_name
        op.run()

        return op

    def _save_to_solved_ops(self, results, hvac, location, profile):
        """Save the results of simulations."""
        name = ' | '.join([hvac, location, profile])

        results_dict = {}
        results_dict['name'] = name
        results_dict['results'] = results
        results_dict['hvac'] = hvac
        results_dict['location'] = location
        results_dict['profile'] = profile

        self.solved_sims.append(results_dict)

        return (name, results)

    def get_solved_sims(self):
        """Return the list of solved  objects in reverse chronological order."""
        return self.solved_sims


class BadRunPopup(WarningPopup):
    """Popup for EnergyPlus crash."""

    def __init__(self, **kwargs):
        super(BadRunPopup, self).__init__(**kwargs)

        self.popup_text.text = 'EnergyPlus had a fatal error. Please read the log or restart the QuESt App to continue.'

    def bad_open(self):
        """Open popup from main thread."""
        Clock.schedule_once(self.open)
