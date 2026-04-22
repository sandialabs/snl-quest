# QuESt flow bootstrap
import os
import sys
import subprocess
QUEST_ROOT = r'C:/work/quest210-py313/Lib/site-packages/quest'
FLOW_PYTHON_EXECUTABLE = r'C:/work/quest210-py313/Scripts/python.exe'
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









# Functions






def btm_flow_2026_new_function(pv_path=None, rate_path=None, power_rating=None, energy_capacity=None, rte=None, load_path=None):
    def update_subflow(subflow_nodes_df, **kwargs):
        for idx, row in subflow_nodes_df.iterrows():
            if row.get('node_type') == 'data_node' and row.get('node_is_from_master') == True:
                node_name = str(row.get('node_name', '')).strip()
                if node_name in kwargs:
                    subflow_nodes_df.at[idx, 'node_input_value'] = repr(kwargs[node_name])
        return subflow_nodes_df

    def run_subflow(subflow_name, subflow_nodes_df, subflow_connections_df, python_executable=None):
        f = flow(flow_name=subflow_name, nodes_df=subflow_nodes_df, connections_df=subflow_connections_df)
        f.set_inputs()
        f.get_outputs(key=None)
        f.make()
        append_lines = []
        append_lines.append('import json')
        append_lines.append('_quest_subflow_results = {}')
        append_lines.append("if 'node0x2085e1469e0_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['data_manager'] = node0x2085e1469e0_outputs")
        append_lines.append("if 'node0x2085e146c40_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['load_profile'] = node0x2085e146c40_outputs")
        append_lines.append("if 'node0x2085e146fd0_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['pv_profile'] = node0x2085e146fd0_outputs")
        append_lines.append("if 'node0x2085e147360_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['rate_structure_new'] = node0x2085e147360_outputs")
        append_lines.append("if 'node0x2085e147490_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['btm_op_request'] = node0x2085e147490_outputs")
        append_lines.append("if 'node0x2085e1475c0_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['btm_op_process'] = node0x2085e1475c0_outputs")
        append_lines.append("if 'node0x2085e147820_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['ess_parameters'] = node0x2085e147820_outputs")
        append_lines.append("if 'node0x2085e147e10_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['results'] = node0x2085e147e10_outputs")
        append_lines.append("print('__QUEST_SUBFLOW_RESULTS_START__')")
        append_lines.append("print(json.dumps(_quest_subflow_results, default=str))")
        append_lines.append("print('__QUEST_SUBFLOW_RESULTS_END__')")
        f.main_py = f.main_py.rstrip() + '\n\n' + '\n'.join(append_lines) + '\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            f.save(tmpdir + os.sep)
            result = f.run(python_executable=python_executable)
            stdout = getattr(result, 'stdout', '') or ''
        start_marker = '__QUEST_SUBFLOW_RESULTS_START__'
        end_marker = '__QUEST_SUBFLOW_RESULTS_END__'
        if start_marker not in stdout or end_marker not in stdout:
            raise RuntimeError('Could not find subflow results in stdout.\nSTDOUT:\n' + stdout)
        payload = stdout.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()
        if not payload:
            return {}
        return json.loads(payload)

    subflow_name = 'btm_flow_2026_new'
    subflow_nodes_df = pd.DataFrame([{'node_id': '0x2085e1468b0', 'node_name': 'BTM Optimization Handler', 'node_type': 'back_node', 'node_input_variable': '', 'node_input_value': 'This is the workprocess for setting up a behind the meter optimization  that estimates the cost saving for utility customers using btm ess given the load, pv profiles and rate structure.', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e1469e0', 'node_name': 'data_manager', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def data_manager_function(data_path):\n    dms = BtmDMS(max_memory=1000000, save_data=True, save_name='btm_dms.p', home_path=data_path)\n    return {'dms': dms}", 'node_imports': 'from btm.es_gui.tools.btm.btm_dms import BtmDMS\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\data_manager.ipynb'}, {'node_id': '0x2085e146b10', 'node_name': 'data_location', 'node_type': 'data_node', 'node_input_variable': 'data_path', 'node_input_value': '"/data/"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e146c40', 'node_name': 'load_profile', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def load_profile_function(load_data_path):\n    load_profile = {'name': 'data_center_10MW', 'path': load_data_path}\n    return {'load_profile': load_profile}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\load_profile.ipynb'}, {'node_id': '0x2085e146d70', 'node_name': 'pv_path', 'node_type': 'data_node', 'node_input_variable': 'pv_path', 'node_input_value': '"C:/work/quest20c/quest2/ZeroPV1.json"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e146fd0', 'node_name': 'pv_profile', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def pv_profile_function(pv_data_path):\n    pv_profile = {'name': 'ZeroPV', 'path': pv_data_path}\n    return {'pv_profile': pv_profile}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\pv_profile.ipynb'}, {'node_id': '0x2085e147100', 'node_name': 'rate_path', 'node_type': 'data_node', 'node_input_variable': 'rate_path', 'node_input_value': '"C:/work/quest20c/quest2/Dominion1MWtou.json"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e147360', 'node_name': 'rate_structure_new', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def rate_structure_new_function(rate_path):\n    with open(rate_path, 'r') as file:\n        rate_structure = json.load(file)\n    return {'rate_structure': rate_structure}", 'node_imports': 'import json\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\rate_structure_new.ipynb'}, {'node_id': '0x2085e147490', 'node_name': 'btm_op_request', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def btm_op_request_function(rate_structure, pv_profile, load_profile, ess_parameters):\n    op_handler_request = {'rate_structure': rate_structure, 'load_profile': load_profile, 'pv_profile': pv_profile, 'params': ess_parameters}\n    return {'btm_op_request': op_handler_request}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\btm_op_request.ipynb'}, {'node_id': '0x2085e1475c0', 'node_name': 'btm_op_process', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def btm_op_process_function(btm_op_request, dms, solver_name, solver_path=None):\n    if solver_path:\n        current_path = os.environ.get('PATH', '')\n        if solver_path not in current_path:\n            os.environ['PATH'] = solver_path + os.pathsep + current_path\n            print(f'[DEBUG] Added solver path: {solver_path}')\n    try:\n        import shutil\n        print('[DEBUG] glpsol found at:', shutil.which('glpsol'))\n    except:\n        pass\n    btm_op_handler = BtmOptimizerHandler(solver_name=solver_name, dms=dms)\n    (btm_solved_op, handler_status) = btm_op_handler.process_requests(btm_op_request)\n    return {'btm_solved_ops': btm_solved_op, 'handler_status': handler_status}", 'node_imports': 'from btm.es_gui.apps.btm.op_handler_workspace import BtmOptimizerHandler\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\btm_op_process.ipynb'}, {'node_id': '0x2085e1476f0', 'node_name': 'power_rating', 'node_type': 'data_node', 'node_input_variable': 'power', 'node_input_value': '100', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e147820', 'node_name': 'ess_parameters', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def ess_parameters_function(power, energy, rte):\n    params = {'Power_rating': power, 'Energy_capacity': energy, 'Round_trip_efficiency': rte, 'Transformer_rating': 10000, 'State_of_charge_min': 0.1, 'State_of_charge_max': 0.9, 'State_of_charge_init': 0.5}\n    return {'ess_parameters': [params]}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\ess_parameters.ipynb'}, {'node_id': '0x2085e147950', 'node_name': 'energy_capacity', 'node_type': 'data_node', 'node_input_variable': 'energy', 'node_input_value': '400', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e147a80', 'node_name': 'rte', 'node_type': 'data_node', 'node_input_variable': 'rte', 'node_input_value': '0.88', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e147bb0', 'node_name': 'solver', 'node_type': 'data_node', 'node_input_variable': 'solver_name', 'node_input_value': '"glpk"', 'node_value_display': True, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e147ce0', 'node_name': 'load_path', 'node_type': 'data_node', 'node_input_variable': 'load_path', 'node_input_value': '"C:/work/quest20c/quest2/data_center_virginia_10MW.csv"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x2085e147e10', 'node_name': 'results', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': ['saved_location', 'checkpoints'], 'node_function_wrapper': "def results_function(solved_ops, saved_location):\n    os.makedirs(saved_location, exist_ok=True)\n    checkpoints = {}\n    for op in solved_ops:\n        op_results = op[1].results\n        file_name = op[0]\n        file_name = re.sub('[^\\\\w\\\\s-]', '', file_name).replace(' ', '_') + '.csv'\n        file_name = saved_location + '/' + file_name\n        op_results.to_csv(file_name, index=False)\n        checkpoints[file_name] = file_name\n    return {'saved_location': saved_location, 'checkpoints': checkpoints}", 'node_imports': 'import os\nimport re\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\results.ipynb'}, {'node_id': '0x20839d9c050', 'node_name': 'results_location', 'node_type': 'data_node', 'node_input_variable': 'rs_location', 'node_input_value': '"./results/workspace"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x20839d9c180', 'node_name': 'solver_path', 'node_type': 'data_node', 'node_input_variable': 'path', 'node_input_value': '"C:/work/quest21c/Lib/site-packages/quest/app_envs/env_btm/glpk/glpk-4.65/w64"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}])
    subflow_connections_df = pd.DataFrame([{'connection_id': 1, 'from_node': '0x2085e146b10', 'to_node': '0x2085e1469e0', 'mapping': {'data_path': 'data_path'}}, {'connection_id': 2, 'from_node': '0x2085e1469e0', 'to_node': '0x2085e1475c0', 'mapping': {'dms': 'dms'}}, {'connection_id': 3, 'from_node': '0x2085e147ce0', 'to_node': '0x2085e146c40', 'mapping': {'load_path': 'load_data_path'}}, {'connection_id': 4, 'from_node': '0x2085e146c40', 'to_node': '0x2085e147490', 'mapping': {'load_profile': 'load_profile'}}, {'connection_id': 5, 'from_node': '0x2085e146d70', 'to_node': '0x2085e146fd0', 'mapping': {'pv_path': 'pv_data_path'}}, {'connection_id': 6, 'from_node': '0x2085e146fd0', 'to_node': '0x2085e147490', 'mapping': {'pv_profile': 'pv_profile'}}, {'connection_id': 7, 'from_node': '0x2085e147100', 'to_node': '0x2085e147360', 'mapping': {'rate_path': 'rate_path'}}, {'connection_id': 8, 'from_node': '0x2085e147360', 'to_node': '0x2085e147490', 'mapping': {'rate_structure': 'rate_structure'}}, {'connection_id': 9, 'from_node': '0x2085e147820', 'to_node': '0x2085e147490', 'mapping': {'ess_parameters': 'ess_parameters'}}, {'connection_id': 10, 'from_node': '0x2085e147490', 'to_node': '0x2085e1475c0', 'mapping': {'btm_op_request': 'btm_op_request'}}, {'connection_id': 11, 'from_node': '0x2085e147bb0', 'to_node': '0x2085e1475c0', 'mapping': {'solver_name': 'solver_name'}}, {'connection_id': 12, 'from_node': '0x20839d9c180', 'to_node': '0x2085e1475c0', 'mapping': {'path': 'solver_path'}}, {'connection_id': 13, 'from_node': '0x2085e1475c0', 'to_node': '0x2085e147e10', 'mapping': {'btm_solved_ops': 'solved_ops'}}, {'connection_id': 14, 'from_node': '0x2085e1476f0', 'to_node': '0x2085e147820', 'mapping': {'power': 'power'}}, {'connection_id': 15, 'from_node': '0x2085e147950', 'to_node': '0x2085e147820', 'mapping': {'energy': 'energy'}}, {'connection_id': 16, 'from_node': '0x2085e147a80', 'to_node': '0x2085e147820', 'mapping': {'rte': 'rte'}}, {'connection_id': 17, 'from_node': '0x20839d9c050', 'to_node': '0x2085e147e10', 'mapping': {'rs_location': 'saved_location'}}])
    subflow_nodes_df = update_subflow(subflow_nodes_df, pv_path=pv_path, rate_path=rate_path, power_rating=power_rating, energy_capacity=energy_capacity, rte=rte, load_path=load_path)
    _results = run_subflow(subflow_name, subflow_nodes_df, subflow_connections_df, python_executable='C:/work/quest210-py313/Lib/site-packages/quest/app_envs/env_btm/Scripts/python.exe')
    return {
        'saved_location': _results.get('results', {}).get('saved_location'),
        'checkpoints': _results.get('results', {}).get('checkpoints'),
    }

# Instantiations
node0x2085e2d5010=data_node(node_name='pv_path')
node0x2085e239f90=data_node(node_name='rate_path')
node0x2085e23a490=data_node(node_name='power rating')
node0x2085e145ba0=data_node(node_name='energy capacity')
node0x2085e146060=data_node(node_name='rte')
node0x2085e1463f0=data_node(node_name='load_path')
node0x2085e146520=python_node(node_name='btm_flow_2026_new',function=btm_flow_2026_new_function)

# Set inputs
node0x2085e145ba0.set_inputs(energy=400)
node0x2085e146060.set_inputs(rte=0.88)
node0x2085e1463f0.set_inputs(load_path="C:/work/quest20c/quest2/data_center_virginia_10MW.csv")
node0x2085e23a490.set_inputs(power=100)
node0x2085e239f90.set_inputs(rate_path="C:/work/quest20c/quest2/Dominion1MWtou.json")
node0x2085e2d5010.set_inputs(pv_path="C:/work/quest20c/quest2/ZeroPV1.json")

# Connections
node0x2085e2d5010.connect_to(to_node_list=[node0x2085e146520], mapping=[{'pv_path': 'pv_path'}])
node0x2085e239f90.connect_to(to_node_list=[node0x2085e146520], mapping=[{'rate_path': 'rate_path'}])
node0x2085e23a490.connect_to(to_node_list=[node0x2085e146520], mapping=[{'power': 'power_rating'}])
node0x2085e145ba0.connect_to(to_node_list=[node0x2085e146520], mapping=[{'energy': 'energy_capacity'}])
node0x2085e146060.connect_to(to_node_list=[node0x2085e146520], mapping=[{'rte': 'rte'}])
node0x2085e1463f0.connect_to(to_node_list=[node0x2085e146520], mapping=[{'load_path': 'load_path'}])

# Get Outputs
print('energy capacity_outputs:',node0x2085e145ba0.get_outputs())
print('rte_outputs:',node0x2085e146060.get_outputs())
print('load_path_outputs:',node0x2085e1463f0.get_outputs())
print('power rating_outputs:',node0x2085e23a490.get_outputs())
print('rate_path_outputs:',node0x2085e239f90.get_outputs())
print('pv_path_outputs:',node0x2085e2d5010.get_outputs())
print('btm_flow_2026_new_outputs:',node0x2085e146520.get_outputs())