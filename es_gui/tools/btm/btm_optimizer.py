from __future__ import division, print_function, absolute_import

import logging

from pyomo.environ import *
import pandas as pd
import numpy as np
import os

from es_gui.tools import optimizer
from es_gui.tools.btm.constraints import ExpressionsBlock


class BtmOptimizer(optimizer.Optimizer):
    """A framework wrapper class for creating Pyomo ConcreteModels for behind the meter valuation."""

    def __init__(self, tou_energy_schedule = None, tou_energy_rate=None, 
                 tou_demand_schedule=None, tou_demand_rate=None, flat_demand_rate=None,
                 nem_type=1, nem_rate=None, load_profile=None, pv_profile=None, 
                 rate_structure_metadata=None, load_profile_metadata=None, pv_profile_metadata=None,
                 cost_charge=None, cost_discharge=None,
                 solver='glpk'):
        
        self._model = ConcreteModel()
        self._solver = solver

        self._expressions_block = None
        
        self._tou_energy_schedule = tou_energy_schedule # type: list, size: number of hours in a month, value: tou_energy_rate index 
        self._tou_energy_rate = tou_energy_rate # type = list, size = number of tou periods for energy, value: tou energy rate [$/kWh] 
        
        self._tou_demand_schedule = tou_demand_schedule # type: list, size: number of hours in a month, value: tou_demand_rate index
        self._tou_demand_rate = tou_demand_rate # type = list, size = number of tou periods for demand , value:tou demand rate [$/kW]
        self._flat_demand_rate = flat_demand_rate # type = list, size = 12 (months) 
        
        self._nem_type = nem_type # type: integer, value: 0 = no net-metering, 1=net-metering 1.0, 2 = net-metering 2.0
        self._nem_rate = nem_rate # type: real, value: sell rate of nem 1.0
        
        self._load_profile = load_profile # type: list, size: number of hours in a month, value: load (kW) 
        self._pv_profile = pv_profile # type: list, size: number of hours in a month, value: pv (kW)

        self._rate_structure_metadata = rate_structure_metadata # type: dict 
        self._load_profile_metadata = load_profile_metadata # type: dict 
        self._pv_profile_metadata = pv_profile_metadata # type: dict
        
#        self._cost_charge = cost_charge
#        self._cost_discharge = cost_discharge
        self._results = None

        self._total_bill_with_es = 0
        self._total_bill_without_es = 0
        self._energy_charge_with_es = 0
        self._energy_charge_without_es = 0
        self._demand_charge_with_es = 0
        self._demand_charge_without_es = 0
        self._nem_charge_with_es = 0
        self._nem_charge_without_es = 0
        
 #---------------------------------------------------   
    @property
    def tou_energy_schedule(self):
        """Time-of-use energy schedule."""
        return self._tou_energy_schedule

    @tou_energy_schedule.setter
    def tou_energy_schedule(self, value):
        self._tou_energy_schedule = value
 #--------------------------------------------------- 
    @property
    def tou_energy_rate(self):
        """Time-of-use energy rate [$/kWh]."""
        return self._tou_energy_rate

    @tou_energy_rate.setter
    def tou_energy_rate(self, value):
        self._tou_energy_rate = value
 #--------------------------------------------------- 
    @property
    def tou_demand_schedule(self):
        """Time-of-use demand schedule."""
        return self._tou_demand_schedule

    @tou_demand_schedule.setter
    def tou_demand_schedule(self, value):
        self._tou_demand_schedule = value
 #---------------------------------------------------  
    @property
    def tou_demand_rate(self):
        """Time-of-use demand rate [$/kW]."""
        return self._tou_demand_rate

    @tou_demand_rate.setter
    def tou_demand_rate(self, value):
        self._tou_demand_rate = value
 #--------------------------------------------------- 
    @property
    def flat_demand_rate(self):
        """Flat demand rate [$/kW]."""
        return self._flat_demand_rate

    @flat_demand_rate.setter
    def flat_demand_rate(self, value):
        self._flat_demand_rate = value
#--------------------------------------------------- 
    @property
    def nem_type(self):
        """The type of net metering program, defaults to 1."""
        return self._nem_type

    @nem_type.setter
    def nem_type(self, value):
        if isinstance(value, int):
            self._nem_type = value
        else:
            raise TypeError('nem_type property must be of type int.')
 #--------------------------------------------------- 
    @property
    def nem_rate(self):
        """The type of net metering program"""
        return self._nem_rate

    @nem_rate.setter
    def nem_rate(self, value):
        self._nem_rate = value 
 #--------------------------------------------------- 
    @property
    def load_profile(self):
        """Load profile [kW]."""
        return self._load_profile

    @load_profile.setter
    def load_profile(self, value):
        self._load_profile = value
 #--------------------------------------------------- 
    @property
    def pv_profile(self):
        """Pv profile [kW]."""
        return self._pv_profile 

    @pv_profile.setter
    def pv_profile (self, value):
        self._pv_profile = value
#--------------------------------------------------- 
    @property
    def rate_structure_metadata(self):
        """Dictionary containing metadata about the rate structure associated with the other input properties."""
        return self._rate_structure_metadata 

    @rate_structure_metadata.setter
    def rate_structure_metadata (self, value):
        self._rate_structure_metadata = value
#--------------------------------------------------- 
    @property
    def load_profile_metadata(self):
        """Dictionary containing metadata about the load profile."""
        return self._load_profile_metadata 

    @load_profile_metadata.setter
    def load_profile_metadata (self, value):
        self._load_profile_metadata = value
#--------------------------------------------------- 
    @property
    def pv_profile_metadata(self):
        """Dictionary containing metadata about the PV profile."""
        return self._pv_profile_metadata 

    @pv_profile_metadata.setter
    def pv_profile_metadata (self, value):
        self._pv_profile_metadata = value
# #--------------------------------------------------- 
#    @property
#    def cost_charge(self):
#        """The cost of charging the energy storage device [$/kWh]."""
#        return self._cost_charge
#
#    @cost_charge.setter
#    def cost_charge(self, value):
#        self._cost_charge = value
# #--------------------------------------------------- 
#    @property
#    def cost_discharge(self):
#        """The cost of discharging the energy storage device [$/kWh]."""
#        return self._cost_discharge
#
#    @cost_discharge.setter
#    def cost_discharge(self, value):
#        self._cost_discharge = value
 #--------------------------------------------------- 
    @property
    def solver(self):
        """The name of the solver for Pyomo to use, defaults to 'glpk'."""
        return self._solver

    @solver.setter
    def solver(self, value):
        self._solver = value
 #--------------------------------------------------- 
    @property
    def expressions_block(self):
        """ExpressionsBlock object for setting model objectives and constraints."""
        return self._expressions_block

    @expressions_block.setter
    def expressions_block(self, value):
        self._expressions_block = value
 
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
    @property
    def total_bill_with_es(self):
        """The total bill for the month with energy storage."""
        return self._total_bill_with_es

    @total_bill_with_es.setter
    def total_bill_with_es(self, value):
        self._total_bill_with_es = value
    
    @property
    def total_bill_without_es(self):
        """The total bill for the month without energy storage."""
        return self._total_bill_without_es

    @total_bill_without_es.setter
    def total_bill_without_es(self, value):
        self._total_bill_without_es = value
    
    @property
    def demand_charge_with_es(self):
        """The total demand charges for the month with energy storage."""
        return self._demand_charge_with_es

    @demand_charge_with_es.setter
    def demand_charge_with_es(self, value):
        self._demand_charge_with_es = value
    
    @property
    def demand_charge_without_es(self):
        """The total demand charges for the month without energy storage."""
        return self._demand_charge_without_es

    @demand_charge_without_es.setter
    def demand_charge_without_es(self, value):
        self._demand_charge_without_es = value
    
    @property
    def energy_charge_with_es(self):
        """The total energy charges for the month with energy storage."""
        return self._energy_charge_with_es

    @energy_charge_with_es.setter
    def energy_charge_with_es(self, value):
        self._energy_charge_with_es = value
    
    @property
    def energy_charge_without_es(self):
        """The total energy charges for the month without energy storage."""
        return self._energy_charge_without_es

    @energy_charge_without_es.setter
    def energy_charge_without_es(self, value):
        self._energy_charge_without_es = value
    
    @property
    def nem_charge_with_es(self):
        """The total net energy metering charges for the month with energy storage."""
        return self._nem_charge_with_es

    @nem_charge_with_es.setter
    def nem_charge_with_es(self, value):
        self._nem_charge_with_es = value
    
    @property
    def nem_charge_without_es(self):
        """The total net energy metering charges for the month without energy storage."""
        return self._nem_charge_without_es

    @nem_charge_without_es.setter
    def nem_charge_without_es(self, value):
        self._nem_charge_without_es = value

    def _set_model_param(self):
        """Sets the model params for the Pyomo ConcreteModel."""
        m = self.model
        
        # Check if params common to all formulations are set.
        if not hasattr(m, 'Transfomer_rating'):
            # Transformer rating; equivalently, the maximum power can be exchanged [kW].
            logging.debug('Optimizer: No Transformer_rating provided, setting default...')
            m.Transformer_rating = 1000000
            
        if not hasattr(m, 'Power_rating'):
            # Power rating; equivalently, the maximum power can be charged or discharged [kW].
            logging.debug('Optimizer: No Power_rating provided, setting default...')
            m.Power_rating = 100

        if not hasattr(m, 'Energy_capacity'):
            # Energy capacity [kWh].
            logging.debug('Optimizer: No Energy_capacity provided, setting default...')
            m.Energy_capacity = 100

        if not hasattr(m, 'Self_discharge_efficiency'):
            # Fraction of energy maintained over one time period.
            logging.debug('Optimizer: No Self_discharge_efficiency provided, setting default...')
            m.Self_discharge_efficiency = 1.00     
        elif getattr(m, 'Self_discharge_efficiency') > 1.0:
            logging.warning('Optimizer: Self_discharge_efficiency provided is greater than 1.0, interpreting as percentage...')
            m.Self_discharge_efficiency = m.Self_discharge_efficiency/100

        if not hasattr(m, 'Round_trip_efficiency'):
            # Fraction of input energy that gets stored over one time period.
            logging.debug('Optimizer: No Round_trip_efficiency provided, setting default...')
            m.Round_trip_efficiency = 0.85
        elif getattr(m, 'Round_trip_efficiency') > 1.0:
            logging.warning('Optimizer: Round_trip_efficiency provided is greater than 1.0, interpreting as percentage...')
            m.Round_trip_efficiency = m.Round_trip_efficiency/100

        if not hasattr(m, 'State_of_charge_min'):
            # Fraction of energy capacity to increase state of charge minimum by.
            logging.debug('Optimizer: No State_of_charge_min provided, setting default...')
            m.State_of_charge_min = 0
        elif getattr(m, 'State_of_charge_min') > 1.0:
            logging.warning('Optimizer: State_of_charge_min provided is greater than 1.0, interpreting as percentage...')
            m.State_of_charge_min = m.State_of_charge_min/100

        if not hasattr(m, 'State_of_charge_max'):
            # Fraction of energy capacity to decrease state of charge maximum by.
            logging.debug('Optimizer: No State_of_charge_max provided, setting default...')
            m.State_of_charge_max = 100
        elif getattr(m, 'State_of_charge_max') > 1.0:
            logging.warning('Optimizer: State_of_charge_max provided is greater than 1.0, interpreting as percentage...')
            m.State_of_charge_max = m.State_of_charge_max/100
        
        if not hasattr(m, 'State_of_charge_init'):
            # Initial state of charge [fraction of capacity], defaults to the amount reserved for discharging.
            logging.debug('Optimizer: No State_of_charge_init provided, setting default...')
            m.State_of_charge_init = 0.50
        elif getattr(m, 'State_of_charge_init') > 1.0:
            logging.warning('Optimizer: State_of_charge_init provided is greater than 1.0, interpreting as percentage...')
            m.State_of_charge_init = m.State_of_charge_init/100
            
        m.smin = m.State_of_charge_min*m.Energy_capacity
        m.smax = m.State_of_charge_max*m.Energy_capacity
    
    def _set_model_var(self):
        """Sets the model vars for the Pyomo ConcreteModel."""
        m = self.model
        
        if not hasattr(m, 's'):
            def _s_init(_m, t):
                """The energy storage device's state of charge [kWh]."""
                return m.State_of_charge_init*m.Energy_capacity

            m.s = Var(m.time, domain = NonNegativeReals,bounds=(m.smin,m.smax))

        if not hasattr(m, 'pdis'):
            def _pdis_init(_m, t):
                """The discharge power vector [kW]"""
                return 0.0

            m.pdis = Var(m.time, initialize= _pdis_init, domain = NonNegativeReals, bounds=(0,m.Power_rating))
        
        if not hasattr(m, 'pcha'):
            def _pcha_init(_m, t):
                """The charge power vector [kW]"""
                return 0.0

            m.pcha = Var(m.time, initialize= _pcha_init, domain = NonNegativeReals, bounds=(0,m.Power_rating))
        
        if not hasattr(m, 'pfpk'):
            def _pfpk_init(_m):
                """Peak demand of a month [kW]"""
                return 0.0

            m.pfpk = Var(initialize= _pfpk_init, domain = NonNegativeReals, bounds=(0,m.Transformer_rating))
            
        if not hasattr(m, 'ptpk'):
            def _ptpk_init(_m, p):
                """Peak demand of different time-of-use periods of a month [kW]"""
                return 0.0

            m.ptpk = Var(m.period, initialize= _ptpk_init, domain = NonNegativeReals,bounds=(0,m.Transformer_rating))
        
        if not hasattr(m, 'xnet'):
            def _xnet_init(_m, t):
                """Xnet[i]=Max{Pload[i]-Ppv[i]+Pcha[i]-Pdis[i],0} [kW]"""
                return 0.0

            m.xnet = Var(m.time, initialize= _xnet_init, domain = NonNegativeReals,bounds=(0,m.Transformer_rating))
        
    def instantiate_model(self):
        """Instantiates the Pyomo ConcreteModel and populates it with supplied time series data."""
        if not hasattr(self, 'model'):
            self.model = ConcreteModel()

        m = self.model
        m.nhr = len(self.tou_energy_schedule)
        m.dml = len(self.tou_demand_rate)
        
        try:
            m.time = RangeSet(0, m.nhr - 1)
            
        except TypeError:
            # self.tou_energy_schedule is of type 'NoneType'
            m.time = []
        
        try:
            m.period = RangeSet(0, m.dml - 1)
            
        except TypeError:
            # self.tou_demand_rate is of type 'NoneType'
            m.period = []
        
        m.tou_er = [self.tou_energy_rate[self.tou_energy_schedule[t]] for t in range(m.nhr)]
        
        m.tou_dr = self.tou_demand_rate
        
        mask_ds = []
        for i in range(m.dml):
            listi=[int(self.tou_demand_schedule[t]==i) for t in range(m.nhr)]
            mask_ds.append(listi)
       
        m.mask_ds = mask_ds
        
        m.flt_dr = self.flat_demand_rate
        
        if self.nem_type==0:
            m.nem_sr=[0 for t in range(m.nhr)]
        elif self.nem_type==1:
            m.nem_sr=[self.nem_rate for t in range(m.nhr)]
        else:
            m.nem_sr=m.tou_er
        
        m.pld = self.load_profile
        m.ppv = self.pv_profile
        m.pnet= [m.pld[t]-m.ppv[t] for t in range(m.nhr)]
        
#        m.cost_cha = self.cost_charge
#        m.cost_dis = self.cost_discharge

              
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

        pcha = [m.pcha[n].value for n in m.time]
        pdis = [m.pdis[n].value for n in m.time]
        ptot = [m.pnet[n] + m.pcha[n].value - m.pdis[n].value for n in m.time]
        soc  = [m.s[n].value for n in m.time]
        pfpk_without_es = max(m.pnet)
        ptpk_without_es = [max(m.pnet[n]*m.mask_ds[p][n] for n in m.time) for p in m.period]
        
        demand_charge_with_es=m.pfpk.value*m.flt_dr+sum(m.ptpk[p].value*m.tou_dr[p] for p in m.period)
        demand_charge_without_es=pfpk_without_es*m.flt_dr+sum(ptpk_without_es[p]*m.tou_dr[p] for p in m.period)
        
        energy_charge_with_es=sum(max(0,ptot[n])*m.tou_er[n] for n in m.time)
        energy_charge_without_es=sum(max(0,m.pnet[n])*m.tou_er[n] for n in m.time)
        
        nem_charge_with_es=sum(min(0,ptot[n])*m.nem_sr[n] for n in m.time) #negative since it is credit
        nem_charge_without_es=sum(min(0,m.pnet[n])*m.nem_sr[n] for n in m.time) #negative since it is credit
        
        tot_bill_with_es=demand_charge_with_es + energy_charge_with_es + nem_charge_with_es
        tot_bill_without_es=demand_charge_without_es + energy_charge_without_es + nem_charge_without_es
        
        run_results = {'time': m.time, 'Pload': m.pld, 'Ppv': m.ppv, 'Pcharge': pcha, 'Pdischarge': pdis, 'Ptotal': ptot,
                       'state of charge': soc, 'energy_charge_with_es': energy_charge_with_es,'nem_charge_with_es': nem_charge_with_es, 
                       'demand_charge_with_es':demand_charge_with_es, 'total_bill_with_es': tot_bill_with_es, 
                       'energy_charge_without_es': energy_charge_without_es,'nem_charge_without_es': nem_charge_without_es, 
                       'demand_charge_without_es':demand_charge_without_es, 'total_bill_without_es': tot_bill_without_es }
        self.results = pd.DataFrame(run_results)

        self.total_bill_with_es = tot_bill_with_es
        self.total_bill_without_es = tot_bill_without_es

        self.demand_charge_with_es = demand_charge_with_es
        self.demand_charge_without_es = demand_charge_without_es

        self.energy_charge_with_es = energy_charge_with_es
        self.energy_charge_without_es = energy_charge_without_es

        self.nem_charge_with_es = nem_charge_with_es
        self.nem_charge_without_es = nem_charge_without_es
        
    def get_results(self):
        """Returns the decision variables and derived quantities in a DataFrame"""
        return self.results
    
    def has_energy_charges(self):
        """Returns True if there are energy charges (savings)."""
        if abs(self.energy_charge_with_es - self.energy_charge_without_es) > 1e-4:
            return True
        else:
            return False
    
    def has_demand_charges(self):
        """Returns True if there are demand charges (savings)."""
        if abs(self.demand_charge_with_es - self.demand_charge_without_es) > 1e-4:
            return True
        else:
            return False
    
    def has_nem_charges(self):
        """Returns True if there are net metering charges (savings)."""
        if abs(self.nem_charge_with_es - self.nem_charge_without_es) > 1e-4:
            return True
        else:
            return False


class BadParameterException(Exception):
    pass


class IncompatibleDataException(Exception):
    pass


if __name__ == '__main__':
    with open('btm_optimizer.log', 'w'):
        pass

    logging.basicConfig(filename='btm_optimizer.log', format='[%(levelname)s] %(asctime)s: %(message)s',
                        level=logging.INFO)