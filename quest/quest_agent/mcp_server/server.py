from .tools_skills_manager import (
    analyze_workspace_canvas,
    analyze_workflow_json_template,
    create_skill_from_flow,
    get_skill,
    get_workflow_template,
    list_active_tools,
    list_workspace_actions,
    list_workspace_operations,
    match_tools_and_skills,
    match_skill_task,
    search_skills,
    search_tools,
    summarize_validation_report,
    update_skill_from_flow,
    validate_flow_analysis,
    validate_workspace_action_plan,
    validate_workspace_operation_plan,
)
from .session_bridge import (
    execute_active_workspace_operation_plan,
    get_workspace_session_status,
    set_active_workspace_session,
)
from .gui_bridge import call_gui_bridge_operation, get_gui_bridge_status


try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - optional deployment dependency
    FastMCP = None


def create_server():
    if FastMCP is None:
        raise RuntimeError("The optional 'mcp' package is not installed. Install it to run the QuESt MCP server.")

    server = FastMCP("quest-tools-skills-manager")

    @server.tool()
    def list_active_quest_tools() -> dict:
        return list_active_tools()

    @server.tool()
    def search_quest_tools(query: str, limit: int = 8) -> dict:
        return search_tools(query, limit=limit)

    @server.tool()
    def search_quest_skills(query: str, limit: int = 8) -> dict:
        return search_skills(query, limit=limit)

    @server.tool()
    def match_quest_tools_and_skills(task_text: str, canvas_context: dict | None = None, limit: int = 8) -> dict:
        return match_tools_and_skills(task_text, canvas_context, limit=limit)

    @server.tool()
    def match_quest_skills_task(task_text: str, canvas_context: dict | None = None, limit: int = 8) -> dict:
        return match_skill_task(task_text, canvas_context, limit=limit)

    @server.tool()
    def analyze_quest_workspace_canvas(canvas_snapshot: dict) -> dict:
        return analyze_workspace_canvas(canvas_snapshot)

    @server.tool()
    def analyze_quest_workflow_json_template(workflow_json: dict) -> dict:
        return analyze_workflow_json_template(workflow_json)

    @server.tool()
    def list_quest_workspace_actions() -> dict:
        return list_workspace_actions()

    @server.tool()
    def list_quest_workspace_operations() -> dict:
        return list_workspace_operations()

    @server.tool()
    def validate_quest_workspace_action_plan(action_plan: dict) -> dict:
        return validate_workspace_action_plan(action_plan)

    @server.tool()
    def validate_quest_workspace_operation_plan(operation_plan: dict) -> dict:
        return validate_workspace_operation_plan(operation_plan)

    @server.tool()
    def get_quest_workspace_session_status(session_id: str = "") -> dict:
        return get_workspace_session_status(session_id)

    @server.tool()
    def get_quest_gui_bridge_status() -> dict:
        return get_gui_bridge_status()

    @server.tool()
    def get_quest_gui_workspace_session_status(session_id: str = "") -> dict:
        return call_gui_bridge_operation(
            "workspace.session_status",
            {"session_id": session_id},
        )

    @server.tool()
    def get_quest_gui_workspace_canvas_facts() -> dict:
        return call_gui_bridge_operation("workspace.get_canvas_facts", {})

    @server.tool()
    def validate_quest_gui_current_flow(task_text: str = "") -> dict:
        return call_gui_bridge_operation(
            "workspace.validate_current_flow",
            {"task_text": task_text},
        )

    @server.tool()
    def execute_quest_gui_workspace_operation_plan(operation_plan: dict) -> dict:
        return call_gui_bridge_operation(
            "workspace.execute_operation_plan",
            {"operation_plan": operation_plan},
        )

    @server.tool()
    def set_active_quest_workspace_session(session_id: str) -> dict:
        return {
            "ok": set_active_workspace_session(session_id),
            "session_id": session_id,
            "source": "quest_mcp_workspace_session_bridge",
        }

    @server.tool()
    def execute_active_quest_workspace_operation_plan(operation_plan: dict, session_id: str = "") -> dict:
        executed = execute_active_workspace_operation_plan(operation_plan, session_id=session_id)
        return {
            "executed": executed,
            "execution_notes": list(dict(operation_plan or {}).get("execution_notes", []) or []),
            "source": "quest_mcp_workspace_session_bridge",
        }

    @server.tool()
    def get_quest_skill(skill_id: str) -> dict:
        return get_skill(skill_id)

    @server.tool()
    def get_quest_workflow_template(skill_id: str) -> dict:
        return get_workflow_template(skill_id)

    @server.tool()
    def create_quest_skill_from_flow(payload: dict) -> dict:
        return create_skill_from_flow(payload)

    @server.tool()
    def update_quest_skill_from_flow(skill_id: str, payload: dict) -> dict:
        return update_skill_from_flow(skill_id, payload)

    @server.tool()
    def validate_quest_flow_analysis(flow_analysis: dict, task_text: str = "") -> dict:
        return validate_flow_analysis(flow_analysis, task_text)

    @server.tool()
    def summarize_quest_validation_report(report: dict) -> str:
        return summarize_validation_report(report)

    return server


def main():
    create_server().run()


if __name__ == "__main__":
    main()
