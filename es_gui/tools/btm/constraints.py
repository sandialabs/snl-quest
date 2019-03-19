from __future__ import absolute_import
import math

from pyomo.environ import *


class ExpressionsBlock:
    """Creates blocks for objective and constraint functions and assigns them to the Pyomo model."""

    def set_expressions(self, model):
        """Generates the objective and constraint expressions for model."""
        block_obj = Block()
        model.objectives = block_obj

        block_con = Block()
        model.constraints = block_con

        self._objective_btm(block_obj)
        self._constraints_btm(block_con)
        

    def _objective_btm(self, block):
        eq_objective_btm(block)

    def _constraints_btm(self, block):
        eq_stateofcharge(block)
        eq_stateofcharge_final(block)
        ineq_peak_demand(block)
        ineq_tou_demand(block)
        ineq_nem_xnet(block)

  
def eq_objective_btm(m):
    
    mp = m.parent_block()
    
    _expr = mp.pfpk*mp.flt_dr + sum(mp.ptpk[p]*mp.tou_dr[p] for p in mp.period) +\
    sum(mp.xnet[t]*(mp.tou_er[t]-mp.nem_sr[t])+(mp.pnet[t]+mp.pcha[t]-mp.pdis[t])*mp.nem_sr[t] for t in mp.time)
    
#    _expr = mp.pfpk*mp.flt_dr +\
#    sum(mp.xnet[t]*(mp.tou_er[t]-mp.nem_sr[t])+(mp.pnet[t]+mp.pcha[t]-mp.pdis[t])*mp.nem_sr[t] for t in mp.time)
#    
    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofcharge(m):
    """Definition of state of charge"""
    mp = m.parent_block()
   
    def _eq_stateofcharge(_m, t):
        if t==0:
            spre=mp.State_of_charge_init*mp.Energy_capacity
        else:
            spre=mp.s[t-1]
        return mp.Self_discharge_efficiency * spre + mp.Round_trip_efficiency * mp.pcha[t] \
            - mp.pdis[t] == mp.s[t]       

    m.stateofcharge = Constraint(mp.time, rule=_eq_stateofcharge)

def eq_stateofcharge_final(m):
    """Requires the final state of charge of the energy storage device to equal its initial value."""
    mp = m.parent_block()
    T  = mp.nhr-1
    def _eq_stateofcharge_final(_m, t):
        return mp.s[T] == mp.State_of_charge_init*mp.Energy_capacity
    m.stateofcharge_final = Constraint(mp.time, rule=_eq_stateofcharge_final)


def ineq_peak_demand(m):
    """Requires all net power at time t less the peak demand"""
    mp = m.parent_block()
    def _ineq_peak_demand(_m, t):
        return mp.pnet[t]+mp.pcha[t]-mp.pdis[t]-mp.pfpk<=0
    m.peak_demand = Constraint(mp.time, rule=_ineq_peak_demand)

def ineq_tou_demand(m):
    """Requires all net power at time t period p less the peak demand of period p"""
    mp = m.parent_block()
    def _ineq_tou_demand(_m, p, t):
        return mp.mask_ds[p][t]*(mp.pnet[t]+mp.pcha[t]-mp.pdis[t])<=mp.ptpk[p]
    m.tou_demand = Constraint(mp.period, mp.time, rule=_ineq_tou_demand)
    
def ineq_nem_xnet(m):
    """Requires all net power at time t less the peak demand"""
    mp = m.parent_block()
    def _ineq_nem_xnet(_m, t):
        return mp.pnet[t]+mp.pcha[t]-mp.pdis[t]<= mp.xnet[t]
    m.nem_xnet = Constraint(mp.time, rule=_ineq_nem_xnet)