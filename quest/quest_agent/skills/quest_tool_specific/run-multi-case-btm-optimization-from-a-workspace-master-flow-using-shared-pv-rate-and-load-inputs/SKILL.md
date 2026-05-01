# Run multi-case BTM optimization from a Workspace master flow using shared PV, rate, and load inputs

## Task Description
Execute a QuESt BTM workflow from a Workspace master flow that passes common PV profile, tariff, and load file paths into a BTM subflow, runs multiple subcases with different ESS parameters, and saves per-case optimization result files.

## Pinned Context
The recorded flow is a master flow named Master_btm_flow_2026 that passes three file-path inputs into a Python node wrapping a BTM subflow. The subflow runs at least two subcases, using shared master-provided PV, tariff, and load inputs while varying ESS parameters. It uses BtmDMS, BtmOptimizerHandler, solver glpk, and writes CSV outputs under a workspace results directory.

## Flow Description
None

## Skill Type
quest_tool_specific

## Skill Level
Competent

## Recommended QuESt Tools
- btm
- data_manager

## Required Inputs
- pv_path (json file path): Path to a PV profile JSON file compatible with the BTM workflow.
- rate_path (json file path): Path to a utility tariff or rate structure JSON file used by the BTM optimizer.
- load_path (csv file path): Path to a load profile CSV file for the behind-the-meter customer.
- subcase_definitions (list of case records): One or more subcases specifying ESS parameters such as power rating, energy capacity, round-trip efficiency, solver, and output location.
- solver_name (string): Optimization solver name supported by the BTM environment, such as glpk.

## Workflow Build Plan
1. Load or create a master Workspace flow with data nodes for pv_path, rate_path, and load_path connected to a Python node that launches the BTM subflow.
2. Inside the BTM subflow, define data preparation nodes for load, PV, tariff, solver, results location, and ESS parameters.
3. Mark the PV, rate, and load path inputs in the subflow as inherited from the master flow so they can be overwritten at runtime.
4. Create one or more subcases in the subflow input table to vary ESS sizing inputs such as power rating and energy capacity while keeping shared file inputs common.
5. Build the BTM request by combining rate structure, load profile, PV profile, and ESS parameters.
6. Run the BTM optimizer handler with the selected solver and data manager context.
7. Collect solved optimization outputs and export each result set to CSV files in the configured results folder.
8. Return saved result locations and checkpoint file mappings for each subcase to the master flow.

## Data Preparation Notes
- Ensure the PV and tariff JSON files follow the schema expected by the QuESt BTM workflow.
- Ensure the load CSV has the time-series structure expected by the load profile node and downstream BTM optimizer.
- Use absolute paths when possible to avoid path resolution issues between master and subflow environments.
- Keep inherited master inputs blank in subcase definitions if they are intended to be supplied dynamically from the master flow.
- Verify the results directory exists or allow the workflow to create it before writing CSV outputs.
- Confirm the selected Python executable points to an environment with the QuESt BTM dependencies and solver installed.

## Validation Notes
- The master flow successfully injects pv_path, rate_path, and load_path into the subflow inputs marked as from master.
- Each configured subcase executes without runtime errors in the BTM environment.
- The optimizer returns solved operations and handler status for each subcase.
- A saved_location is returned for each subcase or a single location for single-case execution.
- Checkpoint mappings reference CSV files that exist on disk after execution.
- Result CSV filenames are sanitized and written to the expected output directory.
- Subcase parameter differences, such as power and energy values, are reflected in separate runs.

## Limitations
- This skill is specific to QuESt BTM workflows and is not a general Workspace pattern.
- It assumes the BTM Python environment and required modules such as BtmDMS and BtmOptimizerHandler are available.
- Solver availability is environment-dependent; glpk or another configured solver must be installed and callable.
- The workflow structure shown varies ESS parameters across subcases but does not demonstrate broader scenario management beyond the included inputs.
- Input schema validation for PV, tariff, and load files is not fully enforced by the recorded flow and may fail at runtime if formats are incompatible.
- The captured outputs focus on saved file locations and checkpoints rather than a normalized summary of economic metrics.

## Action Record
Action record file: `artifacts/action_record.json`

```text
Step | Flow                 | Flow Type   | Scope | Action          | Target               | Workspace Action                                                                                                                                                         | Details                                                                                                                                                                
-----+----------------------+-------------+-------+-----------------+----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1    | Master               | master-flow | skill | start_recording | Master               | {}                                                                                                                                                                       | {"flow_type": "master-flow"}                                                                                                                                           
2    | Master_btm_flow_2026 | master-flow | flow  | load_flow       | Master_btm_flow_2026 | {"flow_type": "master-flow", "path": "C:/work/quest210/snl-quest/quest/snl_libraries/workspace/examples/btm_subflow_input_mangement_example1.json", "type": "load_flow"} | {"flow_type": "master-flow", "path": "C:/work/quest210/snl-quest/quest/snl_libraries/workspace/examples/btm_subflow_input_mangement_example1.json", "subflow_count": 1}
3    | btm_flow_2026_new    | sub-flow    | flow  | add_input_case  | Subcase 1            | {"case_name": "Subcase 1", "type": "add_input_case"}                                                                                                                     | {"flow_type": "sub-flow"}                                                                                                                                              
```
