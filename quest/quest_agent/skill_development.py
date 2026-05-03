import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .llm_matcher import _chat_completion_content
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
) -> dict[str, Any]:
    skill_type = str(payload.get("skill_type", "") or "").strip()
    if skill_type not in {"general_python", "quest_tool_specific"}:
        skill_type = "quest_tool_specific"

    title = str(payload.get("title", "") or "").strip() or "QuESt Skill"
    summary = str(payload.get("summary", "") or "").strip() or "Reusable QuESt workflow skill."
    skill_level = str(payload.get("skill_level", "Competent") or "").strip() or "Competent"
    if skill_level not in {"Novice", "Advanced Beginner", "Competent", "Proficient", "Expert"}:
        skill_level = "Competent"
    tags = [str(tag).strip() for tag in list(payload.get("tags", []) or []) if str(tag).strip()]

    suggested_tools = [str(tool_id).strip() for tool_id in list(payload.get("recommended_tools", []) or []) if str(tool_id).strip()]
    recommended_tools = [tool_id for tool_id in suggested_tools if tool_id in active_tool_ids]
    if not recommended_tools:
        recommended_tools = [
            str(item.get("tool_id", "") or "").strip()
            for item in list(task_match_result.get("tool_matches", []) or [])
            if str(item.get("tool_id", "") or "").strip() in active_tool_ids
        ][:5]

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

    workflow_strategy = str(payload.get("workflow_strategy", "") or "").strip() or "recorded_workflow_replay"
    step_summary = [str(step).strip() for step in list(payload.get("step_summary", []) or []) if str(step).strip()]
    if not step_summary:
        step_summary = ["Replay the recorded workspace actions to rebuild the workflow."]

    expected_inputs = []
    for item in list(payload.get("expected_inputs", []) or []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "") or "").strip()
        if not name:
            continue
        expected_inputs.append({
            "name": name,
            "type": str(item.get("type", "") or "").strip() or "file",
            "description": str(item.get("description", "") or "").strip(),
        })

    required_file_types = [str(item).strip() for item in list(payload.get("required_file_types", []) or []) if str(item).strip()]
    limitations = [str(item).strip() for item in list(payload.get("limitations", []) or []) if str(item).strip()]
    data_preparation_notes = [str(item).strip() for item in list(payload.get("data_preparation_notes", []) or []) if str(item).strip()]
    validation_criteria = [str(item).strip() for item in list(payload.get("validation_criteria", []) or []) if str(item).strip()]
    pinned_context_summary = str(payload.get("pinned_context_summary", "") or "").strip()

    return {
        "skill_type": skill_type,
        "skill_level": skill_level,
        "title": title,
        "summary": summary,
        "tags": tags,
        "recommended_tools": recommended_tools,
        "required_tools": required_tools,
        "workflow_strategy": workflow_strategy,
        "step_summary": step_summary,
        "expected_inputs": expected_inputs,
        "required_file_types": required_file_types,
        "limitations": limitations,
        "data_preparation_notes": data_preparation_notes,
        "validation_criteria": validation_criteria,
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
) -> list[dict[str, str]]:
    system_prompt = (
        "You are QuESt Agent's skill developer. "
        "Convert a recorded set of QuESt Workspace actions plus project and flow context into a reusable QuESt skill specification. "
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
        "\"summary\": string, "
        "\"tags\": [string], "
        "\"recommended_tools\": [string], "
        "\"required_tools\": [string], "
        "\"workflow_strategy\": string, "
        "\"step_summary\": [string], "
        "\"pinned_context_summary\": string, "
        "\"required_file_types\": [string], "
        "\"expected_inputs\": [{\"name\": string, \"type\": string, \"description\": string}], "
        "\"data_preparation_notes\": [string], "
        "\"validation_criteria\": [string], "
        "\"limitations\": [string]"
        "}."
    )
    payload = {
        "project_description": str(project_description or ""),
        "flow_description": str(flow_description or ""),
        "task_match_result": dict(task_match_result or {}),
        "current_flow_json_data": dict(current_flow_json_data or {}),
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
    inferred_specific_tools = _infer_specific_tools(
        task_match_result=task_match_result,
        current_flow_json_data=current_flow_json_data,
        action_records=action_records,
        project_description=project_description,
        flow_description=flow_description,
        active_tools=active_tools,
    )

    content, _ = _chat_completion_content(
        _build_skill_messages(
            project_description=project_description,
            flow_description=flow_description,
            task_match_result=task_match_result,
            action_records=action_records,
            pinned_context=pinned_context,
            attached_files=attached_files,
            active_tools=active_tools,
            current_flow_json_data=current_flow_json_data,
            inferred_specific_tools=inferred_specific_tools,
        ),
        selected_model=selected_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    if not content:
        raise RuntimeError("OpenAI returned an empty skill development response.")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI skill development response was not valid JSON.") from exc

    normalized = _normalize_skill_payload(parsed, active_tool_ids, task_match_result, inferred_specific_tools)

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

    saved_attachments = []
    current_flow_name = str(current_flow_json_data.get("flow_name", "") or "").strip()
    for path in attached_files:
        source = Path(str(path))
        if not source.exists() or not source.is_file():
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

    action_record_path = artifacts_dir / "action_record.json"
    with action_record_path.open("w", encoding="utf-8") as handle:
        json.dump(action_records, handle, indent=2)

    created_at = _iso_now()
    project_description = str(project_description or "").strip()
    flow_description = str(flow_description or "").strip()
    pinned_context_summary = normalized["pinned_context_summary"] or "\n".join(pinned_context[:4]).strip()

    skill_json = {
        "schema_version": "1.0",
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
        "plan": {
            "workflow_strategy": normalized["workflow_strategy"],
            "step_summary": normalized["step_summary"],
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
