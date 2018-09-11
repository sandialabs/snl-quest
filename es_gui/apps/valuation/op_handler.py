from __future__ import absolute_import

import logging
from datetime import datetime
import calendar
import pyutilib

from kivy.clock import mainthread

from es_gui.tools.valuation.valuation_optimizer import ValuationOptimizer, BadParameterException, IncompatibleDataException


class ValuationOptimizerHandler:
    """A handler for creating and solving ValuationOptimizer instances as requested."""
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

    def process_requests(self, requests, *args):
        """Generates and solves ValuationOptimizer models based on the given requests."""
        dms = self.dms

        iso = requests['iso']
        market_type = requests['market type']
        node_id = str(requests['node id'])
        node_name = self.dms.get_node_name(node_id, iso)
        param_set = requests.get('param set', [None])

        solved_requests = []

        handler_status = True  # Set to False if any exceptions raised when building or solving ValuationOptimizer model(s).

        for month, year in requests['months']:
            param_set_iterator = iter(param_set)
            continue_param_loop = True

            while continue_param_loop:
                try:
                    params = next(param_set_iterator)
                except StopIteration:
                    break

                op = ValuationOptimizer(market_type=market_type)

                if iso == 'PJM':
                    #lmp_da, RUP, RDW, MR, RA, RD, RegCCP, RegPCP = dms.get_pjm_data(year, month, node_name)
                    lmp_da, MR, RA, RD, RegCCP, RegPCP = dms.get_pjm_data(year, month, node_id)

                    op.price_electricity = lmp_da
                    op.mileage_ratio = MR
                    op.mileage_slow = RA
                    op.mileage_fast = RD
                    op.price_reg_capacity = RegCCP
                    op.price_reg_performance = RegPCP
                    #op.fraction_reg_up = RUP
                    #op.fraction_reg_down = RDW
                elif iso == 'ERCOT':
                    lmp_da, rd, ru = dms.get_ercot_data(year, month, node_name)

                    op.price_electricity = lmp_da
                    op.price_reg_up = ru
                    op.price_reg_down = rd
                elif iso == 'MISO':
                    lmp_da, regMCP = dms.get_miso_data(year, month, node_name)

                    op.price_electricity = lmp_da
                    op.price_reg_performance = regMCP
                elif iso == 'ISO-NE':
                    daLMP, RegCCP, RegPCP = dms.get_isone_data(year, month, node_id)

                    op.price_electricity = daLMP
                    op.price_reg_capacity = RegCCP
                    op.price_reg_performance = RegPCP
                else:
                    logging.error('ValOp Handler: Invalid ISO provided.')
                    raise ValueError('Invalid ISO provided to ValuationOptimizer handler.')

                if params:
                    op.set_model_parameters(**params)
                else:
                    continue_param_loop = False

                try:
                    solved_op = self._solve_model(op)
                except pyutilib.common._exceptions.ApplicationError as e:
                    logging.error('ValOp Handler: Something went wrong when solving: ({error})'.format(error=e))
                    handler_status = False
                except IncompatibleDataException as e:
                    logging.error(e)
                    handler_status = False
                else:
                    solved_op = self._save_to_solved_ops(solved_op, iso, market_type, node_name,
                                                        year, month, params)
                    solved_requests.append(solved_op)

        logging.info('ValOp Handler: Finished processing requested jobs.')
        return solved_requests, handler_status

    def _solve_model(self, op):
        op.solver = self.solver_name
        op.run()

        return op

    @staticmethod
    def _save_to_solved_ops(op, iso, market_type, node_name, year, month, param_set):
        # time_finished = datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')
        time_finished = datetime.now().strftime('%b %d, %Y %H:%M:%S')
        name = ' | '.join([time_finished, node_name, year, calendar.month_abbr[int(month)], repr(param_set)])

        results_dict = {}

        results_dict['name'] = name
        results_dict['optimizer'] = op
        results_dict['iso'] = iso
        results_dict['market type'] = market_type
        results_dict['year'] = year
        results_dict['month'] = calendar.month_name[int(month)]
        results_dict['node'] = node_name
        if param_set:
            results_dict['params'] = param_set
        results_dict['time'] = time_finished
        results_dict['label'] = ' '.join([node_name, year, calendar.month_abbr[int(month)], repr(param_set)])

        ValuationOptimizerHandler.solved_ops.append(results_dict)

        return (name, op)

if __name__ == '__main__':
    with open('valuation_optimizer.log', 'w'):
        pass

    logging.basicConfig(filename='valuation_optimizer.log', format='[%(levelname)s] %(asctime)s: %(message)s',
                        level=logging.INFO)
    
    op = ValuationOptimizer()

    fpath = os.path.join('data', 'PJM')
    year = 2015
    month = 3
    nodeid = '51217'

    daLMP, mr, rega, regd, RegCCP, RegPCP = read_pjm_data(fpath,year,month,nodeid)

    handler_requests = {}
    handler_requests['iso'] = 'PJM'
    handler_requests['market type'] = 'pjm_pfp'
    handler_requests['months'] = [(month, year),]
    handler_requests['node id'] = nodeid


    results, gross_revenue = op.run()
