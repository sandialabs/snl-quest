# Run a BTM optimization subflow from master-provided PV, tariff, and load paths

## Task Description
Behind-the-meter energy storage optimization workflow that passes master-flow file path inputs for PV, tariff/rate, and load data into a BTM subflow, runs the subflow, and returns saved result locations and checkpoints.

## Pinned Context
Subflow name: btm_flow_2026_new. The workflow uses BTM-specific classes BtmDMS and BtmOptimizerHandler in a BTM app environment. Master-provided inputs are the PV path, rate path, and load path. Default local inputs include data_path='/data/', power=100, energy=400, rte=0.88, solver_name='glpk', and results directory './results/workspace'. The rate file is expected to be JSON, and solved outputs are exported as CSV files.

## Flow Description
None

## Skill Type
quest_tool_specific

## Recommended QuESt Tools
- btm
- data_manager

## Required Inputs
- pv_path (path): Path to the PV profile input file passed from the master flow.
- rate_path (path): Path to the tariff or rate structure JSON file passed from the master flow.
- load_path (path): Path to the load profile input file passed from the master flow.
- data_path (path): Home/data directory used to initialize the BTM data manager and persist intermediate data.
- power (number): ESS power rating used in the optimization parameter set.
- energy (number): ESS energy capacity used in the optimization parameter set.
- rte (number): Round-trip efficiency for the ESS parameter set.
- solver_name (string): Optimization solver name supported by the BTM environment, such as glpk.
- results_location (path): Directory where solved operation result CSV files will be written.

## Workflow Build Plan
1. Accept master-flow inputs for PV path, rate/tariff path, and load path.
2. Create a BTM data manager rooted at the configured data directory.
3. Wrap the load file path into a load profile descriptor.
4. Wrap the PV file path into a PV profile descriptor.
5. Load the tariff/rate JSON file into a rate structure object.
6. Build ESS parameter settings from power, energy, and round-trip efficiency inputs.
7. Assemble a BTM optimization request from rate structure, PV profile, load profile, and ESS parameters.
8. Run the BTM optimizer handler with the selected solver and data manager.
9. Save each solved operation result as a CSV in the configured results directory.
10. Return the saved results directory and a checkpoint mapping of generated files.

## Data Preparation Notes
- Ensure the tariff/rate file is valid JSON and matches the structure expected by the BTM optimizer.
- Provide valid filesystem paths for PV, load, and rate inputs; these are passed through from the master flow and not hardcoded in the subflow.
- The load and PV nodes in this workflow create lightweight descriptors containing a name and path, so downstream BTM logic must be able to resolve those referenced files.
- ESS parameters are packaged as a single-item list containing Power_rating, Energy_capacity, Round_trip_efficiency, Transformer_rating, and state-of-charge bounds.
- Confirm the results directory is writable; the workflow creates it if it does not exist.
- Use filenames for solved operations that can be safely sanitized into CSV filenames, since non-word characters are removed before saving.

## Validation Notes
- The subflow receives non-empty master inputs for pv_path, rate_path, and load_path.
- The rate JSON loads successfully without parse errors.
- The BTM data manager initializes successfully using the configured data_path.
- The optimizer handler runs without solver or environment errors and returns solved operations plus handler status.
- At least one result CSV is written to the configured results directory when solved operations are returned.
- The workflow returns both saved_location and a checkpoints mapping keyed by generated file paths.
- Saved CSV filenames are sanitized and valid on the target filesystem.

## Limitations
- This skill is specific to the QuESt BTM tool and depends on BTM classes and environment availability.
- The workflow assumes the tariff input is JSON; other tariff formats require preprocessing.
- The PV and load preparation steps only wrap file paths into descriptors and do not validate file contents themselves.
- Default ESS settings include fixed transformer rating and state-of-charge bounds; these may not suit all projects.
- Solver support is limited to solvers installed and configured in the BTM environment.
- The recorded workflow exposes saved result locations and checkpoints but does not include downstream analysis or visualization of the optimization outputs.

## Action Record
Action record file: `artifacts/action_record.json`

```text
Step | Flow                 | Flow Type   | Scope | Action          | Target               | Workspace Action                                                                                                                                                         | Details                                                                                                                                                                
-----+----------------------+-------------+-------+-----------------+----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1    | Master_btm_flow_2026 | master-flow | skill | start_recording | Master_btm_flow_2026 | {}                                                                                                                                                                       | {"flow_type": "master-flow"}                                                                                                                                           
2    | Master_btm_flow_2026 | master-flow | flow  | load_flow       | Master_btm_flow_2026 | {"flow_type": "master-flow", "path": "C:/work/quest210/snl-quest/quest/snl_libraries/workspace/examples/btm_subflow_input_mangement_example1.json", "type": "load_flow"} | {"flow_type": "master-flow", "path": "C:/work/quest210/snl-quest/quest/snl_libraries/workspace/examples/btm_subflow_input_mangement_example1.json", "subflow_count": 1}
```
