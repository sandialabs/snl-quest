import ast
import json
import os
import re
import shutil
import tempfile
import time


def _get_selected_single_node(workflow):
    return list(workflow.graph.selected_nodes()) if getattr(workflow, "graph", None) is not None else []


def _all_graph_nodes(workflow):
    graph = getattr(workflow, "graph", None)
    if graph is None:
        return []
    try:
        return list(graph.all_nodes())
    except Exception:
        return []


def _node_identity(node):
    try:
        node_id = str(getattr(node, "id", "") or "").strip()
    except Exception:
        node_id = ""
    if node_id:
        return node_id
    return f"object:{id(node)}"


def _sanitize_created_node_name(workflow, node_type, requested_name, node):
    name = str(requested_name or "").strip()
    if not name:
        return ""
    if node_type == "data" and hasattr(workflow, "_sanitize_data_node_name"):
        return workflow._sanitize_data_node_name(name, exclude_node=node)
    if node_type == "py" and hasattr(workflow, "_sanitize_python_node_name"):
        return workflow._sanitize_python_node_name(name, fallback="py_node", exclude_node=node)
    return name


def _normalize_wrapper_function_name(node_name, wrapper_text):
    expected_name = f"{str(node_name or '').strip()}_function"
    source = str(wrapper_text or "")
    if not expected_name or not source.strip():
        return source
    pattern = re.compile(r"(^\s*def\s+)([A-Za-z_]\w*)(\s*\()", re.MULTILINE)
    if pattern.search(source):
        return pattern.sub(rf"\1{expected_name}\3", source, count=1)
    return source


def _sync_py_node_ports_from_wrapper(node):
    if node is None:
        return False
    wrapper_text = str(getattr(node, "node_function_wrapper", "") or "").strip()
    if not wrapper_text:
        return False
    try:
        parsed_ast = ast.parse(wrapper_text)
    except Exception:
        return False

    func_defs = [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]
    func_def = func_defs[0] if func_defs else None
    if func_def is None:
        return False

    input_ports = [arg.arg for arg in list(func_def.args.args or []) if str(getattr(arg, "arg", "") or "").strip()]
    output_ports = []
    for fc in ast.walk(func_def):
        if isinstance(fc, ast.Return) and isinstance(fc.value, ast.Dict):
            for key in list(fc.value.keys or []):
                if isinstance(key, ast.Constant):
                    text = str(key.value or "").strip()
                elif isinstance(key, ast.Str):
                    text = str(key.s or "").strip()
                else:
                    text = ""
                if text:
                    output_ports.append(text)
            break

    try:
        existing_inputs = list(node.inputs().keys())
    except Exception:
        existing_inputs = []
    try:
        existing_outputs = list(node.outputs().keys())
    except Exception:
        existing_outputs = []

    desired_inputs = []
    for port_name in input_ports:
        if port_name not in desired_inputs:
            desired_inputs.append(port_name)

    desired_outputs = []
    for port_name in output_ports:
        if port_name not in desired_outputs:
            desired_outputs.append(port_name)

    try:
        for in_port_name in existing_inputs:
            if in_port_name not in desired_inputs:
                for connected_port in list(node.inputs()[in_port_name].connected_ports()):
                    node.inputs()[in_port_name].disconnect_from(connected_port)
                node.delete_input(in_port_name)
        for port_name in desired_inputs:
            if port_name not in existing_inputs:
                node.add_dynamic_input(port_name)

        for out_port_name in existing_outputs:
            if out_port_name not in desired_outputs:
                for connected_port in list(node.outputs()[out_port_name].connected_ports()):
                    node.outputs()[out_port_name].disconnect_from(connected_port)
                node.delete_output(out_port_name)
        for port_name in desired_outputs:
            if port_name not in existing_outputs:
                node.add_dynamic_output(port_name)
    except Exception:
        return False
    return True


def _apply_initial_node_content(workflow, node, node_type, action):
    if node is None:
        return
    requested_name = str(action.get("name", "") or "").strip()
    sanitized_name = _sanitize_created_node_name(workflow, node_type, requested_name, node)
    old_name = ""
    try:
        if hasattr(node, "name"):
            old_name = str(node.name() or "").strip()
    except Exception:
        old_name = ""
    if sanitized_name and hasattr(node, "set_name"):
        try:
            node.set_name(sanitized_name)
        except Exception:
            pass
        if node_type == "py" and old_name and sanitized_name != old_name:
            try:
                if hasattr(workflow, "_rename_pynode_notebook_and_wrapper"):
                    workflow._rename_pynode_notebook_and_wrapper(node, old_name, sanitized_name)
            except Exception:
                pass

    if node_type in {"data", "py"}:
        variable_name = str(action.get("variable_name", "") or "").strip()
        if variable_name:
            node.node_input_variable = variable_name
        if "value" in action:
            node.node_input_value = str(action.get("value", "") or "")
        if "value_display" in action:
            node.node_value_display = bool(action.get("value_display", False))
        if "is_path" in action:
            node.node_is_path = bool(action.get("is_path", False))
        try:
            widget = node.get_widget('Text Caption')
        except Exception:
            widget = None
        if widget is not None:
            try:
                widget.set_value(node.node_input_value if bool(getattr(node, "node_value_display", False)) else "")
            except Exception:
                pass
        if node_type == "py":
            imports_text = str(action.get("imports", "") or "")
            wrapper_text = str(action.get("wrapper", "") or "")
            code_text = str(action.get("code", "") or "")
            if code_text and not wrapper_text:
                wrapper_text = code_text
            actual_node_name = ""
            try:
                if hasattr(node, "name"):
                    actual_node_name = str(node.name() or "").strip()
            except Exception:
                actual_node_name = ""
            if wrapper_text and actual_node_name:
                wrapper_text = _normalize_wrapper_function_name(actual_node_name, wrapper_text)
            if imports_text:
                try:
                    node.node_imports = imports_text
                except Exception:
                    pass
            if wrapper_text:
                try:
                    node.node_function_wrapper = wrapper_text
                except Exception:
                    pass
    elif node_type == "text":
        text = str(action.get("text", "") or action.get("value", "") or "")
        if text:
            try:
                node.node_input_value = text
            except Exception:
                pass
            try:
                node.set_text(text=text)
            except Exception:
                pass


def _sync_created_node_ui_state(workflow, node, node_type):
    if workflow is None or node is None:
        return
    try:
        graph = getattr(workflow, "graph", None)
        if graph is not None:
            for existing_node in list(graph.selected_nodes()):
                try:
                    existing_node.set_selected(False)
                except Exception:
                    pass
        node.set_selected(True)
    except Exception:
        pass

    try:
        if hasattr(workflow, "on_node_selected"):
            workflow.on_node_selected()
    except Exception:
        pass

    if node_type == "data":
        try:
            if hasattr(workflow, "update_ports"):
                workflow.update_ports()
        except Exception:
            pass
    elif node_type == "py":
        try:
            has_seeded_code = bool(
                str(getattr(node, "node_imports", "") or "").strip()
                or str(getattr(node, "node_function_wrapper", "") or "").strip()
            )
        except Exception:
            has_seeded_code = False
        if has_seeded_code:
            try:
                _sync_py_node_ports_from_wrapper(node)
            except Exception:
                pass
            try:
                if hasattr(workflow, "_refresh_notebook_from_node_json"):
                    workflow._refresh_notebook_from_node_json(node)
            except Exception:
                pass
            try:
                if hasattr(workflow, "notebook_preview"):
                    imports_text = str(getattr(node, "node_imports", "") or "").strip()
                    wrapper_text = str(getattr(node, "node_function_wrapper", "") or "").strip()
                    code_parts = []
                    if imports_text:
                        code_parts.append(imports_text)
                    if wrapper_text:
                        code_parts.append(wrapper_text)
                    workflow.notebook_preview.setPlainText("\n\n".join(code_parts).strip())
            except Exception:
                pass
            try:
                if hasattr(workflow, "update_ports"):
                    workflow.update_ports()
            except Exception:
                pass


def _find_node_by_name(workflow, node_name):
    target_name = str(node_name or "").strip()
    if not target_name:
        return None
    graph = getattr(workflow, "graph", None)
    if graph is None:
        return None
    try:
        all_nodes = list(graph.all_nodes())
    except Exception:
        all_nodes = []
    target_key = target_name.casefold()
    normalized_target_keys = {target_key}
    try:
        if hasattr(workflow, "_sanitize_python_identifier"):
            normalized_target_keys.add(
                str(workflow._sanitize_python_identifier(target_name, fallback="node", suffix="node") or "").strip().casefold()
            )
    except Exception:
        pass
    try:
        if hasattr(workflow, "_sanitize_data_output_name"):
            normalized_target_keys.add(
                str(workflow._sanitize_data_output_name(target_name) or "").strip().casefold()
            )
    except Exception:
        pass
    for node in all_nodes:
        try:
            current_name = str(node.name() or "").strip()
        except Exception:
            current_name = ""
        if current_name.casefold() in normalized_target_keys:
            return node
    return None


def _record_created_node_alias(alias_map, requested_name, node):
    if not isinstance(alias_map, dict) or node is None:
        return
    keys = []
    requested_text = str(requested_name or "").strip()
    if requested_text:
        keys.append(requested_text.casefold())
    try:
        actual_name = str(node.name() or "").strip()
    except Exception:
        actual_name = ""
    if actual_name:
        keys.append(actual_name.casefold())
    for key in keys:
        if key:
            alias_map[key] = node


def _resolve_action_node(workflow, alias_map, node_name):
    lookup_name = str(node_name or "").strip()
    if not lookup_name:
        return None
    if isinstance(alias_map, dict):
        aliased = alias_map.get(lookup_name.casefold())
        if aliased is not None:
            return aliased
    return _find_node_by_name(workflow, lookup_name)


def _apply_existing_node_update(workflow, node, action):
    if workflow is None or node is None:
        return False, "update_node requires a resolvable target node."
    item = dict(action or {})
    requested_type = str(item.get("node_type", "") or "").strip().lower()
    actual_type = ""
    try:
        class_name = str(getattr(node, "__class__", type(node)).__name__ or "").strip()
        if class_name == "DataNode":
            actual_type = "data"
        elif class_name == "PyNode":
            actual_type = "py"
        elif class_name == "BackNode":
            actual_type = "text"
    except Exception:
        actual_type = ""
    effective_type = actual_type or requested_type
    if requested_type and actual_type and requested_type != actual_type:
        return False, f"update_node expected a {requested_type} node but found {actual_type}."

    new_name = str(item.get("new_name", "") or "").strip()
    if new_name:
        old_name = ""
        try:
            if hasattr(node, "name"):
                old_name = str(node.name() or "").strip()
        except Exception:
            old_name = ""
        sanitized_name = _sanitize_created_node_name(workflow, effective_type, new_name, node)
        if sanitized_name and hasattr(node, "set_name"):
            try:
                node.set_name(sanitized_name)
            except Exception:
                pass
            if effective_type == "py" and old_name and sanitized_name != old_name:
                try:
                    if hasattr(workflow, "_rename_pynode_notebook_and_wrapper"):
                        workflow._rename_pynode_notebook_and_wrapper(node, old_name, sanitized_name)
                except Exception:
                    pass

    if effective_type in {"data", "py"}:
        if "variable_name" in item:
            try:
                node.node_input_variable = str(item.get("variable_name", "") or "").strip()
            except Exception:
                pass
        if "value" in item:
            try:
                node.node_input_value = str(item.get("value", "") or "")
            except Exception:
                pass
        if "value_display" in item:
            try:
                node.node_value_display = bool(item.get("value_display", False))
            except Exception:
                pass
        if "is_path" in item:
            try:
                node.node_is_path = bool(item.get("is_path", False))
            except Exception:
                pass
        try:
            widget = node.get_widget('Text Caption')
        except Exception:
            widget = None
        if widget is not None:
            try:
                widget.set_value(node.node_input_value if bool(getattr(node, "node_value_display", False)) else "")
            except Exception:
                pass
        if effective_type == "py":
            imports_text = str(item.get("imports", "") or "")
            wrapper_text = str(item.get("wrapper", "") or "")
            code_text = str(item.get("code", "") or "")
            if code_text and not wrapper_text:
                wrapper_text = code_text
            actual_node_name = ""
            try:
                if hasattr(node, "name"):
                    actual_node_name = str(node.name() or "").strip()
            except Exception:
                actual_node_name = ""
            if wrapper_text and actual_node_name:
                wrapper_text = _normalize_wrapper_function_name(actual_node_name, wrapper_text)
            if imports_text:
                try:
                    node.node_imports = imports_text
                except Exception:
                    pass
            if wrapper_text:
                try:
                    node.node_function_wrapper = wrapper_text
                except Exception:
                    pass
    elif effective_type == "text" and "text" in item:
        text = str(item.get("text", "") or "")
        try:
            node.node_input_value = text
        except Exception:
            pass
        try:
            node.set_text(text=text)
        except Exception:
            pass

    _sync_created_node_ui_state(workflow, node, effective_type)
    return True, ""


def _load_workflow_json_into_current_workflow(workflow, action):
    if workflow is None:
        return False, "load_workflow_json requires an active workflow."

    workflow_path = str(dict(action or {}).get("workflow_path", "") or "").strip()
    workflow_content = dict(action.get("workflow_content", {}) or {}) if isinstance(action.get("workflow_content"), dict) else {}
    source_skill_id = str(dict(action or {}).get("source_skill_id", "") or "").strip()
    loaded_from_content = False

    if workflow_path:
        normalized_path = os.path.normpath(workflow_path)
        if source_skill_id:
            try:
                source_path = os.path.abspath(normalized_path)
                working_dir = os.path.join(tempfile.gettempdir(), "quest_skill_template_working_copies")
                os.makedirs(working_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(source_path))[0] or "workflow_template"
                safe_skill_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", source_skill_id).strip("_") or "skill"
                copy_name = f"{safe_skill_id}_{base_name}_{int(time.time() * 1000)}.json"
                working_path = os.path.join(working_dir, copy_name)
                shutil.copy2(source_path, working_path)
                normalized_path = os.path.normpath(working_path)
                action["workflow_path"] = normalized_path
                action["source_workflow_path"] = source_path
            except Exception as exc:
                return False, f"load_workflow_json failed to copy skill template before loading '{workflow_path}': {exc}"
        try:
            with open(normalized_path, "r", encoding="utf-8") as handle:
                flow_json_data = json.load(handle)
        except Exception as exc:
            return False, f"load_workflow_json failed to read '{workflow_path}': {exc}"
    elif workflow_content:
        normalized_path = ""
        flow_json_data = workflow_content
        loaded_from_content = True
    else:
        return False, "load_workflow_json requires workflow_path or workflow_content."

    if not isinstance(flow_json_data, dict):
        return False, "load_workflow_json requires a workflow JSON object."
    flow_json_data = _normalize_workflow_json_payload(flow_json_data)
    if not isinstance(flow_json_data, dict):
        return False, "load_workflow_json requires a workflow JSON object."
    if "nodes_df" not in flow_json_data or "flow_layout" not in flow_json_data:
        return False, "load_workflow_json requires workflow JSON with nodes_df and flow_layout."

    has_subflows = isinstance(flow_json_data.get("subflows_df"), list) and len(flow_json_data.get("subflows_df", []) or []) > 0
    requested_flow_type = _infer_workflow_json_flow_type(flow_json_data, has_subflows=has_subflows)
    flow_json_data["flow_type"] = requested_flow_type
    if loaded_from_content:
        try:
            normalized_path = _write_workflow_content_working_copy(flow_json_data, source_skill_id)
            action["workflow_path"] = normalized_path
            action["workflow_content_path"] = normalized_path
        except Exception as exc:
            return False, f"load_workflow_json failed to save adapted workflow JSON before loading: {exc}"

    parent_workspace = workflow._find_workspace_parent() if hasattr(workflow, "_find_workspace_parent") else None
    is_master_context = parent_workspace is not None and getattr(parent_workspace, "master_workflow", None) is workflow
    target_workflow = workflow

    try:
        if requested_flow_type == "master-flow" and has_subflows:
            if parent_workspace is not None and getattr(parent_workspace, "master_workflow", None) is not None:
                target_workflow = parent_workspace.master_workflow
                is_master_context = True
            if not is_master_context or parent_workspace is None or not hasattr(parent_workspace, "_load_master_flow_json_data"):
                return False, "load_workflow_json cannot load a master flow with subflows into the current tab."
            parent_workspace._load_master_flow_json_data(flow_json_data, normalized_path or "")
        else:
            workspace_tabs = getattr(parent_workspace, "tab_widget", None) if parent_workspace is not None else None
            if requested_flow_type == "sub-flow" and parent_workspace is not None and getattr(parent_workspace, "master_workflow", None) is workflow and getattr(workspace_tabs, "currentWidget", lambda: None)() is getattr(parent_workspace, "master_tab", None):
                if hasattr(parent_workspace, "_clear_all_subflows"):
                    parent_workspace._clear_all_subflows()
                workflow._deserialize_flow_json_data(flow_json_data)
                if hasattr(workflow, "set_flow_type"):
                    workflow.set_flow_type("master-flow")
            else:
                workflow._deserialize_flow_json_data(flow_json_data)

        if normalized_path and hasattr(target_workflow, "_set_current_flow_json_path"):
            target_workflow._set_current_flow_json_path(normalized_path)
        if normalized_path and hasattr(target_workflow, "_set_quest_agent_current_flow_attachment"):
            target_workflow._set_quest_agent_current_flow_attachment(normalized_path)
        if hasattr(target_workflow, "_refresh_notebook_ui_after_file_load"):
            target_workflow._refresh_notebook_ui_after_file_load()
        if parent_workspace is not None and hasattr(parent_workspace, "sync_workflow_ui"):
            parent_workspace.sync_workflow_ui(target_workflow)
        return True, ""
    except Exception as exc:
        return False, f"load_workflow_json failed: {exc}"


def _infer_workflow_json_flow_type(flow_json_data, has_subflows=False):
    requested_flow_type = str(dict(flow_json_data or {}).get("flow_type", "") or "").strip().lower()
    if requested_flow_type in {"master-flow", "master_flow", "master"}:
        return "master-flow"
    if requested_flow_type in {"sub-flow", "sub_flow", "subflow", "sub"}:
        return "sub-flow"
    return "master-flow" if has_subflows else "sub-flow"


def _write_workflow_content_working_copy(flow_json_data, source_skill_id=""):
    working_dir = os.path.join(tempfile.gettempdir(), "quest_skill_template_working_copies")
    os.makedirs(working_dir, exist_ok=True)
    safe_skill_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(source_skill_id or "")).strip("_") or "adapted_workflow"
    flow_name = str(dict(flow_json_data or {}).get("flow_name", "") or "").strip() or "workflow_content"
    safe_flow_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", flow_name).strip("_") or "workflow_content"
    copy_name = f"{safe_skill_id}_{safe_flow_name}_{int(time.time() * 1000)}.json"
    working_path = os.path.normpath(os.path.join(working_dir, copy_name))
    with open(working_path, "w", encoding="utf-8") as handle:
        json.dump(flow_json_data, handle, ensure_ascii=False, indent=2)
    return working_path


def _normalize_workflow_json_payload(flow_json_data):
    data = dict(flow_json_data or {})
    if "nodes_df" in data and "flow_layout" in data:
        return data
    for key in ("workflow_content", "workflow_template", "workflow_json", "flow_json", "template", "content"):
        value = data.get(key)
        if isinstance(value, dict):
            normalized = _normalize_workflow_json_payload(value)
            if "nodes_df" in normalized and "flow_layout" in normalized:
                return normalized
    if isinstance(data.get("workflow"), dict):
        normalized = _normalize_workflow_json_payload(data.get("workflow"))
        if "nodes_df" in normalized and "flow_layout" in normalized:
            return normalized
    return data


def _resolve_port(port_dict, requested_name):
    if not isinstance(port_dict, dict) or not port_dict:
        return None, ""
    port_name = str(requested_name or "").strip()
    if port_name:
        for existing_name, port in port_dict.items():
            existing_text = str(existing_name or "").strip()
            if existing_text == port_name or existing_text.casefold() == port_name.casefold():
                return port, existing_text
        return None, port_name
    if len(port_dict) == 1:
        only_name = next(iter(port_dict.keys()))
        return port_dict[only_name], str(only_name or "").strip()
    return None, ""


def _iter_connect_mappings(action):
    mapping = action.get("mapping")
    if isinstance(mapping, dict):
        for source_port, target_port in mapping.items():
            yield str(source_port or "").strip(), str(target_port or "").strip()
        return
    if isinstance(mapping, list):
        for item in mapping:
            if not isinstance(item, dict):
                continue
            source_port = str(
                item.get("source_port", "")
                or item.get("from_port", "")
                or item.get("output_port", "")
                or ""
            ).strip()
            target_port = str(
                item.get("target_port", "")
                or item.get("to_port", "")
                or item.get("input_port", "")
                or ""
            ).strip()
            if source_port or target_port:
                yield source_port, target_port
        return
    yield (
        str(action.get("source_port", "") or action.get("from_port", "") or action.get("output_port", "") or "").strip(),
        str(action.get("target_port", "") or action.get("to_port", "") or action.get("input_port", "") or "").strip(),
    )


def _connect_nodes(workflow, action, created_node_aliases=None):
    source_name = str(
        action.get("source_node", "")
        or action.get("from_node", "")
        or ""
    ).strip()
    target_name = str(
        action.get("target_node", "")
        or action.get("to_node", "")
        or ""
    ).strip()
    if not source_name or not target_name:
        return ""

    source_node = _resolve_action_node(workflow, created_node_aliases, source_name)
    target_node = _resolve_action_node(workflow, created_node_aliases, target_name)
    if source_node is None or target_node is None:
        return ""

    try:
        source_ports = dict(source_node.outputs())
    except Exception:
        source_ports = {}
    try:
        target_ports = dict(target_node.inputs())
    except Exception:
        target_ports = {}

    connected_pairs = []
    for source_port_name, target_port_name in _iter_connect_mappings(action):
        source_port, resolved_source_name = _resolve_port(source_ports, source_port_name)
        target_port, resolved_target_name = _resolve_port(target_ports, target_port_name)
        if source_port is None or target_port is None:
            continue
        try:
            source_port.connect_to(target_port)
        except Exception:
            continue
        connected_pairs.append((resolved_source_name, resolved_target_name))

    if not connected_pairs:
        return ""
    if len(connected_pairs) == 1:
        source_port_name, target_port_name = connected_pairs[0]
        return f"Connected {source_name}.{source_port_name} to {target_name}.{target_port_name}."
    mapping_text = ", ".join(f"{left}->{right}" for left, right in connected_pairs)
    return f"Connected {source_name} to {target_name} with mappings: {mapping_text}."


def execute_canvas_actions(workflow, action_plan):
    actions = list(dict(action_plan or {}).get("actions", []) or [])
    if workflow is None or not actions:
        return []

    action_plan.setdefault("execution_notes", [])
    executed = []
    current_workflow = workflow
    created_node_aliases = {}
    touched_workflows = []
    for action in actions:
        action_type = str(action.get("type", "") or "").strip()
        if action_type == "create_node":
            node_type = str(action.get("node_type", "") or "").strip().lower()
            count = max(1, min(5, int(action.get("count", 1) or 1)))
            creator = None
            if node_type == "data":
                creator = getattr(current_workflow, "create_data_node", None)
            elif node_type == "py":
                creator = getattr(current_workflow, "create_py_node", None)
            elif node_type == "text":
                creator = getattr(current_workflow, "create_text_node", None)
            if creator is None:
                action_plan["execution_notes"].append(f"No canvas creator exists for node type '{node_type}'.")
                continue
            created_names = []
            success_count = 0
            for _ in range(count):
                before_nodes = _all_graph_nodes(current_workflow)
                before_ids = {_node_identity(node) for node in before_nodes}
                creator_error = None
                try:
                    creator()
                except Exception as exc:
                    creator_error = exc
                after_nodes = _all_graph_nodes(current_workflow)
                new_nodes = [node for node in after_nodes if _node_identity(node) not in before_ids]
                node = new_nodes[-1] if new_nodes else None
                if node is not None:
                    success_count += 1
                    _apply_initial_node_content(current_workflow, node, node_type, action)
                    _sync_created_node_ui_state(current_workflow, node, node_type)
                    _record_created_node_alias(created_node_aliases, action.get("name", ""), node)
                    try:
                        created_names.append(str(node.name() or "").strip())
                    except Exception:
                        pass
                    if creator_error is not None:
                        action_plan["execution_notes"].append(
                            f"{node_type} node creation raised after the node appeared on canvas: {creator_error}"
                        )
                elif creator_error is not None:
                    action_plan["execution_notes"].append(
                        f"{node_type} node creation failed before a node was added: {creator_error}"
                    )
                else:
                    action_plan["execution_notes"].append(
                        f"{node_type} node creation did not change the canvas."
                    )
            if success_count > 0 and created_names:
                if current_workflow not in touched_workflows:
                    touched_workflows.append(current_workflow)
                executed.append(
                    f"Created {success_count} {node_type} node{'s' if success_count != 1 else ''}: {', '.join(name for name in created_names if name)}."
                )
            elif success_count > 0:
                if current_workflow not in touched_workflows:
                    touched_workflows.append(current_workflow)
                executed.append(f"Created {success_count} {node_type} node{'s' if success_count != 1 else ''}.")
        elif action_type == "update_node":
            target_name = str(action.get("node_name", "") or "").strip()
            target_node = _resolve_action_node(current_workflow, created_node_aliases, target_name)
            if target_node is None:
                action_plan["execution_notes"].append(f"update_node could not resolve node {target_name or '<missing>'}.")
                continue
            updated_ok, update_note = _apply_existing_node_update(current_workflow, target_node, action)
            if not updated_ok:
                action_plan["execution_notes"].append(update_note or "update_node could not apply the requested changes.")
                continue
            if current_workflow not in touched_workflows:
                touched_workflows.append(current_workflow)
            try:
                actual_name = str(target_node.name() or "").strip() or target_name
            except Exception:
                actual_name = target_name
            executed.append(f"Updated node {actual_name}.")
        elif action_type == "add_subflow":
            parent_workspace = current_workflow._find_workspace_parent() if hasattr(current_workflow, "_find_workspace_parent") else None
            if parent_workspace is None:
                action_plan["execution_notes"].append("add_subflow requires a workspace parent.")
                continue
            requested_name = str(
                action.get("flow_name", "")
                or action.get("subflow_name", "")
                or action.get("name", "")
                or ""
            ).strip()
            created_workflow = None
            try:
                if hasattr(parent_workspace, "create_subflow_for_agent"):
                    created_workflow = parent_workspace.create_subflow_for_agent(title=requested_name or None)
                elif hasattr(parent_workspace, "create_workflow_tab"):
                    created_workflow = parent_workspace.create_workflow_tab(title=requested_name or None, create_proxy=True)
            except Exception as exc:
                action_plan["execution_notes"].append(f"add_subflow failed: {exc}")
                created_workflow = None
            if created_workflow is None:
                action_plan["execution_notes"].append("add_subflow did not create a workflow tab.")
                continue
            actual_name = requested_name
            try:
                if hasattr(created_workflow, "get_flow_display_name"):
                    actual_name = str(created_workflow.get_flow_display_name() or "").strip() or actual_name
            except Exception:
                pass
            current_workflow = created_workflow
            created_node_aliases = {}
            if current_workflow not in touched_workflows:
                touched_workflows.append(current_workflow)
            executed.append(f"Created subflow {actual_name or 'Workflow'}.")
        elif action_type == "rename_selected_node":
            selected_nodes = list(current_workflow.graph.selected_nodes()) if getattr(current_workflow, "graph", None) is not None else []
            if len(selected_nodes) != 1:
                action_plan["execution_notes"].append("rename_selected_node requires exactly one selected node.")
                continue
            new_name = str(action.get("new_name", "") or "").strip()
            if not new_name:
                action_plan["execution_notes"].append("rename_selected_node was missing new_name.")
                continue
            if hasattr(current_workflow, "name_input"):
                current_workflow.name_input.setText(new_name)
            current_workflow.update_node_name()
            if current_workflow not in touched_workflows:
                touched_workflows.append(current_workflow)
            executed.append(f"Renamed the selected node to {new_name}.")
        elif action_type == "update_selected_text_node":
            selected_nodes = list(current_workflow.graph.selected_nodes()) if getattr(current_workflow, "graph", None) is not None else []
            if len(selected_nodes) != 1:
                action_plan["execution_notes"].append("update_selected_text_node requires exactly one selected node.")
                continue
            node = selected_nodes[0]
            node_type_name = str(getattr(node, "__class__", type(node)).__name__ or "").strip()
            if node_type_name != "BackNode":
                action_plan["execution_notes"].append("update_selected_text_node requires a selected text node.")
                continue
            text = str(action.get("text", "") or "")
            if hasattr(current_workflow, "text_input"):
                current_workflow.text_input.setPlainText(text)
            current_workflow.update_caption_value()
            if current_workflow not in touched_workflows:
                touched_workflows.append(current_workflow)
            executed.append("Updated the selected text node.")
        elif action_type == "delete_selected_nodes":
            selected_count = len(list(current_workflow.graph.selected_nodes())) if getattr(current_workflow, "graph", None) is not None else 0
            if selected_count <= 0:
                action_plan["execution_notes"].append("delete_selected_nodes requires at least one selected node.")
                continue
            current_workflow._delete_selected_nodes_with_workspace_rules()
            if current_workflow not in touched_workflows:
                touched_workflows.append(current_workflow)
            executed.append(f"Deleted {selected_count} selected node{'s' if selected_count != 1 else ''}.")
        elif action_type == "delete_node":
            node_name = str(action.get("node_name", "") or action.get("name", "") or action.get("target_node", "") or "").strip()
            node = _resolve_action_node(current_workflow, created_node_aliases, node_name)
            graph = getattr(current_workflow, "graph", None)
            if graph is None:
                action_plan["execution_notes"].append("delete_node requires an active workflow graph.")
                continue
            if node is None:
                action_plan["execution_notes"].append(f"delete_node could not resolve node {node_name or '<missing>'}.")
                continue
            previous_selection = []
            try:
                previous_selection = list(graph.selected_nodes())
            except Exception:
                previous_selection = []
            try:
                for selected_node in previous_selection:
                    try:
                        selected_node.set_selected(False)
                    except Exception:
                        pass
                try:
                    node.set_selected(True)
                except Exception:
                    pass
                deleted_ok = False
                if hasattr(current_workflow, "_delete_selected_nodes_with_workspace_rules"):
                    deleted_ok = bool(current_workflow._delete_selected_nodes_with_workspace_rules())
                else:
                    graph.delete_node(node)
                    deleted_ok = True
                if _find_node_by_name(current_workflow, node_name) is not None:
                    action_plan["execution_notes"].append(f"delete_node did not remove node {node_name}.")
                    continue
                if current_workflow not in touched_workflows:
                    touched_workflows.append(current_workflow)
                executed.append(f"Deleted node {node_name}.")
            except Exception as exc:
                action_plan["execution_notes"].append(f"delete_node failed for {node_name or '<missing>'}: {exc}")
                continue
            finally:
                try:
                    for selected_node in list(graph.selected_nodes()):
                        try:
                            selected_node.set_selected(False)
                        except Exception:
                            pass
                    for selected_node in previous_selection:
                        try:
                            if selected_node is not node:
                                selected_node.set_selected(True)
                        except Exception:
                            pass
                except Exception:
                    pass
        elif action_type == "connect_nodes":
            connection_result = _connect_nodes(current_workflow, action, created_node_aliases=created_node_aliases)
            if connection_result:
                if current_workflow not in touched_workflows:
                    touched_workflows.append(current_workflow)
                executed.append(connection_result)
            else:
                action_plan["execution_notes"].append("connect_nodes could not resolve the requested nodes or ports.")
        elif action_type == "load_workflow_json":
            loaded_ok, message = _load_workflow_json_into_current_workflow(current_workflow, action)
            if loaded_ok:
                if current_workflow not in touched_workflows:
                    touched_workflows.append(current_workflow)
                source_skill_id = str(action.get("source_skill_id", "") or "").strip()
                workflow_path = str(action.get("workflow_path", "") or "").strip()
                if hasattr(current_workflow, "_record_quest_agent_skill_action"):
                    try:
                        current_workflow._record_quest_agent_skill_action(
                            scope="flow",
                            action="load_flow",
                            target=str(current_workflow.get_flow_display_name() if hasattr(current_workflow, "get_flow_display_name") else "Current Flow"),
                            details={
                                "path": workflow_path,
                                "source_skill_id": source_skill_id,
                                "flow_type": str(current_workflow.get_flow_type() if hasattr(current_workflow, "get_flow_type") else ""),
                            },
                            workspace_action=dict(action or {}),
                        )
                    except Exception:
                        pass
                if source_skill_id:
                    source_workflow_path = str(action.get("source_workflow_path", "") or "").strip()
                    if source_workflow_path:
                        executed.append(f"Loaded working copy of workflow template from skill {source_skill_id}.")
                    else:
                        executed.append(f"Loaded workflow template from skill {source_skill_id}.")
                elif workflow_path:
                    executed.append(f"Loaded workflow JSON from {workflow_path}.")
                else:
                    executed.append("Loaded drafted workflow JSON into the current flow.")
            else:
                action_plan["execution_notes"].append(message or "load_workflow_json did not load a workflow.")
        else:
            action_plan["execution_notes"].append(f"Unsupported action type reached the executor: {action_type}")

    if executed:
        for touched_workflow in touched_workflows or [current_workflow]:
            try:
                touched_workflow.update_flow()
            except Exception:
                pass
            try:
                if hasattr(touched_workflow, "request_graph_frame"):
                    touched_workflow.request_graph_frame()
            except Exception:
                pass
            try:
                graph = getattr(touched_workflow, "graph", None)
                viewer = graph.viewer() if graph is not None and hasattr(graph, "viewer") else None
                if viewer is not None:
                    try:
                        viewer.force_update()
                    except Exception:
                        pass
                    try:
                        viewer.viewport().update()
                    except Exception:
                        pass
                    try:
                        viewer.scene().update()
                    except Exception:
                        pass
            except Exception:
                pass
        parent_workspace = current_workflow._find_workspace_parent() if hasattr(current_workflow, "_find_workspace_parent") else None
        if parent_workspace is not None and hasattr(parent_workspace, "sync_workflow_ui"):
            try:
                parent_workspace.sync_workflow_ui(current_workflow)
            except Exception:
                pass
    return executed
