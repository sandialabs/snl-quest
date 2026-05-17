import ast
import json
import re
from pathlib import Path
from typing import Any

from ..skill_library import get_quest_agent_root, load_skill_library
from ..skill_development import develop_skill_from_record
from ..tool_registry import write_active_tool_registry
from .. import workspace_actions


WORKSPACE_ACTION_TYPES = {
    "create_node": {
        "description": "Create a Workspace node.",
        "required_any": ["node_type"],
        "write": True,
    },
    "update_node": {
        "description": "Update an existing Workspace node.",
        "required_any": ["node_name", "name"],
        "write": True,
    },
    "add_subflow": {
        "description": "Create a new Workspace subflow.",
        "required_any": ["flow_name", "subflow_name", "name"],
        "write": True,
    },
    "connect_nodes": {
        "description": "Connect two Workspace nodes.",
        "required_any": ["source_node", "target_node"],
        "write": True,
    },
    "rename_selected_node": {
        "description": "Rename the selected node.",
        "required_any": ["new_name"],
        "write": True,
    },
    "update_selected_text_node": {
        "description": "Update the selected text node.",
        "required_any": ["text"],
        "write": True,
    },
    "delete_selected_nodes": {
        "description": "Delete selected nodes.",
        "required_any": [],
        "write": True,
    },
    "delete_node": {
        "description": "Delete a specific Workspace node by name.",
        "required_any": ["node_name", "name"],
        "write": True,
    },
    "load_workflow_json": {
        "description": "Load workflow JSON from a path or embedded content.",
        "required_any": ["workflow_path", "workflow_content"],
        "write": True,
    },
    "validate_flow": {
        "description": "Validate current Workspace flow facts.",
        "required_any": [],
        "write": False,
    },
}


WORKSPACE_OPERATION_TYPES = {
    f"workspace.{operation_type}": {
        **dict(metadata or {}),
        "operation": f"workspace.{operation_type}",
        "legacy_action_type": operation_type,
    }
    for operation_type, metadata in WORKSPACE_ACTION_TYPES.items()
}
WORKSPACE_OPERATION_TYPES.update(
    {
        "workspace.create_data_node": {
            **dict(WORKSPACE_ACTION_TYPES["create_node"]),
            "operation": "workspace.create_data_node",
            "legacy_action_type": "create_node",
            "default_arguments": {"node_type": "data"},
        },
        "workspace.create_python_node": {
            **dict(WORKSPACE_ACTION_TYPES["create_node"]),
            "operation": "workspace.create_python_node",
            "legacy_action_type": "create_node",
            "default_arguments": {"node_type": "py"},
        },
        "workspace.create_text_node": {
            **dict(WORKSPACE_ACTION_TYPES["create_node"]),
            "operation": "workspace.create_text_node",
            "legacy_action_type": "create_node",
            "default_arguments": {"node_type": "text"},
        },
        "workspace.update_data_node": {
            **dict(WORKSPACE_ACTION_TYPES["update_node"]),
            "operation": "workspace.update_data_node",
            "legacy_action_type": "update_node",
            "default_arguments": {"node_type": "data"},
        },
        "workspace.update_python_node": {
            **dict(WORKSPACE_ACTION_TYPES["update_node"]),
            "operation": "workspace.update_python_node",
            "legacy_action_type": "update_node",
            "default_arguments": {"node_type": "py"},
        },
        "workspace.update_text_node": {
            **dict(WORKSPACE_ACTION_TYPES["update_node"]),
            "operation": "workspace.update_text_node",
            "legacy_action_type": "update_node",
            "default_arguments": {"node_type": "text"},
        },
        "workspace.connect_ports": {
            **dict(WORKSPACE_ACTION_TYPES["connect_nodes"]),
            "operation": "workspace.connect_ports",
            "legacy_action_type": "connect_nodes",
        },
        "workspace.load_template": {
            **dict(WORKSPACE_ACTION_TYPES["load_workflow_json"]),
            "operation": "workspace.load_template",
            "legacy_action_type": "load_workflow_json",
        },
        "workspace.validate_flow": {
            **dict(WORKSPACE_ACTION_TYPES["validate_flow"]),
            "operation": "workspace.validate_flow",
            "legacy_action_type": "validate_flow",
        },
    }
)
LEGACY_ACTION_TO_OPERATION = {
    "add_subflow": "workspace.add_subflow",
    "connect_nodes": "workspace.connect_ports",
    "create_node": "workspace.create_node",
    "delete_node": "workspace.delete_node",
    "delete_selected_nodes": "workspace.delete_selected_nodes",
    "load_workflow_json": "workspace.load_template",
    "rename_selected_node": "workspace.rename_selected_node",
    "update_node": "workspace.update_node",
    "update_selected_text_node": "workspace.update_selected_text_node",
    "validate_flow": "workspace.validate_flow",
}


def list_workspace_actions() -> dict[str, Any]:
    actions = []
    for action_type, metadata in WORKSPACE_ACTION_TYPES.items():
        item = dict(metadata or {})
        item["type"] = action_type
        actions.append(item)
    actions.sort(key=lambda item: str(item.get("type", "") or ""))
    return {
        "actions": actions,
        "count": len(actions),
        "source": "quest_mcp_workspace_actions",
    }


def list_workspace_operations() -> dict[str, Any]:
    operations = []
    for operation_type, metadata in WORKSPACE_OPERATION_TYPES.items():
        item = dict(metadata or {})
        item["operation"] = operation_type
        operations.append(item)
    operations.sort(key=lambda item: str(item.get("operation", "") or ""))
    return {
        "operations": operations,
        "count": len(operations),
        "source": "quest_mcp_workspace_operations",
    }


def _operation_arguments(operation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(operation, dict):
        return {}
    arguments = operation.get("arguments", {})
    if isinstance(arguments, dict):
        return dict(arguments or {})
    return {}


def _operation_to_action(operation: dict[str, Any]) -> dict[str, Any]:
    item = dict(operation or {})
    operation_type = str(item.get("operation", "") or item.get("type", "") or "").strip()
    arguments = _operation_arguments(item)
    if not arguments:
        arguments = {
            key: value
            for key, value in item.items()
            if key not in {"operation", "arguments"}
        }
    metadata = dict(WORKSPACE_OPERATION_TYPES.get(operation_type, {}) or {})
    action = dict(metadata.get("default_arguments", {}) or {})
    action.update(dict(arguments or {}))
    action["type"] = str(metadata.get("legacy_action_type", "") or operation_type).strip()
    return action


def _operation_id_for_action(action_type: str, arguments: dict[str, Any]) -> str:
    action_text = str(action_type or "").strip()
    args = dict(arguments or {})
    if action_text == "create_node":
        node_type = str(args.get("node_type", "") or "").strip()
        if node_type == "data":
            return "workspace.create_data_node"
        if node_type == "py":
            return "workspace.create_python_node"
        if node_type == "text":
            return "workspace.create_text_node"
    if action_text == "update_node":
        node_type = str(args.get("node_type", "") or "").strip()
        if node_type == "data":
            return "workspace.update_data_node"
        if node_type == "py":
            return "workspace.update_python_node"
        if node_type == "text":
            return "workspace.update_text_node"
    return LEGACY_ACTION_TO_OPERATION.get(action_text, f"workspace.{action_text}" if action_text else "")


def _action_to_operation(action: dict[str, Any]) -> dict[str, Any]:
    item = dict(action or {})
    action_type = str(item.get("type", "") or item.get("operation", "") or "").strip()
    arguments = {
        key: value
        for key, value in item.items()
        if key not in {"type", "operation", "arguments"}
    }
    if isinstance(item.get("arguments", None), dict):
        arguments.update(dict(item.get("arguments", {}) or {}))
    if action_type.startswith("workspace."):
        return {
            "operation": action_type,
            "arguments": arguments,
        }
    return {
        "operation": _operation_id_for_action(action_type, arguments),
        "arguments": arguments,
    }


def _normalize_workspace_operation_plan(operation_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = dict(operation_plan or {})
    raw_operations = [
        dict(item or {})
        for item in list(plan.get("operations", []) or [])
        if isinstance(item, dict)
    ]
    if not raw_operations:
        raw_operations = [
            _action_to_operation(dict(item or {}))
            for item in list(plan.get("actions", []) or [])
            if isinstance(item, dict)
        ]
    operations = []
    actions = []
    for operation in raw_operations:
        normalized_operation = _action_to_operation(_operation_to_action(operation))
        operations.append(normalized_operation)
        actions.append(_operation_to_action(normalized_operation))
    plan["operations"] = operations
    plan["actions"] = actions
    return plan


def validate_workspace_action_plan(action_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = _normalize_workspace_operation_plan(action_plan)
    actions = [dict(item or {}) for item in list(plan.get("actions", []) or []) if isinstance(item, dict)]
    errors = []
    warnings = []
    for index, action in enumerate(actions, start=1):
        action_type = str(action.get("type", "") or "").strip()
        if not action_type:
            errors.append(f"Action {index} is missing type.")
            continue
        metadata = WORKSPACE_ACTION_TYPES.get(action_type)
        if metadata is None:
            errors.append(f"Action {index} has unsupported type `{action_type}`.")
            continue
        required_any = [str(item or "").strip() for item in list(metadata.get("required_any", []) or []) if str(item or "").strip()]
        if required_any and not any(action.get(field) not in (None, "", {}, []) for field in required_any):
            errors.append(f"Action {index} `{action_type}` requires one of: {', '.join(required_any)}.")
        if action_type == "connect_nodes":
            if not str(action.get("source_node", "") or "").strip():
                errors.append(f"Action {index} `connect_nodes` requires source_node.")
            if not str(action.get("target_node", "") or "").strip():
                errors.append(f"Action {index} `connect_nodes` requires target_node.")
        if action_type == "create_node":
            node_type = str(action.get("node_type", "") or "").strip()
            if node_type and node_type not in {"data", "py", "text"}:
                warnings.append(f"Action {index} `create_node` has nonstandard node_type `{node_type}`.")
    for index, operation in enumerate(list(plan.get("operations", []) or []), start=1):
        operation_id = str(dict(operation or {}).get("operation", "") or "").strip()
        if operation_id and operation_id not in WORKSPACE_OPERATION_TYPES:
            errors.append(f"Operation {index} has unsupported operation id `{operation_id}`.")
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "action_count": len(actions),
        "operation_count": len(list(plan.get("operations", []) or [])),
        "source": "quest_mcp_workspace_actions",
    }


def validate_workspace_operation_plan(operation_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    validation = validate_workspace_action_plan(operation_plan)
    validation["source"] = "quest_mcp_workspace_operations"
    return validation


def execute_workspace_operation_plan(workflow: Any, operation_plan: dict[str, Any] | None = None) -> list[str]:
    normalized_plan = _normalize_workspace_operation_plan(operation_plan)
    validation = validate_workspace_operation_plan(normalized_plan)
    if not bool(validation.get("valid", False)):
        plan = dict(operation_plan or {})
        plan.setdefault("execution_notes", [])
        plan["execution_notes"].extend(list(validation.get("errors", []) or []))
        return []
    if operation_plan is not None:
        operation_plan["operations"] = list(normalized_plan.get("operations", []) or [])
        operation_plan["actions"] = list(normalized_plan.get("actions", []) or [])
        operation_plan["mcp_operation_contract"] = True
        operation_plan.setdefault("execution_notes", [])
        write_actions = []
        for action in list(operation_plan.get("actions", []) or []):
            item = dict(action or {})
            if str(item.get("type", "") or "").strip() == "validate_flow":
                operation_plan["execution_notes"].append(
                    "validate_flow is a read-only MCP operation; use analyze_workspace_canvas for validation facts."
                )
                continue
            write_actions.append(item)
        if not write_actions:
            return []
        operation_plan["actions"] = write_actions
        return workspace_actions.execute_canvas_actions(workflow, operation_plan)
    normalized_plan.setdefault("execution_notes", [])
    normalized_plan["actions"] = [
        dict(action or {})
        for action in list(normalized_plan.get("actions", []) or [])
        if str(dict(action or {}).get("type", "") or "").strip() != "validate_flow"
    ]
    if not list(normalized_plan.get("actions", []) or []):
        normalized_plan["execution_notes"].append(
            "validate_flow is a read-only MCP operation; use analyze_workspace_canvas for validation facts."
        )
        return []
    return workspace_actions.execute_canvas_actions(workflow, normalized_plan)


def execute_workspace_action_plan(workflow: Any, action_plan: dict[str, Any] | None = None) -> list[str]:
    return execute_workspace_operation_plan(workflow, action_plan)


def _tokenize(text: str) -> set[str]:
    raw_tokens = re.findall(r"[a-zA-Z0-9_]+", str(text or "").casefold())
    stopwords = {
        "about", "agent", "also", "and", "create", "data", "file", "files",
        "for", "from", "have", "into", "need", "node", "nodes",
        "please", "quest", "task", "that", "the", "then", "this", "tool",
        "tools", "use", "using", "value", "with", "workflow", "workflows", "your",
    }
    return {token for token in raw_tokens if len(token) > 2 and token not in stopwords}


def _score_tokens(query_tokens: set[str], candidate_tokens: set[str]) -> float:
    if not query_tokens or not candidate_tokens:
        return 0.0
    return len(query_tokens.intersection(candidate_tokens)) / max(1, len(query_tokens))


_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _extract_task_features(text: str) -> dict[str, Any]:
    lowered = str(text or "").casefold()
    numbers = [int(value) for value in re.findall(r"\b\d+\b", lowered)]
    for word, value in _NUMBER_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            numbers.append(value)
    arithmetic_add = bool(re.search(r"\b(add|sum|plus|total)\b", lowered))
    arithmetic_multiply = bool(re.search(r"\b(multiply|multiplication|product)\b", lowered))
    square = bool(re.search(r"\b(square|squared)\b", lowered) or "**2" in lowered or "^2" in lowered)
    btm = bool(re.search(r"\b(btm|behind[- ]the[- ]meter|storage|battery|pv|tariff|dispatch|optimization|savings)\b", lowered))
    direct_workspace_action = bool(re.search(r"\b(create|add|update|set|connect|delete|remove)\b", lowered)) and bool(re.search(r"\b(data node|datanode|python node|pynode|text node|node)\b", lowered))
    requested_count = 0
    if arithmetic_add and numbers:
        count_candidates = [
            value for value in numbers
            if 1 < value <= 50
        ]
        requested_count = count_candidates[0] if count_candidates else 0
    return {
        "tokens": _tokenize(text),
        "numbers": numbers,
        "requested_count": requested_count,
        "arithmetic_add": arithmetic_add,
        "arithmetic_multiply": arithmetic_multiply,
        "square": square,
        "btm": btm,
        "direct_workspace_action": direct_workspace_action,
    }


def _skill_text(skill: Any) -> str:
    parts = [
        str(getattr(skill, "skill_id", "") or ""),
        str(getattr(skill, "title", "") or ""),
        str(getattr(skill, "summary", "") or ""),
        str(getattr(skill, "description", "") or ""),
    ]
    for field in ("tags", "tool_tags", "structural_tags", "task_pattern_tags", "recommended_tools", "required_tools"):
        parts.extend(str(value or "") for value in list(getattr(skill, field, []) or []))
    return "\n".join(part for part in parts if part)


def _skill_workflow_features(skill: Any) -> dict[str, Any]:
    workflow_path = _skill_workflow_json_path(skill)
    features = {
        "data_node_count": 0,
        "python_node_count": 0,
        "connection_count": 0,
        "python_input_count": 0,
        "square": False,
        "add": False,
        "multiply": False,
        "btm": False,
        "available": False,
    }
    if not workflow_path:
        return features
    try:
        path = Path(workflow_path)
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        analysis = analyze_workflow_json_template(data)
    except Exception:
        return features
    data_nodes = list(analysis.get("data_nodes", []) or [])
    python_nodes = list(analysis.get("python_nodes", []) or [])
    connections = list(analysis.get("connections", []) or [])
    wrappers = "\n".join(str(dict(node or {}).get("wrapper_text", "") or "") for node in python_nodes)
    combined = "\n".join([
        _skill_text(skill),
        wrappers,
        " ".join(str(dict(node or {}).get("name", "") or "") for node in data_nodes + python_nodes),
    ]).casefold()
    features.update({
        "data_node_count": len(data_nodes),
        "python_node_count": len(python_nodes),
        "connection_count": len(connections),
        "python_input_count": max((len(list(dict(node or {}).get("input_ports", []) or [])) for node in python_nodes), default=0),
        "square": bool("** 2" in wrappers or "**2" in wrappers or re.search(r"\b(square|squared)\b", combined)),
        "add": bool(re.search(r"\b(add|sum|plus|total)\b", combined) or "+" in wrappers),
        "multiply": bool(re.search(r"\b(multiply|multiplication|product)\b", combined) or "*" in wrappers),
        "btm": bool(re.search(r"\b(btm|behind[- ]the[- ]meter|battery|storage|pv|tariff|dispatch|optimization)\b", combined)),
        "available": True,
    })
    return features


def _score_skill_against_task(skill: Any, task_features: dict[str, Any]) -> tuple[float, list[str]]:
    skill_features = _skill_workflow_features(skill)
    candidate_tokens = _tokenize(_skill_text(skill))
    query_tokens = set(task_features.get("tokens", set()) or set())
    overlap = _score_tokens(query_tokens, candidate_tokens)
    score = overlap * 0.45
    reasons = []
    shared = sorted(query_tokens.intersection(candidate_tokens))
    if shared:
        reasons.append("matched terms: " + ", ".join(shared[:6]))
    title = str(getattr(skill, "title", "") or "").casefold()
    summary_text = _skill_text(skill).casefold()

    if task_features.get("direct_workspace_action"):
        score -= 0.35
        reasons.append("direct node operation, not a full-flow skill")

    if task_features.get("arithmetic_add"):
        if skill_features.get("add") or re.search(r"\b(add|sum|plus|total)\b", summary_text):
            score += 0.25
            reasons.append("matches addition intent")
        elif skill_features.get("multiply") or "multiplication" in title:
            score -= 0.25
            reasons.append("penalized multiplication skill for addition task")
    if task_features.get("arithmetic_multiply"):
        if skill_features.get("multiply") or "multiplication" in title:
            score += 0.25
            reasons.append("matches multiplication intent")
        elif skill_features.get("add"):
            score -= 0.18
            reasons.append("penalized addition skill for multiplication task")
    if task_features.get("square"):
        if skill_features.get("square"):
            score += 0.22
            reasons.append("matches square step")
        else:
            score -= 0.15
            reasons.append("missing square step")
    elif skill_features.get("square"):
        score -= 0.18
        reasons.append("template includes unrequested square step")

    requested_count = int(task_features.get("requested_count", 0) or 0)
    template_count = int(skill_features.get("python_input_count", 0) or skill_features.get("data_node_count", 0) or 0)
    if requested_count and template_count:
        distance = abs(template_count - requested_count)
        if distance == 0:
            score += 0.28
            reasons.append(f"input count matches requested {requested_count}")
        else:
            score -= min(0.45, 0.09 * distance)
            reasons.append(f"input count differs: template {template_count}, requested {requested_count}")

    if task_features.get("btm"):
        if skill_features.get("btm"):
            score += 0.35
            reasons.append("matches BTM/storage domain")
        else:
            score -= 0.3
            reasons.append("not a BTM/storage skill")
    elif skill_features.get("btm"):
        score -= 0.25
        reasons.append("BTM skill not requested")

    if (task_features.get("arithmetic_add") or task_features.get("arithmetic_multiply")) and skill_features.get("btm"):
        score -= 0.35
        reasons.append("penalized BTM skill for arithmetic Workspace task")

    if str(getattr(skill, "status", "") or "").casefold() == "validated":
        score += 0.04
    if str(getattr(skill, "validation_status", "") or "").casefold() == "passed":
        score += 0.04
    score = max(0.0, min(1.0, score))
    if not reasons:
        reasons.append("weak keyword overlap")
    return score, reasons


def _clean_list(values: Any, limit: int | None = None) -> list[str]:
    cleaned = []
    for value in list(values or []):
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
        if limit is not None and len(cleaned) >= limit:
            break
    return cleaned


def _canvas_context_search_text(canvas_context: dict[str, Any] | None = None) -> str:
    context = dict(canvas_context or {})
    parts = []
    for node in list(context.get("nodes", []) or []):
        item = dict(node or {})
        for key in (
            "name",
            "node_name",
            "type",
            "node_type",
            "display_name",
            "variable_name",
            "node_input_variable",
            "value",
            "node_input_value",
            "text",
            "node_imports",
            "imports",
            "node_function_wrapper",
            "wrapper_text",
        ):
            value = str(item.get(key, "") or "").strip()
            if value:
                parts.append(value)
        for key in ("input_ports", "output_ports"):
            values = item.get(key, [])
            if isinstance(values, (list, tuple, set)):
                parts.extend(str(value or "").strip() for value in values if str(value or "").strip())
    for connection in list(context.get("connections", []) or []):
        item = dict(connection or {})
        parts.append(" ".join(str(item.get(key, "") or "").strip() for key in item.keys()))
    for key in ("current_flow_name", "current_flow_type", "workflow_name", "workflow_type", "flow_name", "flow_type", "selected_node_name", "selected_node_type"):
        value = str(context.get(key, "") or "").strip()
        if value:
            parts.append(value)
    return "\n".join(part for part in parts if part)


def _skill_workflow_json_path(skill: Any) -> str:
    return str(getattr(skill, "workflow_json_path", "") or "").strip()


def _node_kind(node_type: str) -> str:
    lowered = str(node_type or "").casefold()
    if "datanode" in lowered or lowered in {"data", "data_node"}:
        return "data"
    if "pynode" in lowered or lowered in {"py", "python", "python_node"}:
        return "py"
    if "textnode" in lowered or lowered in {"text", "text_node"}:
        return "text"
    return lowered


def _expected_ports_from_wrapper(wrapper_text: str) -> tuple[list[str], list[str]]:
    text = str(wrapper_text or "").strip()
    if not text:
        return [], []
    input_ports: list[str] = []
    output_ports: list[str] = []
    try:
        tree = ast.parse(text)
    except Exception:
        tree = None
    if tree is not None:
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            input_ports = [
                str(arg.arg).strip()
                for arg in list(node.args.args or [])
                if str(arg.arg).strip() and str(arg.arg).strip() != "self"
            ]
            for child in ast.walk(node):
                if not isinstance(child, ast.Return):
                    continue
                value = child.value
                if isinstance(value, ast.Dict):
                    for key in list(value.keys or []):
                        if isinstance(key, ast.Constant) and isinstance(key.value, str) and key.value.strip():
                            output_ports.append(key.value.strip())
                elif isinstance(value, ast.Name):
                    output_ports.append(value.id)
            break
    if not input_ports:
        match = re.search(r"def\s+[A-Za-z_]\w*\s*\(([^)]*)\)", text)
        if match:
            raw_args = str(match.group(1) or "")
            input_ports = [
                part.split("=", 1)[0].split(":", 1)[0].strip()
                for part in raw_args.split(",")
                if part.split("=", 1)[0].split(":", 1)[0].strip()
                and part.split("=", 1)[0].split(":", 1)[0].strip() != "self"
            ]
    if not output_ports:
        for key in re.findall(r"['\"]([A-Za-z_]\w*)['\"]\s*:", text):
            if key not in output_ports:
                output_ports.append(key)
    return _clean_list(input_ports), _clean_list(output_ports)


def _python_node_brief_description(node_name: str, wrapper_text: str, input_ports: list[str], output_ports: list[str]) -> str:
    name = str(node_name or "Python node").strip()
    inputs = ", ".join(input_ports) if input_ports else "no inferred inputs"
    outputs = ", ".join(output_ports) if output_ports else "no inferred outputs"
    first_line = str(wrapper_text or "").strip().splitlines()[0].strip() if str(wrapper_text or "").strip() else ""
    if first_line.startswith("def "):
        return f"Consumes {inputs} and returns {outputs}."
    return f"{name} consumes {inputs} and returns {outputs}."


def _requested_numeric_input_count(task_text: str) -> int | None:
    text = str(task_text or "").casefold()
    if not text:
        return None
    count_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }
    count_pattern = r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
    intent_pattern = (
        rf"(?:add|sum|total)\s+(?:up\s+)?{count_pattern}\s+"
        r"(?:number|numbers|numeric inputs|inputs|values)"
    )
    match = re.search(intent_pattern, text)
    if not match:
        return None
    token = str(match.group(1) or "").strip()
    if token.isdigit():
        try:
            return int(token)
        except Exception:
            return None
    return count_words.get(token)


def _connection_endpoint(connection: dict[str, Any]) -> tuple[str, str, str, str]:
    item = dict(connection or {})
    source_name = str(item.get("source_node", "") or "").strip()
    source_port = str(item.get("source_port", "") or "").strip()
    target_name = str(item.get("target_node", "") or "").strip()
    target_port = str(item.get("target_port", "") or "").strip()
    if (not source_name or not source_port) and str(item.get("from_port", "") or "").strip():
        parts = str(item.get("from_port", "") or "").strip().rsplit(".", 1)
        if len(parts) == 2:
            source_name, source_port = parts[0].strip(), parts[1].strip()
    if (not target_name or not target_port) and str(item.get("to_port", "") or "").strip():
        parts = str(item.get("to_port", "") or "").strip().rsplit(".", 1)
        if len(parts) == 2:
            target_name, target_port = parts[0].strip(), parts[1].strip()
    return source_name, source_port, target_name, target_port


def _wrapper_task_alignment_parts(
    task_text: str,
    data_nodes: list[dict[str, Any]],
    python_nodes: list[dict[str, Any]],
    connections: list[dict[str, Any]],
    missing_parts: list[str],
) -> tuple[list[str], list[str]]:
    requested_count = _requested_numeric_input_count(task_text)
    if requested_count is None or requested_count <= 0:
        return [], _clean_list(missing_parts)
    unexpected = []
    missing = list(missing_parts or [])
    extra_input_keys: set[tuple[str, str]] = set()
    required_input_keys: set[tuple[str, str]] = set()
    data_source_keys = {
        (
            str(dict(node or {}).get("name", "") or "").strip().casefold(),
            str(dict(node or {}).get("port", "") or "").strip().casefold(),
        )
        for node in list(data_nodes or [])
        if str(dict(node or {}).get("name", "") or "").strip()
    }
    if len(data_nodes) < requested_count:
        missing.append(
            f"The task asks for {requested_count} numeric inputs, but the current flow has {len(data_nodes)} data node(s)."
        )
    for node in list(python_nodes or []):
        input_ports = _clean_list(dict(node or {}).get("input_ports", []))
        node_name = str(dict(node or {}).get("name", "") or "Python node").strip()
        if len(input_ports) < requested_count:
            missing.append(
                f"Python node `{node_name}` exposes {len(input_ports)} input port(s), but the task asks for {requested_count} numeric inputs."
            )
        for input_name in input_ports[:requested_count]:
            required_input_keys.add((node_name.casefold(), str(input_name or "").strip().casefold()))
        if len(input_ports) > requested_count:
            extra_inputs = [
                str(name or "").strip()
                for name in input_ports[requested_count:]
                if str(name or "").strip()
            ]
            for input_name in extra_inputs:
                extra_input_keys.add((node_name.casefold(), input_name.casefold()))
            unexpected.append(
                f"Python node `{node_name}` wrapper requires extra input port(s) {', '.join(f'`{name}`' for name in extra_inputs)} beyond the task's {requested_count} numeric inputs."
            )

    required_data_sources: set[tuple[str, str]] = set()
    extra_data_sources: set[tuple[str, str]] = set()
    connected_data_sources: set[tuple[str, str]] = set()
    for connection in list(connections or []):
        source_name, source_port, target_name, target_port = _connection_endpoint(connection)
        if not source_name or not target_name or not target_port:
            continue
        target_key = (target_name.casefold(), target_port.casefold())
        source_key = (source_name.casefold(), source_port.casefold())
        if source_key in data_source_keys:
            connected_data_sources.add(source_key)
        if target_key in required_input_keys:
            required_data_sources.add(source_key)
        if target_key in extra_input_keys:
            extra_data_sources.add(source_key)
            unexpected.append(
                f"Data node `{source_name}` feeds extra wrapper input `{target_name}.{target_port}` that is not required by the task."
            )

    if len(connected_data_sources) < requested_count:
        missing.append(
            f"The task asks for {requested_count} connected numeric inputs, but the current flow has {len(connected_data_sources)} connected data input(s)."
        )

    if len(data_nodes) > requested_count:
        for node in list(data_nodes or []):
            node_name = str(dict(node or {}).get("name", "") or "").strip()
            port_name = str(dict(node or {}).get("port", "") or "").strip()
            source_key = (node_name.casefold(), port_name.casefold())
            if source_key in required_data_sources:
                continue
            if source_key in extra_data_sources:
                continue
            if node_name:
                unexpected.append(
                    f"Data node `{node_name}` is not connected to a required Python wrapper input for this task."
                )

    filtered_missing = []
    for item in list(missing or []):
        text = str(item or "").strip()
        lowered = text.casefold()
        if any(
            f"`{node}.{port}`".casefold() in lowered
            or f"{node}.{port}".casefold() in lowered
            for node, port in extra_input_keys
        ):
            continue
        filtered_missing.append(text)
    return _clean_list(unexpected), _clean_list(filtered_missing)


def analyze_workspace_canvas(canvas_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = dict(canvas_snapshot or {})
    node_records = [
        dict(item or {})
        for item in list(snapshot.get("nodes", []) or [])
        if isinstance(item, dict)
    ]
    connection_records = [
        dict(item or {})
        for item in list(snapshot.get("connections", []) or [])
        if isinstance(item, dict)
    ]
    data_nodes = []
    python_nodes = []
    connections = []
    target_ports_by_node: dict[str, set[str]] = {}
    for item in connection_records:
        source_name = str(item.get("source_node", "") or item.get("from_node", "") or "").strip()
        source_port = str(item.get("source_port", "") or "").strip()
        target_name = str(item.get("target_node", "") or item.get("to_node", "") or "").strip()
        target_port = str(item.get("target_port", "") or "").strip()
        if target_name and target_port:
            target_ports_by_node.setdefault(target_name.casefold(), set()).add(target_port.casefold())
        if source_name and source_port and target_name and target_port:
            connections.append({
                "from_port": f"{source_name}.{source_port}",
                "to_port": f"{target_name}.{target_port}",
                "source_node": source_name,
                "source_port": source_port,
                "target_node": target_name,
                "target_port": target_port,
            })

    for record in sorted(node_records, key=lambda item: str(dict(item or {}).get("node_name", "") or dict(item or {}).get("name", "") or "").casefold()):
        node_name = str(record.get("node_name", "") or record.get("name", "") or "").strip()
        node_type = _node_kind(str(record.get("node_type", "") or record.get("type", "") or ""))
        if not node_name:
            continue
        input_ports = _clean_list(record.get("input_ports", []))
        output_ports = _clean_list(record.get("output_ports", []))
        if node_type == "data":
            variable_name = str(record.get("node_input_variable", "") or record.get("variable_name", "") or "").strip()
            port_name = variable_name or (output_ports[0] if output_ports else "output")
            data_nodes.append({
                "name": node_name,
                "port": port_name,
                "value": str(record.get("node_input_value", "") or record.get("value", "") or "").strip(),
                "variable_name": variable_name,
            })
        elif node_type == "py":
            wrapper_text = str(record.get("node_function_wrapper", "") or record.get("wrapper_text", "") or record.get("code", "") or "").strip()
            expected_inputs, expected_outputs = _expected_ports_from_wrapper(wrapper_text)
            if not input_ports:
                input_ports = list(expected_inputs or [])
            if not output_ports:
                output_ports = list(expected_outputs or [])
            python_nodes.append({
                "name": node_name,
                "input_ports": input_ports,
                "output_ports": output_ports,
                "brief_description": _python_node_brief_description(node_name, wrapper_text, input_ports, output_ports),
                "wrapper_text": wrapper_text,
            })

    missing_parts = []
    if not data_nodes and not python_nodes and not connections:
        missing_parts.append("Canvas is empty.")
    elif not connections and (len(data_nodes) + len(python_nodes)) > 1:
        missing_parts.append("The current flow has nodes but no connections yet.")

    data_sources_by_port: dict[str, list[tuple[str, str]]] = {}
    for entry in data_nodes:
        variable_name = str(entry.get("variable_name", "") or "").strip()
        port_name = str(entry.get("port", "") or "").strip()
        node_name = str(entry.get("name", "") or "").strip()
        node_value = str(entry.get("value", "") or "").strip()
        if not variable_name:
            missing_parts.append(f"Data node `{node_name}` is missing its output variable name.")
        if not node_value:
            missing_parts.append(f"Data node `{node_name}` has no initialized value.")
        if port_name:
            data_sources_by_port.setdefault(port_name.casefold(), []).append((node_name, port_name))

    for entry in python_nodes:
        node_name = str(entry.get("name", "") or "").strip()
        wrapper_text = str(entry.get("wrapper_text", "") or "").strip()
        input_ports = _clean_list(entry.get("input_ports", []))
        output_ports = _clean_list(entry.get("output_ports", []))
        connected_input_ports = set(target_ports_by_node.get(node_name.casefold(), set()) or set())
        if not wrapper_text:
            missing_parts.append(f"Python node `{node_name}` is missing wrapper code.")
        if not input_ports:
            missing_parts.append(f"Python node `{node_name}` has no inferred input ports yet.")
        if not output_ports:
            missing_parts.append(f"Python node `{node_name}` has no inferred output ports yet.")
        for input_name in input_ports:
            input_key = str(input_name or "").strip().casefold()
            if not input_key or input_key in connected_input_ports:
                continue
            matching_sources = list(data_sources_by_port.get(input_key, []) or [])
            if len(matching_sources) == 1:
                source_name, source_port = matching_sources[0]
                missing_parts.append(f"Connect `{source_name}.{source_port}` to `{node_name}.{input_name}`.")
            elif len(matching_sources) > 1:
                choice_text = ", ".join(f"`{source_name}.{source_port}`" for source_name, source_port in matching_sources[:3])
                missing_parts.append(f"Connect one matching source ({choice_text}) to `{node_name}.{input_name}`.")
            else:
                missing_parts.append(
                    f"Missing input source for `{node_name}.{input_name}`: create a data node with output variable `{input_name}` and connect it to `{node_name}.{input_name}`."
                )

    deduped_missing_parts = _clean_list(missing_parts)
    result = {
        "workflow_name": str(snapshot.get("workflow_name", "") or snapshot.get("flow_name", "") or "").strip(),
        "workflow_type": str(snapshot.get("workflow_type", "") or snapshot.get("flow_type", "") or "").strip(),
        "data_nodes": data_nodes,
        "python_nodes": python_nodes,
        "connections": connections,
        "missing_parts": deduped_missing_parts,
        "source": "quest_mcp_workspace_readonly_facts",
    }
    subflow_results = []
    for index, subflow in enumerate(list(snapshot.get("subflows", []) or [])):
        if not isinstance(subflow, dict):
            continue
        subflow_analysis = analyze_workspace_canvas(subflow)
        subflow_analysis["flow_name"] = str(
            subflow.get("workflow_name", "")
            or subflow.get("flow_name", "")
            or subflow_analysis.get("flow_name", "")
            or f"Subflow {index + 1}"
        ).strip()
        subflow_analysis["flow_type"] = str(
            subflow.get("workflow_type", "")
            or subflow.get("flow_type", "")
            or subflow_analysis.get("flow_type", "")
            or "sub-flow"
        ).strip()
        subflow_results.append(subflow_analysis)
    if subflow_results:
        result["subflows"] = subflow_results
        result["subflow_count"] = len(subflow_results)
    return result


def _workflow_json_to_canvas_snapshot(workflow_json: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(workflow_json or {})
    node_rows = [
        dict(item or {})
        for item in list(data.get("nodes_df", []) or [])
        if isinstance(item, dict)
    ]
    node_name_by_id = {
        str(row.get("node_id", "") or "").strip(): str(row.get("node_name", "") or "").strip()
        for row in node_rows
        if str(row.get("node_id", "") or "").strip()
    }
    node_records = []
    for row in node_rows:
        node_type = _node_kind(str(row.get("node_type", "") or ""))
        record = {
            "node_name": str(row.get("node_name", "") or "").strip(),
            "node_type": node_type,
            "node_input_variable": str(row.get("node_input_variable", "") or "").strip(),
            "node_input_value": str(row.get("node_input_value", "") or ""),
            "node_function_wrapper": str(row.get("node_function_wrapper", "") or ""),
        }
        if node_type == "py":
            inputs, outputs = _expected_ports_from_wrapper(record["node_function_wrapper"])
            record["input_ports"] = inputs
            record["output_ports"] = outputs
        node_records.append(record)

    connection_records = []
    for row in list(data.get("connections_df", []) or []):
        item = dict(row or {})
        source_name = node_name_by_id.get(str(item.get("from_node", "") or "").strip(), "")
        target_name = node_name_by_id.get(str(item.get("to_node", "") or "").strip(), "")
        mapping = dict(item.get("mapping", {}) or {}) if isinstance(item.get("mapping"), dict) else {}
        for source_port, target_port in mapping.items():
            connection_records.append({
                "source_node": source_name,
                "source_port": str(source_port or "").strip(),
                "target_node": target_name,
                "target_port": str(target_port or "").strip(),
            })
    subflows = [
        _workflow_json_to_canvas_snapshot(item)
        for item in list(data.get("subflows_df", []) or [])
        if isinstance(item, dict)
    ]
    return {
        "workflow_name": str(data.get("flow_name", "") or "").strip(),
        "workflow_type": str(data.get("flow_type", "") or "").strip(),
        "nodes": node_records,
        "connections": connection_records,
        "subflows": subflows,
    }


def analyze_workflow_json_template(workflow_json: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return MCP read-only facts for a workflow JSON object before it is loaded."""
    return analyze_workspace_canvas(_workflow_json_to_canvas_snapshot(workflow_json))


def _load_tools(quest_agent_root: str | Path | None = None) -> list[dict[str, Any]]:
    registry = write_active_tool_registry(get_quest_agent_root(quest_agent_root))
    return [dict(item or {}) for item in list(registry.get("tools", []) or [])]


def _load_skills(quest_agent_root: str | Path | None = None) -> list[Any]:
    library = load_skill_library(get_quest_agent_root(quest_agent_root))
    return list(library.get("skills", []) or [])


def list_active_tools(quest_agent_root: str | Path | None = None) -> dict[str, Any]:
    tools = [
        {
            "tool_id": str(tool.get("tool_id", "") or ""),
            "name": str(tool.get("name", "") or ""),
            "category": str(tool.get("category", "") or ""),
            "description": str(tool.get("description", "") or ""),
            "typical_tasks": _clean_list(tool.get("typical_tasks", []), 5),
            "workflow_roles": _clean_list(tool.get("workflow_roles", []), 5),
        }
        for tool in _load_tools(quest_agent_root)
        if bool(tool.get("active", True))
    ]
    return {"tools": tools, "count": len(tools)}


def search_tools(query: str, quest_agent_root: str | Path | None = None, limit: int = 8) -> dict[str, Any]:
    task_features = _extract_task_features(query)
    query_tokens = set(task_features.get("tokens", set()) or set())
    matches = []
    for tool in _load_tools(quest_agent_root):
        tool_id = str(tool.get("tool_id", "") or "").strip()
        if tool_id == "workspace":
            continue
        candidate_tokens = set()
        for field in ("tool_id", "name", "description", "search_key"):
            candidate_tokens.update(_tokenize(tool.get(field, "")))
        for field in ("aliases", "input_types", "output_types", "typical_tasks", "workflow_roles"):
            for value in list(tool.get(field, []) or []):
                candidate_tokens.update(_tokenize(value))
        score = _score_tokens(query_tokens, candidate_tokens)
        if tool_id == "btm" and bool(task_features.get("btm")):
            score = max(score, 0.75)
        if score < 0.18:
            score = 0.0
        if score <= 0:
            continue
        shared = sorted(query_tokens.intersection(candidate_tokens))
        matches.append({
            "tool_id": tool_id,
            "name": str(tool.get("name", "") or ""),
            "score": round(score, 4),
            "confidence": round(score, 4),
            "reason": "MCP shortlist candidate: " + (", ".join(shared[:8]) if shared else "domain keyword match"),
            "description": str(tool.get("description", "") or ""),
        })
    matches.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("name", "")).casefold()))
    return {"matches": matches[: max(1, int(limit or 1))], "query_tokens": sorted(query_tokens)}


def search_skills(query: str, quest_agent_root: str | Path | None = None, limit: int = 8) -> dict[str, Any]:
    task_features = _extract_task_features(query)
    if bool(task_features.get("direct_workspace_action")):
        return {"matches": [], "query_tokens": sorted(set(task_features.get("tokens", set()) or set()))}
    tool_result = search_tools(query, quest_agent_root=quest_agent_root, limit=limit)
    related_tool_ids = {
        str(item.get("tool_id", "") or "").strip()
        for item in list(tool_result.get("matches", []) or [])
        if str(item.get("tool_id", "") or "").strip()
    }
    query_tokens = _tokenize(query)
    matches = []
    for skill in _load_skills(quest_agent_root):
        skill_tools = {
            str(tool_id or "").strip()
            for tool_id in list(getattr(skill, "recommended_tools", []) or [])
            + list(getattr(skill, "required_tools", []) or [])
            + list(getattr(skill, "tool_tags", []) or [])
            if str(tool_id or "").strip() and str(tool_id or "").strip() != "workspace"
        }
        skill_text_tokens = _tokenize(_skill_text(skill))
        text_overlap = query_tokens.intersection(skill_text_tokens)
        tool_overlap = related_tool_ids.intersection(skill_tools)
        skill_type = str(getattr(skill, "skill_type", "") or "").strip()
        if related_tool_ids:
            if not tool_overlap and skill_type != "general_python":
                continue
            if not tool_overlap and skill_type == "general_python" and not text_overlap:
                continue
        else:
            if skill_type != "general_python":
                continue
            if not text_overlap:
                continue
        score = 0.5
        if tool_overlap:
            score += 0.2
        if text_overlap:
            score += 0.1
        score = min(0.8, score)
        reasons = []
        if tool_overlap:
            reasons.append("related tools: " + ", ".join(sorted(tool_overlap)[:5]))
        if text_overlap:
            reasons.append("catalog terms: " + ", ".join(sorted(text_overlap)[:6]))
        if not reasons:
            reasons.append("general Python Workspace fallback")
        matches.append({
            "skill_id": str(getattr(skill, "skill_id", "") or ""),
            "title": str(getattr(skill, "title", "") or ""),
            "skill_type": skill_type,
            "status": str(getattr(skill, "status", "") or ""),
            "validation_status": str(getattr(skill, "validation_status", "") or ""),
            "score": round(score, 4),
            "confidence": round(score, 4),
            "reason": "MCP shortlist candidate; " + "; ".join(reasons[:4]),
            "recommended_tools": _clean_list(getattr(skill, "recommended_tools", []), 6),
            "required_tools": _clean_list(getattr(skill, "required_tools", []), 6),
            "related_tools": sorted(skill_tools),
            "workflow_json_path": _skill_workflow_json_path(skill),
        })
    has_tool_specific_matches = any(
        str(item.get("skill_type", "") or "").strip() != "general_python"
        and set(item.get("related_tools", []) or []).intersection(related_tool_ids)
        for item in matches
    )
    if has_tool_specific_matches:
        matches = [
            item for item in matches
            if str(item.get("skill_type", "") or "").strip() != "general_python"
        ]
    matches.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("title", "")).casefold()))
    return {"matches": matches[: max(1, int(limit or 1))], "query_tokens": sorted(query_tokens)}


def match_tools_and_skills(
    task_text: str,
    canvas_context: dict[str, Any] | None = None,
    quest_agent_root: str | Path | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    task_text = str(task_text or "").strip()
    canvas_text = _canvas_context_search_text(canvas_context)
    query = "\n".join(part for part in [task_text, canvas_text] if str(part or "").strip())
    tool_result = search_tools(query, quest_agent_root=quest_agent_root, limit=limit)
    skill_result = search_skills(query, quest_agent_root=quest_agent_root, limit=limit)
    tool_matches = [dict(item or {}) for item in list(tool_result.get("matches", []) or [])]
    skill_matches = [dict(item or {}) for item in list(skill_result.get("matches", []) or [])]
    workflow_templates = []
    for item in skill_matches:
        workflow_path = str(item.get("workflow_json_path", "") or "").strip()
        if not workflow_path:
            continue
        workflow_templates.append({
            "skill_id": str(item.get("skill_id", "") or "").strip(),
            "title": str(item.get("title", "") or "").strip(),
            "skill_type": str(item.get("skill_type", "") or "").strip(),
            "confidence": float(item.get("confidence", 0.0) or 0.0),
            "reason": str(item.get("reason", "") or "").strip(),
            "workflow_json_path": workflow_path,
        })
    strategy = "no_viable_quest_solution"
    if tool_matches and skill_matches:
        has_tool_specific_skill = any(
            str(item.get("skill_type", "") or "").strip() != "general_python"
            for item in skill_matches
        )
        strategy = "use_quest_skill" if has_tool_specific_skill else "use_general_python_skill_plus_tools"
    elif tool_matches:
        strategy = "use_tools_only"
    elif skill_matches:
        strategy = "use_quest_skill"
    notes = [
        "Tool and skill candidates were shortlisted by the QuESt MCP tools and skills manager; final ranking should be done by the LLM.",
    ]
    return {
        "project_description": task_text,
        "task": task_text,
        "flow_description": "",
        "strategy": strategy,
        "tool_matches": tool_matches,
        "skill_matches": skill_matches,
        "best_workflow_template": {},
        "candidate_workflow_templates": workflow_templates[: max(1, int(limit or 1))],
        "notes": notes,
        "mcp_lookup": {
            "source": "quest_mcp_tools_skills_manager",
            "query_tokens": sorted(set(tool_result.get("query_tokens", []) or []) | set(skill_result.get("query_tokens", []) or [])),
            "canvas_context_used": bool(canvas_text.strip()),
        },
        "tool_errors": [],
        "model": "MCP deterministic lookup",
        "model_used_note": "",
    }


def match_skill_task(
    task_text: str,
    canvas_context: dict[str, Any] | None = None,
    quest_agent_root: str | Path | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    result = match_tools_and_skills(
        task_text,
        canvas_context=canvas_context,
        quest_agent_root=quest_agent_root,
        limit=limit,
    )
    return {
        "task": str(task_text or "").strip(),
        "skill_matches": list(dict(result or {}).get("skill_matches", []) or []),
        "best_workflow_template": dict(dict(result or {}).get("best_workflow_template", {}) or {}),
        "mcp_lookup": dict(dict(result or {}).get("mcp_lookup", {}) or {}),
        "source": "quest_mcp_skills_registry",
    }


def _skill_development_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(payload or {})
    return {
        "project_description": str(data.get("project_description", "") or data.get("task", "") or "").strip(),
        "flow_description": str(data.get("flow_description", "") or "").strip(),
        "task_match_result": dict(data.get("task_match_result", {}) or {}),
        "action_records": list(data.get("action_records", []) or []),
        "pinned_context": list(data.get("pinned_context", []) or []),
        "attached_files": list(data.get("attached_files", []) or []),
        "current_flow_json_data": dict(data.get("current_flow_json_data", {}) or data.get("final_flow_json", {}) or {}),
        "selected_model": str(data.get("selected_model", "") or "").strip() or None,
        "api_key": str(data.get("api_key", "") or "").strip() or None,
    }


def create_skill_from_flow(
    payload: dict[str, Any] | None,
    quest_agent_root: str | Path | None = None,
) -> dict[str, Any]:
    args = _skill_development_payload(payload)
    developed = develop_skill_from_record(
        **args,
        quest_agent_root=get_quest_agent_root(quest_agent_root),
        update_skill_id=None,
    )
    return {
        **dict(developed or {}),
        "operation": "skills.create_from_flow",
        "updated_existing_skill": False,
        "source": "quest_mcp_skills_registry",
    }


def update_skill_from_flow(
    skill_id: str,
    payload: dict[str, Any] | None,
    quest_agent_root: str | Path | None = None,
) -> dict[str, Any]:
    requested_id = str(skill_id or "").strip()
    if not requested_id:
        raise RuntimeError("skills.update_from_flow requires skill_id.")
    args = _skill_development_payload(payload)
    developed = develop_skill_from_record(
        **args,
        quest_agent_root=get_quest_agent_root(quest_agent_root),
        update_skill_id=requested_id,
    )
    return {
        **dict(developed or {}),
        "operation": "skills.update_from_flow",
        "updated_existing_skill": True,
        "source": "quest_mcp_skills_registry",
    }


def get_skill(skill_id: str, quest_agent_root: str | Path | None = None) -> dict[str, Any]:
    requested_id = str(skill_id or "").strip()
    for skill in _load_skills(quest_agent_root):
        if str(getattr(skill, "skill_id", "") or "") != requested_id:
            continue
        return skill.to_manifest_entry(get_quest_agent_root(quest_agent_root))
    return {"error": f"Skill not found: {requested_id}"}


def get_workflow_template(skill_id: str, quest_agent_root: str | Path | None = None) -> dict[str, Any]:
    requested_id = str(skill_id or "").strip()
    root = get_quest_agent_root(quest_agent_root)
    for skill in _load_skills(root):
        if str(getattr(skill, "skill_id", "") or "") != requested_id:
            continue
        workflow_path = str(getattr(skill, "workflow_json_path", "") or "").strip()
        if not workflow_path:
            return {"skill_id": requested_id, "workflow_template": {}, "error": "Skill has no workflow template."}
        path = Path(workflow_path)
        try:
            with path.open("r", encoding="utf-8") as handle:
                return {"skill_id": requested_id, "workflow_template": json.load(handle), "workflow_path": path.as_posix()}
        except Exception as exc:
            return {"skill_id": requested_id, "workflow_template": {}, "workflow_path": path.as_posix(), "error": str(exc)}
    return {"skill_id": requested_id, "workflow_template": {}, "error": f"Skill not found: {requested_id}"}


def validate_flow_analysis(flow_analysis: dict[str, Any], task_text: str = "") -> dict[str, Any]:
    analysis = dict(flow_analysis or {})
    data_nodes = [dict(item or {}) for item in list(analysis.get("data_nodes", []) or [])]
    python_nodes = [dict(item or {}) for item in list(analysis.get("python_nodes", []) or [])]
    connections = [dict(item or {}) for item in list(analysis.get("connections", []) or [])]
    missing_parts = _clean_list(analysis.get("missing_parts", []))
    unexpected_parts = _clean_list(
        list(analysis.get("unexpected_parts", []) or [])
    )
    structural_valid = not missing_parts and not unexpected_parts
    status = "complete" if structural_valid else "incomplete"
    task_alignment = "needs_semantic_review" if structural_valid and str(task_text or "").strip() else "partial"
    if not data_nodes and not python_nodes:
        task_alignment = "not_aligned"
    evidence = []
    for item in missing_parts:
        evidence.append({"type": "missing_part", "detail": item})
    for item in unexpected_parts:
        evidence.append({"type": "unexpected_part", "detail": item})
    return {
        "status": status,
        "structural_valid": structural_valid,
        "task_alignment": task_alignment,
        "facts": {
            "data_node_count": len(data_nodes),
            "python_node_count": len(python_nodes),
            "connection_count": len(connections),
            "data_nodes": data_nodes,
            "python_nodes": [
                {
                    "name": str(node.get("name", "") or ""),
                    "input_ports": _clean_list(node.get("input_ports", [])),
                    "output_ports": _clean_list(node.get("output_ports", [])),
                    "brief_description": str(node.get("brief_description", "") or ""),
                }
                for node in python_nodes
            ],
            "connections": connections,
        },
        "missing_parts": missing_parts,
        "unexpected_parts": unexpected_parts,
        "warnings": ["MCP validation is structural only; task-level semantic fit should be reviewed by the LLM."] if str(task_text or "").strip() else [],
        "evidence": evidence,
        "source": "quest_mcp_tools_skills_manager",
    }


def summarize_validation_report(report: dict[str, Any]) -> str:
    data = dict(report or {})
    facts = dict(data.get("facts", {}) or {})
    lines = [
        f"validation_status: {data.get('status', 'unknown')}",
        f"structural_valid: {bool(data.get('structural_valid', False))}",
        f"task_alignment: {data.get('task_alignment', 'unknown')}",
        (
            "facts: "
            f"data_nodes={facts.get('data_node_count', 0)}, "
            f"python_nodes={facts.get('python_node_count', 0)}, "
            f"connections={facts.get('connection_count', 0)}"
        ),
    ]
    missing_parts = _clean_list(data.get("missing_parts", []), 10)
    if missing_parts:
        lines.append("missing_parts: " + "; ".join(missing_parts))
    unexpected_parts = _clean_list(data.get("unexpected_parts", []), 10)
    if unexpected_parts:
        lines.append("unexpected_parts: " + "; ".join(unexpected_parts))
    return "\n".join(lines)
