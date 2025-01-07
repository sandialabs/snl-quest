from __future__ import absolute_import
import math
import re
from pyomo.environ import *
import pandas as pd
import numpy as np


class ExpressionsBlock:
    """Creates blocks for objective and constraint functions and assigns them to the Pyomo model."""

    def __init__(self, data_handler):
        self.data_handler = data_handler

    def set_expressions(self, model):
        """Generates the objective and constraint expressions for model."""
        block_obj = Block()
        model.objectives = block_obj

        block_con = Block()
        model.constraints = block_con

        self._objective(block_obj)

        self._total_constraints(block_con)
        self._gen_daily_constraints(block_con)
        self._es_constraints(block_con)
        self._capacity_factor_constraints(block_con)
        self._misc_constraints(block_con)

    def _objective(self, block):
        obj_expression(block, self.data_handler.Cpv, self.data_handler.Cwind,
                        self.data_handler.Cpcs, self.data_handler.Ces, self.data_handler.es_devices)
    
    def _total_constraints(self, block):
        pv_total_constraint_rule(block, self.data_handler.Ppv_init)
        wind_total_constraint_rule(block, self.data_handler.Pwind_init)
        es_total_constraint_rule(block, self.data_handler.Pes_init, self.data_handler.es_devices)

    def _gen_daily_constraints(self, block):
        pv_daily_generation_constraint_rule(block, self.data_handler.PV_inso)
        wind_daily_generation_constraint_rule(block, self.data_handler.Wind_f)
        pv_daily_curtailment_constraint_rule(block)
        wind_daily_curtailment_constraint_rule(block)
        gen_daily_generation_constraint_rule(block)

    def _es_constraints(self, block):
        es_soe_constraint_rule1(block, self.data_handler.es_devices)
        es_soe_constraint_rule2(block, self.data_handler.es_devices)
        es_charge_discharge_constraint_rule(block)

        cycling_ls = [self.data_handler.es_devices[device]['cycle'] for device in self.data_handler.es_devices]
        
        if 'Weekly' in cycling_ls:
            es_weekly_cycling_constraint_rule(block, self.data_handler.es_devices)
        
        if 'Monthly' in cycling_ls:
            es_monthly_cycling_constraint_rule(block, self.data_handler.es_devices)

        if 'Seasonal' in cycling_ls:
            es_seasonal_cycling_constraint_rule(block, self.data_handler.es_devices)

        if 'Annual' in cycling_ls:
            es_annual_cycling_constraint_rule(block, self.data_handler.es_devices)

    def _capacity_factor_constraints(self, block):
        gen_capacity_factor_constraint_rule(block)

    def _misc_constraints(self, block):
        rps_constraint_rule(block)
        energy_daily_balance_constraint_rule(block, self.data_handler.Eload)


# Objective function
def obj_expression(m, Cpv, Cwind, Cpcs, Ces, es_devices):
    mp = m.parent_block()

    _expr = sum(mp.Ppv[yr]*Cpv[yr-1] + mp.Pwind[yr]*Cwind[yr-1] + \
                sum(mp.Pes[device, yr]*(es_devices[device]['duration']*Ces[device][yr-1] 
                    + Cpcs[yr-1]) for device in es_devices) for yr in mp.year)
    
    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)

# Total installed capacities are represented as constraints below:
def pv_total_constraint_rule(m, Ppv_init):
    mp = m.parent_block()
    pv_drate = 0.01 # degradation rate = 3%/yr
    pv_eol  = 0.8   # end of life capacity = 80%

    def _pv_total_constraint_rule(_m, yr):
        return mp.Ppv_tot[yr]==Ppv_init*(1-yr*pv_drate)*int(1-yr*pv_drate>=pv_eol) + sum(mp.Ppv[k]*(1-(yr-k)*pv_drate)*int(1-(yr-k)*pv_drate>=pv_eol) 
                                                                                         for k in range(1,yr+1))

    m.pv_total_constraint = Constraint(mp.year, rule=_pv_total_constraint_rule)

def wind_total_constraint_rule(m, Pwind_init):
    mp = m.parent_block()
    
    def _wind_total_constraint_rule(_m, yr):
        return mp.Pwind_tot[yr]==Pwind_init + sum(mp.Pwind[k] for k in range(1,yr+1))  
    
    m.wind_total_constraint = Constraint(mp.year, rule=_wind_total_constraint_rule)

def es_total_constraint_rule(m, Pes_init, es_devices):
    """Total Capacity of each ES technology"""
    mp = m.parent_block()

    def _es_total_constraint_rule(_m, device, yr):
        deg = es_devices[device]['deg']
        eol = es_devices[device]['eol']
        return mp.Pes_tot[device, yr] == Pes_init[device]*(1-yr*deg)*int(1-yr*deg>=eol)+\
            sum(mp.Pes[device, k]*(1-(yr-k)*deg)*int(1-(yr-k)*deg>=eol) for k in range(1, yr+1))
    
    m.es_total_constraint = Constraint(mp.es_devices, mp.year, rule=_es_total_constraint_rule)

# Daily renewable energy generations are represented as constraints below:
def pv_daily_generation_constraint_rule(m, PV_inso):
    mp = m.parent_block()

    def _pv_daily_generation_constraint_rule(_m, yr, d):
        return mp.Epv[yr,d] == mp.Ppv_tot[yr]*PV_inso[yr-1][d-1]
    
    m.pv_daily_generation_constraint = Constraint(mp.year, mp.day, rule=_pv_daily_generation_constraint_rule)

def wind_daily_generation_constraint_rule(m, Wind_f):
    mp = m.parent_block()

    def _wind_daily_generation_constraint_rule(_m, yr, d):
        return mp.Ewind[yr,d] == mp.Pwind_tot[yr]*Wind_f[yr-1][d-1]
    
    m.wind_daily_generation_constraint = Constraint(mp.year, mp.day, rule=_wind_daily_generation_constraint_rule)

# Daily renewable energy curtailments are represented as constraints below:
def pv_daily_curtailment_constraint_rule(m):
    mp = m.parent_block()

    def _pv_daily_curtailment_constraint_rule(_m, yr, d):
        return mp.Epv_cut[yr,d] <= mp.Epv[yr,d]
    
    m.pv_daily_curtailment_constraint = Constraint(mp.year, mp.day, rule=_pv_daily_curtailment_constraint_rule)

def wind_daily_curtailment_constraint_rule(m):
    mp = m.parent_block()

    def _wind_daily_curtailment_constraint_rule(_m, yr, d):
        return mp.Ewind_cut[yr,d] <= mp.Ewind[yr,d]
    
    m.wind_daily_curtailment_constraint = Constraint(mp.year, mp.day, rule=_wind_daily_curtailment_constraint_rule)

# Daily generation constraints:

def gen_daily_generation_constraint_rule(m):
    mp = m.parent_block()

    def _gen_daily_generation_constraint_rule(_m, gen, yr, d):
        return mp.Egens[gen, yr, d] <= 24*mp.Pgen[gen][yr-1]
    
    m.gen_daily_generation_constraint_rule = Constraint(mp.gen_nums, mp.year, mp.day, rule=_gen_daily_generation_constraint_rule)

# Energy storage state of energy (soe) constraints:

def es_soe_constraint_rule1(m, es_devices):
    mp = m.parent_block()

    def _es_soe_constraint_rule1(_m, device, yr, d):
        if d==1:
            Ses_pre=0.5*es_devices[device]['duration']*mp.Pes_tot[device, yr]
        else:
            Ses_pre=mp.Ses[device, yr, d-1]
        
        return mp.Ses[device, yr, d] == Ses_pre + es_devices[device]['rte']*mp.Ees_cha[device, yr, d] - mp.Ees_dis[device, yr, d]
    
    m.es_soe_constraint1 = Constraint(mp.es_devices, mp.year, mp.day, rule=_es_soe_constraint_rule1)

def es_soe_constraint_rule2(m, es_devices):
    mp = m.parent_block()

    def _es_soe_constraint_rule2(_m, device, yr, d):
        return mp.Ses[device, yr, d] <= es_devices[device]['duration']*mp.Pes_tot[device, yr]
    
    m.es_soe_constraint2 = Constraint(mp.es_devices, mp.year, mp.day, rule=_es_soe_constraint_rule2)

# Storage daily charge-discharge constraints

def es_charge_discharge_constraint_rule(m):
    mp = m.parent_block()

    def _es_charge_discharge_constraint_rule(_m, device, yr, d):
        return mp.Ees_dis[device, yr, d] + mp.Ees_cha[device, yr, d] <= 24*mp.Pes_tot[device, yr]
    
    m.es_charge_discharge_constraint_rule = Constraint(mp.es_devices, mp.year, mp.day, rule=_es_charge_discharge_constraint_rule)

def es_weekly_cycling_constraint_rule(m, es_devices):
    mp = m.parent_block()

    def _es_weekly_cycling_constraint_rule(_m, device, yr, w):
        return sum(mp.Ees_dis[device, yr, d] - es_devices[device]['rte']*mp.Ees_cha[device, yr, d] 
                   for d in range(7*w-6,7*w+1))==0
    
    m.es_weekly_cycling_constraint_rule = Constraint(mp.weekly_devices, mp.year, mp.week, rule=_es_weekly_cycling_constraint_rule)

def es_monthly_cycling_constraint_rule(m, es_devices):
    mp = m.parent_block()

    def _es_monthly_cycling_constraint_rule(_m, device, yr, w):
        return sum(mp.Ees_dis[device, yr, d] - es_devices[device]['rte']*mp.Ees_cha[device, yr, d]
                   for d in range(28*m-27,28*m+1))==0
    
    m.es_monthly_cycling_constraint_rule = Constraint(mp.monthly_devices, mp.year, mp.month, rule=_es_monthly_cycling_constraint_rule)

def es_seasonal_cycling_constraint_rule(m, es_devices):
    mp = m.parent_block()

    def _es_seasonal_cycling_constraint_rule(_m, device, yr, s):
        return sum(mp.Ees_dis[device, yr, d] - es_devices[device]['rte']*mp.Ees_cha[device, yr, d]
                   for d in range(91*s-90,91*s+1))==0
    
    m.es_seasonal_cycling_constraint = Constraint(mp.seasonal_devices, mp.year, mp.season, rule=_es_seasonal_cycling_constraint_rule)

def es_annual_cycling_constraint_rule(m, es_devices):
    mp = m.parent_block()

    def _es_annual_cycling_constraint_rule(_m, device, yr):
        return sum(mp.Ees_dis[device, yr, d] - es_devices[device]['rte']*mp.Ees_cha[device, yr, d] for d in mp.day) == 0
    
    m.es_annual_cycling_constraint = Constraint(mp.annual_devices, mp.year, rule=_es_annual_cycling_constraint_rule)

# Capacity factor constraints:
def gen_capacity_factor_constraint_rule(m):
    mp = m.parent_block()

    def _gen_capacity_factor_constraint_rule_1(_m, gen, yr):
        return sum(mp.Egens[gen, yr, d] for d in mp.day) <= 8760*mp.Pgen[gen][yr-1]*mp.c_factors[gen] #make c_factors
    
    m.gen_capacity_factor_constraint_rule = Constraint(mp.gen_nums, mp.year, rule=_gen_capacity_factor_constraint_rule_1)

# Renewable Portfolio Standard Constraint
def rps_constraint_rule(m):
    mp = m.parent_block()

    def _rps_constraint_rule(_m, yr):
        return sum(mp.rps_targets[yr]*(mp.Epv[yr, d] + mp.Ewind[yr, d] + sum(mp.Egens[gen, yr, d] for gen in mp.clean)) - sum(mp.Egens[gen, yr, d] for gen in mp.dirty) for d in mp.day) >= 0 #make E_dirty and E_clean
    
    m.rps_constraint = Constraint(mp.year_rps, rule=_rps_constraint_rule)

# Energy balance constraint
def energy_daily_balance_constraint_rule(m, Eload):
    mp = m.parent_block()

    def _energy_daily_balance_constraint_rule(_m, yr, d):
        return mp.Epv[yr,d] - mp.Epv_cut[yr,d] + mp.Ewind[yr,d] - mp.Ewind_cut[yr,d] + \
            sum(mp.Ees_dis[device, yr, d] for device in mp.es_devices) - \
            sum(mp.Ees_cha[device, yr, d] for device in mp.es_devices) + \
            sum(mp.Egens[gen, yr, d] for gen in mp.gen_nums) == Eload[yr-1][d-1]

    m.energy_daily_balance_constraint= Constraint(mp.year, mp.day, rule=_energy_daily_balance_constraint_rule)
    