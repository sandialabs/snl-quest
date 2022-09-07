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

        self._objective_peaker_rep(block_obj)
        self._constraints_peaker_rep(block_con)
        

    def _objective_peaker_rep(self, block):
        eq_objective_peaker_rep(block)

    def _constraints_peaker_rep(self, block):
        eq_stateofenergy(block)
        ineq_power_capacity_rule(block)
        ineq_gen_matching_rule(block)
        ineq_meets_rule(block)
  
def eq_objective_peaker_rep(m):
    mp = m.parent_block()
    _expr = (mp.cost_per_MWh_BESS * mp.energy_capacity
                + mp.cost_per_MW_BESS * mp.power_capacity 
                + mp.cost_per_MW_PV_system * mp.pv_capacity 
                + 0.000001 * sum([mp.meets[i] for i in mp.time]) )
    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofenergy(m):
    """Definition of state of charge"""
    mp = m.parent_block()
   
    def _eq_stateofenergy(_m, t):
        return mp.soe[t+1] - mp.soe[t] == mp.pe_d[t] + mp.pe_c[t]*mp.energy_efficiency
    m.stateofenergy = Constraint(mp.time, rule=_eq_stateofenergy)

    def _energy_capacity_rule(_m,i):
        return mp.soe[i] <= mp.energy_capacity
    m.soe_energy_capacity = Constraint(mp.time,rule=_energy_capacity_rule)

    def _eq_stateofenergy_start(_m):
        return mp.soe[0] == mp.energy_capacity
    m.stateofenergy_start = Constraint(rule=_eq_stateofenergy_start)

    T  = mp.n-1
    def _eq_stateofenergy_final(_m):
        return mp.soe[T] == mp.energy_capacity
    m.stateofenergy_final = Constraint(rule=_eq_stateofenergy_final)

def ineq_power_capacity_rule(m):
    mp = m.parent_block()
    def _power_capacity_rule(battery, i):
        return mp.pe_c[i] - mp.pe_d[i] <= mp.power_capacity
    m.charge_capacity_constraint = Constraint(mp.time, rule=_power_capacity_rule)

def ineq_gen_matching_rule(m):
    mp = m.parent_block()
    def _gen_matching_rule(battery,i):
        return -mp.pe_d[i] - mp.pe_c[i] + mp.pv_capacity*mp.pv_profile[i] >= mp.plant_dispatch[i]*mp.meets[i]
    m.peak_power = Constraint(mp.time,  rule=_gen_matching_rule)

def ineq_meets_rule(m):
    mp = m.parent_block()
    def _meets_rule(battery):
        operating = []
        for ii in mp.time:
            if mp.plant_dispatch[ii] > 0:
                operating.append(ii)
        operating_n = len(operating)     
        return mp.replacement_fraction <= sum([mp.meets[i] for i in operating])/operating_n
    m.meets_fraction = Constraint(rule=_meets_rule)
