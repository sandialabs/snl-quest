from __future__ import absolute_import

import logging
from datetime import datetime
import calendar
import pyutilib
import numpy as np
import json

from kivy.clock import mainthread

from es_gui.tools.equity.equity_optimizer import EquityOptimizer, BadParameterException, IncompatibleDataException

class EquityOptimizerHandler:# create a spesific function for peaker palnt replacement 
    """A handler for creating and solving Equity Optimizer instances as requested."""
    dms = None
    solved_ops = []

    def __init__(self, solver_name='glpk'):
        self.solver_name = solver_name 
    

    def process_requests(self, op_handler_requests, *args):
        """Generates and solves PeakerRepOptimizer models based on the given requests.""" 
        dms = self.dms

        plant_data_path = op_handler_requests['plant_data']
        #pv_profile_path = op_handler_requests['pv_profile']
        params = op_handler_requests['params'][0]

        handler_status = set()
        #hourly_plant_dispatch_schedule = plant_data_path['HourLoad']
        # The problem will be solved K times in order to determin the battery/pv that will replace diferent perportions of the power plant dispatch

        replacement_fractions = params['replacement_fractions']

        solved_requests = []
        for rp in replacement_fractions:
            op = EquityOptimizer(solver=self.solver_name)
            op.path = plant_data_path['path']
            # Get data.
            with open(plant_data_path['path']) as f:
                plant_dispatch_json = json.load(f)
                plant_dispatch = plant_dispatch_json['plant_dispatch']
                pv_profile = plant_dispatch_json['pv']
                op.PM25_emissions = plant_dispatch_json['PM25_emissions']
                op.NOx_emissions = plant_dispatch_json['NOx_emissions']
                op.SO2_emissions = plant_dispatch_json['SO2_emissions']
                op.CO2_emissions = plant_dispatch_json['CO2_emissions']
                op.Pollution_Low_Value = plant_dispatch_json['COBRA_results']['Summary']['TotalHealthBenefitsValue_low']
                op.Pollution_High_Value = plant_dispatch_json['COBRA_results']['Summary']['TotalHealthBenefitsValue_high']
                op.Pollution_Low_Mortality = plant_dispatch_json['COBRA_results']['Summary']['Mortality_All_Cause__low_']
                op.Pollution_High_Mortality = plant_dispatch_json['COBRA_results']['Summary']['Mortality_All_Cause__high_']
                op.total_population = plant_dispatch_json['health_impact_equity']['total_population']
                op.total_disadvantaged_population = plant_dispatch_json['health_impact_equity']['total_disadvantaged_population']
                op.total_low_income_population = plant_dispatch_json['health_impact_equity']['total_low_income_population']
                op.disadvantaged_population_fraction = plant_dispatch_json['health_impact_equity']['disadvantaged_population_fraction']
                op.low_income_population_fraction = plant_dispatch_json['health_impact_equity']['low_income_population_fraction']
                op.total_impact_on_disadvantaged_population_low = plant_dispatch_json['health_impact_equity']['total_impact_on_disadvantaged_population_low']
                op.total_impact_on_disadvantaged_population_high = plant_dispatch_json['health_impact_equity']['total_impact_on_disadvantaged_population_high']
                op.total_impact_on_low_income_population_low = plant_dispatch_json['health_impact_equity']['total_impact_on_low_income_population_low']
                op.total_impact_on_low_income_population_high = plant_dispatch_json['health_impact_equity']['total_impact_on_low_income_population_high']
                op.impact_on_disadvantaged_population_fraction = plant_dispatch_json['health_impact_equity']['impact_on_disadvantaged_population_fraction']
                op.impact_on_low_income_population_fraction = plant_dispatch_json['health_impact_equity']['impact_on_low_income_population_fraction']

                
            op.params_metadata = params
            op.plant_metadata = plant_data_path

            # Populate op.
            op.discount_rate               = float(params['discount_rate'])/100.0
            op.cost_per_ton_of_CO2         = float(params['cost_per_ton_of_CO2'])
            op.cost_per_MW_PV_system       = float(params['cost_per_MW_PV_system'])
            op.fixed_cost_of_PV_system     = float(params['fixed_cost_of_PV_system'])
            op.cost_per_MW_BESS            = float(params['cost_per_MW_BESS'])
            op.cost_per_MWh_BESS           = float(params['cost_per_MWh_BESS'])
            op.fixed_cost_of_the_BESS      = float(params['fixed_cost_of_the_BESS'])
            op.energy_efficiency           = float(params['bess_round_trip_efficiency'])/100.0


            
            # if one profile is taken from a leap year and the other is not, they will have diferent lengths 
            # this selects the shortest profile length to use
            op.n = min(len(plant_dispatch), len(pv_profile)) 
            op.time = range(op.n)
            op.soe_time = range(op.n+1)

            op.plant_dispatch = [plant_dispatch[i] for i in op.time]
            op.pv_profile = pv_profile 

        
            op.replacement_fraction = rp
            try:
                solved_op = self._solve_model(op)

            except pyutilib.common._exceptions.ApplicationError as e:
                logging.error('Op Handler: {error}'.format(error=e))

                if 'No executable found' in e.args[0]:
                    # Could not locate solver executable
                    handler_status.add('* The executable for the selected solver could not be found; please check your installation.')
                else:
                    handler_status.add('* The problem may be infeasible.')
            except IncompatibleDataException as e:
                # Data exception raised by BtmOptimizer
                logging.error(e)
                handler_status.add('* The time series data has mismatched sizes.')
            except AssertionError as e:
                # An optimal solution could not be found as reported by the solver
                logging.error('Op Handler: {error}'.format(error=e))
                handler_status.add('* An optimal solution could not be found; the problem may be infeasible.')
            else:
                logging.info('Op Handler: Finished calculating')
                solved_op = self._save_to_solved_ops(solved_op,rp)
                solved_requests.append(solved_op)        

        logging.info('Op Handler: Finished processing requested jobs.')
        return solved_requests, handler_status
        

    def _solve_model(self, op):
        
        op.run()

        return op

    @staticmethod      
    def _save_to_solved_ops(op,rp):
        # time_finished = datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')
        time_finished = datetime.now().strftime('%b %d, %Y %H:%M:%S')

        name_components = [time_finished,]

        # Check for peaker name.
        #print(op.plant_metadata)
        #print(op.params_metadata)
        powerplant_name = 'Powerplant Name: {0}'.format(op.plant_metadata['name'])
        name_components.append(powerplant_name)

        replacement_fraction_name = ' | Replacement Fraction: {0}'.format(op.replacement_fraction)
        name_components.append(replacement_fraction_name)

        name = ' | '.join(name_components)

        results_dict = {}

        results_dict['name'] = name
        results_dict['optimizer'] = op
        results_dict['time'] = time_finished
        results_dict['run_medidata'] = {'path': op.path, 
                        'replacement_fraction'        : op.replacement_fraction,
                        'energy_capacity'             : op.energy_capacity,
                        'power_capacity'              : op.power_capacity,
                        'pv_capacity'                 : op.pv_capacity,
                        'discount_rate'               : op.discount_rate,
                        'cost_per_ton_of_CO2'         : op.cost_per_ton_of_CO2 ,
                        'cost_per_MW_PV_system'       : op.cost_per_MW_PV_system,
                        'fixed_cost_of_PV_system'     : op.fixed_cost_of_PV_system,
                        'cost_per_MW_BESS'            : op.cost_per_MW_BESS ,
                        'cost_per_MWh_BESS'           : op.cost_per_MWh_BESS,
                        'fixed_cost_of_the_BESS'      : op.fixed_cost_of_the_BESS }

        EquityOptimizerHandler.solved_ops.append(results_dict)

        return (name, op)
    
    def get_solved_ops(self):
        """Returns the list of solved Optimizer objects in reverse chronological order."""
        return_list = reversed(self.solved_ops)

        return return_list
    
