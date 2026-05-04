import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .llm_matcher import _chat_completion_content, _parse_json_response
from .skill_library import build_skills_manifest, get_quest_agent_root
from .tool_registry import write_active_tool_registry


def format_action_records_table(action_records: list[dict[str, Any]] | None = None) -> str:
    records = list(action_records or [])
    if not records:
        return ""

    headers = ["Step", "Flow", "Flow Type", "Scope", "Action", "Target", "Workspace Action", "Details"]
    rows = []
    for index, record in enumerate(records, start=1):
        workspace_action = record.get("workspace_action", None)
        rows.append([
            str(index),
            str(record.get("flow_name", "") or ""),
            str(record.get("flow_type", "") or ""),
            str(record.get("scope", "") or ""),
            str(record.get("action", "") or ""),
            str(record.get("target", "") or ""),
            json.dumps(workspace_action, ensure_ascii=True, sort_keys=True) if isinstance(workspace_action, dict) else "",
            json.dumps(record.get("details", {}), ensure_ascii=True, sort_keys=True) if isinstance(record.get("details", {}), dict) else "",
        ])

    widths = []
    for column_index, header in enumerate(headers):
        widths.append(max(len(header), *(len(row[column_index]) for row in rows)))

    def _format_row(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

    separator = "-+-".join("-" * width for width in widths)
    lines = [_format_row(headers), separator]
    lines.extend(_format_row(row) for row in rows)
    return "\n".join(lines)


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _slugify(text: str, fallback: str = "quest-skill") -> str:
    value = re.sub(r"[^a-z0-9]+", "-", str(text or "").strip().lower()).strip("-")
    return value or fallback


def _unique_slug(base_dir: Path, desired_slug: str) -> str:
    slug = _slugify(desired_slug)
    candidate = slug
    counter = 2
    while (base_dir / candidate).exists():
        candidate = f"{slug}-v{counter}"
        counter += 1
    return candidate


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        cleaned = str(value or "").strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def _normalize_string_list(values: list[Any] | None = None) -> list[str]:
    return _dedupe_preserve([str(value or "").strip() for value in list(values or []) if str(value or "").strip()])


def _normalize_named_items(items: list[Any] | None = None, *, default_type: str) -> list[dict[str, str]]:
    normalized = []
    seen = set()
    for item in list(items or []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "") or "").strip()
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append({
            "name": name,
            "type": str(item.get("type", "") or "").strip() or default_type,
            "description": str(item.get("description", "") or "").strip(),
        })
    return normalized


def _workflow_nodes(current_flow_json_data: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(node or {}) for node in list(current_flow_json_data.get("nodes_df", []) or []) if isinstance(node, dict)]


def _workflow_connections(current_flow_json_data: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(connection or {}) for connection in list(current_flow_json_data.get("connections_df", []) or []) if isinstance(connection, dict)]


def _node_type_text(node: dict[str, Any]) -> str:
    parts = [
        str(node.get("node_type", "") or ""),
        str(node.get("type", "") or ""),
        str(node.get("class", "") or ""),
        str(node.get("node_class", "") or ""),
    ]
    return " ".join(part for part in parts if part).casefold()


def _infer_structural_tags(current_flow_json_data: dict[str, Any], action_records: list[dict[str, Any]]) -> list[str]:
    nodes = _workflow_nodes(current_flow_json_data)
    connections = _workflow_connections(current_flow_json_data)
    subflows = list(current_flow_json_data.get("subflows_df", []) or [])
    flow_type = str(current_flow_json_data.get("flow_type", "") or "").strip().casefold()
    tags = []

    python_node_names = []
    plotting_text = []
    incoming_connection_counts = {}
    for connection in connections:
        target = str(connection.get("to_node", "") or connection.get("target_node", "") or "").strip()
        if target:
            incoming_connection_counts[target] = incoming_connection_counts.get(target, 0) + 1

    for node in nodes:
        node_type_text = _node_type_text(node)
        node_name = str(node.get("node_name", "") or node.get("name", "") or "").strip()
        if any(token in node_type_text for token in ("python", "pynode", "py_node")):
            python_node_names.append(node_name)
        plotting_text.append(f"{node_name} {node_type_text}")

    if subflows or flow_type == "sub-flow" or any(str(record.get("action", "") or "").strip() == "add_subflow" for record in action_records):
        tags.append("subflow")
    if len(python_node_names) >= 2:
        tags.append("multi-step-python")
    if any(count >= 2 for count in incoming_connection_counts.values()):
        tags.append("data-merge")
    if any(keyword in " ".join(plotting_text).casefold() for keyword in ("plot", "chart", "graph", "figure", "matplotlib", "seaborn", "histogram", "scatter")):
        tags.append("plotting")

    return _normalize_string_list(tags)


def _infer_task_pattern_tags(project_description: str, flow_description: str, action_records: list[dict[str, Any]]) -> list[str]:
    searchable_text = "\n".join(
        [
            str(project_description or "").strip(),
            str(flow_description or "").strip(),
            json.dumps(action_records or [], ensure_ascii=True, sort_keys=True, default=str),
        ]
    ).casefold()
    tags = []
    if re.search(r"\b(add|sum|plus)\b", searchable_text) and re.search(r"\b(number|numbers)\b", searchable_text):
        tags.append("sum_numbers")
    if re.search(r"\bsquare|squared|square the result\b", searchable_text):
        tags.append("square_result")
    if re.search(r"\bparameter sweep|param sweep|sensitivity|scenario sweep|sweep\b", searchable_text):
        tags.append("parameter_sweep")
    if re.search(r"\bmultiply|product\b", searchable_text) and re.search(r"\b(number|numbers)\b", searchable_text):
        tags.append("multiply_numbers")
    return _normalize_string_list(tags)


def _infer_transformation_intents(
    project_description: str,
    flow_description: str,
    action_records: list[dict[str, Any]],
) -> list[str]:
    searchable_text = "\n".join(
        [
            str(project_description or "").strip(),
            str(flow_description or "").strip(),
            json.dumps(action_records or [], ensure_ascii=True, sort_keys=True, default=str),
        ]
    ).casefold()
    intents = []

    if re.search(r"\b(add|another|extra|third|fourth|fifth).{0,24}\b(input|number)\b", searchable_text):
        intents.append("add one more input")
    if re.search(r"\b(split|separate|convert).{0,40}\bpython\b", searchable_text) or re.search(r"\beach function in one python node\b", searchable_text):
        intents.append("split one Python node into multiple steps")
    if re.search(r"\b(change|replace|update|initialize).{0,24}\b(value|constant|constants)\b", searchable_text):
        intents.append("replace constant values")
    if re.search(r"\b(remove|delete|drop).{0,24}\b(extra|unused)?\s*data node\b", searchable_text):
        intents.append("remove extra data node")
    if any(str(record.get("action", "") or "").strip() == "update_node_value" for record in action_records):
        intents.append("replace constant values")
    if any(str(record.get("action", "") or "").strip() in {"delete_selected_nodes", "delete_node"} for record in action_records):
        intents.append("remove extra data node")

    return _normalize_string_list(intents)


def _infer_expected_outputs(current_flow_json_data: dict[str, Any]) -> list[dict[str, str]]:
    flow_layout = dict(current_flow_json_data.get("flow_layout", {}) or {})
    layout_nodes = dict(flow_layout.get("nodes", {}) or {})
    layout_connections = list(flow_layout.get("connections", []) or [])
    node_rows = {str(row.get("node_id", "") or "").strip(): dict(row or {}) for row in _workflow_nodes(current_flow_json_data)}
    connected_outputs = {
        (
            str(list(connection.get("out", []) or ["", ""])[0] or "").strip(),
            str(list(connection.get("out", []) or ["", ""])[1] or "").strip(),
        )
        for connection in layout_connections
        if isinstance(connection, dict)
    }

    python_outputs = []
    fallback_outputs = []
    for node_id, layout_node in list(layout_nodes.items()):
        if not isinstance(layout_node, dict):
            continue
        node_id = str(node_id or "").strip()
        row = node_rows.get(node_id, {})
        node_name = str(layout_node.get("name", "") or row.get("node_name", "") or "").strip()
        node_type = f"{str(layout_node.get('type_', '') or '')} {str(row.get('node_type', '') or '')}".casefold()
        output_ports = list(layout_node.get("output_ports", []) or [])
        for output_port in output_ports:
            if not isinstance(output_port, dict):
                continue
            port_name = str(output_port.get("name", "") or "").strip()
            if not port_name or (node_id, port_name) in connected_outputs:
                continue
            entry = {
                "name": port_name,
                "type": "value",
                "description": f"Terminal output from {node_name or 'the workflow'}".strip(),
            }
            if any(token in node_type for token in ("python", "pynode", "py_node")):
                python_outputs.append(entry)
            else:
                fallback_outputs.append(entry)

    return _normalize_named_items(python_outputs or fallback_outputs, default_type="value")


def _infer_skill_mode(
    payload: dict[str, Any],
    project_description: str,
    flow_description: str,
    transformation_intents: list[str],
) -> str:
    requested = str(payload.get("skill_mode", "") or "").strip().lower()
    if requested in {"build", "edit", "hybrid"}:
        return requested

    searchable_text = "\n".join(
        [
            str(project_description or "").strip(),
            str(flow_description or "").strip(),
            str(payload.get("summary", "") or "").strip(),
        ]
    ).casefold()
    has_build = bool(re.search(r"\b(build|create|construct|assemble|make)\b", searchable_text))
    has_edit = bool(
        transformation_intents
        or re.search(r"\b(edit|adapt|modify|revise|update|replace|convert|split|remove|patch|touch up)\b", searchable_text)
    )
    if has_build and has_edit:
        return "hybrid"
    if has_edit:
        return "edit"
    return "build"


def _pick_workflow_baseline_attachment(attached_files: list[str]) -> str:
    for path in list(attached_files or []):
        source = Path(str(path))
        if not source.exists() or not source.is_file() or source.suffix.lower() != ".json":
            continue
        try:
            with source.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue
        if isinstance(data, dict) and any(key in data for key in ("flow_name", "flow_type", "flow_layout", "nodes_df", "connections_df", "subflows_df")):
            return source.as_posix()
    return ""


def _load_workflow_json_file(path: str | Path | None) -> dict[str, Any]:
    normalized = Path(str(path or "")).expanduser()
    if not normalized.exists() or not normalized.is_file() or normalized.suffix.lower() != ".json":
        return {}
    try:
        data = json.loads(normalized.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    if not any(key in data for key in ("flow_name", "flow_type", "flow_layout", "nodes_df", "connections_df", "subflows_df")):
        return {}
    return data


def _workflow_json_complexity_score(data: dict[str, Any]) -> int:
    if not isinstance(data, dict):
        return -1
    nodes = list(data.get("nodes_df", []) or [])
    connections = list(data.get("connections_df", []) or [])
    subflows = list(data.get("subflows_df", []) or [])
    score = 0
    score += len(nodes) * 3
    score += len(connections) * 2
    score += len(subflows) * 10
    if str(data.get("flow_type", "") or "").strip() == "master-flow":
        score += 5
    return score


def _prefer_richer_workflow_json(current_flow_json_data: dict[str, Any], attached_files: list[str]) -> tuple[dict[str, Any], str]:
    best_data = dict(current_flow_json_data or {}) if isinstance(current_flow_json_data, dict) else {}
    best_source = "current_canvas"
    best_score = _workflow_json_complexity_score(best_data)

    for attached_path in list(attached_files or []):
        candidate = _load_workflow_json_file(attached_path)
        candidate_score = _workflow_json_complexity_score(candidate)
        if candidate_score > best_score:
            best_data = candidate
            best_source = Path(str(attached_path)).name
            best_score = candidate_score

    return best_data, best_source


def _describe_workflow_baseline(current_flow_json_data: dict[str, Any]) -> dict[str, Any]:
    workflow_data = dict(current_flow_json_data or {})
    nodes = _workflow_nodes(workflow_data)
    connections = _workflow_connections(workflow_data)
    subflows = [dict(item or {}) for item in list(workflow_data.get("subflows_df", []) or []) if isinstance(item, dict)]

    data_nodes = []
    python_nodes = []
    description_text = ""
    tool_evidence = set()

    for node in nodes:
        node_name = str(node.get("node_name", "") or "").strip()
        node_type = str(node.get("node_type", "") or "").strip()
        if node_type == "back_node" and not description_text:
            description_text = str(node.get("node_input_value", "") or "").strip()
        if node_type == "data_node":
            data_nodes.append({
                "name": node_name,
                "variable": str(node.get("node_input_variable", "") or "").strip(),
                "is_path": bool(node.get("node_is_path", False)),
                "value": str(node.get("node_input_value", "") or "").strip(),
            })
        elif node_type == "python_node":
            imports_text = str(node.get("node_imports", "") or "")
            wrapper_text = str(node.get("node_function_wrapper", "") or "")
            combined = f"{node_name}\n{imports_text}\n{wrapper_text}".casefold()
            if "progress" in combined:
                tool_evidence.add("progress")
            if "btm" in combined:
                tool_evidence.add("btm")
            if "valuation" in combined:
                tool_evidence.add("valuation")
            if "performance" in combined:
                tool_evidence.add("performance")
            if "planning" in combined:
                tool_evidence.add("planning")
            python_nodes.append({
                "name": node_name,
                "input_preview": str(wrapper_text.split("\n", 1)[0] if wrapper_text else "").strip(),
                "output_preview": list(node.get("node_expose_outputs", []) or []),
                "imports_preview": _normalize_string_list([line.strip() for line in imports_text.splitlines() if line.strip()])[:6],
            })

    subflow_summaries = []
    for subflow in subflows:
        subflow_nodes = [dict(item or {}) for item in list(subflow.get("nodes_df", []) or []) if isinstance(item, dict)]
        subflow_connections = [dict(item or {}) for item in list(subflow.get("connections_df", []) or []) if isinstance(item, dict)]
        subflow_data_nodes = []
        subflow_python_nodes = []
        subflow_tool_evidence = set()
        subflow_nodes = [dict(item or {}) for item in list(subflow.get("nodes_df", []) or []) if isinstance(item, dict)]
        for node in subflow_nodes:
            node_name = str(node.get("node_name", "") or "").strip()
            node_type = str(node.get("node_type", "") or "").strip()
            if node_type == "data_node":
                subflow_data_nodes.append({
                    "name": node_name,
                    "variable": str(node.get("node_input_variable", "") or "").strip(),
                    "is_path": bool(node.get("node_is_path", False)),
                })
            if str(node.get("node_type", "") or "").strip() != "python_node":
                continue
            combined = (
                f"{str(node.get('node_name', '') or '')}\n"
                f"{str(node.get('node_imports', '') or '')}\n"
                f"{str(node.get('node_function_wrapper', '') or '')}"
            ).casefold()
            if "progress" in combined:
                tool_evidence.add("progress")
                subflow_tool_evidence.add("progress")
            if "btm" in combined:
                tool_evidence.add("btm")
                subflow_tool_evidence.add("btm")
            if "valuation" in combined:
                tool_evidence.add("valuation")
                subflow_tool_evidence.add("valuation")
            if "performance" in combined:
                tool_evidence.add("performance")
                subflow_tool_evidence.add("performance")
            if "planning" in combined:
                tool_evidence.add("planning")
                subflow_tool_evidence.add("planning")
            subflow_python_nodes.append({
                "name": node_name,
                "input_preview": str(str(node.get("node_function_wrapper", "") or "").split("\n", 1)[0]).strip(),
                "output_preview": list(node.get("node_expose_outputs", []) or [])[:8],
            })
        subflow_summaries.append({
            "name": str(subflow.get("flow_name", "") or "").strip(),
            "flow_type": str(subflow.get("flow_type", "") or "").strip(),
            "data_node_count": len(subflow_data_nodes),
            "python_node_count": len(subflow_python_nodes),
            "connection_count": len(subflow_connections),
            "data_nodes": subflow_data_nodes[:10],
            "python_nodes": subflow_python_nodes[:12],
            "tool_evidence": sorted(subflow_tool_evidence),
        })

    return {
        "flow_name": str(workflow_data.get("flow_name", "") or "").strip(),
        "flow_type": str(workflow_data.get("flow_type", "") or "").strip(),
        "description_text": description_text,
        "data_node_count": len(data_nodes),
        "python_node_count": len([node for node in nodes if str(node.get("node_type", "") or "").strip() == "python_node"]),
        "connection_count": len(connections),
        "subflow_count": len(subflows),
        "data_nodes": data_nodes[:12],
        "python_nodes": python_nodes[:12],
        "subflow_names": [str(item.get("flow_name", "") or "").strip() for item in subflows if str(item.get("flow_name", "") or "").strip()],
        "subflow_summaries": subflow_summaries[:8],
        "tool_evidence": sorted(tool_evidence),
    }


def _humanize_identifier(value: str) -> str:
    text = str(value or "").strip().replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    return text[0].upper() + text[1:]


def _is_generic_skill_title(title: str) -> bool:
    cleaned = str(title or "").strip().casefold()
    return cleaned in {"", "quest skill", "quest-skill", "quest workflow skill", "skill"}


def _is_generic_skill_summary(summary: str) -> bool:
    cleaned = str(summary or "").strip().casefold()
    return cleaned in {
        "",
        "reusable quest workflow skill.",
        "reusable quest skill.",
        "reusable workflow skill.",
    }


def _tool_display_name(tool_id: str) -> str:
    mapping = {
        "btm": "BTM",
        "progress": "Progress",
        "valuation": "Valuation",
        "performance": "Performance",
        "planning": "Planning",
        "workspace": "Workspace",
    }
    cleaned = str(tool_id or "").strip().casefold()
    return mapping.get(cleaned, _humanize_identifier(cleaned))


def _workflow_domain_label(workflow_baseline_profile: dict[str, Any]) -> str:
    tools = [str(item or "").strip() for item in list(workflow_baseline_profile.get("tool_evidence", []) or []) if str(item or "").strip()]
    if tools:
        return _tool_display_name(tools[0])
    subflow_names = [str(item or "").strip() for item in list(workflow_baseline_profile.get("subflow_names", []) or []) if str(item or "").strip()]
    if subflow_names:
        return _humanize_identifier(subflow_names[0])
    flow_name = str(workflow_baseline_profile.get("flow_name", "") or "").strip()
    if flow_name:
        return _humanize_identifier(flow_name)
    return "Workspace"


def _derive_workflow_title(workflow_baseline_profile: dict[str, Any]) -> str:
    profile = dict(workflow_baseline_profile or {})
    flow_name = _humanize_identifier(str(profile.get("flow_name", "") or "").strip())
    flow_type = str(profile.get("flow_type", "") or "").strip().casefold()
    domain = _workflow_domain_label(profile)
    subflow_count = int(profile.get("subflow_count", 0) or 0)
    description_text = str(profile.get("description_text", "") or "").strip()
    if description_text:
        first_line = re.split(r"[\r\n]+|(?<=[.!?])\s+", description_text, maxsplit=1)[0].strip()
        if 8 <= len(first_line) <= 90:
            return _humanize_identifier(first_line.rstrip("."))
    if flow_type == "master-flow" and subflow_count:
        if domain and domain != "Workspace":
            return f"Run {domain} workflow from a Workspace master flow"
        return f"Run {flow_name or 'subflow-based'} workflow from a Workspace master flow"
    if flow_name:
        if domain and domain not in flow_name:
            return f"{flow_name} using {domain}"
        return flow_name
    python_count = int(profile.get("python_node_count", 0) or 0)
    if domain and domain != "Workspace":
        return f"Build a {domain} workflow in Workspace"
    if python_count >= 2:
        return "Build a multi-step Python workflow in Workspace"
    return "Build a Workspace workflow"


def _derive_workflow_summary(workflow_baseline_profile: dict[str, Any]) -> str:
    profile = dict(workflow_baseline_profile or {})
    flow_type = str(profile.get("flow_type", "") or "").strip().casefold() or "workflow"
    domain = _workflow_domain_label(profile)
    description_text = str(profile.get("description_text", "") or "").strip()
    data_count = int(profile.get("data_node_count", 0) or 0)
    python_count = int(profile.get("python_node_count", 0) or 0)
    subflow_count = int(profile.get("subflow_count", 0) or 0)
    if description_text:
        return description_text
    parts = []
    if flow_type == "master-flow" and subflow_count:
        parts.append(f"Reusable Workspace master flow for running {domain} analysis through {subflow_count} subflow{'s' if subflow_count != 1 else ''}.")
    elif domain and domain != "Workspace":
        parts.append(f"Reusable {domain} workflow built inside Workspace.")
    else:
        parts.append("Reusable Workspace workflow.")
    detail = f"It currently uses {data_count} data node{'s' if data_count != 1 else ''} and {python_count} Python node{'s' if python_count != 1 else ''}"
    if subflow_count:
        detail += f", with {subflow_count} embedded subflow{'s' if subflow_count != 1 else ''}"
    parts.append(detail + ".")
    return " ".join(parts).strip()


def _derive_workflow_expected_inputs(workflow_baseline_profile: dict[str, Any]) -> list[dict[str, str]]:
    profile = dict(workflow_baseline_profile or {})
    normalized = []
    seen = set()

    def _append_input(name: str, item_type: str, description: str) -> None:
        cleaned_name = str(name or "").strip()
        if not cleaned_name:
            return
        key = cleaned_name.casefold()
        if key in seen:
            return
        seen.add(key)
        normalized.append({
            "name": cleaned_name,
            "type": item_type or "value",
            "description": str(description or "").strip(),
        })

    for item in list(profile.get("data_nodes", []) or []):
        if not isinstance(item, dict):
            continue
        variable = str(item.get("variable", "") or "").strip()
        node_name = str(item.get("name", "") or "").strip()
        name = variable or node_name
        if not name:
            continue
        item_type = "file" if bool(item.get("is_path", False)) else "value"
        description = f"Input provided through data node {node_name or name}."
        _append_input(name, item_type, description)

    for subflow in list(profile.get("subflow_summaries", []) or []):
        if not isinstance(subflow, dict):
            continue
        subflow_name = str(subflow.get("name", "") or "").strip() or "subflow"
        for item in list(subflow.get("data_nodes", []) or []):
            if not isinstance(item, dict):
                continue
            variable = str(item.get("variable", "") or "").strip()
            node_name = str(item.get("name", "") or "").strip()
            name = variable or node_name
            if not name:
                continue
            item_type = "file" if bool(item.get("is_path", False)) else "value"
            description = f"Input consumed by subflow {subflow_name} through data node {node_name or name}."
            _append_input(name, item_type, description)

    return _normalize_named_items(normalized, default_type="value")


def _derive_workflow_expected_outputs(workflow_baseline_profile: dict[str, Any]) -> list[dict[str, str]]:
    profile = dict(workflow_baseline_profile or {})
    normalized = []
    seen = set()

    def _append_output(name: str, description: str) -> None:
        cleaned_name = str(name or "").strip()
        if not cleaned_name:
            return
        key = cleaned_name.casefold()
        if key in seen:
            return
        seen.add(key)
        normalized.append({
            "name": cleaned_name,
            "type": "value",
            "description": str(description or "").strip(),
        })

    for item in list(profile.get("python_nodes", []) or []):
        if not isinstance(item, dict):
            continue
        node_name = str(item.get("name", "") or "").strip() or "python node"
        for output_name in list(item.get("output_preview", []) or []):
            _append_output(str(output_name or "").strip(), f"Output produced by Python node {node_name}.")

    for subflow in list(profile.get("subflow_summaries", []) or []):
        if not isinstance(subflow, dict):
            continue
        subflow_name = str(subflow.get("name", "") or "").strip() or "subflow"
        for item in list(subflow.get("python_nodes", []) or []):
            if not isinstance(item, dict):
                continue
            node_name = str(item.get("name", "") or "").strip() or "python node"
            for output_name in list(item.get("output_preview", []) or []):
                _append_output(str(output_name or "").strip(), f"Output produced by subflow {subflow_name} node {node_name}.")

    return _normalize_named_items(normalized, default_type="value")


def _derive_workflow_step_summary(workflow_baseline_profile: dict[str, Any]) -> list[str]:
    profile = dict(workflow_baseline_profile or {})
    steps = []
    inputs = _derive_workflow_expected_inputs(profile)
    if inputs:
        input_names = ", ".join(item["name"] for item in inputs[:6])
        steps.append(f"Prepare the required inputs for the flow: {input_names}.")
    for subflow in list(profile.get("subflow_summaries", []) or []):
        if not isinstance(subflow, dict):
            continue
        subflow_name = str(subflow.get("name", "") or "").strip() or "subflow"
        subflow_tools = [_tool_display_name(item) for item in list(subflow.get("tool_evidence", []) or []) if str(item or "").strip()]
        subflow_python_nodes = [str(item.get("name", "") or "").strip() for item in list(subflow.get("python_nodes", []) or []) if isinstance(item, dict) and str(item.get("name", "") or "").strip()]
        if subflow_tools:
            steps.append(f"Run subflow {subflow_name} using the {', '.join(subflow_tools)} tool workflow.")
        elif subflow_python_nodes:
            steps.append(f"Run subflow {subflow_name}, which centers on Python steps {', '.join(subflow_python_nodes[:4])}.")
        else:
            steps.append(f"Run subflow {subflow_name} with its recorded inputs and connections.")
    python_nodes = [str(item.get("name", "") or "").strip() for item in list(profile.get("python_nodes", []) or []) if isinstance(item, dict) and str(item.get("name", "") or "").strip()]
    if python_nodes:
        steps.append(f"Execute the top-level Python nodes in sequence: {', '.join(python_nodes[:6])}.")
    outputs = _derive_workflow_expected_outputs(profile)
    if outputs:
        output_names = ", ".join(item["name"] for item in outputs[:6])
        steps.append(f"Validate that the workflow produces the expected outputs: {output_names}.")
    return _normalize_string_list(steps)


def _derive_workflow_validation_criteria(workflow_baseline_profile: dict[str, Any]) -> list[str]:
    profile = dict(workflow_baseline_profile or {})
    criteria = []
    outputs = _derive_workflow_expected_outputs(profile)
    if outputs:
        criteria.append(
            "The workflow produces the expected outputs: "
            + ", ".join(item["name"] for item in outputs[:6])
            + "."
        )
    if int(profile.get("subflow_count", 0) or 0):
        criteria.append("Each referenced subflow loads and runs with its recorded connections intact.")
    if int(profile.get("connection_count", 0) or 0):
        criteria.append("All required node connections are present after the workflow is loaded.")
    if int(profile.get("python_node_count", 0) or 0):
        criteria.append("Python node wrappers expose the expected inputs and outputs after refresh.")
    return _normalize_string_list(criteria)


def _tool_search_terms(tool: dict[str, Any]) -> list[str]:
    terms = []
    for value in (
        tool.get("tool_id", ""),
        tool.get("name", ""),
        tool.get("search_key", ""),
    ):
        cleaned = str(value or "").strip().casefold()
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
    for value in list(tool.get("aliases", []) or []):
        cleaned = str(value or "").strip().casefold()
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
    for value in list(tool.get("typical_tasks", []) or []):
        cleaned = str(value or "").strip().casefold()
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
    return [term for term in terms if len(term) >= 3]


def _infer_specific_tools(
    *,
    task_match_result: dict[str, Any],
    current_flow_json_data: dict[str, Any],
    action_records: list[dict[str, Any]],
    project_description: str,
    flow_description: str,
    active_tools: list[dict[str, Any]],
) -> list[str]:
    inferred = []

    for item in list(task_match_result.get("tool_matches", []) or []):
        tool_id = str(item.get("tool_id", "") or "").strip()
        if tool_id and tool_id != "workspace" and tool_id not in inferred:
            inferred.append(tool_id)

    searchable_text = "\n".join(
        part
        for part in (
            str(project_description or "").strip(),
            str(flow_description or "").strip(),
            json.dumps(current_flow_json_data or {}, ensure_ascii=True, sort_keys=True, default=str),
            json.dumps(action_records or [], ensure_ascii=True, sort_keys=True, default=str),
        )
        if str(part).strip()
    ).casefold()

    for tool in list(active_tools or []):
        tool_id = str(tool.get("tool_id", "") or "").strip()
        if not tool_id or tool_id == "workspace" or tool_id in inferred:
            continue
        for term in _tool_search_terms(tool):
            pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
            if re.search(pattern, searchable_text):
                inferred.append(tool_id)
                break

    return inferred


def _normalize_skill_payload(
    payload: dict[str, Any],
    active_tool_ids: set[str],
    task_match_result: dict[str, Any],
    specific_tool_ids: list[str],
    project_description: str,
    flow_description: str,
    action_records: list[dict[str, Any]],
    current_flow_json_data: dict[str, Any],
    workflow_baseline_profile: dict[str, Any],
) -> dict[str, Any]:
    skill_type = str(payload.get("skill_type", "") or "").strip()
    if skill_type not in {"general_python", "quest_tool_specific"}:
        skill_type = "quest_tool_specific"

    derived_title = _derive_workflow_title(workflow_baseline_profile)
    derived_summary = _derive_workflow_summary(workflow_baseline_profile)
    title = str(payload.get("title", "") or "").strip()
    if _is_generic_skill_title(title):
        title = derived_title or "QuESt Skill"
    summary = str(payload.get("summary", "") or "").strip()
    if _is_generic_skill_summary(summary):
        summary = derived_summary or "Reusable QuESt workflow skill."
    skill_level = str(payload.get("skill_level", "Competent") or "").strip() or "Competent"
    if skill_level not in {"Novice", "Advanced Beginner", "Competent", "Proficient", "Expert"}:
        skill_level = "Competent"
    workflow_evidence_tools = [
        tool_id for tool_id in list(workflow_baseline_profile.get("tool_evidence", []) or [])
        if str(tool_id or "").strip() in active_tool_ids
    ]
    tool_tags = _normalize_string_list(
        list(payload.get("tool_tags", []) or []) + list(specific_tool_ids or []) + workflow_evidence_tools
    )
    structural_tags = _normalize_string_list(
        list(payload.get("structural_tags", []) or []) + _infer_structural_tags(current_flow_json_data, action_records)
    )
    task_pattern_tags = _normalize_string_list(
        list(payload.get("task_pattern_tags", []) or []) + _infer_task_pattern_tags(project_description, flow_description, action_records)
    )
    tags = _normalize_string_list(
        list(payload.get("tags", []) or []) + tool_tags + structural_tags + task_pattern_tags
    )

    suggested_tools = [str(tool_id).strip() for tool_id in list(payload.get("recommended_tools", []) or []) if str(tool_id).strip()]
    recommended_tools = [tool_id for tool_id in suggested_tools if tool_id in active_tool_ids]
    if not recommended_tools:
        recommended_tools = [
            str(item.get("tool_id", "") or "").strip()
            for item in list(task_match_result.get("tool_matches", []) or [])
            if str(item.get("tool_id", "") or "").strip() in active_tool_ids
        ][:5]
    if workflow_evidence_tools:
        recommended_tools = [
            tool_id for tool_id in workflow_evidence_tools + recommended_tools
            if tool_id in active_tool_ids
        ]
        recommended_tools = _normalize_string_list(recommended_tools)

    required_tools = [
        tool_id for tool_id in [str(tool_id).strip() for tool_id in list(payload.get("required_tools", []) or []) if str(tool_id).strip()]
        if tool_id in active_tool_ids
    ]

    specific_tool_ids = [
        tool_id for tool_id in [str(tool_id).strip() for tool_id in list(specific_tool_ids or []) if str(tool_id).strip()]
        if tool_id in active_tool_ids and tool_id != "workspace"
    ]
    if specific_tool_ids:
        merged_recommended = []
        for tool_id in specific_tool_ids + [tool_id for tool_id in recommended_tools if tool_id != "workspace"]:
            if tool_id and tool_id not in merged_recommended:
                merged_recommended.append(tool_id)
        recommended_tools = merged_recommended
        required_specific = [tool_id for tool_id in required_tools if tool_id != "workspace"]
        if "workspace" in active_tool_ids and "workspace" not in required_tools:
            required_tools = required_specific + ["workspace"]
        else:
            required_tools = required_specific
        skill_type = "quest_tool_specific"
    else:
        skill_type = "general_python"
        effective_tool_set = set(recommended_tools + required_tools)
        if not effective_tool_set and "workspace" in active_tool_ids:
            recommended_tools = ["workspace"]
        elif effective_tool_set and effective_tool_set.issubset({"workspace"}):
            recommended_tools = ["workspace"] if "workspace" in active_tool_ids else recommended_tools
            required_tools = [tool_id for tool_id in required_tools if tool_id == "workspace"]
    tool_tags = _normalize_string_list(tool_tags + recommended_tools + required_tools)
    tags = _normalize_string_list(tags + tool_tags)
    if workflow_evidence_tools:
        required_tools = _normalize_string_list(
            [tool_id for tool_id in required_tools if tool_id == "workspace"] + workflow_evidence_tools + (["workspace"] if "workspace" in active_tool_ids else [])
        )
        recommended_tools = _normalize_string_list(workflow_evidence_tools + recommended_tools + (["workspace"] if "workspace" in active_tool_ids else []))

    workflow_strategy = str(payload.get("workflow_strategy", "") or "").strip() or "recorded_workflow_replay"
    if not str(payload.get("workflow_strategy", "") or "").strip() and workflow_baseline_profile:
        workflow_strategy = (
            f"Reuse and replay the recorded workflow structure in '{workflow_baseline_profile.get('flow_name', '')}', "
            "preserving its existing nodes, subflows, and tool-specific wrappers."
        ).strip()
    step_summary = [str(step).strip() for step in list(payload.get("step_summary", []) or []) if str(step).strip()]
    if not step_summary or step_summary == ["Replay the recorded workspace actions to rebuild the workflow."]:
        step_summary = _derive_workflow_step_summary(workflow_baseline_profile) or [
            "Replay the recorded workspace actions to rebuild the workflow."
        ]

    expected_inputs = _normalize_named_items(payload.get("expected_inputs", []), default_type="file")
    if not expected_inputs:
        expected_inputs = _derive_workflow_expected_inputs(workflow_baseline_profile)
    expected_outputs = _normalize_named_items(payload.get("expected_outputs", []), default_type="value")
    if not expected_outputs:
        expected_outputs = _derive_workflow_expected_outputs(workflow_baseline_profile) or _infer_expected_outputs(current_flow_json_data)

    required_file_types = _normalize_string_list(payload.get("required_file_types", []))
    limitations = _normalize_string_list(payload.get("limitations", []))
    data_preparation_notes = _normalize_string_list(payload.get("data_preparation_notes", []))
    validation_criteria = _normalize_string_list(payload.get("validation_criteria", []))
    if not validation_criteria:
        validation_criteria = _derive_workflow_validation_criteria(workflow_baseline_profile)
    common_variations = _normalize_string_list(payload.get("common_variations", []))
    common_fixes = _normalize_string_list(payload.get("common_fixes", []))
    transformation_intents = _normalize_string_list(
        list(payload.get("transformation_intents", []) or [])
        + _infer_transformation_intents(project_description, flow_description, action_records)
    )
    pinned_context_summary = str(payload.get("pinned_context_summary", "") or "").strip()
    skill_mode = _infer_skill_mode(payload, project_description, flow_description, transformation_intents)

    if not common_variations:
        common_variations = _normalize_string_list([
            "Adjust initialized data-node values while preserving the overall flow shape.",
            "Reuse the workflow baseline and rename nodes or ports to match the new task.",
            "Replace or extend Python wrapper logic while keeping the rest of the flow intact.",
        ])
    if not common_fixes:
        common_fixes = _normalize_string_list([
            "Refresh Python node ports after changing wrapper inputs or outputs.",
            "Reconnect nodes when variable names, wrapper argument names, or output keys change.",
            "Initialize missing data-node values before validating or running the flow.",
        ])

    edit_recipe = {
        "required_tools": _normalize_string_list(recommended_tools + required_tools),
        "expected_inputs": expected_inputs,
        "expected_outputs": expected_outputs,
        "common_variations": common_variations,
        "validation_criteria": validation_criteria,
        "common_fixes": common_fixes,
        "transformation_intents": transformation_intents,
    }

    return {
        "skill_type": skill_type,
        "skill_level": skill_level,
        "skill_mode": skill_mode,
        "title": title,
        "summary": summary,
        "tags": tags,
        "tool_tags": tool_tags,
        "structural_tags": structural_tags,
        "task_pattern_tags": task_pattern_tags,
        "recommended_tools": recommended_tools,
        "required_tools": required_tools,
        "workflow_strategy": workflow_strategy,
        "step_summary": step_summary,
        "expected_inputs": expected_inputs,
        "expected_outputs": expected_outputs,
        "required_file_types": required_file_types,
        "limitations": limitations,
        "data_preparation_notes": data_preparation_notes,
        "validation_criteria": validation_criteria,
        "common_variations": common_variations,
        "common_fixes": common_fixes,
        "transformation_intents": transformation_intents,
        "edit_recipe": edit_recipe,
        "pinned_context_summary": pinned_context_summary,
    }


def _build_skill_messages(
    project_description: str,
    flow_description: str,
    task_match_result: dict[str, Any],
    action_records: list[dict[str, Any]],
    pinned_context: list[str],
    attached_files: list[str],
    active_tools: list[dict[str, Any]],
    current_flow_json_data: dict[str, Any],
    inferred_specific_tools: list[str],
    workflow_baseline_profile: dict[str, Any],
    workflow_baseline_source: str,
) -> list[dict[str, str]]:
    system_prompt = (
        "You are QuESt Agent's skill developer. "
        "Convert a recorded set of QuESt Workspace actions plus project and flow context into a reusable QuESt skill specification. "
        "Treat workflow_json_baseline_profile as the primary ground truth when it is available. "
        "Use the concrete workflow structure, node names, wrappers, subflows, connections, and description text as the main evidence. "
        "Do not invent a broader domain story than the workflow actually shows. "
        "If workflow_json_baseline_profile and task_match_result disagree, trust workflow_json_baseline_profile. "
        "Do not recommend QuESt tools unless they are strongly evidenced by the workflow baseline, the recorded actions, or the task-match result. "
        "If the workflow baseline clearly points to one QuESt tool such as progress, prefer that specific tool and avoid unrelated tools like btm or valuation unless they are directly evidenced. "
        "Classify the skill as quest_tool_specific when the underlying task is clearly about a non-workspace QuESt tool such as btm, valuation, planning, evaluation, performance, microgrid, or technology screening, even if the workflow was built inside Workspace. "
        "Only classify the skill as general_python when the task is not tied to a specific non-workspace QuESt tool and the workflow pattern is broadly reusable. "
        "Do not treat the mere use of Workspace as evidence that the skill should be matched to Workspace tasks. "
        "Assign exactly one skill_level using this scale: Novice, Advanced Beginner, Competent, Proficient, Expert. "
        "Use Competent as the default when the evidence is mixed. "
        "Use only the provided active tool IDs. "
        "Return valid JSON only with this shape: "
        "{"
        "\"title\": string, "
        "\"skill_type\": \"general_python\" | \"quest_tool_specific\", "
        "\"skill_level\": \"Novice\" | \"Advanced Beginner\" | \"Competent\" | \"Proficient\" | \"Expert\", "
        "\"skill_mode\": \"build\" | \"edit\" | \"hybrid\", "
        "\"summary\": string, "
        "\"tags\": [string], "
        "\"tool_tags\": [string], "
        "\"structural_tags\": [string], "
        "\"task_pattern_tags\": [string], "
        "\"recommended_tools\": [string], "
        "\"required_tools\": [string], "
        "\"workflow_strategy\": string, "
        "\"step_summary\": [string], "
        "\"pinned_context_summary\": string, "
        "\"required_file_types\": [string], "
        "\"expected_inputs\": [{\"name\": string, \"type\": string, \"description\": string}], "
        "\"expected_outputs\": [{\"name\": string, \"type\": string, \"description\": string}], "
        "\"data_preparation_notes\": [string], "
        "\"validation_criteria\": [string], "
        "\"common_variations\": [string], "
        "\"common_fixes\": [string], "
        "\"transformation_intents\": [string], "
        "\"limitations\": [string]"
        "}."
    )
    payload = {
        "project_description": str(project_description or ""),
        "flow_description": str(flow_description or ""),
        "task_match_result": dict(task_match_result or {}),
        "workflow_baseline_source": str(workflow_baseline_source or ""),
        "workflow_json_baseline_profile": dict(workflow_baseline_profile or {}),
        "inferred_specific_tools": list(inferred_specific_tools or []),
        "action_records": list(action_records or []),
        "pinned_context": list(pinned_context or []),
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])],
        "active_tools": [
            {
                "tool_id": str(tool.get("tool_id", "") or ""),
                "name": str(tool.get("name", "") or ""),
                "description": str(tool.get("description", "") or ""),
            }
            for tool in list(active_tools or [])
        ],
    }
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]


def _retry_skill_json_response(
    messages: list[dict[str, str]],
    *,
    selected_model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    repair_messages = list(messages or []) + [
        {
            "role": "user",
            "content": (
                "Return only one valid JSON object. "
                "Do not use markdown fences. Do not add commentary before or after the JSON."
            ),
        }
    ]
    retry_content, _ = _chat_completion_content(
        repair_messages,
        selected_model=selected_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    return _parse_json_response(
        retry_content,
        "Skill development returned an empty retry response.",
        "Skill development retry response was not valid JSON.",
    )


def develop_skill_from_record(
    *,
    project_description: str,
    flow_description: str,
    task_match_result: dict[str, Any] | None = None,
    action_records: list[dict[str, Any]] | None = None,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    current_flow_json_data: dict[str, Any] | None = None,
    selected_model: str | None = None,
    quest_agent_root: str | Path | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    task_match_result = dict(task_match_result or {})
    action_records = list(action_records or [])
    pinned_context = list(pinned_context or [])
    attached_files = list(attached_files or [])
    current_flow_json_data = dict(current_flow_json_data or {})

    if not action_records:
        raise RuntimeError("No recorded actions are available to develop a skill.")

    quest_agent_root = get_quest_agent_root(quest_agent_root)
    registry = write_active_tool_registry(quest_agent_root)
    active_tools = list(registry.get("tools", []))
    active_tool_ids = {str(tool.get("tool_id", "") or "").strip() for tool in active_tools}
    current_flow_json_data, workflow_baseline_source = _prefer_richer_workflow_json(current_flow_json_data, attached_files)
    workflow_baseline_profile = _describe_workflow_baseline(current_flow_json_data)
    inferred_specific_tools = _infer_specific_tools(
        task_match_result=task_match_result,
        current_flow_json_data=current_flow_json_data,
        action_records=action_records,
        project_description=project_description,
        flow_description=flow_description,
        active_tools=active_tools,
    )

    messages = _build_skill_messages(
        project_description=project_description,
        flow_description=flow_description,
        task_match_result=task_match_result,
        action_records=action_records,
        pinned_context=pinned_context,
        attached_files=attached_files,
        active_tools=active_tools,
        current_flow_json_data=current_flow_json_data,
        inferred_specific_tools=inferred_specific_tools,
        workflow_baseline_profile=workflow_baseline_profile,
        workflow_baseline_source=workflow_baseline_source,
    )
    content, _ = _chat_completion_content(
        messages,
        selected_model=selected_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "Skill development returned an empty response.",
            "Skill development response was not valid JSON.",
        )
    except RuntimeError:
        parsed = _retry_skill_json_response(
            messages,
            selected_model=selected_model,
            api_key=api_key,
        )

    normalized = _normalize_skill_payload(
        parsed,
        active_tool_ids,
        task_match_result,
        inferred_specific_tools,
        project_description,
        flow_description,
        action_records,
        current_flow_json_data,
        workflow_baseline_profile,
    )

    skills_root = quest_agent_root / "skills"
    target_root = skills_root / normalized["skill_type"]
    target_root.mkdir(parents=True, exist_ok=True)
    slug = _unique_slug(target_root, parsed.get("slug", normalized["title"]))
    skill_dir = target_root / slug
    attachments_dir = skill_dir / "attachments"
    workflow_dir = skill_dir / "workflow"
    artifacts_dir = skill_dir / "artifacts"
    attachments_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    current_flow_name = str(current_flow_json_data.get("flow_name", "") or "").strip()
    baseline_workflow_source = ""
    if not current_flow_json_data:
        baseline_workflow_source = _pick_workflow_baseline_attachment(attached_files)

    saved_attachments = []
    for path in attached_files:
        source = Path(str(path))
        if not source.exists() or not source.is_file():
            continue
        if baseline_workflow_source and source.as_posix() == baseline_workflow_source:
            continue
        if source.suffix.lower() == ".json" and current_flow_name:
            try:
                with source.open("r", encoding="utf-8") as handle:
                    source_json = json.load(handle)
                if str(source_json.get("flow_name", "") or "").strip() == current_flow_name:
                    continue
            except Exception:
                pass
        target = attachments_dir / source.name
        counter = 2
        while target.exists():
            target = attachments_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1
        shutil.copy2(source, target)
        saved_attachments.append(f"attachments/{target.name}")

    workflow_relative = ""
    if current_flow_json_data:
        workflow_relative = "workflow/final_workflow.json"
        with (workflow_dir / "final_workflow.json").open("w", encoding="utf-8") as handle:
            json.dump(current_flow_json_data, handle, indent=2)
    elif baseline_workflow_source:
        workflow_relative = "workflow/baseline_workflow.json"
        shutil.copy2(baseline_workflow_source, workflow_dir / "baseline_workflow.json")

    action_record_path = artifacts_dir / "action_record.json"
    with action_record_path.open("w", encoding="utf-8") as handle:
        json.dump(action_records, handle, indent=2)

    created_at = _iso_now()
    project_description = str(project_description or "").strip()
    flow_description = str(flow_description or "").strip()
    pinned_context_summary = normalized["pinned_context_summary"] or "\n".join(pinned_context[:4]).strip() or "None provided."

    skill_json = {
        "schema_version": "1.1",
        "skill_id": slug,
        "version": 1,
        "parent_skill_id": None,
        "title": normalized["title"],
        "slug": slug,
        "skill_type": normalized["skill_type"],
        "skill_level": normalized["skill_level"],
        "summary": normalized["summary"],
        "status": "draft",
        "created_at": created_at,
        "updated_at": created_at,
        "created_by": "quest_agent",
        "source": {
            "session_id": "",
            "derived_from_run_id": "",
        },
        "task": {
            "description": project_description or normalized["summary"],
            "pinned_context_summary": pinned_context_summary,
            "task_fingerprint": _fingerprint({
                "project_description": project_description,
                "flow_description": flow_description,
                "action_records": action_records,
            }),
            "context_fingerprint": _fingerprint({
                "pinned_context": pinned_context,
                "attached_files": [Path(path).name for path in attached_files],
            }),
        },
        "classification": {
            "tags": normalized["tags"],
            "domains": [],
            "tool_tags": normalized["tool_tags"],
            "structural_tags": normalized["structural_tags"],
            "task_pattern_tags": normalized["task_pattern_tags"],
        },
        "tools": {
            "recommended": normalized["recommended_tools"],
            "required": normalized["required_tools"],
            "optional": [],
        },
        "files": {
            "attachments": saved_attachments,
            "workflow_json": workflow_relative,
        },
        "action_record": {
            "path": "artifacts/action_record.json",
            "records": action_records,
        },
        "inputs": {
            "required_file_types": normalized["required_file_types"],
            "expected_inputs": normalized["expected_inputs"],
        },
        "outputs": {
            "expected_outputs": normalized["expected_outputs"],
        },
        "plan": {
            "skill_mode": normalized["skill_mode"],
            "workflow_strategy": normalized["workflow_strategy"],
            "step_summary": normalized["step_summary"],
            "transformation_intents": normalized["transformation_intents"],
        },
        "edit_recipe": {
            "required_tools": normalized["edit_recipe"]["required_tools"],
            "expected_inputs": normalized["edit_recipe"]["expected_inputs"],
            "expected_outputs": normalized["edit_recipe"]["expected_outputs"],
            "common_variations": normalized["edit_recipe"]["common_variations"],
            "validation_criteria": normalized["edit_recipe"]["validation_criteria"],
            "common_fixes": normalized["edit_recipe"]["common_fixes"],
            "transformation_intents": normalized["edit_recipe"]["transformation_intents"],
        },
        "validation": {
            "status": "draft",
            "criteria": normalized["validation_criteria"],
            "last_validated_at": "",
        },
        "limitations": normalized["limitations"],
    }

    with (skill_dir / "skill.json").open("w", encoding="utf-8") as handle:
        json.dump(skill_json, handle, indent=2)

    record_table = format_action_records_table(action_records)
    markdown_lines = [
        f"# {normalized['title']}",
        "",
        "## Task Description",
        project_description or normalized["summary"],
        "",
        "## Pinned Context",
        pinned_context_summary or "None",
        "",
        "## Flow Description",
        flow_description or "None",
        "",
        "## Skill Type",
        normalized["skill_type"],
        "",
        "## Skill Level",
        normalized["skill_level"],
        "",
        "## Skill Mode",
        normalized["skill_mode"],
        "",
        "## Recommended QuESt Tools",
    ]
    if normalized["recommended_tools"]:
        markdown_lines.extend(f"- {tool_id}" for tool_id in normalized["recommended_tools"])
    else:
        markdown_lines.append("- None")
    markdown_lines.extend([
        "",
        "## Required Inputs",
    ])
    if normalized["expected_inputs"]:
        markdown_lines.extend(
            f"- {item['name']} ({item['type']}): {item['description']}".rstrip(": ")
            for item in normalized["expected_inputs"]
        )
    else:
        markdown_lines.append("- None documented")
    markdown_lines.extend([
        "",
        "## Edit Recipe",
        "### Expected Outputs",
    ])
    if normalized["expected_outputs"]:
        markdown_lines.extend(
            f"- {item['name']} ({item['type']}): {item['description']}".rstrip(": ")
            for item in normalized["expected_outputs"]
        )
    else:
        markdown_lines.append("- None documented")
    markdown_lines.extend([
        "",
        "### Common Variations",
    ])
    if normalized["common_variations"]:
        markdown_lines.extend(f"- {item}" for item in normalized["common_variations"])
    else:
        markdown_lines.append("- None documented")
    markdown_lines.extend([
        "",
        "### Common Fixes",
    ])
    if normalized["common_fixes"]:
        markdown_lines.extend(f"- {item}" for item in normalized["common_fixes"])
    else:
        markdown_lines.append("- None documented")
    markdown_lines.extend([
        "",
        "### Transformation Intents",
    ])
    if normalized["transformation_intents"]:
        markdown_lines.extend(f"- {item}" for item in normalized["transformation_intents"])
    else:
        markdown_lines.append("- None documented")
    markdown_lines.extend([
        "",
        "## Workflow Build Plan",
    ])
    markdown_lines.extend(f"{index}. {step}" for index, step in enumerate(normalized["step_summary"], start=1))
    markdown_lines.extend([
        "",
        "## Data Preparation Notes",
    ])
    if normalized["data_preparation_notes"]:
        markdown_lines.extend(f"- {note}" for note in normalized["data_preparation_notes"])
    else:
        markdown_lines.append("- None")
    markdown_lines.extend([
        "",
        "## Validation Notes",
    ])
    if normalized["validation_criteria"]:
        markdown_lines.extend(f"- {item}" for item in normalized["validation_criteria"])
    else:
        markdown_lines.append("- None")
    markdown_lines.extend([
        "",
        "## Limitations",
    ])
    if normalized["limitations"]:
        markdown_lines.extend(f"- {item}" for item in normalized["limitations"])
    else:
        markdown_lines.append("- None noted")
    markdown_lines.extend([
        "",
        "## Action Record",
        f"Action record file: `artifacts/action_record.json`",
        "",
        "```text",
        record_table or "No actions recorded.",
        "```",
    ])

    with (skill_dir / "SKILL.md").open("w", encoding="utf-8") as handle:
        handle.write("\n".join(markdown_lines).rstrip() + "\n")

    build_skills_manifest(quest_agent_root)
    return {
        "skill_id": slug,
        "title": normalized["title"],
        "skill_type": normalized["skill_type"],
        "skill_level": normalized["skill_level"],
        "folder_path": skill_dir.as_posix(),
        "skill_json_path": (skill_dir / "skill.json").as_posix(),
        "skill_md_path": (skill_dir / "SKILL.md").as_posix(),
        "workflow_json_path": (workflow_dir / "final_workflow.json").as_posix() if workflow_relative else "",
    }
