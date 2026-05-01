# Build a simple Workspace flow to add two numbers

## Task Description
Create and save a QuESt Workspace flow that documents a simple addition task, defines two numeric data inputs, connects them to a Python node configured to output their sum, and saves the flow as a reusable JSON workflow file.

## Pinned Context
No pinned context was provided. The recorded workflow shows a Workspace-only example flow named Master that demonstrates adding two numbers using two data nodes, one Python node, and one descriptive text node, then saving the flow to add_2num.json.

## Flow Description
None

## Skill Type
general_python

## Recommended QuESt Tools
- workspace

## Required Inputs
- flow_save_path (string): Destination path and filename for the saved Workspace flow JSON.
- first_number (number): Optional sample value for the first input data node.
- second_number (number): Optional sample value for the second input data node.
- description_text (string): Optional explanatory text for the Description node.

## Workflow Build Plan
1. Start a master flow recording in Workspace.
2. Create a text node, rename it to Description, and add explanatory text stating the flow adds two numbers.
3. Create two data nodes to represent the numeric inputs.
4. Rename the first data node to number1, set its variable name to a, and assign a sample value of 10.
5. Rename the second data node to number2 and set its variable name to b.
6. Create a Python node, configure its ports with inputs x and y and output output, then rename it to sum.
7. Connect number1.a to sum.x.
8. Connect number2.b to sum.y.
9. Save the master flow as a JSON file for reuse.

## Data Preparation Notes
- No external dataset is required.
- Choose numeric sample values for the two data nodes if you want the flow to include defaults.
- Ensure the save destination is a valid .json path accessible from Workspace.
- The Python node must be configured with ports before wiring connections.

## Validation Notes
- A text node named Description exists and contains explanatory text about adding two numbers.
- Two data nodes exist, named number1 and number2.
- The number1 data node exposes variable a.
- The number2 data node exposes variable b.
- A Python node named sum exists with inputs x and y and output output.
- There is a connection from number1.a to sum.x.
- There is a connection from number2.b to sum.y.
- The flow is successfully saved as a .json file.

## Limitations
- The recording configures Python node ports but does not include the internal Python code that performs the addition.
- The second data node value was not explicitly set in the recording.
- This skill describes Workspace flow construction only and does not guarantee execution behavior without implementing the Python node logic.
- The example is limited to a simple two-input addition pattern and may need adaptation for broader arithmetic workflows.

## Action Record
Action record file: `artifacts/action_record.json`

```text
Step | Flow   | Flow Type   | Scope      | Action                 | Target             | Workspace Action                                                                                                                                                      | Details                                                                                                                                       
-----+--------+-------------+------------+------------------------+--------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------
1    | Master | master-flow | skill      | start_recording        | Master             | {}                                                                                                                                                                    | {"flow_type": "master-flow"}                                                                                                                  
2    | Master | master-flow | node       | create_text_node       | TextNode1          | {"count": 1, "name": "TextNode1", "node_type": "text", "type": "create_node"}                                                                                         | {"node_id": "0x1c13b6f5010", "node_type": "text"}                                                                                             
3    | Master | master-flow | node       | rename_node            | Description        | {"new_name": "Description", "type": "rename_selected_node"}                                                                                                           | {"node_type": "back_node", "old_name": "TextNode1"}                                                                                           
4    | Master | master-flow | node       | update_text_node       | Description        | {"text": "This flow is for adding two numbers", "type": "update_selected_text_node"}                                                                                  | {"text": "This flow is for adding two numbers"}                                                                                               
5    | Master | master-flow | node       | create_data_node       | data_node_1        | {"count": 1, "name": "data_node_1", "node_type": "data", "type": "create_node"}                                                                                       | {"node_id": "0x1c13b427c50", "node_type": "data"}                                                                                             
6    | Master | master-flow | node       | create_data_node       | data_node_2        | {"count": 1, "name": "data_node_2", "node_type": "data", "type": "create_node"}                                                                                       | {"node_id": "0x1c13b427250", "node_type": "data"}                                                                                             
7    | Master | master-flow | node       | create_py_node         | py_node_1          | {"count": 1, "name": "py_node_1", "node_type": "py", "type": "create_node"}                                                                                           | {"node_id": "0x1c10fa6f490", "node_type": "py", "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x1c10fa6f490.ipynb"}       
8    | Master | master-flow | node       | rename_node            | number1            | {"new_name": "number1", "type": "rename_selected_node"}                                                                                                               | {"node_type": "data_node", "old_name": "data_node_1"}                                                                                         
9    | Master | master-flow | node       | update_data_node_ports | number1            | {"type": "update_data_node_ports", "variable_name": "a"}                                                                                                              | {"variable_name": "a"}                                                                                                                        
10   | Master | master-flow | node       | update_node_value      | number1            | {"is_path": false, "type": "update_selected_data_node_value", "value": "10", "value_display": true, "variable_name": "a"}                                             | {"is_path": false, "value": "10", "value_display": true, "variable_name": "a"}                                                                
11   | Master | master-flow | node       | update_node_value      | number1            | {"is_path": false, "type": "update_selected_data_node_value", "value": "10", "value_display": true, "variable_name": "a"}                                             | {"is_path": false, "value": "10", "value_display": true, "variable_name": "a"}                                                                
12   | Master | master-flow | node       | rename_node            | number2            | {"new_name": "number2", "type": "rename_selected_node"}                                                                                                               | {"node_type": "data_node", "old_name": "data_node_2"}                                                                                         
13   | Master | master-flow | node       | update_data_node_ports | number2            | {"type": "update_data_node_ports", "variable_name": "b"}                                                                                                              | {"variable_name": "b"}                                                                                                                        
14   | Master | master-flow | node       | update_py_node_ports   | py_node_1          | {"inputs": ["x", "y"], "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x1c10fa6f490.ipynb", "outputs": ["output"], "type": "update_py_node_ports"} | {"inputs": ["x", "y"], "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x1c10fa6f490.ipynb", "outputs": ["output"]}         
15   | Master | master-flow | node       | rename_node            | sum                | {"new_name": "sum", "type": "rename_selected_node"}                                                                                                                   | {"node_type": "python_node", "old_name": "py_node_1"}                                                                                         
16   | Master | master-flow | connection | connect_nodes          | number1.a -> sum.x | {"mapping": {"a": "x"}, "source_node": "number1", "target_node": "sum", "type": "connect_nodes"}                                                                      | {"source_node": "number1", "source_port": "a", "target_node": "sum", "target_port": "x"}                                                      
17   | Master | master-flow | connection | connect_nodes          | number2.b -> sum.y | {"mapping": {"b": "y"}, "source_node": "number2", "target_node": "sum", "type": "connect_nodes"}                                                                      | {"source_node": "number2", "source_port": "b", "target_node": "sum", "target_port": "y"}                                                      
18   | Master | master-flow | flow       | save_flow_as           | Master             | {"path": "C:/work/quest210/snl-quest/quest/snl_libraries/workspace/examples/add_2num.json", "save_mode": "master", "type": "save_flow_as"}                            | {"flow_type": "master-flow", "path": "C:/work/quest210/snl-quest/quest/snl_libraries/workspace/examples/add_2num.json", "save_mode": "master"}
```
