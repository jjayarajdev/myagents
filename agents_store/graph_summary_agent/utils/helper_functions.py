import yaml
import os
from pathlib import Path
from typing import Union, List, Dict
from pathlib import Path

#----------------------------------------------------------------------------------------------------------
# SECTION: Get output params from supervisor_functions.yaml if present, otherwise from the agent directory.
#---------------------------------------------------------------------------------------------------------

def get_output_params(agent_name):

    """
    Retrieves the output parameters for a given agent from a YAML configuration file.

    If the agent is not present in the `supervisor_functions.yaml` file, it will search for an agent directory with the given name and load the output parameters from the `config_file.yaml` file within that directory.

    Args:
        agent_name (str): The name of the agent for which to retrieve output parameters.

    Returns:
        dict or Exception: A dictionary containing the output parameters for the agent, or an Exception object if the agent is not found in either the YAML file or the agent directory.

    Raises:
        yaml.YAMLError: If there is an error parsing the YAML file.
        FileNotFoundError: If the agent directory or YAML file is not found.
    """

    functions_path = r'config_files\supervisor_functions.yaml'
    
    #loading of the YAML file
    with open(functions_path,encoding="utf-8") as file:
        try:
            yaml.preserve_quotes = True
            prompts = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            return exc
        output_params = None
        for func_type in prompts.keys():
            if prompts[func_type] is not None:
                for functions in prompts[func_type]:
                    for func in functions.keys():
                        if func == agent_name:
                            output_params = functions[agent_name]['output_params']

    # If the agent is not present 

    if output_params is None:
        directory = find_directory(Path.cwd(),agent_name)
        directory = r"{}".format(directory)
        functions_path = directory + r"\config_file.yaml"
        with open(functions_path,encoding="utf-8") as file:
            try:
                yaml.preserve_quotes = True
                prompts = yaml.safe_load(file)
        
            except yaml.YAMLError as exc:
                return exc
            print(prompts)
            for func_type in prompts.keys():
                for functions in prompts[func_type]:
                    for func in functions:
                        if func == agent_name:
                            output_params =functions[agent_name]['output_params']

                    
    return output_params

#-----------------------------------------------------------------------
# SECTION: To find the directory based on the directory name
#-----------------------------------------------------------------------

def find_directory(
    start_path:str,
    dir_name:str
    )->str:

    """
    Searches for a specified directory within a given starting directory and all its subdirectories.
    
    This function performs a recursive search starting from the provided path and looks
    for a directory with the exact name specified in 'dir_name'. It uses os.walk to traverse
    the directory tree and returns the full path of the first matching directory found.
    
    Parameters:
    -----------
    start_path : str
        The directory path where the search should begin. This path will be resolved
        to its absolute form before searching begins.
    
    dir_name : str
        The exact name of the directory to search for. The search is case-sensitive
        and matches only the directory name, not the full path.
    
    Returns:
    --------
    Path or None
        If the directory is found, returns a Path object representing the full path to
        the found directory. If no matching directory is found, returns None.
    
    Raises:
    -------
    Exception
        Any exceptions encountered during directory traversal will be caught, logged with
        a message, and then re-raised to the caller.
    """

    try:
        start_path = Path(start_path).resolve()
        
        # Search through all subdirectories
        for root, dirs, _ in os.walk(start_path):
            if dir_name in dirs:
                required_dir = Path(root) / dir_name
                print(f"Found required directory: {required_dir}")
                return required_dir
        
                
        return None
        
    except Exception as e:
        print(f"Error searching for supervisor directory: {str(e)}")
        raise

# -----------------------------------------------------------------------------
# SECTION: Load Start and Example Prompt YAML from File
# -----------------------------------------------------------------------------

def load_prompt_yaml(file_path: str) -> str:
    """
    Load Start and Example prompt text from YAML file.

    Args:
        file_path (str): The path to the file containing the prompt text in YAML format

    Returns:
        str: The content of the file as a string.
    """
    # Open the specified file in read mode with UTF-8 encoding and return the content
    
    buffer_prompts = []
    final_output = ""
    with open(file_path,encoding="utf-8") as file:
        try:
            yaml.preserve_quotes = True
            prompts = yaml.safe_load(file)

        except yaml.YAMLError as exc:
            return exc
        for key ,value in prompts.items():
            buffer_prompts.append(flatten_json({key:value}))
        

        for prompt in buffer_prompts:
            for key, values in prompt.items():
                if isinstance(values,str):
                    final_output += values + "\n"
                else:
                    if values != None:
                        for key, val in values.items():
                            final_output += val + "\n"

        return final_output
    
#------------------------------------------------------------------------------
# SECTION: flattens the JSON for getting data from nested JSON
#------------------------------------------------------------------------------
def flatten_json(
    prompts: dict,
    parent_key:str = ""
    ):

    """
    Recursively flattens a nested dictionary structure into a single-level dictionary.
    
    This function transforms nested dictionaries and lists into a flat dictionary with 
    concatenated keys representing the path to each value in the original structure.
    
    For dictionaries, keys are joined with underscores: {'a': {'b': 1}} becomes {'a_b': 1}
    
    For lists, items are enumerated starting from 1: {'a': [1, 2]} becomes {'a-1': 1, 'a-2': 2}
    
    When encountering a dictionary inside a list, the function recursively flattens it using
    the list item's enumerated key as a parent key.
    
    Parameters:
    -----------
    prompts : dict
        The nested dictionary to flatten. Can contain other dictionaries, lists, or primitive values.
    
    parent_key : str, optional (default: "")
        Used for recursion to keep track of the current key path. Should not be specified
        by the caller in most cases.
    
    Returns:
    --------
    dict
        A flattened dictionary where all keys are strings representing the path to each value
        in the original nested structure.
    
    """
    
    flattend_output = {}

    for key,value in prompts.items():

        new_key = f"{parent_key}_{key}" if parent_key else key

        if type(value) == dict:
            flattend_output.update(flatten_json(value,new_key))
        
        elif type(value) == list:
            for i,item in enumerate(value):
                flattend_output[f"{new_key}-{i+1}"] = item if not isinstance(item,dict) else flatten_json(item,f"{new_key}-{i+1}")

        else:
            flattend_output[new_key] = value

    return flattend_output

def load_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data
    except Exception as e:  
        print(f"Error loading YAML file: {e}")