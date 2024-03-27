import inspect

class python_node:
    def __init__(self, *, node_name=None, function=None):
        self.node_name = node_name
        self.function = function
        self.input_names = list(inspect.signature(function).parameters.keys()) if function else []
        self.output_names = []
        self.input_values = {}
        self.output_values ={}
        self.from_node_list = []
        self.to_node_list=[]
    
    def set_inputs(self, **kwargs):
        """Set the input values by providing keyword arguments."""
        if not self.function:
            raise ValueError("Function not set for this node.")
        for key, value in kwargs.items():
            if key in self.input_names:
                self.input_values[key] = value
            else:
                raise ValueError(f"{key} is not a valid input for the function {self.function.__name__}")

    def get_outputs(self):
        """Executes the function with the provided inputs and updates outputs."""
        if not self.function:
            raise ValueError("Function not set for this node.")
        if not all(input_name in self.input_values for input_name in self.input_names):
            missing_inputs = [input_name for input_name in self.input_names if input_name not in self.input_values]
            raise ValueError(f"Missing inputs: {missing_inputs}")

        result = self.function(**self.input_values)

        if isinstance(result, dict):
            self.output_values = result
        else:
            self.output_values = {"outputs":result}
        self.output_names = list(self.output_values.keys())
        return self.output_values
    
    def connect_to(self, to_node_list, mapping):
        """
        Connects the current node to another node by mapping outputs to inputs.
        
        Parameters:
        - to_node_list: List of the nodes to connect to.
        - mapping: List of dictionaries mapping output names from this node to input names of the to_node.
        """
        for to_node in to_node_list:
            if not isinstance(to_node, python_node):
                raise ValueError("to_node must be an instance of pynode or its subclasses.")
        for map in mapping:
            if not isinstance(map, dict):
                raise ValueError("Mapping must be a dictionary.")
        
        # Get the current node's outputs
        current_outputs = self.get_outputs()
        for i in range(len(to_node_list)):
            # Prepare the inputs for the to_node based on the mapping
            to_node = to_node_list[i]
            to_node_inputs = {}
            for out_key, in_key in mapping[i].items():
                if out_key in current_outputs:
                    to_node_inputs[in_key] = current_outputs[out_key]
                else:
                    raise ValueError(f"Output {out_key} not found in the current node's outputs.")
            
            # Set the mapped inputs to the to_node
            to_node.set_inputs(**to_node_inputs)
            if to_node not in self.to_node_list:
                self.to_node_list.append(to_node)
                
class data_node(python_node):
    def __init__(self, *, node_name=None):
        super().__init__(node_name=node_name, function=self.fixed_function)
        # Instead of relying on the function's signature, allow any inputs.
        self.inputs = None  # Indicate that any input is acceptable.

    def fixed_function(self, **kwargs):
        return kwargs

    def set_inputs(self, **kwargs):
        """Set the input values for any given keyword arguments."""
        self.input_values = kwargs  # Directly set input values without validation.

    def get_outputs(self):
        """Executes the function with the provided inputs and updates outputs."""
        result = self.function(**self.input_values)

        if isinstance(result, dict):
            self.output_values = result
        else:
            # Assume the function returns a single output
            self.output_values = {"outputs": result}
        self.output_names = list(self.output_values.keys())
        return self.output_values

