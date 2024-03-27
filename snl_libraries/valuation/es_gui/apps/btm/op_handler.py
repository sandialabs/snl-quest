from __future__ import absolute_import

import logging
from datetime import datetime
import calendar
import pyutilib
import numpy as np

from kivy.clock import mainthread

from es_gui.tools.btm.btm_optimizer import BtmOptimizer, BadParameterException, IncompatibleDataException
import es_gui.tools.btm.readutdata as readutdata


class BtmOptimizerHandler:
    """A handler for creating and solving BtmOptimizer instances as requested."""
    dms = None
    solved_ops = []

    def __init__(self, solver_name):
        self._solver_name = solver_name

    @property
    def solver_name(self):
        """The name of the solver for Pyomo to call."""
        return self._solver_name

    @solver_name.setter
    def solver_name(self, value):
        self._solver_name = value

    def process_requests(self, op_handler_requests, *args):
        """Generates and solves BtmOptimizer models based on the given requests."""
        dms = self.dms

        rate_structure = op_handler_requests['rate_structure']
        load_profile_path = op_handler_requests['load_profile']
        pv_profile_path = op_handler_requests['pv_profile']
        param_set = op_handler_requests['params']

        solved_requests = []

        handler_status = set()

        year = 2019

        weekday_energy_schedule = rate_structure['energy rate structure']['weekday schedule']
        weekend_energy_schedule = rate_structure['energy rate structure']['weekend schedule']
        weekday_demand_schedule = rate_structure['demand rate structure']['weekday schedule']
        weekend_demand_schedule = rate_structure['demand rate structure']['weekend schedule']

        nem_type = 2 if rate_structure['net metering']['type'] else 1
        nem_rate = None if rate_structure['net metering']['type'] else rate_structure['net metering']['energy sell price']

        rate_df = readutdata.input_df(year, weekday_energy_schedule, weekend_energy_schedule, weekday_demand_schedule, weekend_demand_schedule)

        for ix, month in enumerate(calendar.month_abbr[1:], start=1):
            param_set_iterator = iter(param_set)
            continue_param_loop = True

            while continue_param_loop:
                try:
                    params = next(param_set_iterator)
                except StopIteration:
                    break

                op = BtmOptimizer()

                # Get data.
                # TODO: Move to a DMS. Should the omission of PV profile data be handled by the BtmOptimizer?
                load_profile = self.dms.get_load_profile_data(load_profile_path['path'], ix)

                try:
                    pv_profile = self.dms.get_pv_profile_data(pv_profile_path['path'], ix)
                except KeyError:
                    pv_profile = np.zeros(len(load_profile))

                # Build op inputs.
                rate_df_month = rate_df.loc[rate_df['month'] == ix]

                # Populate op.
                op.tou_energy_schedule = rate_df_month['tou_energy_schedule'].values
                op.tou_demand_schedule = rate_df_month['tou_demand_schedule'].values

                op.tou_energy_rate = [x[1] for x in rate_structure['energy rate structure']['energy rates'].items()]
                op.tou_demand_rate = [x[1] for x in rate_structure['demand rate structure']['time of use rates'].items()]
                op.flat_demand_rate = rate_structure['demand rate structure']['flat rates'][month]

                op.nem_type = nem_type
                op.nem_rate = nem_rate

                op.load_profile = load_profile
                op.pv_profile = pv_profile
                op.rate_structure_metadata = rate_structure
                op.load_profile_metadata = load_profile_path
                op.pv_profile_metadata = pv_profile_path

                if params:
                    op.set_model_parameters(**params)
                else:
                    continue_param_loop = False
                
                try:
                    solved_op = self._solve_model(op)
                except pyutilib.common._exceptions.ApplicationError as e:
                    logging.error('Op Handler: {error}'.format(error=e))

                    if 'No executable found' in e.args[0]:
                        # Could not locate solver executable
                        handler_status.add('* The executable for the selected solver could not be found; please check your installation.')
                    else:
                        handler_status.add('* ({0} {1}) {2}. The problem may be infeasible.'.format(month, year, e.args[0]))
                except IncompatibleDataException as e:
                    # Data exception raised by BtmOptimizer
                    logging.error(e)
                    handler_status.add('* ({0} {1}) The time series data has mismatched sizes.'.format(month, year))
                except AssertionError as e:
                    # An optimal solution could not be found as reported by the solver
                    logging.error('Op Handler: {error}'.format(error=e))
                    handler_status.add('* ({0} {1}) An optimal solution could not be found; the problem may be infeasible.'.format(month, year))
                else:
                    solved_op = self._save_to_solved_ops(solved_op, month, params)
                    solved_requests.append(solved_op)

        logging.info('Op Handler: Finished processing requested jobs.')
        return solved_requests, handler_status

    def _solve_model(self, op):
        op.solver = self.solver_name
        op.run()

        return op

    @staticmethod
    def _save_to_solved_ops(op, month, param_set):
        # time_finished = datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')
        time_finished = datetime.now().strftime('%b %d, %Y %H:%M:%S')

        name_components = [time_finished, month,]

        # Check for rate structure name.
        rate_structure_name = 'Rate: {0}'.format(op.rate_structure_metadata.get('name', ''))
        name_components.append(rate_structure_name)

        # Check for PV profile.
        if any(op.pv_profile != 0):
            if op.pv_profile_metadata:
                pv_profile_name = 'PV: {0}'.format(op.pv_profile_metadata.get('name', 'Not specified'))
            else:
                pv_profile_name = 'PV: Not specified'
            
            name_components.append(pv_profile_name)
        else:
            name_components.append('PV: None')
        
        # Load profile name.
        load_profile_name = 'Load: {0}'.format(op.load_profile_metadata.get('name', ''))
        name_components.append(load_profile_name)

        name = ' | '.join(name_components)

        results_dict = {}

        results_dict['name'] = name
        results_dict['optimizer'] = op
        results_dict['month'] = month
        if param_set:
            results_dict['params'] = param_set
        results_dict['time'] = time_finished
        results_dict['label'] = ' '.join([month, repr(param_set)])

        BtmOptimizerHandler.solved_ops.append(results_dict)

        return (name, op)
    
    def get_solved_ops(self):
        """Returns the list of solved Optimizer objects in reverse chronological order."""
        return_list = reversed(self.solved_ops)

        return return_list
    