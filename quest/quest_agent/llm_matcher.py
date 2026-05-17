import ctypes
import contextvars
import copy
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .skill_library import SkillRecord, get_quest_agent_root, load_skill_library
from .tool_registry import write_active_tool_registry


MODEL_NAME_MAP = {
    "GPT-5.5": "gpt-5.5",
    "GPT-5.4": "gpt-5.4",
    "GPT-5.4 Mini": "gpt-5.4-mini",
    "GPT-5.2 Codex": "gpt-5.2-codex",
    "GPT-4.1": "gpt-4.1",
    "o4-mini": "o4-mini",
    "Claude Opus 4.7": "claude-opus-4-7",
    "Claude Sonnet 4.6": "claude-sonnet-4-6",
    "Claude Haiku 4.5": "claude-haiku-4-5-20251001",
    "Claude Sonnet 4": "claude-sonnet-4-6",
    "Claude Haiku 3.5": "claude-haiku-4-5-20251001",
    "GPT-OSS 120B": "ollama:gpt-oss:120b",
    "GPT OSS 120B": "ollama:gpt-oss:120b",
    "Gemma 4 E2B": "ollama:gemma4:e2b",
    "Gemma 4 E4B": "ollama:gemma4:e4b",
    "Gemma 4 26B": "ollama:gemma4:26b",
    "Gemma 4 31B": "ollama:gemma4:31b",
}
MODEL_NAME_LABEL_MAP = {value: key for key, value in MODEL_NAME_MAP.items()}

OLLAMA_MODEL_PREFIX = "ollama:"
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_TIMEOUT_SECONDS = 600
DEFAULT_ANTHROPIC_TIMEOUT_SECONDS = 600
ANTHROPIC_MODEL_MAX_TOKENS = {
    "claude-opus-4-7": 128000,
    "claude-sonnet-4-6": 64000,
    "claude-haiku-4-5-20251001": 64000,
}
ANTHROPIC_MODELS_WITHOUT_TEMPERATURE = {
    "claude-opus-4-7",
}
OPENAI_MODELS_WITH_DEFAULT_TEMPERATURE_ONLY = {
    "gpt-5.5",
}
MODEL_PRICING_USD_PER_MILLION_TOKENS = {
    "gpt-5.5": {"input": 5.00, "cached_input": 0.50, "output": 30.00},
    "gpt-5.4": {"input": 2.50, "cached_input": 0.25, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
    "claude-opus-4-7": {"input": 5.00, "cached_input": 0.50, "output": 25.00},
    "claude-sonnet-4-6": {"input": 3.00, "cached_input": 0.30, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "cached_input": 0.10, "output": 5.00},
}
DEFAULT_OLLAMA_CONTEXT_TOKENS = 2048
OLLAMA_MODEL_CONTEXT_TOKENS = {
    "gpt-oss:120b": 8192,
    "gemma4:e2b": 2048,
    "gemma4:e4b": 2048,
    "gemma4:26b": 1024,
    "gemma4:31b": 1024,
}
OLLAMA_LARGE_MODEL_PROMPT_CHAR_LIMIT = 18000
OLLAMA_HEAVY_MODEL_FALLBACK_CHAR_LIMIT = 6000
FAST_LOCAL_PROMPT_CHAR_LIMIT = 14000
FAST_LOCAL_MAX_PINNED_CONTEXT = 1
FAST_LOCAL_MAX_ATTACHED_FILES = 3
FAST_LOCAL_MAX_WORKFLOW_CONTEXTS = 1
FAST_LOCAL_MAX_RECENT_MESSAGES = 2
FAST_LOCAL_MAX_RECIPE_COUNT = 2
FAST_LOCAL_MAX_SKILL_MATCHES = 2
FAST_LOCAL_MAX_TOOL_MATCHES = 3
FAST_LOCAL_TASK_MATCH_SKILL_LIMIT = 8
MATCH_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "these", "those", "into", "onto",
    "flow", "flows", "workflow", "workflows", "node", "nodes", "using", "uses", "used",
    "current", "existing", "already", "contains", "contain", "present", "master", "subflow",
    "canvas", "task", "build", "create", "make", "edit", "update", "fix", "repair", "complete",
    "analysis", "analyze", "is", "are", "was", "were", "be", "been", "being", "it", "its",
    "a", "an", "of", "to", "in", "on", "by", "or", "as", "at", "data", "tool", "tools",
    "json", "file", "files", "input", "inputs", "output", "outputs",
}
OLLAMA_MODEL_MIN_AVAILABLE_MEMORY_GB = {
    "gemma4:26b": 10.0,
    "gemma4:31b": 12.0,
}
OLLAMA_MODEL_FALLBACKS = {
    "gemma4:26b": "ollama:gemma4:e4b",
    "gemma4:31b": "ollama:gemma4:e4b",
}

CANVAS_ACTION_TYPES = {
    "create_node",
    "update_node",
    "add_subflow",
    "connect_nodes",
    "rename_selected_node",
    "update_selected_text_node",
    "delete_node",
    "delete_selected_nodes",
    "load_workflow_json",
    "validate_flow",
}

CANONICAL_NODE_TYPES = {"data", "py", "text"}
_LLM_USAGE_RECORDS = contextvars.ContextVar("quest_agent_llm_usage_records", default=None)


def reset_llm_usage_tracking() -> None:
    _LLM_USAGE_RECORDS.set([])


def _extract_attr_or_key(value: Any, name: str, default: Any = 0) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _coerce_token_count(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except Exception:
        return 0


def _estimate_llm_cost_usd(model_name: str, input_tokens: int, output_tokens: int, cached_input_tokens: int = 0) -> float | None:
    resolved_name = _resolve_model_name(model_name)
    if _is_ollama_model(resolved_name):
        return 0.0
    pricing = MODEL_PRICING_USD_PER_MILLION_TOKENS.get(resolved_name)
    if not pricing:
        return None
    cached_tokens = min(_coerce_token_count(cached_input_tokens), _coerce_token_count(input_tokens))
    regular_input_tokens = max(0, _coerce_token_count(input_tokens) - cached_tokens)
    output_tokens = _coerce_token_count(output_tokens)
    return (
        (regular_input_tokens * float(pricing.get("input", 0.0) or 0.0))
        + (cached_tokens * float(pricing.get("cached_input", pricing.get("input", 0.0)) or 0.0))
        + (output_tokens * float(pricing.get("output", 0.0) or 0.0))
    ) / 1_000_000.0


def _record_llm_usage(
    *,
    provider: str,
    model_name: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cached_input_tokens: int = 0,
) -> None:
    records = _LLM_USAGE_RECORDS.get()
    if records is None:
        return
    input_tokens = _coerce_token_count(input_tokens)
    output_tokens = _coerce_token_count(output_tokens)
    cached_input_tokens = _coerce_token_count(cached_input_tokens)
    records.append({
        "provider": str(provider or "").strip(),
        "model": _resolve_model_name(model_name),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_input_tokens": min(cached_input_tokens, input_tokens),
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost_usd": _estimate_llm_cost_usd(model_name, input_tokens, output_tokens, cached_input_tokens),
    })
    _LLM_USAGE_RECORDS.set(records)


def _format_usd(value: float | None) -> str:
    if value is None:
        return "unavailable"
    if value == 0:
        return "$0.00"
    if value < 1:
        return f"${value:.4f}"
    return f"${value:.2f}"


def get_llm_usage_summary() -> dict[str, Any]:
    records = list(_LLM_USAGE_RECORDS.get() or [])
    total_input_tokens = sum(_coerce_token_count(record.get("input_tokens")) for record in records)
    total_output_tokens = sum(_coerce_token_count(record.get("output_tokens")) for record in records)
    total_cached_input_tokens = sum(_coerce_token_count(record.get("cached_input_tokens")) for record in records)
    known_costs = [record.get("estimated_cost_usd") for record in records if record.get("estimated_cost_usd") is not None]
    total_cost = sum(float(value or 0.0) for value in known_costs) if len(known_costs) == len(records) else None
    models = []
    for record in records:
        label = _describe_model_label(record.get("model"))
        if label not in models:
            models.append(label)
    note = ""
    if records:
        cache_text = f", cached input {total_cached_input_tokens:,}" if total_cached_input_tokens else ""
        model_text = f", models: {', '.join(models)}" if len(models) > 1 else ""
        note = (
            f"Token usage: {len(records)} LLM call{'s' if len(records) != 1 else ''}; "
            f"input {total_input_tokens:,}{cache_text}; output {total_output_tokens:,}; "
            f"total {total_input_tokens + total_output_tokens:,}; estimated cost {_format_usd(total_cost)}{model_text}."
        )
    return {
        "records": records,
        "call_count": len(records),
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "cached_input_tokens": total_cached_input_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "estimated_cost_usd": total_cost,
        "usage_note": note,
    }


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


def _resolve_anthropic_api_key(explicit_api_key: str | None = None) -> str:
    if explicit_api_key and str(explicit_api_key).strip():
        return str(explicit_api_key).strip()
    env_key = str(os.environ.get("ANTHROPIC_API_KEY", "") or "").strip()
    if env_key:
        return env_key
    raise RuntimeError("Anthropic API key is not configured. Set ANTHROPIC_API_KEY before using Claude models.")


def _is_ollama_model(model_name: str | None) -> bool:
    return str(model_name or "").strip().startswith(OLLAMA_MODEL_PREFIX)


def _is_anthropic_model(model_name: str | None) -> bool:
    return str(model_name or "").strip().startswith("claude-")


def _resolve_ollama_model_tag(model_name: str) -> str:
    cleaned = str(model_name or "").strip()
    if cleaned.startswith(OLLAMA_MODEL_PREFIX):
        return cleaned[len(OLLAMA_MODEL_PREFIX):]
    return cleaned


def _resolve_ollama_host() -> str:
    host = str(os.environ.get("OLLAMA_HOST", "") or "").strip()
    return (host or DEFAULT_OLLAMA_HOST).rstrip("/")


def _resolve_ollama_timeout_seconds() -> float:
    raw_value = str(os.environ.get("OLLAMA_REQUEST_TIMEOUT_SECONDS", "") or "").strip()
    try:
        timeout_seconds = float(raw_value) if raw_value else float(DEFAULT_OLLAMA_TIMEOUT_SECONDS)
    except Exception:
        timeout_seconds = float(DEFAULT_OLLAMA_TIMEOUT_SECONDS)
    return max(30.0, timeout_seconds)


def _resolve_anthropic_timeout_seconds() -> float:
    raw_value = str(os.environ.get("ANTHROPIC_REQUEST_TIMEOUT_SECONDS", "") or "").strip()
    try:
        timeout_seconds = float(raw_value) if raw_value else float(DEFAULT_ANTHROPIC_TIMEOUT_SECONDS)
    except Exception:
        timeout_seconds = float(DEFAULT_ANTHROPIC_TIMEOUT_SECONDS)
    return max(30.0, timeout_seconds)


def _fast_local_mode_enabled(selected_model: str | None) -> bool:
    raw_value = str(os.environ.get("QUEST_AGENT_FAST_LOCAL_MODE", "1") or "").strip().casefold()
    if raw_value in {"0", "false", "no", "off"}:
        return False
    return _is_ollama_model(_resolve_model_name(selected_model))


def _resolve_fast_local_reasoning_model(selected_model: str | None) -> str | None:
    if not _fast_local_mode_enabled(selected_model):
        return selected_model
    resolved_model = _resolve_model_name(selected_model)
    model_tag = _resolve_ollama_model_tag(resolved_model)
    if model_tag == "gpt-oss:120b":
        return selected_model
    return "Gemma 4 E4B"


def _estimate_message_chars(messages: list[dict[str, Any]]) -> int:
    total = 0
    for message in list(messages or []):
        total += len(str(message.get("role", "") or ""))
        total += len(str(message.get("content", "") or ""))
    return total


def _get_available_physical_memory_gb() -> float | None:
    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        memory_status = MEMORYSTATUSEX()
        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status)):
            return None
        return float(memory_status.ullAvailPhys) / float(1024 ** 3)
    except Exception:
        return None


def _resolve_ollama_context_tokens(model_tag: str) -> int:
    override = str(os.environ.get("OLLAMA_CONTEXT_TOKENS", "") or "").strip()
    if override:
        try:
            return max(512, int(override))
        except Exception:
            pass
    return int(OLLAMA_MODEL_CONTEXT_TOKENS.get(model_tag, DEFAULT_OLLAMA_CONTEXT_TOKENS))


def _raise_if_ollama_request_is_unstable(model_tag: str, messages: list[dict[str, Any]]) -> None:
    prompt_chars = _estimate_message_chars(messages)
    if model_tag in {"gemma4:26b", "gemma4:31b"} and prompt_chars > OLLAMA_LARGE_MODEL_PROMPT_CHAR_LIMIT:
        raise RuntimeError(
            "The selected local Gemma model is likely to be unstable for this large QuESt prompt/context. "
            "Use Gemma 4 E4B/E2B, reduce attached context, or set OLLAMA_CONTEXT_TOKENS explicitly if you want to force it."
        )
    min_available_gb = OLLAMA_MODEL_MIN_AVAILABLE_MEMORY_GB.get(model_tag)
    available_gb = _get_available_physical_memory_gb()
    if min_available_gb is not None and available_gb is not None and available_gb < min_available_gb:
        raise RuntimeError(
            f"The selected local Gemma model needs more free system memory to run reliably right now "
            f"(available: {available_gb:.1f} GB, recommended free memory: at least {min_available_gb:.1f} GB). "
            "Close other memory-heavy apps or switch to Gemma 4 E4B/E2B."
        )


def _resolve_ollama_runtime_model_name(model_name: str, messages: list[dict[str, Any]]) -> str:
    model_tag = _resolve_ollama_model_tag(model_name)
    prompt_chars = _estimate_message_chars(messages)
    if model_tag in OLLAMA_MODEL_FALLBACKS:
        available_gb = _get_available_physical_memory_gb()
        min_available_gb = float(OLLAMA_MODEL_MIN_AVAILABLE_MEMORY_GB.get(model_tag, 0.0) or 0.0)
        if prompt_chars > OLLAMA_HEAVY_MODEL_FALLBACK_CHAR_LIMIT:
            return str(OLLAMA_MODEL_FALLBACKS[model_tag])
        if available_gb is not None and available_gb < (min_available_gb + 4.0):
            return str(OLLAMA_MODEL_FALLBACKS[model_tag])
    return model_name


def _describe_model_label(model_name: str | None) -> str:
    resolved_name = _resolve_model_name(model_name)
    if resolved_name in MODEL_NAME_LABEL_MAP:
        return str(MODEL_NAME_LABEL_MAP[resolved_name])
    if str(model_name or "").strip() in MODEL_NAME_MAP:
        return str(model_name).strip()
    if _is_ollama_model(resolved_name):
        model_tag = _resolve_ollama_model_tag(resolved_name)
        if model_tag in MODEL_NAME_LABEL_MAP:
            return str(MODEL_NAME_LABEL_MAP[model_tag])
        return model_tag
    return resolved_name


def _build_model_used_note(
    selected_model: str | None,
    selected_reasoning_model: str | None,
    resolved_model_name: str | None,
) -> str:
    requested_name = _resolve_model_name(selected_model)
    reasoning_name = _resolve_model_name(selected_reasoning_model)
    resolved_name = _resolve_model_name(resolved_model_name or selected_reasoning_model or selected_model)
    resolved_label = _describe_model_label(resolved_name)
    requested_label = _describe_model_label(requested_name)
    reasoning_label = _describe_model_label(reasoning_name)

    note_parts = []
    if requested_name != reasoning_name:
        note_parts.append(f"fast local mode; selected {requested_label}")
    if resolved_name != reasoning_name:
        note_parts.append(f"fallback from {reasoning_label} due to prompt/memory")
    if note_parts:
        return f"Model used: {resolved_label} ({'; '.join(note_parts)})."
    return f"Model used: {resolved_label}."


def _truncate_text(value: Any, limit: int) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _trim_recent_conversation_for_fast_local(recent_messages: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    trimmed = []
    for message in list(recent_messages or [])[-FAST_LOCAL_MAX_RECENT_MESSAGES:]:
        role = str(message.get("role", "") or "").strip().lower()
        content = str(message.get("content", "") or "").strip()
        if role in {"user", "assistant"} and content:
            trimmed.append({"role": role, "content": _truncate_text(content, 280)})
    return trimmed


def _trim_workflow_contexts_for_fast_local(attached_workflow_jsons: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    trimmed = []
    for entry in list(attached_workflow_jsons or [])[:FAST_LOCAL_MAX_WORKFLOW_CONTEXTS]:
        item = dict(entry or {})
        flow_names = [
            _truncate_text(flow_name, 80)
            for flow_name in list(item.get("flow_names", []) or [])[:4]
            if str(flow_name or "").strip()
        ]
        summary = {
            "source_name": _truncate_text(item.get("source_name", "") or item.get("path", ""), 120),
            "flow_names": flow_names,
            "summary": _truncate_text(
                item.get("summary", "")
                or item.get("description", "")
                or item.get("flow_description", ""),
                320,
            ),
        }
        if "node_count" in item:
            summary["node_count"] = item.get("node_count")
        if "connection_count" in item:
            summary["connection_count"] = item.get("connection_count")
        trimmed.append(summary)
    return trimmed


def _trim_implicit_code_context_for_fast_local(implicit_code_context: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    trimmed = []
    for entry in list(implicit_code_context or [])[:1]:
        item = dict(entry or {})
        classes = []
        for class_entry in list(item.get("classes", []) or [])[:3]:
            cls = dict(class_entry or {})
            classes.append(
                {
                    "name": _truncate_text(cls.get("name", ""), 80),
                    "bases": list(cls.get("bases", []) or [])[:3],
                    "methods": list(cls.get("methods", []) or [])[:5],
                }
            )
        trimmed.append(
            {
                "file": _truncate_text(item.get("file", ""), 80),
                "module": _truncate_text(item.get("module", ""), 80),
                "classes": classes,
            }
        )
    return trimmed


def _trim_python_wrapper_rules_for_fast_local(python_node_wrapper_rules: dict[str, Any] | None) -> dict[str, Any]:
    rules = dict(python_node_wrapper_rules or {})
    if not rules:
        return {}
    return {
        "available": bool(rules.get("available", False)),
        "source_files": list(rules.get("source_files", []) or [])[:3],
        "summary": _truncate_text(rules.get("summary", ""), 220),
        "rules": [_truncate_text(rule, 140) for rule in list(rules.get("rules", []) or [])[:4]],
        "preferred_template": _truncate_text(rules.get("preferred_template", ""), 220),
        "notes": [_truncate_text(note, 140) for note in list(rules.get("notes", []) or [])[:2]],
    }


def _trim_task_analysis_guidance_for_fast_local(task_match_result: dict[str, Any] | None) -> dict[str, Any]:
    guidance = _task_analysis_guidance(task_match_result)
    return {
        "strategy": _truncate_text(guidance.get("strategy", ""), 80),
        "task": _truncate_text(guidance.get("task", ""), 140),
        "project_description": _truncate_text(guidance.get("project_description", ""), 180),
        "flow_description": _truncate_text(guidance.get("flow_description", ""), 700),
        "structured_flow_summary": _truncate_text(guidance.get("structured_flow_summary", ""), 700),
        "top_tool_matches": list(guidance.get("top_tool_matches", []) or [])[:FAST_LOCAL_MAX_TOOL_MATCHES],
        "top_skill_matches": list(guidance.get("top_skill_matches", []) or [])[:FAST_LOCAL_MAX_SKILL_MATCHES],
        "best_workflow_template": dict(guidance.get("best_workflow_template", {}) or {}),
        "missing_parts": [
            _truncate_text(item, 180)
            for item in list(guidance.get("missing_parts", []) or [])[:5]
        ],
        "notes": [_truncate_text(note, 180) for note in list(guidance.get("notes", []) or [])[:3]],
        "planning_directives": [
            _truncate_text(item, 180)
            for item in list(guidance.get("planning_directives", []) or [])[:3]
        ],
    }


def _trim_task_analysis_for_fast_local(task_match_result: dict[str, Any] | None) -> dict[str, Any]:
    result = dict(task_match_result or {})
    return {
        "project_description": _truncate_text(result.get("project_description", ""), 180),
        "task": _truncate_text(result.get("task", ""), 140),
        "flow_description": _truncate_text(result.get("flow_description", ""), 700),
        "structured_flow_summary": _truncate_text(result.get("structured_flow_summary", ""), 700),
        "strategy": _truncate_text(result.get("strategy", ""), 80),
        "tool_matches": list(result.get("tool_matches", []) or [])[:FAST_LOCAL_MAX_TOOL_MATCHES],
        "skill_matches": list(result.get("skill_matches", []) or [])[:FAST_LOCAL_MAX_SKILL_MATCHES],
        "best_workflow_template": dict(result.get("best_workflow_template", {}) or {}),
        "missing_parts": [
            _truncate_text(item, 180)
            for item in list(result.get("missing_parts", []) or [])[:5]
        ],
        "notes": [_truncate_text(note, 180) for note in list(result.get("notes", []) or [])[:3]],
    }


def _trim_skill_execution_recipes_for_fast_local(skill_execution_recipes: dict[str, Any] | None) -> dict[str, Any]:
    recipes_payload = dict(skill_execution_recipes or {})
    recipes = []
    for entry in list(recipes_payload.get("recipes", []) or [])[:FAST_LOCAL_MAX_RECIPE_COUNT]:
        item = dict(entry or {})
        workflow_template = dict(item.get("workflow_template", {}) or {})
        recipes.append(
            {
                "skill_id": _truncate_text(item.get("skill_id", ""), 80),
                "title": _truncate_text(item.get("title", ""), 120),
                "confidence": item.get("confidence", 0.0),
                "reason": _truncate_text(item.get("reason", ""), 180),
                "workflow_strategy": _truncate_text(item.get("workflow_strategy", ""), 140),
                "step_summary": [_truncate_text(step, 140) for step in list(item.get("step_summary", []) or [])[:4]],
                "validation_criteria": [
                    _truncate_text(step, 140) for step in list(item.get("validation_criteria", []) or [])[:3]
                ],
                "workflow_template": {
                    "path": _truncate_text(workflow_template.get("path", ""), 120),
                    "source_name": _truncate_text(workflow_template.get("source_name", ""), 80),
                    "flow_names": list(workflow_template.get("flow_names", []) or [])[:4],
                    "node_count": workflow_template.get("node_count"),
                    "connection_count": workflow_template.get("connection_count"),
                    "summary": _truncate_text(
                        workflow_template.get("summary", "") or workflow_template.get("description", ""),
                        220,
                    ),
                },
            }
        )
    return {"available": bool(recipes), "recipes": recipes}


def _fast_local_skill_score(skill: SkillRecord, task_description: str) -> tuple[int, int]:
    text = str(task_description or "").casefold()
    if not text:
        return (0, 0)
    haystacks = [
        str(skill.title or "").casefold(),
        str(skill.summary or "").casefold(),
        " ".join(str(tag or "").casefold() for tag in list(skill.tags or [])),
    ]
    score = 0
    overlap = 0
    for token in {part for part in re.split(r"[^a-z0-9_]+", text) if len(part) >= 3}:
        matched = any(token in haystack for haystack in haystacks)
        if matched:
            overlap += 1
            score += len(token)
    if any(str(skill.title or "").casefold() in text for _ in [0]) and str(skill.title or "").strip():
        score += 12
    return (score, overlap)


def _select_skills_for_fast_local(skills: list[SkillRecord], task_description: str) -> list[SkillRecord]:
    ranked = []
    for skill in list(skills or []):
        score, overlap = _fast_local_skill_score(skill, task_description)
        ranked.append(
            (
                -score,
                -overlap,
                str(skill.title or "").casefold(),
                str(getattr(skill, "skill_id", "") or "").casefold(),
                skill,
            )
        )
    ranked.sort()
    selected = [skill for _, _, _, _, skill in ranked[:FAST_LOCAL_TASK_MATCH_SKILL_LIMIT]]
    return selected


def _enforce_fast_local_payload_budget(payload: dict[str, Any], max_chars: int = FAST_LOCAL_PROMPT_CHAR_LIMIT) -> dict[str, Any]:
    compact = dict(payload or {})
    try:
        serialized = json.dumps(compact, ensure_ascii=True)
    except Exception:
        return compact
    if len(serialized) <= max_chars:
        return compact
    if "recent_conversation" in compact:
        compact["recent_conversation"] = []
    if "pinned_context" in compact:
        compact["pinned_context"] = []
    if "implicit_code_context" in compact:
        compact["implicit_code_context"] = []
    if "attached_files" in compact:
        compact["attached_files"] = list(compact.get("attached_files", []) or [])[:1]
    if "skill_execution_recipes" in compact:
        compact["skill_execution_recipes"] = {"available": False, "recipes": []}
    try:
        serialized = json.dumps(compact, ensure_ascii=True)
    except Exception:
        return compact
    if len(serialized) <= max_chars:
        return compact
    if "attached_workflow_jsons" in compact:
        compact["attached_workflow_jsons"] = []
    if "task_analysis" in compact:
        compact["task_analysis"] = _trim_task_analysis_for_fast_local({})
    if "task_analysis_guidance" in compact:
        compact["task_analysis_guidance"] = _trim_task_analysis_guidance_for_fast_local({})
    return compact


def _build_fast_local_router_payload(
    user_prompt: str,
    task_match_result: dict[str, Any] | None,
    pinned_context: list[str] | None,
    attached_files: list[str] | None,
    attached_workflow_jsons: list[dict[str, Any]] | None,
    workspace_relationship_context: dict[str, Any] | None,
    implicit_code_context: list[dict[str, Any]] | None,
    python_node_wrapper_rules: dict[str, Any] | None,
    skill_execution_recipes: dict[str, Any] | None,
    recent_messages: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    payload = {
        "latest_user_prompt": _truncate_text(user_prompt, 700),
        "current_task_analysis": _trim_task_analysis_for_fast_local(task_match_result),
        "task_analysis_guidance": _trim_task_analysis_guidance_for_fast_local(task_match_result),
        "pinned_context": [_truncate_text(item, 220) for item in list(pinned_context or [])[:FAST_LOCAL_MAX_PINNED_CONTEXT]],
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])[:FAST_LOCAL_MAX_ATTACHED_FILES]],
        "attached_workflow_jsons": _trim_workflow_contexts_for_fast_local(attached_workflow_jsons),
        "workspace_relationship_context": {
            "active_flow_name": _truncate_text(dict(workspace_relationship_context or {}).get("active_flow_name", ""), 80),
            "active_flow_type": _truncate_text(dict(workspace_relationship_context or {}).get("active_flow_type", ""), 40),
            "selected_node_count": dict(workspace_relationship_context or {}).get("selected_node_count", 0),
        },
        "implicit_code_context": _trim_implicit_code_context_for_fast_local(implicit_code_context),
        "python_node_wrapper_rules": _trim_python_wrapper_rules_for_fast_local(python_node_wrapper_rules),
        "skill_execution_recipes": _trim_skill_execution_recipes_for_fast_local(skill_execution_recipes),
        "recent_conversation": _trim_recent_conversation_for_fast_local(recent_messages),
    }
    return _enforce_fast_local_payload_budget(payload)


def _build_fast_local_grounding_payload(
    user_prompt: str,
    task_match_result: dict[str, Any] | None,
    pinned_context: list[str] | None,
    attached_files: list[str] | None,
    attached_workflow_jsons: list[dict[str, Any]] | None,
    workspace_relationship_context: dict[str, Any] | None,
    implicit_code_context: list[dict[str, Any]] | None,
    python_node_wrapper_rules: dict[str, Any] | None,
    skill_execution_recipes: dict[str, Any] | None,
    recent_messages: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    payload = {
        "latest_user_prompt": _truncate_text(user_prompt, 800),
        "task_analysis": _trim_task_analysis_for_fast_local(task_match_result),
        "task_analysis_guidance": _trim_task_analysis_guidance_for_fast_local(task_match_result),
        "pinned_context": [_truncate_text(item, 220) for item in list(pinned_context or [])[:FAST_LOCAL_MAX_PINNED_CONTEXT]],
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])[:FAST_LOCAL_MAX_ATTACHED_FILES]],
        "attached_workflow_jsons": _trim_workflow_contexts_for_fast_local(attached_workflow_jsons),
        "workspace_relationship_context": {
            "active_flow_name": _truncate_text(dict(workspace_relationship_context or {}).get("active_flow_name", ""), 80),
            "active_flow_type": _truncate_text(dict(workspace_relationship_context or {}).get("active_flow_type", ""), 40),
        },
        "implicit_code_context": _trim_implicit_code_context_for_fast_local(implicit_code_context),
        "python_node_wrapper_rules": _trim_python_wrapper_rules_for_fast_local(python_node_wrapper_rules),
        "skill_execution_recipes": _trim_skill_execution_recipes_for_fast_local(skill_execution_recipes),
        "recent_conversation": _trim_recent_conversation_for_fast_local(recent_messages),
    }
    return _enforce_fast_local_payload_budget(payload)


def _build_fast_local_action_plan_payload(
    user_prompt: str,
    canvas_context: dict[str, Any] | None,
    task_match_result: dict[str, Any] | None,
    pinned_context: list[str] | None,
    attached_files: list[str] | None,
    attached_workflow_jsons: list[dict[str, Any]] | None,
    workspace_relationship_context: dict[str, Any] | None,
    implicit_code_context: list[dict[str, Any]] | None,
    python_node_wrapper_rules: dict[str, Any] | None,
    skill_execution_recipes: dict[str, Any] | None,
    recent_messages: list[dict[str, Any]] | None,
    build_path_guidance: dict[str, Any] | None,
) -> dict[str, Any]:
    minimized_canvas = dict(canvas_context or {})
    payload = {
        "latest_user_prompt": _truncate_text(user_prompt, 800),
        "canvas_context": {
            "selected_node_count": minimized_canvas.get("selected_node_count", 0),
            "selected_nodes": list(minimized_canvas.get("selected_nodes", []) or [])[:3],
            "nodes": list(minimized_canvas.get("nodes", []) or [])[:10],
            "connections": list(minimized_canvas.get("connections", []) or [])[:12],
            "active_flow_name": _truncate_text(minimized_canvas.get("active_flow_name", ""), 80),
            "active_flow_type": _truncate_text(minimized_canvas.get("active_flow_type", ""), 40),
        },
        "task_analysis": _trim_task_analysis_for_fast_local(task_match_result),
        "task_analysis_guidance": _trim_task_analysis_guidance_for_fast_local(task_match_result),
        "pinned_context": [_truncate_text(item, 220) for item in list(pinned_context or [])[:FAST_LOCAL_MAX_PINNED_CONTEXT]],
        "attached_files": [Path(str(path)).name for path in list(attached_files or [])[:FAST_LOCAL_MAX_ATTACHED_FILES]],
        "attached_workflow_jsons": _trim_workflow_contexts_for_fast_local(attached_workflow_jsons),
        "workspace_relationship_context": {
            "active_flow_name": _truncate_text(dict(workspace_relationship_context or {}).get("active_flow_name", ""), 80),
            "active_flow_type": _truncate_text(dict(workspace_relationship_context or {}).get("active_flow_type", ""), 40),
            "selected_node_count": dict(workspace_relationship_context or {}).get("selected_node_count", 0),
        },
        "implicit_code_context": _trim_implicit_code_context_for_fast_local(implicit_code_context),
        "python_node_wrapper_rules": _trim_python_wrapper_rules_for_fast_local(python_node_wrapper_rules),
        "skill_execution_recipes": _trim_skill_execution_recipes_for_fast_local(skill_execution_recipes),
        "build_path_guidance": dict(build_path_guidance or {}),
        "recent_conversation": _trim_recent_conversation_for_fast_local(recent_messages),
        "fast_local_mode": True,
    }
    return _enforce_fast_local_payload_budget(payload)


def _ollama_chat_completion_content(
    messages: list[dict[str, Any]],
    model_name: str,
    *,
    temperature: float = 0,
    response_json: bool = True,
) -> str:
    runtime_model_name = _resolve_ollama_runtime_model_name(model_name, messages)
    model_tag = _resolve_ollama_model_tag(runtime_model_name)
    _raise_if_ollama_request_is_unstable(model_tag, messages)
    payload: dict[str, Any] = {
        "model": model_tag,
        "messages": [
            {
                "role": str(message.get("role", "") or "").strip() or "user",
                "content": str(message.get("content", "") or ""),
            }
            for message in list(messages or [])
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": _resolve_ollama_context_tokens(model_tag),
        },
    }
    if response_json:
        payload["format"] = "json"

    request = urllib.request.Request(
        url=_resolve_ollama_host() + "/api/chat",
        data=json.dumps(payload, ensure_ascii=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=_resolve_ollama_timeout_seconds()) as response:
            raw_content = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"The local Ollama server is not available. Install and start Ollama, then pull the selected model: ollama pull {model_tag}."
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            "The local Ollama request failed at the system level, which usually means the model ran out of usable local resources. "
            "Try a smaller local model, close other memory-heavy apps, or reduce the planning context."
        ) from exc
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Ollama returned invalid JSON.") from exc

    message = parsed.get("message", {}) if isinstance(parsed, dict) else {}
    content = str(message.get("content", "") or parsed.get("response", "") or "").strip()
    if not content:
        raise RuntimeError("Ollama returned an empty response.")
    _record_llm_usage(
        provider="ollama",
        model_name=runtime_model_name,
        input_tokens=parsed.get("prompt_eval_count", 0),
        output_tokens=parsed.get("eval_count", 0),
    )
    return content


def _anthropic_max_tokens(model_name: str) -> int:
    resolved_name = _resolve_model_name(model_name)
    return int(ANTHROPIC_MODEL_MAX_TOKENS.get(resolved_name, 8192))


def _prepare_anthropic_messages(
    messages: list[dict[str, Any]],
    *,
    response_json: bool = True,
) -> tuple[str, list[dict[str, str]]]:
    system_parts = []
    prepared_messages = []
    for message in list(messages or []):
        role = str(message.get("role", "") or "").strip().lower()
        content = str(message.get("content", "") or "")
        if not content:
            continue
        if role == "system":
            system_parts.append(content)
            continue
        if role not in {"user", "assistant"}:
            role = "user"
        prepared_messages.append({"role": role, "content": content})

    if response_json:
        json_instruction = "Return only valid JSON. Do not include markdown fences or explanatory text outside the JSON object."
        for index in range(len(prepared_messages) - 1, -1, -1):
            if prepared_messages[index]["role"] == "user":
                prepared_messages[index]["content"] = prepared_messages[index]["content"].rstrip() + "\n\n" + json_instruction
                break
        else:
            prepared_messages.append({"role": "user", "content": json_instruction})

    if not prepared_messages:
        prepared_messages.append({"role": "user", "content": "Respond to the current QuESt Agent request."})

    merged_messages = []
    for message in prepared_messages:
        if merged_messages and merged_messages[-1]["role"] == message["role"]:
            merged_messages[-1]["content"] = merged_messages[-1]["content"].rstrip() + "\n\n" + message["content"]
        else:
            merged_messages.append(message)
    return "\n\n".join(system_parts).strip(), merged_messages


def _anthropic_chat_completion_content(
    messages: list[dict[str, Any]],
    model_name: str,
    *,
    temperature: float = 0,
    api_key: str | None = None,
    response_json: bool = True,
) -> str:
    if Anthropic is None:
        raise RuntimeError(
            "The anthropic Python package is not installed. Install it to use Claude models."
        )
    system_text, prepared_messages = _prepare_anthropic_messages(messages, response_json=response_json)
    client = Anthropic(
        api_key=_resolve_anthropic_api_key(api_key),
        timeout=_resolve_anthropic_timeout_seconds(),
    )
    request_kwargs: dict[str, Any] = {
        "model": _resolve_model_name(model_name),
        "max_tokens": _anthropic_max_tokens(model_name),
        "messages": prepared_messages,
    }
    if _resolve_model_name(model_name) not in ANTHROPIC_MODELS_WITHOUT_TEMPERATURE:
        request_kwargs["temperature"] = temperature
    if system_text:
        request_kwargs["system"] = system_text
    try:
        response = client.messages.create(**request_kwargs)
    except Exception as exc:
        raise RuntimeError(f"Anthropic API request failed. {exc}") from exc

    usage = getattr(response, "usage", None)
    _record_llm_usage(
        provider="anthropic",
        model_name=_resolve_model_name(model_name),
        input_tokens=(
            _coerce_token_count(_extract_attr_or_key(usage, "input_tokens", 0))
            + _coerce_token_count(_extract_attr_or_key(usage, "cache_creation_input_tokens", 0))
            + _coerce_token_count(_extract_attr_or_key(usage, "cache_read_input_tokens", 0))
        ),
        output_tokens=_extract_attr_or_key(usage, "output_tokens", 0),
        cached_input_tokens=_extract_attr_or_key(usage, "cache_read_input_tokens", 0),
    )
    content_blocks = list(getattr(response, "content", []) or [])
    text_parts = []
    for block in content_blocks:
        block_type = str(getattr(block, "type", "") or "").strip()
        if block_type == "text":
            text_parts.append(str(getattr(block, "text", "") or ""))
    content = "\n".join(part.strip() for part in text_parts if part.strip()).strip()
    if not content:
        raise RuntimeError("Anthropic returned an empty response.")
    return content


def _chat_completion_content(
    messages: list[dict[str, Any]],
    *,
    selected_model: str | None = None,
    temperature: float = 0,
    api_key: str | None = None,
    response_json: bool = True,
) -> tuple[str, str]:
    resolved_model_name = _resolve_model_name(selected_model)
    if _is_ollama_model(resolved_model_name):
        content = _ollama_chat_completion_content(
            messages,
            resolved_model_name,
            temperature=temperature,
            response_json=response_json,
        )
        return content, _resolve_ollama_runtime_model_name(resolved_model_name, messages)

    if _is_anthropic_model(resolved_model_name):
        content = _anthropic_chat_completion_content(
            messages,
            resolved_model_name,
            temperature=temperature,
            api_key=api_key,
            response_json=response_json,
        )
        return content, resolved_model_name

    if OpenAI is None:
        raise RuntimeError(
            "The openai Python package is not installed. Install it to use OpenAI models, or select a local Gemma 4 model."
        )
    client = OpenAI(api_key=_resolve_api_key(api_key))
    request_kwargs: dict[str, Any] = {
        "model": resolved_model_name,
        "messages": messages,
    }
    if resolved_model_name not in OPENAI_MODELS_WITH_DEFAULT_TEMPERATURE_ONLY:
        request_kwargs["temperature"] = temperature
    if response_json:
        request_kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**request_kwargs)
    usage = getattr(response, "usage", None)
    prompt_tokens_details = _extract_attr_or_key(usage, "prompt_tokens_details", None)
    _record_llm_usage(
        provider="openai",
        model_name=resolved_model_name,
        input_tokens=_extract_attr_or_key(usage, "prompt_tokens", 0),
        output_tokens=_extract_attr_or_key(usage, "completion_tokens", 0),
        cached_input_tokens=_extract_attr_or_key(prompt_tokens_details, "cached_tokens", 0),
    )
    content = str(response.choices[0].message.content or "").strip() if response.choices else ""
    return content, resolved_model_name


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


def _tokenize_match_text(value: Any) -> list[str]:
    return [
        token
        for token in re.split(r"[^a-z0-9_]+", str(value or "").casefold())
        if len(token) >= 2 and token not in MATCH_STOPWORDS
    ]


def _workflow_context_search_text(attached_workflow_jsons: list[dict[str, Any]] | None) -> str:
    parts = []
    for entry in list(attached_workflow_jsons or [])[:3]:
        item = dict(entry or {})
        for key in ("file", "flow_name", "flow_type", "summary", "description"):
            value = str(item.get(key, "") or "").strip()
            if value:
                parts.append(value)
        content = item.get("content", {})
        if isinstance(content, dict):
            for node in list(content.get("nodes_df", []) or [])[:30]:
                node_item = dict(node or {})
                for key in ("name", "node_name", "node_type", "text", "variable_name", "tool", "tool_name", "app"):
                    value = str(node_item.get(key, "") or "").strip()
                    if value:
                        parts.append(value)
            for row in list(content.get("connections_df", []) or [])[:20]:
                row_item = dict(row or {})
                for key in ("source_node", "target_node", "source_port", "target_port"):
                    value = str(row_item.get(key, "") or "").strip()
                    if value:
                        parts.append(value)
    return " ".join(parts)


def _build_matcher_search_text(
    task_description: str,
    pinned_context: list[str],
    attached_files: list[str],
    attached_workflow_jsons: list[dict[str, Any]],
    workspace_relationship_context: dict[str, Any],
    implicit_code_context: list[dict[str, Any]],
) -> str:
    parts = [str(task_description or "").strip()]
    parts.extend(str(item or "").strip() for item in list(pinned_context or [])[:4] if str(item or "").strip())
    parts.extend(Path(str(path)).name for path in list(attached_files or [])[:5] if str(path or "").strip())
    parts.append(_workflow_context_search_text(attached_workflow_jsons))
    for key in ("current_flow_name", "current_flow_type", "master_flow_name", "linked_proxy_name"):
        value = str(dict(workspace_relationship_context or {}).get(key, "") or "").strip()
        if value:
            parts.append(value)
    for subflow in list(dict(workspace_relationship_context or {}).get("sibling_subflows", []) or [])[:8]:
        item = dict(subflow or {})
        for key in ("flow_name", "proxy_name"):
            value = str(item.get(key, "") or "").strip()
            if value:
                parts.append(value)
    for entry in list(implicit_code_context or [])[:2]:
        item = dict(entry or {})
        for key in ("file", "module"):
            value = str(item.get(key, "") or "").strip()
            if value:
                parts.append(value)
        for cls in list(item.get("classes", []) or [])[:4]:
            class_item = dict(cls or {})
            class_name = str(class_item.get("name", "") or "").strip()
            if class_name:
                parts.append(class_name)
    return " ".join(part for part in parts if part)


def _score_overlap(query_text: str, haystack_text: str) -> tuple[float, list[str]]:
    query = str(query_text or "").casefold()
    haystack = str(haystack_text or "").casefold()
    if not query or not haystack:
        return 0.0, []
    query_tokens = _tokenize_match_text(query)
    haystack_tokens = set(_tokenize_match_text(haystack))
    if not query_tokens or not haystack_tokens:
        return 0.0, []
    matched_tokens = []
    score = 0.0
    seen = set()
    for token in query_tokens:
        if token in haystack_tokens and token not in seen:
            seen.add(token)
            matched_tokens.append(token)
            score += min(0.18, 0.04 + (len(token) * 0.01))
    if haystack and any(alias and alias in query for alias in sorted(haystack_tokens, key=len, reverse=True)[:12]):
        score += 0.06
    return min(score, 0.95), matched_tokens[:6]


def _task_match_field_is_empty(value: Any) -> bool:
    cleaned = str(value or "").strip().casefold()
    return cleaned in {"", "n/a", "na", "none", "unknown", "not provided"}


def _coalesce_task_match_text(*values: Any) -> str:
    for value in values:
        cleaned = str(value or "").strip()
        if cleaned:
            return cleaned
    return ""


def _should_replace_task_match_field(
    field_name: str,
    current_value: Any,
    fallback_value: str,
    *,
    task_description: str,
    has_workflow_context: bool,
) -> bool:
    if not fallback_value:
        return False
    if _task_match_field_is_empty(current_value):
        return True
    if not has_workflow_context:
        return False
    current_text = str(current_value or "").strip().casefold()
    if not str(task_description or "").strip():
        if field_name in {"project_description", "task", "flow_description"}:
            return True
    contradiction_markers = {
        "flow_description": ("no existing flow", "no current flow", "not provided"),
        "task": ("create a new workflow", "build a new workflow"),
        "project_description": ("workflow creation",),
    }
    return any(marker in current_text for marker in contradiction_markers.get(field_name, ()))


def _build_task_match_fallback_fields(
    task_description: str,
    attached_workflow_jsons: list[dict[str, Any]],
    workspace_relationship_context: dict[str, Any],
) -> dict[str, str]:
    workflow_summaries = []
    flow_names = []
    for entry in list(attached_workflow_jsons or [])[:3]:
        item = dict(entry or {})
        summary = _coalesce_task_match_text(
            item.get("summary", ""),
            item.get("description", ""),
            item.get("flow_description", ""),
        )
        if summary:
            workflow_summaries.append(summary)
        for flow_name in list(item.get("flow_names", []) or [])[:4]:
            cleaned = str(flow_name or "").strip()
            if cleaned and cleaned not in flow_names:
                flow_names.append(cleaned)

    workspace_context = dict(workspace_relationship_context or {})
    current_flow_summary = _coalesce_task_match_text(
        workspace_context.get("current_flow_summary", ""),
        workspace_context.get("workspace_summary", ""),
    )
    current_flow_name = _coalesce_task_match_text(
        workspace_context.get("current_flow_name", ""),
        flow_names[0] if flow_names else "",
    )

    flow_description = _coalesce_task_match_text(
        workflow_summaries[0] if workflow_summaries else "",
        current_flow_summary,
        f"Current Workspace flow '{current_flow_name}' is attached for analysis." if current_flow_name else "",
    )
    project_description = _coalesce_task_match_text(
        current_flow_summary,
        workflow_summaries[0] if workflow_summaries else "",
        task_description,
        "Current Workspace flow analysis.",
    )
    task = _coalesce_task_match_text(
        task_description,
        "Analyze the current Workspace flow and identify the most relevant QuESt tools and saved skills.",
    )
    return {
        "project_description": project_description,
        "task": task,
        "flow_description": flow_description,
    }


def _tool_query_alignment_bonus(tool: dict[str, Any], query_text: str) -> float:
    query_tokens = set(_tokenize_match_text(query_text))
    if not query_tokens:
        return 0.0
    exact_tokens = set(
        _tokenize_match_text(
            " ".join(
                [
                    str(tool.get("tool_id", "") or "").strip(),
                    str(tool.get("name", "") or "").strip(),
                    str(tool.get("search_key", "") or "").strip(),
                ]
            )
        )
    )
    if query_tokens & exact_tokens:
        return 0.12
    return 0.0


def _skill_query_alignment_bonus(skill: SkillRecord, query_text: str) -> float:
    query_tokens = set(_tokenize_match_text(query_text))
    if not query_tokens:
        return 0.0
    skill_tool_tokens = set()
    for tool_id in list(getattr(skill, "recommended_tools", []) or []) + list(getattr(skill, "required_tools", []) or []):
        skill_tool_tokens.update(_tokenize_match_text(tool_id))

    bonus = 0.0
    if query_tokens & skill_tool_tokens:
        bonus += 0.16
        if str(getattr(skill, "skill_type", "") or "").strip() == "quest_tool_specific":
            bonus += 0.08
    if str(getattr(skill, "workflow_json_path", "") or "").strip():
        bonus += 0.03
    if str(getattr(skill, "skill_level", "") or "").strip() in {"Proficient", "Expert"}:
        bonus += 0.02
    return bonus


def _looks_like_btm_text(text: str) -> bool:
    lowered = str(text or "").casefold().replace("_", " ").replace("-", " ")
    return any(
        phrase in lowered
        for phrase in (
            "btm",
            "behind the meter",
            "cost savings",
            "tariff savings",
            "battery optimization",
            "storage optimization",
            "pv profile",
            "load profile",
        )
    )


def _skill_looks_like_btm(skill: SkillRecord) -> bool:
    return _looks_like_btm_text(_skill_search_haystack(skill))


def _prefer_tool_specific_strategy(result: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(result or {})
    top_non_workspace_tool = next(
        (
            item for item in list(normalized.get("tool_matches", []) or [])
            if str(item.get("tool_id", "") or "").strip() not in {"", "workspace"}
            and float(item.get("confidence", 0.0) or 0.0) >= 0.25
        ),
        None,
    )
    top_tool_specific_skill = next(
        (
            item for item in list(normalized.get("skill_matches", []) or [])
            if str(item.get("skill_type", "") or "").strip() == "quest_tool_specific"
            and float(item.get("confidence", 0.0) or 0.0) >= 0.35
        ),
        None,
    )
    if top_non_workspace_tool and top_tool_specific_skill:
        normalized["strategy"] = "use_quest_skill"
        specific_skills = [
            item for item in list(normalized.get("skill_matches", []) or [])
            if str(item.get("skill_type", "") or "").strip() == "quest_tool_specific"
        ]
        if len(specific_skills) >= 2:
            normalized["skill_matches"] = specific_skills[:4]
    return normalized


def _normalized_tool_id(value: Any) -> str:
    return str(value or "").strip().casefold()


def _skill_tool_ids(skill: SkillRecord) -> set[str]:
    tool_ids = set()
    for tool_id in list(getattr(skill, "recommended_tools", []) or []) + list(getattr(skill, "required_tools", []) or []):
        normalized = _normalized_tool_id(tool_id)
        if normalized:
            tool_ids.add(normalized)
    return tool_ids


def _filter_skills_by_matched_tools(
    skills: list[SkillRecord],
    tool_matches: list[dict[str, Any]] | None,
    *,
    include_general_fallback: bool = True,
) -> list[SkillRecord]:
    ranked_tool_ids = [
        _normalized_tool_id(dict(item or {}).get("tool_id", ""))
        for item in list(tool_matches or [])
    ]
    ranked_tool_ids = [tool_id for tool_id in ranked_tool_ids if tool_id]
    non_workspace_tool_ids = [tool_id for tool_id in ranked_tool_ids if tool_id != "workspace"]
    matched_tool_ids = set(non_workspace_tool_ids or ranked_tool_ids)
    if not matched_tool_ids:
        return list(skills or [])

    prioritized = []
    general_fallback = []
    workspace_fallback = []
    seen_ids = set()

    for skill in list(skills or []):
        skill_id = str(getattr(skill, "skill_id", "") or "").strip()
        if not skill_id or skill_id in seen_ids:
            continue
        seen_ids.add(skill_id)
        skill_type = str(getattr(skill, "skill_type", "") or "").strip()
        skill_tool_ids = _skill_tool_ids(skill)
        intersects = bool(skill_tool_ids & matched_tool_ids)
        if intersects and skill_type == "quest_tool_specific":
            prioritized.append(skill)
            continue
        if include_general_fallback and skill_type == "general_python":
            general_fallback.append(skill)
            continue
        if include_general_fallback and "workspace" in skill_tool_ids:
            workspace_fallback.append(skill)

    if prioritized:
        if non_workspace_tool_ids:
            return prioritized
        return prioritized + general_fallback + workspace_fallback
    if include_general_fallback and (general_fallback or workspace_fallback):
        return general_fallback + workspace_fallback
    return list(skills or [])


def _build_best_workflow_template(
    skill_matches: list[dict[str, Any]] | None,
    skills: list[SkillRecord] | None,
    tool_matches: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    skills_by_id = {
        str(getattr(skill, "skill_id", "") or "").strip(): skill
        for skill in list(skills or [])
        if str(getattr(skill, "skill_id", "") or "").strip()
    }
    preferred_tool_ids = {
        _normalized_tool_id(dict(item or {}).get("tool_id", ""))
        for item in list(tool_matches or [])
        if _normalized_tool_id(dict(item or {}).get("tool_id", ""))
    }
    non_workspace_tool_ids = {tool_id for tool_id in preferred_tool_ids if tool_id != "workspace"}
    btm_preferred = "btm" in non_workspace_tool_ids
    candidates = []
    for match in list(skill_matches or []):
        item = dict(match or {})
        skill_id = str(item.get("skill_id", "") or "").strip()
        skill = skills_by_id.get(skill_id)
        if skill is None:
            continue
        workflow_json_path = str(getattr(skill, "workflow_json_path", "") or "").strip()
        if not workflow_json_path:
            continue
        tool_overlap = _skill_tool_ids(skill) & preferred_tool_ids
        if non_workspace_tool_ids and not (tool_overlap & non_workspace_tool_ids):
            continue
        if btm_preferred and str(getattr(skill, "skill_type", "") or "").strip() == "quest_tool_specific" and not _skill_looks_like_btm(skill):
            continue
        confidence = _coerce_confidence(item.get("confidence", 0.0))
        template_score = confidence
        if tool_overlap:
            template_score += 0.08
        if str(getattr(skill, "skill_type", "") or "").strip() == "quest_tool_specific":
            template_score += 0.05
        candidates.append(
            {
                "skill_id": skill_id,
                "title": str(getattr(skill, "title", "") or skill_id).strip(),
                "skill_type": str(getattr(skill, "skill_type", "") or "").strip(),
                "confidence": confidence,
                "reason": str(item.get("reason", "") or "").strip(),
                "workflow_json_path": workflow_json_path,
                "recommended_tools": [str(value).strip() for value in list(getattr(skill, "recommended_tools", []) or []) if str(value).strip()],
                "required_tools": [str(value).strip() for value in list(getattr(skill, "required_tools", []) or []) if str(value).strip()],
                "summary": str(getattr(skill, "summary", "") or "").strip(),
                "template_score": round(template_score, 4),
                "tool_overlap": sorted(tool_overlap),
            }
        )
    if not candidates:
        return {}
    candidates.sort(
        key=lambda item: (
            -float(item.get("template_score", 0.0) or 0.0),
            str(item.get("title", "") or "").casefold(),
        )
    )
    best = dict(candidates[0] or {})
    return {
        "skill_id": str(best.get("skill_id", "") or "").strip(),
        "title": str(best.get("title", "") or "").strip(),
        "skill_type": str(best.get("skill_type", "") or "").strip(),
        "workflow_json_path": str(best.get("workflow_json_path", "") or "").strip(),
        "confidence": _coerce_confidence(best.get("confidence", 0.0)),
        "reason": str(best.get("reason", "") or "").strip(),
        "recommended_tools": list(best.get("recommended_tools", []) or []),
        "required_tools": list(best.get("required_tools", []) or []),
        "summary": str(best.get("summary", "") or "").strip(),
        "selection_reason": (
            f"Selected '{best.get('title', '')}' as the best reusable workflow template because it matches the task, aligns with the matched tools, and already includes a workflow JSON baseline."
            if list(best.get("tool_overlap", []) or [])
            else
            f"Selected '{best.get('title', '')}' as the best reusable workflow template because it best matches the task and already includes a workflow JSON baseline."
        ).strip(),
    }


def _read_workflow_json_file(path: str) -> dict[str, Any]:
    normalized_path = os.path.normpath(str(path or "").strip())
    if not normalized_path:
        raise RuntimeError("Workflow template path is missing.")
    with open(normalized_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RuntimeError("Workflow template must be a JSON object.")
    return data


def _infer_python_ports_from_wrapper(wrapper_text: str) -> tuple[list[str], list[str]]:
    source = str(wrapper_text or "").strip()
    if not source:
        return [], []
    try:
        tree = __import__("ast").parse(source)
    except Exception:
        return [], []
    for node in list(getattr(tree, "body", []) or []):
        if not isinstance(node, (__import__("ast").FunctionDef, __import__("ast").AsyncFunctionDef)):
            continue
        input_ports = []
        for arg in list(getattr(node.args, "args", []) or []):
            arg_name = str(getattr(arg, "arg", "") or "").strip()
            if arg_name and arg_name != "self":
                input_ports.append(arg_name)
        output_ports = []
        for child in __import__("ast").walk(node):
            if not isinstance(child, __import__("ast").Return):
                continue
            returned_value = getattr(child, "value", None)
            if not isinstance(returned_value, __import__("ast").Dict):
                continue
            for key_node in list(getattr(returned_value, "keys", []) or []):
                if isinstance(key_node, __import__("ast").Constant) and isinstance(key_node.value, str):
                    output_ports.append(str(key_node.value).strip())
                elif isinstance(key_node, __import__("ast").Str):
                    output_ports.append(str(key_node.s).strip())
        return [item for item in input_ports if item], [item for item in output_ports if item]
    return [], []


def _build_template_workflow_inventory(workflow_json_data: dict[str, Any]) -> dict[str, Any]:
    data = dict(workflow_json_data or {})
    node_records = [dict(item or {}) for item in list(data.get("nodes_df", []) or [])]
    node_lookup = {str(item.get("node_id", "") or "").strip(): item for item in node_records if str(item.get("node_id", "") or "").strip()}
    subflow_records = [dict(item or {}) for item in list(data.get("subflows_df", []) or []) if isinstance(item, dict)]
    subflow_names = {
        str(item.get("flow_name", "") or "").strip()
        for item in subflow_records
        if str(item.get("flow_name", "") or "").strip()
    }
    data_nodes = []
    python_nodes = []
    text_nodes = []
    for row in node_records:
        node_name = str(row.get("node_name", "") or "").strip()
        node_type = str(row.get("node_type", "") or "").strip()
        if not node_name:
            continue
        if node_type == "data_node":
            data_nodes.append(
                {
                    "name": node_name,
                    "variable_name": str(row.get("node_input_variable", "") or "").strip(),
                    "value": str(row.get("node_input_value", "") or ""),
                    "value_display": bool(row.get("node_value_display", False)),
                    "is_path": bool(row.get("node_is_path", False)),
                }
            )
        elif node_type == "python_node":
            wrapper = str(row.get("node_function_wrapper", "") or "").strip()
            input_ports, output_ports = _infer_python_ports_from_wrapper(wrapper)
            is_subflow_proxy = node_name in subflow_names
            python_nodes.append(
                {
                    "name": node_name,
                    "input_ports": input_ports,
                    "output_ports": output_ports,
                    "is_subflow_proxy": is_subflow_proxy,
                    "proxy_for_subflow": node_name if is_subflow_proxy else "",
                    "wrapper": _truncate_text(wrapper, 1200) if is_subflow_proxy else wrapper,
                }
            )
        elif node_type == "back_node":
            text_nodes.append(
                {
                    "name": node_name,
                    "text": str(row.get("node_input_value", "") or ""),
                }
            )
    connections = []
    for row in list(data.get("connections_df", []) or []):
        item = dict(row or {})
        source_id = str(item.get("from_node", "") or "").strip()
        target_id = str(item.get("to_node", "") or "").strip()
        source_name = str(node_lookup.get(source_id, {}).get("node_name", "") or "").strip()
        target_name = str(node_lookup.get(target_id, {}).get("node_name", "") or "").strip()
        mapping = dict(item.get("mapping", {}) or {}) if isinstance(item.get("mapping"), dict) else {}
        if mapping:
            for source_port, target_port in mapping.items():
                connections.append(
                    {
                        "from_node": source_name,
                        "from_port": str(source_port or "").strip(),
                        "to_node": target_name,
                        "to_port": str(target_port or "").strip(),
                    }
                )
        else:
            connections.append(
                {
                    "from_node": source_name,
                    "from_port": "",
                    "to_node": target_name,
                    "to_port": "",
                }
            )
    subflows = []
    for subflow in subflow_records:
        subflow_nodes = [dict(item or {}) for item in list(subflow.get("nodes_df", []) or [])]
        subflows.append(
            {
                "flow_name": str(subflow.get("flow_name", "") or "").strip(),
                "flow_type": str(subflow.get("flow_type", "") or "").strip(),
                "data_node_count": sum(1 for item in subflow_nodes if str(item.get("node_type", "") or "").strip() == "data_node"),
                "python_node_count": sum(1 for item in subflow_nodes if str(item.get("node_type", "") or "").strip() == "python_node"),
                "text_node_count": sum(1 for item in subflow_nodes if str(item.get("node_type", "") or "").strip() == "back_node"),
                "connection_count": len(list(subflow.get("connections_df", []) or [])),
                "input_case_count": len(list(subflow.get("inputs_df", []) or [])),
            }
        )
    return {
        "flow_name": str(data.get("flow_name", "") or "").strip(),
        "flow_type": str(data.get("flow_type", "") or "").strip(),
        "data_nodes": data_nodes,
        "python_nodes": python_nodes,
        "text_nodes": text_nodes,
        "connections": connections,
        "subflows": subflows,
    }


def _tool_search_haystack(tool: dict[str, Any]) -> str:
    item = dict(tool or {})
    parts = [
        str(item.get("tool_id", "") or "").strip(),
        str(item.get("name", "") or "").strip(),
        str(item.get("description", "") or "").strip(),
        str(item.get("search_key", "") or "").strip(),
        " ".join(str(value).strip() for value in list(item.get("aliases", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(item.get("typical_tasks", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(item.get("workflow_roles", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(item.get("input_types", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(item.get("output_types", []) or []) if str(value).strip()),
    ]
    return " ".join(part for part in parts if part)


def _skill_search_haystack(skill: SkillRecord) -> str:
    raw_data = getattr(skill, "raw_data", {}) or {}
    if not isinstance(raw_data, dict):
        raw_data = {}
    classification = raw_data.get("classification", {}) if isinstance(raw_data.get("classification", {}), dict) else {}
    task = raw_data.get("task", {}) if isinstance(raw_data.get("task", {}), dict) else {}
    plan = raw_data.get("plan", {}) if isinstance(raw_data.get("plan", {}), dict) else {}
    parts = [
        str(getattr(skill, "skill_id", "") or "").strip(),
        str(getattr(skill, "title", "") or "").strip(),
        str(getattr(skill, "summary", "") or "").strip(),
        str(task.get("description", "") or "").strip(),
        str(task.get("pinned_context_summary", "") or "").strip(),
        str(plan.get("workflow_strategy", "") or "").strip(),
        " ".join(str(value).strip() for value in list(plan.get("step_summary", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(getattr(skill, "tags", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(classification.get("tags", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(getattr(skill, "recommended_tools", []) or []) if str(value).strip()),
        " ".join(str(value).strip() for value in list(getattr(skill, "required_tools", []) or []) if str(value).strip()),
    ]
    return " ".join(part for part in parts if part)


def _heuristic_tool_matches(
    query_text: str,
    tools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    matches = []
    for tool in list(tools or []):
        item = dict(tool or {})
        score, matched_tokens = _score_overlap(query_text, _tool_search_haystack(item))
        score += _tool_query_alignment_bonus(item, query_text)
        if score <= 0.0:
            continue
        if score < 0.14 and len(matched_tokens) < 2:
            continue
        reason = "Matched flow/task terms"
        if matched_tokens:
            reason += ": " + ", ".join(matched_tokens[:4])
        matches.append(
            {
                "tool_id": str(item.get("tool_id", "") or "").strip(),
                "name": str(item.get("name", "") or "").strip(),
                "confidence": _coerce_confidence(score),
                "reason": reason,
            }
        )
    matches.sort(key=lambda entry: (-float(entry.get("confidence", 0.0) or 0.0), str(entry.get("name", "") or "").casefold()))
    return matches[:8]


def _heuristic_skill_matches(
    query_text: str,
    skills: list[SkillRecord],
) -> list[dict[str, Any]]:
    matches = []
    query_is_btm = _looks_like_btm_text(query_text)
    for skill in list(skills or []):
        score, matched_tokens = _score_overlap(query_text, _skill_search_haystack(skill))
        score += _skill_query_alignment_bonus(skill, query_text)
        if query_is_btm and str(getattr(skill, "skill_type", "") or "").strip() == "quest_tool_specific" and not _skill_looks_like_btm(skill):
            continue
        if score <= 0.0:
            continue
        if score < 0.18 and len(matched_tokens) < 2:
            continue
        reason = "Matched flow/task terms"
        if matched_tokens:
            reason += ": " + ", ".join(matched_tokens[:4])
        matches.append(
            {
                "skill_id": str(getattr(skill, "skill_id", "") or "").strip(),
                "title": str(getattr(skill, "title", "") or "").strip(),
                "skill_type": str(getattr(skill, "skill_type", "") or "").strip(),
                "confidence": _coerce_confidence(score),
                "reason": reason,
            }
        )
    matches.sort(key=lambda entry: (-float(entry.get("confidence", 0.0) or 0.0), str(entry.get("title", "") or "").casefold()))
    return matches[:8]


def _merge_ranked_matches(
    primary_matches: list[dict[str, Any]],
    heuristic_matches: list[dict[str, Any]],
    *,
    id_key: str,
    label_key: str,
) -> list[dict[str, Any]]:
    merged = {}
    order = []
    for source_index, collection in enumerate((primary_matches, heuristic_matches)):
        for item in list(collection or []):
            current = dict(item or {})
            item_id = str(current.get(id_key, "") or "").strip()
            if not item_id:
                continue
            if item_id not in merged:
                merged[item_id] = current
                order.append(item_id)
                continue
            existing = merged[item_id]
            existing_conf = float(existing.get("confidence", 0.0) or 0.0)
            current_conf = float(current.get("confidence", 0.0) or 0.0)
            if current_conf > existing_conf:
                merged[item_id] = {**existing, **current}
            elif current.get("reason") and not existing.get("reason"):
                existing["reason"] = current.get("reason")
    ranked = [merged[item_id] for item_id in order]
    ranked.sort(key=lambda entry: (-float(entry.get("confidence", 0.0) or 0.0), str(entry.get(label_key, "") or "").casefold()))
    return ranked[:8]


def _apply_heuristic_match_floor(
    normalized_result: dict[str, Any],
    *,
    query_text: str,
    tools: list[dict[str, Any]],
    skills: list[SkillRecord],
    task_description: str,
    attached_workflow_jsons: list[dict[str, Any]],
    workspace_relationship_context: dict[str, Any],
) -> dict[str, Any]:
    result = dict(normalized_result or {})
    heuristic_tools = _heuristic_tool_matches(query_text, tools)
    heuristic_skills = _heuristic_skill_matches(query_text, skills)
    result["tool_matches"] = _merge_ranked_matches(
        list(result.get("tool_matches", []) or []),
        heuristic_tools,
        id_key="tool_id",
        label_key="name",
    )
    result["skill_matches"] = _merge_ranked_matches(
        list(result.get("skill_matches", []) or []),
        heuristic_skills,
        id_key="skill_id",
        label_key="title",
    )
    notes = [str(note).strip() for note in list(result.get("notes", []) or []) if str(note).strip()]
    if heuristic_tools and not any("heuristic" in note.casefold() for note in notes):
        top_tool_names = ", ".join(str(item.get("name", "") or "").strip() for item in heuristic_tools[:3] if str(item.get("name", "") or "").strip())
        if top_tool_names:
            notes.append(f"Heuristic tool matching surfaced related QuESt tools: {top_tool_names}.")
    if heuristic_skills and not any("heuristic skill" in note.casefold() for note in notes):
        top_skill_names = ", ".join(str(item.get("title", "") or "").strip() for item in heuristic_skills[:2] if str(item.get("title", "") or "").strip())
        if top_skill_names:
            notes.append(f"Heuristic skill matching surfaced related saved skills: {top_skill_names}.")
    result["notes"] = notes[:8]
    if str(result.get("strategy", "") or "").strip() == "no_viable_quest_solution":
        if result["tool_matches"] and result["skill_matches"]:
            result["strategy"] = "use_general_python_skill_plus_tools"
        elif result["tool_matches"]:
            result["strategy"] = "use_tools_only"
        elif result["skill_matches"]:
            result["strategy"] = "use_quest_skill"
    fallback_fields = _build_task_match_fallback_fields(
        task_description,
        list(attached_workflow_jsons or []),
        dict(workspace_relationship_context or {}),
    )
    has_workflow_context = bool(list(attached_workflow_jsons or [])) or bool(dict(workspace_relationship_context or {}))
    for key, fallback_value in fallback_fields.items():
        if _should_replace_task_match_field(
            key,
            result.get(key, ""),
            fallback_value,
            task_description=task_description,
            has_workflow_context=has_workflow_context,
        ):
            result[key] = fallback_value
    return _prefer_tool_specific_strategy(result)


def _enforce_tool_derived_skill_matches(
    result: dict[str, Any],
    *,
    skills: list[SkillRecord],
    mcp_candidate_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = dict(result or {})
    preferred_tool_ids = {
        _normalized_tool_id(dict(item or {}).get("tool_id", ""))
        for item in list(normalized.get("tool_matches", []) or [])
        if _normalized_tool_id(dict(item or {}).get("tool_id", "")) not in {"", "workspace"}
    }
    candidate_result = dict(mcp_candidate_result or {})
    preferred_tool_ids.update(
        _normalized_tool_id(dict(item or {}).get("tool_id", ""))
        for item in list(candidate_result.get("tool_matches", []) or [])
        if _normalized_tool_id(dict(item or {}).get("tool_id", "")) not in {"", "workspace"}
    )
    if not preferred_tool_ids:
        return normalized
    btm_preferred = "btm" in preferred_tool_ids

    skill_lookup = {
        str(getattr(skill, "skill_id", "") or "").strip(): skill
        for skill in list(skills or [])
        if str(getattr(skill, "skill_id", "") or "").strip()
    }

    def _match_has_tool_overlap(item: dict[str, Any]) -> bool:
        skill_id = str(dict(item or {}).get("skill_id", "") or "").strip()
        skill = skill_lookup.get(skill_id)
        if skill is None:
            return False
        if btm_preferred and str(getattr(skill, "skill_type", "") or "").strip() == "quest_tool_specific" and not _skill_looks_like_btm(skill):
            return False
        return bool(_skill_tool_ids(skill).intersection(preferred_tool_ids))

    filtered_matches = [
        dict(item or {})
        for item in list(normalized.get("skill_matches", []) or [])
        if _match_has_tool_overlap(dict(item or {}))
    ]
    existing_ids = {str(item.get("skill_id", "") or "").strip() for item in filtered_matches}
    for item in list(candidate_result.get("skill_matches", []) or []):
        candidate = dict(item or {})
        skill_id = str(candidate.get("skill_id", "") or "").strip()
        if not skill_id or skill_id in existing_ids:
            continue
        if not _match_has_tool_overlap(candidate):
            continue
        skill = skill_lookup.get(skill_id)
        filtered_matches.append({
            "skill_id": skill_id,
            "title": str(getattr(skill, "title", "") or candidate.get("title", "") or skill_id).strip() if skill is not None else str(candidate.get("title", "") or skill_id).strip(),
            "skill_type": str(getattr(skill, "skill_type", "") or candidate.get("skill_type", "") or "").strip() if skill is not None else str(candidate.get("skill_type", "") or "").strip(),
            "confidence": _coerce_confidence(candidate.get("confidence", candidate.get("score", 0.0))),
            "reason": str(candidate.get("reason", "") or "Matched through MCP tool-derived skill catalog.").strip(),
        })
        existing_ids.add(skill_id)

    filtered_matches.sort(key=lambda item: (-float(item.get("confidence", 0.0) or 0.0), str(item.get("title", "") or "").casefold()))
    normalized["skill_matches"] = filtered_matches[:8]
    if filtered_matches:
        normalized["strategy"] = "use_quest_skill"
    elif normalized.get("tool_matches"):
        normalized["strategy"] = "use_tools_only"
    return normalized


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
    active_tool_ids.add("workspace")
    tool_entries = [_tool_prompt_entry(tool) for tool in tools]
    skill_entries = [_skill_prompt_entry(skill, active_tool_ids) for skill in skills]
    attachment_names = [Path(str(path)).name for path in attached_files]

    system_prompt = (
        "You are QuESt Agent's task matcher. "
        "Your job is to interpret a messy analytics or workflow-building request and recommend only from the provided active QuESt tools and saved skills. "
        "Do not invent tools, skills, or IDs. "
        "If task_description is sparse or empty, infer the current task and related tools/skills from the attached/current flow context. "
        "If Python node wrapper behavior is relevant, treat python_node_wrapper_rules as authoritative workspace constraints. "
        "Analyze the request in this order: task -> tools -> tool-specific skills -> best workflow template. "
        "Match the smallest viable active tool set first, then prefer tool-specific skills that align with those tools, then identify the strongest reusable workflow JSON template when one exists. "
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
    structured_flow_summary = str(result.get("structured_flow_summary", "") or "").strip()
    validation_summary = str(result.get("validation_summary", "") or "").strip()
    validation_report = dict(result.get("validation_report", {}) or {})
    missing_parts = [
        str(item).strip()
        for item in list(result.get("missing_parts", validation_report.get("missing_parts", [])) or [])[:8]
        if str(item).strip()
    ]
    notes = [str(note).strip() for note in list(result.get("notes", []) or [])[:6] if str(note).strip()]
    best_workflow_template = dict(result.get("best_workflow_template", {}) or {})
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
    if missing_parts:
        planning_directives.append(
            "Treat missing_parts as the highest-priority build targets for the next plan."
        )
        planning_directives.append(
            "Prefer actions that resolve the listed missing_parts before optional cleanup or improvements."
        )
    if best_workflow_template:
        planning_directives.append(
            "A best reusable workflow template is available; prefer JSON diff/edit -> load -> validate over rebuilding the flow from scratch."
        )
    if validation_report:
        planning_directives.append(
            "Treat validation_report as the deterministic source of truth for structural flow facts."
        )

    return {
        "strategy": str(result.get("strategy", "") or "").strip(),
        "task": str(result.get("task", "") or "").strip(),
        "project_description": str(result.get("project_description", "") or "").strip(),
        "flow_description": flow_description,
        "structured_flow_summary": structured_flow_summary,
        "validation_summary": validation_summary,
        "validation_report": validation_report,
        "top_tool_matches": top_tool_matches,
        "top_skill_matches": top_skill_matches,
        "best_workflow_template": best_workflow_template,
        "analysis_pipeline": [
            "task",
            "tools",
            "tool_specific_skills",
            "best_workflow_template",
        ],
        "action_pipeline": [
            "json_diff_edit",
            "load",
            "validate",
        ],
        "missing_parts": missing_parts,
        "notes": notes,
        "planning_directives": planning_directives,
    }


def _parse_json_response(content: str, empty_message: str, invalid_message: str) -> dict[str, Any]:
    if not content:
        raise RuntimeError(empty_message)
    cleaned = str(content or "").strip()
    candidates = [cleaned]
    if cleaned.startswith("```"):
        fence_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.IGNORECASE | re.DOTALL)
        if fence_match:
            fenced = str(fence_match.group(1) or "").strip()
            if fenced:
                candidates.append(fenced)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            pass
        else:
            if isinstance(parsed, dict):
                return parsed
    for candidate in candidates:
        for match in re.finditer(r"\{", candidate):
            try:
                parsed, end_index = decoder.raw_decode(candidate[match.start():])
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(invalid_message) from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(invalid_message)
    return parsed


def _retry_local_json_response(
    messages: list[dict[str, Any]],
    *,
    selected_model: str | None = None,
    temperature: float = 0,
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
        temperature=temperature,
        api_key=api_key,
        response_json=True,
    )
    return _parse_json_response(
        retry_content,
        "The local model returned an empty retry response.",
        "The local model retry response was not valid JSON.",
    )


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

    if _fast_local_mode_enabled(selected_model):
        grounding_payload = _build_fast_local_grounding_payload(
            user_prompt,
            task_match_result,
            pinned_context,
            attached_files,
            attached_workflow_jsons,
            workspace_relationship_context,
            implicit_code_context,
            python_node_wrapper_rules,
            skill_execution_recipes,
            recent_messages,
        )
    else:
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

    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(grounding_payload, ensure_ascii=True, indent=2)},
    ]
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0.4,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "OpenAI returned an empty grounded chat reply.",
            "OpenAI grounded chat reply was not valid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0.4,
            api_key=api_key,
        )
    reply = str(parsed.get("reply", "") or "").strip()
    if not reply:
        raise RuntimeError("OpenAI grounded chat reply was missing the reply field.")
    return {
        "reply": reply,
        "model_used_note": _build_model_used_note(
            selected_model,
            selected_reasoning_model,
            resolved_model_name,
        ),
    }


def run_semantic_flow_validation(
    task_text: str,
    structured_flow_analysis: dict[str, Any] | None = None,
    validation_report: dict[str, Any] | None = None,
    task_match_result: dict[str, Any] | None = None,
    selected_model: str | None = None,
    recent_messages: list[dict[str, Any]] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    system_prompt = (
        "You are QuESt Agent's semantic flow validator. "
        "MCP has already provided deterministic canvas facts and structural validation. "
        "Your job is only to decide whether the current flow semantically satisfies the user's task. "
        "Use the MCP facts as ground truth. Do not invent canvas nodes, ports, or connections. "
        "If the task requires more inputs, outputs, operations, or a different formula than the current flow provides, list the missing or conflicting parts. "
        "If the current flow satisfies the task, return no missing parts. "
        "Return valid JSON only with this shape: "
        "{\"task_alignment\": \"aligned\" | \"partial\" | \"not_aligned\" | \"ambiguous\", "
        "\"missing_parts\": [string], "
        "\"unexpected_parts\": [string], "
        "\"notes\": [string]}."
    )
    payload = {
        "task_text": str(task_text or "").strip(),
        "mcp_structured_flow_analysis": dict(structured_flow_analysis or {}),
        "mcp_structural_validation": dict(validation_report or {}),
        "mcp_task_and_skill_context": {
            "project_description": str(dict(task_match_result or {}).get("project_description", "") or ""),
            "task": str(dict(task_match_result or {}).get("task", "") or ""),
            "tool_matches": list(dict(task_match_result or {}).get("tool_matches", []) or [])[:5],
            "skill_matches": list(dict(task_match_result or {}).get("skill_matches", []) or [])[:5],
            "best_workflow_template": dict(dict(task_match_result or {}).get("best_workflow_template", {}) or {}),
        },
        "recent_conversation": _recent_conversation(recent_messages),
    }
    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "OpenAI returned an empty semantic flow validation response.",
            "OpenAI semantic flow validation response was not valid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    alignment = str(parsed.get("task_alignment", "") or "").strip()
    if alignment not in {"aligned", "partial", "not_aligned", "ambiguous"}:
        alignment = "ambiguous"
    return {
        "task_alignment": alignment,
        "missing_parts": [
            str(item).strip()
            for item in list(parsed.get("missing_parts", []) or [])
            if str(item).strip()
        ],
        "unexpected_parts": [
            str(item).strip()
            for item in list(parsed.get("unexpected_parts", []) or [])
            if str(item).strip()
        ],
        "notes": [
            str(item).strip()
            for item in list(parsed.get("notes", []) or [])
            if str(item).strip()
        ],
        "model_used_note": _build_model_used_note(
            selected_model,
            selected_reasoning_model,
            resolved_model_name,
        ),
        "source": "llm_semantic_flow_validation",
    }


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
        "When you choose 'analyze_task', the intended analysis pipeline is: task -> tools -> tool-specific skills -> best workflow template. "
        "Choose 'execute_canvas_action' when the user is clearly asking QuESt Agent to create, rename, edit, or delete workflow items on the canvas. "
        "When you choose 'execute_canvas_action', prefer an action-planning mindset of: JSON diff/edit -> load -> validate when a reusable workflow template is available. "
        "Choose 'answer_only' when the user is asking a follow-up question, asking for explanation, asking about the current recommendations, or making a conversational request that can be answered from the current context. "
        "Return valid JSON only with this shape: "
        "{\"action\": \"analyze_task\" | \"execute_canvas_action\" | \"answer_only\", \"reason\": string, \"task_focus\": string}."
    )

    if _fast_local_mode_enabled(selected_model):
        payload = _build_fast_local_router_payload(
            user_prompt,
            task_match_result,
            pinned_context,
            attached_files,
            attached_workflow_jsons,
            workspace_relationship_context,
            implicit_code_context,
            python_node_wrapper_rules,
            skill_execution_recipes,
            recent_messages,
        )
    else:
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

    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "OpenAI returned an empty chat router response.",
            "OpenAI chat router response was not valid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    action = str(parsed.get("action", "") or "").strip()
    if action not in {"analyze_task", "execute_canvas_action", "answer_only"}:
        action = "analyze_task" if not task_match_result else "answer_only"
    return {
        "action": action,
        "reason": str(parsed.get("reason", "") or "").strip(),
        "task_focus": str(parsed.get("task_focus", "") or "").strip(),
        "model_used_note": _build_model_used_note(
            selected_model,
            selected_reasoning_model,
            resolved_model_name,
        ),
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


def _request_prefers_template_json_edit(
    user_prompt: str,
    canvas_context: dict[str, Any] | None = None,
) -> bool:
    lowered = str(user_prompt or "").strip().casefold()
    canvas_context = dict(canvas_context or {})
    node_count = len(list(canvas_context.get("nodes", []) or []))
    explicit_template_tokens = (
        "matched skill",
        "reuse skill",
        "reuse template",
        "load template",
        "start from template",
        "start from the template",
        "use the template",
        "example json",
        "workflow json",
        "load the example",
        "load the matched skill",
    )
    touchup_tokens = (
        "add",
        "connect",
        "wire",
        "rename",
        "update",
        "change",
        "set",
        "edit",
        "remove",
        "delete",
        "fix",
        "repair",
        "complete",
        "finish",
        "adjust",
    )
    if any(token in lowered for token in explicit_template_tokens):
        return True
    if node_count > 0 and any(token in lowered for token in touchup_tokens):
        return False
    return node_count <= 0


def _current_workflow_json_entry(
    attached_workflow_jsons: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    for item in list(attached_workflow_jsons or []):
        entry = dict(item or {})
        file_label = str(entry.get("file", "") or "").strip().casefold()
        if "(current canvas)" in file_label:
            return entry
    for item in list(attached_workflow_jsons or []):
        entry = dict(item or {})
        if isinstance(entry.get("content"), dict):
            return entry
    return {}


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
        "delete": "delete_node",
        "remove": "delete_node",
        "delete_node": "delete_node",
        "remove_node": "delete_node",
        "delete_data_node": "delete_node",
        "remove_data_node": "delete_node",
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
        "backnode": "text",
        "back_node": "text",
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


SKILL_TEMPLATE_REUSE_CONFIDENCE = 0.8


def _numberish_tokens(text: str) -> list[str]:
    if not str(text or "").strip():
        return []
    pattern = (
        r"\b(?:\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b"
    )
    return [match.group(0).casefold() for match in re.finditer(pattern, str(text or "").casefold())]


def _matching_skill_recipe(skill_execution_recipes: dict[str, Any] | None, skill_id: str) -> dict[str, Any]:
    target = str(skill_id or "").strip()
    if not target:
        return {}
    for recipe in list(dict(skill_execution_recipes or {}).get("recipes", []) or []):
        recipe = dict(recipe or {})
        if str(recipe.get("skill_id", "") or "").strip() == target:
            return recipe
    return {}


def _template_reference_text(best_workflow_template: dict[str, Any], skill_execution_recipes: dict[str, Any] | None) -> str:
    template = dict(best_workflow_template or {})
    recipe = _matching_skill_recipe(skill_execution_recipes, str(template.get("skill_id", "") or "").strip())
    parts = [
        str(template.get("title", "") or "").strip(),
        str(template.get("summary", "") or "").strip(),
        str(template.get("reason", "") or "").strip(),
        str(template.get("selection_reason", "") or "").strip(),
        str(recipe.get("title", "") or "").strip(),
        str(recipe.get("summary", "") or "").strip(),
        str(recipe.get("workflow_strategy", "") or "").strip(),
    ]
    for step in list(recipe.get("step_summary", []) or []):
        parts.append(str(step or "").strip())
    for item in list(recipe.get("expected_inputs", []) or []):
        if isinstance(item, dict):
            parts.extend(
                [
                    str(item.get("name", "") or "").strip(),
                    str(item.get("description", "") or "").strip(),
                ]
            )
    for item in list(recipe.get("expected_outputs", []) or []):
        if isinstance(item, dict):
            parts.extend(
                [
                    str(item.get("name", "") or "").strip(),
                    str(item.get("description", "") or "").strip(),
                ]
            )
    return "\n".join(part for part in parts if part).casefold()


def _detect_template_diff_request(
    user_prompt: str,
    best_workflow_template: dict[str, Any] | None,
    skill_execution_recipes: dict[str, Any] | None,
) -> dict[str, Any]:
    lowered = str(user_prompt or "").strip().casefold()
    if not lowered:
        return {"has_diff": False, "reasons": []}

    reasons = []
    modifier_patterns = (
        r"\b(change|modify|revise|adapt|adjust|update|rename|replace|remove|delete|split|convert)\b",
        r"\b(instead|rather than|except|but use|but make|but with)\b",
        r"\b(additional|another|extra)\b",
        r"\b(initialize|set)\b.{0,24}\bto\b",
        r"\beach function in (?:its|one) python node\b",
        r"\buse separate\b",
        r"\bfrom\b.{0,24}\bto\b",
    )
    for pattern in modifier_patterns:
        if re.search(pattern, lowered):
            reasons.append(f"Prompt contains explicit modification signal: {pattern}")

    prompt_number_tokens = _numberish_tokens(lowered)
    template_text = _template_reference_text(dict(best_workflow_template or {}), skill_execution_recipes)
    if prompt_number_tokens and template_text:
        missing_numbers = [token for token in prompt_number_tokens if token not in template_text]
        if missing_numbers:
            reasons.append(
                "Prompt mentions numeric requirements not present in the matched skill template: "
                + ", ".join(sorted(set(missing_numbers)))
            )

    return {
        "has_diff": bool(reasons),
        "reasons": reasons[:6],
    }


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
    current_flow_present = node_count > 0
    missing_parts = [
        str(item or "").strip()
        for item in list(task_match_result.get("missing_parts", []) or [])
        if str(item or "").strip()
    ]
    missing_text = "\n".join(missing_parts).casefold()
    best_workflow_template = dict(task_match_result.get("best_workflow_template", {}) or {})
    matched_skill_ids = {
        str(dict(item or {}).get("skill_id", "") or "").strip()
        for item in list(task_match_result.get("skill_matches", []) or [])
        if str(dict(item or {}).get("skill_id", "") or "").strip()
    }
    if best_workflow_template:
        best_template_skill_id = str(best_workflow_template.get("skill_id", "") or "").strip()
        if not matched_skill_ids or best_template_skill_id not in matched_skill_ids:
            best_workflow_template = {}
    recipe_entries = [
        dict(item or {})
        for item in list(skill_execution_recipes.get("recipes", []) or [])
        if isinstance(item, dict)
    ]
    preferred_tool_ids = {
        _normalized_tool_id(dict(item or {}).get("tool_id", ""))
        for item in list(task_match_result.get("tool_matches", []) or [])
        if _normalized_tool_id(dict(item or {}).get("tool_id", ""))
    }
    non_workspace_tool_ids = {tool_id for tool_id in preferred_tool_ids if tool_id != "workspace"}
    reusable_templates = []
    for recipe in recipe_entries:
        recipe_skill_id = str(recipe.get("skill_id", "") or "").strip()
        if not matched_skill_ids or recipe_skill_id not in matched_skill_ids:
            continue
        workflow_template = dict(recipe.get("workflow_template", {}) or {})
        workflow_path = str(workflow_template.get("path", "") or "").strip()
        confidence = _coerce_confidence(recipe.get("confidence", 0.0))
        recipe_tool_ids = {
            _normalized_tool_id(value)
            for value in (
                list(recipe.get("recommended_tools", []) or [])
                + list(recipe.get("required_tools", []) or [])
                + list(recipe.get("tool_tags", []) or [])
                + list(dict(recipe.get("edit_recipe", {}) or {}).get("required_tools", []) or [])
            )
            if _normalized_tool_id(value)
        }
        if non_workspace_tool_ids and not (recipe_tool_ids & non_workspace_tool_ids):
            continue
        if workflow_path and confidence > SKILL_TEMPLATE_REUSE_CONFIDENCE:
            reusable_templates.append(
                {
                    "skill_id": recipe_skill_id,
                    "title": str(recipe.get("title", "") or "").strip(),
                    "confidence": confidence,
                    "workflow_path": workflow_path,
                    "summary": str(recipe.get("summary", "") or "").strip(),
                }
            )

    available_paths = [
        {
            "path_id": "current_flow_json_patch_then_load",
            "label": "Patch the current flow JSON, then reload it",
            "difficulty": "low",
            "best_when": "The current canvas already contains the right baseline structure and the next step is to fix or complete missing parts deterministically through JSON edits.",
        },
        {
            "path_id": "template_json_edit_then_load",
            "label": "Edit the best matched workflow template JSON, then load it",
            "difficulty": "low",
            "best_when": "A strong matched skill already includes a reusable workflow JSON template that should be adapted to the requested task before loading.",
        },
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
    if current_flow_present:
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
        for item in available_paths:
            if item.get("path_id") == "template_json_edit_then_load":
                item["candidate_skills"] = reusable_templates[:3]
                item["best_when"] = (
                    "A strong matched skill already includes a reusable workflow JSON template; "
                    "validate and adapt that JSON with MCP facts plus LLM review before loading it."
                )
                break

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
    touchup_request = current_flow_present and any(
        token in lowered
        for token in (
            "add",
            "connect",
            "wire",
            "rename",
            "update",
            "change",
            "set",
            "edit",
            "remove",
            "delete",
            "fix",
            "repair",
            "complete",
            "finish",
            "adjust",
        )
    )
    edit_current = (
        current_flow_present
        and any(
            token in lowered
            for token in ("edit", "revise", "change", "modify", "fix", "repair", "complete", "finish", "adapt", "add", "connect", "wire", "rename", "update", "set", "remove", "delete")
        )
    )
    exact_match_confidence = _coerce_confidence(best_workflow_template.get("confidence", 0.0))
    diff_detection = _detect_template_diff_request(user_prompt, best_workflow_template, skill_execution_recipes)
    exact_match_lock = (
        bool(best_workflow_template)
        and not current_flow_present
        and exact_match_confidence > SKILL_TEMPLATE_REUSE_CONFIDENCE
        and not diff_detection.get("has_diff", False)
        and not missing_parts
    )
    create_flow_request = any(
        token in lowered
        for token in (
            "create a flow",
            "create workflow",
            "build a flow",
            "build workflow",
            "make a flow",
            "make workflow",
        )
    )
    significant_change = (
        len(missing_parts) >= 5
        or any(
            token in missing_text or token in lowered
            for token in (
                "subflow",
                "sub-flow",
                "large",
                "many",
                "multiple nodes",
                "replace the flow",
                "rebuild",
                "workflow json",
                "template json",
                "load workflow",
            )
        )
    )

    if exact_match_lock:
        recommended_path = "template_json_edit_then_load"
        reason = (
            f"Matched skill template '{str(best_workflow_template.get('title', '') or '').strip()}' scored higher than 0.8, "
            "the canvas is empty, and no explicit differences were requested; validate and compile an adapted workflow_content copy before loading."
        ).strip()
    elif explicit_json:
        recommended_path = "draft_workflow_json_then_load"
        reason = "The request explicitly points to direct workflow JSON authoring."
    elif current_flow_present and missing_parts and significant_change:
        recommended_path = "current_flow_json_patch_then_load"
        reason = "The current canvas exists and analysis found larger structural gaps, so patching the current flow JSON and reloading it is the safest repair path."
    elif current_flow_present and missing_parts:
        recommended_path = "edit_current_flow"
        reason = "The current canvas exists and analysis found a small number of missing parts, so direct Workspace edits are the simplest repair path."
    elif edit_current:
        recommended_path = "edit_current_flow"
        reason = "The current canvas already has relevant structure, so editing the existing flow is easier than rebuilding."
    elif node_count <= 0 and reusable_templates and create_flow_request:
        recommended_path = "template_json_edit_then_load"
        reason = "The canvas is empty, the user is creating a flow, and a matched skill template scored higher than 0.8, so adapting the template is the preferred starting path."
    elif reusable_templates and _request_prefers_template_json_edit(user_prompt, canvas_context):
        recommended_path = "template_json_edit_then_load"
        reason = "A matched skill template scored higher than 0.8, so the easiest path is usually to edit that JSON baseline, load it, and then validate the result."
    elif touchup_request:
        recommended_path = "edit_current_flow"
        reason = "The request looks like a touch-up on the current flow, so direct canvas edits are the simpler path."
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
        "exact_match_lock": False,
        "explicit_diff_detected": bool(diff_detection.get("has_diff", False)),
        "diff_reasons": list(diff_detection.get("reasons", []) or []),
    }


def _sanitize_template_candidates(
    task_match_result: dict[str, Any] | None,
    skill_execution_recipes: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    task_match_result = dict(task_match_result or {})
    skill_execution_recipes = dict(skill_execution_recipes or {})
    matched_skill_ids = {
        str(dict(item or {}).get("skill_id", "") or "").strip()
        for item in list(task_match_result.get("skill_matches", []) or [])
        if str(dict(item or {}).get("skill_id", "") or "").strip()
    }
    if not matched_skill_ids:
        task_match_result["best_workflow_template"] = {}
        skill_execution_recipes["recipes"] = []
        skill_execution_recipes["available"] = False
        return task_match_result, skill_execution_recipes
    preferred_tool_ids = {
        _normalized_tool_id(dict(item or {}).get("tool_id", ""))
        for item in list(task_match_result.get("tool_matches", []) or [])
        if _normalized_tool_id(dict(item or {}).get("tool_id", ""))
    }
    non_workspace_tool_ids = {tool_id for tool_id in preferred_tool_ids if tool_id != "workspace"}

    sanitized_recipes = []
    for recipe in list(skill_execution_recipes.get("recipes", []) or []):
        recipe = dict(recipe or {})
        recipe_skill_id = str(recipe.get("skill_id", "") or "").strip()
        if recipe_skill_id not in matched_skill_ids:
            continue
        recipe_tool_ids = {
            _normalized_tool_id(value)
            for value in (
                list(recipe.get("recommended_tools", []) or [])
                + list(recipe.get("required_tools", []) or [])
                + list(recipe.get("tool_tags", []) or [])
                + list(dict(recipe.get("edit_recipe", {}) or {}).get("required_tools", []) or [])
            )
            if _normalized_tool_id(value)
        }
        if non_workspace_tool_ids and not (recipe_tool_ids & non_workspace_tool_ids):
            continue
        sanitized_recipes.append(recipe)

    best_workflow_template = dict(task_match_result.get("best_workflow_template", {}) or {})
    if best_workflow_template:
        best_skill_id = str(best_workflow_template.get("skill_id", "") or "").strip()
        best_allowed_by_match = best_skill_id in matched_skill_ids
        best_allowed_by_recipe = any(
            str(dict(recipe or {}).get("skill_id", "") or "").strip() == best_skill_id
            for recipe in sanitized_recipes
        )
        if not best_allowed_by_match or not best_allowed_by_recipe:
            task_match_result["best_workflow_template"] = {}

    skill_execution_recipes["recipes"] = sanitized_recipes
    skill_execution_recipes["available"] = bool(sanitized_recipes)
    return task_match_result, skill_execution_recipes


def _canvas_node_name_lookup(canvas_context: dict[str, Any]) -> dict[str, str]:
    lookup = {}
    for item in list(dict(canvas_context or {}).get("nodes", []) or []):
        name = str(dict(item or {}).get("name", "") or "").strip()
        if name:
            lookup[name.casefold()] = name
    return lookup


def _canvas_node_type_lookup(canvas_context: dict[str, Any]) -> dict[str, str]:
    lookup = {}
    for item in list(dict(canvas_context or {}).get("nodes", []) or []):
        node = dict(item or {})
        name = str(node.get("name", "") or "").strip()
        if not name:
            continue
        node_type = _normalize_workspace_node_type(str(node.get("node_type", "") or node.get("type", "") or ""))
        if node_type in CANONICAL_NODE_TYPES:
            lookup[name.casefold()] = node_type
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


def _resolve_canvas_node_type(node_name: str, canvas_context: dict[str, Any]) -> str:
    resolved_name = _resolve_canvas_node_name(node_name, canvas_context)
    if not resolved_name:
        return ""
    return _canvas_node_type_lookup(canvas_context).get(resolved_name.casefold(), "")


def _extract_candidate_actions(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("actions", "action_list", "operations", "steps"):
        value = parsed.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    single = parsed.get("action")
    if isinstance(single, dict):
        return [single]
    return []


def _workspace_operation_to_action_item(item: dict[str, Any]) -> dict[str, Any]:
    operation_id = str(dict(item or {}).get("operation", "") or "").strip()
    if not operation_id:
        return dict(item or {})
    arguments = dict(dict(item or {}).get("arguments", {}) or {}) if isinstance(dict(item or {}).get("arguments", {}), dict) else {}
    action = dict(arguments)
    operation_map = {
        "workspace.add_subflow": "add_subflow",
        "workspace.connect_nodes": "connect_nodes",
        "workspace.connect_ports": "connect_nodes",
        "workspace.create_node": "create_node",
        "workspace.create_data_node": "create_node",
        "workspace.create_python_node": "create_node",
        "workspace.create_text_node": "create_node",
        "workspace.delete_node": "delete_node",
        "workspace.delete_selected_nodes": "delete_selected_nodes",
        "workspace.load_template": "load_workflow_json",
        "workspace.load_workflow_json": "load_workflow_json",
        "workspace.rename_selected_node": "rename_selected_node",
        "workspace.update_node": "update_node",
        "workspace.update_data_node": "update_node",
        "workspace.update_python_node": "update_node",
        "workspace.update_text_node": "update_node",
        "workspace.update_selected_text_node": "update_selected_text_node",
        "workspace.validate_flow": "validate_flow",
    }
    action["type"] = operation_map.get(operation_id, operation_id)
    if operation_id == "workspace.create_data_node":
        action.setdefault("node_type", "data")
    elif operation_id == "workspace.create_python_node":
        action.setdefault("node_type", "py")
    elif operation_id == "workspace.create_text_node":
        action.setdefault("node_type", "text")
    elif operation_id == "workspace.update_data_node":
        action.setdefault("node_type", "data")
    elif operation_id == "workspace.update_python_node":
        action.setdefault("node_type", "py")
    return action


def _workspace_operation_id_for_action(action: dict[str, Any]) -> str:
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


def _normalize_workspace_action_plan(
    parsed: dict[str, Any],
    canvas_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    canvas_context = dict(canvas_context or {})
    selected_count = int(canvas_context.get("selected_node_count", 0) or 0)
    normalized_actions = []
    dropped = []

    for item in _extract_candidate_actions(parsed):
        item = _workspace_operation_to_action_item(item)
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
            actual_node_type = _resolve_canvas_node_type(node_name, canvas_context)
            if node_type in CANONICAL_NODE_TYPES and actual_node_type and node_type != actual_node_type:
                dropped.append(f"Corrected update_node `{node_name}` type from {node_type} to {actual_node_type} based on canvas context.")
                node_type = actual_node_type
            elif node_type not in CANONICAL_NODE_TYPES and actual_node_type:
                node_type = actual_node_type
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
            if node_type == "text" and "text" not in normalized and "value" in normalized:
                normalized["text"] = str(normalized.pop("value", "") or "")
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
        elif action_type == "delete_node":
            node_name = _resolve_canvas_node_name(
                item.get("node_name", "") or item.get("name", "") or item.get("target_node", "") or item.get("target_name", ""),
                canvas_context,
            )
            if not node_name:
                dropped.append("delete_node was missing node_name.")
                continue
            normalized["node_name"] = node_name
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

    normalized_operations = []
    for action in normalized_actions[:5]:
        operation_id = _workspace_operation_id_for_action(action)
        arguments = {
            key: value
            for key, value in dict(action or {}).items()
            if key != "type"
        }
        if operation_id:
            normalized_operations.append({"operation": operation_id, "arguments": arguments})

    return {
        "reply": str(parsed.get("reply", "") or "").strip(),
        "planning_path": str(parsed.get("planning_path", "") or parsed.get("build_path", "") or "").strip(),
        "path_reason": str(parsed.get("path_reason", "") or parsed.get("build_path_reason", "") or "").strip(),
        "actions": normalized_actions[:5],
        "operations": normalized_operations,
        "dropped_actions": dropped[:10],
    }


def _default_flow_layout_type(node_type: str) -> str:
    mapping = {
        "data_node": "QuESt.Workspace.DataNode",
        "python_node": "QuESt.Workspace.PyNode",
        "back_node": "QuESt.Workspace.BackNode",
    }
    return mapping.get(str(node_type or "").strip(), "QuESt.Workspace.DataNode")


def _default_layout_entry(node_type: str, node_name: str, pos: list[float] | None = None) -> dict[str, Any]:
    position = list(pos or [100.0, 100.0])
    base = {
        "type_": _default_flow_layout_type(node_type),
        "icon": None,
        "name": str(node_name or "").strip(),
        "color": [255, 255, 255],
        "border_color": [74, 84, 85, 255],
        "text_color": [0, 0, 0],
        "disabled": False,
        "selected": False,
        "visible": True,
        "width": 180,
        "height": 80,
        "pos": position,
        "layout_direction": 0,
        "port_deletion_allowed": True,
        "subgraph_session": {},
    }
    if node_type == "back_node":
        base["type_"] = "QuESt.Workspace.BackNode"
        base["color"] = [255, 255, 155]
        base["width"] = 260.0
        base["height"] = 106.0
        base["port_deletion_allowed"] = False
        base["custom"] = {"backdrop_text": ""}
    else:
        base["input_ports"] = []
        base["output_ports"] = []
        if node_type == "data_node":
            base["custom"] = {"Text Caption": ""}
    return base


def _new_flow_node_id(existing_ids: set[str]) -> str:
    while True:
        candidate = "0x" + uuid.uuid4().hex[:12]
        if candidate not in existing_ids:
            existing_ids.add(candidate)
            return candidate


def _coerce_bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().casefold()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return None


def _template_port_entry(name: str, *, multi_connection: bool) -> dict[str, Any]:
    return {
        "name": str(name or "").strip(),
        "multi_connection": bool(multi_connection),
        "display_name": True,
    }


def _update_data_node_ports(node_row: dict[str, Any], layout_entry: dict[str, Any]) -> None:
    variable_name = str(node_row.get("node_input_variable", "") or "").strip()
    value_display = bool(node_row.get("node_value_display", False))
    node_value = str(node_row.get("node_input_value", "") or "")
    if variable_name:
        layout_entry["output_ports"] = [_template_port_entry(variable_name, multi_connection=True)]
    else:
        layout_entry["output_ports"] = []
    layout_entry["input_ports"] = []
    custom = dict(layout_entry.get("custom", {}) or {})
    custom["Text Caption"] = node_value if value_display else ""
    layout_entry["custom"] = custom


def _update_python_node_ports(node_row: dict[str, Any], layout_entry: dict[str, Any]) -> None:
    wrapper_text = str(node_row.get("node_function_wrapper", "") or "").strip()
    input_ports, output_ports = _infer_python_ports_from_wrapper(wrapper_text)
    layout_entry["input_ports"] = [_template_port_entry(name, multi_connection=False) for name in input_ports]
    layout_entry["output_ports"] = [_template_port_entry(name, multi_connection=True) for name in output_ports]


def _update_text_node_layout(node_row: dict[str, Any], layout_entry: dict[str, Any]) -> None:
    custom = dict(layout_entry.get("custom", {}) or {})
    custom["backdrop_text"] = str(node_row.get("node_input_value", "") or "")
    layout_entry["custom"] = custom


def _node_position(layout_entry: dict[str, Any]) -> list[float]:
    pos = list(dict(layout_entry or {}).get("pos", []) or [])
    if len(pos) >= 2:
        try:
            return [float(pos[0]), float(pos[1])]
        except Exception:
            return [100.0, 100.0]
    return [100.0, 100.0]


def _next_added_node_position(flow_layout_nodes: dict[str, Any], node_type: str) -> list[float]:
    positions = []
    for entry in list(dict(flow_layout_nodes or {}).values()):
        item = dict(entry or {})
        if str(item.get("type_", "") or "").strip() == _default_flow_layout_type(node_type):
            positions.append(_node_position(item))
    if positions:
        positions.sort(key=lambda item: (item[0], item[1]))
        last = positions[-1]
        return [last[0] + 220.0, last[1] + 120.0]
    return [100.0, 100.0]


def _resolve_template_node_reference(
    node_name: str,
    nodes_by_name: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    requested = str(node_name or "").strip()
    if not requested:
        return None
    exact = nodes_by_name.get(requested.casefold())
    if exact is not None:
        return exact
    matches = [item for key, item in nodes_by_name.items() if requested.casefold() in key]
    if len(matches) == 1:
        return matches[0]
    return None


def _rebuild_inputs_df_from_nodes(flow_json_data: dict[str, Any]) -> None:
    nodes = [dict(item or {}) for item in list(flow_json_data.get("nodes_df", []) or [])]
    inputs = []
    for row in nodes:
        if str(row.get("node_type", "") or "").strip() != "data_node":
            continue
        inputs.append(
            {
                "node_id": str(row.get("node_id", "") or "").strip(),
                "node_name": str(row.get("node_name", "") or "").strip(),
                "variable_name": str(row.get("node_input_variable", "") or "").strip(),
                "value": str(row.get("node_input_value", "") or ""),
                "is_path": bool(row.get("node_is_path", False)),
                "is_from_master": bool(row.get("node_is_from_master", False)),
            }
        )
    flow_json_data["inputs_df"] = [{"name": "Base Case", "inputs": inputs}]


def _remap_data_node_connection_ports(
    connection_rows: list[dict[str, Any]],
    *,
    node_id: str,
    old_port: str,
    new_port: str,
) -> None:
    old_port_text = str(old_port or "").strip()
    new_port_text = str(new_port or "").strip()
    node_id_text = str(node_id or "").strip()
    if not node_id_text or old_port_text == new_port_text or not new_port_text:
        return
    for row in list(connection_rows or []):
        if str(dict(row or {}).get("from_node", "") or "").strip() != node_id_text:
            continue
        mapping = dict(dict(row or {}).get("mapping", {}) or {}) if isinstance(dict(row or {}).get("mapping"), dict) else {}
        if old_port_text in mapping:
            target_port = mapping.pop(old_port_text)
            mapping[new_port_text] = target_port
            row["mapping"] = mapping


def _remap_python_node_connection_ports(
    connection_rows: list[dict[str, Any]],
    *,
    node_id: str,
    old_inputs: list[str],
    new_inputs: list[str],
    old_outputs: list[str],
    new_outputs: list[str],
) -> None:
    node_id_text = str(node_id or "").strip()
    if not node_id_text:
        return
    input_port_map = {}
    output_port_map = {}
    if list(old_inputs or []) and list(new_inputs or []) and len(list(old_inputs or [])) == len(list(new_inputs or [])):
        input_port_map = {
            str(old_inputs[index] or "").strip(): str(new_inputs[index] or "").strip()
            for index in range(len(list(old_inputs or [])))
            if str(old_inputs[index] or "").strip() and str(new_inputs[index] or "").strip()
        }
    if list(old_outputs or []) and list(new_outputs or []) and len(list(old_outputs or [])) == len(list(new_outputs or [])):
        output_port_map = {
            str(old_outputs[index] or "").strip(): str(new_outputs[index] or "").strip()
            for index in range(len(list(old_outputs or [])))
            if str(old_outputs[index] or "").strip() and str(new_outputs[index] or "").strip()
        }
    for row in list(connection_rows or []):
        mapping = dict(dict(row or {}).get("mapping", {}) or {}) if isinstance(dict(row or {}).get("mapping"), dict) else {}
        if str(dict(row or {}).get("to_node", "") or "").strip() == node_id_text and input_port_map:
            rewritten = {}
            for source_port, target_port in mapping.items():
                target_text = str(target_port or "").strip()
                rewritten[str(source_port or "").strip()] = input_port_map.get(target_text, target_text)
            row["mapping"] = rewritten
        if str(dict(row or {}).get("from_node", "") or "").strip() == node_id_text and output_port_map:
            rewritten = {}
            for source_port, target_port in mapping.items():
                source_text = str(source_port or "").strip()
                rewritten[output_port_map.get(source_text, source_text)] = str(target_port or "").strip()
            row["mapping"] = rewritten


def _template_edits_has_changes(template_edits: dict[str, Any] | None) -> bool:
    edits = dict(template_edits or {})
    if str(edits.get("set_flow_name", "") or "").strip():
        return True
    for key in (
        "text_node_updates",
        "data_node_updates",
        "python_node_updates",
        "node_removals",
        "node_additions",
        "connections_to_add",
        "connections_to_remove",
    ):
        if list(edits.get(key, []) or []):
            return True
    return False


def _compile_template_edit_plan(
    template_flow_json: dict[str, Any],
    template_edits: dict[str, Any] | None,
) -> dict[str, Any]:
    flow_json = copy.deepcopy(dict(template_flow_json or {}))
    edits = dict(template_edits or {})
    flow_json.setdefault("nodes_df", [])
    flow_json.setdefault("connections_df", [])
    flow_json.setdefault("flow_layout", {})
    flow_json["flow_layout"].setdefault("nodes", {})
    flow_json["flow_layout"].setdefault("connections", [])

    if str(edits.get("set_flow_name", "") or "").strip():
        flow_json["flow_name"] = str(edits.get("set_flow_name", "") or "").strip()

    node_rows = [dict(item or {}) for item in list(flow_json.get("nodes_df", []) or [])]
    flow_layout_nodes = dict(flow_json.get("flow_layout", {}).get("nodes", {}) or {})
    existing_ids = {str(item.get("node_id", "") or "").strip() for item in node_rows if str(item.get("node_id", "") or "").strip()}

    nodes_by_name = {
        str(row.get("node_name", "") or "").strip().casefold(): row
        for row in node_rows
        if str(row.get("node_name", "") or "").strip()
    }

    removal_names = {
        str(item.get("node_name", "") or item.get("name", "") or "").strip().casefold()
        for item in list(edits.get("node_removals", []) or [])
        if str(item.get("node_name", "") or item.get("name", "") or "").strip()
    }
    removed_node_ids = {
        str(row.get("node_id", "") or "").strip()
        for row in node_rows
        if str(row.get("node_name", "") or "").strip().casefold() in removal_names
        and str(row.get("node_id", "") or "").strip()
    }
    if removed_node_ids:
        node_rows = [
            row for row in node_rows
            if str(row.get("node_id", "") or "").strip() not in removed_node_ids
        ]
        for node_id in removed_node_ids:
            flow_layout_nodes.pop(node_id, None)
        nodes_by_name = {
            str(row.get("node_name", "") or "").strip().casefold(): row
            for row in node_rows
            if str(row.get("node_name", "") or "").strip()
        }

    def _sync_node_after_edit(node_row: dict[str, Any]) -> None:
        node_id = str(node_row.get("node_id", "") or "").strip()
        node_name = str(node_row.get("node_name", "") or "").strip()
        if not node_id:
            return
        layout_entry = dict(flow_layout_nodes.get(node_id, {}) or {})
        if not layout_entry:
            node_type = str(node_row.get("node_type", "") or "").strip()
            layout_entry = _default_layout_entry(node_type, node_name, _next_added_node_position(flow_layout_nodes, node_type))
        layout_entry["name"] = node_name
        node_type = str(node_row.get("node_type", "") or "").strip()
        if node_type == "data_node":
            _update_data_node_ports(node_row, layout_entry)
        elif node_type == "python_node":
            _update_python_node_ports(node_row, layout_entry)
        elif node_type == "back_node":
            _update_text_node_layout(node_row, layout_entry)
        flow_layout_nodes[node_id] = layout_entry

    def _rename_node_references(old_name: str, new_name: str) -> None:
        if not old_name or not new_name or old_name == new_name:
            return
        for connection in list(flow_json.get("connections_df", []) or []):
            mapping = dict(connection.get("mapping", {}) or {}) if isinstance(connection.get("mapping"), dict) else {}
            connection["mapping"] = mapping
        for edit_group in ("connections_to_add", "connections_to_remove"):
            for item in list(edits.get(edit_group, []) or []):
                if str(item.get("source_node", "") or "").strip() == old_name:
                    item["source_node"] = new_name
                if str(item.get("target_node", "") or "").strip() == old_name:
                    item["target_node"] = new_name

    for group_name, node_type in (
        ("text_node_updates", "back_node"),
        ("data_node_updates", "data_node"),
        ("python_node_updates", "python_node"),
    ):
        for raw_update in list(edits.get(group_name, []) or []):
            update = dict(raw_update or {})
            target = _resolve_template_node_reference(update.get("node_name", ""), nodes_by_name)
            if target is None:
                continue
            old_name = str(target.get("node_name", "") or "").strip()
            new_name = str(update.get("new_name", "") or "").strip()
            if new_name:
                target["node_name"] = new_name
                _rename_node_references(old_name, new_name)
                nodes_by_name.pop(old_name.casefold(), None)
                nodes_by_name[new_name.casefold()] = target
            if node_type == "back_node":
                if "text" in update:
                    target["node_input_value"] = str(update.get("text", "") or "")
            elif node_type == "data_node":
                old_variable_name = str(target.get("node_input_variable", "") or "").strip()
                if "variable_name" in update:
                    target["node_input_variable"] = str(update.get("variable_name", "") or "").strip()
                if "value" in update:
                    target["node_input_value"] = str(update.get("value", "") or "")
                bool_value = _coerce_bool_or_none(update.get("value_display"))
                if bool_value is not None:
                    target["node_value_display"] = bool_value
                bool_value = _coerce_bool_or_none(update.get("is_path"))
                if bool_value is not None:
                    target["node_is_path"] = bool_value
                new_variable_name = str(target.get("node_input_variable", "") or "").strip()
                _remap_data_node_connection_ports(
                    list(flow_json.get("connections_df", []) or []),
                    node_id=str(target.get("node_id", "") or "").strip(),
                    old_port=old_variable_name,
                    new_port=new_variable_name,
                )
            elif node_type == "python_node":
                old_wrapper = str(target.get("node_function_wrapper", "") or "").strip()
                if "imports" in update:
                    target["node_imports"] = str(update.get("imports", "") or "")
                if "wrapper" in update:
                    target["node_function_wrapper"] = str(update.get("wrapper", "") or "")
                new_wrapper = str(target.get("node_function_wrapper", "") or "").strip()
                old_inputs, old_outputs = _infer_python_ports_from_wrapper(old_wrapper)
                new_inputs, new_outputs = _infer_python_ports_from_wrapper(new_wrapper)
                _remap_python_node_connection_ports(
                    list(flow_json.get("connections_df", []) or []),
                    node_id=str(target.get("node_id", "") or "").strip(),
                    old_inputs=old_inputs,
                    new_inputs=new_inputs,
                    old_outputs=old_outputs,
                    new_outputs=new_outputs,
                )
            _sync_node_after_edit(target)

    prototype_by_type = {}
    for row in node_rows:
        node_type = str(row.get("node_type", "") or "").strip()
        node_id = str(row.get("node_id", "") or "").strip()
        if node_type and node_type not in prototype_by_type:
            prototype_by_type[node_type] = (
                copy.deepcopy(row),
                copy.deepcopy(flow_layout_nodes.get(node_id, {}) or {}),
            )

    for raw_add in list(edits.get("node_additions", []) or []):
        addition = dict(raw_add or {})
        requested_type = str(addition.get("node_type", "") or "").strip().lower()
        node_type = {"data": "data_node", "py": "python_node", "text": "back_node"}.get(requested_type, "")
        node_name = str(addition.get("name", "") or "").strip()
        if not node_type or not node_name:
            continue
        template_row, template_layout = prototype_by_type.get(node_type, ({}, {}))
        node_row = copy.deepcopy(template_row) if template_row else {
            "node_id": "",
            "node_name": node_name,
            "node_type": node_type,
            "node_input_variable": "",
            "node_input_value": "",
            "node_value_display": False,
            "node_is_path": False,
            "node_is_from_master": False,
            "node_expose_outputs": [],
            "node_function_wrapper": "",
            "node_imports": "",
            "node_notebook_path": "",
        }
        node_id = _new_flow_node_id(existing_ids)
        node_row["node_id"] = node_id
        node_row["node_name"] = node_name
        node_row["node_type"] = node_type
        if node_type == "data_node":
            node_row["node_input_variable"] = str(addition.get("variable_name", "") or "").strip()
            node_row["node_input_value"] = str(addition.get("value", "") or "")
            node_row["node_value_display"] = bool(_coerce_bool_or_none(addition.get("value_display")) or False)
            node_row["node_is_path"] = bool(_coerce_bool_or_none(addition.get("is_path")) or False)
        elif node_type == "python_node":
            if "imports" in addition:
                node_row["node_imports"] = str(addition.get("imports", "") or "")
            if "wrapper" in addition:
                node_row["node_function_wrapper"] = str(addition.get("wrapper", "") or "")
        elif node_type == "back_node":
            node_row["node_input_value"] = str(addition.get("text", "") or "")
            node_row["node_value_display"] = True
        node_rows.append(node_row)
        nodes_by_name[node_name.casefold()] = node_row

        layout_entry = copy.deepcopy(template_layout) if template_layout else _default_layout_entry(
            node_type,
            node_name,
            _next_added_node_position(flow_layout_nodes, node_type),
        )
        if not layout_entry:
            layout_entry = _default_layout_entry(node_type, node_name, _next_added_node_position(flow_layout_nodes, node_type))
        layout_entry["name"] = node_name
        layout_entry["pos"] = _next_added_node_position(flow_layout_nodes, node_type)
        flow_layout_nodes[node_id] = layout_entry
        _sync_node_after_edit(node_row)

    removed_pairs = set()
    for raw_remove in list(edits.get("connections_to_remove", []) or []):
        item = dict(raw_remove or {})
        removed_pairs.add((
            str(item.get("source_node", "") or "").strip().casefold(),
            str(item.get("source_port", "") or "").strip(),
            str(item.get("target_node", "") or "").strip().casefold(),
            str(item.get("target_port", "") or "").strip(),
        ))

    node_ids_by_name = {
        str(row.get("node_name", "") or "").strip().casefold(): str(row.get("node_id", "") or "").strip()
        for row in node_rows
        if str(row.get("node_name", "") or "").strip() and str(row.get("node_id", "") or "").strip()
    }

    connection_rows = []
    flow_layout_connections = []
    next_connection_id = 1
    for row in list(flow_json.get("connections_df", []) or []):
        item = dict(row or {})
        source_id = str(item.get("from_node", "") or "").strip()
        target_id = str(item.get("to_node", "") or "").strip()
        if source_id in removed_node_ids or target_id in removed_node_ids:
            continue
        source_name = str(next((r.get("node_name", "") for r in node_rows if str(r.get("node_id", "") or "").strip() == source_id), "") or "").strip()
        target_name = str(next((r.get("node_name", "") for r in node_rows if str(r.get("node_id", "") or "").strip() == target_id), "") or "").strip()
        mapping = dict(item.get("mapping", {}) or {}) if isinstance(item.get("mapping"), dict) else {}
        should_keep = True
        if mapping:
            for source_port, target_port in mapping.items():
                key = (source_name.casefold(), str(source_port or "").strip(), target_name.casefold(), str(target_port or "").strip())
                if key in removed_pairs:
                    should_keep = False
                    break
        if should_keep:
            item["connection_id"] = next_connection_id
            next_connection_id += 1
            connection_rows.append(item)
            if mapping:
                for source_port, target_port in mapping.items():
                    flow_layout_connections.append(
                        {"out": [source_id, str(source_port or "").strip()], "in": [target_id, str(target_port or "").strip()]}
                    )

    existing_connection_keys = {
        (
            str(next((r.get("node_name", "") for r in node_rows if str(r.get("node_id", "") or "").strip() == str(conn.get("from_node", "") or "").strip()), "") or "").strip().casefold(),
            str(source_port or "").strip(),
            str(next((r.get("node_name", "") for r in node_rows if str(r.get("node_id", "") or "").strip() == str(conn.get("to_node", "") or "").strip()), "") or "").strip().casefold(),
            str(target_port or "").strip(),
        )
        for conn in connection_rows
        for source_port, target_port in list(dict(conn.get("mapping", {}) or {}).items())
    }

    for raw_add in list(edits.get("connections_to_add", []) or []):
        item = dict(raw_add or {})
        source_node = str(item.get("source_node", "") or "").strip()
        source_port = str(item.get("source_port", "") or "").strip()
        target_node = str(item.get("target_node", "") or "").strip()
        target_port = str(item.get("target_port", "") or "").strip()
        key = (source_node.casefold(), source_port, target_node.casefold(), target_port)
        if not source_node or not target_node or not source_port or not target_port or key in existing_connection_keys:
            continue
        source_id = node_ids_by_name.get(source_node.casefold(), "")
        target_id = node_ids_by_name.get(target_node.casefold(), "")
        if not source_id or not target_id:
            continue
        connection_rows.append(
            {
                "connection_id": next_connection_id,
                "from_node": source_id,
                "to_node": target_id,
                "mapping": {source_port: target_port},
            }
        )
        next_connection_id += 1
        flow_layout_connections.append({"out": [source_id, source_port], "in": [target_id, target_port]})
        existing_connection_keys.add(key)

    flow_json["nodes_df"] = node_rows
    flow_json["connections_df"] = connection_rows
    flow_json["flow_layout"]["nodes"] = flow_layout_nodes
    flow_json["flow_layout"]["connections"] = flow_layout_connections
    _rebuild_inputs_df_from_nodes(flow_json)
    return flow_json


def _normalize_template_edit_plan(parsed: dict[str, Any]) -> dict[str, Any]:
    edits = dict(parsed.get("template_edits", {}) or {}) if isinstance(parsed.get("template_edits"), dict) else {}

    def _normalize_node_items(key: str, *, allowed_fields: tuple[str, ...]) -> list[dict[str, Any]]:
        normalized_items = []
        for raw_item in list(edits.get(key, []) or []):
            item = dict(raw_item or {})
            node_name = str(item.get("node_name", "") or item.get("name", "") or "").strip()
            if key.endswith("updates") and not node_name:
                continue
            normalized = {}
            if node_name:
                normalized["node_name"] = node_name
            for field in allowed_fields:
                if field in item:
                    normalized[field] = item.get(field)
            if normalized:
                normalized_items.append(normalized)
        return normalized_items

    return {
        "reply": str(parsed.get("reply", "") or "").strip(),
        "planning_path": str(parsed.get("planning_path", "") or "template_json_edit_then_load").strip(),
        "path_reason": str(parsed.get("path_reason", "") or "").strip(),
        "template_edits": {
            "set_flow_name": str(edits.get("set_flow_name", "") or "").strip(),
            "text_node_updates": _normalize_node_items("text_node_updates", allowed_fields=("new_name", "text")),
            "data_node_updates": _normalize_node_items("data_node_updates", allowed_fields=("new_name", "variable_name", "value", "value_display", "is_path")),
            "python_node_updates": _normalize_node_items("python_node_updates", allowed_fields=("new_name", "imports", "wrapper")),
            "node_removals": [
                {"node_name": str(dict(item or {}).get("node_name", "") or dict(item or {}).get("name", "") or "").strip()}
                for item in list(edits.get("node_removals", []) or [])
                if str(dict(item or {}).get("node_name", "") or dict(item or {}).get("name", "") or "").strip()
            ][:8],
            "node_additions": [
                {
                    "node_type": str(dict(item or {}).get("node_type", "") or "").strip(),
                    "name": str(dict(item or {}).get("name", "") or "").strip(),
                    "variable_name": str(dict(item or {}).get("variable_name", "") or "").strip(),
                    "value": str(dict(item or {}).get("value", "") or ""),
                    "value_display": dict(item or {}).get("value_display"),
                    "is_path": dict(item or {}).get("is_path"),
                    "text": str(dict(item or {}).get("text", "") or ""),
                    "imports": str(dict(item or {}).get("imports", "") or ""),
                    "wrapper": str(dict(item or {}).get("wrapper", "") or ""),
                }
                for item in list(edits.get("node_additions", []) or [])
                if str(dict(item or {}).get("node_type", "") or "").strip() and str(dict(item or {}).get("name", "") or "").strip()
            ][:8],
            "connections_to_add": [
                {
                    "source_node": str(dict(item or {}).get("source_node", "") or "").strip(),
                    "source_port": str(dict(item or {}).get("source_port", "") or "").strip(),
                    "target_node": str(dict(item or {}).get("target_node", "") or "").strip(),
                    "target_port": str(dict(item or {}).get("target_port", "") or "").strip(),
                }
                for item in list(edits.get("connections_to_add", []) or [])
                if str(dict(item or {}).get("source_node", "") or "").strip() and str(dict(item or {}).get("target_node", "") or "").strip()
            ][:12],
            "connections_to_remove": [
                {
                    "source_node": str(dict(item or {}).get("source_node", "") or "").strip(),
                    "source_port": str(dict(item or {}).get("source_port", "") or "").strip(),
                    "target_node": str(dict(item or {}).get("target_node", "") or "").strip(),
                    "target_port": str(dict(item or {}).get("target_port", "") or "").strip(),
                }
                for item in list(edits.get("connections_to_remove", []) or [])
                if str(dict(item or {}).get("source_node", "") or "").strip() and str(dict(item or {}).get("target_node", "") or "").strip()
            ][:12],
        },
    }


def _run_template_json_edit_repair(
    user_prompt: str,
    task_match_result: dict[str, Any],
    best_workflow_template: dict[str, Any],
    compiled_workflow: dict[str, Any],
    previous_template_edits: dict[str, Any],
    build_path_guidance: dict[str, Any],
    selected_model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    compiled_inventory = _build_template_workflow_inventory(compiled_workflow)
    compiled_mcp_analysis = {}
    compiled_validation_report = {}
    try:
        from quest.quest_agent.mcp_server.tools_skills_manager import analyze_workflow_json_template, validate_flow_analysis
        compiled_mcp_analysis = analyze_workflow_json_template(compiled_workflow)
        compiled_validation_report = validate_flow_analysis(compiled_mcp_analysis, str(user_prompt or ""))
    except Exception:
        compiled_mcp_analysis = {}
        compiled_validation_report = {}
    system_prompt = (
        "You are QuESt Agent's workflow template JSON repair reviewer. "
        "A first-pass template edit has already been compiled into a workflow JSON. "
        "Review the compiled workflow inventory and MCP validation facts against the user's requested task and the analyzed missing parts. "
        "If the compiled workflow still misses required nodes, wrappers, values, or connections, return only the additional structured template edits needed to finish the job. "
        "Do not return canvas actions. Do not return the full workflow JSON. "
        "If the compiled workflow contains extra data, text, or Python nodes that make the flow irrelevant or overbuilt for the task, return node_removals and any connection cleanup needed. "
        "If the compiled workflow already satisfies the request, return empty template edits. "
        "Return valid JSON only with this shape: "
        "{"
        "\"reply\": string, "
        "\"planning_path\": \"template_json_edit_then_load\", "
        "\"path_reason\": string, "
        "\"template_edits\": {"
        "\"set_flow_name\": string, "
        "\"text_node_updates\": [{\"node_name\": string, \"new_name\": string, \"text\": string}], "
        "\"data_node_updates\": [{\"node_name\": string, \"new_name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean}], "
        "\"python_node_updates\": [{\"node_name\": string, \"new_name\": string, \"imports\": string, \"wrapper\": string}], "
        "\"node_removals\": [{\"node_name\": string}], "
        "\"node_additions\": [{\"node_type\": \"data\"|\"py\"|\"text\", \"name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean, \"text\": string, \"imports\": string, \"wrapper\": string}], "
        "\"connections_to_add\": [{\"source_node\": string, \"source_port\": string, \"target_node\": string, \"target_port\": string}], "
        "\"connections_to_remove\": [{\"source_node\": string, \"source_port\": string, \"target_node\": string, \"target_port\": string}]"
        "}"
        "}."
    )
    payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "task_analysis": dict(task_match_result or {}),
        "task_analysis_guidance": _task_analysis_guidance(task_match_result),
        "best_workflow_template": dict(best_workflow_template or {}),
        "compiled_workflow_inventory": compiled_inventory,
        "compiled_mcp_analysis": compiled_mcp_analysis,
        "compiled_validation_report": compiled_validation_report,
        "previous_template_edits": dict(previous_template_edits or {}),
        "build_path_guidance": dict(build_path_guidance or {}),
    }
    if _fast_local_mode_enabled(selected_model):
        payload = _enforce_fast_local_payload_budget(
            {
                "latest_user_prompt": _truncate_text(user_prompt, 800),
                "task_analysis": _trim_task_analysis_for_fast_local(task_match_result),
                "task_analysis_guidance": _trim_task_analysis_guidance_for_fast_local(task_match_result),
                "best_workflow_template": dict(best_workflow_template or {}),
                "compiled_workflow_inventory": compiled_inventory,
                "compiled_mcp_analysis": compiled_mcp_analysis,
                "compiled_validation_report": compiled_validation_report,
                "previous_template_edits": dict(previous_template_edits or {}),
                "build_path_guidance": dict(build_path_guidance or {}),
            },
            max_chars=FAST_LOCAL_PROMPT_CHAR_LIMIT,
        )
    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]
    content, _resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "Template JSON repair returned no content.",
            "Template JSON repair returned invalid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    return _normalize_template_edit_plan(parsed)


def _run_template_json_edit_plan(
    user_prompt: str,
    task_match_result: dict[str, Any],
    skill_execution_recipes: dict[str, Any],
    build_path_guidance: dict[str, Any],
    selected_model: str | None = None,
    single_step_only: bool = False,
    api_key: str | None = None,
) -> dict[str, Any]:
    best_template = dict(task_match_result.get("best_workflow_template", {}) or {})
    workflow_path = str(best_template.get("workflow_json_path", "") or "").strip()
    if not workflow_path:
        raise RuntimeError("No best workflow template was available for JSON editing.")
    template_json = _read_workflow_json_file(workflow_path)
    template_inventory = _build_template_workflow_inventory(template_json)
    template_mcp_analysis = {}
    template_validation_report = {}
    try:
        from quest.quest_agent.mcp_server.tools_skills_manager import analyze_workflow_json_template, validate_flow_analysis
        template_mcp_analysis = analyze_workflow_json_template(template_json)
        template_validation_report = validate_flow_analysis(template_mcp_analysis, str(user_prompt or ""))
    except Exception:
        template_mcp_analysis = {}
        template_validation_report = {}

    system_prompt = (
        "You are QuESt Agent's workflow template JSON editor. "
        "A best matched workflow template has already been chosen. "
        "Your job is to validate that template against the user's requested task and return only the structured edits needed to adapt it. "
        "Do not return canvas actions. Do not return the full workflow JSON. "
        "Never load a saved skill workflow JSON by path directly; the output must compile into a workflow_content copy that can be loaded only after this validation/edit step. "
        "Prefer minimal edits to the template instead of rebuilding its structure. "
        "Use the task analysis, missing parts, template inventory, and MCP validation facts as the source of truth. "
        "Remove unnecessary template nodes when they exceed the requested task or make the workflow irrelevant. "
        "Make the JSON edit complete enough that the loaded workflow should satisfy the task without depending on later touch-up canvas actions for obvious missing pieces. "
        "The output pipeline is: JSON diff/edit -> compile -> load -> validate. "
        "Return valid JSON only with this shape: "
        "{"
        "\"reply\": string, "
        "\"planning_path\": \"template_json_edit_then_load\", "
        "\"path_reason\": string, "
        "\"template_edits\": {"
        "\"set_flow_name\": string, "
        "\"text_node_updates\": [{\"node_name\": string, \"new_name\": string, \"text\": string}], "
        "\"data_node_updates\": [{\"node_name\": string, \"new_name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean}], "
        "\"python_node_updates\": [{\"node_name\": string, \"new_name\": string, \"imports\": string, \"wrapper\": string}], "
        "\"node_removals\": [{\"node_name\": string}], "
        "\"node_additions\": [{\"node_type\": \"data\"|\"py\"|\"text\", \"name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean, \"text\": string, \"imports\": string, \"wrapper\": string}], "
        "\"connections_to_add\": [{\"source_node\": string, \"source_port\": string, \"target_node\": string, \"target_port\": string}], "
        "\"connections_to_remove\": [{\"source_node\": string, \"source_port\": string, \"target_node\": string, \"target_port\": string}]"
        "}"
        "}."
    )
    if single_step_only:
        system_prompt += " Local single-step mode is active, but because this is a template JSON edit path, still return the full minimal template edit set needed for the next load."

    payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "task_analysis": dict(task_match_result or {}),
        "task_analysis_guidance": _task_analysis_guidance(task_match_result),
        "best_workflow_template": best_template,
        "template_inventory": template_inventory,
        "template_mcp_analysis": template_mcp_analysis,
        "template_validation_report": template_validation_report,
        "build_path_guidance": dict(build_path_guidance or {}),
        "skill_execution_recipes": dict(skill_execution_recipes or {}),
    }
    if _fast_local_mode_enabled(selected_model):
        payload = _enforce_fast_local_payload_budget(
            {
                "latest_user_prompt": _truncate_text(user_prompt, 800),
                "task_analysis": _trim_task_analysis_for_fast_local(task_match_result),
                "task_analysis_guidance": _trim_task_analysis_guidance_for_fast_local(task_match_result),
                "best_workflow_template": dict(best_template or {}),
                "template_inventory": template_inventory,
                "template_mcp_analysis": template_mcp_analysis,
                "template_validation_report": template_validation_report,
                "build_path_guidance": dict(build_path_guidance or {}),
            },
            max_chars=FAST_LOCAL_PROMPT_CHAR_LIMIT,
        )

    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "Template JSON edit planner returned no content.",
            "Template JSON edit planner returned invalid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    normalized = _normalize_template_edit_plan(parsed)
    compiled_workflow = _compile_template_edit_plan(template_json, normalized.get("template_edits", {}))
    try:
        repair_result = _run_template_json_edit_repair(
            user_prompt=user_prompt,
            task_match_result=task_match_result,
            best_workflow_template=best_template,
            compiled_workflow=compiled_workflow,
            previous_template_edits=dict(normalized.get("template_edits", {}) or {}),
            build_path_guidance=build_path_guidance,
            selected_model=selected_model,
            api_key=api_key,
        )
    except Exception:
        repair_result = {}
    if _template_edits_has_changes(dict(repair_result or {}).get("template_edits", {})):
        compiled_workflow = _compile_template_edit_plan(
            compiled_workflow,
            dict(repair_result.get("template_edits", {}) or {}),
        )
        if not str(normalized.get("reply", "") or "").strip():
            normalized["reply"] = str(repair_result.get("reply", "") or "").strip()
        if not str(normalized.get("path_reason", "") or "").strip():
            normalized["path_reason"] = str(repair_result.get("path_reason", "") or "").strip()
    return {
        "reply": str(normalized.get("reply", "") or "").strip(),
        "planning_path": "template_json_edit_then_load",
        "path_reason": str(normalized.get("path_reason", "") or best_template.get("selection_reason", "") or "").strip(),
        "planner_contract": "mcp_workspace_operations_v1",
        "planner_prompt_profile": "template_json_edit_then_load",
        "operations": [
            {
                "operation": "workspace.load_template",
                "arguments": {
                    "workflow_content": compiled_workflow,
                    "source_skill_id": str(best_template.get("skill_id", "") or "").strip(),
                },
            }
        ],
        "actions": [
            {
                "type": "load_workflow_json",
                "workflow_content": compiled_workflow,
                "source_skill_id": str(best_template.get("skill_id", "") or "").strip(),
            }
        ],
        "template_edits": dict(normalized.get("template_edits", {}) or {}),
        "planning_source": "template_json_edit",
        "model_used_note": _build_model_used_note(
            selected_model,
            selected_reasoning_model,
            resolved_model_name,
        ),
    }


def _run_current_flow_json_patch_plan(
    user_prompt: str,
    task_match_result: dict[str, Any],
    attached_workflow_jsons: list[dict[str, Any]] | None,
    skill_execution_recipes: dict[str, Any],
    build_path_guidance: dict[str, Any],
    selected_model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    current_entry = _current_workflow_json_entry(attached_workflow_jsons)
    current_flow_json = dict(current_entry.get("content", {}) or {})
    if not current_flow_json:
        raise RuntimeError("No current canvas workflow JSON was available for patching.")
    current_inventory = _build_template_workflow_inventory(current_flow_json)

    system_prompt = (
        "You are QuESt Agent's current-flow JSON patch planner. "
        "The current canvas workflow JSON has already been serialized. "
        "Your job is to patch that current workflow JSON so it satisfies the task and fixes the listed missing parts. "
        "Do not return canvas actions. Do not return the full workflow JSON. "
        "Return only the structured JSON edits needed to transform the current flow into the next better flow state. "
        "Use task analysis and missing parts as the source of truth for what is still wrong. "
        "Use the current flow inventory as the source of truth for what already exists. "
        "Prefer editing and reusing existing nodes and connections over duplicating them. "
        "The output pipeline is: current json patch -> compile -> load -> validate. "
        "Make the patch complete enough that it should not depend on ad hoc touch-up canvas actions for obvious missing pieces. "
        "Return valid JSON only with this shape: "
        "{"
        "\"reply\": string, "
        "\"planning_path\": \"current_flow_json_patch_then_load\", "
        "\"path_reason\": string, "
        "\"template_edits\": {"
        "\"set_flow_name\": string, "
        "\"text_node_updates\": [{\"node_name\": string, \"new_name\": string, \"text\": string}], "
        "\"data_node_updates\": [{\"node_name\": string, \"new_name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean}], "
        "\"python_node_updates\": [{\"node_name\": string, \"new_name\": string, \"imports\": string, \"wrapper\": string}], "
        "\"node_removals\": [{\"node_name\": string}], "
        "\"node_additions\": [{\"node_type\": \"data\"|\"py\"|\"text\", \"name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean, \"text\": string, \"imports\": string, \"wrapper\": string}], "
        "\"connections_to_add\": [{\"source_node\": string, \"source_port\": string, \"target_node\": string, \"target_port\": string}], "
        "\"connections_to_remove\": [{\"source_node\": string, \"source_port\": string, \"target_node\": string, \"target_port\": string}]"
        "}"
        "}."
    )
    payload = {
        "latest_user_prompt": str(user_prompt or ""),
        "task_analysis": dict(task_match_result or {}),
        "task_analysis_guidance": _task_analysis_guidance(task_match_result),
        "current_flow_json_summary": {
            "file": str(current_entry.get("file", "") or "").strip(),
            "flow_name": str(current_entry.get("flow_name", "") or "").strip(),
            "flow_type": str(current_entry.get("flow_type", "") or "").strip(),
            "node_count": int(current_entry.get("node_count", 0) or 0),
            "connection_count": int(current_entry.get("connection_count", 0) or 0),
        },
        "current_flow_inventory": current_inventory,
        "build_path_guidance": dict(build_path_guidance or {}),
        "skill_execution_recipes": dict(skill_execution_recipes or {}),
    }
    if _fast_local_mode_enabled(selected_model):
        payload = _enforce_fast_local_payload_budget(
            {
                "latest_user_prompt": _truncate_text(user_prompt, 800),
                "task_analysis": _trim_task_analysis_for_fast_local(task_match_result),
                "task_analysis_guidance": _trim_task_analysis_guidance_for_fast_local(task_match_result),
                "current_flow_json_summary": dict(payload.get("current_flow_json_summary", {}) or {}),
                "current_flow_inventory": current_inventory,
                "build_path_guidance": dict(build_path_guidance or {}),
            },
            max_chars=FAST_LOCAL_PROMPT_CHAR_LIMIT,
        )

    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "Current flow JSON patch planner returned no content.",
            "Current flow JSON patch planner returned invalid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    normalized = _normalize_template_edit_plan(parsed)
    compiled_workflow = _compile_template_edit_plan(current_flow_json, normalized.get("template_edits", {}))
    try:
        repair_result = _run_template_json_edit_repair(
            user_prompt=user_prompt,
            task_match_result=task_match_result,
            best_workflow_template={
                "skill_id": "",
                "title": str(current_entry.get("file", "") or "Current Canvas"),
                "selection_reason": "Applied a JSON patch to the current canvas workflow.",
            },
            compiled_workflow=compiled_workflow,
            previous_template_edits=dict(normalized.get("template_edits", {}) or {}),
            build_path_guidance=build_path_guidance,
            selected_model=selected_model,
            api_key=api_key,
        )
    except Exception:
        repair_result = {}
    if _template_edits_has_changes(dict(repair_result or {}).get("template_edits", {})):
        compiled_workflow = _compile_template_edit_plan(
            compiled_workflow,
            dict(repair_result.get("template_edits", {}) or {}),
        )
        if not str(normalized.get("reply", "") or "").strip():
            normalized["reply"] = str(repair_result.get("reply", "") or "").strip()
        if not str(normalized.get("path_reason", "") or "").strip():
            normalized["path_reason"] = str(repair_result.get("path_reason", "") or "").strip()
    return {
        "reply": str(normalized.get("reply", "") or "").strip(),
        "planning_path": "current_flow_json_patch_then_load",
        "path_reason": str(normalized.get("path_reason", "") or "Patched the current canvas workflow JSON to resolve the analyzed missing parts.").strip(),
        "planner_contract": "mcp_workspace_operations_v1",
        "planner_prompt_profile": "current_flow_json_patch_then_load",
        "operations": [
            {
                "operation": "workspace.load_template",
                "arguments": {
                    "workflow_content": compiled_workflow,
                    "source_skill_id": "",
                },
            }
        ],
        "actions": [
            {
                "type": "load_workflow_json",
                "workflow_content": compiled_workflow,
                "source_skill_id": "",
            }
        ],
        "template_edits": dict(normalized.get("template_edits", {}) or {}),
        "planning_source": "current_flow_json_patch",
        "model_used_note": _build_model_used_note(
            selected_model,
            selected_reasoning_model,
            resolved_model_name,
        ),
    }


def _repair_workspace_action_plan(
    model_name: str,
    user_prompt: str,
    canvas_context: dict[str, Any],
    task_match_result: dict[str, Any],
    skill_execution_recipes: dict[str, Any],
    conversation: list[dict[str, Any]],
    initial_content: str,
    dropped_actions: list[str],
    single_step_only: bool = False,
    api_key: str | None = None,
) -> dict[str, Any]:
    repair_prompt = (
        "You are repairing a QuESt Workspace MCP operation plan. "
        "The first draft was semantically close but did not normalize into executable canonical operations. "
        "Convert the user's request into the exact supported schema. "
        "Use task_analysis.flow_description, task_analysis.structured_flow_summary, task_analysis.missing_parts, and task_analysis.notes as authoritative evidence about the current flow state. "
        "If analysis indicates a partially built or incomplete flow, prefer repairing and completing the existing flow instead of rebuilding it from scratch unless the user explicitly asked for a rebuild. "
        "Treat task_analysis.missing_parts as the highest-priority issues to resolve in the repaired plan. "
        "If skill_execution_recipes contains strong matched skills, repair the plan toward those recipes instead of falling back to generic blank nodes. "
        "Use build_path_guidance to choose the easiest viable build path before repairing the plan. "
        "Use only these operation ids: workspace.create_data_node, workspace.create_python_node, workspace.create_text_node, workspace.update_data_node, workspace.update_python_node, workspace.update_text_node, workspace.connect_ports, workspace.load_template, workspace.add_subflow, workspace.rename_selected_node, workspace.update_selected_text_node, workspace.delete_node, workspace.delete_selected_nodes, workspace.validate_flow. "
        "When task_analysis.missing_parts says an input/data node is missing, repair that gap with workspace.create_data_node using the named missing input as both name and variable_name when appropriate; do not encode a missing input as a value edit on an unrelated existing node. "
        "When task_analysis.missing_parts says an existing Python wrapper or node logic is incomplete, repair that gap with workspace.update_python_node on the named existing Python node and include the revised wrapper when possible. "
        "When a new input must feed an existing Python node, include the needed workspace.connect_ports operation unless local single-step mode requires returning only the first operation. "
        "When analysis identifies a specific extra or conflicting node to remove, use workspace.delete_node with node_name; use workspace.delete_selected_nodes only when the user explicitly asked to delete the current GUI selection. "
        "If the request is clearly a canvas edit, return at least one operation. "
        "Return valid JSON only with shape {\"reply\": string, \"planning_path\": string, \"path_reason\": string, \"operations\": [{\"operation\": string, \"arguments\": object}]}."
    )
    if single_step_only:
        repair_prompt += " Local single-step mode is active. Return exactly one next executable operation, not a full multi-step plan."
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
    if _fast_local_mode_enabled(model_name):
        repair_payload = _build_fast_local_action_plan_payload(
            user_prompt,
            canvas_context,
            task_match_result,
            [],
            [],
            [],
            {},
            [],
            {},
            skill_execution_recipes,
            conversation,
            repair_payload.get("build_path_guidance", {}),
        ) | {
            "initial_plan_raw": _truncate_text(initial_content, 800),
            "normalization_failures": [_truncate_text(item, 180) for item in list(dropped_actions or [])[:5]],
        }
    selected_reasoning_model = _resolve_fast_local_reasoning_model(model_name)
    messages = [
        {"role": "system", "content": repair_prompt},
        {"role": "user", "content": json.dumps(repair_payload, ensure_ascii=True, indent=2)},
    ]
    try:
        content, resolved_model_name = _chat_completion_content(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
            response_json=True,
        )
    except RuntimeError as exc:
        return {"reply": "", "actions": [], "dropped_actions": [str(exc)]}
    if not content:
        return {"reply": "", "actions": [], "dropped_actions": ["Repair pass returned no content."]}
    try:
        parsed = _parse_json_response(
            content,
            "Repair pass returned no content.",
            "Repair pass returned invalid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(model_name):
            return {"reply": "", "actions": [], "dropped_actions": ["Repair pass returned invalid JSON."]}
        try:
            parsed = _retry_local_json_response(
                messages,
                selected_model=selected_reasoning_model,
                temperature=0,
                api_key=api_key,
            )
        except RuntimeError:
            return {"reply": "", "actions": [], "dropped_actions": ["Repair pass returned invalid JSON."]}
    normalized_plan = _normalize_workspace_action_plan(parsed, canvas_context=canvas_context)
    normalized_plan["planner_contract"] = "mcp_workspace_operations_v1"
    normalized_plan["planner_prompt_profile"] = "workspace_operation_planner"
    normalized_plan["model_used_note"] = _build_model_used_note(
        model_name,
        selected_reasoning_model,
        resolved_model_name,
    )
    return normalized_plan


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
    single_step_only: bool = False,
    force_planning_path: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    canvas_context = dict(canvas_context or {})
    task_match_result = dict(task_match_result or {})
    skill_execution_recipes = dict(skill_execution_recipes or {})
    task_match_result, skill_execution_recipes = _sanitize_template_candidates(
        task_match_result,
        skill_execution_recipes,
    )
    conversation = _recent_conversation(recent_messages)
    build_path_guidance = _build_path_guidance(
        user_prompt,
        canvas_context=canvas_context,
        task_match_result=task_match_result,
        skill_execution_recipes=skill_execution_recipes,
    )
    if str(force_planning_path or "").strip():
        build_path_guidance["recommended_path"] = str(force_planning_path or "").strip()
        if not str(build_path_guidance.get("reason", "") or "").strip():
            build_path_guidance["reason"] = "Forced planning path."
    best_workflow_template = dict(task_match_result.get("best_workflow_template", {}) or {})
    recommended_path = str(build_path_guidance.get("recommended_path", "") or "").strip()
    if recommended_path == "current_flow_json_patch_then_load":
        return _run_current_flow_json_patch_plan(
            user_prompt=user_prompt,
            task_match_result=task_match_result,
            attached_workflow_jsons=attached_workflow_jsons,
            skill_execution_recipes=skill_execution_recipes,
            build_path_guidance=build_path_guidance,
            selected_model=selected_model,
            api_key=api_key,
        )
    if (
        best_workflow_template
        and recommended_path == "template_json_edit_then_load"
    ):
        return _run_template_json_edit_plan(
            user_prompt=user_prompt,
            task_match_result=task_match_result,
            skill_execution_recipes=skill_execution_recipes,
            build_path_guidance=build_path_guidance,
            selected_model=selected_model,
            single_step_only=single_step_only,
            api_key=api_key,
        )

    system_prompt = (
        "You are QuESt Agent's canvas action planner. "
        "First infer the user's high-level canvas intent, then produce concrete canvas actions that can be executed immediately on the current QuESt Workspace canvas. "
        "Do not invent unsupported actions. "
        "If the request involves Python node wrappers, ports, or notebook code, treat python_node_wrapper_rules as authoritative over guesses. "
        "Treat task_analysis_guidance as the main execution guidance from prior analysis. "
        "Use task_analysis_guidance.flow_description, task_analysis_guidance.structured_flow_summary, task_analysis_guidance.missing_parts, and task_analysis_guidance.notes as authoritative current-state evidence about what already exists on canvas. "
        "If analysis shows an incomplete or partially built flow, prefer actions that complete, connect, initialize, or repair existing nodes instead of rebuilding the flow from scratch, unless the user explicitly asks to rebuild or replace it. "
        "Treat task_analysis_guidance.missing_parts as the highest-priority gaps to resolve in the next plan. "
        "When task_analysis_guidance.missing_parts says an input/data node is missing, produce a workspace.create_data_node operation for that named input; do not turn missing input requirements into value edits on unrelated existing nodes. "
        "When task_analysis_guidance.missing_parts says an existing Python wrapper or node logic is incomplete, produce a workspace.update_python_node operation for the named existing Python node and include a revised wrapper when possible. "
        "When a new input must feed an existing Python node, include a workspace.connect_ports operation for the new data node to the existing Python node unless local single-step mode requires returning only the first operation. "
        "Follow task_analysis_guidance.planning_directives strictly when they are present. "
        "Use top_skill_matches and top_tool_matches to shape how the plan should be implemented, but not to ignore the analyzed current flow. "
        "If task_analysis_guidance.best_workflow_template is available, treat it as the preferred baseline for a JSON diff/edit -> load -> validate workflow. "
        "Use build_path_guidance to choose the easiest viable build path before producing actions. "
        "When the current canvas exists and analysis shows a small number of missing parts, prefer edit_current_flow with direct Workspace operations. "
        "When the canvas is empty and the task is to create a flow, prefer adapting a matched template or skill when one is available. "
        "When the current canvas needs many edits, major restructuring, a subflow, or a large template-level change, prefer current_flow_json_patch_then_load. "
        "You may combine direct edits, template loading, and JSON patching when that is the clearest route, but every action must still resolve the analyzed current-flow gaps. "
        "If skill_execution_recipes contains strong matched skills, treat those recipes as concrete prior examples to adapt. "
        "Prefer reusing a matched skill's workflow strategy, step pattern, validation criteria, and saved workflow template structure over inventing a fresh plan from scratch when the task is similar. "
        "If a matched skill includes workflow_template metadata, never load its workflow_path directly; produce edited workflow_content only after validating and adapting it against the task. "
        "If relevant saved skills were matched, let their intent and reasons shape the concrete canvas actions you choose. "
        "Canvas changes are executed through the MCP Workspace operation contract. "
        "Return MCP operation requests in the operations array. "
        "Supported operation ids are: workspace.create_data_node, workspace.create_python_node, workspace.create_text_node, workspace.update_data_node, workspace.update_python_node, workspace.update_text_node, workspace.connect_ports, workspace.load_template, workspace.add_subflow, workspace.rename_selected_node, workspace.update_selected_text_node, workspace.delete_node, workspace.delete_selected_nodes, workspace.validate_flow. "
        "Each operation object must use {\"operation\": string, \"arguments\": object}. "
        "For workspace.create_data_node, include name, variable_name, value, value_display, and is_path when relevant. "
        "For workspace.create_python_node, include name, imports, wrapper, and code when relevant. "
        "For workspace.update_python_node, provide node_name and only changed fields such as new_name, imports, wrapper, or code. "
        "For workspace.update_data_node, provide node_name and only changed fields such as new_name, variable_name, value, value_display, or is_path. "
        "For workspace.update_text_node, provide node_name and text. Use it for existing description, note, annotation, or BackNode text nodes. "
        "For workspace.delete_node, provide node_name. Use it for a known extra or conflicting node; do not use workspace.delete_selected_nodes for this case. "
        "For workspace.connect_ports, provide source_node, target_node, and source_port/target_port or mapping when needed. "
        "For workspace.load_template, provide workflow_content for any matched skill/template reuse; workflow_path is only for explicit user-provided imports, not automatic skill reuse. "
        "If the request is a canvas change, prefer returning at least one operation instead of leaving operations empty. "
        "Return valid JSON only with this shape: "
        "{"
        "\"reply\": string, "
        "\"intent\": string, "
        "\"planning_path\": string, "
        "\"path_reason\": string, "
        "\"operations\": ["
        "{\"operation\": string, \"arguments\": {\"count\": number, \"name\": string, \"node_name\": string, \"flow_name\": string, \"variable_name\": string, \"value\": string, \"value_display\": boolean, \"is_path\": boolean, \"imports\": string, \"wrapper\": string, \"code\": string, \"new_name\": string, \"text\": string, \"source_node\": string, \"target_node\": string, \"source_port\": string, \"target_port\": string, \"mapping\": object, \"workflow_path\": string, \"workflow_content\": object, \"source_skill_id\": string}}"
        "]"
        "}."
    )
    if single_step_only:
        system_prompt += (
            " Local single-step mode is active. "
            "Return exactly one next executable operation only. "
            "Do not include later follow-up build steps yet."
        )

    if _fast_local_mode_enabled(selected_model):
        payload = _build_fast_local_action_plan_payload(
            user_prompt,
            canvas_context,
            task_match_result,
            pinned_context,
            attached_files,
            attached_workflow_jsons,
            workspace_relationship_context,
            implicit_code_context,
            python_node_wrapper_rules,
            skill_execution_recipes,
            recent_messages,
            build_path_guidance,
        )
        system_prompt += (
            " Fast local mode is active. "
            "Use the provided compact context only. "
            "Prefer the shortest viable plan that reuses current flow state and strong matched skill recipes."
        )
    else:
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

    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=True, indent=2)},
    ]
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "OpenAI returned an empty canvas action plan.",
            "OpenAI canvas action plan was not valid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    normalized_plan = _normalize_workspace_action_plan(parsed, canvas_context=canvas_context)
    normalized_plan["model_used_note"] = _build_model_used_note(
        selected_model,
        selected_reasoning_model,
        resolved_model_name,
    )
    if normalized_plan.get("actions"):
        normalized_plan["intent"] = str(parsed.get("intent", "") or "").strip()
        return normalized_plan

    if not _request_looks_actionable(user_prompt):
        normalized_plan["intent"] = str(parsed.get("intent", "") or "").strip()
        return normalized_plan

    repaired_plan = _repair_workspace_action_plan(
        model_name=resolved_model_name,
        user_prompt=user_prompt,
        canvas_context=canvas_context,
        task_match_result=task_match_result,
        skill_execution_recipes=skill_execution_recipes,
        conversation=conversation,
        initial_content=content,
        dropped_actions=list(normalized_plan.get("dropped_actions", []) or []),
        single_step_only=single_step_only,
        api_key=api_key,
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
    mcp_candidate_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    quest_agent_root = get_quest_agent_root(quest_agent_root)
    registry = write_active_tool_registry(quest_agent_root)
    skill_payload = load_skill_library(quest_agent_root)
    tools = list(registry.get("tools", []))
    skills = list(skill_payload.get("skills", []))
    candidate_result = dict(mcp_candidate_result or {})
    candidate_tool_ids = {
        str(item.get("tool_id", "") or "").strip()
        for item in list(candidate_result.get("tool_matches", []) or [])
        if str(item.get("tool_id", "") or "").strip()
    }
    candidate_skill_ids = {
        str(item.get("skill_id", "") or "").strip()
        for item in list(candidate_result.get("skill_matches", []) or [])
        if str(item.get("skill_id", "") or "").strip()
    }
    if candidate_tool_ids:
        tools = [
            tool for tool in tools
            if str(tool.get("tool_id", "") or "").strip() in candidate_tool_ids
        ]
    if candidate_skill_ids:
        skills = [
            skill for skill in skills
            if str(getattr(skill, "skill_id", "") or "").strip() in candidate_skill_ids
        ]
    query_text = _build_matcher_search_text(
        task_description,
        list(pinned_context or []),
        list(attached_files or []),
        list(attached_workflow_jsons or []),
        dict(workspace_relationship_context or {}),
        list(implicit_code_context or []),
    )
    preliminary_tool_matches = _heuristic_tool_matches(query_text, tools)
    selected_skills = _filter_skills_by_matched_tools(
        skills,
        preliminary_tool_matches,
        include_general_fallback=True,
    )
    if _fast_local_mode_enabled(selected_model):
        selected_skills = _select_skills_for_fast_local(selected_skills, query_text or task_description)
        pinned_context = [_truncate_text(item, 220) for item in list(pinned_context or [])[:FAST_LOCAL_MAX_PINNED_CONTEXT]]
        attached_files = list(attached_files or [])[:FAST_LOCAL_MAX_ATTACHED_FILES]
        attached_workflow_jsons = _trim_workflow_contexts_for_fast_local(attached_workflow_jsons)
        workspace_relationship_context = dict(workspace_relationship_context or {})
        implicit_code_context = _trim_implicit_code_context_for_fast_local(implicit_code_context)
        python_node_wrapper_rules = _trim_python_wrapper_rules_for_fast_local(python_node_wrapper_rules)

    selected_reasoning_model = _resolve_fast_local_reasoning_model(selected_model)
    messages = _build_messages(
            task_description=task_description,
            pinned_context=list(pinned_context or []),
            attached_files=list(attached_files or []),
            attached_workflow_jsons=list(attached_workflow_jsons or []),
            workspace_relationship_context=dict(workspace_relationship_context or {}),
            implicit_code_context=list(implicit_code_context or []),
            python_node_wrapper_rules=dict(python_node_wrapper_rules or {}),
            tools=tools,
            skills=selected_skills,
        )
    content, resolved_model_name = _chat_completion_content(
        messages,
        selected_model=selected_reasoning_model,
        temperature=0,
        api_key=api_key,
        response_json=True,
    )
    try:
        parsed = _parse_json_response(
            content,
            "OpenAI returned an empty task match response.",
            "OpenAI task match response was not valid JSON.",
        )
    except RuntimeError:
        if not _fast_local_mode_enabled(selected_model):
            raise
        parsed = _retry_local_json_response(
            messages,
            selected_model=selected_reasoning_model,
            temperature=0,
            api_key=api_key,
        )
    result = _normalize_match_result(parsed, tools, skills)
    result = _apply_heuristic_match_floor(
        result,
        query_text=query_text,
        tools=tools,
        skills=skills,
        task_description=task_description,
        attached_workflow_jsons=list(attached_workflow_jsons or []),
        workspace_relationship_context=dict(workspace_relationship_context or {}),
    )
    result = _enforce_tool_derived_skill_matches(
        result,
        skills=skills,
        mcp_candidate_result=candidate_result,
    )
    best_workflow_template = _build_best_workflow_template(
        list(result.get("skill_matches", []) or []),
        skills,
        list(result.get("tool_matches", []) or []),
    )
    if best_workflow_template:
        result["best_workflow_template"] = best_workflow_template
        notes = [str(note).strip() for note in list(result.get("notes", []) or []) if str(note).strip()]
        title = str(best_workflow_template.get("title", "") or "").strip()
        if title and not any(title.casefold() in note.casefold() for note in notes):
            notes.append(
                f"Best reusable workflow template: {title}. Prefer adapting that saved flow before building from scratch."
            )
        result["notes"] = notes[:10]
    result["tool_errors"] = list(skill_payload.get("errors", []))
    result["model"] = resolved_model_name
    result["model_used_note"] = _build_model_used_note(
        selected_model,
        selected_reasoning_model,
        resolved_model_name,
    )
    return result
