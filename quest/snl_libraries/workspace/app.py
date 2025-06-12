import sys
import os
import inspect, ast, json
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

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

class PopOutPythonEditor(QWidget):
    editorClosed = Signal()

    def __init__(self, editor, update_button, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.update_button = update_button

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.update_button)
        self.setLayout(layout)
        self.setWindowTitle("Python Editor")
        self.setGeometry(200, 200, 500, 400)

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
        self.nodes_df = pd.DataFrame(columns=['node_id', 'node_name', 'node_type', 'node_input_variable','node_input_value','node_function_wrapper', 'node_imports'])
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
        self.flow_run_widget.setFixedWidth(300) 
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
        self.flow_save_widget.setFixedWidth(300) 
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
        self.flow_load_widget.setFixedWidth(300) 
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
        self.flow_result_widget.setFixedWidth(300) 
        self.flow_result_layout = QVBoxLayout(self.flow_result_widget)
        self.flow_result_label = QLabel()
        self.flow_result_label.setWordWrap(True) 
        self.flow_result_label.setStyleSheet("QLabel { color: blue; }")
        
        self.flow_result_layout.addWidget(self.flow_result_label)
        self.flow_control_container = QWidget()
        self.flow_control_container.setFixedWidth(320)
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
        self.id_widget.setFixedWidth(300) 
        self.id_layout = QHBoxLayout(self.id_widget)
        self.id_label = QLabel("Node ID:")
        self.id_layout.addWidget(self.id_label)

        # Create the type widget
        self.type_widget = QWidget()
        self.type_widget.setFixedWidth(300) 
        self.type_layout = QHBoxLayout(self.type_widget)
        self.type_label = QLabel("Node Type:")
        self.type_layout.addWidget(self.type_label)

        # Create the name widget
        self.name_widget = QWidget()
        self.name_widget.setFixedWidth(300) 
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
        self.data_widget.setFixedWidth(300) 
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
        self.value_widget.setFixedWidth(300) 
        self.value_layout = QVBoxLayout(self.value_widget)
        self.value_label = QLabel("Output value:")
        self.value_input = QLineEdit()
        self.value_checkbox = QCheckBox("Display Value")
        self.value_checkbox.clicked.connect(self.update_data_value)
        self.value_button = QPushButton("Update")
        self.value_button.clicked.connect(self.update_data_value)

        self.value_layout.addWidget(self.value_label)
        self.value_layout.addWidget(self.value_input)
        self.value_layout.addWidget(self.value_checkbox)
        self.value_layout.addWidget(self.value_button)
        self.value_widget.hide()

        # Python function widget setup with pop-out button
        self.py_widget = QWidget()
        self.py_widget.setFixedWidth(300)
        
        self.py_layout = QVBoxLayout(self.py_widget)
        self.py_label = QLabel("Python Wrapper Function:")
        
        self.py_input = PythonEditor()
        self.python_syntax_highlighter = PythonSyntaxHighlighter(self.py_input.document())
        self.py_input.setFixedHeight(200)
        
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
        self.py_layout.addWidget(self.py_input)
        self.py_layout.addWidget(self.py_button)

        self.py_editor_window = None
        self.is_popped_out = False

        # Create text widget
        self.text_widget = QWidget()
        self.text_widget.setFixedWidth(300)
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
        self.properties_container.setFixedWidth(320)
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
        self.tab_widget.setFixedWidth(320)
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
    
    def toggle_pop_out(self):
        if not self.is_popped_out:
            # Pop out editor and update button
            self.py_layout.removeWidget(self.py_input)
            self.py_layout.removeWidget(self.py_button)
            self.py_input.setParent(None)
            self.py_button.setParent(None)

            self.py_editor_window = PopOutPythonEditor(self.py_input, self.py_button)
            self.py_editor_window.editorClosed.connect(self.auto_dock_back_in)
            self.py_editor_window.show()

            self.pop_out_btn.setText("↙")
            self.is_popped_out = True
        else:
            self.re_embed_editor()

    def auto_dock_back_in(self):
        # Automatically called when the pop-out window is closed directly
        self.re_embed_editor()

    def re_embed_editor(self):
        if self.py_editor_window:
            self.py_editor_window.editorClosed.disconnect(self.auto_dock_back_in)
            self.py_editor_window.close()

        self.py_layout.insertWidget(1, self.py_input)
        self.py_layout.insertWidget(2, self.py_button)
        self.pop_out_btn.setText("↗")
        self.is_popped_out = False

    def update_flow(self):
        nodes_data=[]
        self.flow_result_label.setText('')
        for node in self.graph.all_nodes():
            # Extract the required attributes from each node
            node_data = [
            node.id, 
            node.name(), 
            node.node_type, 
            node.node_input_variable, 
            node.node_input_value,
            node.node_value_display,  
            node.node_function_wrapper, 
            node.node_imports
            ]
            
            # Append the node data to the data list
            nodes_data.append(node_data)
        # Create a DataFrame from the data list
        print(nodes_data)
        if len(nodes_data)>0:
            self.nodes_df = pd.DataFrame(nodes_data, columns=['node_id', 'node_name', 'node_type', 'node_input_variable', 'node_input_value', 'node_value_display','node_function_wrapper', 'node_imports'])

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
        
    def run_flow(self):
        self.update_flow()
        flow_name=self.flow_run_input.text()
        self.flow=flow(flow_name= flow_name,nodes_df=self.nodes_df, connections_df=self.connections_df)
        self.flow.set_inputs()
        self.flow.get_outputs(key='Show')
        self.flow.make()
        self.flow.save('./')
        result=self.flow.run()
        output_text=f'Outputs:\n {result.stdout} \nErrors:\n {result.stderr}'
        self.flow_result_label.setText(output_text)

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
        layout_dict=flow_json_data['flow_layout']
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
          
            if node_name in existing_nodes:
                node = existing_nodes[node_name]
                print(node.properties())
                node.node_type = node_data['node_type']
                node.node_input_variable = node_data['node_input_variable']
                node.node_input_value = node_data['node_input_value']
                node.node_value_display = node_data['node_value_display']
                node.node_function_wrapper = node_data['node_function_wrapper']
                node.node_imports = node_data['node_imports']
                if node.node_type=='back_node':
                    node.set_text(text='')
                    print(node.node_input_value)
                    node.set_text(text=node.node_input_value)
                
                print(node.id,node.node_type, node.node_input_variable,node.node_input_value,node.node_value_display, node.node_function_wrapper)
        
    def on_node_selected(self):
        self.update_flow
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            # Show properties widget and update text input with node name
            if isinstance(selected_nodes[0], PyNode):
                self.py_widget.show()
                pycode=selected_nodes[0].node_imports+selected_nodes[0].node_function_wrapper
                self.py_input.setText(pycode)
                self.data_widget.hide()
                self.value_widget.hide()
                self.text_widget.hide()
                
            elif isinstance(selected_nodes[0], DataNode):
                self.py_widget.hide()
                self.text_widget.hide()
                self.data_widget.show()
                self.value_widget.show()
                self.data_input.setText(selected_nodes[0].node_input_variable)
                self.value_input.setText(selected_nodes[0].node_input_value)
                self.value_checkbox.setChecked(selected_nodes[0].node_value_display)
            
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
            self.name_input.setText(None)
            self.id_label.setText("Node ID:")
            self.type_label.setText("Node Type:")
            self.py_input.setText(None)
            self.data_input.setText(None)
            self.value_input.setText(None)
            self.text_input.setText(None)
    
    def update_node_name(self):
        selected_nodes = self.graph.selected_nodes()
        if len(selected_nodes) == 1:
            new_name = self.name_input.text()
            old_pos=selected_nodes[0].pos()
            selected_nodes[0].set_name(new_name)
            selected_nodes[0].set_selected(selected=False)
            selected_nodes[0].set_selected(selected=True)
            selected_nodes[0].set_pos(old_pos[0],old_pos[1])
            selected_nodes[0].node_name1=selected_nodes[0].name()
    
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
            checked = self.value_checkbox.isChecked()
            selected_nodes[0].node_value_display=checked
            text=self.value_input.text()
            selected_nodes[0].node_input_value=text
            widget=selected_nodes[0].get_widget('Text Caption')
            if checked:
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
                python_code = self.py_input.toPlainText()

                # Parse the Python code into an AST
                parsed_ast = ast.parse(python_code)

                # Initialize strings for imports
                imports_text = ""
                # Initialize an empty list to hold full function definitions
                func_defs = []

                # Extracting import statements
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

                node.node_imports=imports_text

                # Extracting all function definitions
                func_defs = [n for n in ast.walk(parsed_ast) if isinstance(n, ast.FunctionDef)]
                if len(func_defs)>0:
                    func_def = func_defs[0]
                else:
                    raise ValueError('Wrapper function not found!')
                function_text = ast.unparse(func_def)
                node.node_function_wrapper=function_text

                # Initialize lists to hold the new input and output port names
                input_ports = []
                output_ports = []
                
                # Analyze the arguments of the function for input ports
                input_ports = [arg.arg for arg in func_def.args.args]
                
                for in_port_name in node.inputs().keys():
                    for connected_port in  node.inputs()[in_port_name].connected_ports():
                        node.inputs()[in_port_name].disconnect_from(connected_port)
                    node.delete_input(in_port_name)
                
                for port_name in input_ports:
                    node.add_dynamic_input(port_name)

                # Look for a return statement and analyze it for output ports
                for fc in ast.walk(func_def):
                    if isinstance(fc, ast.Return):
                        if isinstance(fc.value, ast.Dict):  # Direct return of a dictionary
                            output_ports = [key.s for key in fc.value.keys if isinstance(key, ast.Constant)]
                        break  # Only consider the first return statement
                
                for out_port_name in node.outputs().keys():
                    for connected_port in  node.outputs()[out_port_name].connected_ports():
                        node.outputs()[out_port_name].disconnect_from(connected_port)
                    node.delete_output(out_port_name)

                for key in output_ports:
                    node.add_dynamic_output(key)
            except SyntaxError as e:
                print(f"Syntax error in Python function: {e}")
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
        self.graph.create_node('QuESt.Workspace.PyNode', name=node_name, color=(255, 255, 255), text_color=(0,0,0),pos=new_pos,selected=True,push_undo=True)
        
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
