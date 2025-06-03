from __future__ import division, print_function, absolute_import

import logging
import os

from pyomo.environ import *
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

from afr.reg_planning_opt.optimizer import Optimizer
from afr.reg_planning_opt.constraints import ExpressionsBlock

class RegPlanningOptimizer(Optimizer):
    """Class to optimize scenarios for the QuESt: Analysis for Regulators application."""

    def __init__(self, data_handler):

        super().__init__(data_handler.solver)

        self.data_handler = data_handler

        self._expressions_block = None

        self._results = None

    @property
    def expressions_block(self):
        """ExpressionsBlock object for setting model objectives and constraints."""
        return self._expressions_block

    @expressions_block.setter
    def expressions_block(self, value):
        self._expressions_block = value

    @property
    def results(self):
        """Pandas DataFrame containing results."""
        return self._results

    @results.setter
    def results(self, value):
        if isinstance(value, pd.DataFrame):
            self._results = value
        else:
            raise TypeError('results must be a Pandas DataFrame.')

    def _set_model_param(self):
        """Sets the model params for the Pyomo ConcreteModel."""
        m = self.model

        # Parameters
        m.year  = RangeSet(1, self.data_handler.horizon) # year index
        m.season= RangeSet(1,4)  # season index
        m.month = RangeSet(1,13) # 4 week index
        m.week  = RangeSet(1,52) # week index
        m.day   = RangeSet(1,365)# day index

        m.gen_names = [gen for gen in self.data_handler.Pgen]
        m.gen_nums = RangeSet(0, len(self.data_handler.Pgen)-1)

        m.es_devices = [device for device in self.data_handler.es_devices]
        m.weekly_devices = [device for device in self.data_handler.es_devices if 
                            self.data_handler.es_devices[device]['cycle'] == 'weekly']
        m.monthly_devices = [device for device in self.data_handler.es_devices if 
                            self.data_handler.es_devices[device]['cycle'] == 'monthly']
        m.seasonal_devices = [device for device in self.data_handler.es_devices if 
                            self.data_handler.es_devices[device]['cycle'] == 'seasonal']
        m.annual_devices = [device for device in self.data_handler.es_devices if 
                            self.data_handler.es_devices[device]['cycle'] == 'annual']

        m.Pgen = {i: v for i, v in enumerate(self.data_handler.Pgen.values())}
        m.c_factors = {i: v for i, v in enumerate(self.data_handler.cap_factor.values())}

        m.clean = self.data_handler.clean
        m.dirty = self.data_handler.dirty


        # Create rps target list; rps_target_years should be a dict with keys of year index and values of target percentages (decimal format)
        years = [year for year in self.data_handler.rps_target_years]
        year_range = [year for year in range(self.data_handler.start_year, self.data_handler.end_year + 1)]
        year_rps = year_range.index(years[0]) + 1
        m.year_rps = RangeSet(year_rps, self.data_handler.horizon)
        m.year_nrps = RangeSet(1, year_rps-1)
        rps = [0]*(len(m.year)+1)
        for i, year in enumerate(self.data_handler.rps_target_years):
            target = self.data_handler.rps_target_years[year]
            year_i = year_range.index(years[i]) + 1
            if not year == years[-1]:
                year_i1 = year_range.index(years[i+1]) + 1
                rps[year_i:year_i1] = [(1-target)/target]*len(rps[year_i:year_i1])
            else:
                rps[year_i:] = [(1-target)/target]*len(rps[year_i:])

        # print(rps)
        m.rps_targets = rps

            




    def _set_model_var(self):
        """Sets the model vars for the Pyomo ConcreteModel."""
        m = self.model

        # Independent Variables
        m.Ppv     = Var(m.year, domain=NonNegativeReals) # capacity addition at a year of PV, MW
        m.Pwind   = Var(m.year, domain=NonNegativeReals) # capacity addition at a year of PV, MW
        m.Pes     = Var(m.es_devices, m.year, domain=NonNegativeReals)

        # Dependent Variables
        m.Ppv_tot     = Var(m.year, domain=NonNegativeReals) # total installed capacity at a year of PV, MW
        m.Pwind_tot   = Var(m.year, domain=NonNegativeReals) # total installed capacity at a year of Wind, MW
        m.Pes_tot     = Var(m.es_devices, m.year, domain=NonNegativeReals)

        m.Epv         = Var(m.year, m.day, domain=NonNegativeReals) # total energy generation in a day of PV, MWh
        m.Ewind       = Var(m.year, m.day, domain=NonNegativeReals) # total energy generation in a day of Wind, MWh
        m.Epv_cut     = Var(m.year, m.day, domain=NonNegativeReals) # total curtailed energy in a day of PV, MWh
        m.Ewind_cut   = Var(m.year, m.day, domain=NonNegativeReals) # total curtailed energy in a day of Wind, MWh
        m.Egens       = Var(m.gen_nums, m.year, m.day, domain=NonNegativeReals) # total energy generation in a day of given gens
        
        m.Ees_dis       = Var(m.es_devices, m.year, m.day, domain=NonNegativeReals) # total energy discharged by ES devices in a day, MWh
        m.Ees_cha       = Var(m.es_devices, m.year, m.day, domain=NonNegativeReals) # total energy charged by ES devices in a day, MWh

        m.Ses       = Var(m.es_devices, m.year, m.day, domain=NonNegativeReals) # Daily state of energy of ES devices

    def instantiate_model(self):
        """Instantiates the Pyomo ConcreteModel and populates it with supplied time series data."""
        if not hasattr(self, 'model'):
            self.model = ConcreteModel()

        m = self.model




    def populate_model(self):
        """Populates the Pyomo ConcreteModel based on the specified market_type."""
        self.model.objective_expr = 0.0

        self._set_model_param()
        self._set_model_var()

        self.expressions_block = ExpressionsBlock(self.data_handler)

        try:
            self.expressions_block.set_expressions(self.model)
        except IndexError:
            # Array-like object(s) do(es) not match the length of the price_electricity array-like.
            raise(IncompatibleDataException('At least one of the array-like parameter objects is not the expected length. (It should match the length of the price_electricity object.)'))
        else:
            self.model.objective = Objective(expr=self.model.objective_expr, sense=minimize)


    def _process_results(self):
        """Processes optimization results for further evaluation."""
        m = self.model

        result_dict = {}

        result_dict['Ppv'] = [value(m.Ppv[k]) for k in range(1,self.data_handler.horizon+1)]
        result_dict['Ppv_tot'] = [value(m.Ppv_tot[k]) for k in range(1,self.data_handler.horizon+1)]
        result_dict['Epv'] = [[value(m.Epv[yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]
        result_dict['Epv_cut'] = [[value(m.Epv_cut[yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]

        for i, gen in enumerate(self.data_handler.Pgen):
            result_dict[gen] = [[value(m.Egens[i, yr, d]) for d in range(1, 366)] for yr in range(1, self.data_handler.horizon+1)]

        result_dict['Pwind'] = [value(m.Pwind[k]) for k in range(1,self.data_handler.horizon+1)]
        result_dict['Pwind_tot'] = [value(m.Pwind_tot[k]) for k in range(1,self.data_handler.horizon+1)]
        result_dict['Ewind'] = [[value(m.Ewind[yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]
        result_dict['Ewind_cut'] = [[value(m.Ewind_cut[yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]


        for i, device in enumerate(self.data_handler.es_devices):
            result_dict[f"{device} Power"] = [value(m.Pes[device, k]) for k in range(1, self.data_handler.horizon+1)]
            result_dict[f"{device} Total Power"] = [value(m.Pes_tot[device, k]) for k in range(1,self.data_handler.horizon+1)]
            result_dict[f"{device} State of Energy"] = [[value(m.Ses[device, yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]
            result_dict[f"{device} Discharge Energy"] = [[value(m.Ees_dis[device,yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]
            result_dict[f"{device} Charge Energy"] = [[value(m.Ees_cha[device, yr,d]) for d in range(1,366)] for yr in range(1,self.data_handler.horizon+1)]

        self.results = pd.DataFrame(result_dict)
        self.data_handler.results = self.results

    def get_results(self):
        """Returns the decision variables and derived quantities in a DataFrame, plus the net revenue."""
        self.data_handler.results = self.results
        return self.results

class BadParameterException(Exception):
    pass


class IncompatibleDataException(Exception):
    pass


if __name__ == '__main__':
    with open('valuation_optimizer.log', 'w'):
        pass

    logging.basicConfig(filename='valuation_optimizer.log', format='[%(levelname)s] %(asctime)s: %(message)s',
                        level=logging.INFO)