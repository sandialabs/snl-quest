import sys
import os
import inspect, ast, json, socket, shutil
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
import nbformat as nbf

from NodeGraphQt import NodeGraph, BaseNode, NodeBaseWidget, BackdropNode
from NodeGraphQt.constants import *
from quest.paths import get_path
base_dir = get_path()

from quest.snl_libraries.workspace.flow.questflow import *

class PythonEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            # Insert four spaces instead of a tab character
            self.insertPlainText("    ")
            return
        super().keyPressEvent(event)

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


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        
        # Keywords
        keywords = [
            '\\bFalse\\b', '\\bNone\\b', '\\bTrue\\b', '\\band\\b', '\\bas\\b', 
            '\\bassert\\b', '\\bbreak\\b', '\\bclass\\b', '\\bcontinue\\b', 
            '\\bdef\\b', '\\bdel\\b', '\\belif\\b', '\\belse\\b', '\\bexcept\\b', 
            '\\bfinally\\b', '\\bfor\\b', '\\bfrom\\b', '\\bglobal\\b', 
            '\\bif\\b', '\\bimport\\b', '\\bin\\b', '\\bis\\b', '\\blambda\\b', 
            '\\bnonlocal\\b', '\\bnot\\b', '\\bor\\b', '\\bpass\\b', 
            '\\braise\\b', '\\breturn\\b', '\\btry\\b', '\\bwhile\\b', 
            '\\bwith\\b', '\\byield\\b'
        ]

        self.highlighting_rules = [(QRegularExpression(pattern), keyword_format) for pattern in keywords]

        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(Qt.darkGreen))
        self.highlighting_rules.append((QRegularExpression('".*?"|\'.*?\''), string_format))

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(Qt.red))
        self.highlighting_rules.append((QRegularExpression('#[^\n]*'), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)



class FlowRunNotebookWindow(QWidget):
    def __init__(self, notebook_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Flow Runner Notebook")
        self.setGeometry(220, 120, 1200, 800)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        self.info_label = QLabel(
            f"Flow execution notebook: {os.path.basename(notebook_path)}\n"
            "Run the first code cell to execute the generated flow script using %run."
        )
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label, 0)

        self.notebook_view = EmbeddedNotebook(self)
        self.notebook_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.notebook_view, 1)
        self.notebook_view.load_notebook(notebook_path)

    def closeEvent(self, event):
        try:
            self.notebook_view.stop_server()
        except Exception:
            pass
        super().closeEvent(event)

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
            self.webview.setUrl(QUrl(self._build_url(notebook_path)))
            self.webview.show()
            return

        self.current_notebook_path = notebook_path
        self.status_label.setText(f'Starting Jupyter Notebook for: {os.path.basename(notebook_path)}')

        if not self._start_jupyter_server(root_dir):
            self.status_label.setText('Failed to start Jupyter Notebook. Install the notebook package in this Python environment.')
            return

        QTimer.singleShot(4000, lambda: self.webview.setUrl(QUrl(self._build_url(notebook_path))))
        QTimer.singleShot(4000, self.webview.show)

    def closeEvent(self, event):
        self.stop_server()
        self.editorClosed.emit()
        super().closeEvent(event)

class TextEditWidget(QWidget):
    """
    Custom widget for text input to be embedded inside a TextNode.
    """
    def __init__(self, parent=None):
        super(TextEditWidget, self).__init__(parent)


        self.text_caption = QLabel()
        # self.text_caption.setFixedWidth(60)
        self.text_caption.setWordWrap(True)
        self.text_caption.setStyleSheet("QLabel { color: blue; font-size: 12pt}")
               
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setAlignment(Qt.AlignCenter)
        # self.splitter = QSplitter(self)
        # self.splitter.addWidget(self.text_caption)
        self.layout.addWidget(self.text_caption)
       

class TextNodeWidgetWrapper(NodeBaseWidget):
    """
    Wrapper that allows the custom text widget to be added in a TextNode.
    """

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
        self.node_type='data_node'
        self.node_value_display=False
        self.node_is_path = False
        self.node_input_variable=''
        self.node_input_value=''
        self.node_function_wrapper=''
        self.node_imports=''
        
       
    def add_dynamic_input(self, name, color=(100, 100, 100)):
        """
        Add a dynamic input port to the node.
        
        :param name: Name of the input port
        :param color: Color of the input port as a tuple (R, G, B)
        """
        self.add_input(name, color=color)

    def add_dynamic_output(self, name, color=(100, 100, 100)):
        """
        Add a dynamic output port to the node.
        
        :param name: Name of the output port
        :param color: Color of the output port as a tuple (R, G, B)
        """
        self.add_output(name, color=color)


  
# class TextNode(BaseNode):
#     __identifier__ = 'QuESt.Workspace'
#     NODE_NAME = 'Text Node'

#     def __init__(self):
#         super(TextNode, self).__init__()
#         font = self.view.text_item.font()
#         font.setPointSize(12)
#         self.view.text_item.setFont(font)
        
#         self.set_icon('./images/icons/text_icon.png')
#         self.set_port_deletion_allowed(mode=True)
#         self.node_type='text_node'
#         self.node_input_variable=''
#         self.node_input_value=''
#         self.node_function_wrapper=''
#         self.node_imports=''
#         # Add custom widget to node
#         text_node_widget = TextNodeWidgetWrapper(self.view)
#         self.add_custom_widget(text_node_widget, tab='Custom')
#     def set_size(self,width,height):
#         self.set_property('width',width)
#         self.set_property('height',height)
#         self.view.width, self.view.height = width, height
#         self.model.width, self.model.height = width, height
        
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
        return True  # Override to make this node deletable



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
        self.node_type='python_node'
        self.node_input_variable=''
        self.node_input_value=''
        self.node_value_display=False
        self.node_function_wrapper=''
        self.node_imports=''
        self.node_notebook_path=''

    def add_dynamic_input(self, name, color=(100, 100, 100)):
        """
        Add a dynamic input port to the node.
        
        :param name: Name of the input port
        :param color: Color of the input port as a tuple (R, G, B)
        """
        self.add_input(name, color=color)

    def add_dynamic_output(self, name, color=(100, 100, 100)):
        """
        Add a dynamic output port to the node.
        
        :param name: Name of the output port
        :param color: Color of the output port as a tuple (R, G, B)
        """
        self.add_output(name, color=color)

class quest_workspace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
        QLabel, QLineEdit, QTextEdit, QTabWidget,QPushButton {
            color: black;
            font-size: 12pt;
        }
        """)
        # Nodes and connections dataframes for QuESt Flow
        self.nodes_df = pd.DataFrame(columns=['node_id', 'node_name', 'node_type', 'node_input_variable','node_input_value','node_function_wrapper', 'node_imports', 'node_notebook_path'])
        self.connections_df = pd.DataFrame(columns=['connection_id', 'from_node', 'to_node','mapping'])

        # Toolbar
        self.layout = QHBoxLayout(self)
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

        action_data_node = QAction(data_node_icon, 'Add Data Node', self)
        action_text_node = QAction(text_node_icon, 'Add Text Node', self)
        action_py_node = QAction(py_node_icon, 'Add Py Node', self)
        
        self.toolbar.addAction(action_text_node)
        self.toolbar.addAction(action_data_node)
        self.toolbar.addAction(action_py_node)

        action_text_node.triggered.connect(self.create_text_node)              
        action_data_node.triggered.connect(self.create_data_node)
        action_py_node.triggered.connect(self.create_py_node)
        
        # Create the flow run widget
        self.flow_run_widget = QWidget()
        self.flow_run_widget.setFixedWidth(380) 
        self.flow_run_layout = QHBoxLayout(self.flow_run_widget)
        self.flow_run_label = QLabel("Flow name:")
        self.flow_run_input = QLineEdit()
        self.flow_run_button = QPushButton("Run")
        self.flow_run_button.clicked.connect(self.run_flow)

        self.flow_run_layout.addWidget(self.flow_run_label)
        self.flow_run_layout.addWidget(self.flow_run_input)
        self.flow_run_layout.addWidget(self.flow_run_button)
        
        # Create the flow save widget
        self.flow_save_widget = QWidget()
        self.flow_save_widget.setFixedWidth(380) 
        self.flow_save_layout = QVBoxLayout(self.flow_save_widget)
        self.flow_save_label = QLabel("Save to json file:")
        self.flow_save_path = QLabel()
        self.flow_save_button = QPushButton("Save")
        self.flow_save_button.clicked.connect(self.save_flow)

        self.flow_save_layout.addWidget(self.flow_save_label)
        self.flow_save_layout.addWidget(self.flow_save_path)
        self.flow_save_layout.addWidget(self.flow_save_button)

        # Create the flow load widget
        self.flow_load_widget = QWidget()
        self.flow_load_widget.setFixedWidth(380) 
        self.flow_load_layout = QVBoxLayout(self.flow_load_widget)
        self.flow_load_label = QLabel("Load from json file:")
        self.flow_load_path = QLabel()
        self.flow_load_button = QPushButton("Load")
        self.flow_load_button.clicked.connect(self.load_flow)

        self.flow_load_layout.addWidget(self.flow_load_label)
        self.flow_load_layout.addWidget(self.flow_load_path)
        self.flow_load_layout.addWidget(self.flow_load_button)

        # Create the flow result widget
        self.flow_result_widget = QWidget()
        self.flow_result_widget.setFixedWidth(380) 
        self.flow_result_layout = QVBoxLayout(self.flow_result_widget)
        self.flow_result_label = QLabel()
        self.flow_result_label.setWordWrap(True) 
        self.flow_result_label.setStyleSheet("QLabel { color: blue; }")
        
        self.flow_result_layout.addWidget(self.flow_result_label)
        self.flow_control_container = QWidget()
        self.flow_control_container.setFixedWidth(400)
        self.flow_control_layout = QVBoxLayout(self.flow_control_container)
        self.flow_control_layout.addWidget(self.flow_run_widget)
        self.flow_control_layout.addWidget(self.flow_save_widget)
        self.flow_control_layout.addWidget(self.flow_load_widget)
        self.flow_control_layout.addWidget(self.flow_result_widget)
        self.flow_control_layout.addStretch(1)
        
        # Add the toolbar container to the main layout
        self.graph = NodeGraph()
        self.graph.set_background_color(255, 255, 255)
        self.graph.set_grid_mode(mode=2)
        self.graph.register_node(DataNode)
        self.graph.register_node(PyNode)
        self.graph.register_node(BackNode)
        self.graph_widget = self.graph.widget
        self.layout.addWidget(self.graph_widget)
        
        # Create the id widget
        self.id_widget = QWidget()
        self.id_widget.setFixedWidth(380) 
        self.id_layout = QHBoxLayout(self.id_widget)
        self.id_label = QLabel("Node ID:")
        self.id_layout.addWidget(self.id_label)

        # Create the type widget
        self.type_widget = QWidget()
        self.type_widget.setFixedWidth(380) 
        self.type_layout = QHBoxLayout(self.type_widget)
        self.type_label = QLabel("Node Type:")
        self.type_layout.addWidget(self.type_label)

        # Create the name widget
        self.name_widget = QWidget()
        self.name_widget.setFixedWidth(380) 
        self.name_layout = QHBoxLayout(self.name_widget)
        self.name_label = QLabel("Node name:")
        self.name_input = QLineEdit()
        self.name_button = QPushButton("Update")
        self.name_button.clicked.connect(self.update_node_name)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)
        self.name_layout.addWidget(self.name_button)

        # Create the data widget
        self.data_widget = QWidget()
        self.data_widget.setFixedWidth(380) 
        self.data_layout = QHBoxLayout(self.data_widget)
        self.data_label = QLabel("Output name:")
        self.data_input = QLineEdit()
        self.data_button = QPushButton("Update")
        self.data_button.clicked.connect(self.update_ports)
        self.data_layout.addWidget(self.data_label)
        self.data_layout.addWidget(self.data_input)
        self.data_layout.addWidget(self.data_button)
        self.data_widget.hide()

        # Create the value widget
        self.value_widget = QWidget()
        self.value_widget.setFixedWidth(380) 
        self.value_layout = QVBoxLayout(self.value_widget)
        self.value_label = QLabel("Output value:")
        self.value_input = QLineEdit()
        self.value_checkbox = QCheckBox("Display Value")
        self.value_checkbox.clicked.connect(self.update_data_value)
                
        self.value_path_checkbox=QCheckBox("Is File Path?")
        self.value_path_checkbox.clicked.connect(self.update_data_value)
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
        self.value_layout.addWidget(self.value_button)
        self.value_widget.hide()

        # Python function widget setup with pop-out button
        self.py_widget = QWidget()
        self.py_widget.setFixedWidth(380)
        
        self.py_layout = QVBoxLayout(self.py_widget)
        self.py_label = QLabel("Python Wrapper Notebook:")
        
        self.notebook_view = EmbeddedNotebook()
        self.notebook_view.setMinimumHeight(320)
        
        self.py_button = QPushButton("Update Python Function")
        self.py_button.clicked.connect(self.update_ports)
        
        # Pop-out button at top-right corner
        self.pop_out_btn = QPushButton("↗")
        self.pop_out_btn.setFixedSize(30, 30)
        self.pop_out_btn.clicked.connect(self.toggle_pop_out)

        # Layout for the label and pop-out button horizontally
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.py_label)
        top_layout.addStretch()
        top_layout.addWidget(self.pop_out_btn)

        self.py_layout.addLayout(top_layout)
        self.py_layout.addWidget(self.notebook_view)
        self.py_layout.addWidget(self.py_button)

        self.py_editor_window = None
        self.flow_runner_window = None
        self.is_popped_out = False

        # Create text widget
        self.text_widget = QWidget()
        self.text_widget.setFixedWidth(380)
        self.text_layout = QVBoxLayout(self.text_widget)
        self.text_editor = QLabel("Caption:")
        self.text_input = QTextEdit()  

        self.text_input.setFixedHeight(200)
        self.text_button = QPushButton("Update Caption")
        self.text_button.clicked.connect(self.update_caption_value)
        self.text_widget.hide()

        # Add widgets to the python layout
        self.text_layout.addWidget(self.text_editor)
        self.text_layout.addWidget(self.text_input)
        self.text_layout.addWidget(self.text_button)
        
        # Create a container for name_widget and py_widget
        self.properties_container = QWidget()
        self.properties_container.setFixedWidth(400)
        self.properties_layout = QVBoxLayout(self.properties_container)
        
        # Add the name and python widgets to the properties container
        self.properties_layout.addWidget(self.id_widget)
        self.properties_layout.addWidget(self.type_widget)
        self.properties_layout.addWidget(self.name_widget)
        self.properties_layout.addWidget(self.py_widget)
        self.properties_layout.addWidget(self.text_widget)
        self.properties_layout.addWidget(self.data_widget)
        self.properties_layout.addWidget(self.value_widget)
        
        # Add a stretch to push everything to the top
        self.properties_layout.addStretch(1)
        
        # Ensure widgets are aligned from top to bottom
        self.properties_layout.setAlignment(Qt.AlignTop)
        self.tab_widget = QTabWidget()
        self.tab_widget.setFixedWidth(400)
        self.tab_layout = QHBoxLayout(self.tab_widget)
        # self.tab_layout.addWidget(self.properties_container)
        self.tab_widget.addTab(self.properties_container, "Node Settings")
        self.tab_widget.addTab(self.flow_control_container, "Flow Control")
        # Add the properties widget to the main layout, on the right side
        self.layout.addWidget(self.tab_widget)
        
        # Node selection signals
        self.graph.node_selected.connect(self.on_node_selected)
        self.graph.node_selection_changed.connect(self.on_node_selected)
        self.node_counters = {"DataNode": 0, "PyNode": 0, "TextNode":0}
        self.notebooks_dir = os.path.join(os.getcwd(), "node_notebooks")
        os.makedirs(self.notebooks_dir, exist_ok=True)
    
    def toggle_pop_out(self):
        if not self.is_popped_out:
            self.py_layout.removeWidget(self.notebook_view)
            self.py_layout.removeWidget(self.py_button)
            self.notebook_view.setParent(None)
            self.py_button.setParent(None)

            self.py_editor_window = PopOutNotebookEditor(self.notebook_view, self.py_button)
            self.py_editor_window.editorClosed.connect(self.auto_dock_back_in)
            self.py_editor_window.setWindowTitle("Jupyter Notebook")
            self.py_editor_window.show()

            self.pop_out_btn.setText("↙")
            self.is_popped_out = True
        else:
            self.re_embed_editor()

    def auto_dock_back_in(self):
        if self.is_popped_out:
            self.re_embed_editor()

    def re_embed_editor(self):
        if self.py_editor_window:
            self.py_editor_window.editorClosed.disconnect(self.auto_dock_back_in)
            self.py_editor_window.close()

        self.py_layout.insertWidget(1, self.notebook_view)
        self.py_layout.insertWidget(2, self.py_button)
        self.pop_out_btn.setText("↗")
        self.is_popped_out = False

    def _sanitize_node_name_for_file(self, name):
        return "".join(ch if (ch.isalnum() or ch in ("_", "-", ".")) else "_" for ch in name)

    def _default_notebook_code(self, node_name):
        return (
            "import pandas as pd\n"
            "import numpy as np\n\n"
            f"def {node_name}_function(x):\n"
            "    return {'output': x}\n"
        )

    def _create_notebook_template(self, notebook_path, node_name):
        os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
        nb = nbf.v4.new_notebook()
        nb.cells = [
            nbf.v4.new_markdown_cell(f"# {node_name}\n\nNotebook backing this PyNode."),
            nbf.v4.new_code_cell(self._default_notebook_code(node_name)),
        ]
        with open(notebook_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

    def _ensure_node_notebook(self, node):
        path = getattr(node, "node_notebook_path", "") or ""
        if path and os.path.exists(path):
            return path
        safe_name = self._sanitize_node_name_for_file(node.name())
        notebook_path = os.path.join(self.notebooks_dir, f"{safe_name}.ipynb")
        if not os.path.exists(notebook_path):
            self._create_notebook_template(notebook_path, node.name())
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

    def _write_notebook_from_legacy_python(self, node):
        """Create or overwrite a node notebook from legacy JSON fields."""
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

        node.node_notebook_path = notebook_path
        return notebook_path

    def _rename_pynode_notebook_and_wrapper(self, node, old_name, new_name):
        """Rename the backing notebook file and update the wrapper function name."""
        old_func = f"{old_name}_function"
        new_func = f"{new_name}_function"

        old_path = getattr(node, "node_notebook_path", "") or ""
        safe_new_name = self._sanitize_node_name_for_file(new_name)
        new_path = os.path.join(self.notebooks_dir, f"{safe_new_name}.ipynb")

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

            try:
                if os.path.abspath(old_path) != os.path.abspath(new_path) and os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                pass
        else:
            self._create_notebook_template(new_path, new_name)

        node.node_notebook_path = new_path
        return new_path

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
        nodes_data=[]
        self.flow_result_label.setText('')
        for node in self.graph.all_nodes():
            # Extract the required attributes from each node
            node_data = [
            node.id, 
            node.name(), 
            getattr(node, 'node_type', ''), 
            getattr(node, 'node_input_variable', ''), 
            getattr(node, 'node_input_value', ''),
            getattr(node, 'node_value_display', False),  
            getattr(node, 'node_is_path', False),
            getattr(node, 'node_function_wrapper', ''), 
            getattr(node, 'node_imports', ''),
            getattr(node, 'node_notebook_path', '')
            ]
            
            # Append the node data to the data list
            nodes_data.append(node_data)
        # Create a DataFrame from the data list
        print(nodes_data)
        if len(nodes_data)>0:
            self.nodes_df = pd.DataFrame(nodes_data, columns=['node_id', 'node_name', 'node_type', 'node_input_variable', 'node_input_value', 'node_value_display','node_is_path', 'node_function_wrapper', 'node_imports', 'node_notebook_path'])

        connections_data = []
        if 'connections' in self.graph.serialize_session():
            connections=self.graph.serialize_session()['connections']
            # Iterate through each connection to extract information
            for i, connection in enumerate(connections, start=1):
                connection_id = i
                from_node = connection['out'][0]
                to_node = connection['in'][0]
                mapping = {connection['out'][1]: connection['in'][1]}
                
                # Append the extracted information to the data list
                connections_data.append([connection_id, from_node, to_node, mapping])

        # Create a DataFrame from the data list
        if len(connections_data)>0:
            self.connections_df = pd.DataFrame(connections_data, columns=['connection_id', 'from_node', 'to_node', 'mapping'])
        
        # print(self.nodes_df)
        # print(self.connections_df)
        # flow_name=self.flow_run_input.text()
        # self.flow=flow(flow_name= flow_name,nodes_df=self.nodes_df, connections_df=self.connections_df)
        # self.flow.set_inputs()
        # self.flow.get_outputs(key='Show')
        # self.flow.make()
        # self.flow.save('./')
        # result=self.flow.run()
        # output_text=f'Outputs:\n {result.stdout} \nErrors:\n {result.stderr}'
        # self.flow_result_label.setText(output_text)
        
    def _create_flow_runner_notebook(self, script_path, flow_name):
        script_path = os.path.abspath(script_path)
        flow_stub = self._sanitize_node_name_for_file(flow_name or 'flow_run')
        notebook_path = os.path.join(os.path.dirname(script_path), f"{flow_stub}_runner.ipynb")

        code = (
            f'script_path = r"{script_path}"\n'
            'print(f"Running: {script_path}")\n'
            '%run "$script_path"\n'
        )

        nb = nbf.v4.new_notebook()
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

    def run_flow(self):
        self.update_flow()
        flow_name=self.flow_run_input.text()
        self.flow=flow(flow_name= flow_name,nodes_df=self.nodes_df, connections_df=self.connections_df)
        self.flow.set_inputs()
        self.flow.get_outputs(key='Show')
        self.flow.make()
        self.flow.save('./')
        script_path = self.flow.py_file_name
        notebook_path = self._create_flow_runner_notebook(script_path, flow_name)
        self._open_flow_runner_notebook(notebook_path)
        self.flow_result_label.setText(f"Opened flow runner notebook:\n{notebook_path}")

    def save_flow(self):
        self.update_flow()
        nodes_df_json = self.nodes_df.to_json(orient='records')
        connection_df_json = self.connections_df.to_json(orient='records')
        layout_dict = self.graph.serialize_session()
        flow_json_data = {
            "flow_name": self.flow_run_input.text(),
            "flow_layout": layout_dict,
            "nodes_df": json.loads(nodes_df_json),
            "connections_df": json.loads(connection_df_json)
        }

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
            raise ValueError(f'Failed to save file: {e}')

    def load_path(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select File or Folder")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)

        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                raw_path = selected[0]
                path_text = f'"{raw_path}"'   # ← add quotes here
                self.value_input.setText(path_text)


    def load_flow(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Flow JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        self.flow_load_path.setText(path)

        try:
            with open(path, 'r') as file:  
                flow_json_data = json.load(file)
        except FileNotFoundError:
            raise ValueError('The specified JSON file path does not exist. Please check the path and try again.')
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")

        # Load graph layout
        flow_name=flow_json_data['flow_name']
        self.flow_run_input.setText(flow_name)
        
        layout_dict = flow_json_data['flow_layout']
        if hasattr(self, 'normalize_layout_icons'):
            layout_dict = self.normalize_layout_icons(layout_dict)

        self.graph.clear_session()
        self.graph.deserialize_session(layout_dict)

        nodesdf_list=flow_json_data['nodes_df']
        # self.nodes_df=pd.DataFrame.from_dict(nodesdf_dict,dtype=str)
        print(nodesdf_list)
        existing_nodes={str(node.name()):node for node in self.graph.all_nodes()}
        # print(existing_nodes)
        # print(existing_nodes)
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
                if node.node_type=='back_node':
                    node.set_text(text='')
                    print(node.node_input_value)
                    node.set_text(text=node.node_input_value)
                
                print(node.id,node.node_type, node.node_input_variable,node.node_input_value,node.node_value_display, node.node_function_wrapper)
            else:
                print(f"NO MATCH FOR NODE NAME: {repr(node_name)}")
        
    def on_node_selected(self):
        self.update_flow()
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            self.tab_widget.setCurrentIndex(0)
            # Show properties widget and update text input with node name
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
                self.notebook_view.load_notebook(notebook_path)
                self.data_widget.hide()
                self.value_widget.hide()
                self.text_widget.hide()
                
            elif isinstance(selected_nodes[0], DataNode):
                self.py_widget.hide()
                self.text_widget.hide()
                self.data_widget.show()
                self.value_widget.show()

                node = selected_nodes[0]
                self.data_input.setText(node.node_input_variable)
                self.value_input.setText(node.node_input_value)
                self.value_checkbox.setChecked(node.node_value_display)

                # Restore the path checkbox + browse button state
                self.value_path_checkbox.setChecked(getattr(node, "node_is_path", False))
                self.value_browse_button.setEnabled(getattr(node, "node_is_path", False))
            
            else:
                self.py_widget.hide()
                self.data_widget.hide()
                self.value_widget.hide()
                self.text_widget.show()
                self.text_input.setText(selected_nodes[0].node_input_value)
                
            self.name_input.setText(selected_nodes[0].name())
            node_id = selected_nodes[0].id
            node_type = selected_nodes[0].type_
            try:
                node_outputs = list(selected_nodes[0].outputs().keys())
                if len(node_outputs)>0:
                    self.data_input.setText(f"{node_outputs[0]}")
            except:
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
            self.value_browse_button.setEnabled(False)
    
    def update_node_name(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) != 1:
            return

        node = selected_nodes[0]
        old_name = node.name()
        new_name = (self.name_input.text() or "").strip()

        if not new_name or new_name == old_name:
            return

        old_pos = node.pos()
        node.set_name(new_name)
        node.set_selected(False)
        node.set_selected(True)
        node.set_pos(old_pos[0], old_pos[1])
        node.node_name1 = node.name()

        if isinstance(node, PyNode):
            self._rename_pynode_notebook_and_wrapper(node, old_name, new_name)
            if hasattr(self, "notebook_view"):
                self.notebook_view.load_notebook(node.node_notebook_path)

    def update_caption_value(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            old_pos=selected_nodes[0].pos()
            document=self.text_input.document()
            document_text= document.toPlainText()
            docSize = document.size()
            selected_nodes[0].set_size(document.idealWidth(), docSize.height())
            selected_nodes[0].node_input_value=document_text
            selected_nodes[0].set_text(text=selected_nodes[0].node_input_value)
            selected_nodes[0].set_pos(old_pos[0],old_pos[1])
    
    def update_data_value(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            old_pos=selected_nodes[0].pos()
            # Show properties widget and update value input with value
            value_checked = self.value_checkbox.isChecked()
            path_checked = self.value_path_checkbox.isChecked()
            self.value_browse_button.setEnabled(path_checked)
            selected_nodes[0].node_value_display=value_checked
            selected_nodes[0].node_is_path=path_checked
            
            text=self.value_input.text()
            selected_nodes[0].node_input_value=text
            widget=selected_nodes[0].get_widget('Text Caption')
            if value_checked:
                widget.set_value(selected_nodes[0].node_input_value)
            else:
                widget.set_value("")
            
            print(selected_nodes[0].properties())
                         
            selected_nodes[0].set_pos(old_pos[0],old_pos[1])

    def update_ports(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) != 1:
            return  # Exit if not exactly one node is selected
        
        node = selected_nodes[0]
        old_pos=node.pos()
        if isinstance(node, PyNode):
            try:
                notebook_path = self._ensure_node_notebook(node)
                python_code = self._notebook_to_code(notebook_path)
                parsed_ast = ast.parse(python_code)

                imports_text = ""
                import_statements = [n for n in ast.walk(parsed_ast) if isinstance(n, (ast.Import, ast.ImportFrom))]
                for imp in import_statements:
                    if isinstance(imp, ast.Import):
                        for alias in imp.names:
                            if alias.asname:
                                imports_text += f"import {alias.name} as {alias.asname}\n"
                            else:
                                imports_text += f"import {alias.name}\n"
                    elif isinstance(imp, ast.ImportFrom):
                        for alias in imp.names:
                            if alias.asname:
                                imports_text += f"from {imp.module} import {alias.name} as {alias.asname}\n"
                            else:
                                imports_text += f"from {imp.module} import {alias.name}\n"

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

                for in_port_name in list(node.inputs().keys()):
                    for connected_port in node.inputs()[in_port_name].connected_ports():
                        node.inputs()[in_port_name].disconnect_from(connected_port)
                    node.delete_input(in_port_name)

                for port_name in input_ports:
                    node.add_dynamic_input(port_name)

                for fc in ast.walk(func_def):
                    if isinstance(fc, ast.Return):
                        if isinstance(fc.value, ast.Dict):
                            output_ports = [key.s for key in fc.value.keys if isinstance(key, ast.Constant)]
                        break

                for out_port_name in list(node.outputs().keys()):
                    for connected_port in node.outputs()[out_port_name].connected_ports():
                        node.outputs()[out_port_name].disconnect_from(connected_port)
                    node.delete_output(out_port_name)

                for key in output_ports:
                    node.add_dynamic_output(key)
            except Exception as e:
                print(f"Failed to update Python node from notebook: {e}")
        elif isinstance(node, DataNode):
            for out_port_name in node.outputs().keys():
                    for connected_port in  node.outputs()[out_port_name].connected_ports():
                        node.outputs()[out_port_name].disconnect_from(connected_port)
                    node.delete_output(out_port_name)

            variable_name = self.data_input.text()
            node.add_dynamic_output(variable_name)
            node.node_input_variable=variable_name
 
        node.set_pos(old_pos[0],old_pos[1])      

    def get_newest_node_position(self):
        nodes = self.graph.all_nodes()  # Get all nodes in the graph
        position=(0,0)
        if nodes:
            newest_node = nodes[-1]  # Assuming the newest node is the last one added
            position = newest_node.pos()
        return position
    
    def create_data_node(self):
        self.update_flow()
        self.node_counters["DataNode"] += 1
        node_name = f"DataNode{self.node_counters['DataNode']}"
        latest_pos = list(self.get_newest_node_position())
        new_pos=(latest_pos[0]+100,latest_pos[1]+100)
        self.graph.create_node('QuESt.Workspace.DataNode', name=node_name, color=(255, 255, 255), text_color=(0,0,0),pos=new_pos,selected=True,push_undo=True)

    def create_text_node(self):
        self.update_flow()
        self.node_counters["TextNode"] = self.node_counters.get("TextNode", 0) + 1
        node_name = f"TextNode{self.node_counters['TextNode']}"
        latest_pos = self.get_newest_node_position()
        new_pos = (latest_pos[0] + 100, latest_pos[1] + 100) 
        self.graph.create_node('QuESt.Workspace.BackNode', name=node_name, color=(255, 255, 155), text_color=(0,0,0), pos=new_pos, selected=True,push_undo=True)
                     
    def create_py_node(self):
        self.update_flow()
        self.node_counters["PyNode"] += 1
        node_name = f"PyNode{self.node_counters['PyNode']}"
        latest_pos = list(self.get_newest_node_position())
        new_pos=(latest_pos[0]+100,latest_pos[1]+100)
        node = self.graph.create_node('QuESt.Workspace.PyNode', name=node_name, color=(255, 255, 255), text_color=(0,0,0),pos=new_pos,selected=True,push_undo=True)
        notebook_path = os.path.join(self.notebooks_dir, f"{self._sanitize_node_name_for_file(node_name)}.ipynb")
        if not os.path.exists(notebook_path):
            self._create_notebook_template(notebook_path, node_name)
        node.node_notebook_path = notebook_path
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_nodes = self.graph.selected_nodes()
            for node in selected_nodes:
                if hasattr(node, "can_be_deleted") and not node.can_be_deleted():
                    continue
                self.graph.delete_node(node)
            self.update_flow()
        else:
            super().keyPressEvent(event)



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_node_selected()
        super().mousePressEvent(event)


class WMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuESt Workspace")
        self.resize(1400, 900)
        
        # Create the custom widget and set it as the central widget
        self.quest_workspace_widget = quest_workspace(self)
        self.addToolBar(Qt.LeftToolBarArea, self.quest_workspace_widget.toolbar)
        self.setCentralWidget(self.quest_workspace_widget)

    def set_light_graph(self):
        self.quest_workspace_widget.graph.set_background_color(255, 255, 255)
    
    def set_dark_graph(self):
        self.quest_workspace_widget.graph.set_background_color(25, 25, 25)
        self.quest_workspace_widget.graph.set_grid_color(62, 62, 62)
 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WMainWindow()
    window.show()
    sys.exit(app.exec())
