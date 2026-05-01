import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from .skill_library import SkillRecord, get_quest_agent_root, load_skill_library
from .tool_registry import write_active_tool_registry


MODEL_NAME_MAP = {
    "GPT-5.4": "gpt-5.4",
    "GPT-5.4 Mini": "gpt-5.4-mini",
    "GPT-5.2 Codex": "gpt-5.2-codex",
    "GPT-4.1": "gpt-4.1",
    "o4-mini": "o4-mini",
}

CANVAS_ACTION_TYPES = {
    "create_node",
    "update_node",
    "add_subflow",
    "connect_nodes",
    "rename_selected_node",
    "update_selected_text_node",
    "delete_selected_nodes",
    "load_workflow_json",
}

CANONICAL_NODE_TYPES = {"data", "py", "text"}


def _resolve_model_name(model_name: str | None) -> str:
    cleaned = str(model_name or "").strip()
    if cleaned in MODEL_NAME_MAP:
        return MODEL_NAME_MAP[cleaned]
    return cleaned or "gpt-5.4"


def _resolve_api_key(explicit_api_key: str | None = None) -> str:
    if explicit_api_key and str(explicit_api_key).strip():
        return str(explicit_api_key).strip()
    env_key = str(os.environ.get("OPENAI_API_KEY", "") or "").strip()
    if env_key:
        return env_key
    raise RuntimeError("OpenAI API key is not configured. Set OPENAI_API_KEY before using QuESt Agent task analysis.")


def _skill_prompt_entry(skill: SkillRecord, active_tool_ids: set[str]) -> dict[str, Any]:
    required_tools = list(skill.required_tools or [])
    missing_required = sorted(set(required_tools).difference(active_tool_ids))
    return {
        "skill_id": skill.skill_id,
        "title": skill.title,
        "skill_type": skill.skill_type,
        "status": skill.status,
        "summary": skill.summary,
        "tags": list(skill.tags or []),
        "recommended_tools": list(skill.recommended_tools or []),
        "required_tools": required_tools,
        "validation_status": skill.validation_status,
        "usable_now": not missing_required,
        "missing_required_tools": missing_required,
    }


def _tool_prompt_entry(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool_id": str(tool.get("tool_id", "") or ""),
        "name": str(tool.get("name", "") or ""),
        "description": str(tool.get("description", "") or ""),
        "input_types": list(tool.get("input_types", []) or []),
        "output_types": list(tool.get("output_types", []) or []),
        "typical_tasks": list(tool.get("typical_tasks", []) or []),
        "workflow_roles": list(tool.get("workflow_roles", []) or []),
        "aliases": list(tool.get("aliases", []) or []),
        "active": bool(tool.get("active", False)),
    }


def _build_messages(
    task_description: str,
    pinned_context: list[str],
    attached_files: list[str],
    attached_workflow_jsons: list[dict[str, Any]],
    workspace_relationship_context: dict[str, Any],
    implicit_code_context: list[dict[str, Any]],
    python_node_wrapper_rules: dict[str, Any],
    tools: list[dict[str, Any]],
    skills: list[SkillRecord],
) -> list[dict[str, Any]]:
    active_tool_ids = {str(tool.get("tool_id", "") or "") for tool in tools}
    tool_entries = [_tool_prompt_entry(tool) for tool in tools]
    skill_entries = [_skill_prompt_entry(skill, active_tool_ids) for skill in skills]
    attachment_names = [Path(str(path)).name for path in attached_files]

    system_prompt = (
        "You are QuESt Agent's task matcher. "
        "Your job is to interpret a messy analytics or workflow-building request and recommend only from the provided active QuESt tools and saved skills. "
        "Do not invent tools, skills, or IDs. "
        "If Python node wrapper behavior is relevant, treat python_node_wrapper_rules as authoritative workspace constraints. "
        "Prefer the smallest viable active tool set. "
        "Use quest_tool_specific skills only when their required tools are active. "
        "If nothing in QuESt can do the task, say so clearly. "
        "Return valid JSON only with this shape: "
        "{"
        "\"project_description\": string, "
        "\"task\": string, "
        "\"flow_description\": string, "
        "\"strategy\": string, "
        "\"recommended_tools\": [{\"tool_id\": string, \"confidence\": number, \"reason\": string}], "
        "\"recommended_skills\": [{\"skill_id\": string, \"confidence\": number, \"reason\": string}], "
        "\"notes\": [string]"
        "}."
        "Project description should capture the high-level study or analysis goal. "
        "Task should capture what the user currently wants to do on the workflow, such as create, edit, explain, or prepare inputs. "
        "Flow description should summarize the current flow on canvas or attached workflow, including structure, tools used, and inputs/outputs when possible. "
        "Strategy must be one of: use_quest_skill, use_general_python_skill_plus_tools, use_tools_only, no_viable_quest_solution."
    )

    user_payload = {
        "task_description": str(task_description or ""),
        "pinned_context": list(pinned_context or []),
        "attached_files": attachment_names,
        "attached_workflow_jsons": list(attached_workflow_jsons or []),
        "workspace_relationship_context": dict(workspace_relationship_context or {}),
        "implicit_code_context": list(implicit_code_context or []),
        "python_node_wrapper_rules": dict(python_node_wrapper_rules or {}),
        "active_tools": tool_entries,
        "saved_skills": skill_entries,
    }

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=True, indent=2)},
    ]


def _coerce_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except Exception:
        confidence = 0.0
    return max(0.0, min(1.0, round(confidence, 4)))


def _normalize_match_result(
    raw_result: dict[str, Any],
    tools: list[dict[str, Any]],
    skills: list[SkillRecord],
) -> dict[str, Any]:
    tool_lookup = {
        str(tool.get("tool_id", "") or ""): str(tool.get("name", "") or "")
        for tool in tools
    }
    skill_lookup = {
        str(skill.skill_id or ""): {
            "title": str(skill.title or ""),
            "skill_type": str(skill.skill_type or ""),
        }
        for skill in skills
    }

    normalized_tools = []
    for item in list(raw_result.get("recommended_tools", []) or []):
        tool_id = str(item.get("tool_id", "") or "").strip()
        if not tool_id or tool_id not in tool_lookup:
            continue
        normalized_tools.append(
            {
                "tool_id": tool_id,
                "name": tool_lookup.get(tool_id, tool_id),
                "confidence": _coerce_confidence(item.get("confidence", 0.0)),
                "reason": str(item.get("reason", "") or "").strip(),
            }
        )

    normalized_skills = []
    for item in list(raw_result.get("recommended_skills", []) or []):
        skill_id = str(item.get("skill_id", "") or "").strip()
        if not skill_id or skill_id not in skill_lookup:
            continue
        skill_meta = skill_lookup[skill_id]
        normalized_skills.append(
            {
                "skill_id": skill_id,
                "title": skill_meta.get("title", skill_id),
                "skill_type": skill_meta.get("skill_type", ""),
                "confidence": _coerce_confidence(item.get("confidence", 0.0)),
                "reason": str(item.get("reason", "") or "").strip(),
            }
        )

    strategy = str(raw_result.get("strategy", "") or "").strip()
    if strategy not in {
        "use_quest_skill",
        "use_general_python_skill_plus_tools",
        "use_tools_only",
        "no_viable_quest_solution",
    }:
        strategy = "use_tools_only" if normalized_tools else "no_viable_quest_solution"

    return {
        "project_description": str(raw_result.get("project_description", "") or "").strip(),
        "task": str(raw_result.get("task", "") or "").strip(),
        "flow_description": str(raw_result.get("flow_description", "") or "").strip(),
        "strategy": strategy,
        "tool_matches": normalized_tools[:8],
        "skill_matches": normalized_skills[:8],
        "notes": [str(note).strip() for note in list(raw_result.get("notes", []) or []) if str(note).strip()],
    }


def _recent_conversation(recent_messages: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    conversation = []
    for message in list(recent_messages or [])[-6:]:
        role = str(message.get("role", "") or "").strip().lower()
        if role not in {"user", "assistant"}:
            continue
        content = str(message.get("content", "") or "").strip()
        if content:
            conversation.append({"role": role, "content": content})
    return conversation


def _task_analysis_guidance(task_match_result: dict[str, Any] | None) -> dict[str, Any]:
    result = dict(task_match_result or {})

    top_tool_matches = []
    for item in list(result.get("tool_matches", []) or [])[:4]:
        top_tool_matches.append(
            {
                "tool_id": str(item.get("tool_id", "") or "").strip(),
                "name": str(item.get("name", "") or "").strip(),
                "reason": str(item.get("reason", "") or "").strip(),
                "confidence": _coerce_confidence(item.get("confidence", 0.0)),
            }
        )

    top_skill_matches = []
    for item in list(result.get("skill_matches", []) or [])[:4]:
        top_skill_matches.append(
            {
                "skill_id": str(item.get("skill_id", "") or "").strip(),
                "title": str(item.get("title", "") or "").strip(),
                "skill_type": str(item.get("skill_type", "") or "").strip(),
                "reason": str(item.get("reason", "") or "").strip(),
                "confidence": _coerce_confidence(item.get("confidence", 0.0)),
            }
        )

    flow_description = str(result.get("flow_description", "") or "").strip()
    notes = [str(note).strip() for note in list(result.get("notes", []) or [])[:6] if str(note).strip()]
    lowered_notes = [note.casefold() for note in notes]
    lowered_flow = flow_description.casefold()
    planning_directives = []
    if flow_description:
        planning_directives.append(
            "Treat the analyzed current flow as the source of truth for what already exists on canvas."
        )
    if any(
        token in lowered_flow or any(token in note for note in lowered_notes)
        for token in (
            "unconnected",
            "no connections",
            "missing",
            "no inferred input or output ports",
            "empty input values",
            "default output port",
            "incomplete",
        )
    ):
        planning_directives.append(
            "Prefer completing and repairing the existing flow over rebuilding it from scratch."
        )
    if flow_description:
        planning_directives.append(
            "Reuse existing node names, ports, and subflows when possible unless the user explicitly asks to rebuild or replace them."
        )

    return {
        "strategy": str(result.get("strategy", "") or "").strip(),
        "task": str(result.get("task", "") or "").strip(),
        "project_description": str(result.get("project_description", "") or "").strip(),
        "flow_description": flow_description,
        "top_tool_matches": top_tool_matches,
        "top_skill_matches": top_skill_matches,
        "notes": notes,
        "planning_directives": planning_directives,
    }


def _parse_json_response(content: str, empty_message: str, invalid_message: str) -> dict[str, Any]:
    if not content:
        raise RuntimeError(empty_message)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(invalid_message) from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(invalid_message)
    return parsed


def run_grounded_chat_reply(
    user_prompt: str,
    task_match_result: dict[str, Any] | None = None,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    attached_workflow_jsons: list[dict[str, Any]] | None = None,
    workspace_relationship_context: dict[str, Any] | None = None,
    implicit_code_context: list[dict[str, Any]] | None = None,
    python_node_wrapper_rules: dict[str, Any] | None = None,
    skill_execution_recipes: dict[str, Any] | None = None,
    selected_model: str | None = None,
    recent_messages: list[dict[str, Any]] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    system_prompt = (
        "You are QuESt Agent speaking directly to the user in a natural, helpful way. "
        "Use the structured task analysis as grounding, but do not simply restate it mechanically. "
        "Answer the user's latest request or question like a capable human assistant. "
        "Be concise, practical, and specific. "
        "If Python node wrappers, ports, or notebook parsing come up, use python_node_wrapper_rules as the authoritative contract. "
        "Do not invent unavailable QuESt tools or skills. "
        "If the analyzer found no viable QuESt solution, explain that plainly and suggest a useful next move. "
        "If useful, mention the strongest matched tools or skills, but keep the tone conversational rather than report-like. "
        "Do not mention JSON, schemas, or internal implementation details unless the user asks. "
        "Return valid JSON only with this shape: {\"reply\": string}."
    )

    grounding_payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "task_analysis": dict(task_match_result or {}),
        "task_analysis_guidance": _task_analysis_guidance(task_match_result),
        "pinned_context": list(pinned_context or []),
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])],
        "attached_workflow_jsons": list(attached_workflow_jsons or []),
        "workspace_relationship_context": dict(workspace_relationship_context or {}),
        "implicit_code_context": list(implicit_code_context or []),
        "python_node_wrapper_rules": dict(python_node_wrapper_rules or {}),
        "skill_execution_recipes": dict(skill_execution_recipes or {}),
        "recent_conversation": _recent_conversation(recent_messages),
    }

    client = OpenAI(api_key=_resolve_api_key(api_key))
    response = client.chat.completions.create(
        model=_resolve_model_name(selected_model),
        temperature=0.4,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(grounding_payload, ensure_ascii=True, indent=2)},
        ],
    )
    content = str(response.choices[0].message.content or "").strip() if response.choices else ""
    parsed = _parse_json_response(
        content,
        "OpenAI returned an empty grounded chat reply.",
        "OpenAI grounded chat reply was not valid JSON.",
    )
    reply = str(parsed.get("reply", "") or "").strip()
    if not reply:
        raise RuntimeError("OpenAI grounded chat reply was missing the reply field.")
    return {"reply": reply}


def run_chat_router(
    user_prompt: str,
    task_match_result: dict[str, Any] | None = None,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    attached_workflow_jsons: list[dict[str, Any]] | None = None,
    workspace_relationship_context: dict[str, Any] | None = None,
    implicit_code_context: list[dict[str, Any]] | None = None,
    python_node_wrapper_rules: dict[str, Any] | None = None,
    skill_execution_recipes: dict[str, Any] | None = None,
    selected_model: str | None = None,
    recent_messages: list[dict[str, Any]] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    system_prompt = (
        "You are QuESt Agent's chat router. "
        "Decide whether the latest user message should trigger a fresh task analysis, should execute a direct canvas action, or should be answered directly using the current analyzed task context. "
        "If Python node wrapper rules are discussed, treat python_node_wrapper_rules as authoritative context for what the workspace supports. "
        "Choose 'analyze_task' when the user is describing a new task, changing the task, asking for tool/skill/workflow recommendations, or asking you to reassess based on new context. "
        "Choose 'execute_canvas_action' when the user is clearly asking QuESt Agent to create, rename, edit, or delete workflow items on the canvas. "
        "Choose 'answer_only' when the user is asking a follow-up question, asking for explanation, asking about the current recommendations, or making a conversational request that can be answered from the current context. "
        "Return valid JSON only with this shape: "
        "{\"action\": \"analyze_task\" | \"execute_canvas_action\" | \"answer_only\", \"reason\": string, \"task_focus\": string}."
    )

    payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "current_task_analysis": dict(task_match_result or {}),
        "task_analysis_guidance": _task_analysis_guidance(task_match_result),
        "pinned_context": list(pinned_context or []),
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])],
        "attached_workflow_jsons": list(attached_workflow_jsons or []),
        "workspace_relationship_context": dict(workspace_relationship_context or {}),
        "implicit_code_context": list(implicit_code_context or []),
        "python_node_wrapper_rules": dict(python_node_wrapper_rules or {}),
        "skill_execution_recipes": dict(skill_execution_recipes or {}),
        "recent_conversation": _recent_conversation(recent_messages),
    }

    client = OpenAI(api_key=_resolve_api_key(api_key))
    response = client.chat.completions.create(
        model=_resolve_model_name(selected_model),
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
        ],
    )
    content = str(response.choices[0].message.content or "").strip() if response.choices else ""
    parsed = _parse_json_response(
        content,
        "OpenAI returned an empty chat router response.",
        "OpenAI chat router response was not valid JSON.",
    )
    action = str(parsed.get("action", "") or "").strip()
    if action not in {"analyze_task", "execute_canvas_action", "answer_only"}:
        action = "analyze_task" if not task_match_result else "answer_only"
    return {
        "action": action,
        "reason": str(parsed.get("reason", "") or "").strip(),
        "task_focus": str(parsed.get("task_focus", "") or "").strip(),
    }


def _request_looks_actionable(user_prompt: str) -> bool:
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
        "canvas",
        "workflow",
        "flow",
        "subflow",
        "sub-flow",
        "selected",
        "datanode",
        "data node",
        "data-node",
        "pynode",
        "py node",
        "python node",
        "pythonnode",
        "text node",
        "annotation",
        "note node",
    )
    return any(token in prompt for token in action_signals) and any(token in prompt for token in canvas_targets)


def _normalize_workspace_action_type(value: Any) -> str:
    action_type = str(value or "").strip().lower()
    aliases = {
        "create": "create_node",
        "add": "create_node",
        "add_node": "create_node",
        "insert": "create_node",
        "insert_node": "create_node",
        "make": "create_node",
        "make_node": "create_node",
        "update_node": "update_node",
        "edit_node": "update_node",
        "modify_node": "update_node",
        "set_node": "update_node",
        "update_data_node": "update_node",
        "edit_data_node": "update_node",
        "set_data_node": "update_node",
        "add_subflow": "add_subflow",
        "create_subflow": "add_subflow",
        "make_subflow": "add_subflow",
        "create_workflow_tab": "add_subflow",
        "connect": "connect_nodes",
        "connect_node": "connect_nodes",
        "wire": "connect_nodes",
        "rename": "rename_selected_node",
        "rename_node": "rename_selected_node",
        "edit_text": "update_selected_text_node",
        "update_text": "update_selected_text_node",
        "update_text_node": "update_selected_text_node",
        "set_text": "update_selected_text_node",
        "delete": "delete_selected_nodes",
        "remove": "delete_selected_nodes",
        "delete_nodes": "delete_selected_nodes",
        "remove_nodes": "delete_selected_nodes",
        "load_workflow_json": "load_workflow_json",
        "load_workflow": "load_workflow_json",
        "load_flow_json": "load_workflow_json",
        "load_json": "load_workflow_json",
        "import_workflow": "load_workflow_json",
        "import_flow": "load_workflow_json",
        "load_template": "load_workflow_json",
        "reuse_template": "load_workflow_json",
    }
    return aliases.get(action_type, action_type)


def _normalize_workspace_node_type(value: Any) -> str:
    node_type = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "data": "data",
        "datanode": "data",
        "data_node": "data",
        "input": "data",
        "py": "py",
        "python": "py",
        "python_node": "py",
        "pynode": "py",
        "code": "py",
        "text": "text",
        "text_node": "text",
        "note": "text",
        "annotation": "text",
        "backdrop": "text",
    }
    return aliases.get(node_type, node_type)


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().casefold()
    return text in {"1", "true", "yes", "y", "on"}


def _build_path_guidance(
    user_prompt: str,
    canvas_context: dict[str, Any] | None = None,
    task_match_result: dict[str, Any] | None = None,
    skill_execution_recipes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    canvas_context = dict(canvas_context or {})
    task_match_result = dict(task_match_result or {})
    skill_execution_recipes = dict(skill_execution_recipes or {})
    lowered = str(user_prompt or "").strip().casefold()
    node_count = len(list(canvas_context.get("nodes", []) or []))
    flow_description = str(task_match_result.get("flow_description", "") or "").strip()
    recipe_entries = [
        dict(item or {})
        for item in list(skill_execution_recipes.get("recipes", []) or [])
        if isinstance(item, dict)
    ]
    reusable_templates = []
    for recipe in recipe_entries:
        workflow_template = dict(recipe.get("workflow_template", {}) or {})
        workflow_path = str(workflow_template.get("path", "") or "").strip()
        confidence = _coerce_confidence(recipe.get("confidence", 0.0))
        if workflow_path and confidence >= 0.55:
            reusable_templates.append(
                {
                    "skill_id": str(recipe.get("skill_id", "") or "").strip(),
                    "title": str(recipe.get("title", "") or "").strip(),
                    "confidence": confidence,
                    "workflow_path": workflow_path,
                    "summary": str(recipe.get("summary", "") or "").strip(),
                }
            )

    available_paths = [
        {
            "path_id": "manual_canvas_build",
            "label": "Build on canvas step by step",
            "difficulty": "high",
            "best_when": "No strong reusable example exists, or the user explicitly wants manual node-by-node construction.",
        },
        {
            "path_id": "draft_workflow_json_then_load",
            "label": "Draft workflow JSON then load it",
            "difficulty": "expert",
            "best_when": "The user explicitly wants direct JSON authoring, or a structured flow can be created faster in JSON than on canvas.",
        },
    ]
    if node_count > 0 or flow_description:
        available_paths.insert(
            0,
            {
                "path_id": "edit_current_flow",
                "label": "Edit the current flow",
                "difficulty": "medium",
                "best_when": "The current canvas already contains a relevant partial flow that should be completed, fixed, or adapted.",
            },
        )
    if reusable_templates:
        available_paths.insert(
            0,
            {
                "path_id": "reuse_skill_workflow_json",
                "label": "Load and adapt a matched skill/example flow",
                "difficulty": "low",
                "best_when": "A strong matched skill already includes a reusable workflow JSON template close to the requested task.",
                "candidate_skills": reusable_templates[:3],
            },
        )

    explicit_json = any(
        token in lowered
        for token in (
            "draft workflow json",
            "write workflow json",
            "generate workflow json",
            "create the json directly",
            "edit the json directly",
            "json first",
        )
    )
    manual_only = any(
        token in lowered
        for token in (
            "manually",
            "node by node",
            "connection by connection",
            "build on canvas",
        )
    )
    edit_current = (
        (node_count > 0 or flow_description)
        and any(
            token in lowered
            for token in ("edit", "revise", "change", "modify", "fix", "repair", "complete", "finish", "adapt")
        )
    )

    if explicit_json:
        recommended_path = "draft_workflow_json_then_load"
        reason = "The request explicitly points to direct workflow JSON authoring."
    elif edit_current:
        recommended_path = "edit_current_flow"
        reason = "The current canvas already has relevant structure, so editing the existing flow is easier than rebuilding."
    elif reusable_templates and not manual_only:
        recommended_path = "reuse_skill_workflow_json"
        reason = "A strong matched skill already has a reusable workflow template, which is likely the easiest path."
    elif manual_only:
        recommended_path = "manual_canvas_build"
        reason = "The request explicitly prefers manual canvas construction."
    elif node_count <= 0:
        recommended_path = "manual_canvas_build"
        reason = "No current flow is on canvas and no stronger reusable path was clearly requested."
    else:
        recommended_path = "edit_current_flow"
        reason = "Working from the current flow is likely the simplest incremental path."

    return {
        "recommended_path": recommended_path,
        "reason": reason,
        "available_paths": available_paths,
    }


def _canvas_node_name_lookup(canvas_context: dict[str, Any]) -> dict[str, str]:
    lookup = {}
    for item in list(dict(canvas_context or {}).get("nodes", []) or []):
        name = str(dict(item or {}).get("name", "") or "").strip()
        if name:
            lookup[name.casefold()] = name
    return lookup


def _resolve_canvas_node_name(requested_name: str, canvas_context: dict[str, Any]) -> str:
    requested = str(requested_name or "").strip()
    if not requested:
        return ""
    lookup = _canvas_node_name_lookup(canvas_context)
    exact = lookup.get(requested.casefold())
    if exact:
        return exact
    matches = [name for key, name in lookup.items() if requested.casefold() in key]
    if len(matches) == 1:
        return matches[0]
    return requested


def _extract_candidate_actions(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("actions", "action_list", "operations", "steps"):
        value = parsed.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    single = parsed.get("action")
    if isinstance(single, dict):
        return [single]
    return []


def _normalize_workspace_action_plan(
    parsed: dict[str, Any],
    canvas_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    canvas_context = dict(canvas_context or {})
    selected_count = int(canvas_context.get("selected_node_count", 0) or 0)
    normalized_actions = []
    dropped = []

    for item in _extract_candidate_actions(parsed):
        action_type = _normalize_workspace_action_type(item.get("type", "") or item.get("action", ""))
        if action_type not in CANVAS_ACTION_TYPES:
            dropped.append(f"Unsupported action type: {item.get('type', item.get('action', ''))}")
            continue

        normalized = {"type": action_type}
        if action_type == "create_node":
            node_type = _normalize_workspace_node_type(
                item.get("node_type", "") or item.get("kind", "") or item.get("node", "")
            )
            if node_type not in CANONICAL_NODE_TYPES:
                dropped.append(f"Unsupported node type for create_node: {node_type or 'missing'}")
                continue
            try:
                count = int(item.get("count", 1))
            except Exception:
                count = 1
            normalized["node_type"] = node_type
            normalized["count"] = max(1, min(5, count))
            for source_key, target_key in (
                ("name", "name"),
                ("node_name", "name"),
                ("variable_name", "variable_name"),
                ("variable", "variable_name"),
                ("value", "value"),
                ("default_value", "value"),
                ("text", "text"),
                ("caption", "text"),
                ("imports", "imports"),
                ("node_imports", "imports"),
                ("wrapper", "wrapper"),
                ("wrapper_code", "wrapper"),
                ("node_function_wrapper", "wrapper"),
                ("code", "code"),
            ):
                value = str(item.get(source_key, "") or "").strip() if target_key != "value" else str(item.get(source_key, "") or "")
                if value:
                    normalized[target_key] = value
            if _coerce_bool(item.get("value_display", False) or item.get("show_value", False)):
                normalized["value_display"] = True
            if _coerce_bool(item.get("is_path", False) or item.get("path", False)):
                normalized["is_path"] = True
        elif action_type == "update_node":
            node_name = _resolve_canvas_node_name(
                item.get("node_name", "") or item.get("name", "") or item.get("target_node", "") or item.get("target_name", ""),
                canvas_context,
            )
            if not node_name:
                dropped.append("update_node was missing node_name.")
                continue
            normalized["node_name"] = node_name
            node_type = _normalize_workspace_node_type(
                item.get("node_type", "") or item.get("kind", "") or item.get("node", "")
            )
            if node_type in CANONICAL_NODE_TYPES:
                normalized["node_type"] = node_type
            for source_key, target_key in (
                ("new_name", "new_name"),
                ("variable_name", "variable_name"),
                ("variable", "variable_name"),
                ("value", "value"),
                ("default_value", "value"),
                ("text", "text"),
                ("caption", "text"),
                ("imports", "imports"),
                ("node_imports", "imports"),
                ("wrapper", "wrapper"),
                ("wrapper_code", "wrapper"),
                ("node_function_wrapper", "wrapper"),
                ("code", "code"),
            ):
                value = str(item.get(source_key, "") or "").strip() if target_key != "value" else str(item.get(source_key, "") or "")
                if value:
                    normalized[target_key] = value
            if _coerce_bool(item.get("value_display", False) or item.get("show_value", False)):
                normalized["value_display"] = True
            if _coerce_bool(item.get("is_path", False) or item.get("path", False)):
                normalized["is_path"] = True
            editable_fields = {"new_name", "variable_name", "value", "text", "imports", "wrapper", "code", "value_display", "is_path"}
            if not any(field in normalized for field in editable_fields):
                dropped.append("update_node was missing editable fields.")
                continue
        elif action_type == "add_subflow":
            subflow_name = str(
                item.get("flow_name", "")
                or item.get("subflow_name", "")
                or item.get("name", "")
                or item.get("title", "")
                or ""
            ).strip()
            if subflow_name:
                normalized["flow_name"] = subflow_name
        elif action_type == "connect_nodes":
            source_node = _resolve_canvas_node_name(
                item.get("source_node", "") or item.get("from_node", "") or item.get("source", ""),
                canvas_context,
            )
            target_node = _resolve_canvas_node_name(
                item.get("target_node", "") or item.get("to_node", "") or item.get("target", ""),
                canvas_context,
            )
            if not source_node or not target_node:
                dropped.append("connect_nodes was missing source_node or target_node.")
                continue
            normalized["source_node"] = source_node
            normalized["target_node"] = target_node
            mapping = item.get("mapping")
            if isinstance(mapping, dict):
                normalized_mapping = {}
                for source_port, target_port in mapping.items():
                    source_port_text = str(source_port or "").strip()
                    target_port_text = str(target_port or "").strip()
                    if source_port_text and target_port_text:
                        normalized_mapping[source_port_text] = target_port_text
                if normalized_mapping:
                    normalized["mapping"] = normalized_mapping
            if "mapping" not in normalized:
                source_port = str(item.get("source_port", "") or item.get("from_port", "") or item.get("output_port", "") or "").strip()
                target_port = str(item.get("target_port", "") or item.get("to_port", "") or item.get("input_port", "") or "").strip()
                if source_port:
                    normalized["source_port"] = source_port
                if target_port:
                    normalized["target_port"] = target_port
        elif action_type == "rename_selected_node":
            new_name = str(item.get("new_name", "") or item.get("name", "") or item.get("target_name", "") or "").strip()
            if not new_name:
                dropped.append("rename_selected_node was missing new_name.")
                continue
            normalized["new_name"] = new_name
            if selected_count != 1:
                dropped.append("rename_selected_node requires exactly one selected node.")
                continue
        elif action_type == "update_selected_text_node":
            text = str(item.get("text", "") or item.get("caption", "") or item.get("value", "") or "")
            if not text.strip():
                dropped.append("update_selected_text_node was missing text.")
                continue
            normalized["text"] = text
            if selected_count != 1:
                dropped.append("update_selected_text_node requires exactly one selected node.")
                continue
        elif action_type == "delete_selected_nodes":
            if selected_count <= 0:
                dropped.append("delete_selected_nodes requires at least one selected node.")
                continue
        elif action_type == "load_workflow_json":
            workflow_path = str(
                item.get("workflow_path", "")
                or item.get("path", "")
                or item.get("workflow_json_path", "")
                or ""
            ).strip()
            workflow_content = (
                item.get("workflow_content")
                if isinstance(item.get("workflow_content"), dict)
                else item.get("workflow_json")
                if isinstance(item.get("workflow_json"), dict)
                else item.get("content")
                if isinstance(item.get("content"), dict)
                else None
            )
            if not workflow_path and not isinstance(workflow_content, dict):
                dropped.append("load_workflow_json requires workflow_path or workflow_content.")
                continue
            if workflow_path:
                normalized["workflow_path"] = workflow_path
            if isinstance(workflow_content, dict):
                normalized["workflow_content"] = workflow_content
            source_skill_id = str(item.get("source_skill_id", "") or item.get("skill_id", "") or "").strip()
            if source_skill_id:
                normalized["source_skill_id"] = source_skill_id

        normalized_actions.append(normalized)

    return {
        "reply": str(parsed.get("reply", "") or "").strip(),
        "planning_path": str(parsed.get("planning_path", "") or parsed.get("build_path", "") or "").strip(),
        "path_reason": str(parsed.get("path_reason", "") or parsed.get("build_path_reason", "") or "").strip(),
        "actions": normalized_actions[:5],
        "dropped_actions": dropped[:10],
    }


def _repair_workspace_action_plan(
    client: OpenAI,
    model_name: str,
    user_prompt: str,
    canvas_context: dict[str, Any],
    task_match_result: dict[str, Any],
    skill_execution_recipes: dict[str, Any],
    conversation: list[dict[str, Any]],
    initial_content: str,
    dropped_actions: list[str],
) -> dict[str, Any]:
    repair_prompt = (
        "You are repairing a QuESt Workspace canvas action plan. "
        "The first draft was semantically close but did not normalize into executable canonical actions. "
        "Convert the user's request into the exact supported schema. "
        "Use task_analysis.flow_description and task_analysis.notes as authoritative evidence about the current flow state. "
        "If analysis indicates a partially built or incomplete flow, prefer repairing and completing the existing flow instead of rebuilding it from scratch unless the user explicitly asked for a rebuild. "
        "If skill_execution_recipes contains strong matched skills, repair the plan toward those recipes instead of falling back to generic blank nodes. "
        "Use build_path_guidance to choose the easiest viable build path before repairing the plan. "
        "Use only these action types: create_node, update_node, add_subflow, connect_nodes, rename_selected_node, update_selected_text_node, delete_selected_nodes, load_workflow_json. "
        "Use only these create_node node types: data, py, text. "
        "If the request is clearly a canvas edit, return at least one action. "
        "Return valid JSON only with shape {\"reply\": string, \"planning_path\": string, \"path_reason\": string, \"actions\": [ ... ]}."
    )
    repair_payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "canvas_context": dict(canvas_context or {}),
        "task_analysis": dict(task_match_result or {}),
        "skill_execution_recipes": dict(skill_execution_recipes or {}),
        "build_path_guidance": _build_path_guidance(
            user_prompt,
            canvas_context=canvas_context,
            task_match_result=task_match_result,
            skill_execution_recipes=skill_execution_recipes,
        ),
        "recent_conversation": list(conversation or []),
        "initial_plan_raw": str(initial_content or ""),
        "normalization_failures": list(dropped_actions or []),
    }
    response = client.chat.completions.create(
        model=model_name,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": repair_prompt},
            {"role": "user", "content": json.dumps(repair_payload, ensure_ascii=True, indent=2)},
        ],
    )
    content = str(response.choices[0].message.content or "").strip() if response.choices else ""
    if not content:
        return {"reply": "", "actions": [], "dropped_actions": ["Repair pass returned no content."]}
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"reply": "", "actions": [], "dropped_actions": ["Repair pass returned invalid JSON."]}
    return _normalize_workspace_action_plan(parsed, canvas_context=canvas_context)


def run_workspace_action_plan(
    user_prompt: str,
    canvas_context: dict[str, Any] | None = None,
    task_match_result: dict[str, Any] | None = None,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    attached_workflow_jsons: list[dict[str, Any]] | None = None,
    workspace_relationship_context: dict[str, Any] | None = None,
    implicit_code_context: list[dict[str, Any]] | None = None,
    python_node_wrapper_rules: dict[str, Any] | None = None,
    skill_execution_recipes: dict[str, Any] | None = None,
    recent_messages: list[dict[str, Any]] | None = None,
    selected_model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    canvas_context = dict(canvas_context or {})
    task_match_result = dict(task_match_result or {})
    skill_execution_recipes = dict(skill_execution_recipes or {})
    conversation = _recent_conversation(recent_messages)
    build_path_guidance = _build_path_guidance(
        user_prompt,
        canvas_context=canvas_context,
        task_match_result=task_match_result,
        skill_execution_recipes=skill_execution_recipes,
    )

    system_prompt = (
        "You are QuESt Agent's canvas action planner. "
        "First infer the user's high-level canvas intent, then produce concrete canvas actions that can be executed immediately on the current QuESt Workspace canvas. "
        "Do not invent unsupported actions. "
        "If the request involves Python node wrappers, ports, or notebook code, treat python_node_wrapper_rules as authoritative over guesses. "
        "Treat task_analysis_guidance as the main execution guidance from prior analysis. "
        "Use task_analysis_guidance.flow_description and task_analysis_guidance.notes as authoritative current-state evidence about what already exists on canvas. "
        "If analysis shows an incomplete or partially built flow, prefer actions that complete, connect, initialize, or repair existing nodes instead of rebuilding the flow from scratch, unless the user explicitly asks to rebuild or replace it. "
        "Follow task_analysis_guidance.planning_directives strictly when they are present. "
        "Use top_skill_matches and top_tool_matches to shape how the plan should be implemented, but not to ignore the analyzed current flow. "
        "Use build_path_guidance to choose the easiest viable build path before producing actions. "
        "Prefer these paths in order when they fit: edit_current_flow, reuse_skill_workflow_json, manual_canvas_build, draft_workflow_json_then_load. "
        "If skill_execution_recipes contains strong matched skills, treat those recipes as concrete prior examples to adapt. "
        "Prefer reusing a matched skill's workflow strategy, step pattern, validation criteria, and saved workflow template structure over inventing a fresh plan from scratch when the task is similar. "
        "If a matched skill includes workflow_template metadata, you may use that saved flow as the structural blueprint for the plan, or load it directly with load_workflow_json before applying follow-up edits. "
        "If relevant saved skills were matched, let their intent and reasons shape the concrete canvas actions you choose. "
        "Supported action types are: create_node, update_node, add_subflow, connect_nodes, rename_selected_node, update_selected_text_node, delete_selected_nodes, load_workflow_json. "
        "For create_node, node_type must be one of data, py, text and count must be an integer from 1 to 5. "
        "For create_node you may include name, variable_name, value, value_display, is_path, text, imports, wrapper, and code when requested. "
        "For update_node, provide node_name for the existing node to edit, and include only the fields that should change such as new_name, variable_name, value, value_display, is_path, text, imports, wrapper, or code. Prefer update_node over create_node when build_path_guidance recommends editing the current flow. "
        "For add_subflow you may include flow_name or name for the new subflow tab. "
        "For connect_nodes, provide source_node and target_node, and include source_port/target_port or mapping when needed. "
        "For load_workflow_json, provide workflow_path when reusing a saved template, or workflow_content when drafting a full workflow JSON directly; you may also include source_skill_id. "
        "If the request is a canvas change, prefer returning at least one action instead of leaving actions empty. "
        "Return valid JSON only with this shape: "
        "{"
        "\"reply\": string, "
        "\"intent\": string, "
        "\"planning_path\": string, "
        "\"path_reason\": string, "
        "\"actions\": ["
        "{\"type\": string, \"node_type\": string, \"count\": number, \"name\": string, \"node_name\": string, \"flow_name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean, \"imports\": string, \"wrapper\": string, \"code\": string, \"new_name\": string, \"text\": string, \"source_node\": string, \"target_node\": string, \"source_port\": string, \"target_port\": string, \"mapping\": object, \"workflow_path\": string, \"workflow_content\": object, \"source_skill_id\": string}"
        "]"
        "}."
    )

    payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "canvas_context": canvas_context,
        "task_analysis": task_match_result,
        "task_analysis_guidance": _task_analysis_guidance(task_match_result),
        "pinned_context": list(pinned_context or []),
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])],
        "attached_workflow_jsons": list(attached_workflow_jsons or []),
        "workspace_relationship_context": dict(workspace_relationship_context or {}),
        "implicit_code_context": list(implicit_code_context or []),
        "python_node_wrapper_rules": dict(python_node_wrapper_rules or {}),
        "skill_execution_recipes": skill_execution_recipes,
        "build_path_guidance": build_path_guidance,
        "recent_conversation": conversation,
    }

    resolved_model_name = _resolve_model_name(selected_model)
    client = OpenAI(api_key=_resolve_api_key(api_key))
    response = client.chat.completions.create(
        model=resolved_model_name,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
        ],
    )

    content = str(response.choices[0].message.content or "").strip() if response.choices else ""
    parsed = _parse_json_response(
        content,
        "OpenAI returned an empty canvas action plan.",
        "OpenAI canvas action plan was not valid JSON.",
    )
    normalized_plan = _normalize_workspace_action_plan(parsed, canvas_context=canvas_context)
    if normalized_plan.get("actions"):
        normalized_plan["intent"] = str(parsed.get("intent", "") or "").strip()
        return normalized_plan

    if not _request_looks_actionable(user_prompt):
        normalized_plan["intent"] = str(parsed.get("intent", "") or "").strip()
        return normalized_plan

    repaired_plan = _repair_workspace_action_plan(
        client=client,
        model_name=resolved_model_name,
        user_prompt=user_prompt,
        canvas_context=canvas_context,
        task_match_result=task_match_result,
        skill_execution_recipes=skill_execution_recipes,
        conversation=conversation,
        initial_content=content,
        dropped_actions=list(normalized_plan.get("dropped_actions", []) or []),
    )
    if repaired_plan.get("actions"):
        if not repaired_plan.get("reply"):
            repaired_plan["reply"] = str(normalized_plan.get("reply", "") or "").strip()
        repaired_plan["intent"] = str(parsed.get("intent", "") or "").strip()
        return repaired_plan

    normalized_plan["intent"] = str(parsed.get("intent", "") or "").strip()
    return normalized_plan


def run_structured_task_match(
    task_description: str,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    attached_workflow_jsons: list[dict[str, Any]] | None = None,
    workspace_relationship_context: dict[str, Any] | None = None,
    implicit_code_context: list[dict[str, Any]] | None = None,
    python_node_wrapper_rules: dict[str, Any] | None = None,
    selected_model: str | None = None,
    quest_agent_root: str | Path | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    quest_agent_root = get_quest_agent_root(quest_agent_root)
    registry = write_active_tool_registry(quest_agent_root)
    skill_payload = load_skill_library(quest_agent_root)
    tools = list(registry.get("tools", []))
    skills = list(skill_payload.get("skills", []))

    client = OpenAI(api_key=_resolve_api_key(api_key))
    response = client.chat.completions.create(
        model=_resolve_model_name(selected_model),
        temperature=0,
        response_format={"type": "json_object"},
        messages=_build_messages(
            task_description=task_description,
            pinned_context=list(pinned_context or []),
            attached_files=list(attached_files or []),
            attached_workflow_jsons=list(attached_workflow_jsons or []),
            workspace_relationship_context=dict(workspace_relationship_context or {}),
            implicit_code_context=list(implicit_code_context or []),
            python_node_wrapper_rules=dict(python_node_wrapper_rules or {}),
            tools=tools,
            skills=skills,
        ),
    )
    content = str(response.choices[0].message.content or "").strip() if response.choices else ""
    parsed = _parse_json_response(
        content,
        "OpenAI returned an empty task match response.",
        "OpenAI task match response was not valid JSON.",
    )
    result = _normalize_match_result(parsed, tools, skills)
    result["tool_errors"] = list(skill_payload.get("errors", []))
    result["model"] = _resolve_model_name(selected_model)
    return result
