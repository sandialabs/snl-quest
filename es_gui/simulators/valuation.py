"""
Objects for simulations of revenue generation from value stacking in ISO/RTO electricity markets.

This module provides simulator classes performing simulations based on the ValuationOptimizer class.

Classes
-------
- `ValuationOptimizerSimulator` -- simulations using the ValuationOptimizer class model.

"""

import copy

import pandas as pd

from es_gui.simulators.forecasting import persistent_forecast
from es_gui.simulators.utils import Simulator
from es_gui.tools.valuation.valuation_optimizer import ValuationOptimizer


class ValuationOptimizerSimulator(Simulator):
    """A class for performing simulations based on ValuationOptimizer objects.

    The ValuationOptimizerSimulator class has simulation (run) modes based on
    ValuationOptimizer objects.

    """
    def __init__(self, **kwargs):
        super(ValuationOptimizerSimulator, self).__init__(**kwargs)

        self._optimizer = ValuationOptimizer

        self._gross_revenue = 0
    
    @property
    def gross_revenue(self):
        """The gross revenue of the simulation performed.
        """
        return self._gross_revenue
    
    @gross_revenue.setter
    def gross_revenue(self, value):
        self._gross_revenue = value

    def run(self, properties, data, simulation_type, 
            parameters=None, n_days=None, forecast_method=None, **kwargs
            ):
        """Sets up and runs all ValuationOptimizer instances as prescribed 
        by the simulation mode.

        Parameters
        ----------        
        simulation_type : {'monthly_perfect', 'monthly_forecast',
        'daily_perfect', 'daily_forecast'}
            Name of the simulation mode to be performed. 
        
        Other Parameters
        ----------------
        n_days : int
            The number of days in the month that `data` is from.
        
        forecast_method : {'persistent',}
            The method used to create forecasts from `data`. This is
            ignored if `simulation_type` does not use forecasting.
        
        Raises
        ------
        ValueError
            If `forecast_method` is not a valid choice.
            If `simulation_type` is not a valid choice.
            If `n_days` is not given and a "daily"-type simulation mode
                is specified.
        
        Notes
        -----
        Simulation mode descriptions

        monthly_perfect - The time horizon of the optimization is one
            month and the system has perfect foresight.
        
        monthly_forecast - The time horizon of the optimization is one
            month and the system uses forecasted data based on `data`
            for the optimization. The objective function is recomputed
            with the actuals `data`.
        
        daily_perfect - The month of data is spliced into 24-hour
            segments and a new optimization problem is formulated for
            each day in the month. The results are combined afterwards.
            The system has perfect foresight.
        
        daily_forecast - The month of data is spliced into 24-hour
            segments and a new optimization problem is formulated for
            each day in the month. The results are combined afterwards.
            The system uses forecasted data based on `data` for the
            optimization and the objective function is recomputed with
            the actuals `data`.

        Examples
        --------
        >>> props = {'market_type': 'arbitrage', 'solver': 'gurobi'}

        >>> data = {'price_electricity': lmp_da}

        >>> model_params = {'Energy_capacity': 32, 'Power_rating': 8}

        >>> sim = ValuationOptimizerSimulator()

        >>> sim.run(properties=props, data=data, simulation_type='monthly_forecast', 
                    parameters=model_params, n_days=31, forecast_method='persistent')
        """
        super(ValuationOptimizerSimulator, self).run(properties, data, simulation_type, model_parameters, **kwargs)

        data = copy.deepcopy(data)

        if simulation_type == 'monthly_perfect':
            op = self.optimizer()

            # Assign properties to Optimizer object
            if properties:
                op = self.set_optimizer_properties(op, **properties)

            # Process data as needed then assign to Optimizer object
            op = self.set_optimizer_properties(op, **data)

            # Assign Pyomo model parameters
            if parameters:
                op.set_model_parameters(**parameters)

            op.run()
            self.solved_ops.append(op)
        elif simulation_type == 'monthly_forecast':
            op = self.optimizer()

            # Assign properties to Optimizer object
            if properties:
                op = self.set_optimizer_properties(op, **properties)

            # Process data as needed then assign to Optimizer object
            if not forecast_method:
                forecast_method = 'persistent'
            
            if forecast_method == 'persistent':
                forecasted_data = {k: persistent_forecast(v) for (k, v) in data.items()}
            else:
                raise ValueError(
            "The provided forecast_method could not be recognized. (got '{0}')".format(forecast_method)
            )

            op = self.set_optimizer_properties(op, **forecasted_data)

            # Assign Pyomo model parameters
            if parameters:
                op.set_model_parameters(**parameters)

            op.run()

            # Reevaluate using "actuals" data
            op.reprocess_results(**data)
            self.solved_ops.append(op)
        elif simulation_type == 'daily_perfect':
            N_HRS = 24

            if not n_days:
                raise ValueError(
                    "The number of days in the simulation must be specified for a 'daily' simulation type by using the 'n_days' keyword argument."
                    )
            else:
                for ix in range(n_days):
                    op = self.optimizer()

                    # Assign properties to Optimizer object
                    if properties:
                        op = self.set_optimizer_properties(op, **properties)

                    # Process data as needed then assign to Optimizer object
                    daily_data = {}

                    for (attr_name, data_array) in data.items():
                        # Pop the first N_HRS of data
                        daily_data[attr_name] = data_array[:N_HRS]
                        data[attr_name] = data_array[N_HRS:]

                    op = self.set_optimizer_properties(op, **daily_data)

                    # Assign Pyomo model parameters
                    if parameters:
                        op.set_model_parameters(**parameters)

                    op.run()

                    # Add to Simulation's solved objects
                    self.solved_ops.append(op)
        elif simulation_type == 'daily_forecast':
            N_HRS = 24

            if not n_days:
                raise ValueError(
                    "The number of days in the simulation must be specified for a 'daily' simulation type by using the 'n_days' keyword argument."
                    )
            else:
                if not forecast_method:
                    forecast_method = 'persistent'
                
                if forecast_method == 'persistent':
                    forecasted_data = {k: persistent_forecast(v) for (k, v) in data.items()}
                else:
                    raise ValueError(
                "The provided forecast_method could not be recognized. (got '{0}')".format(forecast_method)
                )

                for ix in range(n_days):
                    op = self.optimizer()

                    # Assign properties to Optimizer object
                    if properties:
                        op = self.set_optimizer_properties(op, **properties)

                    # Process data as needed then assign to Optimizer object
                    daily_data = {}
                    daily_forecasted_data = {}

                    for (attr_name, data_array) in forecasted_data.items():
                        # Pop the first N_HRS of forecasted
                        daily_forecasted_data[attr_name] = data_array[:N_HRS]
                        forecasted_data[attr_name] = data_array[N_HRS:]

                    for (attr_name, data_array) in data.items():
                        # Pop the first N_HRS of forecasted
                        daily_data[attr_name] = data_array[:N_HRS]
                        data[attr_name] = data_array[N_HRS:]

                    op = self.set_optimizer_properties(op, **daily_forecasted_data)

                    # Assign Pyomo model parameters
                    if parameters:
                        op.set_model_parameters(**parameters)

                    op.run()

                    # Reevaluate using "actuals" data
                    op.reprocess_results(**daily_data)
                    self.solved_ops.append(op)
        else:
            raise ValueError(
            "The provided simulation_type could not be recognized. (got '{0}')".format(simulation_type)
            )

        # Process simulation's results
        self._process_results(simulation_type=simulation_type)
    
    def _process_results(self, simulation_type):
        if simulation_type in ['monthly_perfect', 'monthly_forecast',]:
            self.gross_revenue = sum(op.gross_revenue for op in self.solved_ops)
            self.results = pd.concat([op.results for op in self.solved_ops])
        elif simulation_type in ['daily_perfect', 'daily_forecast',]:
            self.gross_revenue = sum(op.gross_revenue for op in self.solved_ops)

            # Need to adjust the cumulative revenue calculations s.t. they are cumulative with previous days.
            cumulative_field_names = ['rev_arb', 'rev_reg', 'revenue',]

            for ix, op in enumerate(self.solved_ops, start=0):
                if ix > 0:
                    for field_name in cumulative_field_names:
                        previous_day_final_value = self.solved_ops[ix - 1].results[field_name].tail(1).values

                        op.results[field_name] += previous_day_final_value

            self.results = pd.concat([op.results for op in self.solved_ops])
            self.results.reset_index(drop=True, inplace=True)
