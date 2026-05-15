from .tools_skills_manager import (
    get_skill,
    get_workflow_template,
    list_active_tools,
    search_skills,
    search_tools,
    summarize_validation_report,
    validate_flow_analysis,
)


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
    def get_quest_skill(skill_id: str) -> dict:
        return get_skill(skill_id)

    @server.tool()
    def get_quest_workflow_template(skill_id: str) -> dict:
        return get_workflow_template(skill_id)

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
