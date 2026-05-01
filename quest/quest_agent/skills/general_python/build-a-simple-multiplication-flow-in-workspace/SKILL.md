# Build a simple multiplication flow in Workspace

## Task Description
Create a QuESt Workspace flow that documents a basic multiplication task, defines two numeric input data nodes, and prepares a Python node with two inputs and one output connected for multiplication logic.

## Pinned Context
No pinned context, project description, flow description, or attached files were provided. The recorded actions indicate a simple illustrative Workspace flow for multiplying two numbers using two data nodes and one Python node.

## Flow Description
None

## Skill Type
general_python

## Recommended QuESt Tools
- workspace

## Required Inputs
- input_a (number): First numeric value to be supplied through a Workspace data node variable named a.
- input_b (number): Second numeric value to be supplied through a Workspace data node variable named b.
- python_node_logic (notebook): Python notebook code for the Workspace Python node that multiplies inputs x and y and returns output.

## Workflow Build Plan
1. Start a master flow recording in Workspace.
2. Create a text node, rename it to Description, and add a short explanation of the flow purpose.
3. Create the first data node and configure a variable port named a.
4. Assign the first input value to a.
5. Create the second data node and configure a variable port named b.
6. Assign the second input value to b.
7. Create a Python node.
8. Configure the Python node with input ports x and y and an output port output.
9. Connect data node a to Python node input x.
10. Connect data node b to Python node input y.

## Data Preparation Notes
- Ensure both inputs are numeric or can be safely cast to numeric types in the Python node.
- Keep data node variable names aligned with the intended semantic inputs: a and b.
- Match connection mappings to Python node port names exactly: a -> x and b -> y.
- Implement multiplication logic inside the generated .ipynb associated with the Python node, since the recording only configured ports and connections.
- The recorded values 123 and 456 are example constants and can be replaced with other numeric inputs.

## Validation Notes
- A text node named Description exists and contains a short explanation of the flow.
- One data node exposes variable a and another exposes variable b.
- The Python node exposes inputs x and y and output output.
- Connections exist from data_node_1.a to py_node_1.x and from data_node_2.b to py_node_1.y.
- The Python notebook executes multiplication logic using x and y and produces output.
- Running the flow with valid numeric inputs returns the expected product.

## Limitations
- The recording does not include the actual Python code inside the notebook, only node creation and port configuration.
- No output display, result node, or downstream connection was recorded.
- The flow is a minimal example and does not include input validation, error handling, or type coercion.
- Node names are partly generic in the recording and may need refinement for reuse.
- This specification is based only on Workspace actions and does not use any QuESt domain-specific application tool.

## Action Record
Action record file: `artifacts/action_record.json`

```text
Step | Flow   | Flow Type   | Scope      | Action                 | Target                       | Workspace Action                                                                                                                                                      | Details                                                                                                                                
-----+--------+-------------+------------+------------------------+------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------
1    | Master | master-flow | skill      | start_recording        | Master                       | {}                                                                                                                                                                    | {"flow_type": "master-flow"}                                                                                                           
2    | Master | master-flow | node       | create_text_node       | TextNode1                    | {"count": 1, "name": "TextNode1", "node_type": "text", "type": "create_node"}                                                                                         | {"node_id": "0x1c812199010", "node_type": "text"}                                                                                      
3    | Master | master-flow | node       | rename_node            | Description                  | {"new_name": "Description", "type": "rename_selected_node"}                                                                                                           | {"node_type": "back_node", "old_name": "TextNode1"}                                                                                    
4    | Master | master-flow | node       | update_text_node       | Description                  | {"text": "This is a flow to multiply 2 numbers", "type": "update_selected_text_node"}                                                                                 | {"text": "This is a flow to multiply 2 numbers"}                                                                                       
5    | Master | master-flow | node       | create_data_node       | data_node_1                  | {"count": 1, "name": "data_node_1", "node_type": "data", "type": "create_node"}                                                                                       | {"node_id": "0x1c81e587750", "node_type": "data"}                                                                                      
6    | Master | master-flow | node       | update_data_node_ports | data_node_1                  | {"type": "update_data_node_ports", "variable_name": "a"}                                                                                                              | {"variable_name": "a"}                                                                                                                 
7    | Master | master-flow | node       | update_node_value      | data_node_1                  | {"is_path": false, "type": "update_selected_data_node_value", "value": "123", "value_display": true, "variable_name": "a"}                                            | {"is_path": false, "value": "123", "value_display": true, "variable_name": "a"}                                                        
8    | Master | master-flow | node       | update_node_value      | data_node_1                  | {"is_path": false, "type": "update_selected_data_node_value", "value": "123", "value_display": true, "variable_name": "a"}                                            | {"is_path": false, "value": "123", "value_display": true, "variable_name": "a"}                                                        
9    | Master | master-flow | node       | create_data_node       | data_node_2                  | {"count": 1, "name": "data_node_2", "node_type": "data", "type": "create_node"}                                                                                       | {"node_id": "0x1c81e587610", "node_type": "data"}                                                                                      
10   | Master | master-flow | node       | update_data_node_ports | data_node_2                  | {"type": "update_data_node_ports", "variable_name": "b"}                                                                                                              | {"variable_name": "b"}                                                                                                                 
11   | Master | master-flow | node       | update_node_value      | data_node_2                  | {"is_path": false, "type": "update_selected_data_node_value", "value": "456", "value_display": true, "variable_name": "b"}                                            | {"is_path": false, "value": "456", "value_display": true, "variable_name": "b"}                                                        
12   | Master | master-flow | node       | update_node_value      | data_node_2                  | {"is_path": false, "type": "update_selected_data_node_value", "value": "456", "value_display": true, "variable_name": "b"}                                            | {"is_path": false, "value": "456", "value_display": true, "variable_name": "b"}                                                        
13   | Master | master-flow | node       | create_py_node         | py_node_1                    | {"count": 1, "name": "py_node_1", "node_type": "py", "type": "create_node"}                                                                                           | {"node_id": "0x1c81e637820", "node_type": "py", "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x1c81e637820.ipynb"}
14   | Master | master-flow | node       | update_py_node_ports   | py_node_1                    | {"inputs": ["x", "y"], "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x1c81e637820.ipynb", "outputs": ["output"], "type": "update_py_node_ports"} | {"inputs": ["x", "y"], "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x1c81e637820.ipynb", "outputs": ["output"]}  
15   | Master | master-flow | connection | connect_nodes          | data_node_1.a -> py_node_1.x | {"mapping": {"a": "x"}, "source_node": "data_node_1", "target_node": "py_node_1", "type": "connect_nodes"}                                                            | {"source_node": "data_node_1", "source_port": "a", "target_node": "py_node_1", "target_port": "x"}                                     
16   | Master | master-flow | connection | connect_nodes          | data_node_2.b -> py_node_1.y | {"mapping": {"b": "y"}, "source_node": "data_node_2", "target_node": "py_node_1", "type": "connect_nodes"}                                                            | {"source_node": "data_node_2", "source_port": "b", "target_node": "py_node_1", "target_port": "y"}                                     
```
