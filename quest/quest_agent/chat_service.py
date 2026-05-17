import re


def _fast_local_mode_selected(model_name):
    lowered = str(model_name or "").strip().casefold()
    if not lowered:
        return False
    if lowered.startswith("ollama:"):
        return True
    return lowered.startswith("gemma 4")


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


def _looks_like_direct_workspace_action_request(user_prompt):
    prompt = str(user_prompt or "").casefold()
    if not prompt:
        return False
    direct_targets = (
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
        "selected node",
        "selected nodes",
    )
    direct_actions = (
        "connect",
        "wire",
        "rename selected",
        "rename this node",
        "delete selected",
        "remove selected",
        "delete this node",
        "remove this node",
        "update selected",
        "change selected",
        "set selected",
    )
    if any(target in prompt for target in direct_targets):
        return any(
            action in prompt
            for action in (
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
        )
    return any(action in prompt for action in direct_actions)


def _looks_like_flow_analysis_request(user_prompt):
    prompt = str(user_prompt or "").casefold()
    analysis_signals = (
        "analyze",
        "analyse",
        "validate",
        "review",
        "check",
        "inspect",
    )
    flow_targets = (
        "this flow",
        "current flow",
        "the flow",
        "canvas",
        "workflow",
        "against the task",
        "against task",
    )
    return any(signal in prompt for signal in analysis_signals) and any(target in prompt for target in flow_targets)


def _format_plain_text_table(headers, rows):
    header_cells = [str(value or "").strip() for value in list(headers or [])]
    if not header_cells:
        return []
    normalized_rows = []
    for row in list(rows or []):
        values = [str(value or "").strip() for value in list(row or [])]
        if len(values) < len(header_cells):
            values.extend([""] * (len(header_cells) - len(values)))
        normalized_rows.append(values[:len(header_cells)])
    widths = [len(cell) for cell in header_cells]
    for row in normalized_rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def _format_row(values):
        return " | ".join(
            str(values[index] or "").ljust(widths[index])
            for index in range(len(widths))
        )

    lines = [_format_row(header_cells), "-+-".join("-" * width for width in widths)]
    lines.extend(_format_row(row) for row in normalized_rows)
    return lines


def _format_port_list(port_names):
    cleaned = [str(name or "").strip() for name in list(port_names or []) if str(name or "").strip()]
    return ", ".join(cleaned) if cleaned else "(none)"


def _build_structured_flow_analysis_lines(task_match_result):
    result = dict(task_match_result or {})
    analysis = dict(result.get("structured_flow_analysis", {}) or {})
    if not analysis:
        return []
    data_rows = [
        [
            str(item.get("name", "") or "").strip(),
            str(item.get("port", "") or "").strip(),
            str(item.get("value", "") or "").strip(),
        ]
        for item in list(analysis.get("data_nodes", []) or [])
    ]
    python_rows = [
        [
            str(item.get("name", "") or "").strip(),
            _format_port_list(item.get("input_ports", [])),
            _format_port_list(item.get("output_ports", [])),
            str(item.get("brief_description", "") or "").strip(),
        ]
        for item in list(analysis.get("python_nodes", []) or [])
    ]
    connection_rows = [
        [
            str(item.get("from_port", "") or "").strip(),
            str(item.get("to_port", "") or "").strip(),
        ]
        for item in list(analysis.get("connections", []) or [])
    ]
    missing_source = (
        result.get("missing_parts", None)
        or analysis.get("semantic_missing_parts", None)
        or analysis.get("missing_parts", None)
    )
    missing_parts = [
        str(item).strip()
        for item in list(missing_source or [])
        if str(item).strip()
    ]
    lines = [
        "1. Data nodes:",
        *(_format_plain_text_table(["name", "port", "value"], data_rows) if data_rows else ["(none)"]),
        "",
        "2. Python nodes:",
        *(_format_plain_text_table(["name", "input ports", "output ports", "brief description"], python_rows) if python_rows else ["(none)"]),
        "",
        "3. Connections:",
        *(_format_plain_text_table(["from port", "to port"], connection_rows) if connection_rows else ["(none)"]),
        "",
        "4. Missing parts:",
    ]
    if missing_parts:
        lines.extend(f"- {item}" for item in missing_parts)
    else:
        lines.append("- None")
    validation_summary = str(result.get("validation_summary", "") or "").strip()
    validation_report = dict(result.get("validation_report", analysis.get("validation_report", {})) or {})
    if validation_summary or validation_report:
        lines.extend(["", "5. MCP validation facts:"])
        if validation_summary:
            lines.extend(validation_summary.splitlines())
        else:
            lines.append(f"validation_status: {validation_report.get('status', 'unknown')}")
            lines.append(f"structural_valid: {bool(validation_report.get('structural_valid', False))}")
            lines.append(f"task_alignment: {validation_report.get('task_alignment', 'unknown')}")
    return lines


def build_fallback_reply(task_match_result):
    result = dict(task_match_result or {})
    if not result:
        return {
            "reply": "I couldn't build the current project summary yet. Try again after confirming your API key is available.",
        }

    lines = []
    project_description = str(result.get("project_description", "") or "").strip()

    if project_description:
        lines.append(f"Project description: {project_description}")

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

    best_workflow_template = dict(result.get("best_workflow_template", {}) or {})
    template_title = str(best_workflow_template.get("title", "") or "").strip()
    if template_title:
        lines.append(
            f"Best workflow template: {template_title}. This should be the preferred baseline before building from scratch."
        )

    structured_lines = _build_structured_flow_analysis_lines(result)
    if structured_lines:
        lines.append("Flow analysis:")
        lines.append("\n".join(structured_lines))
    else:
        flow_description = str(result.get("flow_description", "") or "").strip()
        if flow_description:
            lines.append(f"Current flow: {flow_description}")

    validation_report = dict(result.get("validation_report", {}) or {})
    structural_missing_parts = [
        str(item).strip()
        for item in list(result.get("structural_missing_parts", validation_report.get("missing_parts", [])) or [])
        if str(item).strip()
    ]
    semantic_missing_parts = [
        str(item).strip()
        for item in list(result.get("missing_parts", []) or [])
        if str(item).strip()
    ]
    semantic_validation = dict(result.get("semantic_validation", {}) or {})
    semantic_aligned = (
        str(semantic_validation.get("task_alignment", "") or "").strip().casefold() == "aligned"
        and not list(semantic_validation.get("missing_parts", []) or [])
        and not list(semantic_validation.get("unexpected_parts", []) or [])
    )
    if semantic_aligned:
        semantic_missing_parts = []
        structural_missing_parts = []
    review_has_gaps = bool(semantic_missing_parts or structural_missing_parts)
    flow_is_structurally_complete = (
        bool(validation_report.get("structural_valid", False))
        and str(validation_report.get("status", "") or "").strip().casefold() == "complete"
        and not structural_missing_parts
    )

    next_step_map = {
        "use_quest_skill": "Next, I can use the closest saved QuESt skill as the starting point for the workflow plan.",
        "use_general_python_skill_plus_tools": "Next, I can combine the best general Python skill with the matched QuESt tools and draft the workflow plan.",
        "use_tools_only": "Next, I can draft a fresh QuESt workflow plan directly from the matched active tools.",
        "no_viable_quest_solution": "If you want, I can still help refine the project scope, clarify the flow, or suggest what QuESt capability is missing.",
    }
    if strategy in next_step_map and (review_has_gaps or not flow_is_structurally_complete):
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


def _clean_canvas_node_name(value):
    cleaned = re.split(
        r"\s+(?:with\s+)?(?:variable|value|wrapper|code|text|that|which|and\s+value|and\s+variable)\b",
        str(value or "").strip(),
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return re.sub(r"\s+", " ", str(cleaned or "")).strip(" -")


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
    if any(
        token in lowered
        for token in (
            "wrapper",
            "python node",
            "py node",
            "pynode",
            "input port",
            "output port",
            "connect",
            "connection",
            "add input",
            "adding input",
            "accept ",
            "compute",
            "return",
        )
    ):
        return None
    match = re.search(
        r"(?:edit|update|change|set)\s+(?:the\s+)?(?:data\s+node\s+)?value\s+(?:of|for)\s+([\w\- ]+?)\s+(?:to|as)\s+([^,.;\n]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        match = re.search(
            r"(?:edit|update|change|set)\s+([\w\- ]+?)\s+(?:value|input value)\s+(?:to|as)\s+([^,.;\n]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not match:
        return None
    requested_name = str(match.group(1) or "").strip()
    value_text = str(match.group(2) or "").strip().strip('"\'')
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
            name = _clean_canvas_node_name(name)
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
            name = _clean_canvas_node_name(name)
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


def route_chat_turn(user_prompt, model_name, state, context_payload, run_chat_router_func):
    task_match_result = dict((state or {}).get("task_match_results", {}) or {})
    if _looks_like_flow_analysis_request(user_prompt):
        return {
            "action": "analyze_task",
            "reason": "Explicit current-flow analysis request.",
            "task_focus": str(user_prompt or "").strip(),
        }
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


def should_refresh_analysis_before_canvas_plan(user_prompt, state, route_result=None, canvas_context=None, model_name=None):
    task_match_result = dict((state or {}).get("task_match_results", {}) or {})
    lowered = str(user_prompt or "").strip().casefold()
    canvas_context = dict(canvas_context or {})
    node_count = len(list(canvas_context.get("nodes", []) or []))
    flow_description = str(task_match_result.get("flow_description", "") or "").strip()
    fast_local_mode = _fast_local_mode_selected(model_name)

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
    if fast_local_mode:
        strong_analysis_tokens = (
            "revise",
            "fix",
            "repair",
            "complete",
            "missing",
            "existing",
            "current flow",
            "this flow",
            "that flow",
            "initialize",
            "connect",
            "wire",
            "rename",
            "edit value",
            "update value",
        )
        return any(token in lowered for token in strong_analysis_tokens)
    if any(token in lowered for token in analysis_sensitive_tokens):
        return True

    route_action = str(dict(route_result or {}).get("action", "") or "").strip()
    if route_action == "execute_canvas_action" and node_count > 0:
        return True
    return False


def _build_reusable_skill_workflow_plan(context_payload):
    payload = dict(context_payload or {})
    recipes = list(payload.get("skill_execution_recipes", {}).get("recipes", []) or [])
    task_match_result = dict(payload.get("task_match_results", {}) or {})
    matched_skill_ids = {
        str(dict(item or {}).get("skill_id", "") or "").strip()
        for item in list(task_match_result.get("skill_matches", []) or [])
        if str(dict(item or {}).get("skill_id", "") or "").strip()
    }
    if not matched_skill_ids:
        return {}
    matched_tool_ids = {
        str(dict(item or {}).get("tool_id", "") or "").strip().casefold()
        for item in list(task_match_result.get("tool_matches", []) or [])
        if str(dict(item or {}).get("tool_id", "") or "").strip()
    }
    non_workspace_tool_ids = {tool_id for tool_id in matched_tool_ids if tool_id != "workspace"}
    candidates = []
    for recipe in recipes:
        recipe = dict(recipe or {})
        skill_id = str(recipe.get("skill_id", "") or "").strip()
        if skill_id not in matched_skill_ids:
            continue
        try:
            confidence = float(recipe.get("confidence", 0.0) or 0.0)
        except Exception:
            confidence = 0.0
        workflow_template = dict(recipe.get("workflow_template", {}) or {})
        workflow_path = str(workflow_template.get("path", "") or "").strip()
        if not workflow_path or confidence <= 0.8:
            continue
        recipe_tool_ids = {
            str(value or "").strip().casefold()
            for value in (
                list(recipe.get("recommended_tools", []) or [])
                + list(recipe.get("required_tools", []) or [])
                + list(recipe.get("tool_tags", []) or [])
                + list(dict(recipe.get("edit_recipe", {}) or {}).get("required_tools", []) or [])
            )
            if str(value or "").strip()
        }
        if recipe_tool_ids == {"workspace"}:
            recipe_tool_ids = set()
        if non_workspace_tool_ids and not (recipe_tool_ids & non_workspace_tool_ids):
            continue
        candidates.append(
            {
                "skill_id": skill_id,
                "title": str(recipe.get("title", "") or "").strip(),
                "confidence": confidence,
                "workflow_path": workflow_path,
                "tool_ids": sorted(recipe_tool_ids),
            }
        )
    if not candidates:
        return {}
    candidates.sort(key=lambda item: (-float(item.get("confidence", 0.0) or 0.0), str(item.get("title", "") or "").casefold()))
    selected = dict(candidates[0] or {})
    title = str(selected.get("title", "") or "").strip()
    skill_id = str(selected.get("skill_id", "") or "").strip()
    workflow_path = str(selected.get("workflow_path", "") or "").strip()
    return {
        "reply": "",
        "actions": [
            {
                "type": "load_workflow_json",
                "workflow_path": workflow_path,
                "source_skill_id": skill_id,
            }
        ],
        "planning_source": "deterministic_skill_template",
        "planning_path": "reuse_skill_workflow_json",
        "path_reason": (
            f"Loaded the matched skill template '{title}' because the canvas is empty and the matched skill score is higher than 0.8."
            if title else
            "Loaded a strong matched skill template because the canvas is empty and the matched skill score is higher than 0.8."
        ),
    }


def _eligible_template_skill_ids(context_payload):
    payload = dict(context_payload or {})
    task_match_result = dict(payload.get("task_match_results", {}) or {})
    matched_skill_ids = {
        str(dict(item or {}).get("skill_id", "") or "").strip()
        for item in list(task_match_result.get("skill_matches", []) or [])
        if str(dict(item or {}).get("skill_id", "") or "").strip()
    }
    if not matched_skill_ids:
        return set()
    matched_tool_ids = {
        str(dict(item or {}).get("tool_id", "") or "").strip().casefold()
        for item in list(task_match_result.get("tool_matches", []) or [])
        if str(dict(item or {}).get("tool_id", "") or "").strip()
    }
    non_workspace_tool_ids = {tool_id for tool_id in matched_tool_ids if tool_id != "workspace"}
    eligible = set()
    for recipe in list(dict(payload.get("skill_execution_recipes", {}) or {}).get("recipes", []) or []):
        recipe = dict(recipe or {})
        skill_id = str(recipe.get("skill_id", "") or "").strip()
        if skill_id not in matched_skill_ids:
            continue
        try:
            confidence = float(recipe.get("confidence", 0.0) or 0.0)
        except Exception:
            confidence = 0.0
        workflow_template = dict(recipe.get("workflow_template", {}) or {})
        workflow_path = str(workflow_template.get("path", "") or "").strip()
        if not workflow_path or confidence <= 0.8:
            continue
        recipe_tool_ids = {
            str(value or "").strip().casefold()
            for value in (
                list(recipe.get("recommended_tools", []) or [])
                + list(recipe.get("required_tools", []) or [])
                + list(recipe.get("tool_tags", []) or [])
                + list(dict(recipe.get("edit_recipe", {}) or {}).get("required_tools", []) or [])
            )
            if str(value or "").strip()
        }
        if recipe_tool_ids == {"workspace"}:
            recipe_tool_ids = set()
        if non_workspace_tool_ids and not (recipe_tool_ids & non_workspace_tool_ids):
            continue
        eligible.add(skill_id)
    return eligible


def _drop_unmatched_template_load_actions(plan, context_payload):
    finalized = dict(plan or {})
    eligible_skill_ids = _eligible_template_skill_ids(context_payload)
    kept_actions = []
    dropped = list(finalized.get("dropped_actions", []) or [])
    for action in list(finalized.get("actions", []) or []):
        item = dict(action or {})
        action_type = str(item.get("type", "") or "").strip()
        source_skill_id = str(item.get("source_skill_id", "") or "").strip()
        if action_type == "load_workflow_json" and source_skill_id and source_skill_id not in eligible_skill_ids:
            dropped.append(
                f"Dropped template load from ineligible skill '{source_skill_id}'."
            )
            continue
        kept_actions.append(item)
    finalized["actions"] = kept_actions
    if dropped:
        finalized["dropped_actions"] = dropped
    return finalized


def _is_simple_deterministic_canvas_plan(plan):
    actions = [dict(action or {}) for action in list(dict(plan or {}).get("actions", []) or [])]
    if len(actions) != 1:
        return False
    action = actions[0]
    action_type = str(action.get("type", "") or "").strip()
    if action_type in {
        "add_subflow",
        "connect_nodes",
        "rename_selected_node",
        "update_selected_text_node",
        "delete_node",
        "delete_selected_nodes",
    }:
        return True
    if action_type == "update_node":
        return True
    if action_type == "create_node":
        node_type = str(action.get("node_type", "") or "").strip()
        return node_type in {"data", "text"}
    return False


def _operation_id_for_canvas_action(action):
    item = dict(action or {})
    action_type = str(item.get("type", "") or "").strip()
    if action_type == "create_node":
        node_type = str(item.get("node_type", "") or "").strip()
        if node_type == "data":
            return "workspace.create_data_node"
        if node_type == "py":
            return "workspace.create_python_node"
        if node_type == "text":
            return "workspace.create_text_node"
        return "workspace.create_node"
    if action_type == "update_node":
        node_type = str(item.get("node_type", "") or "").strip()
        if node_type == "data":
            return "workspace.update_data_node"
        if node_type == "py":
            return "workspace.update_python_node"
        if node_type == "text":
            return "workspace.update_text_node"
        return "workspace.update_node"
    mapping = {
        "add_subflow": "workspace.add_subflow",
        "connect_nodes": "workspace.connect_ports",
        "delete_node": "workspace.delete_node",
        "delete_selected_nodes": "workspace.delete_selected_nodes",
        "load_workflow_json": "workspace.load_template",
        "rename_selected_node": "workspace.rename_selected_node",
        "update_selected_text_node": "workspace.update_selected_text_node",
        "validate_flow": "workspace.validate_flow",
    }
    return mapping.get(action_type, f"workspace.{action_type}" if action_type else "")


def _ensure_workspace_operations(plan):
    finalized = dict(plan or {})
    operations = [
        dict(item or {})
        for item in list(finalized.get("operations", []) or [])
        if isinstance(item, dict) and str(dict(item or {}).get("operation", "") or "").strip()
    ]
    if not operations:
        for action in list(finalized.get("actions", []) or []):
            item = dict(action or {})
            operation_id = _operation_id_for_canvas_action(item)
            if not operation_id:
                continue
            arguments = {
                key: value
                for key, value in item.items()
                if key != "type"
            }
            operations.append({"operation": operation_id, "arguments": arguments})
    if operations:
        finalized["operations"] = operations
        finalized.setdefault("planner_contract", "mcp_workspace_operations_v1")
        finalized.setdefault("planner_prompt_profile", str(finalized.get("planning_source", "") or "deterministic_canvas_action"))
    return finalized


def _collapse_local_plan_to_single_step(plan, user_prompt, model_name):
    finalized = dict(plan or {})
    goal_prompt = str(finalized.get("goal_prompt", "") or user_prompt or "").strip()
    if goal_prompt:
        finalized["goal_prompt"] = goal_prompt

    if not _fast_local_mode_selected(model_name):
        return _ensure_workspace_operations(finalized)

    actions = [dict(action or {}) for action in list(finalized.get("actions", []) or [])]
    if not actions:
        return _ensure_workspace_operations(finalized)

    first_action = dict(actions[0] or {})
    if str(first_action.get("type", "") or "").strip() == "create_node":
        try:
            action_count = int(first_action.get("count", 1) or 1)
        except Exception:
            action_count = 1
        if action_count > 1:
            first_action["count"] = 1

    finalized["actions"] = [first_action]
    finalized = _ensure_workspace_operations(finalized)
    finalized["planning_mode"] = "local_single_step"
    note = "Local stepwise mode is active, so this plan includes only the next build step."
    reply_text = str(finalized.get("reply", "") or "").strip()
    if note not in reply_text:
        finalized["reply"] = f"{reply_text}\n\n{note}".strip() if reply_text else note
    return finalized


def plan_canvas_actions(
    user_prompt,
    model_name,
    state,
    context_payload,
    canvas_context,
    run_workspace_action_plan_func,
    analysis_driven=False,
):
    local_single_step = _fast_local_mode_selected(model_name)
    fallback_plan = {"reply": "", "actions": []} if analysis_driven else _fallback_canvas_plan(user_prompt, canvas_context)
    direct_workspace_action = False if analysis_driven else _looks_like_direct_workspace_action_request(user_prompt)
    simple_direct_plan = direct_workspace_action and _is_simple_deterministic_canvas_plan(fallback_plan)
    context_payload = dict(context_payload or {})
    if "task_match_results" not in context_payload:
        context_payload["task_match_results"] = dict((state or {}).get("task_match_results", {}) or {})
    reusable_template_plan = {} if direct_workspace_action else _build_reusable_skill_workflow_plan(context_payload)
    existing_value_update_action = _extract_existing_node_value_update_action(user_prompt, canvas_context)
    revision_request = _extract_revision_request(user_prompt)
    is_revision_request = bool(revision_request)
    if simple_direct_plan:
        direct_plan = dict(fallback_plan or {})
        direct_plan["planning_source"] = "deterministic_canvas_action"
        direct_plan["planning_path"] = str(direct_plan.get("planning_path", "") or "edit_current_flow")
        direct_plan["path_reason"] = str(
            direct_plan.get("path_reason", "")
            or "The request is a direct Workspace canvas action, so QuESt used the canvas action tool instead of loading a skill template."
        )
        return _collapse_local_plan_to_single_step(direct_plan, user_prompt, model_name)
    if run_workspace_action_plan_func is None:
        return _collapse_local_plan_to_single_step(_ensure_workspace_operations(fallback_plan), user_prompt, model_name)

    try:
        task_match_result = dict((state or {}).get("task_match_results", {}) or {})
        skill_execution_recipes = dict(context_payload.get("skill_execution_recipes", {}) or {})
        if direct_workspace_action:
            task_match_result["skill_matches"] = []
            task_match_result["top_skill_matches"] = []
            task_match_result["best_workflow_template"] = {}
            skill_execution_recipes = {"recipes": []}
        planned = run_workspace_action_plan_func(
            user_prompt=user_prompt,
            canvas_context=dict(canvas_context or {}),
            task_match_result=task_match_result,
            pinned_context=list(context_payload.get("pinned_context", []) or []),
            attached_files=list(context_payload.get("attached_files", []) or []),
            attached_workflow_jsons=list(context_payload.get("attached_workflow_jsons", []) or []),
            workspace_relationship_context=dict(context_payload.get("workspace_relationship_context", {}) or {}),
            implicit_code_context=list(context_payload.get("implicit_code_context", []) or []),
            python_node_wrapper_rules=dict(context_payload.get("python_node_wrapper_rules", {}) or {}),
            skill_execution_recipes=skill_execution_recipes,
            recent_messages=list(context_payload.get("recent_messages", []) or []),
            selected_model=model_name,
            single_step_only=local_single_step,
            force_planning_path="edit_current_flow" if direct_workspace_action and len(list(dict(canvas_context or {}).get("nodes", []) or [])) > 0 else ("manual_canvas_build" if direct_workspace_action else None),
        )
    except Exception:
        if len(list(dict(canvas_context or {}).get("nodes", []) or [])) <= 0 and reusable_template_plan:
            return _collapse_local_plan_to_single_step(_ensure_workspace_operations(reusable_template_plan), user_prompt, model_name)
        if analysis_driven:
            return {"reply": "", "actions": [], "goal_prompt": str(user_prompt or "").strip()}
        return _collapse_local_plan_to_single_step(fallback_plan, user_prompt, model_name)

    planned = dict(planned or {})
    planned = _drop_unmatched_template_load_actions(planned, context_payload)
    node_count = len(list(dict(canvas_context or {}).get("nodes", []) or []))
    if node_count <= 0 and reusable_template_plan:
        planned_actions = list(planned.get("actions", []) or [])
        has_load_action = any(str(dict(action or {}).get("type", "") or "").strip() == "load_workflow_json" for action in planned_actions)
        if not planned_actions or not has_load_action:
            return _collapse_local_plan_to_single_step(_ensure_workspace_operations(reusable_template_plan), user_prompt, model_name)
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
        return _collapse_local_plan_to_single_step(_ensure_workspace_operations(planned), user_prompt, model_name)

    if list(planned.get("dropped_actions", []) or []):
        planned["planning_source"] = str(planned.get("planning_source", "") or "llm")
        return _collapse_local_plan_to_single_step(_ensure_workspace_operations(planned), user_prompt, model_name)

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
        return _collapse_local_plan_to_single_step(_ensure_workspace_operations(fallback_plan), user_prompt, model_name)

    planned["planning_source"] = "llm"
    return _collapse_local_plan_to_single_step(_ensure_workspace_operations(planned), user_prompt, model_name)


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
