from quest.snl_libraries.workspace.nodes.pynodes import python_node, data_node










from valuation.es_gui.apps.valuation.op_handler_workspace import ValuationOptimizerHandler
from valuation.es_gui.tools.valuation.valuation_dms import ValuationDMS



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

def valuation_function(request, solver_name):
    dms = ValuationDMS(max_memory=10000, save_data=True, save_name='valuation_dms.p', home_path='data')
    handler = ValuationOptimizerHandler(solver_name=solver_name, dms=dms)
    handler.process_requests(request)
    op_results = handler.get_solved_ops()
    return {'optimization_results': op_results}


# Instantiations
node0x21af11202e0=data_node(node_name='iso')
node0x21af11203d0=data_node(node_name='node')
node0x21af1120580=data_node(node_name='market')
node0x21af1120730=data_node(node_name='Power Rating')
node0x21af11208e0=data_node(node_name='Energy Capacity')
node0x21af1120a90=data_node(node_name='Round Trip')
node0x21af1120c40=data_node(node_name='months')
node0x21af1120ee0=python_node(node_name='ess_parameters',function=ess_parameters_function)
node0x21af1120f70=python_node(node_name='op_request',function=op_request_function)
node0x21aec8d62b0=data_node(node_name='Solver')
node0x21aec8d6700=python_node(node_name='valuation',function=valuation_function)


# Set inputs
node0x21af1120c40.set_inputs(m=[("3","2018")])
node0x21af1120730.set_inputs(power=1)
node0x21af11202e0.set_inputs(iso_name="PJM")
node0x21af11208e0.set_inputs(energy=4)
node0x21af11203d0.set_inputs(node_id="1")
node0x21aec8d62b0.set_inputs(solver_name='glpk')
node0x21af1120580.set_inputs(market_type="pjm_pfp")
node0x21af1120a90.set_inputs(rte=0.85)

# Connections
node0x21af11202e0.connect_to(to_node_list=[node0x21af1120f70], mapping=[{'iso_name': 'iso'}])
node0x21af11203d0.connect_to(to_node_list=[node0x21af1120f70], mapping=[{'node_id': 'node'}])
node0x21af1120580.connect_to(to_node_list=[node0x21af1120f70], mapping=[{'market_type': 'market'}])
node0x21af1120730.connect_to(to_node_list=[node0x21af1120ee0], mapping=[{'power': 'power'}])
node0x21af11208e0.connect_to(to_node_list=[node0x21af1120ee0], mapping=[{'energy': 'energy'}])
node0x21af1120a90.connect_to(to_node_list=[node0x21af1120ee0], mapping=[{'rte': 'rte'}])
node0x21af1120c40.connect_to(to_node_list=[node0x21af1120f70], mapping=[{'m': 'month'}])
node0x21aec8d62b0.connect_to(to_node_list=[node0x21aec8d6700], mapping=[{'solver_name': 'solver_name'}])
node0x21af1120ee0.connect_to(to_node_list=[node0x21af1120f70], mapping=[{'ess_parameters': 'ess'}])
node0x21af1120f70.connect_to(to_node_list=[node0x21aec8d6700], mapping=[{'request': 'request'}])

# Get Outputs
print('months_outputs:',node0x21af1120c40.get_outputs())
print('Power Rating_outputs:',node0x21af1120730.get_outputs())
print('iso_outputs:',node0x21af11202e0.get_outputs())
print('Energy Capacity_outputs:',node0x21af11208e0.get_outputs())
print('node_outputs:',node0x21af11203d0.get_outputs())
print('Solver_outputs:',node0x21aec8d62b0.get_outputs())
print('market_outputs:',node0x21af1120580.get_outputs())
print('Round Trip_outputs:',node0x21af1120a90.get_outputs())
print('ess_parameters_outputs:',node0x21af1120ee0.get_outputs())
print('op_request_outputs:',node0x21af1120f70.get_outputs())
print('valuation_outputs:',node0x21aec8d6700.get_outputs())