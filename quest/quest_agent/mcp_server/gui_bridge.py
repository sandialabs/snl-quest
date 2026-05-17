from __future__ import annotations

import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import error as urlerror
from urllib import request
from typing import Any, Callable

from .session_bridge import get_workspace_session_status


BridgeCallback = Callable[[dict[str, Any]], Any]

_BRIDGE_LOCK = threading.RLock()
_BRIDGE_SERVER: ThreadingHTTPServer | None = None
_BRIDGE_THREAD: threading.Thread | None = None
_BRIDGE_INFO: dict[str, Any] = {}
_BRIDGE_CALLBACKS: dict[str, BridgeCallback] = {}


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=True, default=str).encode("utf-8")
    try:
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        handler.wfile.write(body)
    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
        return


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except Exception:
        length = 0
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    data = json.loads(raw.decode("utf-8"))
    return dict(data or {}) if isinstance(data, dict) else {}


def _operation_from_path(path: str) -> str:
    cleaned = str(path or "").split("?", 1)[0].strip("/")
    if cleaned.startswith("workspace."):
        return cleaned
    if cleaned.startswith("workspace/"):
        return "workspace." + cleaned.split("/", 1)[1].strip().replace("/", ".")
    return cleaned.replace("/", ".")


def _authorized(handler: BaseHTTPRequestHandler, payload: dict[str, Any]) -> bool:
    token = str(_BRIDGE_INFO.get("token", "") or "").strip()
    if not token:
        return True
    header_token = str(handler.headers.get("X-Quest-MCP-Token", "") or "").strip()
    body_token = str(payload.get("token", "") or "").strip()
    return token in {header_token, body_token}


def _dispatch_operation(operation: str, payload: dict[str, Any]) -> Any:
    callbacks = dict(_BRIDGE_CALLBACKS)
    callback = callbacks.get(operation)
    if callback is not None:
        return callback(payload)
    if operation == "workspace.session_status":
        return get_workspace_session_status(str(payload.get("session_id", "") or ""))
    raise KeyError(f"Unsupported GUI bridge operation: {operation}")


class _BridgeHandler(BaseHTTPRequestHandler):
    server_version = "QuEStGUIBridge/0.1"

    def log_message(self, _format: str, *args: Any) -> None:  # pragma: no cover - keep GUI stderr quiet
        return

    def do_GET(self) -> None:
        operation = _operation_from_path(self.path)
        if operation in {"", "status", "workspace.session_status"}:
            payload = {"operation": "workspace.session_status"}
            if not _authorized(self, payload):
                _json_response(self, 401, {"ok": False, "error": "Unauthorized GUI bridge request."})
                return
            _json_response(self, 200, {"ok": True, "result": get_gui_bridge_status()})
            return
        _json_response(self, 404, {"ok": False, "error": f"Unknown GUI bridge endpoint: {operation}"})

    def do_POST(self) -> None:
        try:
            payload = _read_json_body(self)
        except Exception as exc:
            _json_response(self, 400, {"ok": False, "error": f"Invalid JSON body: {exc}"})
            return
        operation = str(payload.get("operation", "") or "").strip() or _operation_from_path(self.path)
        if not _authorized(self, payload):
            _json_response(self, 401, {"ok": False, "operation": operation, "error": "Unauthorized GUI bridge request."})
            return
        try:
            result = _dispatch_operation(operation, payload)
            _json_response(self, 200, {"ok": True, "operation": operation, "result": result})
        except KeyError as exc:
            _json_response(self, 404, {"ok": False, "operation": operation, "error": str(exc)})
        except Exception as exc:
            _json_response(self, 500, {"ok": False, "operation": operation, "error": str(exc)})


def start_gui_bridge(
    *,
    session_id: str = "",
    host: str = "127.0.0.1",
    port: int = 0,
    token: str | None = None,
    callbacks: dict[str, BridgeCallback] | None = None,
) -> dict[str, Any]:
    global _BRIDGE_SERVER, _BRIDGE_THREAD, _BRIDGE_INFO, _BRIDGE_CALLBACKS
    with _BRIDGE_LOCK:
        if _BRIDGE_SERVER is not None:
            if callbacks:
                _BRIDGE_CALLBACKS.update(callbacks)
            if session_id:
                _BRIDGE_INFO["session_id"] = str(session_id or "").strip()
            return dict(_BRIDGE_INFO)
        resolved_token = str(token or "").strip() or secrets.token_urlsafe(24)
        _BRIDGE_CALLBACKS = dict(callbacks or {})
        server = ThreadingHTTPServer((str(host or "127.0.0.1"), int(port or 0)), _BridgeHandler)
        thread = threading.Thread(target=server.serve_forever, name="quest-gui-mcp-bridge", daemon=True)
        thread.start()
        bound_host, bound_port = server.server_address[:2]
        _BRIDGE_SERVER = server
        _BRIDGE_THREAD = thread
        _BRIDGE_INFO = {
            "available": True,
            "host": bound_host,
            "port": int(bound_port),
            "url": f"http://{bound_host}:{int(bound_port)}",
            "token": resolved_token,
            "session_id": str(session_id or "").strip(),
            "operations": [
                "workspace.session_status",
                "workspace.get_canvas_facts",
                "workspace.validate_current_flow",
                "workspace.execute_operation_plan",
            ],
            "source": "quest_gui_mcp_bridge",
        }
        return dict(_BRIDGE_INFO)


def stop_gui_bridge() -> dict[str, Any]:
    global _BRIDGE_SERVER, _BRIDGE_THREAD, _BRIDGE_INFO, _BRIDGE_CALLBACKS
    with _BRIDGE_LOCK:
        server = _BRIDGE_SERVER
        if server is not None:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass
        _BRIDGE_SERVER = None
        _BRIDGE_THREAD = None
        previous = dict(_BRIDGE_INFO)
        _BRIDGE_INFO = {}
        _BRIDGE_CALLBACKS = {}
        return {"stopped": bool(previous), "previous": previous, "source": "quest_gui_mcp_bridge"}


def get_gui_bridge_status() -> dict[str, Any]:
    with _BRIDGE_LOCK:
        if _BRIDGE_SERVER is None:
            configured_url = str(os.environ.get("QUEST_GUI_BRIDGE_URL", "") or "").strip()
            if configured_url:
                return {
                    "available": True,
                    "host": configured_url,
                    "url": configured_url,
                    "token": "***" if os.environ.get("QUEST_GUI_BRIDGE_TOKEN") else "",
                    "source": "quest_gui_mcp_bridge_env",
                    "mode": "external_client",
                }
            return {"available": False, "source": "quest_gui_mcp_bridge"}
        status = dict(_BRIDGE_INFO)
        public_status = dict(status)
        if public_status.get("token"):
            public_status["token"] = "***"
        public_status["workspace_session"] = get_workspace_session_status(str(status.get("session_id", "") or ""))
        return public_status


def get_gui_bridge_connection_info(include_token: bool = False) -> dict[str, Any]:
    with _BRIDGE_LOCK:
        data = dict(_BRIDGE_INFO)
        if data and not include_token:
            data["token"] = "***" if data.get("token") else ""
        return data


def call_gui_bridge_operation(operation: str, payload: dict[str, Any] | None = None, timeout: float = 30.0) -> dict[str, Any]:
    local_info = get_gui_bridge_connection_info(include_token=True)
    bridge_url = str(local_info.get("url", "") or os.environ.get("QUEST_GUI_BRIDGE_URL", "") or "").strip()
    bridge_token = str(local_info.get("token", "") or os.environ.get("QUEST_GUI_BRIDGE_TOKEN", "") or "").strip()
    operation_id = str(operation or "").strip()
    if not bridge_url:
        return {"ok": False, "operation": operation_id, "error": "QuESt GUI bridge URL is not configured."}
    if not operation_id:
        return {"ok": False, "operation": operation_id, "error": "GUI bridge operation is required."}
    body = dict(payload or {})
    body["operation"] = operation_id
    raw_body = json.dumps(body, ensure_ascii=True, default=str).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if bridge_token:
        headers["X-Quest-MCP-Token"] = bridge_token
    req = request.Request(bridge_url.rstrip("/") + "/", data=raw_body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=float(timeout or 30.0)) as response:
            response_body = response.read().decode("utf-8")
        data = json.loads(response_body or "{}")
        return dict(data or {}) if isinstance(data, dict) else {"ok": False, "operation": operation_id, "error": "GUI bridge returned a non-object response."}
    except urlerror.HTTPError as exc:
        try:
            error_body = exc.read().decode("utf-8")
            data = json.loads(error_body or "{}")
            if isinstance(data, dict):
                data.setdefault("ok", False)
                data.setdefault("operation", operation_id)
                data.setdefault("http_status", exc.code)
                return data
        except Exception:
            pass
        return {"ok": False, "operation": operation_id, "http_status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "operation": operation_id, "error": str(exc)}
