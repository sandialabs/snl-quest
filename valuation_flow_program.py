from quest.snl_libraries.workspace.nodes.pynodes import python_node, data_node










from valuation.es_gui.apps.valuation.op_handler import ValuationOptimizerHandler



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
    handler = ValuationOptimizerHandler(solver_name=solver_name)
    handler.process_requests(request)
    op_results = handler.get_solved_ops()
    return {'optimization_results': op_results}


# Instantiations
node0x290043de730=data_node(node_name='iso')
node0x290043deb50=data_node(node_name='node')
node0x290043debb0=data_node(node_name='market')
node0x290043de9d0=data_node(node_name='Power Rating')
node0x29001c3e8e0=data_node(node_name='Energy Capacity')
node0x29001c3edc0=data_node(node_name='Round Trip')
node0x29001c3e7c0=data_node(node_name='months')
node0x29001c3e250=python_node(node_name='ess_parameters',function=ess_parameters_function)
node0x29001c3e430=python_node(node_name='op_request',function=op_request_function)
node0x29001c3eac0=data_node(node_name='Solver')
node0x29002f32070=python_node(node_name='valuation',function=valuation_function)


# Set inputs
node0x290043debb0.set_inputs(market_type="pjm_pfp")
node0x29001c3e8e0.set_inputs(energy=4)
node0x29001c3eac0.set_inputs(solver_name='glpk')
node0x290043deb50.set_inputs(node_id=1)
node0x290043de730.set_inputs(iso_name="PJM")
node0x29001c3edc0.set_inputs(rte=0.85)
node0x29001c3e7c0.set_inputs(m=[(3,2018)])
node0x290043de9d0.set_inputs(power=1)

# Connections
node0x290043de730.connect_to(to_node_list=[node0x29001c3e430], mapping=[{'iso_name': 'iso'}])
node0x290043deb50.connect_to(to_node_list=[node0x29001c3e430], mapping=[{'node_id': 'node'}])
node0x290043debb0.connect_to(to_node_list=[node0x29001c3e430], mapping=[{'market_type': 'market'}])
node0x290043de9d0.connect_to(to_node_list=[node0x29001c3e250], mapping=[{'power': 'power'}])
node0x29001c3e8e0.connect_to(to_node_list=[node0x29001c3e250], mapping=[{'energy': 'energy'}])
node0x29001c3edc0.connect_to(to_node_list=[node0x29001c3e250], mapping=[{'rte': 'rte'}])
node0x29001c3e7c0.connect_to(to_node_list=[node0x29001c3e430], mapping=[{'m': 'month'}])
node0x29001c3eac0.connect_to(to_node_list=[node0x29002f32070], mapping=[{'solver_name': 'solver_name'}])
node0x29001c3e250.connect_to(to_node_list=[node0x29001c3e430], mapping=[{'ess_parameters': 'ess'}])
node0x29001c3e430.connect_to(to_node_list=[node0x29002f32070], mapping=[{'request': 'request'}])

# Get Outputs
print('market_outputs:',node0x290043debb0.get_outputs())
print('Energy Capacity_outputs:',node0x29001c3e8e0.get_outputs())
print('Solver_outputs:',node0x29001c3eac0.get_outputs())
print('node_outputs:',node0x290043deb50.get_outputs())
print('iso_outputs:',node0x290043de730.get_outputs())
print('Round Trip_outputs:',node0x29001c3edc0.get_outputs())
print('months_outputs:',node0x29001c3e7c0.get_outputs())
print('Power Rating_outputs:',node0x290043de9d0.get_outputs())
print('ess_parameters_outputs:',node0x29001c3e250.get_outputs())
print('op_request_outputs:',node0x29001c3e430.get_outputs())
print('valuation_outputs:',node0x29002f32070.get_outputs())