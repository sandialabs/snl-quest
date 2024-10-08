from quest.snl_libraries.workspace.nodes.pynodes import python_node, data_node











from valuation.es_gui.tools.valuation.valuation_dms import ValuationDMS

from valuation.es_gui.apps.valuation.op_handler_workspace import ValuationOptimizerHandler



# Functions







def ess_parameters_function(power, energy, rte):
    params = {}
    params['Power_rating'] = power
    params['Energy_capacity'] = energy
    params['Round_trip_efficiency'] = rte
    params['Self_discharge_efficiency'] = 1
    params['R'] = 0
    params['Reserve_reg_min'] = 0
    params['Reserve_reg_max'] = 1
    params['State_of_charge_min'] = 0
    params['State_of_charge_max'] = 1
    params['State_of_charge_init'] = 0.5
    return {'ess_parameters': [params]}

def op_request_function(iso, node, market, month, ess):
    request = {}
    request['param set'] = ess
    request['iso'] = iso
    request['node id'] = node
    request['market type'] = market
    request['months'] = month
    return {'request': request}

def data_management_function(data_path):
    dms = ValuationDMS(max_memory=10000, save_data=True, save_name='valuation_dms.p', home_path=data_path)
    return {'dms': dms}
def valuation_function(request, solver_name, dms):
    handler = ValuationOptimizerHandler(solver_name=solver_name, dms=dms)
    handler.process_requests(request)
    op_results = handler.get_solved_ops()
    return {'optimization_results': op_results}


# Instantiations
node0x1c03353c790=data_node(node_name='Power Rating')
node0x1c02d9eeeb0=data_node(node_name='Energy Capacity')
node0x1c02da21070=data_node(node_name='Round Trip')
node0x1c02da21460=data_node(node_name='iso')
node0x1c02da21700=data_node(node_name='node')
node0x1c02da219d0=data_node(node_name='market')
node0x1c02da21ca0=data_node(node_name='months')
node0x1c02da21f70=python_node(node_name='ess_parameters',function=ess_parameters_function)
node0x1c02da38ac0=data_node(node_name='data_location 1')
node0x1c02da386d0=python_node(node_name='op_request',function=op_request_function)
node0x1c02da4ddf0=data_node(node_name='Solver')
node0x1c02da4d790=python_node(node_name='data_management',function=data_management_function)
node0x1c02da38280=python_node(node_name='valuation',function=valuation_function)


# Set inputs
node0x1c02da4ddf0.set_inputs(solver_name='glpk')
node0x1c02da21ca0.set_inputs(m=[("3","2018")])
node0x1c02da38ac0.set_inputs(data_path="data")
node0x1c02da21460.set_inputs(iso_name="PJM")
node0x1c02da219d0.set_inputs(market_type="pjm_pfp")
node0x1c03353c790.set_inputs(power=1)
node0x1c02d9eeeb0.set_inputs(energy=8)
node0x1c02da21070.set_inputs(rte=.85)
node0x1c02da21700.set_inputs(node_id=1)

# Connections
node0x1c03353c790.connect_to(to_node_list=[node0x1c02da21f70], mapping=[{'power': 'power'}])
node0x1c02d9eeeb0.connect_to(to_node_list=[node0x1c02da21f70], mapping=[{'energy': 'energy'}])
node0x1c02da21070.connect_to(to_node_list=[node0x1c02da21f70], mapping=[{'rte': 'rte'}])
node0x1c02da21460.connect_to(to_node_list=[node0x1c02da386d0], mapping=[{'iso_name': 'iso'}])
node0x1c02da21700.connect_to(to_node_list=[node0x1c02da386d0], mapping=[{'node_id': 'node'}])
node0x1c02da219d0.connect_to(to_node_list=[node0x1c02da386d0], mapping=[{'market_type': 'market'}])
node0x1c02da21ca0.connect_to(to_node_list=[node0x1c02da386d0], mapping=[{'m': 'month'}])
node0x1c02da38ac0.connect_to(to_node_list=[node0x1c02da4d790], mapping=[{'data_path': 'data_path'}])
node0x1c02da4ddf0.connect_to(to_node_list=[node0x1c02da38280], mapping=[{'solver_name': 'solver_name'}])
node0x1c02da21f70.connect_to(to_node_list=[node0x1c02da386d0], mapping=[{'ess_parameters': 'ess'}])
node0x1c02da4d790.connect_to(to_node_list=[node0x1c02da38280], mapping=[{'dms': 'dms'}])
node0x1c02da386d0.connect_to(to_node_list=[node0x1c02da38280], mapping=[{'request': 'request'}])

# Get Outputs
print('Solver_outputs:',node0x1c02da4ddf0.get_outputs())
print('months_outputs:',node0x1c02da21ca0.get_outputs())
print('data_location 1_outputs:',node0x1c02da38ac0.get_outputs())
print('iso_outputs:',node0x1c02da21460.get_outputs())
print('market_outputs:',node0x1c02da219d0.get_outputs())
print('Power Rating_outputs:',node0x1c03353c790.get_outputs())
print('Energy Capacity_outputs:',node0x1c02d9eeeb0.get_outputs())
print('Round Trip_outputs:',node0x1c02da21070.get_outputs())
print('node_outputs:',node0x1c02da21700.get_outputs())
print('ess_parameters_outputs:',node0x1c02da21f70.get_outputs())
print('data_management_outputs:',node0x1c02da4d790.get_outputs())
print('op_request_outputs:',node0x1c02da386d0.get_outputs())
print('valuation_outputs:',node0x1c02da38280.get_outputs())