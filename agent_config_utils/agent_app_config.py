
from pathlib import Path
import yaml
import json
import os
agents_list_path= os.path.join(os.getcwd(),r'agent_config_utils\agents_list.yaml')

import yaml

def str_presenter(dumper, data):
    # Check if the string is multiline
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    # For single line strings, use no quotes when possible
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
 
# Register the custom representer
yaml.add_representer(str, str_presenter)
    





def load_yaml(file_path):
    """Load data from a YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def load_config(file_path):
    """Load the configuration from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)
    



def generate_yaml_db_query_agent(data,user):
    for table in data['db_query_agent']['table']:
        # user ='user1'
        table_name = table['name']
        # table_directory = r'C:\Users\NCheethir\testing_folder\agents_store\db_agent\user_configurable_files\db_agent_prompts'
        table_directory=os.path.join(os.getcwd(),'user_config_files', user, 'db_agent_prompts')
        table_directory = os.path.join(table_directory, table_name)
        os.makedirs(table_directory, exist_ok=True)
        system_data = {
            "system": table['system']
        }
        with open(os.path.join(table_directory, "system_prompt.yaml"), 'w') as file:
            yaml.dump(system_data, file, default_flow_style=False)
        print(f"Generated: {table_directory}/system_prompt.yaml")
    
        schema_data = {
            "schema": table['schema']
        }
        with open(os.path.join(table_directory, "schema_prompt.yaml"), 'w') as file:
            yaml.dump(schema_data, file, default_flow_style=False)
        print(f"Generated: {table_directory}/schema_prompt.yaml")
        
        examples_data = {
            "Examples": table['Examples']
        }
        with open(os.path.join(table_directory, "example_prompt.yaml"), 'w') as file:
            yaml.dump(examples_data, file, default_flow_style=False)
        print(f"Generated: {table_directory}/example_prompt.yaml")


def update_yaml_with_config(yaml_data, config_data, agent_name, file_type, append=False):
    """Update the YAML data with the configuration data for the specified agent."""
    if file_type in config_data[agent_name]:
         data_to_update = config_data[agent_name][file_type]
         
         for key in data_to_update:
             if key in yaml_data:
                 if append:
                     # If the key exists, append the new data
                     if isinstance(yaml_data[key], list) and isinstance(data_to_update[key], list):
                         # If both are lists, extend the existing list
                         yaml_data[key].extend(data_to_update[key])
                     elif isinstance(yaml_data[key], list):
                         # If the existing data is a list, append the new data as a single item
                         yaml_data[key].append(data_to_update[key])
                     else:
                         # If the existing data is not a list, convert it to a list and append
                         yaml_data[key] = [yaml_data[key], data_to_update[key]]
                 else:
                     # If not appending, simply update the value
                     yaml_data[key] = data_to_update[key]
             else:
                 # If the key doesn't exist, add it
                 yaml_data[key] = data_to_update[key]
 
    return yaml_data
 
def update_yaml_with_config_table_pruning(yaml_data, config_data, agent_name, file_type):
     """Update the YAML data with the configuration data for the specified agent."""
     return update_yaml_with_config(yaml_data, config_data, agent_name, file_type, append=False)
 
def update_yaml_with_config_summary_agent(yaml_data, config_data, agent_name, file_type):
     """Update the YAML data with the configuration data for the specified agent."""
     return update_yaml_with_config(yaml_data, config_data, agent_name, file_type, append=True)


def table_pruning_prompt_handler(config_data,user):
    file_type=['system_prompt.yaml','example_prompt.yaml']
    agent_name='table_pruning_agent'
    yaml_template_file_path = os.path.join(os.getcwd(),r'agents_store\db_agent\config_files\table_pruning_agent_prompts')
    for file in file_type:
        yaml_data = load_yaml(os.path.join(yaml_template_file_path,file))
        final_yaml_data = update_yaml_with_config_table_pruning(yaml_data, config_data, agent_name, file.split('_')[0])
        yaml_output = yaml.dump(final_yaml_data, sort_keys=False,stream=None)
        yaml_output_directory = os.path.join(os.getcwd(),'user_config_files', user, 'table_pruning_agent_prompts')
        if not os.path.exists(yaml_output_directory):
            os.makedirs(yaml_output_directory)
        with open(os.path.join(yaml_output_directory,file), 'w') as file:
            file.write(yaml_output)
        print(yaml_output)


def summary_agent_handler(config_data,user): 
    file_type=['system_prompt.yaml']
    agent_name='summary_agent'
    yaml_template_file_path = os.path.join(os.getcwd(),r'agents_store\summary_agent\summary_agent_prompts')
    for file in file_type:
        yaml_data = load_yaml(os.path.join(yaml_template_file_path,file))
        final_yaml_data = update_yaml_with_config_summary_agent(yaml_data, config_data, agent_name, file.split('_')[0])
        yaml_output = yaml.dump(final_yaml_data, sort_keys=False,stream=None)
        yaml_output_directory = os.path.join(os.getcwd(),'user_config_files', user, 'summary_agent_prompts')
        if not os.path.exists(yaml_output_directory):
            os.makedirs(yaml_output_directory)
        with open(os.path.join(yaml_output_directory,file), 'w') as file:
            file.write(yaml_output)
        print(yaml_output)
    

def supervisor_agent_handler(config_data,user):

    file_type=['example_prompt.yaml']
    agent_name='supervisor_agent'
    # data =load_config(config_data)
    req_config_data=config_data[agent_name]['Examples']
    print(req_config_data)
    for file in file_type:
        yaml_output_directory = os.path.join(os.getcwd(),'user_config_files', user, 'supervisor_agent_prompts')
        if not os.path.exists(yaml_output_directory):
            os.makedirs(yaml_output_directory)
        with open(os.path.join(yaml_output_directory,file), 'w') as file:
            yaml.dump(req_config_data, file, default_flow_style=False)
        print(req_config_data)
    return req_config_data


def supervisor_functions_config(config_data,user):
    supervisor_template_path = os.path.join(os.getcwd(),'config_files','supervisor_functions.yaml')
    yaml_output_directory = os.path.join(os.getcwd(),'user_config_files', user)
    if not os.path.exists(yaml_output_directory):
        os.makedirs(yaml_output_directory)
    supervisor_yaml_file_path= os.path.join(yaml_output_directory, 'supervisory_functions.yaml')
    if Path(supervisor_template_path).exists():
        data = load_yaml(supervisor_template_path)
        for function in data['functions']:
            if 'db_agent' in function:
                function['db_agent']['db_config'] = config_data
                with open(supervisor_yaml_file_path, 'w') as file:
                 yaml.dump(data, file,sort_keys=False)      




def supervisor_functions_config_v1(config_data,user):
    config_data_req = config_data['supervisor_db_config']['db_config']
    supervisor_template_path = os.path.join(os.getcwd(),'config_files','supervisor_functions.yaml')
    yaml_output_directory = os.path.join(os.getcwd(),'user_config_files', user)
    if not os.path.exists(yaml_output_directory):
        os.makedirs(yaml_output_directory)
    supervisor_yaml_file_path= os.path.join(yaml_output_directory, 'supervisor_functions.yaml')
    if Path(supervisor_template_path).exists():
        data = load_yaml(supervisor_template_path)
        for function in data['functions']:
            if 'db_agent' in function:
                function['db_agent']['db_config'] = config_data_req
                with open(supervisor_yaml_file_path, 'w') as file:
                 yaml.dump(data, file,sort_keys=False)      
      
def agents_list():
    with open(agents_list_path, 'r') as f:
        agents_yaml = yaml.safe_load(f)
        # Extract list of agents from YAML  
        agents = agents_yaml.get('agents', [])
    return agents


def agent_config(agent_name):
    agent_directory = os.path.join(os.getcwd(),r'agent_config_utils')
    agent_config_path = os.path.join(agent_directory, f'{agent_name}.json')
    if os.path.exists(agent_config_path):
        config = load_config(agent_config_path)
        return config
    else:
        return {'error': 'Agent configuration not found'}

def save_config(config_data,agent_name,user):    
    agent_directory = os.path.join(os.getcwd(),'user_config_files',user)
    agent_config_path = os.path.join(agent_directory, f'{agent_name}.json')
    if not os.path.exists(agent_directory):
        os.makedirs(agent_directory)
    with open(agent_config_path, 'w') as file:
        json.dump(config_data, file, indent=4)
    



def get_user_config_agent(user,agent_name):
    agent_directory = os.path.join(os.getcwd(),'user_config_files',user)
    user_config_path = os.path.join(agent_directory, f'{agent_name}.json')
    if os.path.exists(user_config_path):
        config = load_config(user_config_path)
        return config
    else:
        return {'error': 'Agent configuration not found'}    
    


def save_yaml(file_path, data):
    """Save data to a YAML file."""
    with open(file_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


def enable_disable_agent_handler(agent_name, enable,user):
    AGENTS_CONFIG_PATH = os.path.join(os.getcwd(),'config_files','agents_required.yaml')
    agents_config_user_directory = os.path.join(os.getcwd(),'user_config_files',user)
    if not Path(agents_config_user_directory).exists():
        os.makedirs(agents_config_user_directory)
    agents_config_user_path = os.path.join(os.getcwd(),'user_config_files',user,'agents_required.yaml')
    config = load_yaml(AGENTS_CONFIG_PATH)
    agents = config.get('agents_required', [])
    
    for agent in agents:
        if agent['name'] == agent_name:
            agent['enabled'] = enable
            break
    
    save_yaml(agents_config_user_path, config)
    return config

