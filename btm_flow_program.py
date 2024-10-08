from quest.snl_libraries.workspace.nodes.pynodes import python_node, data_node
from btm.es_gui.tools.btm.btm_dms import BtmDMS






import json


from btm.es_gui.apps.btm.op_handler_workspace import BtmOptimizerHandler








# Functions
def data_manager_function(data_path):
    dms = BtmDMS(max_memory=100000, save_data=True, save_name='btm_dms.p', home_path=data_path)
    return {'dms': dms}

def load_profile_function(load_data_path):
    load_profile = {'name': 'load', 'path': load_data_path}
    return {'load_profile': load_profile}

def pv_profile_function(pv_data_path):
    pv_profile = {'name': 'pv', 'path': pv_data_path}
    return {'pv_profile': pv_profile}

def rate_structure_function(rate_path):
    with open(rate_path, 'r') as file:
        rate_structure = json.load(file)
    return {'rate_structure': rate_structure}
def btm_op_request_function(rate_structure, pv_profile, load_profile, ess_parameters):
    op_handler_request = {'rate_structure': rate_structure, 'load_profile': load_profile, 'pv_profile': pv_profile, 'params': ess_parameters}
    return {'btm_op_request': op_handler_request}
def btm_op_process_function(btm_op_request, dms, solver_name):
    btm_op_handler = BtmOptimizerHandler(solver_name=solver_name, dms=dms)
    (btm_solved_op, handler_status) = btm_op_handler.process_requests(btm_op_request)
    return {'btm_solved_op': btm_solved_op, 'handler_status': handler_status}

def ess_parameters_function(power, energy, rte):
    params = {'Power_rating': power, 'Energy_capacity': energy, 'Round_trip_efficiency': rte, 'Transformer_rating': 10000, 'State_of_charge_min': 0.1, 'State_of_charge_max': 0.9, 'State_of_charge_init': 0.5}
    return {'ess_parameters': [params]}





# Instantiations
node0x2b23fe3db80=python_node(node_name='data_manager',function=data_manager_function)
node0x2b23fe69ac0=data_node(node_name='data_location')
node0x2b23fe69f40=python_node(node_name='load_profile',function=load_profile_function)
node0x2b23fe8d520=data_node(node_name='pv_path')
node0x2b23fe8d3a0=python_node(node_name='pv_profile',function=pv_profile_function)
node0x2b23fe8d220=data_node(node_name='rate_path')
node0x2b23fe8d730=python_node(node_name='rate_structure',function=rate_structure_function)
node0x2b23fe8d880=python_node(node_name='btm_op_request',function=btm_op_request_function)
node0x2b23fe8da60=python_node(node_name='btm_op_process',function=btm_op_process_function)
node0x2b23fe8ddf0=data_node(node_name='power rating')
node0x2b23f8bf1f0=python_node(node_name='ess_parameters',function=ess_parameters_function)
node0x2b23f8bf340=data_node(node_name='energy capacity')
node0x2b23f8bf670=data_node(node_name='rte')
node0x2b23f8bf7f0=data_node(node_name='solver')
node0x2b23f8bf970=data_node(node_name='load_path')

# Set inputs
node0x2b23fe8ddf0.set_inputs(power=100)
node0x2b23fe8d520.set_inputs(pv_path=r"C:\Users\ylpomer\Desktop\pub_q\snl-quest\quest\app_envs\env_btm\Lib\site-packages\btm\data\pv\pvhydepark.json")
node0x2b23fe69ac0.set_inputs(data_path="data")
node0x2b23fe8d220.set_inputs(rate_path=r"C:\Users\ylpomer\Desktop\pub_q\snl-quest\quest\app_envs\env_btm\Lib\site-packages\btm\data\rate_structures\Flatratesantafe.json")
node0x2b23f8bf7f0.set_inputs(solver_name="glpk")
node0x2b23f8bf340.set_inputs(energy=400)
node0x2b23f8bf670.set_inputs(rte=0.88)
node0x2b23f8bf970.set_inputs(load_path=r"C:\Users\ylpomer\Desktop\pub_q\snl-quest\quest\app_envs\env_btm\Lib\site-packages\btm\data\load\commercial\USA_CA_San.Francisco.Intl.AP.724940_TMY3\RefBldgLargeHotelNew2004_7.1_5.0_3C_USA_CA_SAN_FRANCISCO.csv")

# Connections
node0x2b23fe69ac0.connect_to(to_node_list=[node0x2b23fe3db80], mapping=[{'data_path': 'data_path'}])
node0x2b23f8bf970.connect_to(to_node_list=[node0x2b23fe69f40], mapping=[{'load_path': 'load_data_path'}])
node0x2b23fe8d520.connect_to(to_node_list=[node0x2b23fe8d3a0], mapping=[{'pv_path': 'pv_data_path'}])
node0x2b23fe8d220.connect_to(to_node_list=[node0x2b23fe8d730], mapping=[{'rate_path': 'rate_path'}])
node0x2b23f8bf7f0.connect_to(to_node_list=[node0x2b23fe8da60], mapping=[{'solver_name': 'solver_name'}])
node0x2b23fe8ddf0.connect_to(to_node_list=[node0x2b23f8bf1f0], mapping=[{'power': 'power'}])
node0x2b23f8bf340.connect_to(to_node_list=[node0x2b23f8bf1f0], mapping=[{'energy': 'energy'}])
node0x2b23f8bf670.connect_to(to_node_list=[node0x2b23f8bf1f0], mapping=[{'rte': 'rte'}])
node0x2b23fe3db80.connect_to(to_node_list=[node0x2b23fe8da60], mapping=[{'dms': 'dms'}])
node0x2b23fe69f40.connect_to(to_node_list=[node0x2b23fe8d880], mapping=[{'load_profile': 'load_profile'}])
node0x2b23fe8d3a0.connect_to(to_node_list=[node0x2b23fe8d880], mapping=[{'pv_profile': 'pv_profile'}])
node0x2b23fe8d730.connect_to(to_node_list=[node0x2b23fe8d880], mapping=[{'rate_structure': 'rate_structure'}])
node0x2b23f8bf1f0.connect_to(to_node_list=[node0x2b23fe8d880], mapping=[{'ess_parameters': 'ess_parameters'}])
node0x2b23fe8d880.connect_to(to_node_list=[node0x2b23fe8da60], mapping=[{'btm_op_request': 'btm_op_request'}])

# Get Outputs
print('power rating_outputs:',node0x2b23fe8ddf0.get_outputs())
print('pv_path_outputs:',node0x2b23fe8d520.get_outputs())
print('data_location_outputs:',node0x2b23fe69ac0.get_outputs())
print('rate_path_outputs:',node0x2b23fe8d220.get_outputs())
print('solver_outputs:',node0x2b23f8bf7f0.get_outputs())
print('energy capacity_outputs:',node0x2b23f8bf340.get_outputs())
print('rte_outputs:',node0x2b23f8bf670.get_outputs())
print('load_path_outputs:',node0x2b23f8bf970.get_outputs())
print('pv_profile_outputs:',node0x2b23fe8d3a0.get_outputs())
print('data_manager_outputs:',node0x2b23fe3db80.get_outputs())
print('ess_parameters_outputs:',node0x2b23f8bf1f0.get_outputs())
print('rate_structure_outputs:',node0x2b23fe8d730.get_outputs())
print('load_profile_outputs:',node0x2b23fe69f40.get_outputs())
print('btm_op_request_outputs:',node0x2b23fe8d880.get_outputs())
print('btm_op_process_outputs:',node0x2b23fe8da60.get_outputs())