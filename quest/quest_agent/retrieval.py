import re
from pathlib import Path
from typing import Any

from .skill_library import get_quest_agent_root, load_skill_library
from .tool_registry import write_active_tool_registry


def _tokenize(text: str) -> set[str]:
    raw = re.findall(r"[a-zA-Z0-9_]+", str(text or "").lower())
    stopwords = {
        "the", "and", "for", "with", "from", "into", "this", "that", "your", "have",
        "need", "using", "use", "task", "data", "file", "files", "workflow", "tool",
        "tools", "quest", "agent", "please", "about", "then", "than", "also",
    }
    return {token for token in raw if len(token) > 2 and token not in stopwords}


def _score_overlap(query_tokens: set[str], candidate_tokens: set[str]) -> float:
    if not query_tokens or not candidate_tokens:
        return 0.0
    shared = query_tokens.intersection(candidate_tokens)
    return len(shared) / max(len(query_tokens), 1)


def _attachment_tokens(attachments: list[str]) -> set[str]:
    tokens = set()
    for path in attachments or []:
        name = Path(str(path)).name
        tokens.update(_tokenize(name))
    return tokens


def _build_tool_candidate(tool: dict[str, Any], query_tokens: set[str]) -> dict[str, Any]:
    candidate_tokens = set()
    for field in (
        tool.get("tool_id", ""),
        tool.get("name", ""),
        tool.get("description", ""),
        tool.get("search_key", ""),
    ):
        candidate_tokens.update(_tokenize(field))
    for group in ("aliases", "input_types", "output_types", "typical_tasks", "workflow_roles"):
        for value in tool.get(group, []) or []:
            candidate_tokens.update(_tokenize(value))

    score = _score_overlap(query_tokens, candidate_tokens)
    shared = sorted(query_tokens.intersection(candidate_tokens))
    return {
        "tool_id": str(tool.get("tool_id", "") or ""),
        "name": str(tool.get("name", "") or ""),
        "score": round(score, 4),
        "reason": f"Matched keywords: {', '.join(shared[:8])}" if shared else "No strong keyword overlap.",
        "raw": tool,
    }


def _build_skill_candidate(skill: Any, query_tokens: set[str], active_tool_ids: set[str]) -> dict[str, Any]:
    candidate_tokens = set()
    for value in (
        getattr(skill, "skill_id", ""),
        getattr(skill, "title", ""),
        getattr(skill, "summary", ""),
    ):
        candidate_tokens.update(_tokenize(value))
    for group in ("tags", "recommended_tools", "required_tools"):
        for value in getattr(skill, group, []) or []:
            candidate_tokens.update(_tokenize(value))
    raw_data = getattr(skill, "raw_data", {}) or {}
    task = raw_data.get("task", {}) if isinstance(raw_data, dict) else {}
    candidate_tokens.update(_tokenize(task.get("description", "")))
    candidate_tokens.update(_tokenize(task.get("pinned_context_summary", "")))

    base_score = _score_overlap(query_tokens, candidate_tokens)
    required_tools = set(getattr(skill, "required_tools", []) or [])
    missing_required = sorted(required_tools.difference(active_tool_ids))
    status = str(getattr(skill, "status", "") or "").strip().lower()
    validation_status = str(getattr(skill, "validation_status", "") or "").strip().lower()

    bonus = 0.0
    if status == "validated":
        bonus += 0.08
    if validation_status == "passed":
        bonus += 0.07
    if getattr(skill, "skill_type", "") == "quest_tool_specific":
        bonus += 0.04

    penalty = 0.25 if missing_required else 0.0
    final_score = max(0.0, min(1.0, base_score + bonus - penalty))
    shared = sorted(query_tokens.intersection(candidate_tokens))

    if missing_required:
        reason = f"Missing required active tools: {', '.join(missing_required)}"
    elif shared:
        reason = f"Matched keywords: {', '.join(shared[:8])}"
    else:
        reason = "No strong keyword overlap."

    return {
        "skill_id": str(getattr(skill, "skill_id", "") or ""),
        "title": str(getattr(skill, "title", "") or ""),
        "skill_type": str(getattr(skill, "skill_type", "") or ""),
        "status": str(getattr(skill, "status", "") or ""),
        "score": round(final_score, 4),
        "reason": reason,
        "missing_required_tools": missing_required,
        "raw": skill,
    }


def run_retrieval_test(
    task_description: str,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    quest_agent_root: str | Path | None = None,
) -> dict[str, Any]:
    quest_agent_root = get_quest_agent_root(quest_agent_root)
    pinned_context = pinned_context or []
    attached_files = attached_files or []

    registry = write_active_tool_registry(quest_agent_root)
    loaded_skills = load_skill_library(quest_agent_root)

    combined_text = "\n".join(
        [str(task_description or "")]
        + [str(item or "") for item in pinned_context]
        + [Path(str(path)).name for path in attached_files]
    )
    query_tokens = _tokenize(combined_text).union(_attachment_tokens(attached_files))

    tools = list(registry.get("tools", []))
    active_tool_ids = {str(tool.get("tool_id", "") or "") for tool in tools}

    tool_candidates = [_build_tool_candidate(tool, query_tokens) for tool in tools]
    tool_candidates.sort(key=lambda item: (-item["score"], item["name"].lower()))

    skill_candidates = [
        _build_skill_candidate(skill, query_tokens, active_tool_ids)
        for skill in loaded_skills.get("skills", [])
    ]
    skill_candidates.sort(key=lambda item: (-item["score"], item["title"].lower()))

    selected_tools = [candidate for candidate in tool_candidates if candidate["score"] > 0]
    selected_skills = [candidate for candidate in skill_candidates if candidate["score"] > 0]

    if selected_tools:
        strategy = "use_tools_or_skills"
    else:
        strategy = "no_viable_quest_tools"

    return {
        "query_tokens": sorted(query_tokens),
        "tool_matches": selected_tools[:8],
        "skill_matches": selected_skills[:8],
        "tool_errors": list(loaded_skills.get("errors", [])),
        "strategy": strategy,
    }
