import json
import re
from pathlib import Path
from typing import Any

from ..skill_library import get_quest_agent_root, load_skill_library
from ..tool_registry import write_active_tool_registry


def _tokenize(text: str) -> set[str]:
    raw_tokens = re.findall(r"[a-zA-Z0-9_]+", str(text or "").casefold())
    stopwords = {
        "about", "agent", "also", "and", "canvas", "data", "file", "files",
        "flow", "for", "from", "have", "into", "need", "node", "nodes",
        "please", "quest", "task", "that", "the", "then", "this", "tool",
        "tools", "use", "using", "workflow", "workflows", "your",
    }
    return {token for token in raw_tokens if len(token) > 2 and token not in stopwords}


def _score_tokens(query_tokens: set[str], candidate_tokens: set[str]) -> float:
    if not query_tokens or not candidate_tokens:
        return 0.0
    return len(query_tokens.intersection(candidate_tokens)) / max(1, len(query_tokens))


def _clean_list(values: Any, limit: int | None = None) -> list[str]:
    cleaned = []
    for value in list(values or []):
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
        if limit is not None and len(cleaned) >= limit:
            break
    return cleaned


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
    query_tokens = _tokenize(query)
    matches = []
    for tool in _load_tools(quest_agent_root):
        candidate_tokens = set()
        for field in ("tool_id", "name", "description", "search_key"):
            candidate_tokens.update(_tokenize(tool.get(field, "")))
        for field in ("aliases", "input_types", "output_types", "typical_tasks", "workflow_roles"):
            for value in list(tool.get(field, []) or []):
                candidate_tokens.update(_tokenize(value))
        score = _score_tokens(query_tokens, candidate_tokens)
        if score <= 0:
            continue
        shared = sorted(query_tokens.intersection(candidate_tokens))
        matches.append({
            "tool_id": str(tool.get("tool_id", "") or ""),
            "name": str(tool.get("name", "") or ""),
            "score": round(score, 4),
            "reason": "Matched keywords: " + ", ".join(shared[:8]),
            "description": str(tool.get("description", "") or ""),
        })
    matches.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("name", "")).casefold()))
    return {"matches": matches[: max(1, int(limit or 1))], "query_tokens": sorted(query_tokens)}


def search_skills(query: str, quest_agent_root: str | Path | None = None, limit: int = 8) -> dict[str, Any]:
    query_tokens = _tokenize(query)
    matches = []
    for skill in _load_skills(quest_agent_root):
        candidate_tokens = set()
        for value in (
            getattr(skill, "skill_id", ""),
            getattr(skill, "title", ""),
            getattr(skill, "summary", ""),
        ):
            candidate_tokens.update(_tokenize(value))
        for field in ("tags", "tool_tags", "structural_tags", "task_pattern_tags", "recommended_tools", "required_tools"):
            for value in list(getattr(skill, field, []) or []):
                candidate_tokens.update(_tokenize(value))
        score = _score_tokens(query_tokens, candidate_tokens)
        if score <= 0:
            continue
        if str(getattr(skill, "status", "") or "").casefold() == "validated":
            score = min(1.0, score + 0.08)
        if str(getattr(skill, "validation_status", "") or "").casefold() == "passed":
            score = min(1.0, score + 0.07)
        shared = sorted(query_tokens.intersection(candidate_tokens))
        matches.append({
            "skill_id": str(getattr(skill, "skill_id", "") or ""),
            "title": str(getattr(skill, "title", "") or ""),
            "skill_type": str(getattr(skill, "skill_type", "") or ""),
            "status": str(getattr(skill, "status", "") or ""),
            "validation_status": str(getattr(skill, "validation_status", "") or ""),
            "score": round(score, 4),
            "reason": "Matched keywords: " + ", ".join(shared[:8]) if shared else "Validated skill with weak keyword overlap.",
            "recommended_tools": _clean_list(getattr(skill, "recommended_tools", []), 6),
            "required_tools": _clean_list(getattr(skill, "required_tools", []), 6),
        })
    matches.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("title", "")).casefold()))
    return {"matches": matches[: max(1, int(limit or 1))], "query_tokens": sorted(query_tokens)}


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
    structural_valid = not missing_parts
    status = "complete" if structural_valid else "incomplete"
    task_alignment = "likely_aligned" if structural_valid else "partial"
    if not data_nodes and not python_nodes:
        task_alignment = "not_aligned"
    evidence = []
    for item in missing_parts:
        evidence.append({"type": "missing_part", "detail": item})
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
        "warnings": [],
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
    return "\n".join(lines)
