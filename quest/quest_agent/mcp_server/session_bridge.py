from __future__ import annotations

import uuid
import weakref
from typing import Any


_SESSIONS: dict[str, dict[str, Any]] = {}
_ACTIVE_SESSION_ID = ""


def _new_session_id() -> str:
    return f"workspace-{uuid.uuid4().hex[:12]}"


def register_workspace_session(
    owner: Any,
    session_id: str | None = None,
    workflow_getter: str = "_get_quest_agent_target_workflow",
    metadata: dict[str, Any] | None = None,
) -> str:
    global _ACTIVE_SESSION_ID
    resolved_id = str(session_id or "").strip() or _new_session_id()
    _SESSIONS[resolved_id] = {
        "owner": weakref.ref(owner),
        "workflow_getter": str(workflow_getter or "").strip(),
        "metadata": dict(metadata or {}),
    }
    _ACTIVE_SESSION_ID = resolved_id
    return resolved_id


def unregister_workspace_session(session_id: str | None = None) -> bool:
    global _ACTIVE_SESSION_ID
    resolved_id = str(session_id or _ACTIVE_SESSION_ID or "").strip()
    if not resolved_id:
        return False
    removed = _SESSIONS.pop(resolved_id, None) is not None
    if _ACTIVE_SESSION_ID == resolved_id:
        _ACTIVE_SESSION_ID = next(iter(_SESSIONS.keys()), "")
    return removed


def set_active_workspace_session(session_id: str | None = None) -> bool:
    global _ACTIVE_SESSION_ID
    resolved_id = str(session_id or "").strip()
    if not resolved_id or resolved_id not in _SESSIONS:
        return False
    _ACTIVE_SESSION_ID = resolved_id
    return True


def get_workspace_session_status(session_id: str | None = None) -> dict[str, Any]:
    resolved_id = str(session_id or _ACTIVE_SESSION_ID or "").strip()
    sessions = []
    stale_ids = []
    for current_id, record in list(_SESSIONS.items()):
        owner_ref = record.get("owner")
        owner = owner_ref() if callable(owner_ref) else None
        if owner is None:
            stale_ids.append(current_id)
            continue
        sessions.append(
            {
                "session_id": current_id,
                "active": current_id == _ACTIVE_SESSION_ID,
                "metadata": dict(record.get("metadata", {}) or {}),
            }
        )
    for stale_id in stale_ids:
        _SESSIONS.pop(stale_id, None)
    return {
        "available": bool(sessions),
        "active_session_id": resolved_id if resolved_id in _SESSIONS else _ACTIVE_SESSION_ID,
        "sessions": sessions,
        "source": "quest_mcp_workspace_session_bridge",
    }


def get_active_workspace(session_id: str | None = None) -> Any:
    resolved_id = str(session_id or _ACTIVE_SESSION_ID or "").strip()
    record = _SESSIONS.get(resolved_id)
    if not record:
        return None
    owner_ref = record.get("owner")
    owner = owner_ref() if callable(owner_ref) else None
    if owner is None:
        unregister_workspace_session(resolved_id)
        return None
    getter_name = str(record.get("workflow_getter", "") or "").strip()
    if getter_name and hasattr(owner, getter_name):
        try:
            return getattr(owner, getter_name)()
        except Exception:
            return None
    return owner


def execute_active_workspace_operation_plan(
    operation_plan: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> list[str]:
    workflow = get_active_workspace(session_id)
    if workflow is None:
        plan = operation_plan if isinstance(operation_plan, dict) else {}
        plan.setdefault("execution_notes", [])
        plan["execution_notes"].append("No active Workspace session is registered with the MCP session bridge.")
        return []
    from .tools_skills_manager import execute_workspace_operation_plan

    return execute_workspace_operation_plan(workflow, operation_plan)
