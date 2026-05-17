import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


TOOL_REGISTRY_SCHEMA_VERSION = "1.0"


@dataclass
class ToolRecord:
    tool_id: str
    name: str
    active: bool
    category: str
    description: str
    input_types: list[str]
    output_types: list[str]
    typical_tasks: list[str]
    limitations: list[str]
    workflow_roles: list[str]
    aliases: list[str]
    search_key: str
    launch_type: str
    launch_value: str
    source_app_card_path: str
    raw_data: dict[str, Any]

    def to_registry_entry(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "active": self.active,
            "category": self.category,
            "description": self.description,
            "input_types": list(self.input_types),
            "output_types": list(self.output_types),
            "typical_tasks": list(self.typical_tasks),
            "limitations": list(self.limitations),
            "workflow_roles": list(self.workflow_roles),
            "aliases": list(self.aliases),
            "search_key": self.search_key,
            "launch_type": self.launch_type,
            "launch_value": self.launch_value,
            "source_app_card_path": self.source_app_card_path,
        }


def get_package_root(package_root: str | Path | None = None) -> Path:
    if package_root is None:
        package_root = Path(__file__).resolve().parents[1]
    package_root = Path(package_root)
    if package_root.name == "quest_agent":
        return package_root.parent
    return package_root


def get_quest_agent_root(package_root: str | Path | None = None) -> Path:
    package_root = get_package_root(package_root)
    return package_root / "quest_agent"


def get_registry_root(package_root: str | Path | None = None) -> Path:
    return get_quest_agent_root(package_root) / "registry"


def get_app_cards_path(package_root: str | Path | None = None) -> Path:
    package_root = get_package_root(package_root)
    return package_root / "app" / "home_page" / "app_cards.json"


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _clean_html_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_title(title: str) -> str:
    cleaned = _clean_html_text(title)
    cleaned = re.sub(r"^QuESt[-\s]*", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned or _clean_html_text(title)


def _infer_input_types(info_text: str) -> list[str]:
    info = info_text.lower()
    mapping = {
        "csv": ["csv"],
        "market data": ["market_data"],
        "tariff": ["tariff"],
        "load profile": ["load_profile"],
        "photovoltaic": ["pv_profile"],
        "pv": ["pv_profile"],
        "historical": ["historical_data"],
        "building": ["building_data"],
        "distribution": ["distribution_data"],
        "energyplus": ["energyplus_model"],
    }
    found = []
    for phrase, labels in mapping.items():
        if phrase in info:
            for label in labels:
                if label not in found:
                    found.append(label)
    return found


def _infer_output_types(info_text: str) -> list[str]:
    info = info_text.lower()
    mapping = {
        "rank": ["ranking"],
        "revenue": ["revenue_metrics"],
        "value": ["valuation_metrics"],
        "analysis": ["analysis"],
        "visual": ["visualization"],
        "simulation": ["simulation_results"],
        "benefits": ["benefit_metrics"],
        "capacity": ["capacity_results"],
        "download": ["downloaded_data"],
    }
    found = []
    for phrase, labels in mapping.items():
        if phrase in info:
            for label in labels:
                if label not in found:
                    found.append(label)
    return found


def _infer_workflow_roles(info_text: str) -> list[str]:
    info = info_text.lower()
    mapping = {
        "download": "data_acquisition",
        "acquiring data": "data_acquisition",
        "visual": "visualization",
        "analy": "analysis",
        "simulate": "simulation",
        "planning": "planning",
        "valuation": "valuation",
        "equity": "equity_assessment",
        "technology": "technology_screening",
    }
    found = []
    for phrase, label in mapping.items():
        if phrase in info and label not in found:
            found.append(label)
    return found


def _infer_typical_tasks(app_id: str, title: str, info_text: str) -> list[str]:
    tasks = []
    normalized_title = _normalize_title(title).lower()
    if normalized_title:
        tasks.append(normalized_title)
    if app_id == "data_manager":
        tasks.extend(["download quest-compatible datasets", "prepare input datasets"])
    elif app_id == "btm":
        tasks.extend(["behind-the-meter analysis", "tariff savings analysis"])
    elif app_id == "valuation":
        tasks.extend(["energy storage valuation", "market revenue analysis"])
    elif app_id == "planning":
        tasks.extend(["capacity expansion planning", "investment planning"])
    elif app_id == "gpt":
        tasks.extend(["data analysis", "data visualization"])
    else:
        summary = _clean_html_text(info_text)
        if summary:
            tasks.append(summary[:120].strip())
    seen = []
    for task in tasks:
        cleaned = str(task).strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return seen


def _extract_launch_details(app_card: dict[str, Any]) -> tuple[str, str]:
    launch = app_card.get("launch", {})
    if isinstance(launch, dict):
        if "type" in launch:
            return str(launch.get("type", "")).strip(), str(launch.get("value", "") or launch.get("value_relpath", "")).strip()
        if "default" in launch and isinstance(launch["default"], dict):
            default = launch["default"]
            return str(default.get("type", "")).strip(), str(default.get("value", "") or default.get("value_relpath", "")).strip()
        if "windows" in launch and isinstance(launch["windows"], dict):
            windows = launch["windows"]
            return str(windows.get("type", "")).strip(), str(windows.get("value", "") or windows.get("value_relpath", "")).strip()
    return "", ""


def _tool_aliases(app_card: dict[str, Any], normalized_name: str) -> list[str]:
    aliases = []
    for value in (
        app_card.get("id", ""),
        app_card.get("search_key", ""),
        normalized_name,
        str(app_card.get("title", "") or ""),
    ):
        cleaned = _clean_html_text(value).lower()
        if cleaned and cleaned not in aliases:
            aliases.append(cleaned)
    return aliases


def load_app_cards(package_root: str | Path | None = None) -> dict[str, Any]:
    app_cards_path = get_app_cards_path(package_root)
    with app_cards_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_active_tool_registry(package_root: str | Path | None = None) -> dict[str, Any]:
    package_root = get_package_root(package_root)
    app_cards_path = get_app_cards_path(package_root)
    loaded = load_app_cards(package_root)
    apps = list(loaded.get("apps", []))

    tools: list[ToolRecord] = []
    for app_card in apps:
        if not isinstance(app_card, dict):
            continue
        if not bool(app_card.get("active", False)):
            continue

        app_id = str(app_card.get("id", "") or "").strip()
        title = str(app_card.get("title", "") or "").strip()
        info_text = str(app_card.get("info", "") or "").strip()
        normalized_name = _normalize_title(title)
        launch_type, launch_value = _extract_launch_details(app_card)

        tools.append(
            ToolRecord(
                tool_id=app_id,
                name=normalized_name or app_id,
                active=True,
                category="quest_tool",
                description=_clean_html_text(info_text),
                input_types=_infer_input_types(info_text),
                output_types=_infer_output_types(info_text),
                typical_tasks=_infer_typical_tasks(app_id, title, info_text),
                limitations=[],
                workflow_roles=_infer_workflow_roles(info_text),
                aliases=_tool_aliases(app_card, normalized_name),
                search_key=str(app_card.get("search_key", "") or "").strip(),
                launch_type=launch_type,
                launch_value=launch_value,
                source_app_card_path=app_cards_path.as_posix(),
                raw_data=app_card,
            )
        )

    registry = {
        "schema_version": TOOL_REGISTRY_SCHEMA_VERSION,
        "updated_at": _iso_now(),
        "source_app_cards_path": app_cards_path.as_posix(),
        "tools": [tool.to_registry_entry() for tool in tools],
    }
    return registry


def write_active_tool_registry(
    package_root: str | Path | None = None,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    package_root = get_package_root(package_root)
    registry_root = get_registry_root(package_root)
    registry_root.mkdir(parents=True, exist_ok=True)

    if registry_path is None:
        registry_path = registry_root / "tools.json"
    registry_path = Path(registry_path)

    registry = build_active_tool_registry(package_root)
    registry_to_write = dict(registry)
    source_path = registry_to_write.get("source_app_cards_path", "")
    try:
        registry_to_write["source_app_cards_path"] = Path(source_path).relative_to(package_root).as_posix()
    except Exception:
        registry_to_write["source_app_cards_path"] = Path(source_path).as_posix() if source_path else ""

    normalized_tools = []
    for tool in registry_to_write.get("tools", []):
        tool_entry = dict(tool)
        tool_source_path = tool_entry.get("source_app_card_path", "")
        try:
            tool_entry["source_app_card_path"] = Path(tool_source_path).relative_to(package_root).as_posix()
        except Exception:
            tool_entry["source_app_card_path"] = Path(tool_source_path).as_posix() if tool_source_path else ""
        normalized_tools.append(tool_entry)
    registry_to_write["tools"] = normalized_tools

    with registry_path.open("w", encoding="utf-8") as handle:
        json.dump(registry_to_write, handle, indent=2)

    return registry_to_write
