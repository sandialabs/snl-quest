# QuESt flow bootstrap
import os
import sys
import subprocess
QUEST_ROOT = r'C:/work/quest210-py313/Lib/site-packages/quest'
FLOW_PYTHON_EXECUTABLE = r'C:/work/quest210_env/Scripts/python.exe'
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
    env['PYTHONUNBUFFERED'] = '1'
    proc = subprocess.Popen(
        [FLOW_PYTHON_EXECUTABLE, '-u', __file__],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            print(line, end='')
    raise SystemExit(proc.wait())

import sys
import os
import json
import tempfile
import pandas as pd
QUEST_ROOT = r'C:\work\quest210-py313\Lib\site-packages\quest'
quest_parent = os.path.dirname(QUEST_ROOT)
if quest_parent not in sys.path:
    sys.path.append(quest_parent)
from quest.snl_libraries.workspace.nodes.pynodes import python_node, data_node
from quest.snl_libraries.workspace.flow.questflow import *






# Functions



def btm_flow_2026_new_function(pv_path=None, rate_path1=None, load_path=None):
    def apply_master_inputs_to_subflow_inputs(subflow_inputs_df, **kwargs):
        updated_cases = []
        for case_info in subflow_inputs_df or []:
            if not isinstance(case_info, dict):
                continue
            updated_case = dict(case_info)
            case_inputs = case_info.get('inputs', [])
            if not isinstance(case_inputs, list):
                case_inputs = []
            updated_inputs = []
            for record in case_inputs:
                if not isinstance(record, dict):
                    continue
                updated_record = dict(record)
                is_from_master = str(updated_record.get('is_from_master', '')).strip().lower() == 'true' if not isinstance(updated_record.get('is_from_master'), bool) else bool(updated_record.get('is_from_master'))
                if is_from_master:
                    node_name = str(updated_record.get('node_name', '')).strip()
                    incoming_value = None
                    if node_name in kwargs and kwargs.get(node_name) is not None:
                        incoming_value = kwargs.get(node_name)
                    if incoming_value is not None:
                        updated_record['value'] = repr(incoming_value)
                updated_inputs.append(updated_record)
            updated_case['inputs'] = updated_inputs
            updated_cases.append(updated_case)
        return updated_cases

    def normalize_subflow_inputs(subflow_inputs_df):
        normalized_inputs = []
        for index, case_info in enumerate(subflow_inputs_df or []):
            if not isinstance(case_info, dict):
                continue
            case_name = str(case_info.get('name', '') or '').strip()
            if not case_name or (index == 0 and case_name == 'Base Case'):
                case_name = f'Subcase {index}'
            case_inputs = case_info.get('inputs', [])
            if not isinstance(case_inputs, list):
                case_inputs = []
            normalized_inputs.append({'name': case_name, 'inputs': case_inputs})
        if not normalized_inputs:
            normalized_inputs.append({'name': 'Subcase 0', 'inputs': []})
        return normalized_inputs

    def materialize_subflow_nodes_df(subflow_nodes_df, subflow_inputs_df, input_case=None):
        case_inputs = []
        fallback_inputs = []
        for index, case_info in enumerate(subflow_inputs_df or []):
            if not isinstance(case_info, dict):
                continue
            case_name = str(case_info.get('name', '') or '').strip() or f'Subcase {index}'
            inputs = case_info.get('inputs', [])
            if not isinstance(inputs, list):
                inputs = []
            if not fallback_inputs:
                fallback_inputs = inputs
            if input_case is not None and case_name == input_case:
                case_inputs = inputs
                break
        if not case_inputs:
            case_inputs = fallback_inputs
        case_inputs_by_id = {}
        case_inputs_by_name = {}
        for record in case_inputs:
            if not isinstance(record, dict):
                continue
            node_id = str(record.get('node_id', '') or '').strip()
            node_name = str(record.get('node_name', '') or '').strip()
            if node_id:
                case_inputs_by_id[node_id] = record
            if node_name:
                case_inputs_by_name[node_name] = record
        nodes_df = subflow_nodes_df.copy(deep=True)
        nodes_records = []
        for row in nodes_df.to_dict('records'):
            updated_row = dict(row)
            if str(updated_row.get('node_type', '')).strip() == 'data_node':
                node_id = str(updated_row.get('node_id', '') or '').strip()
                node_name = str(updated_row.get('node_name', '') or '').strip()
                record = case_inputs_by_id.get(node_id) or case_inputs_by_name.get(node_name)
                if isinstance(record, dict) and 'value' in record:
                    updated_row['node_input_value'] = record.get('value', '')
            nodes_records.append(updated_row)
        return pd.DataFrame(nodes_records)

    def run_subflow(subflow_name, subflow_nodes_df, subflow_connections_df, subflow_inputs_df, input_case=None, python_executable=None):
        materialized_nodes_df = materialize_subflow_nodes_df(subflow_nodes_df, subflow_inputs_df, input_case=input_case)
        f = flow(flow_name=subflow_name, nodes_df=materialized_nodes_df, connections_df=subflow_connections_df, inputs_df=subflow_inputs_df)
        f.make(input_case=input_case)
        append_lines = []
        append_lines.append('import json')
        append_lines.append('_quest_subflow_results = {}')
        append_lines.append("if 'node0x13997aca780_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['data_manager'] = node0x13997aca780_outputs")
        append_lines.append("if 'node0x13997acab10_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['load_profile'] = node0x13997acab10_outputs")
        append_lines.append("if 'node0x13997acafd0_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['pv_profile'] = node0x13997acafd0_outputs")
        append_lines.append("if 'node0x13997acb360_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['rate_structure_new'] = node0x13997acb360_outputs")
        append_lines.append("if 'node0x13997acb490_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['btm_op_request'] = node0x13997acb490_outputs")
        append_lines.append("if 'node0x13997acb5c0_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['btm_op_process'] = node0x13997acb5c0_outputs")
        append_lines.append("if 'node0x13997acb820_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['ess_parameters'] = node0x13997acb820_outputs")
        append_lines.append("if 'node0x13997acbe10_outputs' in globals():")
        append_lines.append("    _quest_subflow_results['results'] = node0x13997acbe10_outputs")
        append_lines.append("print('__QUEST_SUBFLOW_RESULTS_START__')")
        append_lines.append("print(json.dumps(_quest_subflow_results, default=str))")
        append_lines.append("print('__QUEST_SUBFLOW_RESULTS_END__')")
        f.main_py = f.main_py.rstrip() + '\n\n' + '\n'.join(append_lines) + '\n'
        with tempfile.TemporaryDirectory() as tmpdir:
            f.save(tmpdir + os.sep)
            result = f.run(python_executable=python_executable, stream_output=True, input_case=input_case)
            stdout = getattr(result, 'quest_stdout', None)
            if stdout is None:
                stdout = getattr(result, 'stdout', '') or ''
            if hasattr(stdout, 'read'):
                try:
                    stdout = stdout.read()
                except Exception:
                    stdout = str(stdout)
            elif not isinstance(stdout, str):
                stdout = str(stdout)
        start_marker = '__QUEST_SUBFLOW_RESULTS_START__'
        end_marker = '__QUEST_SUBFLOW_RESULTS_END__'
        if start_marker not in stdout or end_marker not in stdout:
            raise RuntimeError('Could not find subflow results in stdout.\nSTDOUT:\n' + stdout)
        payload = stdout.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()
        if not payload:
            return {}
        return json.loads(payload)

    subflow_name = 'btm_flow_2026_new'
    subflow_nodes_df = pd.DataFrame([{'node_id': '0x13997ac96e0', 'node_name': 'BTM Optimization Handler', 'node_type': 'back_node', 'node_input_variable': '', 'node_input_value': 'This is the workprocess for setting up a behind the meter optimization  that estimates the cost saving for utility customers using btm ess given the load, pv profiles and rate structure.', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997aca780', 'node_name': 'data_manager', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def data_manager_function(data_path):\n    dms = BtmDMS(max_memory=1000000, save_data=True, save_name='btm_dms.p', home_path=data_path)\n    return {'dms': dms}", 'node_imports': 'from btm.es_gui.tools.btm.btm_dms import BtmDMS\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\data_manager.ipynb'}, {'node_id': '0x13997aca9e0', 'node_name': 'data_location', 'node_type': 'data_node', 'node_input_variable': 'data_path', 'node_input_value': '"/data/"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acab10', 'node_name': 'load_profile', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def load_profile_function(load_data_path):\n    load_profile = {'name': 'data_center_10MW', 'path': load_data_path}\n    return {'load_profile': load_profile}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\load_profile.ipynb'}, {'node_id': '0x13997acad70', 'node_name': 'pv_path', 'node_type': 'data_node', 'node_input_variable': 'pv_path', 'node_input_value': '', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acafd0', 'node_name': 'pv_profile', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def pv_profile_function(pv_data_path):\n    pv_profile = {'name': 'ZeroPV', 'path': pv_data_path}\n    return {'pv_profile': pv_profile}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\pv_profile.ipynb'}, {'node_id': '0x13997acb100', 'node_name': 'rate_path1', 'node_type': 'data_node', 'node_input_variable': 'rate_path', 'node_input_value': '', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acb360', 'node_name': 'rate_structure_new', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def rate_structure_new_function(rate_path):\n    with open(rate_path, 'r') as file:\n        rate_structure = json.load(file)\n    return {'rate_structure': rate_structure}", 'node_imports': 'import json\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\rate_structure_new.ipynb'}, {'node_id': '0x13997acb490', 'node_name': 'btm_op_request', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def btm_op_request_function(rate_structure, pv_profile, load_profile, ess_parameters):\n    op_handler_request = {'rate_structure': rate_structure, 'load_profile': load_profile, 'pv_profile': pv_profile, 'params': ess_parameters}\n    return {'btm_op_request': op_handler_request}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\btm_op_request.ipynb'}, {'node_id': '0x13997acb5c0', 'node_name': 'btm_op_process', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def btm_op_process_function(btm_op_request, dms, solver_name):\n    btm_op_handler = BtmOptimizerHandler(solver_name=solver_name, dms=dms)\n    btm_solved_op, handler_status = btm_op_handler.process_requests(btm_op_request)\n    return {'btm_solved_ops': btm_solved_op, 'handler_status': handler_status}", 'node_imports': 'from btm.es_gui.apps.btm.op_handler_workspace import BtmOptimizerHandler\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\btm_op_process.ipynb'}, {'node_id': '0x13997acb6f0', 'node_name': 'power_rating', 'node_type': 'data_node', 'node_input_variable': 'power', 'node_input_value': '100', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acb820', 'node_name': 'ess_parameters', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': "def ess_parameters_function(power, energy, rte):\n    params = {'Power_rating': power, 'Energy_capacity': energy, 'Round_trip_efficiency': rte, 'Transformer_rating': 10000, 'State_of_charge_min': 0.1, 'State_of_charge_max': 0.9, 'State_of_charge_init': 0.5}\n    return {'ess_parameters': [params]}", 'node_imports': '', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\ess_parameters.ipynb'}, {'node_id': '0x13997acb950', 'node_name': 'energy_capacity', 'node_type': 'data_node', 'node_input_variable': 'energy', 'node_input_value': '400', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acba80', 'node_name': 'rte', 'node_type': 'data_node', 'node_input_variable': 'rte', 'node_input_value': '0.88', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acbbb0', 'node_name': 'solver', 'node_type': 'data_node', 'node_input_variable': 'solver_name', 'node_input_value': '"glpk"', 'node_value_display': True, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acbce0', 'node_name': 'load_path', 'node_type': 'data_node', 'node_input_variable': 'load_path', 'node_input_value': '', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': True, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}, {'node_id': '0x13997acbe10', 'node_name': 'results', 'node_type': 'python_node', 'node_input_variable': '', 'node_input_value': '', 'node_value_display': False, 'node_is_path': False, 'node_is_from_master': False, 'node_expose_outputs': ['saved_location', 'checkpoints'], 'node_function_wrapper': "def results_function(solved_ops, saved_location):\n    os.makedirs(saved_location, exist_ok=True)\n    checkpoints = {}\n    for op in solved_ops:\n        op_results = op[1].results\n        file_name = op[0]\n        file_name = re.sub('[^\\\\w\\\\s-]', '', file_name).replace(' ', '_') + '.csv'\n        file_name = saved_location + '/' + file_name\n        op_results.to_csv(file_name, index=False)\n        checkpoints[file_name] = file_name\n    return {'saved_location': saved_location, 'checkpoints': checkpoints}", 'node_imports': 'import os\nimport re\n', 'node_notebook_path': 'c:\\work\\quest20c\\node_notebooks\\results.ipynb'}, {'node_id': '0x1399cb2c050', 'node_name': 'results_location', 'node_type': 'data_node', 'node_input_variable': 'rs_location', 'node_input_value': '"./results/workspace"', 'node_value_display': False, 'node_is_path': True, 'node_is_from_master': False, 'node_expose_outputs': [], 'node_function_wrapper': '', 'node_imports': '', 'node_notebook_path': ''}])
    subflow_connections_df = pd.DataFrame([{'connection_id': 1, 'from_node': '0x13997aca9e0', 'to_node': '0x13997aca780', 'mapping': {'data_path': 'data_path'}}, {'connection_id': 2, 'from_node': '0x13997aca780', 'to_node': '0x13997acb5c0', 'mapping': {'dms': 'dms'}}, {'connection_id': 3, 'from_node': '0x13997acbce0', 'to_node': '0x13997acab10', 'mapping': {'load_path': 'load_data_path'}}, {'connection_id': 4, 'from_node': '0x13997acab10', 'to_node': '0x13997acb490', 'mapping': {'load_profile': 'load_profile'}}, {'connection_id': 5, 'from_node': '0x13997acad70', 'to_node': '0x13997acafd0', 'mapping': {'pv_path': 'pv_data_path'}}, {'connection_id': 6, 'from_node': '0x13997acafd0', 'to_node': '0x13997acb490', 'mapping': {'pv_profile': 'pv_profile'}}, {'connection_id': 7, 'from_node': '0x13997acb100', 'to_node': '0x13997acb360', 'mapping': {'rate_path': 'rate_path'}}, {'connection_id': 8, 'from_node': '0x13997acb360', 'to_node': '0x13997acb490', 'mapping': {'rate_structure': 'rate_structure'}}, {'connection_id': 9, 'from_node': '0x13997acb820', 'to_node': '0x13997acb490', 'mapping': {'ess_parameters': 'ess_parameters'}}, {'connection_id': 10, 'from_node': '0x13997acb490', 'to_node': '0x13997acb5c0', 'mapping': {'btm_op_request': 'btm_op_request'}}, {'connection_id': 11, 'from_node': '0x13997acbbb0', 'to_node': '0x13997acb5c0', 'mapping': {'solver_name': 'solver_name'}}, {'connection_id': 12, 'from_node': '0x13997acb5c0', 'to_node': '0x13997acbe10', 'mapping': {'btm_solved_ops': 'solved_ops'}}, {'connection_id': 13, 'from_node': '0x13997acb6f0', 'to_node': '0x13997acb820', 'mapping': {'power': 'power'}}, {'connection_id': 14, 'from_node': '0x13997acb950', 'to_node': '0x13997acb820', 'mapping': {'energy': 'energy'}}, {'connection_id': 15, 'from_node': '0x13997acba80', 'to_node': '0x13997acb820', 'mapping': {'rte': 'rte'}}, {'connection_id': 16, 'from_node': '0x1399cb2c050', 'to_node': '0x13997acbe10', 'mapping': {'rs_location': 'saved_location'}}])
    subflow_inputs_df = normalize_subflow_inputs([{'name': 'Subcase 0', 'inputs': [{'node_id': '0x13997aca9e0', 'node_name': 'data_location', 'variable_name': 'data_path', 'value': '"/data/"', 'is_path': True, 'is_from_master': False}, {'node_id': '0x13997acb950', 'node_name': 'energy_capacity', 'variable_name': 'energy', 'value': '400', 'is_path': False, 'is_from_master': False}, {'node_id': '0x13997acbce0', 'node_name': 'load_path', 'variable_name': 'load_path', 'value': '', 'is_path': True, 'is_from_master': True}, {'node_id': '0x13997acb6f0', 'node_name': 'power_rating', 'variable_name': 'power', 'value': '100', 'is_path': False, 'is_from_master': False}, {'node_id': '0x13997acad70', 'node_name': 'pv_path', 'variable_name': 'pv_path', 'value': '', 'is_path': True, 'is_from_master': True}, {'node_id': '0x13997acb100', 'node_name': 'rate_path1', 'variable_name': 'rate_path', 'value': '', 'is_path': True, 'is_from_master': True}, {'node_id': '0x1399cb2c050', 'node_name': 'results_location', 'variable_name': 'rs_location', 'value': '"./results/workspace"', 'is_path': True, 'is_from_master': False}, {'node_id': '0x13997acba80', 'node_name': 'rte', 'variable_name': 'rte', 'value': '0.88', 'is_path': False, 'is_from_master': False}, {'node_id': '0x13997acbbb0', 'node_name': 'solver', 'variable_name': 'solver_name', 'value': '"glpk"', 'is_path': False, 'is_from_master': False}]}, {'name': 'Subcase 1', 'inputs': [{'node_id': '0x13997aca9e0', 'node_name': 'data_location', 'variable_name': 'data_path', 'value': '"/data/"', 'is_path': True, 'is_from_master': False}, {'node_id': '0x13997acb950', 'node_name': 'energy_capacity', 'variable_name': 'energy', 'value': '800', 'is_path': False, 'is_from_master': False}, {'node_id': '0x13997acbce0', 'node_name': 'load_path', 'variable_name': 'load_path', 'value': '', 'is_path': True, 'is_from_master': True}, {'node_id': '0x13997acb6f0', 'node_name': 'power_rating', 'variable_name': 'power', 'value': '100', 'is_path': False, 'is_from_master': False}, {'node_id': '0x13997acad70', 'node_name': 'pv_path', 'variable_name': 'pv_path', 'value': '', 'is_path': True, 'is_from_master': True}, {'node_id': '0x13997acb100', 'node_name': 'rate_path1', 'variable_name': 'rate_path', 'value': '', 'is_path': True, 'is_from_master': True}, {'node_id': '0x1399cb2c050', 'node_name': 'results_location', 'variable_name': 'rs_location', 'value': '"./results/workspace"', 'is_path': True, 'is_from_master': False}, {'node_id': '0x13997acba80', 'node_name': 'rte', 'variable_name': 'rte', 'value': '0.88', 'is_path': False, 'is_from_master': False}, {'node_id': '0x13997acbbb0', 'node_name': 'solver', 'variable_name': 'solver_name', 'value': '"glpk"', 'is_path': False, 'is_from_master': False}]}])
    subflow_inputs_df = apply_master_inputs_to_subflow_inputs(subflow_inputs_df, pv_path=pv_path, rate_path1=rate_path1, load_path=load_path)
    subcase_names = [str(case_info.get('name', '') or '').strip() or f'Subcase {index}' for index, case_info in enumerate(subflow_inputs_df)]
    case_results = {}
    for subcase_name in subcase_names:
        print(f"\033[94mRun {subflow_name}'s {subcase_name}\033[0m")
        case_results[subcase_name] = run_subflow(
            subflow_name,
            subflow_nodes_df.copy(deep=True),
            subflow_connections_df.copy(deep=True),
            subflow_inputs_df,
            input_case=subcase_name,
            python_executable='C:/work/quest210_env/Lib/site-packages/quest/app_envs/env_btm/Scripts/python.exe'
        )
    has_multiple_subcases = len(subcase_names) > 1
    return {
        'saved_location': ({subcase_name: case_results.get(subcase_name, {}).get('results', {}).get('saved_location') for subcase_name in subcase_names} if has_multiple_subcases else case_results.get(subcase_names[0], {}).get('results', {}).get('saved_location')),
        'checkpoints': ({subcase_name: case_results.get(subcase_name, {}).get('results', {}).get('checkpoints') for subcase_name in subcase_names} if has_multiple_subcases else case_results.get(subcase_names[0], {}).get('results', {}).get('checkpoints')),
    }

# Instantiations
node0x13997a23cb0=data_node(node_name='pv_path')
node0x13997b979d0=data_node(node_name='rate_path')
node0x13997b97750=data_node(node_name='load_path')
node0x139e9263230=python_node(node_name='btm_flow_2026_new',function=btm_flow_2026_new_function)

# Set inputs
node0x13997a23cb0.set_inputs(pv_path="C:/work/quest20c/quest2/ZeroPV1.json")
node0x13997b979d0.set_inputs(rate_path="C:/work/quest20c/quest2/Dominion1MWtou.json")
node0x13997b97750.set_inputs(load_path="C:/work/quest20c/quest2/data_center_virginia_10MW.csv")

# Connections
node0x13997a23cb0.connect_to(to_node_list=[node0x139e9263230], mapping=[{'pv_path': 'pv_path'}])
node0x13997b979d0.connect_to(to_node_list=[node0x139e9263230], mapping=[{'rate_path': 'rate_path1'}])
node0x13997b97750.connect_to(to_node_list=[node0x139e9263230], mapping=[{'load_path': 'load_path'}])

# Get Outputs
print('pv_path_outputs:',node0x13997a23cb0.get_outputs())
print('rate_path_outputs:',node0x13997b979d0.get_outputs())
print('load_path_outputs:',node0x13997b97750.get_outputs())
print('btm_flow_2026_new_outputs:',node0x139e9263230.get_outputs())