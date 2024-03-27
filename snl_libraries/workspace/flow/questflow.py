# from nodes.pynodes import python_node, data_node
import pandas as pd
import json
import subprocess
# from nodes.sequence import *
def build_graph(df):
    graph_temp = {}
    for _, row in df.iterrows():
        if row['from_node'] not in graph_temp:
            graph_temp[row['from_node']] = set()
        graph_temp[row['from_node']].add(row['to_node'])
        if row['to_node'] not in graph_temp:
            graph_temp[row['to_node']] = set()
    return graph_temp

def find_start_nodes(graph_input):
    all_nodes = set(graph_input.keys())
    to_nodes = set(node for edges in graph_input.values() for node in edges)
    start_nodes = all_nodes - to_nodes
    return start_nodes

def remove_nodes(graph_input, nodes_to_remove):
    for node in nodes_to_remove:
        del graph_input[node]
    for edges in graph_input.values():
        edges -= nodes_to_remove
    
def find_sequence(graph_input):
    results = []
    while graph_input:
        start_nodes = find_start_nodes(graph_input)
        if not start_nodes:
            break
        results.append(list(start_nodes))
        remove_nodes(graph_input, start_nodes)
    return results

def sort_df_based_on_sequence(df, results):
    # Create a mapping of node to its removal order
    df_temp=df
    node_order = {}
    for order, nodes in enumerate(results, start=1):
        for node in nodes:
            node_order[node] = order

    # Assign an order to each row based on the 'from_node' column
    df_temp['removal_order'] = df_temp['from_node'].map(node_order)

    # Sort the DataFrame based on the removal order
    sorted_df = df_temp.sort_values(by='removal_order').drop('removal_order', axis=1)

    # Reset the index of the sorted DataFrame
    sorted_df = sorted_df.reset_index(drop=True)
    return sorted_df

class flow:
    def __init__(self, flow_name, nodes_df=None, connections_df=None):
        """
        Initializes the Flow with a name, optional dataframes for nodes and connections with specific columns, and initializes
        py_dict dictionary based on the nodes_df if provided.
        
        Parameters:
        - flow_name: The name of the flow.
        - nodes_df: A DataFrame containing node information.
        - connections_df: A DataFrame containing connection information.
        """
        self.flow_name = flow_name
        self.nodes_df = pd.DataFrame(columns=['node_id', 'node_name', 'node_type', 'node_input_variable','node_input_value','node_function_wrapper', 'node_imports'])
        self.connections_df = pd.DataFrame(columns=['connection_id', 'from_node', 'to_node','mapping'])
        self.py_dict = {"imports": {}, "node_functions": {},"node_instantiations":{}, "set_inputs":{},"node_connections": {},"get_outputs":{}}
        self.py_dict["imports"]["main"] = "from snl_libraries.workspace.nodes.pynodes import python_node, data_node\nimport pandas, json"
        self.py_file_name = ''
        self.main_py = ''
        if nodes_df is not None:
            for col in ['node_id', 'node_name', 'node_type', 'node_function_wrapper', 'node_imports']:
                if col not in nodes_df.columns:
                    raise ValueError(f"Missing '{col}' column in nodes_df")
            for _, node in nodes_df.iterrows():
                self.add_node(node)
        
        if connections_df is not None:
            for col in ['connection_id', 'from_node', 'to_node','mapping']:
                if col not in connections_df.columns:
                    raise ValueError(f"Missing '{col}' column in connections_df")
            for _, connection in connections_df.iterrows():
                self.add_connection(connection)
         
        self._update_graph()
                   
    def add_node(self, new_node):
        # Validate new_node dictionary keys
        required_keys = ['node_id', 'node_name', 'node_type', 'node_input_variable','node_input_value','node_function_wrapper', 'node_imports']
        if not all(key in new_node for key in required_keys):
            missing_keys = [key for key in required_keys if key not in new_node]
            raise ValueError(f"Missing keys in new_node dictionary: {missing_keys}")
        # Check if the node_id already exists
        if new_node['node_id'] in self.nodes_df['node_id'].values:
            raise ValueError(f"Node ID '{new_node['node_id']}' already exists in the flow.")

        # Check if the node name already exists
        if new_node['node_name'] in self.nodes_df['node_name'].values:
            raise ValueError(f"Node '{new_node['node_name']}' already exists in the flow.")
        
        # Ensure the function name matches the {node_name}_function pattern
        if 'python_node' == new_node['node_type']:
            if not new_node['node_function_wrapper'].startswith(f"def {new_node['node_name']}_function"):
                raise ValueError(f"Function wrapper name must be '{new_node['node_name']}_function'.")

        # Ensure data nodes are initialized with node_input_variable that follow python rules for variable names and nonempty node_input_value
        if 'data_node' == new_node['node_type']:
            # Validate node_input_variable according to Python variable naming rules
            if not new_node['node_input_variable'].replace('_', '').isidentifier() or not new_node['node_input_variable'][0].isalpha():
                raise ValueError(f"Variable name '{new_node['node_input_variable']}' does not follow Python variable naming conventions.")

            # Ensure nonempty node_input_value
            if new_node['node_input_value'] == '':
                raise ValueError("node_input_value cannot be empty for data nodes.")
            
        # Update self.nodes_df
        self.nodes_df = pd.concat([self.nodes_df, pd.DataFrame([new_node])], ignore_index=True)
        node_name = new_node['node_name']
        node_type = new_node['node_type']
        node_id = new_node['node_id']
        self.py_dict["imports"][node_name] = new_node.get('node_imports', "")
                
        if node_type == 'data_node':
            self.py_dict["node_instantiations"][node_name] = f"node{node_id}=data_node(node_name='{node_name}')"
            self.py_dict["node_functions"][node_name] = ""
        elif node_type == 'python_node':
            self.py_dict["node_instantiations"][node_name] = f"node{node_id}=python_node(node_name='{node_name}',function={node_name}_function)"
            self.py_dict["node_functions"][node_name] = new_node.get('node_function_wrapper', "")
        else:
            raise ValueError(f"Note type {node_type} does not exist")
   
    def remove_node(self, node_name):
        """
        Removes a node from the flow based on the node's name.
        
        Parameters:
        - node_name: The name of the node to remove.
        """
        # Check if the node exists in nodes_df
        if node_name not in self.nodes_df['node_name'].values:
            raise ValueError(f"Node '{node_name}' does not exist in the flow.")
        
        # Remove the node from nodes_df
        self.nodes_df = self.nodes_df[self.nodes_df['node_name'] != node_name]
        
        # Update py_dict by removing any references to the node
        if node_name in self.py_dict["imports"]:
            del self.py_dict["imports"][node_name]
        if node_name in self.py_dict["node_functions"]:
            del self.py_dict["node_functions"][node_name]
        if node_name in self.py_dict["node_instantiations"]:
            del self.py_dict["node_instantiations"][node_name]
        
        # Remove corresponding connections in connections_df
        # Find all connections associated with this node (either from or to this node)
        associated_connections = self.connections_df[
            (self.connections_df['from_node'] == node_name) | 
            (self.connections_df['to_node'] == node_name)]['connection_id'].values
    
        # Remove all associated connections using remove_connection method
        for connection_id in associated_connections:
            self.remove_connection(connection_id)

    def add_connection(self, new_connection):
        """
        Adds a new connection to connections_df and updates node_connections in py_dict.
        
        Parameters:
        - new_connection: A dictionary with the connection details, including 'connection_id', 
                        'from_node', 'to_node', and 'mapping'.
        """
        required_keys = ['connection_id', 'from_node', 'to_node', 'mapping']
        if not all(key in new_connection for key in required_keys):
            missing_keys = [key for key in required_keys if key not in new_connection]
            raise ValueError(f"Missing keys in new_connection dictionary: {missing_keys}")
        
        # Check if the connection already exists based on from_node and to_node
        existing_connection = self.connections_df[
            (self.connections_df['from_node'] == new_connection['from_node']) & 
            (self.connections_df['to_node'] == new_connection['to_node'])& (self.connections_df['mapping']==new_connection['mapping'])
        ]

        if not existing_connection.empty:
            raise ValueError(f"Connection from '{new_connection['from_node']}' to '{new_connection['to_node']}' already exists in the flow.")
    
        # Add new connection to connection_df
        self.connections_df = pd.concat([self.connections_df, pd.DataFrame([new_connection])], ignore_index=True)
        
        # Update py_dict with the new connection
        from_node = new_connection['from_node']
        # from_node_id = self.nodes_df['node_id'][self.nodes_df['node_name']==from_node].values[0]
        to_node = new_connection['to_node']
        # to_node_id = self.nodes_df['node_id'][self.nodes_df['node_name']==to_node].values[0]
        mapping = new_connection['mapping']
        connection_id = new_connection['connection_id']
        self.py_dict['node_connections'][connection_id] = f"node{from_node}.connect_to(to_node_list=[node{to_node}], mapping=[{mapping}])"

    def remove_connection(self, connection_id):
        """
        Removes a connection from connections_df and py_dict['node_connections'] based on the connection_id.
        
        Parameters:
        - connection_id: The ID of the connection to remove.
        """
        if connection_id not in self.connections_df['connection_id'].values:
            raise ValueError(f"Connection '{connection_id}' does not exist in the flow.")
        
        # Remove the connection from connections_df
        self.connections_df = self.connections_df[self.connections_df['connection_id'] != connection_id]
        
        # Remove the connection from py_dict
        if connection_id in self.py_dict['node_connections']:
            del self.py_dict['node_connections'][connection_id]
    
    def _update_graph(self):
        graph_temp = build_graph(self.connections_df)
        self.start_nodes = list(find_start_nodes(graph_temp))
        self.sequence = find_sequence(graph_temp)
        self.graph_dict = build_graph(self.connections_df)

        connected_nodes=[]
        for i in range(len(self.sequence)):
            connected_nodes+=self.sequence[i]
        self.connected_nodes=connected_nodes

    def set_inputs(self):
         
        self._update_graph()
        # Check if start nodes of the flow are data nodes, if not raise error that start nodes must be data nodes
        for start_node in self.start_nodes:
            start_node_type = self.nodes_df['node_type'][self.nodes_df['node_id']==start_node].values[0]
            if start_node_type != 'data_node':
                raise ValueError(f"Start node '{start_node}' must be a data node.")
            
        # Set input values for start nodes by adding proper python code into self.py_dict
        for start_node in self.start_nodes:
            start_node_input_variable = self.nodes_df['node_input_variable'][self.nodes_df['node_id']==start_node].values[0]
            start_node_input_value = self.nodes_df['node_input_value'][self.nodes_df['node_id']==start_node].values[0]
            self.py_dict['set_inputs'][start_node]=f"node{start_node}.set_inputs({start_node_input_variable}={start_node_input_value})"

    def get_outputs(self, key=None):
        self._update_graph()
        
        for connected_node in self.connected_nodes:
            connected_node_name = self.nodes_df['node_name'][self.nodes_df['node_id']==connected_node].values[0]
            if key==None:
                self.py_dict['get_outputs'][connected_node_name]=f"node{connected_node}_outputs=node{connected_node}.get_outputs()"
            elif key=='Show':
                self.py_dict['get_outputs'][connected_node_name]=f"print('node{connected_node}_outputs:',node{connected_node}.get_outputs())"
            else:
                raise ValueError("get_outputs key must be None or 'Show' ")
    # def load(self,flow_file_name):
    #     nodes_df=None
    #     connections_df=None

    #     if nodes_file_name.endswith('.csv'):
    #         # Load CSV file
    #         nodes_df = pd.read_csv(nodes_file_name,dtype=str,na_filter=False)
    #     elif nodes_file_name.endswith('.json'):
    #         # Load JSON file
    #         nodes_df = pd.read_json(nodes_file_name,dtype=str)
    #     else:
    #         # Raise an error for unsupported file formats
    #         raise ValueError("Unsupported file format. Please use a .csv or .json file.")
        
    #     if connections_file_name.endswith('.csv'):
    #         # Load CSV file
    #         nodes_df = pd.read_csv(connections_file_name,dtype=str,na_filter=False)
    #     elif connections_file_name.endswith('.json'):
    #         # Load JSON file
    #         connections_df = pd.read_json(connections_file_name,dtype=str)
    #     else:
    #         # Raise an error for unsupported file formats
    #         raise ValueError("Unsupported file format. Please use a .csv or .json file.")
        
    #     if nodes_df is not None:
    #         for col in ['node_id', 'node_name', 'node_type', 'node_function_wrapper', 'node_imports']:
    #             if col not in nodes_df.columns:
    #                 raise ValueError(f"Missing '{col}' column in nodes_df")
    #         for _, node in nodes_df.iterrows():
    #             self.add_node(node)
        
    #     if connections_df is not None:
    #         for col in ['connection_id', 'from_node', 'to_node','mapping']:
    #             if col not in connections_df.columns:
    #                 raise ValueError(f"Missing '{col}' column in connections_df")
    #         for _, connection in connections_df.iterrows():
    #             self.add_connection(connection)
    def make(self):
        
        self._update_graph()
        # Update the flow graph and find the start nodes and flow sequence
        sorted_df=sort_df_based_on_sequence(self.connections_df,self.sequence)

        # Initialize separate lists for different parts of the program
        imports_lines = [self.py_dict["imports"]["main"]]
        functions_lines = []
        instantiations_lines = []
        set_inputs_lines = []
        connections_lines = []
        get_outputs_lines = []

        # Add imports, functions, and instantiations for each node in nodes_df
        for _, row in self.nodes_df.iterrows():
            node_name = row['node_name']
            
            # Add import lines
            if node_name in self.py_dict["imports"]:
                imports_lines.append(self.py_dict["imports"][node_name])
            
            # Add node function lines
            if node_name in self.py_dict["node_functions"]:
                functions_lines.append(self.py_dict["node_functions"][node_name])
            
            # Add node instantiation lines
            if node_name in self.py_dict["node_instantiations"]:
                instantiations_lines.append(self.py_dict["node_instantiations"][node_name])

        # Add Set inputs commands for each start node
        for start_node_name in self.start_nodes:
            if start_node_name in self.py_dict["set_inputs"]:
                set_inputs_lines.append(self.py_dict["set_inputs"][start_node_name])

        # Add node connections in the order specified by the sequence
        ordered_connection_ids=list(sorted_df['connection_id'])
        for connection_id in ordered_connection_ids:
            if connection_id in self.py_dict["node_connections"]:
                connections_lines.append(self.py_dict["node_connections"][connection_id])

        # Add get outputs commands for each connected node
        for connected_node in self.connected_nodes:
            connected_node_name = self.nodes_df['node_name'][self.nodes_df['node_id']==connected_node].values[0]
            if connected_node_name in self.py_dict["get_outputs"]:
                get_outputs_lines.append(self.py_dict["get_outputs"][connected_node_name])

        # Combine all parts into the final program
        program_lines = imports_lines + ['\n# Functions'] + functions_lines + ['\n# Instantiations'] + instantiations_lines + ['\n# Set inputs'] + set_inputs_lines + ['\n# Connections'] + connections_lines + ['\n# Get Outputs'] + get_outputs_lines
    
        # Combine all lines into a single program string
        self.main_py = '\n'.join(program_lines)
        
    def save(self,path):
        flow_name=self.flow_name.replace(" ", "_")
        flow_name=flow_name.lower()
        self.flow_file_name=flow_name+'.json'
        self.py_file_name = path + flow_name+'_program.py'
        nodes_df_json=self.nodes_df.to_json(orient='records')
        connection_df_json=self.connections_df.to_json(orient='records')
        flow_json_data={'nodes_df':json.loads(nodes_df_json), 'connections_df':json.loads(connection_df_json)}
        # Save the composed program to the specified file
        with open(self.py_file_name , 'w') as py_file:
            py_file.write(self.main_py)
        
        # Save the nodes and connections data to the specified file
        with open(self.flow_file_name , 'w') as json_file:
            json.dump(flow_json_data, json_file, indent=4)
                
    def run(self):
        if self.py_file_name == '':
            print('Please make the flow Python program by running flow.make(py_file_name)')
            return
        try:
            # Run the Python script using subprocess.run
            result = subprocess.run(['python', self.py_file_name], capture_output=True, text=True)
            
            # Print the output and error (if any)
            print("Output:\n", result.stdout)
            if result.stderr:
                print("Error:\n", result.stderr)
        except Exception as e:
            print(f"An error occurred while running the script: {e}")

