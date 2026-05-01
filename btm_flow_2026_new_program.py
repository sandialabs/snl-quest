# QuESt flow bootstrap
import os
import sys
import subprocess
QUEST_ROOT = r'C:/work/quest210-py313/Lib/site-packages/quest'
FLOW_PYTHON_EXECUTABLE = r'C:/work/quest210-py313/Lib/site-packages/quest/app_envs/env_btm/Scripts/python.exe'
if os.path.dirname(QUEST_ROOT) not in sys.path:
    sys.path.append(os.path.dirname(QUEST_ROOT))
if (
    FLOW_PYTHON_EXECUTABLE
    and os.path.isfile(FLOW_PYTHON_EXECUTABLE)
    and os.path.abspath(sys.executable) != os.path.abspath(FLOW_PYTHON_EXECUTABLE)
    and os.environ.get('QUEST_FLOW_REEXEC') != '1'
):
    env = os.environ.copy()
    env['QUEST_FLOW_REEXEC'] = '1'
    result = subprocess.run(
        [FLOW_PYTHON_EXECUTABLE, __file__],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    raise SystemExit(result.returncode)

import sys
import os
import json
import tempfile
import pandas as pd
QUEST_ROOT = r'C:\work\quest210-py313\Lib\site-packages\quest'
if os.path.dirname(QUEST_ROOT) not in sys.path:
    sys.path.append(os.path.dirname(QUEST_ROOT))
from quest.snl_libraries.workspace.nodes.pynodes import python_node, data_node
from quest.snl_libraries.workspace.flow.questflow import *


from btm.es_gui.tools.btm.btm_dms import BtmDMS






import json


from btm.es_gui.apps.btm.op_handler_workspace import BtmOptimizerHandler







import os
import re




# Functions

def data_manager_function(data_path):
    dms = BtmDMS(max_memory=1000000, save_data=True, save_name='btm_dms.p', home_path=data_path)
    return {'dms': dms}

def load_profile_function(load_data_path):
    load_profile = {'name': 'data_center_10MW', 'path': load_data_path}
    return {'load_profile': load_profile}

def pv_profile_function(pv_data_path):
    pv_profile = {'name': 'ZeroPV', 'path': pv_data_path}
    return {'pv_profile': pv_profile}

def rate_structure_new_function(rate_path):
    with open(rate_path, 'r') as file:
        rate_structure = json.load(file)
    return {'rate_structure': rate_structure}
def btm_op_request_function(rate_structure, pv_profile, load_profile, ess_parameters):
    op_handler_request = {'rate_structure': rate_structure, 'load_profile': load_profile, 'pv_profile': pv_profile, 'params': ess_parameters}
    return {'btm_op_request': op_handler_request}
def btm_op_process_function(btm_op_request, dms, solver_name, solver_path=None):
    if solver_path:
        current_path = os.environ.get('PATH', '')
        if solver_path not in current_path:
            os.environ['PATH'] = solver_path + os.pathsep + current_path
            print(f'[DEBUG] Added solver path: {solver_path}')
    try:
        import shutil
        print('[DEBUG] glpsol found at:', shutil.which('glpsol'))
    except:
        pass
    btm_op_handler = BtmOptimizerHandler(solver_name=solver_name, dms=dms)
    (btm_solved_op, handler_status) = btm_op_handler.process_requests(btm_op_request)
    return {'btm_solved_ops': btm_solved_op, 'handler_status': handler_status}

def ess_parameters_function(power, energy, rte):
    params = {'Power_rating': power, 'Energy_capacity': energy, 'Round_trip_efficiency': rte, 'Transformer_rating': 10000, 'State_of_charge_min': 0.1, 'State_of_charge_max': 0.9, 'State_of_charge_init': 0.5}
    return {'ess_parameters': [params]}




def results_function(solved_ops, saved_location):
    os.makedirs(saved_location, exist_ok=True)
    checkpoints = {}
    for op in solved_ops:
        op_results = op[1].results
        file_name = op[0]
        file_name = re.sub('[^\\w\\s-]', '', file_name).replace(' ', '_') + '.csv'
        file_name = saved_location + '/' + file_name
        op_results.to_csv(file_name, index=False)
        checkpoints[file_name] = file_name
    return {'saved_location': saved_location, 'checkpoints': checkpoints}



# Instantiations

node0x23e731869e0=python_node(node_name='data_manager',function=data_manager_function)
node0x23e73186b10=data_node(node_name='data_location')
node0x23e73186c40=python_node(node_name='load_profile',function=load_profile_function)
node0x23e73186d70=data_node(node_name='pv_path')
node0x23e73186fd0=python_node(node_name='pv_profile',function=pv_profile_function)
node0x23e73187100=data_node(node_name='rate_path')
node0x23e73187360=python_node(node_name='rate_structure_new',function=rate_structure_new_function)
node0x23e73187490=python_node(node_name='btm_op_request',function=btm_op_request_function)
node0x23e731875c0=python_node(node_name='btm_op_process',function=btm_op_process_function)
node0x23e731876f0=data_node(node_name='power_rating')
node0x23e73187820=python_node(node_name='ess_parameters',function=ess_parameters_function)
node0x23e73187950=data_node(node_name='energy_capacity')
node0x23e73187a80=data_node(node_name='rte')
node0x23e73187bb0=data_node(node_name='solver')
node0x23e73187ce0=data_node(node_name='load_path')
node0x23e73187e10=python_node(node_name='results',function=results_function)
node0x23e4edf0050=data_node(node_name='results_location')
node0x23e4edf0180=data_node(node_name='solver_path')

# Set inputs
node0x23e73187a80.set_inputs(rte=0.88)
node0x23e731876f0.set_inputs(power=100)
node0x23e73187100.set_inputs(rate_path="C:/work/quest20c/quest2/Dominion1MWtou.json")
node0x23e4edf0180.set_inputs(path="C:/work/quest21c/Lib/site-packages/quest/app_envs/env_btm/glpk/glpk-4.65/w64")
node0x23e73186d70.set_inputs(pv_path="C:/work/quest20c/quest2/ZeroPV1.json")
node0x23e73187ce0.set_inputs(load_path="C:/work/quest20c/quest2/data_center_virginia_10MW.csv")
node0x23e73186b10.set_inputs(data_path="/data/")
node0x23e73187bb0.set_inputs(solver_name="glpk")
node0x23e73187950.set_inputs(energy=400)
node0x23e4edf0050.set_inputs(rs_location="./results/workspace")

# Connections
node0x23e73186b10.connect_to(to_node_list=[node0x23e731869e0], mapping=[{'data_path': 'data_path'}])
node0x23e73187950.connect_to(to_node_list=[node0x23e73187820], mapping=[{'energy': 'energy'}])
node0x23e731876f0.connect_to(to_node_list=[node0x23e73187820], mapping=[{'power': 'power'}])
node0x23e4edf0180.connect_to(to_node_list=[node0x23e731875c0], mapping=[{'path': 'solver_path'}])
node0x23e73187bb0.connect_to(to_node_list=[node0x23e731875c0], mapping=[{'solver_name': 'solver_name'}])
node0x23e73187a80.connect_to(to_node_list=[node0x23e73187820], mapping=[{'rte': 'rte'}])
node0x23e4edf0050.connect_to(to_node_list=[node0x23e73187e10], mapping=[{'rs_location': 'saved_location'}])
node0x23e73186d70.connect_to(to_node_list=[node0x23e73186fd0], mapping=[{'pv_path': 'pv_data_path'}])
node0x23e73187ce0.connect_to(to_node_list=[node0x23e73186c40], mapping=[{'load_path': 'load_data_path'}])
node0x23e73187100.connect_to(to_node_list=[node0x23e73187360], mapping=[{'rate_path': 'rate_path'}])
node0x23e73187360.connect_to(to_node_list=[node0x23e73187490], mapping=[{'rate_structure': 'rate_structure'}])
node0x23e73186fd0.connect_to(to_node_list=[node0x23e73187490], mapping=[{'pv_profile': 'pv_profile'}])
node0x23e73186c40.connect_to(to_node_list=[node0x23e73187490], mapping=[{'load_profile': 'load_profile'}])
node0x23e731869e0.connect_to(to_node_list=[node0x23e731875c0], mapping=[{'dms': 'dms'}])
node0x23e73187820.connect_to(to_node_list=[node0x23e73187490], mapping=[{'ess_parameters': 'ess_parameters'}])
node0x23e73187490.connect_to(to_node_list=[node0x23e731875c0], mapping=[{'btm_op_request': 'btm_op_request'}])
node0x23e731875c0.connect_to(to_node_list=[node0x23e73187e10], mapping=[{'btm_solved_ops': 'solved_ops'}])

# Get Outputs
print('rte_outputs:',node0x23e73187a80.get_outputs())
print('power_rating_outputs:',node0x23e731876f0.get_outputs())
print('rate_path_outputs:',node0x23e73187100.get_outputs())
print('solver_path_outputs:',node0x23e4edf0180.get_outputs())
print('pv_path_outputs:',node0x23e73186d70.get_outputs())
print('load_path_outputs:',node0x23e73187ce0.get_outputs())
print('data_location_outputs:',node0x23e73186b10.get_outputs())
print('solver_outputs:',node0x23e73187bb0.get_outputs())
print('energy_capacity_outputs:',node0x23e73187950.get_outputs())
print('results_location_outputs:',node0x23e4edf0050.get_outputs())
print('data_manager_outputs:',node0x23e731869e0.get_outputs())
print('ess_parameters_outputs:',node0x23e73187820.get_outputs())
print('load_profile_outputs:',node0x23e73186c40.get_outputs())
print('rate_structure_new_outputs:',node0x23e73187360.get_outputs())
print('pv_profile_outputs:',node0x23e73186fd0.get_outputs())
print('btm_op_request_outputs:',node0x23e73187490.get_outputs())
print('btm_op_process_outputs:',node0x23e731875c0.get_outputs())
print('results_outputs:',node0x23e73187e10.get_outputs())