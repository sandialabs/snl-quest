from __future__ import annotations

from typing import Any, Callable

from langgraph.graph import END, START, StateGraph


ChatCallbacks = dict[str, Callable[..., Any]]


def _build_flow_analysis_graph():
    graph = StateGraph(dict)

    def analyze_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        update_status = callbacks.get("update_status")
        if update_status is not None:
            update_status("QuESt Agent is analyzing project and current flow...")
        matcher = callbacks.get("run_matcher")
        if matcher is None:
            return {"raw_result": {}}
        raw_result = matcher(
            str(state.get("task_description", "") or ""),
            list(state.get("pinned_context", []) or []),
            list(state.get("attached_files", []) or []),
            str(state.get("model_name", "") or ""),
        )
        return {"raw_result": dict(raw_result or {})}

    def normalize_node(state: dict[str, Any]) -> dict[str, Any]:
        raw = dict(state.get("raw_result", {}) or {})
        return {
            "result": {
                **raw,
                "project_description": str(raw.get("project_description", "") or "").strip(),
                "flow_description": str(raw.get("flow_description", "") or "").strip(),
                "strategy": str(raw.get("strategy", "") or "").strip(),
                "tool_matches": list(raw.get("tool_matches", []) or []),
                "skill_matches": list(raw.get("skill_matches", []) or []),
                "notes": [str(note).strip() for note in list(raw.get("notes", []) or []) if str(note).strip()],
            }
        }

    graph.add_node("analyze", analyze_node)
    graph.add_node("normalize", normalize_node)

    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "normalize")
    graph.add_edge("normalize", END)
    return graph.compile()


def _build_chat_turn_graph():
    graph = StateGraph(dict)

    def route_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        route_func = callbacks.get("route_chat_turn")
        if route_func is None:
            return {
                "route_result": {
                    "action": "analyze_task" if not state.get("task_match_result") else "answer_only",
                    "reason": "",
                    "task_focus": str(state.get("user_prompt", "") or "").strip(),
                }
            }
        return {
            "route_result": route_func(
                str(state.get("user_prompt", "") or ""),
                str(state.get("model_name", "") or ""),
            )
        }

    def analyze_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        update_status = callbacks.get("update_status")
        if update_status is not None:
            update_status("QuESt Agent is analyzing the task and checking tools and skills...")
        analyze_func = callbacks.get("run_analysis")
        if analyze_func is None:
            return {}
        result = analyze_func()
        return {"task_match_result": dict(result or {})}

    def answer_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        update_status = callbacks.get("update_status")
        route_action = str(dict(state.get("route_result", {}) or {}).get("action", "") or "").strip()
        if update_status is not None:
            if route_action == "answer_only":
                update_status("QuESt Agent is preparing a response from the current context...")
        generate_reply = callbacks.get("generate_reply")
        if generate_reply is None:
            return {"final_reply": {"reply": "I couldn't prepare a response right now."}}
        final_reply = generate_reply(
            str(state.get("user_prompt", "") or ""),
            str(state.get("model_name", "") or ""),
        )
        return {"final_reply": dict(final_reply or {})}

    def plan_actions_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        update_status = callbacks.get("update_status")
        if update_status is not None:
            update_status("QuESt Agent is planning canvas actions for the current workflow...")
        planner = callbacks.get("plan_actions")
        if planner is None:
            return {"action_plan": {"reply": "", "actions": []}}
        return {
            "action_plan": dict(
                planner(
                    str(state.get("user_prompt", "") or ""),
                    str(state.get("model_name", "") or ""),
                )
                or {}
            )
        }

    def execute_actions_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        update_status = callbacks.get("update_status")
        if update_status is not None:
            update_status("QuESt Agent is applying changes on the canvas...")
        executor = callbacks.get("execute_actions")
        if executor is None:
            return {"executed_actions": []}
        try:
            executed = executor(dict(state.get("action_plan", {}) or {}))
            return {"executed_actions": list(executed or [])}
        except Exception as exc:
            return {"canvas_error": exc}

    def action_reply_node(state: dict[str, Any]) -> dict[str, Any]:
        callbacks: ChatCallbacks = dict(state.get("callbacks", {}) or {})
        builder = callbacks.get("build_action_reply")
        if builder is None:
            if state.get("canvas_error") is not None:
                return {"final_reply": {"reply": f"I couldn't apply the requested canvas changes.\n\nDetails: {state['canvas_error']}"}}
            executed = list(state.get("executed_actions", []) or [])
            action_plan = dict(state.get("action_plan", {}) or {})
            reply_text = str(action_plan.get("reply", "") or "").strip()
            if executed:
                summary = "\n".join(f"- {item}" for item in executed)
                reply = reply_text + ("\n\n" if reply_text else "") + "Applied canvas actions:\n" + summary
            else:
                reply = reply_text or "I did not apply any canvas changes."
            return {"final_reply": {"reply": reply}}
        return {
            "final_reply": dict(
                builder(
                    dict(state.get("action_plan", {}) or {}),
                    list(state.get("executed_actions", []) or []),
                    error=state.get("canvas_error"),
                )
                or {}
            )
        }

    def route_after_route(state: dict[str, Any]) -> str:
        action = str(dict(state.get("route_result", {}) or {}).get("action", "") or "").strip()
        if action == "analyze_task":
            return "analyze"
        if action == "execute_canvas_action":
            return "plan_actions"
        return "answer"

    graph.add_node("route", route_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("answer", answer_node)
    graph.add_node("plan_actions", plan_actions_node)
    graph.add_node("execute_actions", execute_actions_node)
    graph.add_node("action_reply", action_reply_node)

    graph.add_edge(START, "route")
    graph.add_conditional_edges(
        "route",
        route_after_route,
        {
            "analyze": "analyze",
            "plan_actions": "plan_actions",
            "answer": "answer",
        },
    )
    graph.add_edge("analyze", "answer")
    graph.add_edge("answer", END)
    graph.add_edge("plan_actions", "execute_actions")
    graph.add_edge("execute_actions", "action_reply")
    graph.add_edge("action_reply", END)
    return graph.compile()


_CHAT_TURN_GRAPH = _build_chat_turn_graph()
_FLOW_ANALYSIS_GRAPH = _build_flow_analysis_graph()


def run_chat_turn(
    *,
    user_prompt: str,
    model_name: str,
    callbacks: ChatCallbacks | None = None,
    initial_task_match_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = {
        "user_prompt": str(user_prompt or ""),
        "model_name": str(model_name or ""),
        "callbacks": dict(callbacks or {}),
        "task_match_result": dict(initial_task_match_result or {}),
    }
    final_state = _CHAT_TURN_GRAPH.invoke(state)
    return {
        "route_result": dict(final_state.get("route_result", {}) or {}),
        "task_match_result": dict(final_state.get("task_match_result", {}) or {}),
        "action_plan": dict(final_state.get("action_plan", {}) or {}),
        "executed_actions": list(final_state.get("executed_actions", []) or []),
        "final_reply": dict(final_state.get("final_reply", {}) or {}),
    }


def run_flow_analysis(
    *,
    task_description: str,
    pinned_context: list[str] | None = None,
    attached_files: list[str] | None = None,
    model_name: str,
    callbacks: ChatCallbacks | None = None,
) -> dict[str, Any]:
    state = {
        "task_description": str(task_description or ""),
        "pinned_context": list(pinned_context or []),
        "attached_files": list(attached_files or []),
        "model_name": str(model_name or ""),
        "callbacks": dict(callbacks or {}),
    }
    final_state = _FLOW_ANALYSIS_GRAPH.invoke(state)
    result = dict(final_state.get("result", {}) or {})
    if result:
        return result
    return dict(final_state.get("raw_result", {}) or {})
