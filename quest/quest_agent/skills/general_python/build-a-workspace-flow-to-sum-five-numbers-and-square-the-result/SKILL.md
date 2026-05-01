# Build a Workspace flow to sum five numbers and square the result

## Task Description
Build a simple QuESt Workspace workflow that takes five numeric inputs, computes their sum, and squares that sum.

## Pinned Context
The recorded master flow already implements the requested logic in Workspace. It contains a description node, five data nodes named number1 through number5 mapped to variables a through e, and a Python node named sum_and_square with wrapper function sum_and_square_function(a, b, c, d, e). The function returns outputs sum and squared_result. Current example inputs are 1, 2, 3, 4, and 5.

## Flow Description
The current master flow already implements the requested logic. It contains a description/backdrop node, five data nodes named number1 through number5 with outputs a, b, c, d, and e, and one Python node named sum_and_square. Each data node is connected to the matching input port on the Python node. The Python node wrapper is defined as sum_and_square_function(a, b, c, d, e), computes total = a + b + c + d + e, computes squared = total ** 2, and returns a dictionary with output keys 'sum' and 'squared_result'. Input values are currently 1, 2, 3, 4, and 5.

## Skill Type
general_python

## Skill Level
Competent

## Recommended QuESt Tools
- workspace

## Required Inputs
- number1 (number): First numeric input mapped to variable a.
- number2 (number): Second numeric input mapped to variable b.
- number3 (number): Third numeric input mapped to variable c.
- number4 (number): Fourth numeric input mapped to variable d.
- number5 (number): Fifth numeric input mapped to variable e.

## Workflow Build Plan
1. Create a description or backdrop node documenting that the flow adds five numbers and squares the sum.
2. Create five data nodes and configure their output variable names as a, b, c, d, and e.
3. Assign numeric values to the five data nodes.
4. Create one Python node named sum_and_square.
5. Configure the Python node with input ports a, b, c, d, e and output ports sum and squared_result.
6. Implement the wrapper function sum_and_square_function(a, b, c, d, e) so it computes total = a + b + c + d + e, squared = total ** 2, and returns {'sum': total, 'squared_result': squared}.
7. Connect each data node output to the matching Python node input port.
8. Run or inspect the flow outputs using a known example such as 1, 2, 3, 4, and 5 to confirm sum = 15 and squared_result = 225.

## Data Preparation Notes
- Ensure all five inputs are numeric values compatible with Python addition and exponentiation.
- Keep data node output variable names aligned exactly with the Python function arguments: a, b, c, d, e.
- Keep Python node output names aligned with the returned dictionary keys: sum and squared_result.
- No external dataset or domain-specific preprocessing is required for this workflow.

## Validation Notes
- The flow contains exactly five input data nodes feeding one Python node.
- Each connection maps the correct source variable to the matching Python input port.
- The Python wrapper uses one top-level function and returns a dictionary with keys sum and squared_result.
- For inputs 1, 2, 3, 4, and 5, the outputs evaluate to sum = 15 and squared_result = 225.
- The flow remains acyclic and free of broken port mappings.

## Limitations
- This skill covers a simple arithmetic pattern only and does not use any domain-specific QuESt analysis tool.
- The workflow assumes exactly five inputs unless the Python node and connected data nodes are modified.
- No explicit type checking, error handling, or input validation is included beyond relying on numeric-compatible inputs.
- Outputs are only available inside Workspace unless additional nodes are added for export or display.

## Action Record
Action record file: `artifacts/action_record.json`

```text
Step | Flow   | Flow Type   | Scope      | Action                 | Target                        | Workspace Action                                                                                                                                                                                         | Details                                                                                                                                                                 
-----+--------+-------------+------------+------------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1    | Master | master-flow | skill      | start_recording        | Master                        | {}                                                                                                                                                                                                       | {"flow_type": "master-flow"}                                                                                                                                            
2    | Master | master-flow | node       | create_text_node       | TextNode1                     | {"count": 1, "name": "TextNode1", "node_type": "text", "type": "create_node"}                                                                                                                            | {"node_id": "0x26f2c18ee40", "node_type": "text"}                                                                                                                       
3    | Master | master-flow | node       | create_data_node       | data_node_1                   | {"count": 1, "name": "data_node_1", "node_type": "data", "type": "create_node"}                                                                                                                          | {"node_id": "0x26f2ddc6e90", "node_type": "data"}                                                                                                                       
4    | Master | master-flow | node       | update_data_node_ports | number1                       | {"type": "update_data_node_ports", "variable_name": "a"}                                                                                                                                                 | {"variable_name": "a"}                                                                                                                                                  
5    | Master | master-flow | node       | create_data_node       | data_node_2                   | {"count": 1, "name": "data_node_2", "node_type": "data", "type": "create_node"}                                                                                                                          | {"node_id": "0x26f2ddc7110", "node_type": "data"}                                                                                                                       
6    | Master | master-flow | node       | update_data_node_ports | number2                       | {"type": "update_data_node_ports", "variable_name": "b"}                                                                                                                                                 | {"variable_name": "b"}                                                                                                                                                  
7    | Master | master-flow | node       | create_data_node       | data_node_3                   | {"count": 1, "name": "data_node_3", "node_type": "data", "type": "create_node"}                                                                                                                          | {"node_id": "0x26f05b13950", "node_type": "data"}                                                                                                                       
8    | Master | master-flow | node       | update_data_node_ports | number3                       | {"type": "update_data_node_ports", "variable_name": "c"}                                                                                                                                                 | {"variable_name": "c"}                                                                                                                                                  
9    | Master | master-flow | node       | create_data_node       | data_node_4                   | {"count": 1, "name": "data_node_4", "node_type": "data", "type": "create_node"}                                                                                                                          | {"node_id": "0x26f2c346520", "node_type": "data"}                                                                                                                       
10   | Master | master-flow | node       | update_data_node_ports | number4                       | {"type": "update_data_node_ports", "variable_name": "d"}                                                                                                                                                 | {"variable_name": "d"}                                                                                                                                                  
11   | Master | master-flow | node       | create_data_node       | data_node_5                   | {"count": 1, "name": "data_node_5", "node_type": "data", "type": "create_node"}                                                                                                                          | {"node_id": "0x26f29d81350", "node_type": "data"}                                                                                                                       
12   | Master | master-flow | node       | update_data_node_ports | number5                       | {"type": "update_data_node_ports", "variable_name": "e"}                                                                                                                                                 | {"variable_name": "e"}                                                                                                                                                  
13   | Master | master-flow | node       | create_py_node         | py_node_1                     | {"count": 1, "name": "py_node_1", "node_type": "py", "type": "create_node"}                                                                                                                              | {"node_id": "0x26f29d810f0", "node_type": "py", "notebook_path": "c:/work/quest210-py313/node_notebooks/py_node_1_0x26f29d810f0.ipynb"}                                 
14   | Master | master-flow | node       | update_py_node_ports   | sum_and_square                | {"inputs": ["a", "b", "c", "d", "e"], "notebook_path": "c:/work/quest210-py313/node_notebooks/sum_and_square_0x26f29d810f0.ipynb", "outputs": ["sum", "squared_result"], "type": "update_py_node_ports"} | {"inputs": ["a", "b", "c", "d", "e"], "notebook_path": "c:/work/quest210-py313/node_notebooks/sum_and_square_0x26f29d810f0.ipynb", "outputs": ["sum", "squared_result"]}
15   | Master | master-flow | connection | connect_nodes          | number1.a -> sum_and_square.a | {"mapping": {"a": "a"}, "source_node": "number1", "target_node": "sum_and_square", "type": "connect_nodes"}                                                                                              | {"source_node": "number1", "source_port": "a", "target_node": "sum_and_square", "target_port": "a"}                                                                     
16   | Master | master-flow | connection | connect_nodes          | number2.b -> sum_and_square.b | {"mapping": {"b": "b"}, "source_node": "number2", "target_node": "sum_and_square", "type": "connect_nodes"}                                                                                              | {"source_node": "number2", "source_port": "b", "target_node": "sum_and_square", "target_port": "b"}                                                                     
17   | Master | master-flow | connection | connect_nodes          | number3.c -> sum_and_square.c | {"mapping": {"c": "c"}, "source_node": "number3", "target_node": "sum_and_square", "type": "connect_nodes"}                                                                                              | {"source_node": "number3", "source_port": "c", "target_node": "sum_and_square", "target_port": "c"}                                                                     
18   | Master | master-flow | connection | connect_nodes          | number4.d -> sum_and_square.d | {"mapping": {"d": "d"}, "source_node": "number4", "target_node": "sum_and_square", "type": "connect_nodes"}                                                                                              | {"source_node": "number4", "source_port": "d", "target_node": "sum_and_square", "target_port": "d"}                                                                     
19   | Master | master-flow | connection | connect_nodes          | number5.e -> sum_and_square.e | {"mapping": {"e": "e"}, "source_node": "number5", "target_node": "sum_and_square", "type": "connect_nodes"}                                                                                              | {"source_node": "number5", "source_port": "e", "target_node": "sum_and_square", "target_port": "e"}                                                                     
```
