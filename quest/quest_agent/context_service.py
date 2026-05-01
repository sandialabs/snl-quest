import ast
import json
import os


def extract_pinned_context(chat_messages):
    pinned_context = []
    for message in list(chat_messages or []):
        if str(message.get("role", "")).strip().lower() != "user":
            continue
        if not bool(message.get("pinned", False)):
            continue
        content = str(message.get("content", "")).strip()
        if content:
            pinned_context.append(content)
    return pinned_context


def get_match_inputs(state, draft_prompt, normalize_path):
    latest_prompt = ""
    pinned_context = []
    for message in list((state or {}).get("chat_messages", [])):
        if str(message.get("role", "")).strip().lower() != "user":
            continue
        content = str(message.get("content", "")).strip()
        if content:
            latest_prompt = content
        if bool(message.get("pinned", False)) and content:
            pinned_context.append(content)
    task_description = str(draft_prompt or "").strip() or latest_prompt
    attached_files = get_effective_context_files(state, normalize_path)
    return task_description, pinned_context, attached_files


def workspace_is_recommended(task_match_results):
    result = dict(task_match_results or {})
    for item in list(result.get("tool_matches", []) or []):
        tool_id = str(item.get("tool_id", "") or "").strip().lower()
        tool_name = str(item.get("name", "") or "").strip().lower()
        if tool_id == "workspace" or tool_name == "workspace":
            return True
    return False


def has_workflow_json_context(state, normalize_path):
    state = dict(state or {})
    current_flow_attachment_path = normalize_path(state.get("current_flow_attachment_path", ""))
    if current_flow_attachment_path:
        return True
    for path in list(state.get("chat_attachments", [])):
        normalized = normalize_path(path)
        if normalized and normalized.lower().endswith(".json"):
            return True
    return False


def get_implicit_context_files(state, normalize_path, workspace_root, task_match_results):
    if not (has_workflow_json_context(state, normalize_path) or workspace_is_recommended(task_match_results)):
        return []
    implicit_paths = [
        os.path.join(workspace_root, "flow", "questflow.py"),
        os.path.join(workspace_root, "nodes", "pynodes.py"),
    ]
    normalized_paths = []
    for path in implicit_paths:
        normalized = normalize_path(path)
        if normalized and os.path.exists(normalized):
            normalized_paths.append(normalized)
    return normalized_paths


def build_code_context_summary(path, normalize_path):
    normalized = normalize_path(path)
    if not normalized or not os.path.exists(normalized):
        return {}
    try:
        with open(normalized, "r", encoding="utf-8") as handle:
            source = handle.read()
        tree = ast.parse(source, filename=normalized)
    except Exception:
        return {}

    file_summary = {
        "file": os.path.basename(normalized),
        "module": os.path.splitext(os.path.basename(normalized))[0],
        "classes": [],
    }

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        base_names = []
        for base in list(node.bases or []):
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                parts = []
                current = base
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                base_names.append(".".join(reversed(parts)))
            else:
                try:
                    base_names.append(ast.unparse(base))
                except Exception:
                    continue

        methods = []
        for child in list(node.body or []):
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            method_name = str(child.name or "").strip()
            if not method_name:
                continue
            if method_name.startswith("_") and method_name not in {"__init__"}:
                continue
            args = []
            positional_args = list(getattr(child.args, "args", []) or [])
            if positional_args and getattr(positional_args[0], "arg", "") == "self":
                positional_args = positional_args[1:]
            for arg in positional_args:
                arg_name = str(getattr(arg, "arg", "") or "").strip()
                if arg_name:
                    args.append(arg_name)
            methods.append({
                "name": method_name,
                "args": args[:6],
            })

        file_summary["classes"].append({
            "name": str(node.name or "").strip(),
            "bases": base_names,
            "methods": methods[:12],
        })

    return file_summary


def get_implicit_code_context(state, normalize_path, workspace_root, task_match_results):
    summaries = []
    for path in get_implicit_context_files(state, normalize_path, workspace_root, task_match_results):
        summary = build_code_context_summary(path, normalize_path)
        if summary and list(summary.get("classes", []) or []):
            summaries.append(summary)
    return summaries


def get_python_node_wrapper_rules(state, normalize_path, workspace_root, task_match_results):
    workspace_root = normalize_path(workspace_root)
    source_paths = []
    for path in [
        os.path.join(workspace_root or "", "app.py"),
        os.path.join(workspace_root or "", "flow", "questflow.py"),
        os.path.join(workspace_root or "", "nodes", "pynodes.py"),
    ]:
        normalized = normalize_path(path)
        if normalized and os.path.exists(normalized):
            source_paths.append(normalized)

    return {
        "available": bool(source_paths),
        "source_files": [os.path.basename(path) for path in source_paths],
        "summary": (
            "Use these rules whenever you explain, generate, or revise a QuESt Python node wrapper. "
            "These rules come from the workspace runtime that parses Python node notebooks and derives ports."
        ),
        "rules": [
            "Write one top-level wrapper function for the node.",
            "Prefer naming the wrapper function exactly <node_name>_function. The runtime looks for that name first.",
            "If no exact <node_name>_function exists, the runtime falls back to the first top-level function it finds.",
            "Input ports are created from the wrapper function argument names, in order.",
            "Output ports are created from the string keys of a returned dictionary literal.",
            "Return a dictionary with stable string keys if you want output ports to appear on the node.",
            "Use normal Python identifiers for function names, argument names, and returned output keys.",
            "Keep imports as ordinary top-level import statements; the runtime extracts them separately from the wrapper function body.",
            "Avoid relying on multiple competing wrapper functions in the same node notebook; one clear wrapper is the safe pattern.",
        ],
        "preferred_template": (
            "def <node_name>_function(input_a, input_b):\n"
            "    result = ...\n"
            "    return {\"output_name\": result}"
        ),
        "notes": [
            "If the wrapper does not return a dictionary literal with string keys, output ports may not be inferred during port refresh.",
            "Renaming a Python node changes the preferred wrapper name to match the new node name.",
        ],
    }


def _normalize_skill_confidence(value):
    try:
        numeric = float(value)
    except Exception:
        return 0.0
    if numeric < 0.0:
        return 0.0
    if numeric > 1.0:
        return 1.0
    return round(numeric, 4)


def _build_skill_workflow_template_context(workflow_json_path, normalize_path, source_name):
    normalized = normalize_path(workflow_json_path)
    if not normalized or not normalized.lower().endswith(".json") or not os.path.exists(normalized):
        return {}
    try:
        with open(normalized, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    context_entry = build_workflow_json_context_entry(data, source_name=source_name)
    if not context_entry:
        return {}
    context_entry["path"] = normalized
    return context_entry


def get_skill_execution_recipes(state, normalize_path):
    state = dict(state or {})
    task_match_results = dict(state.get("task_match_results", {}) or {})
    skill_matches = [dict(item or {}) for item in list(task_match_results.get("skill_matches", []) or [])]
    loaded_skills = list(state.get("loaded_skills", []) or [])
    if not skill_matches or not loaded_skills:
        return {"available": False, "recipes": []}

    skill_lookup = {}
    for skill in loaded_skills:
        skill_id = str(getattr(skill, "skill_id", "") or "").strip()
        if skill_id:
            skill_lookup[skill_id] = skill

    ranked_matches = []
    for item in skill_matches:
        skill_id = str(item.get("skill_id", "") or "").strip()
        if not skill_id or skill_id not in skill_lookup:
            continue
        ranked_matches.append(
            (
                -_normalize_skill_confidence(item.get("confidence", 0.0)),
                str(item.get("title", skill_id) or skill_id).casefold(),
                skill_id,
                item,
            )
        )
    ranked_matches.sort()

    selected_matches = []
    strong_matches = [item for _, _, _, item in ranked_matches if _normalize_skill_confidence(item.get("confidence", 0.0)) >= 0.55]
    if strong_matches:
        selected_matches = strong_matches[:3]
    else:
        selected_matches = [item for _, _, _, item in ranked_matches[:2]]

    recipes = []
    for item in selected_matches:
        skill_id = str(item.get("skill_id", "") or "").strip()
        skill = skill_lookup.get(skill_id)
        if skill is None:
            continue
        raw_data = getattr(skill, "raw_data", {}) or {}
        if not isinstance(raw_data, dict):
            raw_data = {}
        plan = raw_data.get("plan", {}) if isinstance(raw_data.get("plan", {}), dict) else {}
        inputs = raw_data.get("inputs", {}) if isinstance(raw_data.get("inputs", {}), dict) else {}
        validation = raw_data.get("validation", {}) if isinstance(raw_data.get("validation", {}), dict) else {}
        workflow_template = _build_skill_workflow_template_context(
            getattr(skill, "workflow_json_path", ""),
            normalize_path,
            source_name=f"Skill workflow: {getattr(skill, 'title', skill_id)}",
        )
        recipes.append(
            {
                "skill_id": skill_id,
                "title": str(getattr(skill, "title", "") or skill_id).strip(),
                "summary": str(getattr(skill, "summary", "") or "").strip(),
                "skill_type": str(getattr(skill, "skill_type", "") or "").strip(),
                "confidence": _normalize_skill_confidence(item.get("confidence", 0.0)),
                "reason": str(item.get("reason", "") or "").strip(),
                "recommended_tools": [str(value).strip() for value in list(getattr(skill, "recommended_tools", []) or []) if str(value).strip()],
                "required_tools": [str(value).strip() for value in list(getattr(skill, "required_tools", []) or []) if str(value).strip()],
                "workflow_strategy": str(plan.get("workflow_strategy", "") or "").strip(),
                "step_summary": [
                    str(value).strip()
                    for value in list(plan.get("step_summary", []) or [])[:8]
                    if str(value).strip()
                ],
                "expected_inputs": [
                    {
                        "name": str(dict(entry or {}).get("name", "") or "").strip(),
                        "type": str(dict(entry or {}).get("type", "") or "").strip(),
                        "description": str(dict(entry or {}).get("description", "") or "").strip(),
                    }
                    for entry in list(inputs.get("expected_inputs", []) or [])[:6]
                    if str(dict(entry or {}).get("name", "") or "").strip()
                ],
                "validation_criteria": [
                    str(value).strip()
                    for value in list(validation.get("criteria", []) or [])[:8]
                    if str(value).strip()
                ],
                "limitations": [
                    str(value).strip()
                    for value in list(raw_data.get("limitations", []) or [])[:4]
                    if str(value).strip()
                ],
                "workflow_template": workflow_template,
            }
        )

    return {
        "available": bool(recipes),
        "recipes": recipes,
    }


def get_effective_context_files(state, normalize_path):
    effective_paths = []
    seen = set()
    for path in list((state or {}).get("chat_attachments", [])):
        normalized = normalize_path(path)
        normalized_key = os.path.normcase(normalized) if normalized else ""
        if not normalized or normalized_key in seen:
            continue
        seen.add(normalized_key)
        effective_paths.append(normalized)
    return effective_paths


def get_attached_workflow_json_context(state, normalize_path):
    workflow_context = []
    for path in get_effective_context_files(state, normalize_path):
        normalized = normalize_path(path)
        if not normalized or not normalized.lower().endswith(".json") or not os.path.exists(normalized):
            continue
        try:
            with open(normalized, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if not any(key in data for key in ("flow_name", "flow_type", "flow_layout", "nodes_df", "connections_df", "subflows_df")):
            continue
        nodes = list(data.get("nodes_df", []) or [])
        connections = list(data.get("connections_df", []) or [])
        subflows = list(data.get("subflows_df", []) or [])
        workflow_context.append({
            "file": os.path.basename(normalized),
            "flow_name": str(data.get("flow_name", "") or "").strip(),
            "flow_type": str(data.get("flow_type", "") or "").strip(),
            "node_count": len(nodes),
            "connection_count": len(connections),
            "subflow_count": len(subflows),
            "content": data,
        })
    return workflow_context


def build_workflow_json_context_entry(data, source_name="Current Flow on Canvas"):
    if not isinstance(data, dict):
        return {}
    if not any(key in data for key in ("flow_name", "flow_type", "flow_layout", "nodes_df", "connections_df", "subflows_df")):
        return {}
    nodes = list(data.get("nodes_df", []) or [])
    connections = list(data.get("connections_df", []) or [])
    subflows = list(data.get("subflows_df", []) or [])
    return {
        "file": str(source_name or "Current Flow on Canvas"),
        "flow_name": str(data.get("flow_name", "") or "").strip(),
        "flow_type": str(data.get("flow_type", "") or "").strip(),
        "node_count": len(nodes),
        "connection_count": len(connections),
        "subflow_count": len(subflows),
        "content": data,
    }


def get_canvas_context(workflow):
    graph = getattr(workflow, "graph", None)
    if graph is None:
        return {}
    try:
        all_nodes = list(graph.all_nodes())
    except Exception:
        all_nodes = []
    try:
        selected_nodes = list(graph.selected_nodes())
    except Exception:
        selected_nodes = []

    node_type_counts = {}
    for node in all_nodes:
        node_type = str(getattr(node, "__class__", type(node)).__name__ or "Unknown").strip()
        node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

    selected_summary = []
    for node in selected_nodes[:8]:
        try:
            input_ports = [str(name).strip() for name in list(node.inputs().keys()) if str(name).strip()]
        except Exception:
            input_ports = []
        try:
            output_ports = [str(name).strip() for name in list(node.outputs().keys()) if str(name).strip()]
        except Exception:
            output_ports = []
        selected_summary.append({
            "name": str(node.name() if hasattr(node, "name") else "").strip(),
            "node_type": str(getattr(node, "__class__", type(node)).__name__ or "Unknown").strip(),
            "id": str(getattr(node, "id", "") or "").strip(),
            "input_ports": input_ports,
            "output_ports": output_ports,
        })

    node_summaries = []
    for node in all_nodes[:25]:
        try:
            input_ports = [str(name).strip() for name in list(node.inputs().keys()) if str(name).strip()]
        except Exception:
            input_ports = []
        try:
            output_ports = [str(name).strip() for name in list(node.outputs().keys()) if str(name).strip()]
        except Exception:
            output_ports = []
        node_summaries.append({
            "name": str(node.name() if hasattr(node, "name") else "").strip(),
            "node_type": str(getattr(node, "__class__", type(node)).__name__ or "Unknown").strip(),
            "id": str(getattr(node, "id", "") or "").strip(),
            "input_ports": input_ports,
            "output_ports": output_ports,
        })

    return {
        "workflow_name": str(workflow.get_flow_display_name() if hasattr(workflow, "get_flow_display_name") else "").strip(),
        "workflow_type": str(workflow.get_flow_type() if hasattr(workflow, "get_flow_type") else "").strip(),
        "node_count": len(all_nodes),
        "selected_node_count": len(selected_nodes),
        "selected_nodes": selected_summary,
        "nodes": node_summaries,
        "node_type_counts": node_type_counts,
    }


def get_workspace_relationship_context(workflow):
    parent_workspace = workflow._find_workspace_parent() if hasattr(workflow, "_find_workspace_parent") else None
    relationship = {
        "current_flow_name": str(workflow.get_flow_display_name() if hasattr(workflow, "get_flow_display_name") else "").strip(),
        "current_flow_type": str(workflow.get_flow_type() if hasattr(workflow, "get_flow_type") else "").strip(),
        "is_master_flow": False,
        "is_subflow": False,
        "master_flow_name": "",
        "linked_proxy_name": "",
        "sibling_subflows": [],
        "subflow_count": 0,
    }
    if parent_workspace is None:
        return relationship

    master_workflow = getattr(parent_workspace, "master_workflow", None)
    relationship["is_master_flow"] = bool(workflow is master_workflow)
    relationship["is_subflow"] = bool(workflow is not master_workflow)
    if master_workflow is not None and hasattr(master_workflow, "get_flow_display_name"):
        relationship["master_flow_name"] = str(master_workflow.get_flow_display_name() or "").strip()

    subflows = []
    if hasattr(parent_workspace, "_subflow_workflows"):
        try:
            subflows = list(parent_workspace._subflow_workflows())
        except Exception:
            subflows = []
    relationship["subflow_count"] = len(subflows)

    sibling_subflows = []
    for subflow in subflows:
        try:
            subflow_name = str(subflow.get_flow_display_name() or "").strip()
        except Exception:
            subflow_name = ""
        proxy = getattr(subflow, "_subflow_proxy_node", None)
        try:
            proxy_name = str(proxy.name() or "").strip() if proxy is not None else ""
        except Exception:
            proxy_name = ""
        sibling_subflows.append({
            "flow_name": subflow_name,
            "proxy_name": proxy_name,
            "is_current": bool(subflow is workflow),
        })
    relationship["sibling_subflows"] = sibling_subflows

    current_proxy = getattr(workflow, "_subflow_proxy_node", None)
    if current_proxy is not None:
        try:
            relationship["linked_proxy_name"] = str(current_proxy.name() or "").strip()
        except Exception:
            relationship["linked_proxy_name"] = ""
    return relationship
