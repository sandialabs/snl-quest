# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:14:23 2020

@author: wolis
"""

import sys
import logging
from ctypes import c_void_p
import pandas as pd

from es_gui.tools.performance.Energyplus_simulator import Energyplus_simulator
from es_gui.tools.performance.Battery_v2 import Battery


class Grid_simulator(Energyplus_simulator):
    """Handles the simulation of a grid connected energy storage system."""

    def __init__(self, idf, weather, output_dir, variables=None, actuators=None,
                 battery=Battery(1, 0.5, 1, 0.9332), h_setpoint=15, c_setpoint=35,
                 load=pd.DataFrame(), charge_discharge=pd.DataFrame()):
        super().__init__(idf, weather, output_dir, variables, actuators)

        self._battery = battery
        self.h_setpoint = h_setpoint
        self.c_setpoint = c_setpoint
        self._load = load
        self._charge_discharge = charge_discharge

        self.bdata_lst = []
        self.bdataF = None
        self.hvac_flag = True
        self.power_electronics_flag = True
        self.may_flag = False

    @property
    def battery(self):
        """Battery object."""
        return self._battery

    @battery.setter
    def battery(self, value):
        self._battery = value

    @property
    def load(self):
        """Load profile."""
        return self._load

    @load.setter
    def load(self, value):
        self._load = value

    @property
    def charge_discharge(self):
        """Charge/Discharge profile."""
        return self._charge_discharge

    @charge_discharge.setter
    def charge_discharge(self, value):
        self._charge_discharge = value

#    def _progress_func(self, x: int) -> None:
#        """
#            Progress function to send to Eplus callback 'callback_progress'.
#        """
#        pass

    def _message_func(self, message: str) -> None:
        """Message function to sent o Eplus callback 'callback_message'."""
        pass

    def _begin_new_environment_func(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_new_environment'."""
        month = self.exchange.month(self.state)
        day = self.exchange.day_of_month(self.state)

        if month == 4 and day == 30:
            self.may_flag = True
        else:
            self.may_flag = False

    def _after_new_environment_warmup_complete(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_new_environment_warmup_complete'."""
        pass

    def _begin_zone_timestep_before_init_heat_balance(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_zone_timestep_before_init_heat_balance'."""
        pass

    def _begin_zone_timestep_after_init_heat_balance(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_zone_timestep_after_init_heat_balance'."""
        pass

    def _begin_system_timestep_before_predictor(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_system_timestep_before_predictor'."""
        sys.stdout.flush()

        # only need to get the handle once
        # this piece gets the variable and actuator handles from E+
        if self.one_time:
            if self.exchange.api_data_fully_ready(state):
                try:
                    self.variablesF['Handle'] = [self.exchange.get_variable_handle(state, vtype, key)
                                                 for vtype, key in self.variablesF[['Variable Type',
                                                                                    'Variable Key']].values]
                    self.actuatorsF['Handle'] = [self.exchange.get_actuator_handle(state, atype, actype, akey)
                                                 for atype, actype, akey in self.actuatorsF[['Component Type',
                                                                                             'Control Type',
                                                                                             'Actuator Key']].values]
                except BaseException as e:
                    logging.exception(e)
                    sys.exit(1)

                if self.variablesF['Handle'].isin([-1]).any():
                    failed = self.variablesF[['Variable Type', 'Variable Key']].loc[self.variablesF['Handle'] == -1]
                    for vtype, vkey in failed.values:
                        print('{}:{} Failed'.format(vtype, vkey))
                    sys.exit(1)
                elif self.actuatorsF['Handle'].isin([-1]).any():
                    failed = self.actuatorsF[['Component Type', 'Control Type', 'Actuator Key']].loc[self.actuatorsF['Handle'] == -1]
                    for atype, actype, akey in failed.values:
                        print('{}:{}:{} Failed'.format(atype, actype, akey))
                    sys.exit(1)

                self.one_time = False

        # environment 3 is the simulation in the idfs I've run; future needs to make sure that is always the case
        environ = self.exchange.current_environment_num(state)
        if self.exchange.warmup_flag(state):
            pass
        elif environ < 3:
            pass
        else:
            try:
                self.exchange.set_actuator_value(state, int(self.actuatorsF['Handle'].loc[
                    (self.actuatorsF[['Control Type', 'Actuator Key']] == ['Heating Setpoint', 'Zone One']).all(axis=1)].values), self.h_setpoint)
                self.exchange.set_actuator_value(state, int(self.actuatorsF['Handle'].loc[
                    (self.actuatorsF[['Control Type', 'Actuator Key']] == ['Cooling Setpoint', 'Zone One']).all(axis=1)].values), self.c_setpoint)

                self.simulate_battery()
            except BaseException:
                logging.exception('Something bad happened')
                sys.exit(1)

    def _begin_zone_timestep_before_set_current_weather(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_zone_timestep_before_set_current_weather'."""
        pass

    def _after_predictor_before_hvac_managers(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_predictor_before_hvac_managers'."""
        pass

    def _after_predictor_after_hvac_managers(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_predictor_after_hvac_managers'."""
        pass

    def _inside_system_iteration_loop(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_inside_system_iteration_loop'."""
        # hvac flag is always false so this does nothing...take out to save computation time?
        environ = self.exchange.current_environment_num(state)
        if self.exchange.warmup_flag(state):
            pass
        elif environ < 3:
            pass
        else:
            try:
                if self.hvac_flag:
                    self.simulate_battery()
            except BaseException as e:
                logging.exception(e)
                sys.exit(1)

    def _end_zone_timestep_before_zone_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_zone_timestep_before_zone_reporting'."""
        pass

    def _end_zone_timestep_after_zone_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_zone_timestep_after_zone_reporting'."""
        sys.stdout.flush()

        # environment 3 is the simulation in the idfs I've run; future needs to make sure that is always the case
        # this piece collects data along the simulation
        environ = self.exchange.current_environment_num(state)
        if self.exchange.warmup_flag(state):
            pass
        elif environ < 3:
            pass
        else:
            try:
                self.append_eplus_data()
                self.append_battery_data()

                self.battery.soc_begin = self.battery.soc_end
            except BaseException as e:
                logging.exception(e)
                sys.exit(1)

    def _end_system_timestep_before_hvac_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_system_timestep_before_hvac_reporting'."""
        pass

    def _end_system_timestep_after_hvac_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_system_timestep_after_hvac_reporting'."""
        # this also does nothing because hvac flag is always false
        environ = self.exchange.current_environment_num(state)
        if self.exchange.warmup_flag(state):
            pass
        elif environ < 3:
            pass
        else:
            try:
                if self.hvac_flag:
                    self.simulate_battery()
            except BaseException as e:
                logging.exception(e)
                sys.exit(1)

    def _end_zone_sizing(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_zone_sizing'."""
        pass

    def _end_system_sizing(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_system_sizing'."""
        pass

    def _after_component_get_input(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_component_get_input'."""
        pass

    def _unitary_system_sizing(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_unitary_system_sizing'."""
        pass

    def _register_external_hvac_manager(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_register_external_hvac_manager'."""
        pass

    def _default_callback_funcs(self):
        """Set default callback functions."""

        def time_step_handler_first(self, state):
            """Pass to 'callback_begin_timestep_before_predictor'."""
            sys.stdout.flush()

            # only need to get the handle once
            if self.one_time:
                if self.exchange.api_data_fully_ready(state):
                    try:
                        self.variablesF['Handle'] = [self.exchange.get_variable_handle(state, vtype, key)
                                                     for vtype, key in self.variablesF[['Variable Type', 'Variable Key']].values]
                        self.actuatorsF['Handle'] = [self.exchange.get_actuator_handle(state, atype, actype, akey)
                                                     for atype, actype, akey in self.actuatorsF[['Component Type', 'Control Type', 'Actuator Key']].values]
                    except BaseException as e:
                        logging.exception(e)
                        sys.exit(1)

                    if self.variablesF['Handle'].isin([-1]).any():
                        failed = self.variablesF[['Variable Type', 'Variable Key']].loc[self.variablesF['Handle'] == -1]
                        for vtype, vkey in failed.values:
                            print('{}:{} Failed'.format(vtype, vkey))
                        sys.exit(1)
                    elif self.actuatorsF['Handle'].isin([-1]).any():
                        failed = self.actuatorsF[['Component Type', 'Control Type', 'Actuator Key']].loc[self.actuatorsF['Handle'] == -1]
                        for atype, actype, akey in failed.values:
                            print('{}:{}:{} Failed'.format(atype, actype, akey))
                        sys.exit(1)

                    self.one_time = False

            # environment 3 is the simulation in the idfs I've run; future needs to make sure that is always the case
            environ = self.exchange.current_environment_num(state)
            if self.exchange.warmup_flag(state):
                pass
            elif environ < 3:
                pass
            else:
                try:
                    self.exchange.set_actuator_value(state, self.actuatorsF['Handle'].loc[
                        (self.actuatorsF[['Control Type', 'Actuator Key']] == ['Heating Setpoint', 'Zone One']).all(axis=1)], self.h_setpoint)
                    self.exchange.set_actuator_value(state, self.actuatorsF['Handle'].loc[
                        (self.actuatorsF[['Control Type', 'Actuator Key']] == ['Cooling Setpoint', 'Zone One']).all(axis=1)], self.c_setpoint)

                    self.simulate_battery()
                except BaseException:
                    logging.exception('Something bad happened')
                    sys.exit(1)

        def time_step_handler_system(self, state):
            """Pass to function callback_inside_system_iteration_loop."""
            environ = self.exchange.current_environment_num(state)
            if self.exchange.warmup_flag(state):
                pass
            elif environ < 3:
                pass
            else:
                try:
                    if self.hvac_flag:
                        self.simulate_battery()
                except BaseException as e:
                    logging.exception(e)
                    sys.exit(1)

        def time_step_handler_system_after_HVAC(self, state):
            """Pass to Eplus callback 'callback_end_system_timestep_after_hvac_reporting'."""
            # this also does nothing because hvac flag is always false
            environ = self.exchange.current_environment_num(state)
            if self.exchange.warmup_flag(state):
                pass
            elif environ < 3:
                pass
            else:
                try:
                    if self.hvac_flag:
                        self.simulate_battery()
                except BaseException as e:
                    logging.exception(e)
                    sys.exit(1)

        def time_step_handler_last(self, state):
            """Pass to Eplus callback 'callback_end_zone_timestep_after_zone_reporting'."""
            sys.stdout.flush()

            # environment 3 is the simulation in the idfs I've run; future needs to make sure that is always the case
            # this piece collects data along the simulation
            environ = self.exchange.current_environment_num(state)
            if self.exchange.warmup_flag(state):
                pass
            elif environ < 3:
                pass
            else:
                try:
                    self.append_eplus_data()
                    self.append_battery_data()

                    self.battery.soc_begin = self.battery.soc_end
                except BaseException as e:
                    logging.exception(e)
                    sys.exit(1)

        def pass_func(self, var):
            pass

        self.set_callback_func('begin_system_timestep_before_predictor', time_step_handler_first)
        self.set_callback_func('inside_system_iteration_loop', time_step_handler_system)
        self.set_callback_func('end_zone_timestep_after_zone_reporting', time_step_handler_system_after_HVAC)
        self.set_callback_func('end_system_timestep_after_hvac_reporting', time_step_handler_last)

        self.set_callback_func('progress', pass_func)
        self.set_callback_func('message', pass_func)
        self.set_callback_func('begin_new_environment', pass_func)
        self.set_callback_func('after_new_environment_warmup_complete', pass_func)
        self.set_callback_func('begin_zone_timestep_before_init_heat_balance', pass_func)
        self.set_callback_func('begin_zone_timestep_after_init_heat_balance', pass_func)
        self.set_callback_func('begin_zone_timestep_before_set_current_weather', pass_func)
        self.set_callback_func('after_predictor_before_hvac_managers', pass_func)
        self.set_callback_func('after_predictor_after_hvac_managers', pass_func)
        self.set_callback_func('end_zone_timestep_before_zone_reporting', pass_func)
        self.set_callback_func('end_system_timestep_before_hvac_reporting', pass_func)
        self.set_callback_func('end_zone_sizing', pass_func)
        self.set_callback_func('end_system_sizing', pass_func)
        self.set_callback_func('after_component_get_input', pass_func)
        self.set_callback_func('unitary_system_sizing', pass_func)
        self.set_callback_func('register_external_hvac_manager', pass_func)

        print('Default callback functions set')

    def simulate_battery(self):
        """Simulate the battery based upon energyplus values."""
        # get the current timestep
        month = self.exchange.month(self.state)
        day = self.exchange.day_of_month(self.state)
        hour = self.exchange.hour(self.state)
        minutes = self.exchange.minutes(self.state)
        minutes = int(minutes/15) - 1
        i = (hour)*4 + 24*4*(day-1) + minutes

        charge_discharge = self.charge_discharge.loc[self.charge_discharge['Month'] == month]

        # battery setpoints based on current timestep
        if i >= len(charge_discharge.index):
            self.battery.p_c = 0.0
            self.battery.p_d = 0.0
        elif self.may_flag and month == 4 and day == 30:
            self.battery.p_c = 0
            self.battery.p_d = 0
        else:
            if not self.charge_discharge.empty:
                self.battery.p_c = charge_discharge['P_c'].iloc[i]
                self.battery.p_d = charge_discharge['P_d'].iloc[i]

                if not self.battery.p_d == 0 and self.hvac_flag:  # can potentially remove this
                    self.battery.p_d += self.exchange.get_variable_value(
                        self.state, int(self.variablesF['Handle'].loc[
                            (self.variablesF[['Variable Type', 'Variable Key']] ==
                             ['Facility Total HVAC Electricity Demand Rate', 'Whole Building']).all(axis=1)].values))/1e6

            elif not self.load.empty:  # can potentially remove this
                self.battery.p_c = 0
                self.battery.p_d = self.load['Load {MW}'].iloc[i]
            else:
                self.battery.p_c = 0
                self.battery.p_d = 0

        self.battery.sim_battery()

        # set battery heat loss in simulation
        heat_loss = self.battery.heat_loss*1e6
        if self.power_electronics_flag:
            heat_loss += self.battery.pe_heat_loss*1e6

        self.exchange.set_actuator_value(self.state, int(self.actuatorsF['Handle'].loc[self.actuatorsF['Actuator Key'] == 'BATTERY'].values), heat_loss)

    def append_battery_data(self):
        """Append battery data at end of timestep."""
        temp_lst = [self.battery.soc_end, self.battery.p_c, self.battery.p_d, self.battery.heat_loss]
        self.bdata_lst.append(temp_lst)

    def clear_data(self):
        """Clear variables."""
        self.state_manager.delete_state(self.state)
        self.battery.p_c = self.battery.p_d = 0
        self.battery.heat_loss = 0
        self.battery.soc_begin = self.battery.eCap*0.5
        self.battery.soc_end = 0

        self.vdata_lst = []
        self.bdata_lst = []
        self.vdataF = None
        self.bdataF = None
        self.results = None
        self.one_time = True

    def get_results(self):
        """Return variable data."""
        self.bdataF = pd.DataFrame(self.bdata_lst, columns=['SOC', 'Charge Power', 'Discharge Power', 'Heat Loss'])

        self.results = pd.concat([self.bdataF, self.vdataF], axis=1)

        return self.results
