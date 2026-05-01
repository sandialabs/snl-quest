import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_SCHEMA_VERSION = "1.0"
SKILL_TYPES = {"general_python", "quest_tool_specific"}
SKILL_STATUSES = {"draft", "validated", "deprecated"}
VALIDATION_STATUSES = {"draft", "passed", "failed"}
WORKSPACE_ONLY_TOOL_IDS = {"workspace"}
SKILL_LEVELS = {"Novice", "Advanced Beginner", "Competent", "Proficient", "Expert"}


@dataclass
class SkillLoadError:
    folder_path: str
    error: str


@dataclass
class SkillRecord:
    skill_id: str
    slug: str
    skill_type: str
    skill_level: str
    title: str
    summary: str
    status: str
    tags: list[str]
    recommended_tools: list[str]
    required_tools: list[str]
    folder_path: str
    skill_json_path: str
    skill_md_path: str
    workflow_json_path: str
    attachments: list[str]
    action_record_path: str
    action_record_count: int
    validation_status: str
    raw_data: dict[str, Any]

    def to_manifest_entry(self, manifest_root: str | Path | None = None) -> dict[str, Any]:
        manifest_root = Path(manifest_root) if manifest_root is not None else None

        def _rel(path_value: str) -> str:
            if not path_value:
                return ""
            path_obj = Path(path_value)
            if manifest_root is None:
                return path_obj.as_posix()
            try:
                return path_obj.relative_to(manifest_root).as_posix()
            except ValueError:
                return path_obj.as_posix()

        return {
            "skill_id": self.skill_id,
            "slug": self.slug,
            "skill_type": self.skill_type,
            "skill_level": self.skill_level,
            "title": self.title,
            "summary": self.summary,
            "status": self.status,
            "tags": list(self.tags),
            "recommended_tools": list(self.recommended_tools),
            "required_tools": list(self.required_tools),
            "folder_path": _rel(self.folder_path),
            "skill_json_path": _rel(self.skill_json_path),
            "skill_md_path": _rel(self.skill_md_path),
            "workflow_json_path": _rel(self.workflow_json_path),
            "attachments": [_rel(path) for path in self.attachments],
            "action_record_path": _rel(self.action_record_path),
            "action_record_count": self.action_record_count,
            "validation_status": self.validation_status,
        }


def get_quest_agent_root(package_root: str | Path | None = None) -> Path:
    if package_root is None:
        package_root = Path(__file__).resolve().parents[1]
    package_root = Path(package_root)
    if package_root.name == "quest_agent":
        return package_root
    return package_root / "quest_agent"


def get_skill_library_root(root_path: str | Path | None = None) -> Path:
    if root_path is None:
        root_path = get_quest_agent_root()
    return Path(root_path) / "skills"


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{key}' must be a non-empty string.")
    return value.strip()


def _require_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"Field '{key}' must be a list.")
    return value


def _validate_relative_path(skill_folder: Path, raw_relative_path: str, field_name: str) -> str:
    if not isinstance(raw_relative_path, str):
        raise ValueError(f"Field '{field_name}' must be a string path.")
    relative_path = raw_relative_path.strip().replace("\\", "/")
    if not relative_path:
        return ""
    candidate = (skill_folder / relative_path).resolve()
    try:
        candidate.relative_to(skill_folder.resolve())
    except ValueError as exc:
        raise ValueError(f"Field '{field_name}' points outside the skill folder.") from exc
    return relative_path


def _effective_skill_type(
    declared_skill_type: str,
    recommended_tools: list[str] | None = None,
    required_tools: list[str] | None = None,
) -> str:
    recommended_tools = [str(tool_id or "").strip() for tool_id in list(recommended_tools or []) if str(tool_id or "").strip()]
    required_tools = [str(tool_id or "").strip() for tool_id in list(required_tools or []) if str(tool_id or "").strip()]
    tool_set = set(recommended_tools + required_tools)
    if tool_set and tool_set.issubset(WORKSPACE_ONLY_TOOL_IDS):
        return "general_python"
    return str(declared_skill_type or "").strip()


def validate_skill_json(data: dict[str, Any], skill_folder: str | Path, expected_type: str) -> dict[str, Any]:
    if expected_type not in SKILL_TYPES:
        raise ValueError(f"Unsupported expected skill type '{expected_type}'.")

    skill_folder = Path(skill_folder)
    if not isinstance(data, dict):
        raise ValueError("Skill JSON must be an object.")

    schema_version = _require_string(data, "schema_version")
    if schema_version != SKILL_SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version '{schema_version}'.")

    skill_id = _require_string(data, "skill_id")
    slug = _require_string(data, "slug")
    title = _require_string(data, "title")
    summary = _require_string(data, "summary")
    skill_type = _require_string(data, "skill_type")
    skill_level = str(data.get("skill_level", "Competent") or "").strip()
    status = _require_string(data, "status")

    if slug != skill_folder.name:
        raise ValueError("Field 'slug' must match the skill folder name.")
    if skill_type not in SKILL_TYPES:
        raise ValueError(f"Invalid skill_type '{skill_type}'.")
    if skill_type != expected_type:
        raise ValueError("Field 'skill_type' must match the parent skill category folder.")
    if skill_level not in SKILL_LEVELS:
        raise ValueError(f"Invalid skill_level '{skill_level}'.")
    if status not in SKILL_STATUSES:
        raise ValueError(f"Invalid status '{status}'.")

    version = data.get("version", None)
    if not isinstance(version, int) or version < 1:
        raise ValueError("Field 'version' must be an integer >= 1.")

    for stamp_key in ("created_at", "updated_at"):
        _require_string(data, stamp_key)

    task = data.get("task", {})
    if not isinstance(task, dict):
        raise ValueError("Field 'task' must be an object.")
    _require_string(task, "description")
    _require_string(task, "pinned_context_summary")
    _require_string(task, "task_fingerprint")
    _require_string(task, "context_fingerprint")

    classification = data.get("classification", {})
    if not isinstance(classification, dict):
        raise ValueError("Field 'classification' must be an object.")
    tags = _require_list(classification, "tags")

    tools = data.get("tools", {})
    if not isinstance(tools, dict):
        raise ValueError("Field 'tools' must be an object.")
    recommended_tools = _require_list(tools, "recommended")
    required_tools = _require_list(tools, "required")
    optional_tools = _require_list(tools, "optional")

    files = data.get("files", {})
    if not isinstance(files, dict):
        raise ValueError("Field 'files' must be an object.")
    attachments = _require_list(files, "attachments")
    workflow_json = files.get("workflow_json", "")
    if workflow_json is None:
        workflow_json = ""

    normalized_attachments: list[str] = []
    for index, attachment in enumerate(attachments):
        normalized_attachments.append(
            _validate_relative_path(skill_folder, attachment, f"files.attachments[{index}]")
        )

    normalized_workflow_json = _validate_relative_path(skill_folder, str(workflow_json), "files.workflow_json")
    if skill_type == "quest_tool_specific" and status == "validated" and not normalized_workflow_json:
        raise ValueError("Validated QuESt-tool-specific skills must include files.workflow_json.")

    if normalized_workflow_json and not (skill_folder / normalized_workflow_json).exists():
        raise ValueError("Referenced workflow JSON file does not exist.")

    for attachment in normalized_attachments:
        if attachment and not (skill_folder / attachment).exists():
            raise ValueError(f"Referenced attachment does not exist: {attachment}")

    action_record = data.get("action_record", None)
    normalized_action_record_path = ""
    normalized_action_records: list[dict[str, Any]] = []
    if action_record is not None:
        if not isinstance(action_record, dict):
            raise ValueError("Field 'action_record' must be an object.")
        action_record_path = action_record.get("path", "")
        if action_record_path is None:
            action_record_path = ""
        normalized_action_record_path = _validate_relative_path(skill_folder, str(action_record_path), "action_record.path")
        action_records = action_record.get("records", [])
        if not isinstance(action_records, list):
            raise ValueError("Field 'action_record.records' must be a list.")
        for index, entry in enumerate(action_records):
            if not isinstance(entry, dict):
                raise ValueError(f"Field 'action_record.records[{index}]' must be an object.")
        normalized_action_records = action_records
        if normalized_action_record_path and not (skill_folder / normalized_action_record_path).exists():
            raise ValueError("Referenced action record file does not exist.")

    plan = data.get("plan", {})
    if not isinstance(plan, dict):
        raise ValueError("Field 'plan' must be an object.")
    _require_string(plan, "workflow_strategy")
    _require_list(plan, "step_summary")

    validation = data.get("validation", {})
    if not isinstance(validation, dict):
        raise ValueError("Field 'validation' must be an object.")
    validation_status = _require_string(validation, "status")
    if validation_status not in VALIDATION_STATUSES:
        raise ValueError(f"Invalid validation.status '{validation_status}'.")
    _require_list(validation, "criteria")
    if status == "validated":
        _require_string(validation, "last_validated_at")

    limitations = data.get("limitations", [])
    if not isinstance(limitations, list):
        raise ValueError("Field 'limitations' must be a list.")

    normalized = dict(data)
    normalized["skill_level"] = skill_level
    normalized["task"] = dict(task)
    normalized["classification"] = dict(classification)
    normalized["tools"] = dict(tools)
    normalized["files"] = dict(files)
    normalized["plan"] = dict(plan)
    normalized["validation"] = dict(validation)
    normalized["classification"]["tags"] = tags
    normalized["tools"]["recommended"] = recommended_tools
    normalized["tools"]["required"] = required_tools
    normalized["tools"]["optional"] = optional_tools
    normalized["files"]["attachments"] = normalized_attachments
    normalized["files"]["workflow_json"] = normalized_workflow_json
    if action_record is not None:
        normalized["action_record"] = {
            "path": normalized_action_record_path,
            "records": normalized_action_records,
        }
    normalized["limitations"] = limitations
    return normalized


def load_skill_folder(skill_folder: str | Path, expected_type: str) -> SkillRecord:
    skill_folder = Path(skill_folder)
    skill_json_path = skill_folder / "skill.json"
    skill_md_path = skill_folder / "SKILL.md"

    if not skill_json_path.exists():
        raise ValueError("Missing skill.json")
    if not skill_md_path.exists():
        raise ValueError("Missing SKILL.md")

    with skill_json_path.open("r", encoding="utf-8") as handle:
        raw_data = json.load(handle)

    normalized = validate_skill_json(raw_data, skill_folder, expected_type)
    workflow_json_relative = str(normalized["files"].get("workflow_json", "") or "")
    attachments_relative = [str(path) for path in normalized["files"].get("attachments", [])]
    action_record_section = normalized.get("action_record", {}) if isinstance(normalized.get("action_record", {}), dict) else {}
    action_record_relative = str(action_record_section.get("path", "") or "")
    action_record_entries = list(action_record_section.get("records", []) or [])

    return SkillRecord(
        skill_id=str(normalized["skill_id"]),
        slug=str(normalized["slug"]),
        skill_type=_effective_skill_type(
            str(normalized["skill_type"]),
            list(normalized["tools"].get("recommended", [])),
            list(normalized["tools"].get("required", [])),
        ),
        skill_level=str(normalized.get("skill_level", "Competent") or "Competent"),
        title=str(normalized["title"]),
        summary=str(normalized["summary"]),
        status=str(normalized["status"]),
        tags=list(normalized["classification"].get("tags", [])),
        recommended_tools=list(normalized["tools"].get("recommended", [])),
        required_tools=list(normalized["tools"].get("required", [])),
        folder_path=skill_folder.as_posix(),
        skill_json_path=skill_json_path.as_posix(),
        skill_md_path=skill_md_path.as_posix(),
        workflow_json_path=(skill_folder / workflow_json_relative).as_posix() if workflow_json_relative else "",
        attachments=[(skill_folder / rel_path).as_posix() for rel_path in attachments_relative],
        action_record_path=(skill_folder / action_record_relative).as_posix() if action_record_relative else "",
        action_record_count=len(action_record_entries),
        validation_status=str(normalized["validation"].get("status", "draft")),
        raw_data=normalized,
    )


def load_skill_library(root_path: str | Path | None = None) -> dict[str, Any]:
    skills_root = get_skill_library_root(root_path)
    skills: list[SkillRecord] = []
    errors: list[SkillLoadError] = []

    for skill_type in sorted(SKILL_TYPES):
        category_path = skills_root / skill_type
        if not category_path.exists():
            continue
        for skill_folder in sorted(path for path in category_path.iterdir() if path.is_dir()):
            try:
                skills.append(load_skill_folder(skill_folder, skill_type))
            except Exception as exc:
                errors.append(SkillLoadError(folder_path=skill_folder.as_posix(), error=str(exc)))

    return {"skills": skills, "errors": errors}


def build_skills_manifest(
    root_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    quest_agent_root = get_quest_agent_root(root_path)
    skills_root = get_skill_library_root(root_path)
    registry_root = quest_agent_root / "registry"
    registry_root.mkdir(parents=True, exist_ok=True)

    if manifest_path is None:
        manifest_path = registry_root / "skills_manifest.json"
    manifest_path = Path(manifest_path)

    loaded = load_skill_library(quest_agent_root)
    manifest = {
        "schema_version": SKILL_SCHEMA_VERSION,
        "updated_at": _iso_now(),
        "root_path": "skills",
        "skills": [record.to_manifest_entry(quest_agent_root) for record in loaded["skills"]],
        "errors": [asdict(error) for error in loaded["errors"]],
    }

    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    return manifest
