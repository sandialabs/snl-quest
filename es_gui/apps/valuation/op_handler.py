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

        handler_status = set()

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
                    op.mileage_mult = MR
                    # op.mileage_slow = RA
                    # op.mileage_fast = RD
                    op.price_regulation = RegCCP
                    op.price_reg_service = RegPCP
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
                    # op.price_reg_service = regMCP
                    op.price_regulation = regMCP
                elif iso == 'ISONE':
                    daLMP, RegCCP, RegPCP, miMULT = dms.get_isone_data(year, month, node_id)

                    op.price_electricity = daLMP
                    op.price_regulation = RegCCP
                    op.price_reg_service = RegPCP
                    op.mileage_mult = miMULT
                ########################################################################################################
                elif iso == 'NYISO':
                    lbmp_da, rcap_da = dms.get_nyiso_data(year, month, node_id)

                    op.price_electricity = lbmp_da
                    op.price_regulation = rcap_da
                elif iso == 'SPP':
                    lmp_da, mcpru_da, mcprd_da = dms.get_spp_data(year, month, node_name)

                    op.price_electricity = lmp_da
                    op.price_reg_up = mcpru_da
                    op.price_reg_down = mcprd_da
                elif iso == 'CAISO':
                    lmp_da, aspru_da, asprd_da, asprmu_da, asprmd_da, rmu_mm, rmd_mm, rmu_pacc, rmd_pacc = dms.get_caiso_data(year, month, node_name)

                    op.price_electricity = lmp_da
                    op.price_reg_up = aspru_da
                    op.price_reg_down = asprd_da
                    op.price_reg_serv_up = asprmu_da
                    op.price_reg_serv_down = asprmd_da
                    op.mileage_mult_ru = rmu_mm
                    op.mileage_mult_rd = rmd_mm
                    op.perf_score_ru = rmu_pacc # TODO: give the option to the user to override this
                    op.perf_score_rd = rmd_pacc
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
                    logging.error('Op Handler: {error}'.format(error=e))

                    if 'No executable found' in e.args[0]:
                        # Could not locate solver executable
                        handler_status.add('* The executable for the selected solver could not be found; please check your installation.')
                    else:
                        handler_status.add('* ({0} {1}) {2}. The problem may be infeasible.'.format(month, year, e.args[0]))
                except IncompatibleDataException as e:
                    # Data exception raised by ValuationOptimizer
                    logging.error(e)
                    handler_status.add('* ({0} {1}) The time series data has mismatched sizes.'.format(month, year))
                except AssertionError as e:
                    # An optimal solution could not be found as reported by the solver
                    logging.error('Op Handler: {error}'.format(error=e))
                    handler_status.add('* ({0} {1}) An optimal solution could not be found; the problem may be infeasible.'.format(month, year))
                else:
                    solved_op = self._save_to_solved_ops(solved_op, iso, market_type, node_name,
                                                        year, month, params)
                    solved_requests.append(solved_op)

        logging.info('Op Handler: Finished processing requested jobs.')
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
    
    def get_solved_ops(self):
        """Returns the list of solved Optimizer objects in reverse chronological order."""
        return_list = reversed(self.solved_ops)

        return return_list

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
