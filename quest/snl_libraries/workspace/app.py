import sys
import os
import keyword
import tempfile
import pickle
import inspect, ast, json, socket, subprocess, html, re
import pandas as pd
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
import nbformat as nbf

from NodeGraphQt import NodeGraph, BaseNode, NodeBaseWidget, BackdropNode
from NodeGraphQt.constants import *
from quest.paths import get_path
import quest
base_dir = get_path()

from quest.snl_libraries.workspace.flow.questflow import *


class PythonEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet(
            "QPlainTextEdit { "
            "background: #ffffff; "
            "border: 1px solid #d9e2ec; "
            "font-family: Consolas, 'Courier New', monospace; "
            "font-size: 10pt; "
            "}"
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
            return
        super().keyPressEvent(event)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#2563eb"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r'\bFalse\b', r'\bNone\b', r'\bTrue\b', r'\band\b', r'\bas\b',
            r'\bassert\b', r'\bbreak\b', r'\bclass\b', r'\bcontinue\b',
            r'\bdef\b', r'\bdel\b', r'\belif\b', r'\belse\b', r'\bexcept\b',
            r'\bfinally\b', r'\bfor\b', r'\bfrom\b', r'\bglobal\b',
            r'\bif\b', r'\bimport\b', r'\bin\b', r'\bis\b', r'\blambda\b',
            r'\bnonlocal\b', r'\bnot\b', r'\bor\b', r'\bpass\b',
            r'\braise\b', r'\breturn\b', r'\btry\b', r'\bwhile\b',
            r'\bwith\b', r'\byield\b'
        ]
        self.highlighting_rules.extend((QRegularExpression(pattern), keyword_format) for pattern in keywords)

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#7c3aed"))
        builtins = [
            r'\bprint\b', r'\blen\b', r'\brange\b', r'\bstr\b', r'\bint\b',
            r'\bfloat\b', r'\blist\b', r'\bdict\b', r'\bset\b', r'\btuple\b',
            r'\bopen\b', r'\bsum\b', r'\bmin\b', r'\bmax\b', r'\babs\b',
            r'\benumerate\b', r'\bzip\b'
        ]
        self.highlighting_rules.extend((QRegularExpression(pattern), builtin_format) for pattern in builtins)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#059669"))
        self.highlighting_rules.append((QRegularExpression(r'".*?"|\'.*?\''), string_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6b7280"))
        self.highlighting_rules.append((QRegularExpression(r'#[^\n]*'), comment_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#ea580c"))
        self.highlighting_rules.append((QRegularExpression(r'\b[0-9]+(\.[0-9]+)?\b'), number_format))

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#dc2626"))
        self.highlighting_rules.append((QRegularExpression(r'@[A-Za-z_][A-Za-z0-9_\.]*'), decorator_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class PopOutNotebookEditor(QWidget):
    editorClosed = Signal()

    def __init__(self, editor, update_button, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.update_button = update_button

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(self.editor, 1)
        layout.addWidget(self.update_button, 0)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)

        self.setLayout(layout)
        self.setWindowTitle("Jupyter Notebook")
        self.resize(1200, 800)

    def closeEvent(self, event):
        self.editorClosed.emit()
        event.accept()


class EmbeddedNotebook(QWidget):
    editorClosed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_process = None
        self.server_port = None
        self.current_notebook_path = ""
        self.current_root_dir = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.status_label = QLabel("Notebook not loaded.")
        self.status_label.setWordWrap(True)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        layout.addWidget(self.status_label, 0)

        self.webview = QWebEngineView(self)
        self.webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webview.setMinimumHeight(280)
        layout.addWidget(self.webview, 1)

    def _find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def _build_url(self, notebook_path):
        root_dir = os.path.abspath(self.current_root_dir or os.path.dirname(notebook_path))
        nb_abs = os.path.abspath(notebook_path)
        rel_path = os.path.relpath(nb_abs, root_dir).replace("\\", "/")
        return f"http://127.0.0.1:{self.server_port}/notebooks/{rel_path}"

    def _handle_server_output(self):
        if not self.server_process:
            return
        try:
            text = bytes(self.server_process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        except Exception:
            text = ""
        if not text:
            return
        print(text)
        lower = text.lower()
        if 'http://127.0.0.1:' in lower or 'http://localhost:' in lower:
            self.status_label.setText(f'Loaded notebook: {os.path.basename(self.current_notebook_path)}')
        elif 'no module named notebook' in lower or ('error' in lower and 'notebook' in lower):
            self.status_label.setText('Failed to start Jupyter Notebook. Install the notebook package in this Python environment.')

    def stop_server(self):
        if self.server_process:
            try:
                if self.server_process.state() != QProcess.NotRunning:
                    self.server_process.kill()
                    self.server_process.waitForFinished(2000)
            except Exception:
                pass
        self.server_process = None

    def _start_process(self, program, arguments, root_dir):
        self.server_process = QProcess(self)
        self.server_process.setWorkingDirectory(root_dir)
        self.server_process.setProcessChannelMode(QProcess.MergedChannels)
        self.server_process.readyReadStandardOutput.connect(self._handle_server_output)
        self.server_process.setProgram(program)
        self.server_process.setArguments(arguments)
        self.server_process.start()
        return self.server_process.waitForStarted(5000)

    def _start_jupyter_server(self, root_dir):
        self.stop_server()
        self.server_port = self._find_free_port()
        self.current_root_dir = root_dir

        args = [
            '-m', 'notebook',
            '--no-browser',
            f'--NotebookApp.notebook_dir={root_dir}',
            f'--NotebookApp.port={self.server_port}',
            '--NotebookApp.token=',
            '--NotebookApp.password=',
            '--NotebookApp.allow_origin=*',
        ]
        return self._start_process(sys.executable, args, root_dir)

    def load_notebook(self, notebook_path):
        notebook_path = os.path.abspath(notebook_path)
        root_dir = os.path.abspath(os.path.dirname(notebook_path))

        if self.server_process and self.server_process.state() == QProcess.Running and os.path.abspath(self.current_root_dir) == root_dir:
            self.current_notebook_path = notebook_path
            self.status_label.setText(f'Loading notebook: {os.path.basename(notebook_path)}')

            # Detach from the previous page/session first to reduce websocket races.
            self.webview.setUrl(QUrl("about:blank"))

            def _load_new_url():
                try:
                    self.webview.setUrl(QUrl(self._build_url(notebook_path)))
                    self.webview.show()
                except Exception:
                    pass

            QTimer.singleShot(250, _load_new_url)
            return

        self.current_notebook_path = notebook_path
        self.status_label.setText(f'Starting Jupyter Notebook for: {os.path.basename(notebook_path)}')

        if not self._start_jupyter_server(root_dir):
            self.status_label.setText('Failed to start Jupyter Notebook. Install the notebook package in this Python environment.')
            return

        self.webview.setUrl(QUrl("about:blank"))

        def _first_load():
            try:
                self.webview.setUrl(QUrl(self._build_url(notebook_path)))
                self.webview.show()
            except Exception:
                pass

        QTimer.singleShot(4000, _first_load)

    def closeEvent(self, event):
        self.stop_server()
        self.editorClosed.emit()
        super().closeEvent(event)


class NodeOutputsHtmlWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Outputs")
        self.resize(1100, 750)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.addStretch()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        top_row.addWidget(self.close_button)
        layout.addLayout(top_row)

        self.webview = QWebEngineView(self)
        layout.addWidget(self.webview, 1)

    def load_html(self, html_text):
        self.webview.setHtml(html_text)




class TextEditWidget(QWidget):
    def __init__(self, parent=None):
        super(TextEditWidget, self).__init__(parent)
        self.text_caption = QLabel()
        self.text_caption.setWordWrap(True)
        self.text_caption.setStyleSheet("QLabel { color: blue; font-size: 12pt}")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.text_caption)


class TextNodeWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(TextNodeWidgetWrapper, self).__init__(parent)
        self.set_name('Text Caption')
        self.set_custom_widget(TextEditWidget())

    def get_value(self):
        widget = self.get_custom_widget()
        return widget.text_caption.text()

    def set_value(self, value):
        widget = self.get_custom_widget()
        widget.text_caption.setText(value)


class DataNode(BaseNode):
    __identifier__ = 'QuESt.Workspace'
    NODE_NAME = 'Data Node'

    def __init__(self):
        super(DataNode, self).__init__()
        font = self.view.text_item.font()
        font.setPointSize(12)
        self.view.text_item.setFont(font)

        d_icon = os.path.join(base_dir, "images", "icons", "data_icon.png")
        self.set_icon(d_icon)
        self.set_port_deletion_allowed(mode=True)
        text_node_widget = TextNodeWidgetWrapper(self.view)
        self.add_custom_widget(text_node_widget, tab='Custom')
        self.node_type = 'data_node'
        self.node_value_display = False
        self.node_is_path = False
        self.node_is_from_master = False
        self.node_input_variable = ''
        self.node_input_value = ''
        self.node_function_wrapper = ''
        self.node_imports = ''
        self.node_expose_outputs = []

    def add_dynamic_input(self, name, color=(100, 100, 100)):
        self.add_input(name, color=color)

    def add_dynamic_output(self, name, color=(100, 100, 100)):
        self.add_output(name, color=color)


class BackNode(BackdropNode):
    __identifier__ = 'QuESt.Workspace'
    NODE_NAME = 'Back Node'

    def __init__(self):
        super(BackNode, self).__init__()
        self.set_backdrop_font_size(12)
        self.node_type = 'back_node'
        self.node_input_variable = ''
        self.node_input_value = ''
        self.node_value_display = True
        self.node_function_wrapper = ''
        self.node_imports = ''

    def can_be_deleted(self):
        return True


class PyNode(BaseNode):
    __identifier__ = 'QuESt.Workspace'
    NODE_NAME = 'Py Node'

    def __init__(self):
        super(PyNode, self).__init__()
        font = self.view.text_item.font()
        font.setPointSize(12)
        self.view.text_item.setFont(font)
        p_icon = os.path.join(base_dir, "images", "icons", "python_icon.png")
        self.set_icon(p_icon)
        self.set_port_deletion_allowed(mode=True)
        self.node_type = 'python_node'
        self.node_input_variable = ''
        self.node_input_value = ''
        self.node_value_display = False
        self.node_is_path = False
        self.node_is_from_master = False
        self.node_function_wrapper = ''
        self.node_imports = ''
        self.node_notebook_path = ''
        self.node_expose_outputs = []

    def add_dynamic_input(self, name, color=(100, 100, 100)):
        self.add_input(name, color=color)

    def add_dynamic_output(self, name, color=(100, 100, 100)):
        self.add_output(name, color=color)


class quest_workflow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
        QLabel, QLineEdit, QTextEdit, QTabWidget {
            color: black;
            font-size: 12pt;
        }
        QPushButton {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            padding: 6px 12px;
            font-size: 11pt;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
        QPushButton:disabled {
            background-color: #cbd5e1;
            color: #64748b;
        }
        """)
        self.nodes_df = pd.DataFrame(columns=['node_id', 'node_name', 'node_type', 'node_input_variable', 'node_input_value', 'node_value_display', 'node_is_path', 'node_is_from_master', 'node_expose_outputs', 'node_function_wrapper', 'node_imports', 'node_notebook_path'])
        self.connections_df = pd.DataFrame(columns=['connection_id', 'from_node', 'to_node', 'mapping'])
        self.flow_name = ''
        self.flow_environment_name = 'workflow_env'
        self.flow_environment_path = self._normalize_python_path(sys.executable) if hasattr(self, '_normalize_python_path') else sys.executable.replace('\\', '/')
        self._proxy_wrapper_sync_in_progress = False
        self._suspend_proxy_wrapper_sync = False
        self._last_auto_environment_name = self.flow_environment_name
        self._pending_graph_frame = False

        self.layout = QHBoxLayout(self)
        self.flow_run_widget = QWidget()
        self.flow_run_widget.setFixedWidth(400)
        self.flow_run_layout = QHBoxLayout(self.flow_run_widget)
        self.flow_run_label = QLabel("Flow name:")
        self.flow_run_input = QLineEdit()
        self.flow_run_input.textChanged.connect(self._sync_flow_metadata_from_controls)
        self.flow_run_button = QPushButton("Run")
        self.flow_run_button.setFixedHeight(36)
        self.flow_run_button.clicked.connect(self.run_flow)

        self.flow_run_layout.addWidget(self.flow_run_label)
        self.flow_run_layout.addWidget(self.flow_run_input)
        self.flow_run_layout.addWidget(self.flow_run_button)

        self.flow_type_widget = QWidget()
        self.flow_type_widget.setFixedWidth(400)
        self.flow_type_layout = QHBoxLayout(self.flow_type_widget)
        self.flow_type_label_title = QLabel("Flow type:")
        self.flow_type_label_value = QLabel("sub-flow")
        self.flow_type_label_value.setStyleSheet("QLabel { color: #475569; font-weight: 600; }")
        self.flow_type_layout.addWidget(self.flow_type_label_title)
        self.flow_type_layout.addWidget(self.flow_type_label_value)
        self.flow_type_layout.addStretch(1)

        self.flow_save_widget = QWidget()
        self.flow_save_widget.setFixedWidth(400)
        self.flow_save_layout = QVBoxLayout(self.flow_save_widget)
        self.flow_save_label = QLabel("Save to json file:")
        self.flow_save_mode_combo = QComboBox()
        self.flow_save_mode_combo.addItem("Save as master flow", "master")
        self.flow_save_mode_combo.addItem("Save as independent flow", "independent")
        self.flow_save_mode_combo.currentIndexChanged.connect(self._enforce_valid_save_mode_selection)
        self.flow_save_path = QLabel()
        self.flow_save_button = QPushButton("Save")
        self.flow_save_button.setFixedHeight(36)
        self.flow_save_button.clicked.connect(self.save_flow)

        self.flow_save_layout.addWidget(self.flow_save_label)
        self.flow_save_layout.addWidget(self.flow_save_mode_combo)
        self.flow_save_layout.addWidget(self.flow_save_path)
        self.flow_save_layout.addWidget(self.flow_save_button)

        self.flow_load_widget = QWidget()
        self.flow_load_widget.setFixedWidth(400)
        self.flow_load_layout = QVBoxLayout(self.flow_load_widget)
        self.flow_load_label = QLabel("Load from json file:")
        self.flow_load_path = QLabel()
        self.flow_load_button = QPushButton("Load")
        self.flow_load_button.setFixedHeight(36)
        self.flow_load_button.clicked.connect(self.load_flow)
        self.flow_load_path.setText(self._display_flow_path(self._default_flow_examples_dir()))

        self.flow_load_layout.addWidget(self.flow_load_label)
        self.flow_load_layout.addWidget(self.flow_load_path)
        self.flow_load_layout.addWidget(self.flow_load_button)

        self.flow_result_widget = QWidget()
        self.flow_result_widget.setFixedWidth(400)
        self.flow_result_layout = QVBoxLayout(self.flow_result_widget)
        self.flow_result_label = QLabel()
        self.flow_result_label.setWordWrap(True)
        self.flow_result_label.setStyleSheet("QLabel { color: blue; }")

        self.flow_result_layout.addWidget(self.flow_result_label)
        self.flow_control_container = QWidget()
        self.flow_control_container.setFixedWidth(420)
        self.flow_control_layout = QVBoxLayout(self.flow_control_container)
        self.flow_control_layout.addWidget(self.flow_run_widget)
        self.flow_control_layout.addWidget(self.flow_type_widget)
        self.flow_control_layout.addWidget(self.flow_save_widget)
        self.flow_control_layout.addWidget(self.flow_load_widget)
        self.flow_control_layout.addWidget(self.flow_result_widget)
        self.flow_control_layout.addStretch(1)

        self.graph = NodeGraph()
        self.graph.set_background_color(255, 255, 255)
        self.graph.set_grid_mode(mode=2)
        self.graph.register_node(DataNode)
        self.graph.register_node(PyNode)
        self.graph.register_node(BackNode)
        self.graph_widget = self.graph.widget
        try:
            self.graph_widget.installEventFilter(self)
        except Exception:
            pass
        try:
            graph_view = self.graph_widget.findChild(QGraphicsView)
            if graph_view is not None:
                graph_view.installEventFilter(self)
                if graph_view.viewport() is not None:
                    graph_view.viewport().installEventFilter(self)
        except Exception:
            pass
        self.graph_help_overlay = QFrame(self.graph_widget)
        self.graph_help_overlay.setObjectName("graphHelpOverlay")
        self.graph_help_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.graph_help_overlay.setStyleSheet(
            "QFrame#graphHelpOverlay {"
            "background: rgba(255, 255, 255, 235);"
            "border: 1px solid #cbd5e1;"
            "border-radius: 8px;"
            "}"
            "QLabel { color: #111111; font-size: 10pt; }"
            "QLabel[role='hintHeader'] { color: #111111; font-weight: 600; }"
            "QLabel[role='hintAction'] { color: #666666; font-family: Consolas, 'Courier New', monospace; }"
        )
        self.graph_help_layout = QGridLayout(self.graph_help_overlay)
        self.graph_help_layout.setContentsMargins(12, 10, 12, 10)
        self.graph_help_layout.setHorizontalSpacing(10)
        self.graph_help_layout.setVerticalSpacing(6)
        zoom_label = QLabel("Zoom In/Out")
        zoom_label.setProperty("role", "hintHeader")
        zoom_action = QLabel("Alt + Middle Mouse Button + Drag")
        zoom_action.setProperty("role", "hintAction")
        zoom_or = QLabel("or")
        zoom_scroll = QLabel("Mouse Scroll Up/Down")
        zoom_scroll.setProperty("role", "hintAction")
        pan_label = QLabel("Pan")
        pan_label.setProperty("role", "hintHeader")
        pan_action = QLabel("Alt + Left Mouse Button + Drag")
        pan_action.setProperty("role", "hintAction")
        pan_or = QLabel("or")
        pan_drag = QLabel("Middle Mouse Button + Drag")
        pan_drag.setProperty("role", "hintAction")
        self.graph_help_layout.addWidget(zoom_label, 0, 0)
        self.graph_help_layout.addWidget(zoom_action, 0, 1)
        self.graph_help_layout.addWidget(zoom_or, 0, 2)
        self.graph_help_layout.addWidget(zoom_scroll, 0, 3)
        self.graph_help_layout.addWidget(pan_label, 1, 0)
        self.graph_help_layout.addWidget(pan_action, 1, 1)
        self.graph_help_layout.addWidget(pan_or, 1, 2)
        self.graph_help_layout.addWidget(pan_drag, 1, 3)
        self.graph_help_overlay.adjustSize()
        self.graph_help_overlay.show()
        self._position_graph_help_overlay()
        self.clear_canvas_button = QPushButton("Clear Canvas", self.graph_widget)
        self.clear_canvas_button.setObjectName("clearCanvasButton")
        self.clear_canvas_button.setFixedHeight(34)
        self.clear_canvas_button.setStyleSheet(
            "QPushButton#clearCanvasButton {"
            "background: rgba(255, 255, 255, 235);"
            "color: #991b1b;"
            "border: 1px solid #fca5a5;"
            "border-radius: 8px;"
            "padding: 4px 12px;"
            "font-size: 10pt;"
            "font-weight: 600;"
            "}"
            "QPushButton#clearCanvasButton:hover {"
            "background: rgba(254, 242, 242, 245);"
            "border-color: #ef4444;"
            "}"
        )
        self.clear_canvas_button.clicked.connect(self.clear_canvas)
        self.clear_canvas_button.adjustSize()
        self.clear_canvas_button.show()
        self._position_clear_canvas_button()
        self.master_graph_tab = QWidget()
        self.master_graph_layout = QVBoxLayout(self.master_graph_tab)
        self.master_graph_layout.setContentsMargins(0, 0, 0, 0)
        self.master_graph_layout.setSpacing(0)
        self.master_graph_layout.addWidget(self.graph_widget)
        # master tab removed from workflow
        self.layout.addWidget(self.graph_widget)

        self.id_widget = QWidget()
        self.id_widget.setFixedWidth(400)
        self.id_layout = QHBoxLayout(self.id_widget)
        self.id_label = QLabel("Node ID:")
        self.id_layout.addWidget(self.id_label)

        self.type_widget = QWidget()
        self.type_widget.setFixedWidth(400)
        self.type_layout = QHBoxLayout(self.type_widget)
        self.type_label = QLabel("Node Type:")
        self.type_layout.addWidget(self.type_label)

        self.name_widget = QWidget()
        self.name_widget.setFixedWidth(400)
        self.name_layout = QHBoxLayout(self.name_widget)
        self.name_label = QLabel("Node name:")
        self.name_input = QLineEdit()
        self.name_button = QPushButton("Update")
        self.name_button.clicked.connect(self.update_node_name)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)
        self.name_layout.addWidget(self.name_button)

        self.node_env_widget = QWidget()
        self.node_env_widget.setFixedWidth(400)
        self.node_env_layout = QHBoxLayout(self.node_env_widget)
        self.node_env_label = QLabel("Environment:")
        self.node_env_combo = QComboBox()
        self.node_env_combo.currentIndexChanged.connect(self.update_selected_node_environment)
        self.node_env_layout.addWidget(self.node_env_label)
        self.node_env_layout.addWidget(self.node_env_combo)
        self.node_env_widget.hide()

        self.data_widget = QWidget()
        self.data_widget.setFixedWidth(400)
        self.data_layout = QHBoxLayout(self.data_widget)
        self.data_label = QLabel("Output name:")
        self.data_input = QLineEdit()
        self.data_button = QPushButton("Update")
        self.data_button.clicked.connect(self.update_ports)
        self.data_layout.addWidget(self.data_label)
        self.data_layout.addWidget(self.data_input)
        self.data_layout.addWidget(self.data_button)
        self.data_widget.hide()

        self.value_widget = QWidget()
        self.value_widget.setFixedWidth(400)
        self.value_layout = QVBoxLayout(self.value_widget)
        self.value_label = QLabel("Output value:")
        self.value_input = QLineEdit()
        self.value_checkbox = QCheckBox("Display Value")
        self.value_checkbox.clicked.connect(self.update_data_value)

        self.value_path_checkbox = QCheckBox("Is File Path?")
        self.value_path_checkbox.clicked.connect(self.update_data_value)

        self.value_from_master_checkbox = QCheckBox("Value is from master flow")
        self.value_from_master_checkbox.clicked.connect(self.update_data_node_from_master)

        self.value_button = QPushButton("Update")
        self.value_button.clicked.connect(self.update_data_value)

        self.value_browse_button = QPushButton("Browse")
        self.value_browse_button.setEnabled(False)
        self.value_browse_button.clicked.connect(self.load_path)

        self.value_layout.addWidget(self.value_label)
        self.value_layout.addWidget(self.value_input)
        self.value_layout.addWidget(self.value_checkbox)
        self.value_layout.addWidget(self.value_path_checkbox)
        self.value_layout.addWidget(self.value_browse_button)
        self.value_layout.addWidget(self.value_from_master_checkbox)
        self.value_layout.addWidget(self.value_button)
        self.value_widget.hide()

        self.py_widget = QWidget()
        self.py_widget.setFixedWidth(400)

        self.py_layout = QVBoxLayout(self.py_widget)
        self.py_label = QLabel("Python Wrapper Notebook:")

        self.notebook_view = EmbeddedNotebook()
        self.notebook_view.setMinimumHeight(320)
        self.notebook_preview = PythonEditor()
        self.notebook_preview.setMinimumHeight(220)
        self.notebook_preview_highlighter = PythonSyntaxHighlighter(self.notebook_preview.document())

        self.py_button = QPushButton("Update Python Function")
        self.py_button.clicked.connect(self.update_ports)

        self.py_node_outputs_button = QPushButton("View Node Outputs")
        self.py_node_outputs_button.clicked.connect(self.view_node_outputs_from_selected_node)

        self.py_expose_outputs_widget = QWidget()
        self.py_expose_outputs_widget.hide()
        self.py_expose_outputs_layout = QVBoxLayout(self.py_expose_outputs_widget)
        self.py_expose_outputs_layout.setContentsMargins(0, 0, 0, 0)
        self.py_expose_outputs_layout.setSpacing(4)
        self.py_expose_outputs_label = QLabel("Expose Outputs to Master:")
        self.py_expose_outputs_scroll = QScrollArea()
        self.py_expose_outputs_scroll.setWidgetResizable(True)
        self.py_expose_outputs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.py_expose_outputs_scroll.setMinimumHeight(110)
        self.py_expose_outputs_scroll.setMaximumHeight(140)
        self.py_expose_outputs_list_widget = QWidget()
        self.py_expose_outputs_list_layout = QVBoxLayout(self.py_expose_outputs_list_widget)
        self.py_expose_outputs_list_layout.setContentsMargins(6, 6, 6, 6)
        self.py_expose_outputs_list_layout.setSpacing(4)
        self.py_expose_outputs_list_layout.addStretch()
        self.py_expose_outputs_scroll.setWidget(self.py_expose_outputs_list_widget)
        self.py_expose_outputs_layout.addWidget(self.py_expose_outputs_label)
        self.py_expose_outputs_layout.addWidget(self.py_expose_outputs_scroll)
        self.py_expose_outputs_widget.setEnabled(False)

        self.pop_out_btn = QPushButton("↗")
        self.pop_out_btn.setFixedSize(36, 36)
        self.pop_out_btn.setStyleSheet("QPushButton { font-size: 16pt; padding: 2px; }")
        self.pop_out_btn.clicked.connect(self.toggle_pop_out)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.py_label)
        top_layout.addStretch()
        top_layout.addWidget(self.pop_out_btn)

        self.py_layout.addLayout(top_layout)
        self.py_layout.addWidget(self.notebook_preview)
        self.py_layout.addWidget(self.py_button)
        self.py_layout.addWidget(self.py_node_outputs_button)
        self.py_layout.addWidget(self.py_expose_outputs_widget)

        self.py_editor_window = None
        self.flow_runner_window = None
        self.is_popped_out = False
        self.node_outputs_windows = []

        self.text_widget = QWidget()
        self.text_widget.setFixedWidth(400)
        self.text_layout = QVBoxLayout(self.text_widget)
        self.text_editor = QLabel("Caption:")
        self.text_input = QTextEdit()

        self.text_input.setFixedHeight(200)
        self.text_button = QPushButton("Update Caption")
        self.text_button.clicked.connect(self.update_caption_value)
        self.text_widget.hide()

        self.text_layout.addWidget(self.text_editor)
        self.text_layout.addWidget(self.text_input)
        self.text_layout.addWidget(self.text_button)

        self.env_settings_container = QWidget()
        self.env_settings_container.setFixedWidth(400)
        self.env_settings_layout = QVBoxLayout(self.env_settings_container)
        self.env_settings_layout.setContentsMargins(0, 0, 0, 0)
        self.env_settings_layout.setSpacing(6)

        self.env_name_widget = QWidget()
        self.env_name_widget.setFixedWidth(400)
        self.env_name_layout = QHBoxLayout(self.env_name_widget)
        self.env_name_layout.setContentsMargins(0, 0, 0, 0)
        self.env_name_label = QLabel("Environment name:")
        self.env_name_input = QLineEdit(self.flow_environment_name)
        self.env_name_input.textChanged.connect(self._refresh_environment_status)
        self.env_name_layout.addWidget(self.env_name_label)
        self.env_name_layout.addWidget(self.env_name_input)

        self.env_select_widget = QWidget()
        self.env_select_widget.setFixedWidth(400)
        self.env_select_layout = QHBoxLayout(self.env_select_widget)
        self.env_select_layout.setContentsMargins(0, 0, 0, 0)
        self.env_select_label = QLabel("Detected envs:")
        self.env_select_combo = QComboBox()
        self.env_select_combo.currentIndexChanged.connect(self._on_environment_selector_changed)
        self.env_select_layout.addWidget(self.env_select_label)
        self.env_select_layout.addWidget(self.env_select_combo)

        self.env_path_widget = QWidget()
        self.env_path_widget.setFixedWidth(400)
        self.env_path_layout = QHBoxLayout(self.env_path_widget)
        self.env_path_layout.setContentsMargins(0, 0, 0, 0)
        self.env_path_label = QLabel("Environment path:")
        self.env_path_input = QLineEdit()
        self.env_path_input.setPlaceholderText("Select Python executable path")
        self.env_path_input.textChanged.connect(self._refresh_environment_status)
        self.env_path_layout.addWidget(self.env_path_label)
        self.env_path_layout.addWidget(self.env_path_input)

        self.env_browse_widget = QWidget()
        self.env_browse_widget.setFixedWidth(400)
        self.env_browse_layout = QHBoxLayout(self.env_browse_widget)
        self.env_browse_layout.setContentsMargins(0, 0, 0, 0)
        self.env_browse_layout.addStretch(1)
        self.env_browse_button = QPushButton("Browse")
        self.env_browse_button.setFixedHeight(36)
        self.env_browse_button.clicked.connect(self.browse_environment_path)
        self.env_browse_layout.addWidget(self.env_browse_button)

        self.env_update_button = QPushButton("Update Environment")
        self.env_update_button.setFixedHeight(36)
        self.env_update_button.clicked.connect(self.apply_environment_changes)
        self.env_browse_layout.addWidget(self.env_update_button)

        self.env_status_label = QLabel("1 environment configured")
        self.env_status_label.setStyleSheet("font-size: 10pt; color: #475569;")

        self.env_settings_layout.addWidget(self.env_name_widget)
        self.env_settings_layout.addWidget(self.env_select_widget)
        self.env_settings_layout.addWidget(self.env_path_widget)
        self.env_settings_layout.addWidget(self.env_browse_widget)
        self.env_settings_layout.addWidget(self.env_status_label)
        self.flow_control_layout.insertWidget(0, self.env_settings_container)

        self.properties_container = QWidget()
        self.properties_container.setFixedWidth(420)
        self.properties_layout = QVBoxLayout(self.properties_container)

        self.properties_layout.addWidget(self.id_widget)
        self.properties_layout.addWidget(self.type_widget)
        self.properties_layout.addWidget(self.name_widget)
        self.properties_layout.addWidget(self.py_widget)
        self.properties_layout.addWidget(self.text_widget)
        self.properties_layout.addWidget(self.data_widget)
        self.properties_layout.addWidget(self.value_widget)
        self.properties_layout.addStretch(1)
        self.properties_layout.setAlignment(Qt.AlignTop)
        self.tab_widget = QTabWidget()
        self.tab_widget.setFixedWidth(420)
        self.tab_layout = QHBoxLayout(self.tab_widget)
        self.tab_widget.addTab(self.properties_container, "Node Settings")
        self.tab_widget.addTab(self.flow_control_container, "Flow Control")
        self.layout.addWidget(self.tab_widget)

        self.graph.node_selected.connect(self.on_node_selected)
        self.graph.node_selection_changed.connect(self.on_node_selected)
        self.node_counters = {"DataNode": 0, "PyNode": 0, "TextNode": 0}
        self.notebooks_dir = os.path.join(os.getcwd(), "node_notebooks")
        self._kernel_cache = None
        self._kernel_cache_valid = False
        os.makedirs(self.notebooks_dir, exist_ok=True)
        self.populate_environment_settings_table()
        self._sync_flow_metadata_from_controls()
        self._refresh_save_mode_options()



    def _quest_master_environment_label(self):
        if hasattr(self, 'env_name_input'):
            value = str(self.env_name_input.text()).strip()
            if value:
                return value
        if getattr(self, 'flow_environment_name', ''):
            return str(self.flow_environment_name).strip()
        return self._default_environment_name()

    def _refresh_flow_environment_dropdown(self, selected_name=None):
        self._sync_flow_metadata_from_controls()

    def update_selected_flow_environment(self):
        self._sync_flow_metadata_from_controls()

    def _default_environment_name(self, flow_name=None):
        base_name = str(flow_name if flow_name is not None else getattr(self, "flow_name", "")).strip()
        if not base_name:
            base_name = "workflow"
        safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in base_name.replace(" ", "_"))
        while "__" in safe:
            safe = safe.replace("__", "_")
        safe = safe.strip("_") or "workflow"
        return f"{safe}_env"

    def _sync_flow_metadata_from_controls(self, *args):
        try:
            self.flow_name = str(self.flow_run_input.text()).strip()
        except Exception:
            self.flow_name = ''
        auto_env_name = self._default_environment_name(self.flow_name)
        env_name = auto_env_name
        env_path = self._normalize_python_path(sys.executable)
        try:
            if hasattr(self, 'env_name_input'):
                current_env_name = str(self.env_name_input.text()).strip()
                if not current_env_name or current_env_name == getattr(self, "_last_auto_environment_name", "") or current_env_name == 'quest master':
                    env_name = auto_env_name
                    if current_env_name != auto_env_name:
                        try:
                            self.env_name_input.blockSignals(True)
                            self.env_name_input.setText(auto_env_name)
                        finally:
                            self.env_name_input.blockSignals(False)
                else:
                    env_name = current_env_name
            if hasattr(self, 'env_path_input'):
                entered_path = self._normalize_python_path(self.env_path_input.text().strip())
                if entered_path:
                    env_path = entered_path
        except Exception:
            pass
        self.flow_environment_name = env_name
        self.flow_environment_path = env_path
        self._last_auto_environment_name = auto_env_name

    def _refresh_node_environment_dropdown(self, selected_name=None):
        return

    def _get_env_path_edit(self, row=0, column=1):
        return getattr(self, 'env_path_input', None)

    def _read_environment_rows(self):
        env_name = ''
        python_path = ''
        if hasattr(self, 'env_name_input'):
            env_name = str(self.env_name_input.text()).strip()
        if hasattr(self, 'env_path_input'):
            python_path = self._normalize_python_path(self.env_path_input.text().strip())
        return [{'environment_name': env_name or self._default_environment_name(), 'python_path': python_path or self._normalize_python_path(sys.executable)}]

    def _environment_path_from_name(self, env_name):
        requested = (env_name or '').strip()
        current_name = ''
        current_path = self._normalize_python_path(sys.executable)
        if hasattr(self, 'env_name_input'):
            current_name = str(self.env_name_input.text()).strip()
        if hasattr(self, 'env_path_input'):
            entered_path = self._normalize_python_path(self.env_path_input.text().strip())
            if entered_path:
                current_path = entered_path
        if not requested or requested == current_name or requested == self.flow_environment_name:
            return current_path
        return current_path

    def apply_environment_changes(self):
        try:
            if hasattr(self, 'env_name_input'):
                self.env_name_input.setText(str(self.env_name_input.text()).strip())
            if hasattr(self, 'env_path_input'):
                self.env_path_input.setText(self._normalize_python_path(self.env_path_input.text().strip()))
            self.update_envs()
            self._sync_flow_metadata_from_controls()
            self.populate_environment_settings_table_from_df()
            self._refresh_environment_status()

            parent_workspace = self._find_workspace_parent() if hasattr(self, '_find_workspace_parent') else None
            if parent_workspace is not None and self.get_flow_type() == 'sub-flow':
                try:
                    parent_workspace._sync_proxy_wrapper_for_subflow(self)
                except Exception:
                    pass

            if hasattr(self, 'flow_result_label'):
                self.flow_result_label.setText(
                    f"Environment updated:\n{self.flow_environment_name}\n{self.flow_environment_path}"
                )
        except Exception as e:
            if hasattr(self, 'flow_result_label'):
                self.flow_result_label.setText(f"Failed to update environment:\n{e}")

    def browse_environment_path(self):
        current_path = self._normalize_python_path(self.env_path_input.text().strip()) if hasattr(self, 'env_path_input') else ''
        start_dir = current_path or self._normalize_python_path(os.path.dirname(sys.executable))
        chosen_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python Executable",
            start_dir,
            "Python Executable (python.exe python python3 python3.11 python3.13);;All Files (*)"
        )
        if chosen_path and hasattr(self, 'env_path_input'):
            self.env_path_input.setText(self._resolve_python_interpreter_path(chosen_path))
            self._refresh_environment_status()

    def _position_graph_help_overlay(self):
        if not hasattr(self, "graph_help_overlay") or self.graph_help_overlay is None:
            return
        if not hasattr(self, "graph_widget") or self.graph_widget is None:
            return
        margin = 16
        self.graph_help_overlay.adjustSize()
        overlay_size = self.graph_help_overlay.sizeHint()
        x = max(margin, self.graph_widget.width() - overlay_size.width() - margin)
        y = max(margin, self.graph_widget.height() - overlay_size.height() - margin)
        self.graph_help_overlay.setGeometry(x, y, overlay_size.width(), overlay_size.height())
        self.graph_help_overlay.raise_()

    def _position_clear_canvas_button(self):
        if not hasattr(self, "clear_canvas_button") or self.clear_canvas_button is None:
            return
        if not hasattr(self, "graph_widget") or self.graph_widget is None:
            return
        margin = 16
        self.clear_canvas_button.adjustSize()
        button_size = self.clear_canvas_button.sizeHint()
        x = max(margin, self.graph_widget.width() - button_size.width() - margin)
        y = margin
        self.clear_canvas_button.setGeometry(x, y, button_size.width(), button_size.height())
        self.clear_canvas_button.raise_()

    def clear_canvas(self):
        try:
            all_nodes = list(self.graph.all_nodes())
        except Exception:
            all_nodes = []

        if not all_nodes:
            if hasattr(self, "flow_result_label"):
                self.flow_result_label.setText("Canvas is already empty.")
            return

        flow_label = "master flow" if self.get_flow_type() == "master-flow" else "sub-flow"
        response = QMessageBox.warning(
            self,
            "Clear Canvas",
            f"Are you sure you want to clear everything in this {flow_label}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response != QMessageBox.Yes:
            return

        parent_workspace = self._find_workspace_parent()
        try:
            if (
                self.get_flow_type() == "master-flow"
                and parent_workspace is not None
                and hasattr(parent_workspace, "_clear_all_subflows")
            ):
                parent_workspace._clear_all_subflows()
        except Exception:
            pass

        try:
            self.graph.clear_session()
        except Exception:
            pass

        self.node_counters = {"DataNode": 0, "PyNode": 0, "TextNode": 0}
        self.nodes_df = pd.DataFrame(columns=self.nodes_df.columns)
        self.connections_df = pd.DataFrame(columns=self.connections_df.columns)
        try:
            self.update_flow()
        except Exception:
            pass
        self._sync_parent_proxy_wrapper_from_current_graph()
        try:
            self.request_graph_frame()
        except Exception:
            pass
        try:
            if parent_workspace is not None and hasattr(parent_workspace, "sync_workflow_ui"):
                parent_workspace.sync_workflow_ui(self)
        except Exception:
            pass

        if hasattr(self, "flow_result_label"):
            self.flow_result_label.setText(f"{flow_label.capitalize()} canvas cleared.")

    def _sync_node_environments_with_available_list(self):
        return

    def update_selected_node_environment(self):
        return

    def _normalize_python_path(self, python_path):
        try:
            if not python_path:
                return ""
            return os.path.abspath(str(python_path)).replace("\\", "/")
        except Exception:
            return str(python_path).replace("\\", "/")

    def _resolve_python_interpreter_path(self, python_path):
        normalized = self._normalize_python_path(python_path)
        if not normalized:
            return ""

        os_path = normalized.replace("/", os.sep)
        candidate_paths = []

        if os.path.isfile(os_path):
            candidate_paths.append(os_path)
        elif os.path.isdir(os_path):
            base_name = os.path.basename(os_path).lower()
            if base_name in ("scripts", "bin"):
                candidate_paths.extend([
                    os.path.join(os_path, "python.exe"),
                    os.path.join(os_path, "pythonw.exe"),
                    os.path.join(os_path, "python"),
                    os.path.join(os_path, "python3"),
                ])
                try:
                    for child in sorted(os.listdir(os_path)):
                        if re.fullmatch(r"python\d+(?:\.\d+)*", child.lower()):
                            candidate_paths.append(os.path.join(os_path, child))
                except Exception:
                    pass
            else:
                candidate_paths.extend(self._python_executable_candidates(os_path))

        for candidate in candidate_paths:
            if not os.path.isfile(candidate):
                continue
            name = os.path.basename(candidate).lower()
            if not re.fullmatch(r"python(?:w)?(?:\d+(?:\.\d+)*)?(?:\.exe)?", name):
                continue
            if os.name != "nt" and not os.access(candidate, os.X_OK):
                continue
            return self._normalize_python_path(candidate)

        return normalized

    def _python_executable_candidates(self, env_root):
        env_root = os.path.abspath(str(env_root))
        candidates = []
        if os.name == "nt":
            candidates.extend([
                os.path.join(env_root, "Scripts", "python.exe"),
                os.path.join(env_root, "Scripts", "python"),
            ])
        else:
            bin_dir = os.path.join(env_root, "bin")
            candidates.extend([
                os.path.join(bin_dir, "python"),
                os.path.join(bin_dir, "python3"),
            ])
            if os.path.isdir(bin_dir):
                try:
                    for child in sorted(os.listdir(bin_dir)):
                        if re.fullmatch(r"python\d+(?:\.\d+)*", child):
                            candidates.append(os.path.join(bin_dir, child))
                except Exception:
                    pass
        return [self._normalize_python_path(path) for path in candidates]

    def _discover_available_python_environments(self):
        discovered = []
        seen_paths = set()
        current_python = self._normalize_python_path(sys.executable)
        discovered.append({
            "label": f"Current QuESt Python ({os.path.basename(current_python)})",
            "path": current_python,
        })
        seen_paths.add(current_python)

        candidate_env_dirs = [
            os.path.join(os.path.dirname(quest.__file__), "app_envs"),
            os.path.join(base_dir, "app_envs"),
            os.path.join(os.getcwd(), "snl-quest", "quest", "app_envs"),
        ]
        seen_env_dirs = set()
        for env_dir in candidate_env_dirs:
            normalized_dir = os.path.abspath(env_dir)
            if normalized_dir in seen_env_dirs or not os.path.isdir(normalized_dir):
                continue
            seen_env_dirs.add(normalized_dir)
            try:
                children = sorted(os.listdir(normalized_dir))
            except Exception:
                continue
            for child in children:
                child_path = os.path.join(normalized_dir, child)
                if not os.path.isdir(child_path) or child == "__pycache__":
                    continue
                for candidate in self._python_executable_candidates(child_path):
                    if candidate in seen_paths or not self._is_valid_python_path(candidate):
                        continue
                    discovered.append({
                        "label": f"{child} ({os.path.basename(candidate)})",
                        "path": candidate,
                    })
                    seen_paths.add(candidate)
                    break

        return discovered

    def _refresh_environment_selector(self, selected_path=None):
        if not hasattr(self, "env_select_combo"):
            return
        normalized_selected = self._normalize_python_path(selected_path or "")
        combo = self.env_select_combo
        options = self._discover_available_python_environments()
        try:
            combo.blockSignals(True)
            combo.clear()
            selected_index = -1
            for index, option in enumerate(options):
                combo.addItem(option["label"], option["path"])
                if normalized_selected and option["path"] == normalized_selected:
                    selected_index = index
            combo.addItem("Custom...", "__custom__")
            combo.setCurrentIndex(selected_index if selected_index >= 0 else combo.count() - 1)
        finally:
            combo.blockSignals(False)

    def _on_environment_selector_changed(self, index):
        if not hasattr(self, "env_select_combo") or not hasattr(self, "env_path_input"):
            return
        selected_path = self.env_select_combo.itemData(index)
        if not selected_path or selected_path == "__custom__":
            return
        normalized_path = self._resolve_python_interpreter_path(selected_path)
        if self._normalize_python_path(self.env_path_input.text().strip()) == normalized_path:
            return
        try:
            self.env_path_input.blockSignals(True)
            self.env_path_input.setText(normalized_path)
        finally:
            self.env_path_input.blockSignals(False)
        self._refresh_environment_status()

    def _default_flow_examples_dir(self):
        candidates = [
            os.path.join(os.getcwd(), "snl-quest", "quest", "snl_libraries", "workspace", "examples"),
            os.path.join(os.path.dirname(__file__), "examples"),
        ]
        for candidate in candidates:
            abs_candidate = os.path.abspath(candidate)
            if os.path.isdir(abs_candidate):
                return abs_candidate
        return os.path.abspath(candidates[0])

    def _display_flow_path(self, path):
        normalized = self._normalize_python_path(path)
        if not normalized:
            return ""
        try:
            cwd = os.path.abspath(os.getcwd())
            rel_path = os.path.relpath(normalized.replace("/", os.sep), cwd)
            if not rel_path.startswith(".."):
                return rel_path.replace("\\", "/")
        except Exception:
            pass
        return normalized



    def _is_valid_python_path(self, python_path):
        try:
            if not python_path:
                return False
            resolved = self._resolve_python_interpreter_path(python_path)
            path = os.path.abspath(str(resolved).replace("/", os.sep))
            if not os.path.isfile(path):
                return False
            name = os.path.basename(path).lower()
            is_python_name = bool(re.fullmatch(r"python(?:w)?(?:\d+(?:\.\d+)*)?(?:\.exe)?", name))
            if not is_python_name:
                return False
            if os.name != "nt" and not os.access(path, os.X_OK):
                return False
            return True
        except Exception:
            return False

    def _apply_path_validation_style(self, path_widget, python_path):
        valid = self._is_valid_python_path(python_path)
        if hasattr(path_widget, 'setStyleSheet'):
            if valid:
                path_widget.setStyleSheet(
                    "QLineEdit { color: #166534; background: #ecfdf5; border: 1px solid #86efac; border-radius: 6px; padding: 4px 6px; }"
                )
                path_widget.setToolTip("Valid Python interpreter path")
            else:
                path_widget.setStyleSheet(
                    "QLineEdit { color: #991b1b; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; padding: 4px 6px; }"
                )
                path_widget.setToolTip("Invalid Python interpreter path")
        return valid
    def _add_environment_row_widget(self, row, env_name="", python_path=""):
        # legacy no-op now that environment is edited directly in line edits.
        if hasattr(self, 'env_name_input') and env_name:
            self.env_name_input.setText(env_name)
        if hasattr(self, 'env_path_input') and python_path:
            self.env_path_input.setText(self._normalize_python_path(python_path))
        self._refresh_environment_status()
    def on_environment_table_clicked(self, row, column):
        return
    def populate_environment_settings_table(self):
        default_name = self.flow_environment_name or self._default_environment_name()
        default_path = self.flow_environment_path or self._normalize_python_path(sys.executable)
        if hasattr(self, 'env_name_input'):
            self.env_name_input.setText(default_name)
        if hasattr(self, 'env_path_input'):
            self.env_path_input.setText(default_path)
        self._refresh_environment_selector(default_path)
        self._refresh_environment_status()

    def populate_environment_settings_table_from_df(self):
        env_name = self.flow_environment_name or self._default_environment_name()
        python_path = self.flow_environment_path or self._normalize_python_path(sys.executable)
        if hasattr(self, 'env_name_input'):
            self.env_name_input.setText(env_name)
        if hasattr(self, 'env_path_input'):
            self.env_path_input.setText(python_path)
        self._refresh_environment_selector(python_path)
        self._refresh_environment_status()

    def _next_default_environment_name(self):
        return self._default_environment_name()
    def _ensure_add_row(self):
        return

    def add_environment_row(self, env_name="", python_path=""):
        if hasattr(self, 'env_name_input') and env_name:
            self.env_name_input.setText(env_name)
        if hasattr(self, 'env_path_input') and python_path:
            self.env_path_input.setText(self._normalize_python_path(python_path))
        self._refresh_environment_status()
    def _refresh_environment_status(self):
        path_text = ''
        if hasattr(self, 'env_path_input'):
            path_text = self.env_path_input.text().strip()
            self._apply_path_validation_style(self.env_path_input, path_text)
        self._refresh_environment_selector(path_text)
        valid_count = 1 if self._is_valid_python_path(path_text) else 0
        if hasattr(self, 'env_status_label'):
            self.env_status_label.setText(f"1 environment configured • {valid_count} valid")
        self._sync_flow_metadata_from_controls()

    def update_envs(self):
        self._sync_flow_metadata_from_controls()

    def toggle_pop_out(self):
        if not self.is_popped_out:
            self.py_layout.removeWidget(self.notebook_preview)
            self.py_layout.removeWidget(self.py_button)
            self.py_layout.removeWidget(self.py_node_outputs_button)
            self.notebook_preview.setParent(None)
            self.py_button.setParent(None)
            self.py_node_outputs_button.setParent(None)
            self.py_expose_outputs_widget.setParent(None)

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(8)

            # Reparent widgets explicitly into the pop-out container so they can be detached cleanly later.
            self.notebook_view.setParent(container)
            self.py_button.setParent(container)
            self.py_node_outputs_button.setParent(container)
            self.py_expose_outputs_widget.setParent(container)

            container_layout.addWidget(self.notebook_view, 1)
            container_layout.addWidget(self.py_button, 0)
            container_layout.addWidget(self.py_node_outputs_button, 0)
            container_layout.addWidget(self.py_expose_outputs_widget, 0)

            selected_nodes = self.graph.selected_nodes()
            if len(selected_nodes) == 1 and isinstance(selected_nodes[0], PyNode):
                node = selected_nodes[0]
                notebook_path = getattr(node, 'node_notebook_path', '') or ''
                if notebook_path and os.path.exists(notebook_path):
                    self._editor_to_notebook(notebook_path)
                    self.notebook_view.load_notebook(notebook_path)

            self.py_editor_window = QWidget()
            self.py_editor_window.setAttribute(Qt.WA_DeleteOnClose, True)
            self.py_editor_window.setWindowTitle("Jupyter Notebook")
            self.py_editor_window.resize(1200, 800)
            outer = QVBoxLayout(self.py_editor_window)
            outer.setContentsMargins(8, 8, 8, 8)
            outer.setSpacing(8)
            outer.addWidget(container, 1)

            self.py_editor_window.destroyed.connect(self.auto_dock_back_in)
            self.py_editor_window.show()

            self.pop_out_btn.setText("↙")
            self.is_popped_out = True
        else:
            self.re_embed_editor()

    def auto_dock_back_in(self, *args):
        if self.is_popped_out:
            self.re_embed_editor()

    def re_embed_editor(self):
        selected_nodes = self.graph.selected_nodes()
        selected_notebook_path = ""
        if len(selected_nodes) == 1 and isinstance(selected_nodes[0], PyNode):
            selected_notebook_path = getattr(selected_nodes[0], 'node_notebook_path', '') or ''

        if self.py_editor_window:
            # Detach live widgets from the pop-out window before it closes, otherwise
            # WA_DeleteOnClose can delete the underlying C++ objects.
            try:
                self.notebook_view.setParent(None)
            except Exception:
                pass
            try:
                self.py_button.setParent(None)
            except Exception:
                pass
            try:
                self.py_node_outputs_button.setParent(None)
                self.py_expose_outputs_widget.setParent(None)
            except Exception:
                pass

            try:
                self.py_editor_window.destroyed.disconnect(self.auto_dock_back_in)
            except Exception:
                pass
            try:
                self.py_editor_window.close()
            except Exception:
                pass

        if selected_notebook_path and os.path.exists(selected_notebook_path):
            self._notebook_to_editor(selected_notebook_path)

        self.py_layout.insertWidget(1, self.notebook_preview)
        self.py_layout.insertWidget(2, self.py_button)
        self.py_layout.insertWidget(3, self.py_node_outputs_button)
        self.py_layout.insertWidget(4, self.py_expose_outputs_widget)
        self.pop_out_btn.setText("↗")
        self.is_popped_out = False
        self.py_editor_window = None

    def _sanitize_node_name_for_file(self, name):
        return "".join(ch if (ch.isalnum() or ch in ("_", "-", ".")) else "_" for ch in name)

    def _notebook_filename(self, node_name, node_id):
        safe_name = self._sanitize_node_name_for_file(node_name)
        return f"{safe_name}_{node_id}.ipynb"

    def _default_notebook_code(self, node_name):
        return (
            "import pandas as pd\n"
            "import numpy as np\n\n"
            f"def {node_name}_function(x):\n"
            "    return {'output': x}\n"
        )

    def _create_notebook_template(self, notebook_path, node_name, python_path=None, env_name=None):
        os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
        nb = nbf.v4.new_notebook()
        nb.cells = [
            nbf.v4.new_markdown_cell(f"# {node_name}\n\nNotebook backing this PyNode."),
            nbf.v4.new_code_cell(self._default_notebook_code(node_name)),
        ]
        with open(notebook_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
        self._apply_notebook_kernel(notebook_path, python_path or sys.executable, env_name or self._quest_master_environment_label())

    def _ensure_node_notebook(self, node):
        path = getattr(node, "node_notebook_path", "") or ""
        if path and os.path.exists(path):
            return path
        notebook_path = os.path.join(
            self.notebooks_dir,
            self._notebook_filename(node.name(), node.id)
        )
        if not os.path.exists(notebook_path):
            self._create_notebook_template(
                notebook_path,
                node.name()
            )
        else:
            self._apply_notebook_kernel(
                notebook_path
            )
        node.node_notebook_path = notebook_path
        return notebook_path

    def _notebook_to_code(self, notebook_path):
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbf.read(f, as_version=4)
        code_cells = []
        for cell in nb.cells:
            if cell.cell_type == "code":
                src = (cell.source or "").strip()
                if src:
                    code_cells.append(src)
        return "\n\n".join(code_cells)

    def _editor_to_notebook(self, notebook_path):
        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbf.read(f, as_version=4)

            code = self.notebook_preview.toPlainText()
            updated = False
            for cell in nb.cells:
                if cell.cell_type == "code":
                    cell.source = code
                    updated = True
                    break

            if not updated:
                nb.cells.append(nbf.v4.new_code_cell(code))

            with open(notebook_path, "w", encoding="utf-8") as f:
                nbf.write(nb, f)
        except Exception as e:
            if hasattr(self, "flow_result_label"):
                self.flow_result_label.setText(f"Editor → Notebook sync failed:\n{e}")

    def _notebook_to_editor(self, notebook_path):
        try:
            code = self._notebook_to_code(notebook_path)
            self.notebook_preview.setPlainText(code)
        except Exception as e:
            if hasattr(self, "flow_result_label"):
                self.flow_result_label.setText(f"Notebook → Editor sync failed:\n{e}")

    def _write_notebook_from_legacy_python(self, node):
        notebook_path = self._ensure_node_notebook(node)

        imports_text = getattr(node, "node_imports", "") or ""
        wrapper_text = getattr(node, "node_function_wrapper", "") or ""

        code_parts = []
        if str(imports_text).strip():
            code_parts.append(str(imports_text).strip())
        if str(wrapper_text).strip():
            code_parts.append(str(wrapper_text).strip())

        code = "\n\n".join(code_parts).strip()
        if not code:
            code = self._default_notebook_code(node.name())

        nb = nbf.v4.new_notebook()
        nb.cells = [
            nbf.v4.new_markdown_cell(f"# {node.name()}\n\nMigrated from legacy flow JSON."),
            nbf.v4.new_code_cell(code),
        ]

        with open(notebook_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

        self._apply_notebook_kernel(
            notebook_path
        )

        node.node_notebook_path = notebook_path
        return notebook_path

    def _rename_pynode_notebook_and_wrapper(self, node, old_name, new_name):
        old_func = f"{old_name}_function"
        new_func = f"{new_name}_function"

        old_path = getattr(node, "node_notebook_path", "") or ""
        new_path = os.path.join(
            self.notebooks_dir,
            self._notebook_filename(new_name, node.id)
        )

        if not old_path or not os.path.exists(old_path):
            if getattr(node, "node_imports", "") or getattr(node, "node_function_wrapper", ""):
                old_path = self._write_notebook_from_legacy_python(node)
            else:
                old_path = self._ensure_node_notebook(node)

        if old_path and os.path.exists(old_path):
            with open(old_path, "r", encoding="utf-8") as f:
                nb = nbf.read(f, as_version=4)

            changed = False
            for cell in nb.cells:
                if cell.cell_type == "code" and old_func in (cell.source or ""):
                    cell.source = cell.source.replace(old_func, new_func)
                    changed = True

            for cell in nb.cells:
                if cell.cell_type == "markdown" and old_name in (cell.source or ""):
                    cell.source = cell.source.replace(old_name, new_name)
                    changed = True

            if getattr(node, "node_function_wrapper", ""):
                node.node_function_wrapper = node.node_function_wrapper.replace(old_func, new_func)

            if not changed:
                for cell in nb.cells:
                    if cell.cell_type != "code" or not (cell.source or "").strip():
                        continue
                    try:
                        parsed = ast.parse(cell.source)
                        func_defs = [n for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef)]
                        if func_defs:
                            src = cell.source
                            first_name = func_defs[0].name
                            cell.source = src.replace(f"def {first_name}(", f"def {new_func}(", 1)
                            changed = True
                            break
                    except Exception:
                        pass

            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            with open(new_path, "w", encoding="utf-8") as f:
                nbf.write(nb, f)

            self._apply_notebook_kernel(
                new_path
            )

            try:
                if os.path.abspath(old_path) != os.path.abspath(new_path) and os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                pass
        else:
            self._create_notebook_template(
                new_path,
                new_name
            )

        node.node_notebook_path = new_path
        return new_path

    def _kernel_name_for_python_path(self, python_path, env_name=None):
        label = (env_name or os.path.basename(os.path.dirname(str(python_path))) or "python").strip()
        safe = self._sanitize_node_name_for_file(f"quest-workspace-{label}")
        return safe.lower()

    def _kernel_display_name_for_python_path(self, python_path, env_name=None):
        label = (env_name or os.path.basename(os.path.dirname(str(python_path))) or str(python_path)).strip()
        return f"Python ({label})"

    def _list_jupyter_kernels(self, force_refresh=False):
        if self._kernel_cache_valid and self._kernel_cache is not None and not force_refresh:
            return self._kernel_cache

        try:
            result = subprocess.run(
                [sys.executable, "-m", "jupyter", "kernelspec", "list", "--json"],
                capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout or "{}")
            self._kernel_cache = data.get("kernelspecs", {}) if isinstance(data, dict) else {}
            self._kernel_cache_valid = True
            return self._kernel_cache
        except Exception:
            return {}

    def _ensure_kernel_for_python_path(self, python_path, env_name=None):
        python_path = self._normalize_python_path(python_path or sys.executable)
        kernel_name = self._kernel_name_for_python_path(python_path, env_name)
        kernels = self._list_jupyter_kernels()
        if kernel_name in kernels:
            return kernel_name

        python_cmd = python_path.replace("/", os.sep)
        subprocess.run(
            [python_cmd, "-m", "pip", "install", "ipykernel"],
            check=True
        )
        subprocess.run(
            [
                python_cmd, "-m", "ipykernel", "install", "--user",
                "--name", kernel_name,
                "--display-name", self._kernel_display_name_for_python_path(python_path, env_name)
            ],
            check=True
        )
        self._kernel_cache_valid = False
        return kernel_name

    def _notebook_has_expected_kernel(self, notebook_path, python_path=None, env_name=None):
        try:
            python_path = self._normalize_python_path(python_path or sys.executable)
            env_name = (env_name or self._quest_master_environment_label()).strip()
            expected_name = self._kernel_name_for_python_path(python_path, env_name)

            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbf.read(f, as_version=4)

            kernelspec = nb.metadata.get("kernelspec", {})
            current_name = str(kernelspec.get("name", "")).strip()
            return current_name == expected_name
        except Exception:
            return False

    def _apply_notebook_kernel(self, notebook_path, python_path=None, env_name=None):
        notebook_path = os.path.abspath(notebook_path)
        python_path = self._normalize_python_path(python_path or sys.executable)
        env_name = (env_name or self._quest_master_environment_label()).strip()

        if self._notebook_has_expected_kernel(notebook_path, python_path, env_name):
            return self._kernel_name_for_python_path(python_path, env_name)

        kernel_name = self._ensure_kernel_for_python_path(python_path, env_name)
        display_name = self._kernel_display_name_for_python_path(python_path, env_name)

        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbf.read(f, as_version=4)

        nb.metadata["kernelspec"] = {
            "display_name": display_name,
            "language": "python",
            "name": kernel_name
        }
        nb.metadata["language_info"] = {
            "name": "python",
            "version": "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        }

        with open(notebook_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

        return kernel_name

    def _safe_json_default(self, obj):
        try:
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient="records")
            return str(obj)
        except Exception:
            return repr(obj)

    def _node_outputs_payload_to_html(self, payload):
        if not isinstance(payload, dict):
            payload = {"value": payload}

        title = payload.get("title", "Node Outputs")

        parts = [
            "<html><head><meta charset='utf-8'>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; color: #222; }",
            "h1 { margin-bottom: 20px; }",
            ".card { background: white; border: 1px solid #d9d9d9; border-radius: 10px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }",
            ".kpi { font-size: 32px; font-weight: bold; color: #1f4e79; }",
            "table { border-collapse: collapse; width: 100%; margin-top: 8px; }",
            "th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }",
            "th { background: #eee; }",
            "pre { white-space: pre-wrap; word-wrap: break-word; margin: 0; }",
            "</style></head><body>",
            f"<h1>{html.escape(str(title))}</h1>",
        ]

        for key, value in payload.items():
            if key == "title":
                continue

            parts.append("<div class='card'>")
            parts.append(f"<h3>{html.escape(str(key))}</h3>")

            if isinstance(value, pd.DataFrame):
                try:
                    parts.append(value.to_html(index=False, border=0, classes="dataframe"))
                except Exception:
                    parts.append(f"<pre>{html.escape(repr(value))}</pre>")
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                parts.append(f"<div class='kpi'>{html.escape(str(value))}</div>")
            elif isinstance(value, str):
                parts.append(f"<pre>{html.escape(value)}</pre>")
            elif isinstance(value, (dict, list, tuple)):
                try:
                    pretty = json.dumps(value, indent=2, default=self._safe_json_default)
                except Exception:
                    pretty = repr(value)
                parts.append(f"<pre>{html.escape(pretty)}</pre>")
            else:
                parts.append(f"<pre>{html.escape(repr(value))}</pre>")

            parts.append("</div>")

        parts.append("</body></html>")
        return "".join(parts)

    def _show_node_outputs_payload(self, payload, node_name=None):
        html_text = self._node_outputs_payload_to_html(payload)

        if not hasattr(self, "node_outputs_windows"):
            self.node_outputs_windows = []

        window = NodeOutputsHtmlWindow(None)
        window.setAttribute(Qt.WA_DeleteOnClose, True)

        if node_name:
            window.setWindowTitle(f"Node Outputs - {node_name}")
        else:
            window.setWindowTitle("Node Outputs")

        window.load_html(html_text)
        window.show()
        window.raise_()
        window.activateWindow()

        self.node_outputs_windows.append(window)

        def _cleanup(*args):
            try:
                self.node_outputs_windows.remove(window)
            except ValueError:
                pass

        window.destroyed.connect(_cleanup)

    def _build_node_outputs_subflow(self, target_node):
        self.update_flow()

        target_id = target_node.id
        connections_df = self.connections_df.copy()
        nodes_df = self.nodes_df.copy()

        needed = {target_id}
        changed = True

        while changed:
            changed = False
            incoming = connections_df[connections_df["to_node"].isin(needed)]
            for from_id in incoming["from_node"].tolist():
                if from_id not in needed:
                    needed.add(from_id)
                    changed = True

        sub_nodes_df = nodes_df[nodes_df["node_id"].isin(needed)].copy()
        sub_connections_df = connections_df[
            connections_df["from_node"].isin(needed) & connections_df["to_node"].isin(needed)
        ].copy()

        return sub_nodes_df.reset_index(drop=True), sub_connections_df.reset_index(drop=True)

    def _run_node_outputs_subflow(self, target_node):
        sub_nodes_df, sub_connections_df = self._build_node_outputs_subflow(target_node)

        cp_flow = flow(
            flow_name=f"{target_node.name()}_node_outputs",
            nodes_df=sub_nodes_df,
            connections_df=sub_connections_df
        )

        cp_flow.set_inputs()
        cp_flow.get_outputs(key=None)
        cp_flow.make()

        exec_scope = {}
        exec(cp_flow.main_py, exec_scope, exec_scope)

        target_var_name = None
        for _, row in sub_nodes_df.iterrows():
            if row["node_id"] == target_node.id:
                target_var_name = f"node{row['node_id']}"
                break

        if not target_var_name or target_var_name not in exec_scope:
            raise ValueError(f"Could not locate instantiated node for '{target_node.name()}'.")

        target_runtime_node = exec_scope[target_var_name]
        outputs = target_runtime_node.get_outputs()
        return outputs

    def view_node_outputs_from_selected_node(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) != 1 or not isinstance(selected_nodes[0], PyNode):
            return

        node = selected_nodes[0]

        try:
            result = self._run_node_outputs_subflow(node)

            if not isinstance(result, dict):
                QMessageBox.information(
                    self,
                    "Node Outputs",
                    "This node did not return a dictionary of outputs."
                )
                return

            payload = {"title": f"Node Outputs - {node.name()}"}
            for key, value in result.items():
                if not str(key).startswith("_"):
                    payload[key] = value

            self._show_node_outputs_payload(payload, node.name())

        except Exception as e:
            QMessageBox.critical(
                self,
                "Node Outputs Error",
                f"Failed to view node outputs:\n{e}"
            )

    def normalize_layout_icons(self, layout_dict):
        if not isinstance(layout_dict, dict):
            return layout_dict
        nodes = layout_dict.get("nodes", {})
        if not isinstance(nodes, dict):
            return layout_dict
        for _, node_data in nodes.items():
            if not isinstance(node_data, dict):
                continue
            icon_path = node_data.get("icon")
            if isinstance(icon_path, str) and icon_path:
                node_data["icon"] = icon_path.replace('\\', '/')
        return layout_dict

    def update_flow(self):
        nodes_data = []
        self.flow_result_label.setText('')
        for node in self.graph.all_nodes():
            node_data = [
                node.id,
                node.name(),
                getattr(node, 'node_type', ''),
                getattr(node, 'node_input_variable', ''),
                getattr(node, 'node_input_value', ''),
                getattr(node, 'node_value_display', False),
                getattr(node, 'node_is_path', False),
                getattr(node, 'node_is_from_master', False),
                getattr(node, 'node_expose_outputs', []),
                getattr(node, 'node_function_wrapper', ''),
                getattr(node, 'node_imports', ''),
                getattr(node, 'node_notebook_path', '')]
            nodes_data.append(node_data)
        self.nodes_df = pd.DataFrame(
            nodes_data,
            columns=['node_id', 'node_name', 'node_type', 'node_input_variable', 'node_input_value', 'node_value_display', 'node_is_path', 'node_is_from_master', 'node_expose_outputs', 'node_function_wrapper', 'node_imports', 'node_notebook_path']
        )

        connections_data = []
        graph_session = self.graph.serialize_session()
        if 'connections' in graph_session:
            connections = graph_session['connections']
            for i, connection in enumerate(connections, start=1):
                connection_id = i
                from_node = connection['out'][0]
                to_node = connection['in'][0]
                mapping = {connection['out'][1]: connection['in'][1]}
                connections_data.append([connection_id, from_node, to_node, mapping])

        self.connections_df = pd.DataFrame(
            connections_data,
            columns=['connection_id', 'from_node', 'to_node', 'mapping']
        )

        # Keep the Environment Settings tab synchronized with the saved dataframe,
        # without resetting it back to the default quest master row.
        self.populate_environment_settings_table_from_df()

        selected_nodes = self.graph.selected_nodes()
        selected_name = self._quest_master_environment_label()
        if len(selected_nodes) == 1:
            selected_name = getattr(selected_nodes[0], 'node_environment_name', self._quest_master_environment_label())
        self._refresh_node_environment_dropdown(selected_name)

        if (
            self.get_flow_type() != 'master-flow'
            and not getattr(self, '_proxy_wrapper_sync_in_progress', False)
            and not getattr(self, '_suspend_proxy_wrapper_sync', False)
        ):
            parent_workspace = self._find_workspace_parent()
            if parent_workspace is not None and hasattr(parent_workspace, '_sync_proxy_wrapper_for_subflow'):
                try:
                    parent_workspace._sync_proxy_wrapper_for_subflow(self)
                except Exception:
                    pass

    def _create_flow_runner_notebook(self, script_path, flow_name):
        script_path = os.path.abspath(script_path)
        flow_stub = self._sanitize_node_name_for_file(flow_name or 'flow_run')
        notebook_path = os.path.join(os.path.dirname(script_path), f"{flow_stub}_runner.ipynb")

        kernel_name = self._ensure_kernel_for_python_path(sys.executable, self._quest_master_environment_label())
        display_name = self._kernel_display_name_for_python_path(sys.executable, self._quest_master_environment_label())

        code = (
            f'script_path = r"{script_path}"\n'
            'print(f"Running: {script_path}")\n'
            '%run "$script_path"\n'
        )

        nb = nbf.v4.new_notebook()
        nb.metadata["kernelspec"] = {
            "display_name": display_name,
            "language": "python",
            "name": kernel_name
        }
        nb.metadata["language_info"] = {
            "name": "python",
            "version": "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        }
        nb.cells = [
            nbf.v4.new_markdown_cell(
                f"# {flow_name or 'Flow'} runner\n\n"
                "Run the first code cell below to execute the generated Python flow script using `%run`."
            ),
            nbf.v4.new_code_cell(code),
        ]
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
        return notebook_path

    def _open_flow_runner_notebook(self, notebook_path):
        if not hasattr(self, "runner_notebook_window") or self.runner_notebook_window is None:
            self.runner_notebook_view = EmbeddedNotebook()
            self.runner_update_button = QPushButton("Close")
            self.runner_update_button.clicked.connect(
                lambda: self.runner_notebook_window.close() if self.runner_notebook_window else None
            )

            self.runner_notebook_window = PopOutNotebookEditor(
                self.runner_notebook_view,
                self.runner_update_button
            )
            self.runner_notebook_window.setWindowTitle("Flow Runner Notebook")

        self.runner_notebook_view.load_notebook(notebook_path)
        self.runner_notebook_window.show()
        self.runner_notebook_window.raise_()
        self.runner_notebook_window.activateWindow()

    # def _quest_root_bootstrap(self, basedir=None):
    #     quest_root = basedir or base_dir or get_path()
    #     quest_root = os.path.abspath(str(quest_root)).replace("\\", "/")
    #     return (
    #         "import os\n"
    #         "import sys\n"
    #         f"QUEST_ROOT = r'{quest_root}'\n"
    #         "if QUEST_ROOT not in sys.path:\n"
    #         "    sys.path.insert(0, QUEST_ROOT)\n"
    #     )

    # def _inject_quest_root_into_script(self, script_path, basedir=None):
    #     script_path = os.path.abspath(str(script_path))
    #     if not os.path.exists(script_path):
    #         return script_path

    #     bootstrap = self._quest_root_bootstrap(basedir)
    #     with open(script_path, 'r', encoding='utf-8') as f:
    #         script_text = f.read()

    #     if "QUEST_ROOT = r'" in script_text:
    #         return script_path

    #     with open(script_path, 'w', encoding='utf-8') as f:
    #         f.write(bootstrap + "\n" + script_text)

    #     return script_path

    def run_flow(self):
        try:
            self.update_flow()
            flow_name = self.flow_run_input.text()
            self.flow = flow(flow_name=flow_name, nodes_df=self.nodes_df, connections_df=self.connections_df)
            self.flow.set_inputs()
            self.flow.get_outputs(key='Show')
            self.flow.make()
            self.flow.save('./')
            script_path = self.flow.py_file_name
            # script_path = self._inject_quest_root_into_script(script_path, base_dir)
            notebook_path = self._create_flow_runner_notebook(script_path, flow_name)
            self._open_flow_runner_notebook(notebook_path)
            self.flow_result_label.setText(f"Opened flow runner notebook:\n{notebook_path}")
        except subprocess.CalledProcessError as e:
            self.flow_result_label.setText(f"Failed to prepare notebook kernel:\n{e}")
        except Exception as e:
            self.flow_result_label.setText(f"Failed to run flow:\n{e}")

    def set_flow_type(self, flow_type):
        flow_type = (flow_type or "sub-flow").strip().lower()
        if flow_type not in {"master-flow", "sub-flow"}:
            flow_type = "sub-flow"
        self.flow_type_label_value.setText(flow_type)
        self._refresh_save_mode_options()

    def _can_save_as_independent_flow(self):
        if self.get_flow_type() != "master-flow":
            return True
        parent_workspace = self._find_workspace_parent()
        if parent_workspace is None:
            return True
        try:
            return len(parent_workspace._subflow_workflows()) == 0
        except Exception:
            return True

    def _refresh_save_mode_options(self):
        combo = getattr(self, "flow_save_mode_combo", None)
        if combo is None:
            return

        independent_enabled = self._can_save_as_independent_flow()
        try:
            model = combo.model()
            item = model.item(1) if model is not None else None
            if item is not None:
                item.setEnabled(independent_enabled)
                tooltip = ""
                if not independent_enabled:
                    tooltip = "Remove all subflows before saving the master flow as an independent flow."
                item.setToolTip(tooltip)
        except Exception:
            pass

        tooltip = ""
        if not independent_enabled:
            tooltip = "Save as independent flow is disabled for the master flow while subflows exist."
        try:
            combo.setToolTip(tooltip)
        except Exception:
            pass

        self._enforce_valid_save_mode_selection()

    def _enforce_valid_save_mode_selection(self, *args):
        combo = getattr(self, "flow_save_mode_combo", None)
        if combo is None:
            return

        if combo.currentData() == "independent" and not self._can_save_as_independent_flow():
            try:
                combo.blockSignals(True)
                combo.setCurrentIndex(0)
            finally:
                combo.blockSignals(False)

    def get_flow_type(self):
        flow_type = (self.flow_type_label_value.text() or "sub-flow").strip().lower()
        if flow_type not in {"master-flow", "sub-flow"}:
            flow_type = "sub-flow"
        return flow_type

    def get_flow_display_name(self):
        """Return the user-facing flow name from this workflow's flow_run_input."""
        name = ""
        if hasattr(self, 'flow_run_input') and self.flow_run_input is not None:
            try:
                name = str(self.flow_run_input.text()).strip()
            except Exception:
                name = ""
        return name or "Untitled Flow"

    def _serialize_independent_flow_json_data(self):
        self.update_envs()
        previous_suspend = getattr(self, "_suspend_proxy_wrapper_sync", False)
        self._suspend_proxy_wrapper_sync = True
        try:
            self.update_flow()
        finally:
            self._suspend_proxy_wrapper_sync = previous_suspend
        nodes_df_json = self.nodes_df.to_json(orient='records')
        connection_df_json = self.connections_df.to_json(orient='records')
        layout_dict = self.graph.serialize_session()
        self._sync_flow_metadata_from_controls()
        return {
            "flow_name": self.get_flow_display_name(),
            # Independent files must always be portable into a sub-flow tab.
            # A master workflow saved as an independent file should therefore
            # serialize as a plain sub-flow, not as a master-flow.
            "flow_type": "sub-flow",
            "flow_environment_name": self.flow_environment_name,
            "flow_environment_path": self.flow_environment_path,
            "flow_layout": layout_dict,
            "nodes_df": json.loads(nodes_df_json),
            "connections_df": json.loads(connection_df_json)
        }

    def _deserialize_flow_json_data(self, flow_json_data):
        flow_name = flow_json_data.get('flow_name', '')
        self.flow_run_input.setText(flow_name)
        self.set_flow_type(flow_json_data.get('flow_type', self.get_flow_type()))

        loaded_env_name = str(flow_json_data.get('flow_environment_name', '')).strip()
        loaded_env_path = self._normalize_python_path(str(flow_json_data.get('flow_environment_path', '')).strip())

        if (not loaded_env_name or not loaded_env_path) and isinstance(flow_json_data.get('environments_df', None), list):
            envs_list = flow_json_data.get('environments_df', [])
            for row in envs_list:
                if not isinstance(row, dict):
                    continue
                if not loaded_env_name:
                    loaded_env_name = str(row.get('environment_name', '')).strip()
                if not loaded_env_path:
                    loaded_env_path = self._normalize_python_path(str(row.get('python_path', '')).strip())
                if loaded_env_name and loaded_env_path:
                    break

        self.flow_environment_name = loaded_env_name or self._default_environment_name(flow_name)
        self.flow_environment_path = loaded_env_path or self._normalize_python_path(sys.executable)
        self._last_auto_environment_name = self._default_environment_name(flow_name)
        self.populate_environment_settings_table_from_df()

        layout_dict = flow_json_data['flow_layout']
        if hasattr(self, 'normalize_layout_icons'):
            layout_dict = self.normalize_layout_icons(layout_dict)

        self.graph.clear_session()
        self.graph.deserialize_session(layout_dict)
        self.request_graph_frame()

        nodesdf_list = flow_json_data['nodes_df']
        data_node_rename_map = {}
        for loaded_node in self.graph.all_nodes():
            if not isinstance(loaded_node, DataNode):
                continue
            old_loaded_name = str(loaded_node.name() or "").strip()
            new_loaded_name = self.parent()._sanitize_data_node_name(old_loaded_name, exclude_node=loaded_node) if hasattr(self.parent(), "_sanitize_data_node_name") else old_loaded_name
            if new_loaded_name != old_loaded_name:
                old_pos = loaded_node.pos()
                loaded_node.set_name(new_loaded_name)
                loaded_node.set_pos(old_pos[0], old_pos[1])
                data_node_rename_map[old_loaded_name] = new_loaded_name
        if data_node_rename_map:
            for node_data in nodesdf_list:
                if node_data.get('node_type') == 'data_node':
                    original_name = str(node_data.get('node_name', '') or '').strip()
                    if original_name in data_node_rename_map:
                        node_data['node_name'] = data_node_rename_map[original_name]

        existing_nodes = {str(node.name()): node for node in self.graph.all_nodes()}
        for node_data in nodesdf_list:
            node_name = node_data['node_name']
            print("JSON node_name =", repr(node_name))
            print("Available loaded node names =", [repr(n) for n in existing_nodes.keys()])
            if node_name in existing_nodes:
                node = existing_nodes[node_name]
                print(node.properties())
                node.node_type = node_data.get('node_type', '')
                node.node_input_variable = node_data.get('node_input_variable', '')
                node.node_input_value = node_data.get('node_input_value', '')
                node.node_value_display = node_data.get('node_value_display', False)
                node.node_is_path = node_data.get('node_is_path', False)
                node.node_is_from_master = bool(node_data.get('node_is_from_master', False))
                expose_outputs = node_data.get('node_expose_outputs', [])
                node.node_expose_outputs = list(expose_outputs) if isinstance(expose_outputs, list) else []
                node.node_function_wrapper = node_data.get('node_function_wrapper', '')
                node.node_imports = node_data.get('node_imports', '')
                if isinstance(node, PyNode):
                    node.node_notebook_path = node_data.get('node_notebook_path', '')
                    notebook_path = node.node_notebook_path
                    has_legacy_code = bool(
                        (node.node_imports and str(node.node_imports).strip()) or
                        (node.node_function_wrapper and str(node.node_function_wrapper).strip())
                    )
                    if notebook_path and os.path.exists(notebook_path):
                        pass
                    elif has_legacy_code:
                        self._write_notebook_from_legacy_python(node)
                    else:
                        self._ensure_node_notebook(node)
                if node.node_type == 'back_node':
                    node.set_text(text='')
                    node.set_text(text=node.node_input_value)

                print(node.id, node.node_type, node.node_input_variable, node.node_input_value, node.node_value_display, node.node_function_wrapper)
            else:
                print(f"NO MATCH FOR NODE NAME: {repr(node_name)}")

    def save_flow(self):
        save_mode = "independent"
        if hasattr(self, "flow_save_mode_combo"):
            save_mode = str(self.flow_save_mode_combo.currentData() or "independent").strip().lower()

        parent_workspace = self._find_workspace_parent()
        flow_name = self.get_flow_display_name()

        try:
            if save_mode == "master":
                if self.get_flow_type() != "master-flow":
                    QMessageBox.warning(
                        self,
                        "Invalid Save Option",
                        "Save as master flow is only allowed for the master flow.\n\nPlease switch to the Master tab or choose 'Save as independent flow'."
                    )
                    return
                if parent_workspace is None or getattr(parent_workspace, 'master_workflow', None) is not self:
                    QMessageBox.warning(
                        self,
                        "Invalid Save Context",
                        "Save as master flow is only available from the active master workflow."
                    )
                    return
                flow_json_data = parent_workspace._serialize_master_flow_json_data()
            else:
                if self.get_flow_type() == "master-flow" and parent_workspace is not None:
                    subflows = parent_workspace._subflow_workflows()
                    if len(subflows) > 0:
                        QMessageBox.warning(
                            self,
                            "Invalid Save Option",
                            "The master flow cannot be saved as an independent flow while subflows exist.\n\nUse 'Save as master flow' instead, or remove all subflows first."
                        )
                        return
                flow_json_data = self._serialize_independent_flow_json_data()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Flow Error",
                f"The flow could not be prepared for saving.\n\nDetails: {e}"
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Flow JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        self.flow_save_path.setText(path)

        try:
            with open(path, 'w') as json_file:
                json.dump(flow_json_data, json_file, indent=4)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Flow Error",
                f"Failed to save the flow file.\n\nDetails: {e}"
            )
            return

        mode_label = "master flow" if save_mode == "master" else "independent flow"
        QMessageBox.information(
            self,
            "Flow Saved",
            f"'{flow_name}' was saved successfully as a {mode_label}."
        )

    def load_path(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select File or Folder")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)

        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                raw_path = selected[0]
                path_text = f'"{raw_path}"'
                self.value_input.setText(path_text)

    def load_flow(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Flow JSON", self._default_flow_examples_dir(), "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        self.flow_load_path.setText(self._display_flow_path(path))

        try:
            with open(path, 'r') as file:
                flow_json_data = json.load(file)
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Load Flow Error",
                "The selected JSON file does not exist. Please check the file path and try again."
            )
            return
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self,
                "Invalid JSON File",
                f"The selected file is not a valid flow JSON file.\n\nDetails: {e}"
            )
            return
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Flow Error",
                f"An error occurred while reading the flow file.\n\nDetails: {e}"
            )
            return

        requested_flow_type = str(flow_json_data.get('flow_type', 'sub-flow')).strip().lower()
        if requested_flow_type not in {'master-flow', 'sub-flow'}:
            requested_flow_type = 'sub-flow'
        has_subflows = isinstance(flow_json_data.get('subflows_df'), list) and len(flow_json_data.get('subflows_df', [])) > 0

        # Backward compatibility: older independent files saved from the master
        # workflow were incorrectly tagged as ``master-flow`` even though they
        # contained no subflows. Treat those files as plain independent flows.
        if requested_flow_type == 'master-flow' and not has_subflows:
            requested_flow_type = 'sub-flow'
            flow_json_data['flow_type'] = 'sub-flow'

        parent_workspace = self._find_workspace_parent()
        is_master_context = parent_workspace is not None and getattr(parent_workspace, 'master_workflow', None) is self

        try:
            if requested_flow_type == 'master-flow' and has_subflows:
                if not is_master_context:
                    QMessageBox.warning(
                        self,
                        "Invalid Load Target",
                        "A master flow file cannot be loaded into a sub-flow.\n\nPlease switch to the Master tab and load it there."
                    )
                    return
                parent_workspace._load_master_flow_json_data(flow_json_data, path)
                QMessageBox.information(
                    self,
                    "Flow Loaded",
                    f"Master flow '{flow_json_data.get('flow_name', 'Untitled Flow')}' was loaded successfully with its subflows."
                )
                return

            if (
                requested_flow_type == 'sub-flow'
                and parent_workspace is not None
                and getattr(parent_workspace, 'master_workflow', None) is self
                and parent_workspace.tab_widget.currentWidget() is getattr(parent_workspace, 'master_tab', None)
            ):
                # Loading an independent flow into the master tab should reset the workspace
                # and load that flow directly into the master workflow, with no subflows.
                parent_workspace._clear_all_subflows()
                self._deserialize_flow_json_data(flow_json_data)
                self.flow_load_path.setText(self._display_flow_path(path))
                self.set_flow_type('master-flow')
                parent_workspace.activate_workflow(self)
                parent_workspace.sync_workflow_ui(self)
                QMessageBox.information(
                    self,
                    "Flow Loaded",
                    f"Independent flow '{flow_json_data.get('flow_name', 'Untitled Flow')}' was loaded into the Master flow."
                )
                return

            if requested_flow_type == 'master-flow' and not has_subflows and not is_master_context:
                QMessageBox.warning(
                    self,
                    "Invalid Load Target",
                    "A master flow file cannot be loaded into a sub-flow.\n\nPlease switch to the Master tab and load it there."
                )
                return

            self._deserialize_flow_json_data(flow_json_data)
            if parent_workspace is not None and hasattr(parent_workspace, 'sync_workflow_ui'):
                parent_workspace.sync_workflow_ui(self)
            QMessageBox.information(
                self,
                "Flow Loaded",
                f"Flow '{flow_json_data.get('flow_name', 'Untitled Flow')}' was loaded successfully."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Flow Error",
                f"The flow could not be loaded.\n\nDetails: {e}"
            )
            return


    def _clear_py_expose_outputs_checkboxes(self):
        try:
            while self.py_expose_outputs_list_layout.count():
                item = self.py_expose_outputs_list_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        except Exception:
            return
        self.py_expose_outputs_list_layout.addStretch()

    def _refresh_py_expose_outputs_menu(self, node=None):
        self._clear_py_expose_outputs_checkboxes()

        selected_nodes = self.graph.selected_nodes()
        if node is None:
            if len(selected_nodes) != 1 or not isinstance(selected_nodes[0], PyNode):
                self.py_expose_outputs_widget.setVisible(False)
                self.py_expose_outputs_widget.setEnabled(False)
                return
            node = selected_nodes[0]

        if self.get_flow_type() == "master-flow":
            self.py_expose_outputs_widget.setVisible(False)
            self.py_expose_outputs_widget.setEnabled(False)
            return

        output_names = [str(name).strip() for name in list(node.outputs().keys()) if str(name).strip()]
        exposed = [str(name).strip() for name in getattr(node, "node_expose_outputs", []) if str(name).strip()]
        valid_exposed = [name for name in exposed if name in output_names]
        node.node_expose_outputs = valid_exposed

        self.py_expose_outputs_widget.setVisible(True)
        self.py_expose_outputs_widget.setEnabled(True)

        if not output_names:
            label = QLabel("(No outputs available)")
            label.setEnabled(False)
            self.py_expose_outputs_list_layout.insertWidget(0, label)
            return

        for out_name in output_names:
            checkbox = QCheckBox(out_name)
            checkbox.setChecked(out_name in valid_exposed)
            checkbox.toggled.connect(lambda checked, name=out_name, n=node: self._toggle_py_output_exposure(n, name, checked))
            self.py_expose_outputs_list_layout.insertWidget(self.py_expose_outputs_list_layout.count() - 1, checkbox)

    def _toggle_py_output_exposure(self, node, output_name, checked):
        if node is None or not isinstance(node, PyNode):
            return
        current = [str(name).strip() for name in getattr(node, "node_expose_outputs", []) if str(name).strip()]
        if checked:
            if output_name not in current:
                current.append(output_name)
        else:
            current = [name for name in current if name != output_name]
        node.node_expose_outputs = current

        parent_workspace = self._find_workspace_parent()
        if parent_workspace is not None and hasattr(parent_workspace, "_sync_proxy_wrapper_for_subflow"):
            try:
                parent_workspace._sync_proxy_wrapper_for_subflow(self)
            except Exception:
                pass

        self._refresh_py_expose_outputs_menu(node)

    def on_node_selected(self):
        self.update_flow()
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            self.tab_widget.setCurrentIndex(0)
            if isinstance(selected_nodes[0], PyNode):
                self.py_widget.show()
                node = selected_nodes[0]
                notebook_path = getattr(node, 'node_notebook_path', '')
                has_legacy_code = bool(
                    (getattr(node, 'node_imports', '') or '').strip() or
                    (getattr(node, 'node_function_wrapper', '') or '').strip()
                )
                if not notebook_path or not os.path.exists(notebook_path):
                    if has_legacy_code:
                        notebook_path = self._write_notebook_from_legacy_python(node)
                    else:
                        notebook_path = self._ensure_node_notebook(node)
                try:
                    preview_code = self._notebook_to_code(notebook_path)
                except Exception:
                    preview_code = ""
                self.notebook_preview.setPlainText(preview_code)
                self.data_widget.hide()
                self.value_widget.hide()
                self.text_widget.hide()
                self._refresh_py_expose_outputs_menu(node)

            elif isinstance(selected_nodes[0], DataNode):
                self.py_widget.hide()
                self.text_widget.hide()
                self.py_expose_outputs_widget.setVisible(False)
                self.py_expose_outputs_widget.setVisible(False)
                self.py_expose_outputs_widget.setEnabled(False)
                self._clear_py_expose_outputs_checkboxes()
                self.data_widget.show()
                self.value_widget.show()

                node = selected_nodes[0]
                self.data_input.setText(node.node_input_variable)
                self.value_input.setText(node.node_input_value)
                self.value_checkbox.setChecked(node.node_value_display)
                self.value_path_checkbox.setChecked(getattr(node, "node_is_path", False))
                self.value_from_master_checkbox.setChecked(bool(getattr(node, "node_is_from_master", False)))
                self._refresh_data_node_settings_state(node)

            else:
                self.py_widget.hide()
                self.data_widget.hide()
                self.value_widget.hide()
                self.py_expose_outputs_widget.setEnabled(False)
                self._clear_py_expose_outputs_checkboxes()
                self.text_widget.show()
                self.text_input.setText(selected_nodes[0].node_input_value)

            self.name_input.setText(selected_nodes[0].name())
            node_id = selected_nodes[0].id
            node_type = selected_nodes[0].type_
            try:
                node_outputs = list(selected_nodes[0].outputs().keys())
                if len(node_outputs) > 0:
                    self.data_input.setText(f"{node_outputs[0]}")
            except Exception:
                pass
            self.id_label.setText(f"Node ID: {node_id}")
            self.type_label.setText(f"Node Type: {node_type}")

        else:
            self.py_widget.hide()
            self.data_widget.hide()
            self.value_widget.hide()
            self.text_widget.hide()
            self.name_input.setText(None)
            self.id_label.setText("Node ID:")
            self.type_label.setText("Node Type:")
            self.data_input.setText(None)
            self.value_input.setText(None)
            self.text_input.setText(None)
            self.value_path_checkbox.setChecked(False)
            self.value_from_master_checkbox.setChecked(False)
            self.value_browse_button.setEnabled(False)
            self.py_expose_outputs_widget.setVisible(False)
            self.py_expose_outputs_widget.setEnabled(False)
            self._clear_py_expose_outputs_checkboxes()

    def _refresh_data_node_settings_state(self, node=None):
        if node is None:
            selected_nodes = self.graph.selected_nodes()
            if len(selected_nodes) != 1 or not isinstance(selected_nodes[0], DataNode):
                return
            node = selected_nodes[0]

        is_master_flow = (self.get_flow_type() == "master-flow")
        is_from_master = bool(getattr(node, "node_is_from_master", False))

        if is_master_flow:
            is_from_master = False
            node.node_is_from_master = False
            try:
                self.value_from_master_checkbox.blockSignals(True)
                self.value_from_master_checkbox.setChecked(False)
            finally:
                self.value_from_master_checkbox.blockSignals(False)
            self.value_from_master_checkbox.setEnabled(False)
        else:
            self.value_from_master_checkbox.setEnabled(True)

        widgets_to_toggle = [
            self.value_input,
            self.value_checkbox,
            self.value_path_checkbox,
            self.value_browse_button,
        ]

        enabled = not is_from_master
        for widget in widgets_to_toggle:
            widget.setEnabled(enabled)

        if enabled:
            self.value_browse_button.setEnabled(bool(getattr(node, "node_is_path", False)))

    def update_data_node_from_master(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) != 1 or not isinstance(selected_nodes[0], DataNode):
            return

        node = selected_nodes[0]
        old_pos = node.pos()

        if self.get_flow_type() == "master-flow":
            node.node_is_from_master = False
            try:
                self.value_from_master_checkbox.blockSignals(True)
                self.value_from_master_checkbox.setChecked(False)
            finally:
                self.value_from_master_checkbox.blockSignals(False)
        else:
            node.node_is_from_master = self.value_from_master_checkbox.isChecked()
            if node.node_is_from_master:
                node.node_value_display = False
                try:
                    widget = node.get_widget('Text Caption')
                    widget.set_value("")
                except Exception:
                    pass
                try:
                    self.value_checkbox.blockSignals(True)
                    self.value_checkbox.setChecked(False)
                finally:
                    self.value_checkbox.blockSignals(False)

        self._refresh_data_node_settings_state(node)

        parent_workspace = self._find_workspace_parent()
        if parent_workspace is not None and hasattr(parent_workspace, "_sync_proxy_wrapper_for_subflow"):
            try:
                parent_workspace._sync_proxy_wrapper_for_subflow(self)
            except Exception:
                pass

        node.set_pos(old_pos[0], old_pos[1])

    def update_node_name(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) != 1:
            return

        node = selected_nodes[0]
        old_name = node.name()
        new_name = (self.name_input.text() or "").strip()
        if isinstance(node, DataNode):
            parent_workspace = self._find_workspace_parent()
            if parent_workspace is not None and hasattr(parent_workspace, "_sanitize_data_node_name"):
                corrected_name = parent_workspace._sanitize_data_node_name(new_name or old_name, exclude_node=node)
            else:
                corrected_name = new_name or old_name
            new_name = corrected_name
            self.name_input.setText(new_name)
            if (self.name_input.text() or "").strip() != (new_name or "").strip():
                self.name_input.setText(new_name)

        if not new_name:
            return
        if isinstance(node, DataNode):
            self.name_input.setText(new_name)
        if new_name == old_name:
            return

        old_pos = node.pos()
        node.set_name(new_name)
        node.set_selected(False)
        node.set_selected(True)
        node.set_pos(old_pos[0], old_pos[1])
        node.node_name1 = node.name()

        if isinstance(node, PyNode):
            self._rename_pynode_notebook_and_wrapper(node, old_name, new_name)
            if self.get_flow_type() == "master-flow":
                parent_workspace = self._find_workspace_parent()
                if parent_workspace is not None and hasattr(parent_workspace, "_workflow_for_proxy_node"):
                    try:
                        linked_workflow = parent_workspace._workflow_for_proxy_node(node)
                    except Exception:
                        linked_workflow = None
                    if linked_workflow is not None and linked_workflow is not self:
                        linked_workflow.flow_name = new_name
                        try:
                            linked_workflow.flow_run_input.setText(new_name)
                        except Exception:
                            pass
                        try:
                            linked_tab = parent_workspace._workflow_tab_for_proxy_node(node)
                            if linked_tab is not None:
                                linked_index = parent_workspace.tab_widget.indexOf(linked_tab)
                                if linked_index >= 0:
                                    parent_workspace.tab_widget.setTabText(linked_index, new_name)
                        except Exception:
                            pass
                        try:
                            parent_workspace.sync_workflow_ui(linked_workflow)
                        except Exception:
                            pass
                        try:
                            parent_workspace._sync_proxy_wrapper_for_subflow(linked_workflow)
                        except Exception:
                            pass
            if hasattr(self, "notebook_preview"):
                try:
                    self.notebook_preview.setPlainText(self._notebook_to_code(node.node_notebook_path))
                except Exception:
                    self.notebook_preview.setPlainText("")
            if self.is_popped_out and hasattr(self, "notebook_view"):
                self.notebook_view.load_notebook(node.node_notebook_path)
        elif isinstance(node, DataNode) and bool(getattr(node, "node_is_from_master", False)) and self.get_flow_type() != "master-flow":
            parent_workspace = self._find_workspace_parent()
            if parent_workspace is not None and hasattr(parent_workspace, "_sync_proxy_wrapper_for_subflow"):
                try:
                    parent_workspace._sync_proxy_wrapper_for_subflow(self)
                except Exception:
                    pass

    def update_caption_value(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            old_pos = selected_nodes[0].pos()
            document = self.text_input.document()
            document_text = document.toPlainText()
            docSize = document.size()
            selected_nodes[0].set_size(document.idealWidth(), docSize.height())
            selected_nodes[0].node_input_value = document_text
            selected_nodes[0].set_text(text=selected_nodes[0].node_input_value)
            selected_nodes[0].set_pos(old_pos[0], old_pos[1])

    def update_data_value(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            node = selected_nodes[0]
            old_pos = node.pos()

            if isinstance(node, DataNode) and bool(getattr(node, "node_is_from_master", False)) and self.get_flow_type() != "master-flow":
                self._refresh_data_node_settings_state(node)
                node.set_pos(old_pos[0], old_pos[1])
                return

            value_checked = self.value_checkbox.isChecked()
            path_checked = self.value_path_checkbox.isChecked()
            self.value_browse_button.setEnabled(path_checked)
            node.node_value_display = value_checked
            node.node_is_path = path_checked

            text = self.value_input.text()
            node.node_input_value = text
            widget = node.get_widget('Text Caption')
            if value_checked:
                widget.set_value(node.node_input_value)
            else:
                widget.set_value("")

            print(node.properties())
            node.set_pos(old_pos[0], old_pos[1])

    def update_ports(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) != 1:
            return

        node = selected_nodes[0]
        old_pos = node.pos()
        if isinstance(node, PyNode):
            try:
                notebook_path = self._ensure_node_notebook(node)

                if not self.is_popped_out:
                    self._editor_to_notebook(notebook_path)

                python_code = self._notebook_to_code(notebook_path)
                parsed_ast = ast.parse(python_code)

                ordered_imports = []
                seen_imports = set()
                import_statements = [
                    n for n in parsed_ast.body
                    if isinstance(n, (ast.Import, ast.ImportFrom))
                ]
                for imp in import_statements:
                    import_line = ast.unparse(imp).strip()
                    if not import_line or import_line in seen_imports:
                        continue
                    seen_imports.add(import_line)
                    ordered_imports.append(import_line)

                imports_text = "\n".join(ordered_imports)
                if imports_text:
                    imports_text += "\n"

                node.node_imports = imports_text

                func_defs = [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]
                if len(func_defs) > 0:
                    expected_name = f"{node.name()}_function"
                    matched = [fn for fn in func_defs if fn.name == expected_name]
                    func_def = matched[0] if matched else func_defs[0]
                else:
                    raise ValueError('Wrapper function not found!')

                node.node_function_wrapper = ast.unparse(func_def)
                node.node_notebook_path = notebook_path

                input_ports = [arg.arg for arg in func_def.args.args]
                output_ports = []

                for fc in ast.walk(func_def):
                    if isinstance(fc, ast.Return):
                        if isinstance(fc.value, ast.Dict):
                            output_ports = [key.s for key in fc.value.keys if isinstance(key, ast.Constant)]
                        break

                existing_inputs = list(node.inputs().keys())
                existing_outputs = list(node.outputs().keys())

                desired_inputs = []
                for port_name in input_ports:
                    if port_name not in desired_inputs:
                        desired_inputs.append(port_name)

                desired_outputs = []
                for port_name in output_ports:
                    if port_name not in desired_outputs:
                        desired_outputs.append(port_name)

                for in_port_name in existing_inputs:
                    if in_port_name not in desired_inputs:
                        for connected_port in list(node.inputs()[in_port_name].connected_ports()):
                            node.inputs()[in_port_name].disconnect_from(connected_port)
                        node.delete_input(in_port_name)

                for port_name in desired_inputs:
                    if port_name not in existing_inputs:
                        node.add_dynamic_input(port_name)

                for out_port_name in existing_outputs:
                    if out_port_name not in desired_outputs:
                        for connected_port in list(node.outputs()[out_port_name].connected_ports()):
                            node.outputs()[out_port_name].disconnect_from(connected_port)
                        node.delete_output(out_port_name)

                for key in desired_outputs:
                    if key not in existing_outputs:
                        node.add_dynamic_output(key)

                valid_exposed = [name for name in getattr(node, 'node_expose_outputs', []) if name in output_ports]
                node.node_expose_outputs = valid_exposed
                self._refresh_py_expose_outputs_menu(node)
                parent_workspace = self._find_workspace_parent()
                if self.get_flow_type() != 'master-flow' and parent_workspace is not None and hasattr(parent_workspace, '_sync_proxy_wrapper_for_subflow'):
                    try:
                        parent_workspace._sync_proxy_wrapper_for_subflow(self)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Failed to update Python node from notebook: {e}")
        elif isinstance(node, DataNode):
            for out_port_name in list(node.outputs().keys()):
                for connected_port in node.outputs()[out_port_name].connected_ports():
                    node.outputs()[out_port_name].disconnect_from(connected_port)
                node.delete_output(out_port_name)

            variable_name = self.data_input.text()
            node.add_dynamic_output(variable_name)
            node.node_input_variable = variable_name

            parent_workspace = self._find_workspace_parent()
            if parent_workspace is not None and hasattr(parent_workspace, "_sync_proxy_wrapper_for_subflow"):
                try:
                    parent_workspace._sync_proxy_wrapper_for_subflow(self)
                except Exception:
                    pass

        node.set_pos(old_pos[0], old_pos[1])

    def get_newest_node_position(self):
        nodes = self.graph.all_nodes()
        position = (0, 0)
        if nodes:
            newest_node = nodes[-1]
            position = newest_node.pos()
        return position

    def create_data_node(self):
        self.update_flow()
        self.node_counters["DataNode"] += 1
        node_name = f"DataNode{self.node_counters['DataNode']}"
        latest_pos = list(self.get_newest_node_position())
        new_pos = (latest_pos[0] + 100, latest_pos[1] + 100)
        node = self.graph.create_node('QuESt.Workspace.DataNode', name=node_name, color=(255, 255, 255), text_color=(0, 0, 0), pos=new_pos, selected=True, push_undo=True)
        node.node_is_from_master = False

    def create_text_node(self):
        self.update_flow()
        self.node_counters["TextNode"] = self.node_counters.get("TextNode", 0) + 1
        node_name = f"TextNode{self.node_counters['TextNode']}"
        latest_pos = self.get_newest_node_position()
        new_pos = (latest_pos[0] + 100, latest_pos[1] + 100)
        node = self.graph.create_node('QuESt.Workspace.BackNode', name=node_name, color=(255, 255, 155), text_color=(0, 0, 0), pos=new_pos, selected=True, push_undo=True)
        node.node_is_from_master = False

    def create_py_node(self):
        self.update_flow()
        self.node_counters["PyNode"] += 1
        node_name = f"PyNode{self.node_counters['PyNode']}"
        latest_pos = list(self.get_newest_node_position())
        new_pos = (latest_pos[0] + 100, latest_pos[1] + 100)
        node = self.graph.create_node('QuESt.Workspace.PyNode', name=node_name, color=(255, 255, 255), text_color=(0, 0, 0), pos=new_pos, selected=True, push_undo=True)
        node.node_is_from_master = False
        notebook_path = os.path.join(
            self.notebooks_dir,
            self._notebook_filename(node_name, node.id)
        )
        if not os.path.exists(notebook_path):
            self._create_notebook_template(
                notebook_path,
                node_name,
                self.flow_environment_path,
                self.flow_environment_name
            )
        node.node_notebook_path = notebook_path

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_nodes = self.graph.selected_nodes()
            parent_workspace = self._find_workspace_parent()
            for node in selected_nodes:
                if hasattr(node, "can_be_deleted") and not node.can_be_deleted():
                    continue
                handled = False
                try:
                    if (
                        self is getattr(parent_workspace, "master_workflow", None)
                        and parent_workspace is not None
                        and hasattr(parent_workspace, "_remove_subflow_for_proxy_node")
                    ):
                        handled = bool(parent_workspace._remove_subflow_for_proxy_node(node))
                except Exception:
                    handled = False
                if not handled:
                    self.graph.delete_node(node)
            self.update_flow()
            self._sync_parent_proxy_wrapper_from_current_graph()
        else:
            super().keyPressEvent(event)

    def _sync_parent_proxy_wrapper_from_current_graph(self):
        try:
            self.update_flow()
        except Exception:
            pass

        if self.get_flow_type() == 'master-flow':
            return

        try:
            parent_workspace = self._find_workspace_parent()
            if parent_workspace is not None and hasattr(parent_workspace, '_sync_proxy_wrapper_for_subflow'):
                parent_workspace._sync_proxy_wrapper_for_subflow(self)
        except Exception:
            pass

    def _find_workspace_parent(self):
        parent = self.parentWidget() or self.parent()
        while parent is not None:
            if hasattr(parent, "_open_selected_subworkflow_from_master"):
                return parent
            parent = parent.parentWidget() if hasattr(parent, "parentWidget") else parent.parent()
        return None

    def _handle_subworkflow_double_click(self):
        self.on_node_selected()
        try:
            parent_workspace = self._find_workspace_parent()
            if parent_workspace is not None:
                parent_workspace._open_selected_subworkflow_from_master()
        except Exception:
            pass

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.MouseButtonDblClick and event.button() == Qt.LeftButton:
                QTimer.singleShot(0, self._handle_subworkflow_double_click)
            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                QTimer.singleShot(0, self._sync_parent_proxy_wrapper_from_current_graph)
            elif event.type() in (QEvent.Resize, QEvent.Show):
                QTimer.singleShot(0, self._position_graph_help_overlay)
                QTimer.singleShot(0, self._position_clear_canvas_button)
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        self._position_graph_help_overlay()
        self._position_clear_canvas_button()
        self._apply_pending_graph_frame()

    def request_graph_frame(self):
        self._pending_graph_frame = True
        QTimer.singleShot(0, self._apply_pending_graph_frame)

    def _apply_pending_graph_frame(self):
        if not self._pending_graph_frame:
            return
        try:
            if not self.isVisible():
                return
            if self.graph_widget is None or not self.graph_widget.isVisible():
                return
            all_nodes = self.graph.all_nodes()
            if not all_nodes:
                self._pending_graph_frame = False
                return
            self.graph.fit_to_selection()
            try:
                self.graph.center_on(all_nodes)
            except Exception:
                pass
            try:
                self.graph.viewer().force_update()
            except Exception:
                pass
            self._pending_graph_frame = False
        except Exception:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_node_selected()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._handle_subworkflow_double_click()
        super().mouseDoubleClickEvent(event)





class quest_workspace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.toolbar = QToolBar("Node Tools", self)
        self.toolbar.setFloatable(True)
        self.toolbar.setMovable(True)
        self.toolbar.setIconSize(QSize(40, 40))

        d_icon = os.path.join(base_dir, "images", "icons", "data_icon.png")
        t_icon = os.path.join(base_dir, "images", "icons", "text_icon.png")
        p_icon = os.path.join(base_dir, "images", "icons", "python_icon.png")

        data_node_icon = QIcon(d_icon)
        text_node_icon = QIcon(t_icon)
        py_node_icon = QIcon(p_icon)

        self.action_text_node = QAction(text_node_icon, 'Add Text Node', self)
        self.action_data_node = QAction(data_node_icon, 'Add Data Node', self)
        self.action_py_node = QAction(py_node_icon, 'Add Py Node', self)

        self.toolbar.addAction(self.action_text_node)
        self.toolbar.addAction(self.action_data_node)
        self.toolbar.addAction(self.action_py_node)

        self.action_text_node.triggered.connect(lambda: self.active_workflow().create_text_node())
        self.action_data_node.triggered.connect(lambda: self.active_workflow().create_data_node())
        self.action_py_node.triggered.connect(lambda: self.active_workflow().create_py_node())

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("workspaceTabWidget")
        self.tab_widget.setStyleSheet("""
        QTabWidget#workspaceTabWidget::pane {
            border: 1px solid #d9e2ec;
            background: white;
        }
        QTabBar::tab {
            min-width: 70px;
            padding: 5px 10px;
            margin-right: 2px;
            background: #e5e7eb;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-weight: 600;
        }
        QTabBar::tab:selected {
            background: #2563eb;
            color: white;
            border: 1px solid #1d4ed8;
            border-bottom: none;
            font-weight: 700;
        }
        QTabBar::tab:hover:!selected {
            background: #dbeafe;
            color: #1e3a8a;
        }
        """)

        self.workflows = []
        self.workflow_counter = 1
        self._plus_tab = QWidget()

        self.master_workflow = quest_workflow(self)
        self.master_workflow.flow_run_input.setText("Master")
        self.master_workflow.set_flow_type("master-flow")
        self.workflows.append(self.master_workflow)

        self.master_tab = QWidget()
        self.master_tab._workflow_instance = self.master_workflow
        self.master_tab_layout = QVBoxLayout(self.master_tab)
        self.master_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.master_tab_layout.setSpacing(0)
        self.master_tab_layout.addWidget(self.master_workflow)

        self.tab_widget.addTab(self.master_tab, "Master")
        self.tab_widget.addTab(self._plus_tab, "+")
        self.tab_widget.currentChanged.connect(self._on_workspace_tab_changed)

        self.layout.addWidget(self.tab_widget)
        self._refresh_all_save_mode_options()

    def _on_workspace_tab_changed(self, index):
        try:
            if self.tab_widget.widget(index) is self._plus_tab:
                self.create_workflow_tab()
            else:
                self.sync_active_flow_name_from_tab_name()
                workflow = self.active_workflow()
                if workflow is not None:
                    workflow.request_graph_frame()
        except Exception:
            pass

    def active_workflow(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is None or current_widget is self._plus_tab:
            return self.master_workflow
        return getattr(current_widget, "_workflow_instance", self.master_workflow)

    def activate_workflow(self, workflow):
        if workflow is None:
            return
        if workflow is self.master_workflow:
            self.tab_widget.setCurrentWidget(self.master_tab)
            return
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if getattr(tab, "_workflow_instance", None) is workflow:
                self.tab_widget.setCurrentWidget(tab)
                return

    def sync_workflow_ui(self, workflow):
        if workflow is None:
            return
        current_active = self.active_workflow()
        self.activate_workflow(workflow)
        self.sync_active_workflow_tab_name_from_flow_name()
        if workflow is self.master_workflow:
            workflow.set_flow_type("master-flow")
        else:
            workflow.set_flow_type("sub-flow")
        self._refresh_all_save_mode_options()
        if current_active is not workflow and current_active is not None:
            self.activate_workflow(current_active)

    def _sanitize_flow_name(self, name):
        name = (name or "").strip() or "Workflow"
        sanitized = []
        for ch in name:
            if ch.isalnum() or ch == "_":
                sanitized.append(ch)
            else:
                sanitized.append("_")
        name = "".join(sanitized).strip("_") or "Workflow"
        while "__" in name:
            name = name.replace("__", "_")
        if name and name[0].isdigit():
            name = f"_{name}"
        if keyword.iskeyword(name):
            name = f"{name}_flow"
        return name

    def _existing_flow_names(self, exclude_workflow=None):
        names = []
        for workflow in getattr(self, "workflows", []):
            if workflow is exclude_workflow:
                continue
            try:
                name = (workflow.flow_run_input.text() or "").strip()
            except Exception:
                name = ""
            if name:
                names.append(name)
        return names

    def _make_unique_flow_name(self, base_name, exclude_workflow=None):
        base_name = self._sanitize_flow_name(base_name)
        existing = set(self._existing_flow_names(exclude_workflow=exclude_workflow))
        if base_name not in existing:
            return base_name

        i = 2
        while True:
            candidate = f"{base_name}_{i}"
            if candidate not in existing:
                return candidate
            i += 1

    def _existing_node_names(self, exclude_node=None):
        names = []
        try:
            nodes = self.graph.all_nodes()
        except Exception:
            nodes = []
        for node in nodes:
            if exclude_node is not None and node is exclude_node:
                continue
            try:
                name = str(node.name() or "").strip()
            except Exception:
                name = ""
            if name:
                names.append(name)
        return names

    def _make_unique_node_name(self, base_name, exclude_node=None):
        base_name = (base_name or "").strip() or "Node"
        existing = set(self._existing_node_names(exclude_node=exclude_node))
        if base_name not in existing:
            return base_name
        i = 2
        while True:
            candidate = f"{base_name}_{i}"
            if candidate not in existing:
                return candidate
            i += 1

    def _sanitize_data_node_name(self, name, exclude_node=None):
        base = self._sanitize_flow_name(name or "DataNode")
        return self._make_unique_node_name(base, exclude_node=exclude_node)

    def _normalize_data_node_name(self, node, desired_name):
        if not isinstance(node, DataNode):
            return (desired_name or "").strip()
        safe_name = self._sanitize_data_node_name(desired_name, exclude_node=node)
        old_pos = node.pos()
        if node.name() != safe_name:
            node.set_name(safe_name)
            try:
                node.set_pos(old_pos[0], old_pos[1])
            except Exception:
                pass
        return safe_name


    def _create_subworkflow_proxy_node(self, workflow, flow_name):
        if workflow is self.master_workflow:
            return None

        master = self.master_workflow
        latest_pos = list(master.get_newest_node_position())
        new_pos = (latest_pos[0] + 100, latest_pos[1] + 100)

        node = master.graph.create_node(
            'QuESt.Workspace.PyNode',
            name=flow_name,
            color=(255, 255, 255),
            text_color=(0, 0, 0),
            pos=new_pos,
            selected=False,
            push_undo=True
        )
        node.node_is_from_master = False

        notebook_path = os.path.join(
            master.notebooks_dir,
            master._notebook_filename(flow_name, node.id)
        )
        if not os.path.exists(notebook_path):
            master._create_notebook_template(
                notebook_path,
                flow_name,
                master.flow_environment_path,
                master.flow_environment_name
            )
        node.node_notebook_path = notebook_path
        workflow._subflow_proxy_node = node
        try:
            self._sync_proxy_wrapper_for_subflow(workflow)
        except Exception:
            pass
        return node

    def _sync_subworkflow_proxy_node_name(self, workflow, new_name):
        if workflow is self.master_workflow:
            return

        node = getattr(workflow, "_subflow_proxy_node", None)
        if node is None:
            return

        old_name = node.name()
        if old_name == new_name:
            return

        old_pos = node.pos()
        node.set_name(new_name)
        node.set_pos(old_pos[0], old_pos[1])

        try:
            self.master_workflow._rename_pynode_notebook_and_wrapper(node, old_name, new_name)
        except Exception:
            pass

        try:
            self._sync_proxy_wrapper_for_subflow(workflow)
        except Exception:
            pass

    def _subflow_proxy_input_names(self, workflow):
        names = []
        if workflow is None or workflow is self.master_workflow:
            return names
        try:
            workflow.update_flow()
        except Exception:
            pass
        for node in workflow.graph.all_nodes():
            if not isinstance(node, DataNode):
                continue
            if not bool(getattr(node, "node_is_from_master", False)):
                continue
            candidate = str(node.name() or "").strip()
            if candidate and candidate not in names:
                names.append(candidate)
        return names

    def _subflow_proxy_output_names(self, workflow):
        names = []
        if workflow is None or workflow is self.master_workflow:
            return names
        try:
            workflow.update_flow()
        except Exception:
            pass
        for node in workflow.graph.all_nodes():
            if not isinstance(node, PyNode):
                continue
            for candidate in getattr(node, 'node_expose_outputs', []) or []:
                candidate = str(candidate).strip()
                if candidate and candidate not in names:
                    names.append(candidate)
        return names


    # def _proxy_wrapper_imports(self, dir):
    #     return (
    #         self.master_workflow._quest_root_bootstrap(dir)
    #         + "import pandas as pd\n"
    #         + "from quest.snl_libraries.workspace.flow.questflow import *"
    #     )

    def _workflow_graph_nodes_records(self, workflow):
        if workflow is None:
            return []
        try:
            workflow.update_flow()
        except Exception:
            pass
        try:
            return workflow.nodes_df.to_dict(orient="records")
        except Exception:
            return []

    def _workflow_graph_connections_records(self, workflow):
        if workflow is None:
            return []
        try:
            workflow.update_flow()
        except Exception:
            pass
        try:
            records = workflow.connections_df.to_dict(orient="records")
        except Exception:
            records = []
        if records:
            return records

        try:
            graph_session = workflow.graph.serialize_session() or {}
        except Exception:
            graph_session = {}

        connections = graph_session.get('connections', []) or []
        fallback_records = []
        for i, connection in enumerate(connections, start=1):
            try:
                fallback_records.append({
                    'connection_id': i,
                    'from_node': connection['out'][0],
                    'to_node': connection['in'][0],
                    'mapping': {connection['out'][1]: connection['in'][1]},
                })
            except Exception:
                pass
        return fallback_records

    def _generate_proxy_wrapper_for_subflow(self, workflow, proxy_node):
        import json

        if workflow is None or proxy_node is None:
            return ""

        try:
            self.update_envs()
        except Exception:
            pass

        nodes_records = self._workflow_graph_nodes_records(workflow)
        connections_records = self._workflow_graph_connections_records(workflow)

        input_names = []
        for row in nodes_records:
            try:
                if str(row.get("node_type", "")).strip() == "data_node" and bool(row.get("node_is_from_master", False)):
                    name = str(row.get("node_name", "")).strip()
                    if name and name not in input_names:
                        input_names.append(name)
            except Exception:
                pass

        output_map = []
        python_node_rows = []
        for row in nodes_records:
            try:
                if str(row.get("node_type", "")).strip() != "python_node":
                    continue
                python_node_rows.append(row)
                node_name = str(row.get("node_name", "")).strip()
                outputs = row.get("node_expose_outputs", [])
                if isinstance(outputs, str):
                    try:
                        outputs = json.loads(outputs)
                    except Exception:
                        outputs = []
                for out_name in outputs or []:
                    out_name = str(out_name).strip()
                    if node_name and out_name:
                        output_map.append((node_name, out_name))
            except Exception:
                pass

        wrapper_name = f"{proxy_node.name()}_function"
        signature = ", ".join([f"{name}=None" for name in input_names])

        python_executable = ""
        try:
            if hasattr(workflow, "_sync_flow_metadata_from_controls"):
                workflow._sync_flow_metadata_from_controls()
        except Exception:
            pass
        try:
            python_executable = str(getattr(workflow, "flow_environment_path", "") or "").strip()
        except Exception:
            python_executable = ""
        if not python_executable:
            try:
                if hasattr(workflow, "env_path_input") and workflow.env_path_input is not None:
                    python_executable = str(workflow.env_path_input.text() or "").strip()
            except Exception:
                pass

        IND = "    "
        code = []

        # --- wrapper function ---
        code.append(f"def {wrapper_name}({signature}):")

        # --- update_subflow ---
        code.append(IND + "def update_subflow(subflow_nodes_df, **kwargs):")
        code.append(IND*2 + "for idx, row in subflow_nodes_df.iterrows():")
        code.append(IND*3 + "if row.get('node_type') == 'data_node' and row.get('node_is_from_master') == True:")
        code.append(IND*4 + "node_name = str(row.get('node_name', '')).strip()")
        code.append(IND*4 + "if node_name in kwargs:")
        code.append(IND*5 + "subflow_nodes_df.at[idx, 'node_input_value'] = repr(kwargs[node_name])")
        code.append(IND*2 + "return subflow_nodes_df")
        code.append("")

        # --- run_subflow ---
        code.append(IND + "def run_subflow(subflow_name, subflow_nodes_df, subflow_connections_df, python_executable=None):")
        code.append(IND*2 + "f = flow(flow_name=subflow_name, nodes_df=subflow_nodes_df, connections_df=subflow_connections_df)")
        code.append(IND*2 + "f.set_inputs()")
        code.append(IND*2 + "f.get_outputs(key=None)")
        code.append(IND*2 + "f.make()")

        # --- append_lines ---
        code.append(IND*2 + "append_lines = []")
        code.append(IND*2 + "append_lines.append('import json')")
        code.append(IND*2 + "append_lines.append('_quest_subflow_results = {}')")

        for row in python_node_rows:
            node_id = str(row.get("node_id", "") or "").strip()
            node_name = str(row.get("node_name", "") or "").strip()
            if not node_id or not node_name:
                continue

            output_var = f"node{node_id}_outputs"

            # FIX: use repr on variable name so it becomes a string in generated code
            code.append(
                IND*2 + f"append_lines.append({repr(f'if {output_var!r} in globals():')})"
            )
            code.append(
                IND*2 + f"append_lines.append({repr(f'    _quest_subflow_results[{node_name!r}] = {output_var}')})"
            )

        # --- result printing ---
        code.append(IND*2 + "append_lines.append(\"print('__QUEST_SUBFLOW_RESULTS_START__')\")")
        code.append(IND*2 + "append_lines.append(\"print(json.dumps(_quest_subflow_results, default=str))\")")
        code.append(IND*2 + "append_lines.append(\"print('__QUEST_SUBFLOW_RESULTS_END__')\")")

        code.append(IND*2 + "f.main_py = f.main_py.rstrip() + '\\n\\n' + '\\n'.join(append_lines) + '\\n'")

        # --- temp run ---
        code.append(IND*2 + "with tempfile.TemporaryDirectory() as tmpdir:")
        code.append(IND*3 + "f.save(tmpdir + os.sep)")
        code.append(IND*3 + "result = f.run(python_executable=python_executable)")
        code.append(IND*3 + "stdout = getattr(result, 'stdout', '') or ''")

        # --- parse output ---
        code.append(IND*2 + "start_marker = '__QUEST_SUBFLOW_RESULTS_START__'")
        code.append(IND*2 + "end_marker = '__QUEST_SUBFLOW_RESULTS_END__'")

        code.append(IND*2 + "if start_marker not in stdout or end_marker not in stdout:")
        code.append(IND*3 + "raise RuntimeError('Could not find subflow results in stdout.\\nSTDOUT:\\n' + stdout)")

        code.append(IND*2 + "payload = stdout.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()")
        code.append(IND*2 + "if not payload:")
        code.append(IND*3 + "return {}")

        code.append(IND*2 + "return json.loads(payload)")
        code.append("")

        # --- main wrapper logic ---
        code.append(IND + f"subflow_name = {proxy_node.name()!r}")
        code.append(IND + f"subflow_nodes_df = pd.DataFrame({repr(nodes_records)})")
        code.append(IND + f"subflow_connections_df = pd.DataFrame({repr(connections_records)})")

        if input_names:
            args = ", ".join([f"{name}={name}" for name in input_names])
            code.append(IND + f"subflow_nodes_df = update_subflow(subflow_nodes_df, {args})")
        else:
            code.append(IND + "subflow_nodes_df = update_subflow(subflow_nodes_df)")

        code.append(IND + f"_results = run_subflow(subflow_name, subflow_nodes_df, subflow_connections_df, python_executable={python_executable!r})")

        # --- return ---
        code.append(IND + "return {")

        if output_map:
            for node_name, out_name in output_map:
                code.append(IND*2 + f"{out_name!r}: _results.get({node_name!r}, {{}}).get({out_name!r}),")
        else:
            code.append(IND*2 + "'output': None,")

        code.append(IND + "}")

        return "\n".join(code)


    def _proxy_wrapper_code_for_subflow(self, proxy_node_name, input_names, output_names=None):
        safe_inputs = [str(name).strip() for name in input_names if str(name).strip()]
        safe_outputs = [str(name).strip() for name in (output_names or []) if str(name).strip()]
        if not safe_outputs:
            safe_outputs = ["output"]
        args = ", ".join(safe_inputs)
        return_items = ", ".join([f"'{name}': None" for name in safe_outputs])
        return f"def {proxy_node_name}_function({args}):\n    return {{{return_items}}}\n"

    def _set_proxy_node_wrapper(self, proxy_node, wrapper_code):
        if proxy_node is None or not isinstance(proxy_node, PyNode):
            return

        # proxy_node.node_imports = self._proxy_wrapper_imports(os.path.dirname(base_dir)).strip()
        proxy_node.node_function_wrapper = wrapper_code

        try:
            notebook_path = self.master_workflow._ensure_node_notebook(proxy_node)
            code_parts = []
            imports_text = (proxy_node.node_imports or "").strip()
            if imports_text:
                code_parts.append(imports_text)
            code_parts.append(wrapper_code.strip())
            nb = nbf.v4.new_notebook()
            nb.cells = [
                nbf.v4.new_markdown_cell(f"# {proxy_node.name()}\n\nNotebook backing this PyNode."),
                nbf.v4.new_code_cell("\n\n".join(code_parts)),
            ]
            with open(notebook_path, "w", encoding="utf-8") as f:
                nbf.write(nb, f)
            self.master_workflow._apply_notebook_kernel(
                notebook_path
            )
            proxy_node.node_notebook_path = notebook_path
        except Exception:
            pass

        try:
            parsed_ast = ast.parse(wrapper_code)
            func_defs = [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]
            func_def = func_defs[0] if func_defs else None
            input_ports = [arg.arg for arg in func_def.args.args] if func_def else []
            output_ports = []
            if func_def is not None:
                for fc in ast.walk(func_def):
                    if isinstance(fc, ast.Return) and isinstance(fc.value, ast.Dict):
                        output_ports = [key.value if isinstance(key, ast.Constant) else key.s for key in fc.value.keys if isinstance(key, (ast.Constant, ast.Str))]
                        break

            existing_inputs = list(proxy_node.inputs().keys())
            existing_outputs = list(proxy_node.outputs().keys())

            desired_inputs = []
            for port_name in input_ports:
                if port_name not in desired_inputs:
                    desired_inputs.append(port_name)

            desired_outputs = []
            for port_name in output_ports:
                if port_name not in desired_outputs:
                    desired_outputs.append(port_name)

            for in_port_name in existing_inputs:
                if in_port_name not in desired_inputs:
                    for connected_port in list(proxy_node.inputs()[in_port_name].connected_ports()):
                        proxy_node.inputs()[in_port_name].disconnect_from(connected_port)
                    proxy_node.delete_input(in_port_name)
            for port_name in desired_inputs:
                if port_name not in existing_inputs:
                    proxy_node.add_dynamic_input(port_name)

            for out_port_name in existing_outputs:
                if out_port_name not in desired_outputs:
                    for connected_port in list(proxy_node.outputs()[out_port_name].connected_ports()):
                        proxy_node.outputs()[out_port_name].disconnect_from(connected_port)
                    proxy_node.delete_output(out_port_name)
            for port_name in desired_outputs:
                if port_name not in existing_outputs:
                    proxy_node.add_dynamic_output(port_name)
        except Exception:
            pass

    def _sync_proxy_wrapper_for_subflow(self, workflow):
        if workflow is None or workflow is self.master_workflow:
            return
        proxy_node = getattr(workflow, "_subflow_proxy_node", None)
        if proxy_node is None:
            return
        if getattr(workflow, "_proxy_wrapper_sync_in_progress", False):
            return

        workflow._proxy_wrapper_sync_in_progress = True
        try:
            input_names = self._subflow_proxy_input_names(workflow)

            output_names = self._subflow_proxy_output_names(workflow)
            if not output_names:
                try:
                    wrapper_text = getattr(proxy_node, "node_function_wrapper", "") or ""
                    parsed_ast = ast.parse(wrapper_text)
                    for func_def in [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]:
                        for fc in ast.walk(func_def):
                            if isinstance(fc, ast.Return) and isinstance(fc.value, ast.Dict):
                                output_names = [key.value if isinstance(key, ast.Constant) else key.s for key in fc.value.keys if isinstance(key, (ast.Constant, ast.Str))]
                                break
                        if output_names:
                            break
                except Exception:
                    output_names = []

            wrapper_code = self._generate_proxy_wrapper_for_subflow(workflow, proxy_node)
            self._set_proxy_node_wrapper(proxy_node, wrapper_code)
            try:
                self.master_workflow.update_flow()
            except Exception:
                pass
        finally:
            workflow._proxy_wrapper_sync_in_progress = False

    def _workflow_tab_for_proxy_node(self, node):
        for i in range(0, self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            workflow = getattr(w, "_workflow_instance", None)
            if workflow is None or workflow is self.master_workflow:
                continue
            proxy = getattr(workflow, "_subflow_proxy_node", None)
            if proxy is node:
                return w
        return None

    def _workflow_for_proxy_node(self, node):
        tab = self._workflow_tab_for_proxy_node(node)
        if tab is None:
            return None
        return getattr(tab, "_workflow_instance", None)

    def _find_unassigned_master_proxy_node_by_name(self, flow_name):
        target_name = str(flow_name or "").strip()
        if not target_name:
            return None

        assigned = set()
        for workflow in self._subflow_workflows():
            proxy = getattr(workflow, "_subflow_proxy_node", None)
            if proxy is not None:
                assigned.add(proxy)

        try:
            all_nodes = list(self.master_workflow.graph.all_nodes())
        except Exception:
            all_nodes = []

        for node in all_nodes:
            if not isinstance(node, PyNode):
                continue
            if node in assigned:
                continue
            try:
                node_name = str(node.name() or "").strip()
            except Exception:
                node_name = ""
            if node_name == target_name:
                return node
        return None

    def _attach_or_create_proxy_node_for_workflow(self, workflow, flow_name):
        if workflow is None or workflow is self.master_workflow:
            return None

        existing = self._find_unassigned_master_proxy_node_by_name(flow_name)
        if existing is not None:
            workflow._subflow_proxy_node = existing
            return existing

        return self._create_subworkflow_proxy_node(workflow, flow_name)

    def _remove_unassigned_master_proxy_nodes(self):
        assigned = set()
        for workflow in self._subflow_workflows():
            proxy = getattr(workflow, "_subflow_proxy_node", None)
            if proxy is not None:
                assigned.add(proxy)

        try:
            all_nodes = list(self.master_workflow.graph.all_nodes())
        except Exception:
            all_nodes = []

        for node in all_nodes:
            if not isinstance(node, PyNode):
                continue
            if node in assigned:
                continue
            try:
                self.master_workflow.graph.delete_node(node)
            except Exception:
                pass

    def _remove_subflow_workflow(self, workflow):
        if workflow is None or workflow is self.master_workflow:
            return False

        tab_to_remove = None
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if getattr(tab, "_workflow_instance", None) is workflow:
                tab_to_remove = tab
                break

        proxy = getattr(workflow, "_subflow_proxy_node", None)
        if proxy is not None:
            try:
                self.master_workflow.graph.delete_node(proxy)
            except Exception:
                pass
        workflow._subflow_proxy_node = None

        if tab_to_remove is not None:
            current_widget = self.tab_widget.currentWidget()
            if current_widget is tab_to_remove:
                self.tab_widget.setCurrentWidget(self.master_tab)
            idx = self.tab_widget.indexOf(tab_to_remove)
            if idx >= 0:
                self.tab_widget.removeTab(idx)

        try:
            self.workflows.remove(workflow)
        except ValueError:
            pass

        try:
            self.sync_workflow_ui(self.master_workflow)
        except Exception:
            pass
        self._refresh_all_save_mode_options()
        return True

    def _remove_subflow_for_proxy_node(self, node):
        workflow = self._workflow_for_proxy_node(node)
        if workflow is None:
            return False
        return self._remove_subflow_workflow(workflow)

    def _open_selected_subworkflow_from_master(self):
        try:
            if self.tab_widget.currentWidget() is not self.master_tab:
                return
            selected_nodes = self.master_workflow.graph.selected_nodes()
            if len(selected_nodes) != 1:
                return
            node = selected_nodes[0]
            if not isinstance(node, PyNode):
                return
            tab = self._workflow_tab_for_proxy_node(node)
            if tab is not None:
                self.tab_widget.setCurrentWidget(tab)
        except Exception:
            pass

    def sync_active_workflow_tab_name_from_flow_name(self):
        workflow = self.active_workflow()
        if workflow is None:
            return

        current_widget = self.tab_widget.currentWidget()
        if current_widget is None or current_widget is self._plus_tab:
            return

        requested_name = (workflow.flow_run_input.text() or "").strip()
        if not requested_name:
            requested_name = "Workflow"

        unique_name = self._make_unique_flow_name(requested_name, exclude_workflow=workflow)

        if unique_name != requested_name:
            try:
                workflow.flow_run_input.blockSignals(True)
                workflow.flow_run_input.setText(unique_name)
            finally:
                workflow.flow_run_input.blockSignals(False)

        index = self.tab_widget.indexOf(current_widget)
        if index >= 0:
            self.tab_widget.setTabText(index, unique_name)
        if workflow is self.master_workflow:
            workflow.set_flow_type("master-flow")
        else:
            workflow.set_flow_type("sub-flow")
        self._sync_subworkflow_proxy_node_name(workflow, unique_name)

    def sync_active_flow_name_from_tab_name(self):
        workflow = self.active_workflow()
        if workflow is None:
            return

        current_widget = self.tab_widget.currentWidget()
        if current_widget is None or current_widget is self._plus_tab:
            return

        index = self.tab_widget.indexOf(current_widget)
        if index < 0:
            return

        tab_name = self.tab_widget.tabText(index)
        unique_name = self._make_unique_flow_name(tab_name, exclude_workflow=workflow)
        try:
            workflow.flow_run_input.setText(unique_name)
        except Exception:
            pass
        self.tab_widget.setTabText(index, unique_name)
        if workflow is self.master_workflow:
            workflow.set_flow_type("master-flow")
        else:
            workflow.set_flow_type("sub-flow")
        self._sync_subworkflow_proxy_node_name(workflow, unique_name)

    def _refresh_all_save_mode_options(self):
        for workflow in getattr(self, "workflows", []):
            try:
                workflow._refresh_save_mode_options()
            except Exception:
                pass

    def _subflow_workflows(self):
        return [w for w in getattr(self, "workflows", []) if w is not self.master_workflow]

    def _clear_all_subflows(self):
        for workflow in list(self._subflow_workflows()):
            self._remove_subflow_workflow(workflow)

    def _serialize_master_flow_json_data(self):
        master_data = self.master_workflow._serialize_independent_flow_json_data()
        master_data["flow_type"] = "master-flow"
        master_data["subflows_df"] = [
            workflow._serialize_independent_flow_json_data()
            for workflow in self._subflow_workflows()
        ]
        return master_data

    def _master_proxy_nodes_in_load_order(self):
        try:
            all_nodes = list(self.master_workflow.graph.all_nodes())
        except Exception:
            all_nodes = []
        return [node for node in all_nodes if isinstance(node, PyNode)]

    def _load_master_flow_json_data(self, flow_json_data, source_path=""):
        self._clear_all_subflows()
        self.master_workflow._deserialize_flow_json_data(flow_json_data)
        self.master_workflow.flow_load_path.setText(self.master_workflow._display_flow_path(source_path))
        self.master_workflow.set_flow_type("master-flow")

        subflows_data = [d for d in flow_json_data.get("subflows_df", []) if isinstance(d, dict)]
        proxy_nodes = self._master_proxy_nodes_in_load_order()

        if len(proxy_nodes) != len(subflows_data):
            try:
                QMessageBox.warning(
                    self,
                    "Master Flow Load Warning",
                    "The number of proxy Python nodes in the loaded master flow does not match the number of saved subflows.\n\n"
                    f"Proxy nodes found: {len(proxy_nodes)}\n"
                    f"Saved subflows found: {len(subflows_data)}\n\n"
                    "The app will load subflows in proxy-node order up to the smaller count."
                )
            except Exception:
                pass

        for proxy_node, subflow_data in zip(proxy_nodes, subflows_data):
            subflow_name = str(subflow_data.get("flow_name") or "").strip() or str(proxy_node.name() or "").strip() or f"Workflow {self.workflow_counter}"
            workflow = self.create_workflow_tab(title=subflow_name, create_proxy=False)
            workflow._subflow_proxy_node = proxy_node
            workflow._deserialize_flow_json_data(subflow_data)
            workflow.set_flow_type("sub-flow")
            workflow.flow_load_path.setText(workflow._display_flow_path(source_path))
            try:
                loaded_name = str(workflow.flow_run_input.text() or "").strip()
            except Exception:
                loaded_name = ""
            if loaded_name:
                try:
                    self._sync_subworkflow_proxy_node_name(workflow, loaded_name)
                except Exception:
                    pass
            self.sync_workflow_ui(workflow)

        self.activate_workflow(self.master_workflow)
        self.sync_workflow_ui(self.master_workflow)

    def create_workflow_tab(self, title=None, create_proxy=True):
        workflow = quest_workflow(self)
        workflow.set_flow_type("sub-flow")
        self.workflows.append(workflow)
        self.workflow_counter += 1

        tab = QWidget()
        tab._workflow_instance = workflow
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(workflow)

        requested_title = title or f"Workflow {self.workflow_counter - 1}"
        tab_title = self._make_unique_flow_name(requested_title, exclude_workflow=workflow)
        try:
            workflow.flow_run_input.setText(tab_title)
        except Exception:
            pass
        plus_index = self.tab_widget.indexOf(self._plus_tab)
        if plus_index < 0:
            plus_index = self.tab_widget.count()

        self.tab_widget.insertTab(plus_index, tab, tab_title)
        if create_proxy:
            self._create_subworkflow_proxy_node(workflow, tab_title)
        self.sync_workflow_ui(workflow)
        self._refresh_all_save_mode_options()
        self.tab_widget.setCurrentWidget(self.master_tab)
        return workflow

class WMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuESt Workspace")
        self.resize(1400, 900)

        self.quest_workspace_widget = quest_workspace(self)
        self.addToolBar(Qt.LeftToolBarArea, self.quest_workspace_widget.toolbar)
        self.setCentralWidget(self.quest_workspace_widget)

        self._connect_flow_name_sync_signals()
        self.quest_workspace_widget.tab_widget.currentChanged.connect(self._connect_flow_name_sync_signals)

    def _connect_flow_name_sync_signals(self, *args):
        workflow = self.quest_workspace_widget.active_workflow()
        if workflow is None:
            return
        try:
            workflow.flow_run_input.textChanged.disconnect(self.quest_workspace_widget.sync_active_workflow_tab_name_from_flow_name)
        except Exception:
            pass
        try:
            workflow.flow_run_input.textChanged.connect(self.quest_workspace_widget.sync_active_workflow_tab_name_from_flow_name)
        except Exception:
            pass

    def set_light_graph(self):
        workflow = self.quest_workspace_widget.active_workflow()
        workflow.graph.set_background_color(255, 255, 255)

    def set_dark_graph(self):
        workflow = self.quest_workspace_widget.active_workflow()
        workflow.graph.set_background_color(25, 25, 25)
        workflow.graph.set_grid_color(62, 62, 62)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WMainWindow()
    window.show()
    sys.exit(app.exec())
