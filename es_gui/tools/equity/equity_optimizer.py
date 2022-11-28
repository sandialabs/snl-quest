from __future__ import division, print_function, absolute_import

import logging

from pyomo.environ import *
import pandas as pd
import numpy as np

from es_gui.tools import optimizer
from es_gui.tools.equity.constraints import ExpressionsBlock


class EquityOptimizer(optimizer.Optimizer):
    """A framework wrapper class for creating Pyomo ConcreteModels for peaker plant replacement equity analysis."""

    def __init__(self,discount_rate=None, cost_per_ton_of_CO2=None, cost_per_MW_PV_system=None,
                fixed_cost_of_PV_system=None, cost_per_MW_BESS=None, cost_per_MWh_BESS=None, fixed_cost_of_the_BESS=None,
                energy_efficiency=None, plant_dispatch=None, n=None, time=None, soe_time=None, pv_profile=None,
                replacement_scenarios=None,replacement_fraction=None,
                solver='glpk'):

        self._model = ConcreteModel()
        self._solver = solver

        self.discount_rate               = discount_rate
        self.cost_per_ton_of_CO2         = cost_per_ton_of_CO2
        self.cost_per_MW_PV_system       = cost_per_MW_PV_system
        self.fixed_cost_of_PV_system     = fixed_cost_of_PV_system
        self.cost_per_MW_BESS            = cost_per_MW_BESS
        self.cost_per_MWh_BESS           = cost_per_MWh_BESS
        self.fixed_cost_of_the_BESS      = fixed_cost_of_the_BESS
        self.energy_efficiency           = energy_efficiency
        self.plant_dispatch             = plant_dispatch     
        self.filtered_plant_dispatch    = plant_dispatch          
        self.n                          = n
        self.time                       = time
        self.soe_time                   = soe_time

        self.pv_profile                 = pv_profile
        self.replacement_fraction      = replacement_fraction
        self.path = ''
 #--------------------------------------------------- 
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
 #--------------------------------------------------- 
    '''#--------------------------------------------------- 
        @property
        def discount_rate(self):
            """time discount rate [%]."""
            return self._discount_rate 

        @discount_rate.setter
        def discount_rate(self, value):
            self._discount_rate = value
    #--------------------------------------------------- 
    #--------------------------------------------------- 
        @property
        def soe_time(self):
            """time steps for SOE [hour]."""
            return self._soe_time 

        @soe_time.setter
        def soe_time(self, value):
            self._soe_time = value
    #--------------------------------------------------- 

    #--------------------------------------------------- 
        @property
        def pv_profile(self):
            """Pv profile [kW]."""
            return self._pv_profile 

        @pv_profile.setter
        def pv_profile(self, value):
            self._pv_profile = value
    #--------------------------------------------------- '''




    def _set_model_param(self):
        """Sets the model params for the Pyomo ConcreteModel."""
        m = self.model
        
        # Check if params common to all formulations are set.
        if not hasattr(m, 'discount_rate'):
            # Transformer rating; equivalently, the maximum power can be exchanged [kW].
            logging.debug('Optimizer: No discount_rate provided, setting default...')
            m.Transformer_rating = 3
    
    def _set_model_var(self):
        """Sets the model vars for the Pyomo ConcreteModel."""
        m = self.model
        
        if not hasattr(m, 'energy_capacity'):
            def _energy_capacity_init(_m):
                """The energy storage device's state of energy [kWh]."""
                return 0

            m.energy_capacity = Var(domain = NonNegativeReals)

        if not hasattr(m, 'power_capacity'):
            def _power_capacity_init(_m):
                """The energy storage device's state of energy [kWh]."""
                return 0

            m.power_capacity = Var(domain = NonNegativeReals)

        if not hasattr(m, 'pv_capacity'):
            def _pv_capacity_init(_m):
                """The energy storage device's state of energy [kWh]."""
                return 0

            m.pv_capacity = Var(domain = NonNegativeReals)

        if not hasattr(m, 'soe'):
            def _soe_init(_m, t):
                """The energy storage device's state of energy [kWh]."""
                return m.energy_capacity
            m.soe = Var(m.soe_time, domain = NonNegativeReals)

        if not hasattr(m, 'pe_c'):
            def _pe_c_init(_m, t):
                """The energy storage device's state of energy [kWh]."""
                return 0

            m.pe_c = Var(m.time, domain = NonNegativeReals)

        if not hasattr(m, 'pe_d'):
            def _pe_d_init(_m, t):
                """The energy storage device's state of energy [kWh]."""
                return 0

            m.pe_d = Var(m.time, domain = NonPositiveReals)

        if not hasattr(m, 'meets'):
            def _pe_d_init(_m, t):
                """The fraction of the peakers power at any time that the BESS+PV meets."""
                return 0
            m.meets = Var(m.time, domain = NonNegativeReals, bounds=(0,1))

    def instantiate_model(self):
        """Instantiates the Pyomo ConcreteModel and populates it with supplied time series data."""
        if not hasattr(self, 'model'):
            self.model = ConcreteModel()
        
        m = self.model

        m.replacement_fraction       = self.replacement_fraction
        m.discount_rate               = self.discount_rate
        m.cost_per_ton_of_CO2         = self.cost_per_ton_of_CO2 
        m.CO2_emissions               = self.CO2_emissions  
        m.cost_per_MW_PV_system       = self.cost_per_MW_PV_system
        m.fixed_cost_of_PV_system     = self.fixed_cost_of_PV_system
        m.cost_per_MW_BESS            = self.cost_per_MW_BESS 
        m.cost_per_MWh_BESS           = self.cost_per_MWh_BESS
        m.fixed_cost_of_the_BESS      = self.fixed_cost_of_the_BESS  
        m.energy_efficiency           = self.energy_efficiency 
        m.plant_dispatch              = self.plant_dispatch
        m.filtered_plant_dispatch     = self.filtered_plant_dispatch
        m.n                           = self.n
        m.time                        = self.time
        m.soe_time                    = self.soe_time
        m.pv_profile                  = self.pv_profile
        m.flexible_dispatch           = self.flexible_dispatch
        m.fixed_dispatch              = self.fixed_dispatch      

        logging.info('Optimizer: Pyomo ConcreteModel has been populated with supplied time series data.')

            
    def populate_model(self):
        """Populates the Pyomo ConcreteModel based on the specified market_type."""
        self.model.objective_expr = 0.0

        self._set_model_param()
        self._set_model_var()

        self.expressions_block = ExpressionsBlock()
        
        try:
            self.expressions_block.set_expressions(self.model)
        except IndexError:
            # Array-like object(s) do(es) not match the length of the price_electricity array-like.
            raise(IncompatibleDataException('At least one of the array-like parameter objects is not the expected length. (It should match the length of the price_electricity object.)'))
        else:
            self.model.objective = Objective(expr=self.model.objective_expr)

    def _process_results(self):
        """Processes optimization results for further evaluation."""
        m = self.model
        self.replacement_fraction = m.replacement_fraction
        self.energy_capacity = m.energy_capacity.value
        self.power_capacity = m.power_capacity.value
        self.pv_capacity = m.pv_capacity.value
        self.soe = [m.soe[i].value for i in self.time]
        self.pe_c = [m.pe_c[i].value for i in self.time]
        self.pe_d = [m.pe_d[i].value for i in self.time]
        ptot = [m.pe_c[i].value + m.pe_d[i].value for i in self.time]
        ppv = [m.pv_capacity.value*m.pv_profile[i] for i in self.time]
        self.es_pv_dispatch = [-m.pe_d[i].value - m.pe_c[i].value + m.pv_capacity.value*m.pv_profile[i] for i in self.time]

        run_results = {'time': self.time,  'plant dispatch': self.plant_dispatch, 'filtered plant dispatch': self.filtered_plant_dispatch,
                       'Ppv': ppv, 'Pcharge': self.pe_c, 'Pdischarge': self.pe_d, 'es power': ptot,
                       'es+pv power': self.es_pv_dispatch, 'state of energy': self.soe,}
        

        self.results = pd.DataFrame(run_results)        
        logging.info('Optimizer: Results have been processed for further evaluation.')
        
    def get_results(self):
        """Returns the decision variables and derived quantities in a DataFrame"""
        return self.results
    
 

class BadParameterException(Exception):
    pass


class IncompatibleDataException(Exception):
    pass


if __name__ == '__main__':
    print('this script does not run on its own')