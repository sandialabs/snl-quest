from __future__ import absolute_import
import math

from pyomo.environ import *


class ExpressionsBlock:
    """Creates blocks for objective and constraint functions and assigns them to the Pyomo model."""

    def __init__(self, market_type):
        self._market_type = market_type

    @property
    def market_type(self):
        """The market formulation to create blocks for."""
        return self._market_type

    @market_type.setter
    def market_type(self, value):
        self._market_type = value

    def set_expressions(self, model):
        """Generates the objective and constraint expressions for model."""
        block_obj = Block()
        model.objectives = block_obj

        block_con = Block()
        model.constraints = block_con

        if self.market_type == 'arbitrage':
            self._objective_arb(block_obj)
            self._constraints_arb(block_con)
        elif self.market_type == 'ercot_arbreg':
            self._objective_ercot_arbreg(block_obj)
            self._constraints_ercot_arbreg(block_con)
        elif self.market_type == 'pjm_pfp':
            self._objective_pjm_pfp(block_obj)
            self._constraints_pjm_pfp(block_con)
        elif self.market_type == 'miso_pfp':
            self._objective_miso_pfp(block_obj)
            self._constraints_miso_pfp(block_con)
        elif self.market_type == 'isone_pfp':
            self._objective_isone_pfp(block_obj)
            self._constraints_isone_pfp(block_con)
        else:
            raise ValueError('Invalid market type specified!')

    def _objective_arb(self, block):
        eq_objective_arb(block)

    def _constraints_arb(self, block):
        eq_stateofcharge_arb(block)
        eq_stateofcharge_initial(block)
        eq_stateofcharge_final(block)
        ineq_stateofcharge_minimum(block)
        ineq_stateofcharge_maximum(block)
        ineq_power_limit(block)
        #ineq_charge_limit(block)
        #ineq_discharge_limit(block)

    def _objective_ercot_arbreg(self, block):
        eq_objective_ercot_arbreg(block)

    def _constraints_ercot_arbreg(self, block):
        eq_stateofcharge_ercot_arbreg(block)
        eq_stateofcharge_initial(block)
        eq_stateofcharge_final(block)
        ineq_stateofcharge_minimum_reserve_twoprod(block)
        ineq_stateofcharge_maximum_reserve_twoprod(block)
        ineq_power_limit_twoprod(block)
        # ineq_charge_limit_ercot_arbreg(block)
        # ineq_discharge_limit_ercot_arbreg(block)

    def _objective_pjm_pfp(self, block):
        eq_objective_pjm_pfp(block)

    def _constraints_pjm_pfp(self, block):
        eq_stateofcharge_pjm_pfp(block)
        eq_stateofcharge_initial(block)
        eq_stateofcharge_final(block)
        ineq_stateofcharge_minimum_reserve_oneprod(block)
        ineq_stateofcharge_maximum_reserve_oneprod(block)
        ineq_power_limit_oneprod(block)
        # ineq_charge_limit_pfp(block)
        # ineq_discharge_limit_pfp(block)

    def _objective_miso_pfp(self, block):
        eq_objective_miso_pfp(block)

    def _constraints_miso_pfp(self, block):
        eq_stateofcharge_miso_pfp(block)
        eq_stateofcharge_initial(block)
        eq_stateofcharge_final(block)
        ineq_stateofcharge_minimum_reserve_oneprod(block)
        ineq_stateofcharge_maximum_reserve_oneprod(block)
        ineq_power_limit_oneprod(block)
        # ineq_charge_limit_pfp(block)
        # ineq_discharge_limit_pfp(block)

    def _objective_isone_pfp(self, block):
        eq_objective_isone_pfp(block)

    def _constraints_isone_pfp(self, block):
        eq_stateofcharge_isone_pfp(block)
        eq_stateofcharge_initial(block)
        eq_stateofcharge_final(block)
        ineq_stateofcharge_minimum_reserve_oneprod(block)
        ineq_stateofcharge_maximum_reserve_oneprod(block)
        ineq_power_limit_oneprod(block)
        # ineq_charge_limit_pfp(block)
        # ineq_discharge_limit_pfp(block)


#############################
# Arbitrage only ############
#############################


def eq_objective_arb(m):
    """Net revenue over the time horizon for arbitrage only."""
    mp = m.parent_block()

    _expr = sum(
        (mp.price_electricity[t] * mp.q_d[t] - mp.price_electricity[t] * mp.q_r[t]) * math.e ** (-t * mp.R) for
        t in mp.time)

    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofcharge_arb(m):
    """Definition of state of charge for device in participating in arbitrage only."""
    mp = m.parent_block()

    def _eq_stateofcharge_arb(_m, t):
        return mp.Self_discharge_efficiency * mp.s[t] + mp.Round_trip_efficiency * mp.q_r[t] \
            - mp.q_d[t] == mp.s[t+1]       

    m.stateofcharge = Constraint(mp.time, rule=_eq_stateofcharge_arb)


def ineq_power_limit(m):
    """Limits the energy charged and discharged at each timestep to the device power rating."""
    mp = m.parent_block()

    def _ineq_power_limit(_m, t):
        return mp.Power_rating >= mp.q_r[t] + mp.q_d[t]

    m.power_limit = Constraint(mp.time, rule=_ineq_power_limit)


def ineq_charge_limit(m):
    """Limits the energy charged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_charge_limit(_m, t):
        return mp.Q_r_max >= mp.q_r[t]

    m.charge_limit = Constraint(mp.time, rule=_ineq_charge_limit)


def ineq_discharge_limit(m):
    """Limits the energy discharged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_discharge_limit(_m, t):
        return mp.Q_d_max >= mp.q_d[t]

    m.discharge_limit = Constraint(mp.time, rule=_ineq_discharge_limit)


###################################
# ERCOT Arbitrage and regulation ##
###################################


def eq_objective_ercot_arbreg(m):
    """Net revenue over the time horizon for ERCOT arbitrage and regulation."""

    mp = m.parent_block()

    _expr = sum((mp.price_electricity[t] * mp.q_d[t] - mp.price_electricity[t] * mp.q_r[t]
                 + mp.ru[t] * mp.q_ru[t] + mp.rd[t] * mp.q_rd[t]
                 + mp.price_electricity[t] * mp.q_ru[t] * mp.fraction_reg_up[t]
                 - mp.price_electricity[t] * mp.q_rd[t] * mp.fraction_reg_down[t])
                * math.e ** (-t * mp.R) for t in mp.time)

    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofcharge_ercot_arbreg(m):
    """Definition of state of charge for device participating in ERCOT arbitrage and regulation."""
    mp = m.parent_block()

    def _eq_stateofcharge_ercot_arbreg(_m, t):
        return mp.Self_discharge_efficiency * mp.s[t] + mp.Round_trip_efficiency * mp.q_r[t] \
                - mp.q_d[t] + mp.Round_trip_efficiency * mp.fraction_reg_down[t] * mp.q_rd[t] \
                - mp.fraction_reg_up[t] * mp.q_ru[t] == mp.s[t+1]

    m.stateofcharge = Constraint(mp.time, rule=_eq_stateofcharge_ercot_arbreg)


def ineq_charge_limit_ercot_arbreg(m):
    """Limits the energy charged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_charge_limit_arbreg(_m, t):
        return mp.Q_r_max >= mp.q_r[t] + mp.q_rd[t]

    m.charge_limit = Constraint(mp.time, rule=_ineq_charge_limit_arbreg)


def ineq_discharge_limit_ercot_arbreg(m):
    """Limits the energy discharged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_discharge_limit_ercot_arbreg(_m, t):
        return mp.Q_d_max >= mp.q_d[t] + mp.q_ru[t]

    m.discharge_limit = Constraint(mp.time, rule=_ineq_discharge_limit_ercot_arbreg)


#############################
# PJM Pay-for-Performance ###
#############################


def eq_objective_pjm_pfp(m):
    """Net revenue over the time horizon for pay-for-performance in PJM market."""
    mp = m.parent_block()

    _expr = sum((mp.price_electricity[t] * mp.q_d[t] - mp.price_electricity[t] * mp.q_r[t]
                 + mp.q_reg[t] * mp.Perf_score * (mp.mi_ratio[t] * mp.rmpcp[t] + mp.rmccp[t]))
                * math.e ** (-t * mp.R) for t in mp.time)

    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofcharge_pjm_pfp(m):
    """Definition of state of charge for device in PJM pay-for-performance market."""
    mp = m.parent_block()

    def _eq_stateofcharge_pjm_pfp(_m, t):
        return mp.Self_discharge_efficiency * mp.s[t] + mp.Round_trip_efficiency * mp.q_r[t] \
                - mp.q_d[t] + mp.Round_trip_efficiency * mp.fraction_reg_down[t] * mp.q_reg[t] \
                - mp.fraction_reg_up[t] * mp.q_reg[t] == mp.s[t+1]

    m.stateofcharge = Constraint(mp.time, rule=_eq_stateofcharge_pjm_pfp)


def ineq_charge_limit_pjm_pfp(m):
    """Limits the energy charged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_charge_limit_pjm_pfp(_m, t):
        return mp.Q_r_max >= mp.q_r[t] + mp.q_reg[t]

    m.charge_limit = Constraint(mp.time, rule=_ineq_charge_limit_pjm_pfp)


def ineq_discharge_limit_pjm_pfp(m):
    """Limits the energy discharged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_discharge_limit_pjm_pfp(_m, t):
        return mp.Q_d_max >= mp.q_d[t] + mp.q_reg[t]

    m.discharge_limit = Constraint(mp.time, rule=_ineq_discharge_limit_pjm_pfp)


#############################
# MISO Pay-for-Performance ##
#############################


def eq_objective_miso_pfp(m):
    """Net revenue over the time horizon for pay-for-performance in MISO regulation market."""
    mp = m.parent_block()
    _expr = sum((mp.price_electricity[t] * mp.q_d[t] - mp.price_electricity[t] * mp.q_r[t]
                 + (1 + mp.Make_whole) * mp.q_reg[t] * mp.Perf_score * mp.regMCP[t])
                * math.e ** (-t * mp.R) for t in mp.time)

    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofcharge_miso_pfp(m):
    """Definition of state of charge for device in MISO market."""
    mp = m.parent_block()

    def _eq_stateofcharge_miso_pfp(_m, t):
        return mp.Self_discharge_efficiency * mp.s[t] + mp.Round_trip_efficiency * mp.q_r[t] \
                - mp.q_d[t] + mp.Round_trip_efficiency * mp.fraction_reg_down[t] * mp.q_reg[t] \
                - mp.fraction_reg_up[t] * mp.q_reg[t] == mp.s[t+1]

    m.stateofcharge = Constraint(mp.time, rule=_eq_stateofcharge_miso_pfp)


def ineq_charge_limit_miso_pfp(m):
    """Limits the energy charged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_charge_limit_miso_pfp(_m, t):
        return mp.Q_r_max >= mp.q_r[t] + mp.q_reg[t]

    m.charge_limit = Constraint(mp.time, rule=_ineq_charge_limit_miso_pfp)


def ineq_discharge_limit_miso_pfp(m):
    """Limits the energy discharged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_discharge_limit_miso_pfp(_m, t):
        return mp.Q_d_max >= mp.q_d[t] + mp.q_reg[t]

    m.discharge_limit = Constraint(mp.time, rule=_ineq_discharge_limit_miso_pfp)


#################################
#  ISO-NE Pay-for-Performance  ##
#            FW                ##
#################################


def eq_objective_isone_pfp(m):
    """Net revenue over the time horizon for pay-for-performance in ISO-NE market."""
    mp = m.parent_block()

    _expr = sum((mp.price_electricity[t] * mp.q_d[t] - mp.price_electricity[t] * mp.q_r[t]
                 + mp.q_reg[t] * mp.rmccp[t]) * math.e ** (-t * mp.R) for t in mp.time)

    mp.objective_expr += _expr
    m.objective_rt = Expression(expr=_expr)


def eq_stateofcharge_isone_pfp(m):
    """Definition of state of charge for device in ISO-NE market."""
    mp = m.parent_block()

    def _eq_stateofcharge_isone_pfp(_m, t):
        return mp.Self_discharge_efficiency * mp.s[t] + mp.Round_trip_efficiency * mp.q_r[t] \
                - mp.q_d[t] + mp.Round_trip_efficiency * mp.fraction_reg_down[t] * mp.q_reg[t] \
                - mp.fraction_reg_up[t] * mp.q_reg[t] == mp.s[t+1]

    m.stateofcharge = Constraint(mp.time, rule=_eq_stateofcharge_isone_pfp)


# def ineq_stateofcharge_minimum_isone_pfp(m): # WHY REPLICATE EQUATIONS THAT ARE THE SAME FOR DIFF MARKETS???? -FW
#     """
#     Requires the state of charge of the energy storage device to remain above the minimum at any given time.
#
#     :param m: Pyomo ConcreteModel object
#     :return: n/a
#     """
#     mp = m.parent_block()
#
#     def _ineq_stateofcharge_minimum_isone_pfp(_m, t):
#         try:
#             return mp.s[t] >= mp.S_min
#             # return mp.s[t] >= mp.S_min + mp.q_reg[t] # Other code supposedly so it can bid?
#         except ValueError:
#             return Constraint.Feasible
#
#     m.stateofcharge_minimum = Constraint(mp.time_interval, rule=_ineq_stateofcharge_minimum_isone_pfp)
#
#
# def ineq_stateofcharge_maximum_isone_pfp(m):
#     """
#     Requires the state of charge of the energy storage device to remain below the maximum at any given time.
#
#     :param m: Pyomo ConcreteModel object
#     :return: n/a
#     """
#     mp = m.parent_block()
#
#     def _ineq_stateofcharge_maximum_isone_pfp(_m, t):
#         try:
#             return mp.s[t] <= mp.S_max
#             # return mp.s[t] <= mp.S_max - mp.Gamma_c*mp.q_reg[t] # Other code supposedly so it can bid?
#         except ValueError:
#             return Constraint.Feasible
#
#     m.stateofcharge_maximum = Constraint(mp.time_interval, rule=_ineq_stateofcharge_maximum_isone_pfp)
#
#
# def ineq_charge_limit_isone_pfp(m):
#     """
#     Limits the energy charged at each timestep to the device maximum.
#
#     :param m: Pyomo ConcreteModel object
#     :return: n/a
#     """
#     mp = m.parent_block()
#
#     def _ineq_charge_limit_isone_pfp(_m, t):
#         return mp.Q_r_max >= mp.q_r[t] + mp.q_reg[t]
#
#     m.charge_limit = Constraint(mp.time_interval, rule=_ineq_charge_limit_isone_pfp)
#
#
# def ineq_discharge_limit_isone_pfp(m):
#     """
#     Limits the energy discharged at each timestep to the device maximum.
#
#     :param m: Pyomo ConcreteModel object
#     :return: n/a
#     """
#     mp = m.parent_block()
#
#     def _ineq_discharge_limit_isone_pfp(_m, t):
#         return mp.Q_d_max >= mp.q_d[t] + mp.q_reg[t]
#
#     m.discharge_limit = Constraint(mp.time_interval, rule=_ineq_discharge_limit_isone_pfp)

##################################
#          Generic              ##
#     Equality Constraints      ##
##################################

def eq_stateofcharge_initial(m):
    """Requires the initial state of charge of the energy storage device to equal its minimum value."""
    mp = m.parent_block()

    def _eq_stateofcharge_initial(_m, t):
        if not t == 0:
            return Constraint.Skip
        else:
            return mp.s[t] == mp.State_of_charge_init

    m.stateofcharge_initial = Constraint(mp.soc_time, rule=_eq_stateofcharge_initial)

def eq_stateofcharge_final(m):
    """Requires the final state of charge of the energy storage device to equal its initial value."""
    mp = m.parent_block()

    def _eq_stateofcharge_final(_m, t):
        if not t == mp.soc_time[-1]:
            return Constraint.Skip
        else:
            return mp.s[t] == mp.State_of_charge_init
        
    m.stateofcharge_final = Constraint(mp.soc_time, rule=_eq_stateofcharge_final)


##################################
#          Generic              ##
#   Inequality Constraints      ##
##################################


def ineq_stateofcharge_minimum(m):
    """Requires the state of charge of the energy storage device to remain above the minimum at any given time."""
    mp = m.parent_block()

    def _ineq_stateofcharge_minimum(_m, t):
        return mp.s[t] >= mp.Reserve_charge_min*mp.Energy_capacity

    m.stateofcharge_minimum = Constraint(mp.soc_time, rule=_ineq_stateofcharge_minimum)


def ineq_stateofcharge_maximum(m):
    """Requires the state of charge of the energy storage device to remain below the maximum at any given time."""
    mp = m.parent_block()

    def _ineq_stateofcharge_maximum(_m, t):
        return mp.s[t] <= mp.Energy_capacity - mp.Reserve_charge_max*mp.Energy_capacity

    m.stateofcharge_maximum = Constraint(mp.soc_time, rule=_ineq_stateofcharge_maximum)


def ineq_stateofcharge_minimum_reserve_oneprod(m):
    """Requires the state of charge of the energy storage device to remain above the minimum at any given time. Accounts for penalty aversion parameters."""
    mp = m.parent_block()

    def _ineq_stateofcharge_minimum(_m, t):
        return mp.s[t+1] >= mp.Reserve_reg_min*mp.q_reg[t] + mp.Reserve_charge_min*mp.Energy_capacity

    m.stateofcharge_minimum = Constraint(mp.time, rule=_ineq_stateofcharge_minimum)


def ineq_stateofcharge_maximum_reserve_oneprod(m):
    """Requires the state of charge of the energy storage device to remain below the maximum at any given time. Accounts for penalty aversion parameters."""
    mp = m.parent_block()

    def _ineq_stateofcharge_maximum(_m, t):
        return mp.s[t+1] <= mp.Energy_capacity - mp.Round_trip_efficiency*mp.Reserve_reg_max*mp.q_reg[t] \
                              - mp.Reserve_charge_max*mp.Energy_capacity

    m.stateofcharge_maximum = Constraint(mp.time, rule=_ineq_stateofcharge_maximum)


def ineq_stateofcharge_minimum_reserve_twoprod(m):
    """Requires the state of charge of the energy storage device to remain above the minimum at any given time. Accounts for penalty aversion parameters."""
    mp = m.parent_block()

    def _ineq_stateofcharge_minimum(_m, t):
        return mp.s[t+1] >= mp.Reserve_reg_min*mp.q_ru[t] + mp.Reserve_charge_min*mp.Energy_capacity

    m.stateofcharge_minimum = Constraint(mp.time, rule=_ineq_stateofcharge_minimum)


def ineq_stateofcharge_maximum_reserve_twoprod(m):
    """Requires the state of charge of the energy storage device to remain below the maximum at any given time. Accounts for penalty aversion parameters."""
    mp = m.parent_block()

    def _ineq_stateofcharge_maximum(_m, t):
        return mp.s[t+1] <= mp.Energy_capacity - mp.Round_trip_efficiency*mp.Reserve_reg_max*mp.q_rd[t] \
                              - mp.Reserve_charge_max*mp.Energy_capacity

    m.stateofcharge_maximum = Constraint(mp.time, rule=_ineq_stateofcharge_maximum)


def ineq_power_limit_oneprod(m):
    """Limits the energy charged and discharged at each timestep to the device power rating."""
    mp = m.parent_block()

    def _ineq_power_limit_oneprod(_m, t):
        return mp.Power_rating >= mp.q_r[t] + mp.q_d[t] + mp.q_reg[t]

    m.power_limit = Constraint(mp.time, rule=_ineq_power_limit_oneprod)


def ineq_power_limit_twoprod(m):
    """Limits the energy charged and discharged at each timestep to the device power rating."""
    mp = m.parent_block()

    def _ineq_power_limit_twoprod(_m, t):
        return mp.Power_rating >= mp.q_r[t] + mp.q_d[t] + mp.q_ru[t] + mp.q_rd[t]

    m.power_limit = Constraint(mp.time, rule=_ineq_power_limit_twoprod)

##################################
#  Generic Pay-for-Performance  ##
#   Inequality Constraints      ##
##################################


def ineq_charge_limit_pfp(m):
    """Limits the energy charged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_charge_limit_pfp(_m, t):
        return mp.Q_r_max >= mp.q_r[t] + mp.q_reg[t]

    m.charge_limit = Constraint(mp.time, rule=_ineq_charge_limit_pfp)


def ineq_discharge_limit_pfp(m):
    """Limits the energy discharged at each timestep to the device maximum."""
    mp = m.parent_block()

    def _ineq_discharge_limit_pfp(_m, t):
        return mp.Q_d_max >= mp.q_d[t] + mp.q_reg[t]

    m.discharge_limit = Constraint(mp.time, rule=_ineq_discharge_limit_pfp)