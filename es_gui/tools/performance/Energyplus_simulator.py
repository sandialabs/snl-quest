# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 09:56:35 2020

@author: wolis

Code to parent Energyplus simulator class.
"""

from pyenergyplus.api import EnergyPlusAPI
import pandas as pd
from abc import ABC, abstractmethod
from ctypes import c_void_p
import sys
import os
sys.path.insert(0, os.getcwd()+'\\energyplus')


class Energyplus_simulator(EnergyPlusAPI, ABC):
    """Energyplus simulation parent class."""

    def __init__(self, idf, weather, output_dir, variables=None, actuators=None):

        super().__init__()
        self._idf = idf
        self._weather = weather
        self._output_dir = output_dir

        self.variablesF = pd.DataFrame(variables, columns=['Variable Type', 'Variable Key'])
        self.actuatorsF = pd.DataFrame(actuators, columns=['Component Type', 'Control Type', 'Actuator Key'])

        self.vdata_lst = []
        self.vdataF = None
        self.results = None

        self._one_time = True
        self._default_callbacks = True
        self._progress = 0
        self.state = None

    @property
    def idf(self):
        """Energyplus input file."""
        return self._idf

    @idf.setter
    def idf(self, value):
        self._idf = value

    @property
    def weather(self):
        """Energyplus weather file."""
        return self._weather

    @weather.setter
    def weather(self, value):
        self._weather = value

    @property
    def output_dir(self):
        """Specify output directory."""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value

    @property
    def one_time(self):
        """If first iteration. To get variable handles."""
        return self._one_time

    @one_time.setter
    def one_time(self, value):
        self._one_time = value

    @property
    def default_callbacks(self):
        """Whether to use default callbacks or user defined."""
        return self._default_callbacks

    @default_callbacks.setter
    def default_callbacks(self, value):
        self._default_callbacks = value

    @property
    def progress(self):
        """Progress of simulation."""
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    def _progress_func(self, x: int) -> None:
        """Progress function to send to Eplus callback 'callback_progress'."""
        self.progress = x

    @abstractmethod
    def _message_func(self, message: str) -> None:
        """Message function to sent o Eplus callback 'callback_message'."""
        pass

    @abstractmethod
    def _begin_new_environment_func(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_new_environment'."""
        pass

    @abstractmethod
    def _after_new_environment_warmup_complete(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_new_environment_warmup_complete'."""
        pass

    @abstractmethod
    def _begin_zone_timestep_before_init_heat_balance(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_zone_timestep_before_init_heat_balance'."""
        pass

    @abstractmethod
    def _begin_zone_timestep_after_init_heat_balance(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_zone_timestep_after_init_heat_balance'."""
        pass

    @abstractmethod
    def _begin_system_timestep_before_predictor(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_system_timestep_before_predictor'."""
        pass

    @abstractmethod
    def _begin_zone_timestep_before_set_current_weather(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_begin_zone_timestep_before_set_current_weather'."""
        pass

    @abstractmethod
    def _after_predictor_before_hvac_managers(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_predictor_before_hvac_managers'."""
        pass

    @abstractmethod
    def _after_predictor_after_hvac_managers(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_predictor_after_hvac_managers'."""
        pass

    @abstractmethod
    def _inside_system_iteration_loop(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_inside_system_iteration_loop'."""
        pass

    @abstractmethod
    def _end_zone_timestep_before_zone_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_zone_timestep_before_zone_reporting'."""
        pass

    @abstractmethod
    def _end_zone_timestep_after_zone_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_zone_timestep_after_zone_reporting'."""
        pass

    @abstractmethod
    def _end_system_timestep_before_hvac_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_system_timestep_before_hvac_reporting'."""
        pass

    @abstractmethod
    def _end_system_timestep_after_hvac_reporting(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_system_timestep_after_hvac_reporting'."""
        pass

    @abstractmethod
    def _end_zone_sizing(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_zone_sizing'."""
        pass

    @abstractmethod
    def _end_system_sizing(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_end_system_sizing'."""
        pass

    @abstractmethod
    def _after_component_get_input(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_after_component_get_input'."""
        pass

    @abstractmethod
    def _unitary_system_sizing(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_unitary_system_sizing'."""
        pass

    @abstractmethod
    def _register_external_hvac_manager(self, state: c_void_p) -> None:
        """Pass to Eplus callback 'callback_register_external_hvac_manager'."""
        pass

    @abstractmethod
    def _default_callback_funcs(self):
        """Set default callbacks."""
        pass

    def set_callback_func(self, sim_point, func):
        """Set callback in Eplus simulation."""
        callbacks = ['progress', 'message', 'begin_new_environment', 'after_new_environment_warmup_complete',
                     'begin_zone_timestep_before_init_heat_balance', 'begin_zone_timestep_after_init_heat_balance',
                     'begin_system_timestep_before_predictor', 'begin_zone_timestep_before_set_current_weather',
                     'after_predictor_before_hvac_managers', 'after_predictor_after_hvac_managers',
                     'inside_system_iteration_loop', 'end_zone_timestep_before_zone_reporting',
                     'end_zone_timestep_after_zone_reporting', 'end_system_timestep_before_hvac_reporting',
                     'end_system_timestep_after_hvac_reporting', 'end_zone_sizing', 'end_system_sizing',
                     'after_component_get_input', 'unitary_system_sizing', 'register_external_hvac_manager']

        assert sim_point in callbacks

        if sim_point == callbacks[0]:
            self._progress_func = func
        elif sim_point == callbacks[1]:
            self._message_func = func
        elif sim_point == callbacks[2]:
            self._begin_new_environment_func = func
        elif sim_point == callbacks[3]:
            self._after_new_environment_warmup_complete = func
        elif sim_point == callbacks[4]:
            self._begin_zone_timestep_before_init_heat_balance = func
        elif sim_point == callbacks[5]:
            self._begin_zone_timestep_after_init_heat_balance = func
        elif sim_point == callbacks[6]:
            self._begin_system_timestep_before_predictor = func
        elif sim_point == callbacks[7]:
            self._begin_zone_timestep_before_set_current_weather = func
        elif sim_point == callbacks[8]:
            self._after_predictor_before_hvac_managers = func
        elif sim_point == callbacks[9]:
            self._after_predictor_after_hvac_managers = func
        elif sim_point == callbacks[10]:
            self._inside_system_iteration_loop = func
        elif sim_point == callbacks[11]:
            self._end_zone_timestep_before_zone_reporting = func
        elif sim_point == callbacks[12]:
            self._end_zone_timestep_after_zone_reporting = func
        elif sim_point == callbacks[13]:
            self._end_system_timestep_before_hvac_reporting = func
        elif sim_point == callbacks[14]:
            self._end_system_timestep_after_hvac_reporting = func
        elif sim_point == callbacks[15]:
            self._end_zone_sizing = func
        elif sim_point == callbacks[16]:
            self._end_system_sizing = func
        elif sim_point == callbacks[17]:
            self._after_component_get_input = func
        elif sim_point == callbacks[18]:
            self._unitary_system_sizing = func
        elif sim_point == callbacks[19]:
            self._register_external_hvac_manager = func
        else:
            print('{} is not a valid callback'.format(sim_point))

    def set_callbacks(self):
        """Set the callback functions of the state."""
        self.runtime.callback_progress(
            self.state, self._progress_func)
        self.runtime.callback_message(
            self.state, self._message_func)
        self.runtime.callback_begin_new_environment(
            self.state, self._begin_new_environment_func)
        self.runtime.callback_after_new_environment_warmup_complete(
            self.state, self._after_new_environment_warmup_complete)
        self.runtime.callback_begin_zone_timestep_before_init_heat_balance(
            self.state, self._begin_zone_timestep_before_init_heat_balance)
        self.runtime.callback_begin_zone_timestep_after_init_heat_balance(
            self.state, self._begin_zone_timestep_after_init_heat_balance)
        self.runtime.callback_begin_system_timestep_before_predictor(
            self.state, self._begin_system_timestep_before_predictor)
        self.runtime.callback_begin_zone_timestep_before_set_current_weather(
            self.state, self._begin_zone_timestep_before_set_current_weather)
        self.runtime.callback_after_predictor_before_hvac_managers(
            self.state, self._after_predictor_before_hvac_managers)
        self.runtime.callback_after_predictor_after_hvac_managers(
            self.state, self._after_predictor_after_hvac_managers)
        self.runtime.callback_inside_system_iteration_loop(
            self.state, self._inside_system_iteration_loop)
        self.runtime.callback_end_zone_timestep_before_zone_reporting(
            self.state, self._end_zone_timestep_before_zone_reporting)
        self.runtime.callback_end_zone_timestep_after_zone_reporting(
            self.state, self._end_zone_timestep_after_zone_reporting)
        self.runtime.callback_end_system_timestep_before_hvac_reporting(
            self.state, self._end_system_timestep_before_hvac_reporting)
        self.runtime.callback_end_system_timestep_after_hvac_reporting(
            self.state, self._end_system_timestep_after_hvac_reporting)
        self.runtime.callback_end_zone_sizing(
            self.state, self._end_zone_sizing)

    def append_eplus_data(self):
        """
        Collect Energyplus variable data at the end of each time step. Should be called in "time step handler last".

        param variablesF  : contains the relevant info for each E+ variable
        dtype variablesF  : pd.DataFrame

        """
        temp_lst = [self.exchange.month(self.state), self.exchange.day_of_month(self.state),
                    self.exchange.hour(self.state)] + [self.exchange.get_variable_value(self.state, handle) for handle in self.variablesF['Handle']]
        self.vdata_lst.append(temp_lst)

    @abstractmethod
    def clear_data(self):
        """Remove data from previous run."""
        pass

    def request_variables(self):
        """Request variables in variablesF for access from Eplus."""
        for vtype, vkey in self.variablesF[['Variable Type', 'Variable Key']].values:
            self.exchange.request_variable(self.state, vtype, vkey)

    def simulate(self):
        """Run an Energyplus simulation."""
        print('Simulating')

        code = self.runtime.run_energyplus(self.state, [
            '-d',
            self.output_dir,
            '-w',
            self.weather,
            self.idf
        ])

        print('Done')

        return code

    def new_simulation(self):
        """Run a simulation with a new Eplus state."""
        self.clear_data()
        self.state = self.state_manager.new_state()

        self.set_callbacks()
        self.request_variables()
        code = self.simulate()

        self.vdataF = pd.DataFrame(self.vdata_lst, columns=['Month',
                                                            'Day', 'Hour'] + self.variablesF['Variable Type'].values.tolist())

        return code

    def rerun_simulation(self):
        """Rerun an Eplus simulation."""
        self.state_manager.reset_state(self.state)
        self.clear_data()

        self.set_callbacks()
        self.request_variables()
        code = self.simulate()

        self.vdataF = pd.DataFrame(self.vdata_lst, columns=['Month',
                                                            'Day', 'Hour'] + self.variablesF['Variable Type'].values.tolist())

        return code

    @abstractmethod
    def get_results(self):
        """Return variable data."""
        pass
