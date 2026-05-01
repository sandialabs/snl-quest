import re


def _looks_like_canvas_action_request(user_prompt):
    prompt = str(user_prompt or "").casefold()
    action_signals = (
        "create",
        "add",
        "insert",
        "make",
        "connect",
        "wire",
        "rename",
        "delete",
        "remove",
        "update",
        "change",
        "set",
        "edit",
    )
    canvas_targets = (
        "node",
        "datanode",
        "data node",
        "data-node",
        "pynode",
        "py node",
        "pythonnode",
        "python node",
        "text node",
        "annotation",
        "note node",
        "canvas",
        "workflow",
        "flow",
        "subflow",
        "sub-flow",
        "selected",
    )
    return any(token in prompt for token in action_signals) and any(token in prompt for token in canvas_targets)


def build_fallback_reply(task_match_result):
    result = dict(task_match_result or {})
    if not result:
        return {
            "reply": "I couldn't build the current project summary yet. Try again after confirming your API key is available.",
        }

    lines = []
    project_description = str(result.get("project_description", "") or "").strip()
    flow_description = str(result.get("flow_description", "") or "").strip()

    if project_description:
        lines.append(f"Project description: {project_description}")
    if flow_description:
        lines.append(f"Current flow: {flow_description}")

    strategy = str(result.get("strategy", "") or "").strip()
    tool_matches = list(result.get("tool_matches", []))
    skill_matches = list(result.get("skill_matches", []))
    notes = [str(note).strip() for note in list(result.get("notes", []) or []) if str(note).strip()]

    if strategy == "no_viable_quest_solution":
        lines.append("I don't see an active QuESt tool or saved skill that cleanly fits this task right now.")
    else:
        if tool_matches:
            top_tools = ", ".join(
                str(item.get("name", item.get("tool_id", "Unknown Tool"))).strip()
                for item in tool_matches[:3]
            )
            lines.append(f"The strongest active QuESt tool matches are: {top_tools}.")
        if skill_matches:
            top_skills = ", ".join(
                str(item.get("title", item.get("skill_id", "Unknown Skill"))).strip()
                for item in skill_matches[:2]
            )
            lines.append(f"I also found relevant saved skills: {top_skills}.")

    if notes:
        lines.append(notes[0])

    next_step_map = {
        "use_quest_skill": "Next, I can use the closest saved QuESt skill as the starting point for the workflow plan.",
        "use_general_python_skill_plus_tools": "Next, I can combine the best general Python skill with the matched QuESt tools and draft the workflow plan.",
        "use_tools_only": "Next, I can draft a fresh QuESt workflow plan directly from the matched active tools.",
        "no_viable_quest_solution": "If you want, I can still help refine the project scope, clarify the flow, or suggest what QuESt capability is missing.",
    }
    if strategy in next_step_map:
        lines.append(next_step_map[strategy])

    return {
        "reply": "\n\n".join(line for line in lines if str(line).strip()),
    }


def _extract_count(prompt_text):
    word_map = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    lowered = str(prompt_text or "").casefold()
    match = re.search(r"\b([1-5])\b", lowered)
    if match:
        try:
            return max(1, min(5, int(match.group(1))))
        except Exception:
            return 1
    for word, value in word_map.items():
        if re.search(rf"\b{word}\b", lowered):
            return value
    return 1


def _extract_named_value(prompt_text, patterns):
    text = str(prompt_text or "")
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        value = str(match.group(1) or "").strip().strip('"\'')
        if value:
            return value
    return ""


def _extract_subflow_name(prompt_text):
    value = _extract_named_value(
        prompt_text,
        [
            r"(?:subflow|sub-flow)\s+(?:named|called)\s+([\w\- ]+?)(?=\s+(?:to|with|for|that)\b|[.,;\n]|$)",
            r"(?:create|add|make)\s+(?:a\s+)?(?:new\s+)?(?:subflow|sub-flow)\s+(?:named|called)\s+([\w\- ]+?)(?=\s+(?:to|with|for|that)\b|[.,;\n]|$)",
            r"name\s+(?:the\s+)?(?:subflow|sub-flow)\s+([\w\- ]+?)(?=\s+(?:to|with|for|that)\b|[.,;\n]|$)",
        ],
    )
    value = re.sub(r"\s+", " ", str(value or "")).strip(" -")
    return value


def _extract_revision_request(prompt_text):
    text = str(prompt_text or "").strip()
    if not text:
        return ""
    marker = "Latest authoritative revision request:"
    if marker in text:
        after_marker = text.split(marker, 1)[1]
        stop_marker = "Revision rule:"
        if stop_marker in after_marker:
            after_marker = after_marker.split(stop_marker, 1)[0]
        candidate = str(after_marker or "").strip()
        if candidate:
            return candidate
    if re.match(r"^\s*revise\b", text, flags=re.IGNORECASE):
        return text
    return ""


def _extract_add_two_numbers_initial_values(prompt_text):
    text = str(prompt_text or "")
    lowered = text.casefold()
    patterns = [
        r"(?:initialize|set)\s+(?:the\s+)?data\s+nodes?\s+with\s+values?\s+([^.;\n]+)",
        r"values?\s+([^.;\n]+)",
    ]
    raw_values = ""
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw_values = str(match.group(1) or "").strip()
            if raw_values:
                break
    if not raw_values:
        return []

    candidates = []
    for quoted in re.findall(r'"([^"]*)"|\'([^\']*)\'', raw_values):
        value = str(quoted[0] or quoted[1] or "").strip()
        if value:
            candidates.append(value)
    if len(candidates) >= 2:
        return candidates[:2]

    numeric_matches = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])", raw_values)
    if len(numeric_matches) >= 2:
        return numeric_matches[:2]

    parts = [
        part.strip().strip('"\'')
        for part in re.split(r"\s*(?:,|and)\s*", raw_values)
        if part.strip()
    ]
    cleaned = []
    for part in parts:
        lowered_part = part.casefold()
        if lowered_part in {"value", "values", "respectively"}:
            continue
        cleaned.append(part)
    return cleaned[:2]


def _build_connected_add_two_numbers_actions(flow_name="", create_subflow=False, initial_values=None):
    initial_values = list(initial_values or [])
    first_value = str(initial_values[0]).strip() if len(initial_values) >= 1 else ""
    second_value = str(initial_values[1]).strip() if len(initial_values) >= 2 else ""
    actions = []
    if create_subflow:
        action = {"type": "add_subflow"}
        if str(flow_name or "").strip():
            action["flow_name"] = str(flow_name).strip()
        actions.append(action)
    first_data_action = {
        "type": "create_node",
        "node_type": "data",
        "name": "x_input",
        "variable_name": "x",
        "value_display": True,
    }
    second_data_action = {
        "type": "create_node",
        "node_type": "data",
        "name": "y_input",
        "variable_name": "y",
        "value_display": True,
    }
    if first_value:
        first_data_action["value"] = first_value
    if second_value:
        second_data_action["value"] = second_value
    actions.extend(
        [
            first_data_action,
            second_data_action,
            {
                "type": "create_node",
                "node_type": "py",
                "name": "add_numbers",
                "imports": "import pandas as pd\nimport numpy as np\n",
                "wrapper": (
                    "def add_numbers_function(x, y):\n"
                    "    return {'sum': x + y}\n"
                ),
            },
            {
                "type": "connect_nodes",
                "source_node": "x_input",
                "target_node": "add_numbers",
                "mapping": {"x": "x"},
            },
            {
                "type": "connect_nodes",
                "source_node": "y_input",
                "target_node": "add_numbers",
                "mapping": {"y": "y"},
            },
        ]
    )
    return actions


def _ordered_node_names_in_prompt(prompt_text, canvas_context):
    prompt_lower = str(prompt_text or "").casefold()
    indexed = []
    for node in list(dict(canvas_context or {}).get("nodes", []) or []):
        name = str(dict(node or {}).get("name", "") or "").strip()
        if not name:
            continue
        position = prompt_lower.find(name.casefold())
        if position >= 0:
            indexed.append((position, name))
    indexed.sort(key=lambda item: item[0])
    ordered = []
    seen = set()
    for _, name in indexed:
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(name)
    return ordered


def _find_canvas_node_entry(canvas_context, node_name):
    target = str(node_name or "").strip()
    if not target:
        return {}
    target_key = target.casefold()
    for node in list(dict(canvas_context or {}).get("nodes", []) or []):
        item = dict(node or {})
        current_name = str(item.get("name", "") or "").strip()
        if current_name and current_name.casefold() == target_key:
            return item
    return {}


def _extract_existing_node_value_update_action(prompt_text, canvas_context):
    text = str(prompt_text or "").strip()
    lowered = text.casefold()
    if not text or not any(token in lowered for token in ("edit", "update", "change", "set")):
        return None
    match = re.search(
        r"(?:edit|update|change|set)\s+(?:the\s+)?value\s+(?:of|for)\s+([\w\- ]+?)\s+(?:to|as)\s+([^,.;\n]+)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        requested_name = str(match.group(1) or "").strip()
        value_text = str(match.group(2) or "").strip().strip('"\'')
    else:
        ordered_names = _ordered_node_names_in_prompt(text, canvas_context)
        if not ordered_names:
            return None
        requested_name = ordered_names[0]
        value_text = _extract_named_value(
            text,
            [
                r"(?:value|input value)\s+(?:to|as)\s+([^,.;\n]+)",
                r"(?:edit|update|change|set)\s+[\w\- ]+?\s+(?:to|as)\s+([^,.;\n]+)",
            ],
        )
        value_text = str(value_text or "").strip().strip('"\'')
    if not requested_name or not value_text:
        return None
    node_entry = _find_canvas_node_entry(canvas_context, requested_name)
    actual_name = str(node_entry.get("name", "") or requested_name).strip()
    node_type_name = str(node_entry.get("node_type", "") or node_entry.get("type", "") or "").strip()
    normalized_type = ""
    if node_type_name == "DataNode":
        normalized_type = "data"
    elif node_type_name == "PyNode":
        normalized_type = "py"
    elif node_type_name == "BackNode":
        normalized_type = "text"
    if normalized_type == "text":
        return None
    action = {
        "type": "update_node",
        "node_name": actual_name,
        "value": value_text,
    }
    if normalized_type:
        action["node_type"] = normalized_type
    if "show value" in lowered or "display value" in lowered:
        action["value_display"] = True
    return action


def _plan_matches_existing_node_value_update(plan, expected_action):
    item = dict(expected_action or {})
    expected_name = str(item.get("node_name", "") or "").strip().casefold()
    expected_value = str(item.get("value", "") or "")
    if not expected_name or expected_value == "":
        return False
    for action in list(dict(plan or {}).get("actions", []) or []):
        current = dict(action or {})
        action_type = str(current.get("type", "") or "").strip()
        if action_type != "update_node":
            continue
        current_name = str(current.get("node_name", "") or "").strip().casefold()
        current_value = str(current.get("value", "") or "")
        if current_name == expected_name and current_value == expected_value:
            return True
    return False


def _fallback_canvas_plan(user_prompt, canvas_context):
    text = str(user_prompt or "").strip()
    lowered = text.casefold()
    selected_nodes = list(dict(canvas_context or {}).get("selected_nodes", []) or [])
    selected_count = int(dict(canvas_context or {}).get("selected_node_count", 0) or 0)
    create_verbs = ("create", "add", "insert", "make")
    subflow_request = any(verb in lowered for verb in create_verbs) and ("subflow" in lowered or "sub-flow" in lowered)
    initial_values = _extract_add_two_numbers_initial_values(text)

    arithmetic_flow_request = _looks_like_add_two_numbers_flow_request(text)
    if arithmetic_flow_request and subflow_request:
        return {
            "reply": "",
            "actions": _build_connected_add_two_numbers_actions(
                flow_name=_extract_subflow_name(text),
                create_subflow=True,
                initial_values=initial_values,
            ),
        }
    if arithmetic_flow_request:
        return {
            "reply": "",
            "actions": _build_connected_add_two_numbers_actions(initial_values=initial_values),
        }

    existing_value_update_action = _extract_existing_node_value_update_action(text, canvas_context)
    if existing_value_update_action is not None:
        return {
            "reply": "",
            "actions": [existing_value_update_action],
            "planning_path": "edit_current_flow",
            "path_reason": "The current canvas already contains the target node, so the simplest valid action is to edit that existing node rather than rebuild anything.",
        }

    if subflow_request:
        subflow_name = _extract_subflow_name(text)
        action = {"type": "add_subflow"}
        if subflow_name:
            action["flow_name"] = subflow_name
        return {"reply": "", "actions": [action]}

    if any(verb in lowered for verb in create_verbs):
        if "data node" in lowered or "datanode" in lowered or "data-node" in lowered:
            action = {"type": "create_node", "node_type": "data", "count": _extract_count(text)}
            name = _extract_named_value(text, [r"(?:named|called)\s+([\w\- ]+)", r"name\s+(?:it|them)\s+([\w\- ]+)"])
            variable_name = _extract_named_value(text, [r"variable\s+(?:named\s+)?([A-Za-z_][\w\.]*)"])
            value = _extract_named_value(text, [r"value\s+(?:to\s+)?([^,.;\n]+)"])
            if name:
                action["name"] = name
            if variable_name:
                action["variable_name"] = variable_name
            if value:
                action["value"] = value
            if "show value" in lowered or "display value" in lowered:
                action["value_display"] = True
            if "path" in lowered or "file" in lowered or "folder" in lowered:
                action["is_path"] = True
            return {"reply": "", "actions": [action]}
        if "python node" in lowered or "pythonnode" in lowered or re.search(r"\bpynode\b", lowered) or re.search(r"\bpy node\b", lowered):
            action = {"type": "create_node", "node_type": "py", "count": _extract_count(text)}
            name = _extract_named_value(text, [r"(?:named|called)\s+([\w\- ]+)", r"name\s+(?:it|them)\s+([\w\- ]+)"])
            if name:
                action["name"] = name
            return {"reply": "", "actions": [action]}
        if "text node" in lowered or "note node" in lowered or "annotation" in lowered:
            action = {"type": "create_node", "node_type": "text", "count": _extract_count(text)}
            note_text = _extract_named_value(text, [r"(?:with text|saying|that says|text)\s+([^\n]+)"])
            if note_text:
                action["text"] = note_text
            return {"reply": "", "actions": [action]}

    if selected_count > 0 and any(token in lowered for token in ("delete selected", "remove selected", "delete this node", "delete these nodes", "remove this node")):
        return {"reply": "", "actions": [{"type": "delete_selected_nodes"}]}

    if selected_count == 1 and any(token in lowered for token in ("rename selected", "rename this node", "rename node", "name this node")):
        new_name = _extract_named_value(text, [r"rename(?: the)?(?: selected)?(?: node)? to\s+([^,.;\n]+)", r"name this node\s+([^,.;\n]+)"])
        if new_name:
            return {"reply": "", "actions": [{"type": "rename_selected_node", "new_name": new_name}]}

    if selected_count == 1:
        selected_type = str(dict(selected_nodes[0] or {}).get("node_type", "") or "").strip()
        if selected_type == "BackNode" and any(token in lowered for token in ("update text", "change text", "set text", "caption", "note")):
            new_text = _extract_named_value(text, [r"(?:update|change|set)\s+(?:the\s+)?(?:text|caption|note)(?:\s+to)?\s+([^\n]+)"])
            if new_text:
                return {"reply": "", "actions": [{"type": "update_selected_text_node", "text": new_text}]}

    if "connect" in lowered and " to " in lowered:
        ordered_names = _ordered_node_names_in_prompt(text, canvas_context)
        if len(ordered_names) >= 2:
            return {
                "reply": "",
                "actions": [{
                    "type": "connect_nodes",
                    "source_node": ordered_names[0],
                    "target_node": ordered_names[1],
                }],
            }

    return {"reply": "", "actions": []}


def _looks_like_add_two_numbers_flow_request(user_prompt):
    lowered = str(user_prompt or "").strip().casefold()
    if not lowered:
        return False
    explicit_flow = any(
        token in lowered
        for token in (
            "fully connected flow",
            "connected flow",
            "full flow",
            "workflow",
            "flow",
        )
    )
    add_two_numbers = any(
        token in lowered
        for token in (
            "add two numbers",
            "sum two numbers",
            "add 2 numbers",
            "sum 2 numbers",
            "add numbers",
            "sum numbers",
        )
    )
    return explicit_flow and add_two_numbers


def _plan_has_connected_arithmetic_flow(plan):
    actions = list(dict(plan or {}).get("actions", []) or [])
    has_connect = any(str(dict(action).get("type", "") or "").strip() == "connect_nodes" for action in actions)
    has_py_wrapper = any(
        str(dict(action).get("type", "") or "").strip() == "create_node"
        and str(dict(action).get("node_type", "") or "").strip() == "py"
        and any(str(dict(action).get(key, "") or "").strip() for key in ("wrapper", "code", "node_function_wrapper"))
        for action in actions
    )
    return has_connect and has_py_wrapper


def _plan_has_named_arithmetic_inputs(plan):
    actions = [dict(action or {}) for action in list(dict(plan or {}).get("actions", []) or [])]
    data_actions = [
        action for action in actions
        if str(action.get("type", "") or "").strip() == "create_node"
        and str(action.get("node_type", "") or "").strip() == "data"
    ]
    if len(data_actions) < 2:
        return False

    named_inputs = {}
    for action in data_actions:
        node_name = str(action.get("name", "") or "").strip()
        variable_name = str(action.get("variable_name", "") or "").strip()
        if node_name and variable_name:
            named_inputs[node_name] = variable_name

    if len(named_inputs) < 2:
        return False

    py_actions = [
        action for action in actions
        if str(action.get("type", "") or "").strip() == "create_node"
        and str(action.get("node_type", "") or "").strip() == "py"
    ]
    if not py_actions:
        return False

    py_names = {
        str(action.get("name", "") or "").strip()
        for action in py_actions
        if str(action.get("name", "") or "").strip()
    }
    if not py_names:
        return False

    connect_actions = [
        action for action in actions
        if str(action.get("type", "") or "").strip() == "connect_nodes"
    ]
    if len(connect_actions) < 2:
        return False

    connected_variables = set()
    for action in connect_actions:
        source_node = str(action.get("source_node", "") or action.get("from_node", "") or "").strip()
        target_node = str(action.get("target_node", "") or action.get("to_node", "") or "").strip()
        if source_node not in named_inputs or target_node not in py_names:
            continue
        mapping = action.get("mapping")
        if isinstance(mapping, dict):
            for source_port, target_port in mapping.items():
                if str(source_port or "").strip() == named_inputs[source_node] and str(target_port or "").strip():
                    connected_variables.add(named_inputs[source_node])
        else:
            source_port = str(action.get("source_port", "") or "").strip()
            target_port = str(action.get("target_port", "") or "").strip()
            if source_port and target_port and source_port == named_inputs[source_node]:
                connected_variables.add(named_inputs[source_node])

    required_variables = set(named_inputs.values())
    return len(required_variables) >= 2 and required_variables.issubset(connected_variables)


def _plan_matches_add_two_numbers_request(plan, user_prompt):
    if not _plan_has_connected_arithmetic_flow(plan):
        return False
    if not _plan_has_named_arithmetic_inputs(plan):
        return False
    lowered = str(user_prompt or "").strip().casefold()
    if "subflow" in lowered or "sub-flow" in lowered:
        actions = list(dict(plan or {}).get("actions", []) or [])
        return any(str(dict(action).get("type", "") or "").strip() == "add_subflow" for action in actions)
    return True


def route_chat_turn(user_prompt, model_name, state, context_payload, run_chat_router_func):
    task_match_result = dict((state or {}).get("task_match_results", {}) or {})
    if run_chat_router_func is None:
        if _looks_like_canvas_action_request(user_prompt):
            return {
                "action": "execute_canvas_action",
                "reason": "Heuristic canvas action routing.",
                "task_focus": str(user_prompt or "").strip(),
            }
        return {
            "action": "analyze_task" if not task_match_result else "answer_only",
            "reason": "",
            "task_focus": str(user_prompt or "").strip(),
        }

    try:
        routed = run_chat_router_func(
            user_prompt=user_prompt,
            task_match_result=task_match_result,
            pinned_context=list(context_payload.get("pinned_context", []) or []),
            attached_files=list(context_payload.get("attached_files", []) or []),
            attached_workflow_jsons=list(context_payload.get("attached_workflow_jsons", []) or []),
            workspace_relationship_context=dict(context_payload.get("workspace_relationship_context", {}) or {}),
            implicit_code_context=list(context_payload.get("implicit_code_context", []) or []),
            python_node_wrapper_rules=dict(context_payload.get("python_node_wrapper_rules", {}) or {}),
            skill_execution_recipes=dict(context_payload.get("skill_execution_recipes", {}) or {}),
            selected_model=model_name,
            recent_messages=list(context_payload.get("recent_messages", []) or []),
        )
        if _looks_like_canvas_action_request(user_prompt):
            routed_action = str(routed.get("action", "") or "").strip()
            if routed_action != "execute_canvas_action":
                routed["action"] = "execute_canvas_action"
                routed["reason"] = str(routed.get("reason", "") or "Heuristic canvas action routing.")
        return routed
    except Exception:
        if _looks_like_canvas_action_request(user_prompt):
            return {
                "action": "execute_canvas_action",
                "reason": "Heuristic canvas action routing.",
                "task_focus": str(user_prompt or "").strip(),
            }
        return {
            "action": "analyze_task" if not task_match_result else "answer_only",
            "reason": "",
            "task_focus": str(user_prompt or "").strip(),
        }


def generate_assistant_reply(user_prompt, model_name, state, context_payload, run_grounded_chat_reply_func):
    task_match_result = dict((state or {}).get("task_match_results", {}) or {})
    fallback_reply = build_fallback_reply(task_match_result)
    if run_grounded_chat_reply_func is None:
        return fallback_reply

    try:
        reply_payload = run_grounded_chat_reply_func(
            user_prompt=user_prompt,
            task_match_result=task_match_result,
            pinned_context=list(context_payload.get("pinned_context", []) or []),
            attached_files=list(context_payload.get("attached_files", []) or []),
            attached_workflow_jsons=list(context_payload.get("attached_workflow_jsons", []) or []),
            workspace_relationship_context=dict(context_payload.get("workspace_relationship_context", {}) or {}),
            implicit_code_context=list(context_payload.get("implicit_code_context", []) or []),
            python_node_wrapper_rules=dict(context_payload.get("python_node_wrapper_rules", {}) or {}),
            skill_execution_recipes=dict(context_payload.get("skill_execution_recipes", {}) or {}),
            selected_model=model_name,
            recent_messages=list(context_payload.get("recent_messages", []) or []),
        )
        if isinstance(reply_payload, dict):
            reply_text = str(reply_payload.get("reply", "") or "").strip()
            if reply_text:
                return {"reply": reply_text}
        return fallback_reply
    except Exception:
        return fallback_reply


def should_refresh_analysis_before_canvas_plan(user_prompt, state, route_result=None, canvas_context=None):
    task_match_result = dict((state or {}).get("task_match_results", {}) or {})
    lowered = str(user_prompt or "").strip().casefold()
    canvas_context = dict(canvas_context or {})
    node_count = len(list(canvas_context.get("nodes", []) or []))
    flow_description = str(task_match_result.get("flow_description", "") or "").strip()

    if not task_match_result:
        return True
    if node_count > 0 and not flow_description:
        return True

    analysis_sensitive_tokens = (
        "revise",
        "change",
        "modify",
        "adjust",
        "fix",
        "repair",
        "complete",
        "finish",
        "missing",
        "existing",
        "current flow",
        "this flow",
        "that flow",
        "initialize",
        "value",
        "connect",
        "wire",
        "rename",
    )
    if any(token in lowered for token in analysis_sensitive_tokens):
        return True

    route_action = str(dict(route_result or {}).get("action", "") or "").strip()
    if route_action == "execute_canvas_action" and node_count > 0:
        return True
    return False


def _should_prefer_analysis_guided_plan(user_prompt, state, canvas_context=None):
    task_match_result = dict((state or {}).get("task_match_results", {}) or {})
    canvas_context = dict(canvas_context or {})
    lowered = str(user_prompt or "").strip().casefold()
    flow_description = str(task_match_result.get("flow_description", "") or "").strip()
    notes = [
        str(note).strip().casefold()
        for note in list(task_match_result.get("notes", []) or [])
        if str(note).strip()
    ]
    node_count = len(list(canvas_context.get("nodes", []) or []))

    if node_count <= 0 and not flow_description:
        return False

    if any(token in lowered for token in ("revise", "change", "modify", "adjust", "fix", "repair", "complete", "finish")):
        return True

    if flow_description:
        return True

    analysis_gap_tokens = (
        "unconnected",
        "missing",
        "no connections",
        "no inferred input or output ports",
        "empty input values",
        "default output port",
        "incomplete",
    )
    return any(any(token in note for token in analysis_gap_tokens) for note in notes)


def _has_reusable_skill_workflow_template(context_payload):
    recipes = list(dict(context_payload or {}).get("skill_execution_recipes", {}).get("recipes", []) or [])
    for recipe in recipes:
        recipe = dict(recipe or {})
        try:
            confidence = float(recipe.get("confidence", 0.0))
        except Exception:
            confidence = 0.0
        workflow_template = dict(recipe.get("workflow_template", {}) or {})
        workflow_path = str(workflow_template.get("path", "") or "").strip()
        if workflow_path and confidence >= 0.55:
            return True
    return False


def plan_canvas_actions(user_prompt, model_name, state, context_payload, canvas_context, run_workspace_action_plan_func):
    fallback_plan = _fallback_canvas_plan(user_prompt, canvas_context)
    existing_value_update_action = _extract_existing_node_value_update_action(user_prompt, canvas_context)
    revision_request = _extract_revision_request(user_prompt)
    is_revision_request = bool(revision_request)
    if _looks_like_add_two_numbers_flow_request(user_prompt) and not is_revision_request and not _should_prefer_analysis_guided_plan(
        user_prompt,
        state,
        canvas_context,
    ) and not _has_reusable_skill_workflow_template(context_payload):
        deterministic_plan = dict(fallback_plan or {})
        deterministic_plan["planning_source"] = "deterministic_fallback"
        deterministic_plan["planning_path"] = "manual_canvas_build"
        deterministic_plan["path_reason"] = "Used the deterministic canvas build fallback because no stronger reusable template path was available."
        deterministic_plan["reply"] = str(deterministic_plan.get("reply", "") or "").strip()
        return deterministic_plan
    if run_workspace_action_plan_func is None:
        return fallback_plan

    try:
        planned = run_workspace_action_plan_func(
            user_prompt=user_prompt,
            canvas_context=dict(canvas_context or {}),
            task_match_result=dict((state or {}).get("task_match_results", {}) or {}),
            pinned_context=list(context_payload.get("pinned_context", []) or []),
            attached_files=list(context_payload.get("attached_files", []) or []),
            attached_workflow_jsons=list(context_payload.get("attached_workflow_jsons", []) or []),
            workspace_relationship_context=dict(context_payload.get("workspace_relationship_context", {}) or {}),
            implicit_code_context=list(context_payload.get("implicit_code_context", []) or []),
            python_node_wrapper_rules=dict(context_payload.get("python_node_wrapper_rules", {}) or {}),
            skill_execution_recipes=dict(context_payload.get("skill_execution_recipes", {}) or {}),
            recent_messages=list(context_payload.get("recent_messages", []) or []),
            selected_model=model_name,
        )
    except Exception:
        return fallback_plan

    planned = dict(planned or {})
    if _looks_like_add_two_numbers_flow_request(user_prompt) and not is_revision_request and not _plan_matches_add_two_numbers_request(planned, user_prompt):
        fallback_actions = list(dict(fallback_plan or {}).get("actions", []) or [])
        if fallback_actions:
            upgraded = dict(planned)
            upgraded["actions"] = fallback_actions
            reply_text = str(upgraded.get("reply", "") or "").strip()
            if not reply_text:
                upgraded["reply"] = ""
            upgraded["planning_source"] = "deterministic_fallback"
            upgraded["planning_path"] = "manual_canvas_build"
            upgraded["path_reason"] = "Replaced an incomplete arithmetic-flow plan with the deterministic manual canvas build fallback."
            notes = list(upgraded.get("dropped_actions", []) or [])
            notes.append("Replaced partial arithmetic-flow plan with deterministic connected flow plan.")
            upgraded["dropped_actions"] = notes
            planned = upgraded
    if existing_value_update_action is not None and not _plan_matches_existing_node_value_update(planned, existing_value_update_action):
        fallback_actions = list(dict(fallback_plan or {}).get("actions", []) or [])
        if fallback_actions:
            upgraded = dict(planned)
            upgraded["actions"] = fallback_actions
            upgraded["planning_source"] = "deterministic_fallback"
            upgraded["planning_path"] = str(dict(fallback_plan or {}).get("planning_path", "") or "edit_current_flow")
            upgraded["path_reason"] = str(
                dict(fallback_plan or {}).get("path_reason", "")
                or "Replaced an incorrect rebuild plan with a deterministic edit of the existing node."
            )
            notes = list(upgraded.get("dropped_actions", []) or [])
            notes.append("Replaced a rebuild plan with a deterministic existing-node value edit.")
            upgraded["dropped_actions"] = notes
            planned = upgraded
    if list(planned.get("actions", []) or []):
        planned["planning_source"] = str(planned.get("planning_source", "") or "llm")
        return planned

    if list(planned.get("dropped_actions", []) or []):
        planned["planning_source"] = str(planned.get("planning_source", "") or "llm")
        return planned

    fallback_actions = list(dict(fallback_plan or {}).get("actions", []) or [])
    if fallback_actions:
        fallback_plan = dict(fallback_plan or {})
        fallback_plan["planning_source"] = "fallback"
        fallback_plan["planning_path"] = str(
            fallback_plan.get("planning_path", "") or "manual_canvas_build"
        )
        fallback_plan["path_reason"] = str(
            fallback_plan.get("path_reason", "")
            or "Fell back to the manual canvas build heuristic because the planner did not return executable actions."
        )
        fallback_plan["reply"] = str(planned.get("reply", "") or fallback_plan.get("reply", "") or "").strip()
        return fallback_plan

    planned["planning_source"] = "llm"
    return planned


def build_canvas_action_reply(action_plan, executed, error=None):
    if error is not None:
        return {
            "reply": f"I couldn't apply the requested canvas changes.\n\nDetails: {error}",
        }

    reply_text = str(dict(action_plan or {}).get("reply", "") or "").strip()
    dropped = [
        str(item).strip()
        for item in list(dict(action_plan or {}).get("dropped_actions", []) or [])
        if str(item).strip()
    ]
    execution_notes = [
        str(item).strip()
        for item in list(dict(action_plan or {}).get("execution_notes", []) or [])
        if str(item).strip()
    ]
    planning_source = str(dict(action_plan or {}).get("planning_source", "") or "").strip()
    executed = list(executed or [])
    if executed:
        summary = "\n".join(f"- {item}" for item in executed)
        source_note = ""
        if planning_source == "fallback":
            source_note = "Used a deterministic fallback interpretation of your canvas request.\n\n"
        elif planning_source == "llm" and dropped:
            source_note = "Repaired part of the plan before execution.\n\n"
        note_text = ""
        if execution_notes:
            note_text = "\n\nExecution notes:\n" + "\n".join(f"- {item}" for item in execution_notes[:5])
        final_reply = source_note + reply_text + ("\n\n" if reply_text else "") + "Applied canvas actions:\n" + summary + note_text
    else:
        if dropped:
            details = "\n".join(f"- {item}" for item in dropped[:5])
            prefix = reply_text + "\n\n" if reply_text else ""
            if execution_notes:
                details += "\n" + "\n".join(f"- {item}" for item in execution_notes[:5])
            final_reply = prefix + "I understood this as a canvas request, but no executable actions survived validation.\n\nValidation details:\n" + details
        elif execution_notes:
            details = "\n".join(f"- {item}" for item in execution_notes[:5])
            prefix = reply_text + "\n\n" if reply_text else ""
            final_reply = prefix + "I planned canvas changes, but the executor could not apply them.\n\nExecution details:\n" + details
        else:
            final_reply = reply_text or "I did not apply any canvas changes."
    return {"reply": final_reply}
