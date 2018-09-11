from __future__ import division, print_function, absolute_import

import logging

from pyomo.environ import *
import pandas as pd
import numpy as np

from es_gui.tools import optimizer
from es_gui.tools.valuation.constraints import ExpressionsBlock


class ValuationOptimizer(optimizer.Optimizer):
    """A framework wrapper class for creating Pyomo ConcreteModels for energy storage valuation."""

    def __init__(self, price_electricity=None,
                 price_reg_up=None, price_reg_down=None,
                 price_reg_capacity=None, price_reg_performance=None,
                 cost_charge=None, cost_discharge=None,
                 mileage_slow=None, mileage_fast=None, mileage_ratio=None,
                 fraction_reg_up=None, fraction_reg_down=None,
                 market_type='arbitrage',
                 solver='glpk'):
        self._model = ConcreteModel()
        self._market_type = market_type
        self._solver = solver

        self._expressions_block = None

        self._price_electricity = price_electricity

        self._price_reg_up = price_reg_up
        self._price_reg_down = price_reg_down

        self._price_reg_capacity = price_reg_capacity
        self._price_reg_performance = price_reg_performance

        self._cost_charge = cost_charge
        self._cost_discharge = cost_discharge

        self._mileage_slow = mileage_slow
        self._mileage_fast = mileage_fast
        self._mileage_ratio = mileage_ratio

        self._fraction_reg_up = fraction_reg_up
        self._fraction_reg_down = fraction_reg_down

        self._results = None
        self._gross_revenue = None

    @property
    def price_electricity(self):
        """The price for buying electricity via energy arbitrage [$/MWh]."""
        return self._price_electricity

    @price_electricity.setter
    def price_electricity(self, value):
        self._price_electricity = value

    @property
    def price_reg_up(self):
        """The price for providing regulation up products [$/MWh]."""
        return self._price_reg_up

    @price_reg_up.setter
    def price_reg_up(self, value):
        self._price_reg_up = value

    @property
    def price_reg_down(self):
        """The price for providing regulation down products [$/MWh]."""
        return self._price_reg_down

    @price_reg_down.setter
    def price_reg_down(self, value):
        self._price_reg_down = value

    @property
    def price_reg_capacity(self):
        """The price for providing capacity for regulation services in pay-for-performance markets [$/MWh]."""
        return self._price_reg_capacity

    @price_reg_capacity.setter
    def price_reg_capacity(self, value):
        self._price_reg_capacity = value

    @property
    def price_reg_performance(self):
        """The price for providing regulation services; based on mileage or performance [$/MWh]."""
        return self._price_reg_performance

    @price_reg_performance.setter
    def price_reg_performance(self, value):
        self._price_reg_performance = value

    @property
    def cost_charge(self):
        """The cost of charging the energy storage device [$/MWh]."""
        return self._cost_charge

    @cost_charge.setter
    def cost_charge(self, value):
        self._cost_charge = value

    @property
    def cost_discharge(self):
        """The cost of discharging the energy storage device [$/MWh]."""
        return self._cost_discharge

    @cost_discharge.setter
    def cost_discharge(self, value):
        self._cost_discharge = value

    @property
    def mileage_slow(self):
        """The mileage of the low pass-filtered ACE signal."""
        return self._mileage_slow

    @mileage_slow.setter
    def mileage_slow(self, value):
        self._mileage_slow = value

    @property
    def mileage_fast(self):
        """The mileage of the high pass-filtered ACE signal."""
        return self._mileage_fast

    @mileage_fast.setter
    def mileage_fast(self, value):
        self._mileage_fast = value

    @property
    def mileage_ratio(self):
        """The ratio of the mileages of the high and low pass-filtered ACE signal."""
        return self._mileage_ratio

    @mileage_ratio.setter
    def mileage_ratio(self, value):
        self._mileage_ratio = value

    @property
    def fraction_reg_up(self):
        """The fraction of regulation up reserve capacity actually employed."""
        return self._fraction_reg_up

    @fraction_reg_up.setter
    def fraction_reg_up(self, value):
        self._fraction_reg_up = value

    @property
    def fraction_reg_down(self):
        """The fraction of regulation down reserve capacity actually employed."""
        return self._fraction_reg_down

    @fraction_reg_down.setter
    def fraction_reg_down(self, value):
        self._fraction_reg_down = value

    @property
    def solver(self):
        """The name of the solver for Pyomo to use, defaults to 'glpk'."""
        return self._solver

    @solver.setter
    def solver(self, value):
        self._solver = value

    @property
    def expressions_block(self):
        """ExpressionsBlock object for setting model objectives and constraints."""
        return self._expressions_block

    @expressions_block.setter
    def expressions_block(self, value):
        self._expressions_block = value

    @property
    def market_type(self):
        """The name of the market formulation to be modeled, defaults to 'arbitrage'."""
        return self._market_type

    @market_type.setter
    def market_type(self, value):
        if isinstance(value, str):
            self._market_type = value
        else:
            raise TypeError('market_type property must be of type str.')

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

    @property
    def gross_revenue(self):
        """The net revenue generated over the time period as solved for in the optimization."""
        return self._gross_revenue

    @gross_revenue.setter
    def gross_revenue(self, value):
        self._gross_revenue = value

    def _set_model_param(self):
        """Sets the model params for the Pyomo ConcreteModel."""
        m = self.model

        # Check if params common to all formulations are set.
        if not hasattr(m, 'Power_rating'):
            # Power rating; equivalently, the maximum energy charged in one hour [MW].
            logging.debug('ValuationOptimizer: No Power_rating provided, setting default...')
            m.Power_rating = 20

        if not hasattr(m, 'R'):
            # Discount/interest rate [hour^(-1)].
            logging.debug('ValuationOptimizer: No R provided, setting default...')
            m.R = 0

        if not hasattr(m, 'Energy_capacity'):
            # Energy capacity [MWh].
            logging.debug('ValuationOptimizer: No Energy_capacity provided, setting default...')
            m.Energy_capacity = 5

        if not hasattr(m, 'Self_discharge_efficiency'):
            # Fraction of energy maintained over one time period.
            logging.debug('ValuationOptimizer: No Self_discharge_efficiency provided, setting default...')
            m.Self_discharge_efficiency = 1.00
        elif getattr(m, 'Self_discharge_efficiency') > 1.0:
            logging.warning('ValuationOptimizer: Self_discharge_efficiency provided is greater than 1.0, interpreting as percentage...')
            m.Self_discharge_efficiency = m.Self_discharge_efficiency/100

        if not hasattr(m, 'Round_trip_efficiency'):
            # Fraction of input energy that gets stored over one time period.
            logging.debug('ValuationOptimizer: No Round_trip_efficiency provided, setting default...')
            m.Round_trip_efficiency = 0.85
        elif getattr(m, 'Round_trip_efficiency') > 1.0:
            logging.warning('ValuationOptimizer: Round_trip_efficiency provided is greater than 1.0, interpreting as percentage...')
            m.Round_trip_efficiency = m.Round_trip_efficiency/100

        if not hasattr(m, 'Reserve_reg_min'):
            # Fraction of q_reg bid to increase state of charge minimum by.
            logging.debug('ValuationOptimizer: No Reserve_reg_min provided, setting default...')
            m.Reserve_reg_min = 0
        elif getattr(m, 'Reserve_reg_min') > 1.0:
            logging.warning('ValuationOptimizer: Reserve_reg_min provided is greater than 1.0, interpreting as percentage...')
            m.Reserve_reg_min = m.Reserve_reg_min/100

        if not hasattr(m, 'Reserve_reg_max'):
            # Fraction of q_reg bid to decrease state of charge maximum by.
            logging.debug('ValuationOptimizer: No Reserve_reg_max provided, setting default...')
            m.Reserve_reg_max = 0
        elif getattr(m, 'Reserve_reg_max') > 1.0:
            logging.warning('ValuationOptimizer: Reserve_reg_max provided is greater than 1.0, interpreting as percentage...')
            m.Reserve_reg_max = m.Reserve_reg_max/100

        if not hasattr(m, 'Reserve_charge_min'):
            # Fraction of energy capacity to increase state of charge minimum by.
            logging.debug('ValuationOptimizer: No Reserve_charge_min provided, setting default...')
            m.Reserve_charge_min = 0
        elif getattr(m, 'Reserve_charge_min') > 1.0:
            logging.warning('ValuationOptimizer: Reserve_charge_min provided is greater than 1.0, interpreting as percentage...')
            m.Reserve_charge_min = m.Reserve_charge_min/100

        if not hasattr(m, 'Reserve_charge_max'):
            # Fraction of energy capacity to decrease state of charge maximum by.
            logging.debug('ValuationOptimizer: No Reserve_charge_max provided, setting default...')
            m.Reserve_charge_max = 0
        elif getattr(m, 'Reserve_charge_max') > 1.0:
            logging.warning('ValuationOptimizer: Reserve_charge_max provided is greater than 1.0, interpreting as percentage...')
            m.Reserve_charge_max = m.Reserve_charge_max/100
        
        if not hasattr(m, 'State_of_charge_init'):
            # Initial state of charge [MWh], defaults to the amount reserved for discharging.
            logging.debug('ValuationOptimizer: No State_of_charge_init provided, setting default...')
            m.State_of_charge_init = m.Reserve_charge_min*m.Energy_capacity

        # Check if params necessary for certain formulations are set if required.
        if self.market_type in {'ercot_arbreg', 'pjm_pfp', 'miso_pfp', 'isone_pfp'}:
            try:
                if not getattr(m, 'fraction_reg_up', None):
                    logging.debug('ValuationOptimizer: No fraction_reg_up provided, setting default...')
                    m.fraction_reg_up = 0.25
            except ValueError:  # fraction_reg_up is array-like
                if np.isnan(m.fraction_reg_up).any():
                    logging.debug('ValuationOptimizer: fraction_reg_up array-like provided has None values, setting default...')
                    m.fraction_reg_up = 0.25

            try:
                if not getattr(m, 'fraction_reg_down', None):
                    logging.debug('ValuationOptimizer: No fraction_reg_down provided, setting default...')
                    m.fraction_reg_down = 0.25
            except ValueError:  # fraction_reg_down is array-like
                if np.isnan(m.fraction_reg_down).any():
                    logging.debug('ValuationOptimizer: fraction_reg_down array-like provided has None values, setting default...')
                    m.fraction_reg_down = 0.25

            # Converts fraction_reg_up and fraction_reg_down to arrays.
            try:
                m.fraction_reg_up[len(m.price_electricity) - 1]
            except TypeError:
                m.fraction_reg_up = np.array([m.fraction_reg_up] * len(m.price_electricity))

            try:
                m.fraction_reg_down[len(m.price_electricity) - 1]
            except TypeError:
                m.fraction_reg_down = np.array([m.fraction_reg_down] * len(m.price_electricity))

        if self.market_type in {'pjm_pfp', 'miso_pfp'}:
            if not hasattr(m, 'Perf_score'):
                # Performance score for pay-for-performance models.
                m.Perf_score = 0.95

        if self.market_type in {'miso_pfp'}:
            if not hasattr(m, 'Make_whole'):
                # Adjusts the credit for providing regulation services in MISO.
                m.Make_whole = 0.03

    def _set_model_var(self):
        """Sets the model vars for the Pyomo ConcreteModel."""
        m = self.model

        if not hasattr(m, 's'):
            def _s_init(_m, t):
                """The energy storage device's state of charge [MWh]."""
                return 0.0

            m.s = Var(m.soc_time, initialize=_s_init, within=NonNegativeReals)

        if not hasattr(m, 'q_r'):
            def _q_r_init(_m, t):
                """The quantity of energy allocated for charging via energy arbitrage [MWh]."""
                return 0.0

            m.q_r = Var(m.time, initialize=_q_r_init, within=NonNegativeReals)

        if not hasattr(m, 'q_d'):
            def _q_d_init(_m, t):
                """The quantity of energy allocated for discharging via energy arbitrage [MWh]."""
                return 0.0

            m.q_d = Var(m.time, initialize=_q_d_init, within=NonNegativeReals)

        if not hasattr(m, 'q_ru'):
            def _q_ru_init(_m, t):
                """The quantity of energy offered into the regulation up market [MWh]."""
                return 0.0

            m.q_ru = Var(m.time, initialize=_q_ru_init, within=NonNegativeReals)

        if not hasattr(m, 'q_rd'):
            def _q_rd_init(_m, t):
                """The quantity of energy offered into the regulation down market [MWh]."""
                return 0.0

            m.q_rd = Var(m.time, initialize=_q_rd_init, within=NonNegativeReals)

        if not hasattr(m, 'q_reg'):
            def _q_reg_init(_m, t):
                """The quantity of energy offered into the regulation market [MWh]. For single product frequency regulation markets."""
                return 0.0

            m.q_reg = Var(m.time, initialize=_q_reg_init, within=NonNegativeReals)

    def instantiate_model(self):
        """Instantiates the Pyomo ConcreteModel and populates it with supplied time series data."""
        if not hasattr(self, 'model'):
            self.model = ConcreteModel()

        m = self.model

        try:
            m.time = RangeSet(0, len(self.price_electricity) - 1)
            m.soc_time = RangeSet(0, len(self.price_electricity))
        except TypeError:
            # self.price_electricity is of type 'NoneType'
            m.time = []
            m.soc_time = []

        m.price_electricity = self.price_electricity
        m.ru = self.price_reg_up
        m.rd = self.price_reg_down

        m.rmccp = self.price_reg_capacity
        m.rmpcp = self.price_reg_performance

        m.regMCP = self.price_reg_performance

        m.cost_charge = self.cost_charge
        m.cost_discharge = self.cost_discharge

        m.mi_ratio = self.mileage_ratio
        m.reg_a = self.mileage_slow
        m.reg_d = self.mileage_fast

        # If fraction_reg_up/fraction_reg_down are provided to the instance, set them in the ConcreteModel.
        if self.fraction_reg_up is not None:
            m.fraction_reg_up = self.fraction_reg_up
        if self.fraction_reg_down is not None:
            m.fraction_reg_down = self.fraction_reg_down

    def populate_model(self):
        """Populates the Pyomo ConcreteModel based on the specified market_type."""
        self.model.objective_expr = NumericConstant(0.0)

        self._set_model_param()
        self._set_model_var()

        self.expressions_block = ExpressionsBlock(self.market_type)

        try:
            self.expressions_block.set_expressions(self.model)
        except IndexError:
            # Array-like object(s) do(es) not match the length of the price_electricity array-like.
            raise(IncompatibleDataException('At least one of the array-like parameter objects is not the expected length. (It should match the length of the price_electricity object.)'))
        else:
            self.model.objective = Objective(expr=self.model.objective_expr, sense=maximize)

    def _process_results(self):
        """Processes optimization results for further evaluation."""
        m = self.model

        t = m.time
        q_r = [m.q_r[n].value for n in m.time]
        q_d = [m.q_d[n].value for n in m.time]
        q_ru = [m.q_ru[n].value for n in m.time]
        q_rd = [m.q_rd[n].value for n in m.time]
        q_reg = [m.q_reg[n].value for n in m.time]
        soc = [m.s[n].value for n in m.time]
        price_electricity = [m.price_electricity[n] for n in m.time]

        run_results = {'time': t, 'q_r': q_r, 'q_d': q_d, 'q_ru': q_ru, 'q_rd': q_rd, 'q_reg': q_reg,
                       'state of charge': soc, 'price of electricity': price_electricity}

        if self.market_type == 'pjm_pfp':
            rev_arb = np.cumsum(np.array([m.price_electricity[t]*(m.q_d[t].value - m.q_r[t].value) for t in m.time]))
            rev_reg = np.cumsum(np.array([m.q_reg[t].value*m.Perf_score*(m.mi_ratio[t]*m.rmpcp[t] + m.rmccp[t]) for t in m.time]))

            revenue = rev_arb + rev_reg

            run_results['rev_arb'] = rev_arb
            run_results['rev_reg'] = rev_reg
            run_results['revenue'] = revenue
        elif self.market_type == 'miso_pfp':
            rev_arb = np.cumsum(np.array([m.price_electricity[t]*(m.q_d[t].value - m.q_r[t].value) for t in m.time]))
            rev_reg = np.cumsum(np.array([(1 + m.Make_whole)*m.Perf_score*m.regMCP[t]*m.q_reg[t].value for t in m.time]))

            revenue = rev_arb + rev_reg

            run_results['rev_arb'] = rev_arb
            run_results['rev_reg'] = rev_reg
            run_results['revenue'] = revenue
        elif self.market_type == 'isone_pfp':
            # copied from PJM and adjusted according to the Sterling code -FW
            # DOUBLE CHECK THE EQUATION WITH RAY -The Eqn of the Sterling code DOES NOT match the info available
            # online for the ISO-NE market...

            rev_arb = np.cumsum(np.array([m.price_electricity[t]*(m.q_d[t].value - m.q_r[t].value) for t in m.time]))
            rev_reg = np.cumsum(np.array([m.rmccp[t]*m.q_reg[t].value for t in m.time]))

            revenue = rev_arb + rev_reg

            run_results['rev_arb'] = rev_arb
            run_results['rev_reg'] = rev_reg
            run_results['revenue'] = revenue
        elif self.market_type == 'ercot_arbreg':
            rev_arb = np.cumsum(np.array([m.price_electricity[t]*(m.q_d[t].value - m.q_r[t].value
                                                                  + m.q_ru[t].value*m.fraction_reg_up[t]
                                                                  - m.q_rd[t].value*m.fraction_reg_down[t])
                                          for t in m.time]))
            rev_reg = np.cumsum(np.array([m.ru[t]*m.q_ru[t].value + m.rd[t]*m.q_rd[t].value for t in m.time]))

            revenue = rev_arb + rev_reg

            run_results['rev_arb'] = rev_arb
            run_results['rev_reg'] = rev_reg
            run_results['revenue'] = revenue
        else:
            rev_arb = np.cumsum(np.array([m.price_electricity[t] * (m.q_d[t].value - m.q_r[t].value)
                                          for t in m.time]))
            rev_reg = np.cumsum(np.array([0 for t in m.time]))

            revenue = rev_arb + rev_reg

            run_results['rev_arb'] = rev_arb
            run_results['rev_reg'] = rev_reg
            run_results['revenue'] = revenue

        try:
            self.gross_revenue = revenue[-1]
        except IndexError:
            # Revenue is of length-0, likely due to no price_electricity array-like being given before solving.
            self.gross_revenue = 0
        
        self.results = pd.DataFrame(run_results)

    def get_results(self):
        """Returns the decision variables and derived quantities in a DataFrame, plus the net revenue."""
        return self.results, self.gross_revenue


class BadParameterException(Exception):
    pass


class IncompatibleDataException(Exception):
    pass


if __name__ == '__main__':
    with open('valuation_optimizer.log', 'w'):
        pass

    logging.basicConfig(filename='valuation_optimizer.log', format='[%(levelname)s] %(asctime)s: %(message)s',
                        level=logging.INFO)