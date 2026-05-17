from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any


try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except Exception:  # pragma: no cover - optional external server dependency
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


def external_mcp_available() -> bool:
    return ClientSession is not None and StdioServerParameters is not None and stdio_client is not None


def external_mcp_server_command() -> tuple[str, list[str]]:
    return sys.executable, ["-m", "quest.quest_agent.mcp_server.server"]


def external_mcp_mode_enabled() -> bool:
    return str(os.environ.get("QUEST_MCP_MODE", "") or "").strip().casefold() == "external"


async def _call_external_tool_async(tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
    if not external_mcp_available():
        raise RuntimeError("The optional 'mcp' package is not installed.")
    program, args = external_mcp_server_command()
    params = StdioServerParameters(command=program, args=args, env=dict(os.environ))
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(str(tool_name or "").strip(), dict(arguments or {}))
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured
    content = getattr(result, "content", None)
    if isinstance(content, list) and content:
        first = content[0]
        text = getattr(first, "text", None)
        if isinstance(text, str):
            try:
                return json.loads(text)
            except Exception:
                return {"text": text}
    return result


def call_external_tool(tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
    try:
        return asyncio.run(_call_external_tool_async(tool_name, arguments))
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"External MCP tool call failed for {tool_name}: {exc}") from exc
