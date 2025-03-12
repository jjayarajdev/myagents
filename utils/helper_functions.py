"""
Module Name: helper_functions.py

Description:
This module contains utility functions for loading prompt text from a file and 
loading email addresses into a list. These functions are designed to be used 
as helpers for reading and processing text data in various formats.

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
import yaml
import os
from pathlib import Path
from typing import Union, List, Dict
from pathlib import Path

#----------------------------------------------------------------------------------------------------------
# SECTION: Get output params from supervisor_functions.yaml if present, otherwise from the agent directory.
#---------------------------------------------------------------------------------------------------------

def get_output_params(agent_name,user):

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
    
    functions_path = os.path.join(os.getcwd(),'user_config_files', user, 'supervisor_functions.yaml')
    output_params = None
    if Path(functions_path).exists():
       #loading of the YAML file
        with open(functions_path,encoding="utf-8") as file:
            try:
                yaml.preserve_quotes = True
                prompts = yaml.safe_load(file)
            
            except yaml.YAMLError as exc:
                return exc
        for func_type in prompts.keys():
            if prompts[func_type] is not None:
                for functions in prompts[func_type]:
                    for func in functions.keys():
                        if func == agent_name:
                            output_params = functions[agent_name]['output_params']
                        
    
    # print(output_params)
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
            for func_type in prompts.keys():
                for functions in prompts[func_type]:
                    for func in functions.keys():
                        if func == agent_name:
                            output_params =functions[agent_name]['output_params']

                    
    return output_params

def get_required_agents(user):
    user_dir_path = os.path.join(os.getcwd(),'user_config_files', user, 'agents_required.yaml')
    if Path(user_dir_path).exists():
        path = user_dir_path
        print(f"Loading agents_required file from user_config_files")
    else:
        path = os.path.join(os.getcwd(),'config_files','agents_required.yaml')
        print(f"Loading agents_required file from agent_store")
    with open(path,encoding="utf-8") as file:
        try:
            yaml.preserve_quotes = True
            prompts = yaml.safe_load(file)
        
        except yaml.YAMLError as exc:
            return exc
    return prompts['agents_required']

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
            if value != None:
                flattend_output[new_key] = "**"+ key +"**" + " : " +value
            else:
                flattend_output[new_key] = ""
    return flattend_output

 
# -----------------------------------------------------------------------------
# SECTION: Compute Total Length of Output
# -----------------------------------------------------------------------------
 
def compute_total_length(output: Union[str, List[Dict]]) -> int:
    """
    Compute the total character length across the task output, which can either 
    be a string or a list of dictionaries containing string values.
 
    Args:
        output (Union[str, List[Dict]]): The task output to compute the length for. 
            It can be either a direct string or a list of dictionaries.
 
    Returns:
        int: The total character length of the task output.
    """
    total_length = 0
 
    if isinstance(output, str):
        # If the output is a string, return its length directly
        total_length = len(output)
    elif isinstance(output, list):
        # If the output is a list of dictionaries, sum the length of all string values
        for item in output:
            for value in item.values():
                total_length += len(value)
 
    return total_length

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
    
        
#---------------------------------------------------------------------------------------------
# SECTION: loads agents that are required for supervisor agent from supervisor_functions.yaml
#---------------------------------------------------------------------------------------------
    
def load_functions_prompt(required_agents) -> str:

    """
    Loads the functions prompts for a list of required agents from a YAML configuration file.

    Args:
        required_agents (list): A list of agent names for which to load the functions prompts.

    Returns:
        str: A string containing the concatenated functions prompts for the required agents.

    Raises:
        yaml.YAMLError: If there is an error parsing the YAML file.
    """

    description = ""
    parameters = ""
    final_prompt = ""
    functions_path = r'config_files\supervisor_functions.yaml'
    enabled_agents = [agent['name'] for agent in required_agents if agent['enabled'] == True]
    print(enabled_agents)
    #loading of the YAML file
    with open(functions_path, encoding="utf-8") as file:
        try:
            yaml.preserve_quotes = True
            prompts = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            return exc
    functions = prompts['functions']
    indices = []
    agents = []
    for func in functions:
        key = func.keys()
        agents.append(list(key)[0])

    for agent in enabled_agents:
        indices.append((agent,agents.index(agent)))
    

    for agent_name,idx in indices:
        description = functions[idx][agent_name]['description'] 
        parameters = functions[idx][agent_name]['parameters']
        final_prompt += description  +\
                    parameters + "\n"

    return final_prompt

def load_explicit_functions():

    functions_path = r'config_files\supervisor_functions.yaml'
    
    with open(functions_path,encoding="utf-8") as file:
        try:
            yaml.preserve_quotes = True
            prompts = yaml.safe_load(file)
        
        except yaml.YAMLError as exc:
            return exc
    explicit_functions = prompts['explicit_functions']
        
    return explicit_functions



# -----------------------------------------------------------------------------
# SECTION: Load Prompt Text from File
# -----------------------------------------------------------------------------

def load_prompt(file_path: str) -> str:
    """
    Load prompt text from a file.

    Args:
        file_path (str): The path to the file containing the prompt text.

    Returns:
        str: The content of the file as a string.
    """
    # Open the specified file in read mode with UTF-8 encoding and return the content
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# -----------------------------------------------------------------------------
# SECTION: Dynamic Loading of Example Prompts based on Snowflake Table Names
# -----------------------------------------------------------------------------

def load_dynamic_example_prompt(table_names):
    """
    Load and concatenate example prompts dynamically based on table names.

    Args:
        table_names (list): List of table names.

    Returns:
        str: Concatenated example prompt text.
    """
    example_texts = []
    for table_name in table_names:
        prompt_file = f"prompts/snowflake/snowflake_nidhi_tables/{table_name}.txt"  # Construct file path
        try:
            example_text = load_prompt(prompt_file)  # Load prompt from file
            example_texts.append(example_text)
        except FileNotFoundError:
            print(f"Warning: Prompt file {prompt_file} not found.")
    
    # Concatenate all example texts into a single string
    return "\n".join(example_texts)


def load_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data
    except Exception as e:  
        print(f"Error loading YAML file: {e}")
# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------